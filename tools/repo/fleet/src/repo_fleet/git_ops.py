"""GitHub and git operations, all executed through a CommandRunner."""

import logging
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from repo_fleet.errors import FleetError
from repo_fleet.planner import PlannedChange, write_changes
from repo_fleet.runner import CommandRunner

LOGGER = logging.getLogger(__name__)
SYNC_BRANCH = "devhub/repo-sync"
SYNC_REF = f"refs/heads/{SYNC_BRANCH}"
REMOTE_TRACKING_REF = f"refs/remotes/origin/{SYNC_BRANCH}"
COMMIT_MESSAGE = "chore(repo): sync DevHub templates"
PR_TITLE = COMMIT_MESSAGE
PR_BODY_INTRO = (
    "Automated sync of DevHub repository templates from `tools/repo/templates`.\n\n"
    "Changed files:\n"
)
APM_SYNC_BRANCH = "devhub/apm-sync"
APM_COMMIT_MESSAGE = "chore(apm): sync DevHub packages"
APM_PR_TITLE = APM_COMMIT_MESSAGE
APM_PR_BODY_INTRO = (
    "Automated refresh of DevHub APM packages and seed manifest.\n\nChanged files:\n"
)
GIT_AUTH_ENV = {
    "GIT_CONFIG_COUNT": "2",
    "GIT_CONFIG_KEY_0": "credential.helper",
    "GIT_CONFIG_VALUE_0": "!gh auth git-credential",
    "GIT_CONFIG_KEY_1": "core.hooksPath",
    "GIT_CONFIG_VALUE_1": "/dev/null",
}


@dataclass(frozen=True)
class SyncResult:
    pushed: bool
    pull_request: str


def ensure_gh_auth(runner: CommandRunner) -> None:
    runner.run(["gh", "auth", "status"])


def default_branch(runner: CommandRunner, slug: str) -> str:
    result = runner.run(
        [
            "gh",
            "repo",
            "view",
            slug,
            "--json",
            "defaultBranchRef",
            "-q",
            ".defaultBranchRef.name",
        ]
    )
    branch = result.stdout.strip()
    if not branch:
        raise FleetError(f"{slug}: GitHub reported no default branch")
    return branch


def clone(runner: CommandRunner, slug: str, destination: Path, branch: str) -> None:
    runner.run(
        [
            "gh",
            "repo",
            "clone",
            slug,
            str(destination),
            "--",
            "--depth",
            "1",
            "--branch",
            branch,
        ]
    )


def remote_sync_sha(
    runner: CommandRunner, checkout: Path, branch: str = SYNC_BRANCH
) -> str | None:
    ref = f"refs/heads/{branch}"
    result = runner.run(
        ["git", "ls-remote", "origin", ref], cwd=checkout, env=GIT_AUTH_ENV
    )
    for line in result.stdout.splitlines():
        sha, _, ref = line.partition("\t")
        if ref == f"refs/heads/{branch}" and sha:
            return sha
    return None


def commit_changes(
    runner: CommandRunner,
    checkout: Path,
    changes: tuple[PlannedChange, ...],
    commit_message: str = COMMIT_MESSAGE,
    branch: str = SYNC_BRANCH,
) -> None:
    paths = [str(change.path) for change in changes if change.writes]
    if not paths:
        raise FleetError("nothing to commit")
    runner.run(["git", "switch", "-c", branch], cwd=checkout, env=GIT_AUTH_ENV)
    write_changes(changes, checkout)
    runner.run(["git", "add", "--", *paths], cwd=checkout, env=GIT_AUTH_ENV)
    runner.run(["git", "commit", "-m", commit_message], cwd=checkout, env=GIT_AUTH_ENV)


def matches_remote_tree(
    runner: CommandRunner,
    checkout: Path,
    remote_sha: str,
    branch: str = SYNC_BRANCH,
) -> bool:
    """Return True when the local commit has the same tree as the remote branch."""
    ref = f"refs/heads/{branch}"
    tracking_ref = f"refs/remotes/origin/{branch}"
    runner.run(
        [
            "git",
            "fetch",
            "--depth",
            "1",
            "origin",
            f"+{ref}:{tracking_ref}",
        ],
        cwd=checkout,
        env=GIT_AUTH_ENV,
    )
    fetched = _rev_parse(runner, checkout, tracking_ref)
    if fetched != remote_sha:
        return False
    local_tree = _rev_parse(runner, checkout, "HEAD^{tree}")
    remote_tree = _rev_parse(runner, checkout, f"{tracking_ref}^{{tree}}")
    return local_tree == remote_tree


def push(
    runner: CommandRunner,
    checkout: Path,
    expected_sha: str | None,
    branch: str = SYNC_BRANCH,
) -> None:
    ref = f"refs/heads/{branch}"
    lease = f"--force-with-lease={ref}:{expected_sha or ''}"
    runner.run(
        ["git", "push", lease, "origin", f"HEAD:{ref}"],
        cwd=checkout,
        env=GIT_AUTH_ENV,
    )


def upsert_pull_request(
    runner: CommandRunner,
    slug: str,
    base: str,
    paths: Iterable[PurePosixPath],
    branch: str = SYNC_BRANCH,
    title: str = PR_TITLE,
    body_intro: str = PR_BODY_INTRO,
) -> str:
    body = body_intro + "".join(f"- `{path}`\n" for path in paths)
    existing = runner.run(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            slug,
            "--head",
            branch,
            "--state",
            "open",
            "--json",
            "number",
            "-q",
            ".[0].number // empty",
        ]
    ).stdout.strip()
    if existing:
        runner.run(
            [
                "gh",
                "pr",
                "edit",
                existing,
                "--repo",
                slug,
                "--title",
                title,
                "--body",
                body,
            ]
        )
        return f"updated #{existing}"
    created = runner.run(
        [
            "gh",
            "pr",
            "create",
            "--repo",
            slug,
            "--base",
            base,
            "--head",
            branch,
            "--title",
            title,
            "--body",
            body,
        ]
    )
    return f"created {created.stdout.strip()}".rstrip()


def sync_checkout(
    runner: CommandRunner,
    slug: str,
    base: str,
    checkout: Path,
    changes: tuple[PlannedChange, ...],
    *,
    branch: str = SYNC_BRANCH,
    commit_message: str = COMMIT_MESSAGE,
    pr_title: str = PR_TITLE,
    pr_body_intro: str = PR_BODY_INTRO,
) -> SyncResult:
    """Commit planned changes on the sync branch, push it, and open or update a PR."""
    if base == branch:
        raise FleetError(f"{slug}: default branch is the sync branch {branch}")
    written = tuple(change for change in changes if change.writes)
    if not written:
        raise FleetError(f"{slug}: no changes to sync")
    expected_sha = remote_sync_sha(runner, checkout, branch)
    commit_changes(runner, checkout, written, commit_message, branch)
    unchanged_remote = expected_sha is not None and matches_remote_tree(
        runner, checkout, expected_sha, branch
    )
    if unchanged_remote:
        LOGGER.info("%s: %s already up to date", slug, branch)
    else:
        push(runner, checkout, expected_sha, branch)
    pull_request = upsert_pull_request(
        runner,
        slug,
        base,
        (change.path for change in written),
        branch,
        pr_title,
        pr_body_intro,
    )
    return SyncResult(pushed=not unchanged_remote, pull_request=pull_request)


def _rev_parse(runner: CommandRunner, checkout: Path, revision: str) -> str:
    return runner.run(
        ["git", "rev-parse", revision], cwd=checkout, env=GIT_AUTH_ENV
    ).stdout.strip()

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


def remote_sync_sha(runner: CommandRunner, checkout: Path) -> str | None:
    result = runner.run(["git", "ls-remote", "origin", SYNC_REF], cwd=checkout)
    for line in result.stdout.splitlines():
        sha, _, ref = line.partition("\t")
        if ref == SYNC_REF and sha:
            return sha
    return None


def commit_changes(
    runner: CommandRunner, checkout: Path, changes: tuple[PlannedChange, ...]
) -> None:
    paths = [str(change.path) for change in changes if change.writes]
    if not paths:
        raise FleetError("nothing to commit")
    runner.run(["git", "switch", "-c", SYNC_BRANCH], cwd=checkout)
    write_changes(changes, checkout)
    runner.run(["git", "add", "--", *paths], cwd=checkout)
    runner.run(["git", "commit", "-m", COMMIT_MESSAGE], cwd=checkout)


def matches_remote_tree(runner: CommandRunner, checkout: Path, remote_sha: str) -> bool:
    """Return True when the local commit has the same tree as the remote branch."""
    runner.run(
        [
            "git",
            "fetch",
            "--depth",
            "1",
            "origin",
            f"+{SYNC_REF}:{REMOTE_TRACKING_REF}",
        ],
        cwd=checkout,
    )
    fetched = _rev_parse(runner, checkout, REMOTE_TRACKING_REF)
    if fetched != remote_sha:
        return False
    local_tree = _rev_parse(runner, checkout, "HEAD^{tree}")
    remote_tree = _rev_parse(runner, checkout, f"{REMOTE_TRACKING_REF}^{{tree}}")
    return local_tree == remote_tree


def push(runner: CommandRunner, checkout: Path, expected_sha: str | None) -> None:
    lease = f"--force-with-lease={SYNC_REF}:{expected_sha or ''}"
    runner.run(
        ["git", "push", lease, "origin", f"HEAD:{SYNC_REF}"],
        cwd=checkout,
    )


def upsert_pull_request(
    runner: CommandRunner,
    slug: str,
    base: str,
    paths: Iterable[PurePosixPath],
) -> str:
    body = PR_BODY_INTRO + "".join(f"- `{path}`\n" for path in paths)
    existing = runner.run(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            slug,
            "--head",
            SYNC_BRANCH,
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
                PR_TITLE,
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
            SYNC_BRANCH,
            "--title",
            PR_TITLE,
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
) -> SyncResult:
    """Commit planned changes on the sync branch, push it, and open or update a PR."""
    if base == SYNC_BRANCH:
        raise FleetError(f"{slug}: default branch is the sync branch {SYNC_BRANCH}")
    written = tuple(change for change in changes if change.writes)
    if not written:
        raise FleetError(f"{slug}: no changes to sync")
    expected_sha = remote_sync_sha(runner, checkout)
    commit_changes(runner, checkout, written)
    unchanged_remote = expected_sha is not None and matches_remote_tree(
        runner, checkout, expected_sha
    )
    if unchanged_remote:
        LOGGER.info("%s: %s already up to date", slug, SYNC_BRANCH)
    else:
        push(runner, checkout, expected_sha)
    pull_request = upsert_pull_request(
        runner, slug, base, (change.path for change in written)
    )
    return SyncResult(pushed=not unchanged_remote, pull_request=pull_request)


def _rev_parse(runner: CommandRunner, checkout: Path, revision: str) -> str:
    return runner.run(["git", "rev-parse", revision], cwd=checkout).stdout.strip()

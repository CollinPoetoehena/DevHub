from pathlib import Path, PurePosixPath

import pytest

from repo_fleet import git_ops
from repo_fleet.errors import CommandError, FleetError
from repo_fleet.planner import PlannedChange
from tests.fakes import FakeRunner

pytestmark = pytest.mark.unit

SLUG = "octo/alpha"
SHA = "a" * 40
LIST_PR = ("gh", "pr", "list")
LS_REMOTE = ("git", "ls-remote")
PR_LIST_ARGS = (
    "gh",
    "pr",
    "list",
    "--repo",
    SLUG,
    "--head",
    "devhub/repo-sync",
    "--state",
    "open",
    "--json",
    "number",
    "-q",
    ".[0].number // empty",
)
EXPECTED_BODY = (
    "Automated sync of DevHub repository templates from `tools/repo/templates`.\n\n"
    "Changed files:\n- `a.yml`\n"
)


def _changes() -> tuple[PlannedChange, ...]:
    return (
        PlannedChange(PurePosixPath("a.yml"), "create", "sync", b"a\n"),
        PlannedChange(PurePosixPath("b.yml"), "unchanged", "sync", b"b\n"),
    )


def test_ensure_gh_auth_aborts_on_failure() -> None:
    runner = FakeRunner(fail_on=("gh", "auth", "status"))

    with pytest.raises(CommandError):
        git_ops.ensure_gh_auth(runner)


def test_default_branch_queries_github() -> None:
    runner = FakeRunner(outputs={("gh", "repo", "view"): "trunk\n"})

    assert git_ops.default_branch(runner, SLUG) == "trunk"
    assert runner.commands() == [
        (
            "gh",
            "repo",
            "view",
            SLUG,
            "--json",
            "defaultBranchRef",
            "-q",
            ".defaultBranchRef.name",
        )
    ]


def test_default_branch_requires_a_value() -> None:
    with pytest.raises(FleetError, match="no default branch"):
        git_ops.default_branch(FakeRunner(), SLUG)


def test_clone_uses_shallow_default_branch(tmp_path: Path) -> None:
    runner = FakeRunner()

    git_ops.clone(runner, SLUG, tmp_path / "alpha", "main")

    assert runner.commands() == [
        (
            "gh",
            "repo",
            "clone",
            SLUG,
            str(tmp_path / "alpha"),
            "--",
            "--depth",
            "1",
            "--branch",
            "main",
        )
    ]


def test_remote_sync_sha_parses_ls_remote(tmp_path: Path) -> None:
    output = f"{SHA}\trefs/heads/devhub/repo-sync\n"
    runner = FakeRunner(outputs={LS_REMOTE: output})

    assert git_ops.remote_sync_sha(runner, tmp_path) == SHA
    assert runner.calls == [
        (("git", "ls-remote", "origin", "refs/heads/devhub/repo-sync"), tmp_path)
    ]


def test_remote_sync_sha_returns_none_when_branch_is_absent(tmp_path: Path) -> None:
    assert git_ops.remote_sync_sha(FakeRunner(), tmp_path) is None


@pytest.mark.parametrize(
    ("expected", "lease"),
    [
        (SHA, f"--force-with-lease=refs/heads/devhub/repo-sync:{SHA}"),
        (None, "--force-with-lease=refs/heads/devhub/repo-sync:"),
    ],
)
def test_push_uses_explicit_lease(
    tmp_path: Path, expected: str | None, lease: str
) -> None:
    runner = FakeRunner()

    git_ops.push(runner, tmp_path, expected)

    assert runner.calls == [
        (
            ("git", "push", lease, "origin", "HEAD:refs/heads/devhub/repo-sync"),
            tmp_path,
        )
    ]


def test_upsert_pull_request_creates_when_none_is_open() -> None:
    runner = FakeRunner(outputs={("gh", "pr", "create"): "https://pr/1\n"})

    result = git_ops.upsert_pull_request(runner, SLUG, "main", [PurePosixPath("a.yml")])

    assert result == "created https://pr/1"
    assert runner.commands() == [
        PR_LIST_ARGS,
        (
            "gh",
            "pr",
            "create",
            "--repo",
            SLUG,
            "--base",
            "main",
            "--head",
            "devhub/repo-sync",
            "--title",
            "chore(repo): sync DevHub templates",
            "--body",
            EXPECTED_BODY,
        ),
    ]


def test_upsert_pull_request_edits_open_pull_request() -> None:
    runner = FakeRunner(outputs={LIST_PR: "7\n"})

    result = git_ops.upsert_pull_request(runner, SLUG, "main", [PurePosixPath("a.yml")])

    assert result == "updated #7"
    assert runner.commands()[1] == (
        "gh",
        "pr",
        "edit",
        "7",
        "--repo",
        SLUG,
        "--title",
        "chore(repo): sync DevHub templates",
        "--body",
        EXPECTED_BODY,
    )


def test_sync_checkout_commits_pushes_and_opens_pr(tmp_path: Path) -> None:
    runner = FakeRunner()

    result = git_ops.sync_checkout(runner, SLUG, "main", tmp_path, _changes())

    assert result.pushed
    assert (tmp_path / "a.yml").read_bytes() == b"a\n"
    assert not (tmp_path / "b.yml").exists()
    assert [(cmd, cwd) for cmd, cwd in runner.calls if cmd[0] == "git"] == [
        (("git", "ls-remote", "origin", "refs/heads/devhub/repo-sync"), tmp_path),
        (("git", "switch", "-c", "devhub/repo-sync"), tmp_path),
        (("git", "add", "--", "a.yml"), tmp_path),
        (("git", "commit", "-m", "chore(repo): sync DevHub templates"), tmp_path),
        (
            (
                "git",
                "push",
                "--force-with-lease=refs/heads/devhub/repo-sync:",
                "origin",
                "HEAD:refs/heads/devhub/repo-sync",
            ),
            tmp_path,
        ),
    ]
    assert runner.commands()[-1][:3] == ("gh", "pr", "create")


def test_apm_sync_uses_its_own_local_branch_name(tmp_path: Path) -> None:
    runner = FakeRunner()

    git_ops.sync_checkout(
        runner,
        SLUG,
        "main",
        tmp_path,
        _changes(),
        branch=git_ops.APM_SYNC_BRANCH,
        commit_message=git_ops.APM_COMMIT_MESSAGE,
        pr_title=git_ops.APM_PR_TITLE,
        pr_body_intro=git_ops.APM_PR_BODY_INTRO,
    )

    assert (
        "git",
        "switch",
        "-c",
        git_ops.APM_SYNC_BRANCH,
    ) in runner.commands()


def test_sync_checkout_skips_push_when_remote_tree_matches(tmp_path: Path) -> None:
    runner = FakeRunner(
        outputs={
            LS_REMOTE: f"{SHA}\trefs/heads/devhub/repo-sync\n",
            ("git", "rev-parse", "refs/remotes/origin/devhub/repo-sync"): SHA,
            ("git", "rev-parse"): "tree",
        }
    )

    result = git_ops.sync_checkout(runner, SLUG, "main", tmp_path, _changes())

    assert not result.pushed
    assert not any(cmd[:2] == ("git", "push") for cmd in runner.commands())
    assert (
        "git",
        "fetch",
        "--depth",
        "1",
        "origin",
        "+refs/heads/devhub/repo-sync:refs/remotes/origin/devhub/repo-sync",
    ) in runner.commands()


def test_sync_checkout_pushes_with_lease_when_remote_tree_differs(
    tmp_path: Path,
) -> None:
    runner = FakeRunner(
        outputs={
            LS_REMOTE: f"{SHA}\trefs/heads/devhub/repo-sync\n",
            ("git", "rev-parse", "refs/remotes/origin/devhub/repo-sync"): SHA,
            ("git", "rev-parse", "HEAD^{tree}"): "local-tree",
            ("git", "rev-parse"): "remote-tree",
        }
    )

    result = git_ops.sync_checkout(runner, SLUG, "main", tmp_path, _changes())

    assert result.pushed
    push = next(cmd for cmd in runner.commands() if cmd[:2] == ("git", "push"))
    assert push[2] == f"--force-with-lease=refs/heads/devhub/repo-sync:{SHA}"


def test_matches_remote_tree_is_false_when_branch_moved(tmp_path: Path) -> None:
    runner = FakeRunner(outputs={("git", "rev-parse"): "other"})

    assert not git_ops.matches_remote_tree(runner, tmp_path, SHA)


def test_sync_checkout_refuses_sync_branch_as_default(tmp_path: Path) -> None:
    runner = FakeRunner()

    with pytest.raises(FleetError, match="default branch is the sync branch"):
        git_ops.sync_checkout(runner, SLUG, "devhub/repo-sync", tmp_path, _changes())
    assert runner.calls == []


def test_sync_checkout_requires_changes(tmp_path: Path) -> None:
    with pytest.raises(FleetError, match="no changes"):
        git_ops.sync_checkout(FakeRunner(), SLUG, "main", tmp_path, _changes()[1:])


def test_commit_changes_requires_changes(tmp_path: Path) -> None:
    with pytest.raises(FleetError, match="nothing to commit"):
        git_ops.commit_changes(FakeRunner(), tmp_path, ())

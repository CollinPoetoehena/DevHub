"""Real git against a local bare repository; gh is replaced by local equivalents."""

import shutil
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from repo_fleet import cli, git_ops
from repo_fleet.errors import CommandError
from repo_fleet.inventory import load_inventory
from repo_fleet.planner import plan_repo
from repo_fleet.runner import CommandResult, SubprocessRunner
from repo_fleet.templates import TemplateVariables, render_repository
from tests.fakes import inventory_data, write_inventory, write_template

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed"),
]

HEADER = (
    "# Managed by DevHub tools/repo (templates/common/sync); "
    "local changes are overwritten.\n"
)


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


def bare_git(remote: Path, *args: str) -> str:
    return git(f"--git-dir={remote}", *args, cwd=remote.parent)


def configure_identity(repo: Path) -> None:
    git("config", "user.name", "Fleet Test", cwd=repo)
    git("config", "user.email", "fleet@example.invalid", cwd=repo)
    git("config", "commit.gpgsign", "false", cwd=repo)


@dataclass
class HybridRunner:
    """Runs git for real and answers gh commands from local state."""

    remote: Path
    pr_number: str = ""
    gh_calls: list[tuple[str, ...]] = field(default_factory=list)
    real: SubprocessRunner = field(default_factory=SubprocessRunner)

    def run(self, args: Sequence[str], *, cwd: Path | None = None) -> CommandResult:
        command = tuple(args)
        if command[0] != "gh":
            return self.real.run(command, cwd=cwd)
        self.gh_calls.append(command)
        return CommandResult(command, 0, self._gh(command), "")

    def _gh(self, command: tuple[str, ...]) -> str:
        if command[1:3] == ("repo", "view"):
            return "main\n"
        if command[1:3] == ("repo", "clone"):
            destination = Path(command[4])
            branch = command[command.index("--branch") + 1]
            url = self.remote.as_uri()
            git(
                "clone",
                "--depth",
                "1",
                "--branch",
                branch,
                url,
                str(destination),
                cwd=self.remote.parent,
            )
            configure_identity(destination)
            return ""
        if command[1:3] == ("pr", "list"):
            return self.pr_number
        if command[1:3] == ("pr", "create"):
            self.pr_number = "1"
            return "https://example.invalid/pr/1\n"
        return ""


@pytest.fixture
def remote(tmp_path: Path) -> Path:
    bare = tmp_path / "remote.git"
    git("init", "--bare", "--initial-branch", "main", str(bare), cwd=tmp_path)
    seed = tmp_path / "seed"
    git("init", "--initial-branch", "main", str(seed), cwd=tmp_path)
    configure_identity(seed)
    (seed / "README.md").write_text("existing\n", encoding="utf-8")
    git("add", "README.md", cwd=seed)
    git("commit", "-m", "init", cwd=seed)
    git("push", bare.as_uri(), "main", cwd=seed)
    return bare


@pytest.fixture
def fleet_args(tmp_path: Path) -> list[str]:
    inventory = write_inventory(tmp_path / "inventory.json", inventory_data())
    templates = tmp_path / "templates"
    write_template(
        templates, "common/sync/.github/ci.yml.tmpl", "on: $default_branch\n"
    )
    write_template(templates, "common/seed/README.md", "template readme\n")
    return ["--inventory", str(inventory), "--templates", str(templates)]


def _branch_sha(remote: Path) -> str:
    return bare_git(remote, "rev-parse", "refs/heads/devhub/repo-sync")


def test_apply_pushes_sync_branch_and_is_idempotent(
    remote: Path, fleet_args: list[str]
) -> None:
    runner = HybridRunner(remote)

    assert cli.main(["apply", "--yes", *fleet_args], runner=runner) == cli.EXIT_OK

    first = _branch_sha(remote)
    ci = bare_git(remote, "show", "devhub/repo-sync:.github/ci.yml")
    assert ci + "\n" == HEADER + "on: main\n"
    assert bare_git(remote, "show", "devhub/repo-sync:README.md") == "existing"
    message = bare_git(remote, "log", "-1", "--format=%s", "devhub/repo-sync")
    assert message == "chore(repo): sync DevHub templates"
    assert any(call[1:3] == ("pr", "create") for call in runner.gh_calls)

    assert cli.main(["apply", "--yes", *fleet_args], runner=runner) == cli.EXIT_OK

    assert _branch_sha(remote) == first
    assert any(call[1:3] == ("pr", "edit") for call in runner.gh_calls)


def test_plan_reports_changes_against_real_clone(
    remote: Path, fleet_args: list[str]
) -> None:
    runner = HybridRunner(remote)

    assert cli.main(["plan", *fleet_args], runner=runner) == cli.EXIT_CHANGES


def test_push_fails_when_lease_is_stale(
    tmp_path: Path, remote: Path, fleet_args: list[str]
) -> None:
    runner = HybridRunner(remote)
    inventory = load_inventory(Path(fleet_args[1]))
    repository = inventory.repositories[0]
    checkout = tmp_path / "work"
    git_ops.clone(runner, "octo/alpha", checkout, "main")
    variables = TemplateVariables.for_repository(inventory, repository, "main")
    rendered = render_repository(Path(fleet_args[3]), repository.profiles, variables)
    changes = plan_repo(rendered, checkout)
    expected = git_ops.remote_sync_sha(runner, checkout)
    git_ops.commit_changes(runner, checkout, changes)

    competitor = tmp_path / "competitor"
    git("clone", remote.as_uri(), str(competitor), cwd=tmp_path)
    configure_identity(competitor)
    git("commit", "--allow-empty", "-m", "concurrent", cwd=competitor)
    git("push", "origin", "HEAD:refs/heads/devhub/repo-sync", cwd=competitor)

    assert expected is None
    with pytest.raises(CommandError, match="git push failed"):
        git_ops.push(runner, checkout, expected)
    assert bare_git(remote, "log", "-1", "--format=%s", "devhub/repo-sync") == (
        "concurrent"
    )

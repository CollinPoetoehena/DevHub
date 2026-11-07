"""Real git against a local bare repository; gh is replaced by local equivalents."""

import shutil
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from repo_fleet import cli, git_ops
from repo_fleet.apm import LEGACY_CALLER_CONTENT
from repo_fleet.errors import CommandError
from repo_fleet.inventory import load_inventory
from repo_fleet.planner import plan_repo
from repo_fleet.runner import CommandResult, SubprocessRunner
from repo_fleet.templates import TemplateVariables, render_repository
from tests.fakes import (
    FakeRunner,
    inventory_data,
    repository_entry,
    write_inventory,
    write_template,
)

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

    def run(
        self,
        args: Sequence[str],
        *,
        cwd: Path | None = None,
        env: Mapping[str, str | None] | None = None,
        timeout: float | None = None,
    ) -> CommandResult:
        command = tuple(args)
        if command[0] != "gh":
            return self.real.run(command, cwd=cwd, env=env, timeout=timeout)
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
    write_template(
        templates,
        "common/seed/apm.yml.tmpl",
        "name: $repository\n"
        "version: 1.0.0\n"
        "target: copilot\n"
        "dependencies:\n"
        "  apm:\n"
        "$apm_dependencies\n",
    )
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


@dataclass
class APMHybridRunner(HybridRunner):
    apm_calls: list[tuple[str, ...]] = field(default_factory=list)
    apm_environments: list[Mapping[str, str | None] | None] = field(
        default_factory=list
    )
    fail_apm_for: str | None = None

    def run(
        self,
        args: Sequence[str],
        *,
        cwd: Path | None = None,
        env: Mapping[str, str | None] | None = None,
        timeout: float | None = None,
    ) -> CommandResult:
        command = tuple(args)
        if command[0] != "apm":
            return super().run(command, cwd=cwd, env=env, timeout=timeout)
        self.apm_calls.append(command)
        self.apm_environments.append(env)
        if cwd is not None and cwd.name == self.fail_apm_for:
            raise CommandError("apm preflight failed")
        if command[1] == "--version":
            output = "Agent Package Manager (APM) CLI version 0.35.0\n"
        elif command[1] == "install":
            assert cwd is not None
            (cwd / "apm.lock.yaml").write_text(
                "lockfile_version: '1'\napm_version: 0.35.0\ndependencies: []\n",
                encoding="utf-8",
            )
            (cwd / ".gitignore").write_text("apm_modules/\n", encoding="utf-8")
            output = ""
        else:
            output = (
                "[>] Checking upstream for revision-pin freshness...\n"
                "[+] All dependencies already at their latest matching refs.\n"
            )
        return CommandResult(command, 0, output, "")


def test_apm_apply_migrates_exact_caller_and_is_idempotent(
    tmp_path: Path, remote: Path, fleet_args: list[str]
) -> None:
    seed = tmp_path / "legacy-seed"
    git("clone", remote.as_uri(), str(seed), cwd=tmp_path)
    configure_identity(seed)
    caller = seed / ".github" / "workflows" / "devhub-apm-sync.yml"
    caller.parent.mkdir(parents=True)
    caller.write_bytes(LEGACY_CALLER_CONTENT)
    git("add", ".github/workflows/devhub-apm-sync.yml", cwd=seed)
    git("commit", "-m", "add legacy APM caller", cwd=seed)
    git("push", "origin", "main", cwd=seed)

    runner = APMHybridRunner(remote)
    assert cli.main(["apply", "--apm", "--yes", *fleet_args], runner=runner) == (
        cli.EXIT_OK
    )

    branch = "devhub/apm-sync"
    assert bare_git(remote, "show", f"{branch}:apm.yml").startswith("name: alpha")
    assert bare_git(remote, "show", f"{branch}:apm.lock.yaml").startswith(
        "lockfile_version"
    )
    assert (
        bare_git(
            remote,
            "ls-tree",
            "-r",
            branch,
            "--",
            ".github/workflows/devhub-apm-sync.yml",
        )
        == ""
    )
    first = bare_git(remote, "rev-parse", f"refs/heads/{branch}")
    assert all(
        env is not None
        and env.get("GH_TOKEN") is None
        and env.get("GITHUB_TOKEN") is None
        and env.get("TF_TOKEN_app_terraform_io") is None
        and env.get("TF_CLOUD_TOKEN") is None
        and env.get("GIT_CONFIG_GLOBAL") == "/dev/null"
        and env.get("GH_CONFIG_DIR")
        for env in runner.apm_environments
    )

    assert cli.main(["apply", "--apm", "--yes", *fleet_args], runner=runner) == (
        cli.EXIT_OK
    )

    assert bare_git(remote, "rev-parse", f"refs/heads/{branch}") == first
    assert any(call[1:3] == ("pr", "edit") for call in runner.gh_calls)


def test_apm_apply_preflights_every_repository_before_writing(
    tmp_path: Path, remote: Path, fleet_args: list[str]
) -> None:
    inventory = write_inventory(
        tmp_path / "two-repositories.json",
        inventory_data(
            {
                "alpha": repository_entry(),
                "beta": repository_entry(),
            }
        ),
    )
    args = [*fleet_args]
    args[1] = str(inventory)
    runner = APMHybridRunner(remote, fail_apm_for="beta")

    assert cli.main(["apply", "--apm", "--yes", *args], runner=runner) == (
        cli.EXIT_ERROR
    )

    assert bare_git(remote, "for-each-ref", "refs/heads/devhub/apm-sync") == ""
    assert not any(
        call[1:3] in {("pr", "create"), ("pr", "edit")} for call in runner.gh_calls
    )


def test_apm_apply_auth_failure_precedes_repository_access(
    fleet_args: list[str],
) -> None:
    runner = FakeRunner(fail_on=("gh", "auth", "status"))

    assert cli.main(["apply", "--apm", "--yes", *fleet_args], runner=runner) == (
        cli.EXIT_ERROR
    )

    assert runner.commands() == [("gh", "auth", "status")]

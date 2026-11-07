import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from types import SimpleNamespace

import pytest

from repo_fleet import git_ops, sync
from repo_fleet.inventory import parse_inventory
from repo_fleet.paths import FleetPaths
from repo_fleet.planner import PlannedChange, write_changes
from repo_fleet.runner import CommandResult, SubprocessRunner
from tests.fakes import inventory_data, repository_entry, write_inventory

pytestmark = pytest.mark.integration


def _git(*args: str, cwd: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


def _configure_git(repository: Path) -> None:
    _git("config", "user.name", "Fleet Test", cwd=repository)
    _git("config", "user.email", "fleet@example.invalid", cwd=repository)
    _git("config", "commit.gpgsign", "false", cwd=repository)


@dataclass
class LocalGitHubRunner:
    remote: Path
    commands: list[tuple[str, ...]] = field(default_factory=list)
    pull_requests: list[tuple[str, ...]] = field(default_factory=list)
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
        self.commands.append(command)
        if command[0] != "gh":
            return self.real.run(command, cwd=cwd, env=env, timeout=timeout)
        if command[1:3] == ("repo", "view"):
            return CommandResult(command, 0, "main\n", "")
        if command[1:3] == ("repo", "clone"):
            destination = Path(command[4])
            _git(
                "clone",
                "--depth",
                "1",
                "--branch",
                "main",
                self.remote.as_uri(),
                str(destination),
                cwd=self.remote.parent,
            )
            _configure_git(destination)
            return CommandResult(command, 0, "", "")
        if command[1:3] == ("pr", "list"):
            return CommandResult(command, 0, "", "")
        if command[1:3] == ("pr", "create"):
            self.pull_requests.append(command)
            return CommandResult(command, 0, "https://example.invalid/pr/1\n", "")
        raise AssertionError(f"unexpected gh command: {command}")


@pytest.fixture
def remote(tmp_path: Path) -> Path:
    bare = tmp_path / "alpha.git"
    seed = tmp_path / "seed"
    _git("init", "--bare", "--initial-branch=main", str(bare), cwd=tmp_path)
    _git("init", "--initial-branch=main", str(seed), cwd=tmp_path)
    _configure_git(seed)
    (seed / "README.md").write_text("existing\n", encoding="utf-8")
    _git("add", "README.md", cwd=seed)
    _git("commit", "-m", "initial", cwd=seed)
    _git("push", bare.as_uri(), "main", cwd=seed)
    return bare


def test_delivery_creates_one_combined_pr_without_default_branch_push(
    tmp_path: Path, remote: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inventory_file = write_inventory(
        tmp_path / "terraform" / "inventory.json",
        inventory_data({"alpha": repository_entry()}),
    )
    templates = tmp_path / "templates"
    templates.mkdir()
    inventory = parse_inventory(
        inventory_data({"alpha": repository_entry()}), str(inventory_file)
    )
    paths = FleetPaths(inventory_file, templates)
    workdir = tmp_path / "repo-fleet-sync-42-1"
    checkout_root = workdir / "checkouts"
    checkout_root.mkdir(parents=True)
    runner = LocalGitHubRunner(remote)
    checkout = checkout_root / "alpha"
    git_ops.clone(runner, "octo/alpha", checkout, "main")
    changes = (
        PlannedChange(
            PurePosixPath(".github/workflows/ci.yml"),
            "create",
            "sync",
            b"name: shared ci\n",
        ),
        PlannedChange(
            PurePosixPath("apm.lock.yaml"),
            "create",
            "sync",
            b"apm_version: 0.35.0\n",
        ),
    )
    write_changes(changes, checkout)
    entry = sync._prepared_repository(
        "alpha",
        checkout,
        SimpleNamespace(default_branch="main", changes=changes),
        runner,
    )
    inventory_digest = sync._digest(inventory_file.read_bytes())
    state = {
        "source_sha": "local-source",
        "inventory_digest": inventory_digest,
        "settings": {"plan_digest": "saved-plan"},
    }
    prepared = {
        "source_sha": "local-source",
        "inventory_digest": inventory_digest,
        "repositories": [entry],
    }
    workdir.mkdir(exist_ok=True)
    sync._write_json(workdir / sync.STATE_FILE, state)
    sync._write_json(workdir / sync.PREPARED_FILE, prepared)
    sync._write_json(
        workdir / sync.APPLIED_FILE,
        {
            "source_sha": "local-source",
            "inventory_digest": inventory_digest,
            "prepared_digest": sync._file_digest(workdir / sync.PREPARED_FILE),
            "plan_digest": "saved-plan",
        },
    )
    monkeypatch.setattr(sync, "_validate_source", lambda *_: None)

    sync.deliver(inventory, paths, runner, workdir, tmp_path)

    branch = "devhub/repo-sync"
    assert _git(
        "--git-dir",
        str(remote),
        "show",
        f"{branch}:.github/workflows/ci.yml",
        cwd=tmp_path,
    ) == ("name: shared ci")
    assert _git(
        "--git-dir", str(remote), "show", f"{branch}:apm.lock.yaml", cwd=tmp_path
    ) == ("apm_version: 0.35.0")
    assert _git("--git-dir", str(remote), "ls-tree", "-r", "main", cwd=tmp_path) == (
        "100644 blob "
        + _git("--git-dir", str(remote), "rev-parse", "main:README.md", cwd=tmp_path)
        + "\tREADME.md"
    )
    assert len(runner.pull_requests) == 1
    assert not any(command[0] == "apm" for command in runner.commands)
    assert any(
        command[:2] == ("git", "push") and "refs/heads/devhub/repo-sync" in command[-1]
        for command in runner.commands
    )

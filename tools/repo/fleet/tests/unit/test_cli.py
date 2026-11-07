import sys
from pathlib import Path

import pytest

from repo_fleet import cli
from repo_fleet.paths import INVENTORY_ENV_VAR, TEMPLATES_ENV_VAR
from tests.fakes import (
    FakeRunner,
    inventory_data,
    repository_entry,
    write_inventory,
    write_template,
)

pytestmark = pytest.mark.unit

REPO_VIEW = ("gh", "repo", "view")


@pytest.fixture
def fleet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    data = inventory_data(
        {"alpha": repository_entry(), "old": repository_entry(archived=True)}
    )
    write_inventory(tmp_path / "inventory.json", data)
    write_template(
        tmp_path / "templates", "common/sync/ci.yml.tmpl", "b: $default_branch\n"
    )
    write_template(tmp_path / "templates", "common/seed/README.md", "readme\n")
    monkeypatch.setenv(INVENTORY_ENV_VAR, str(tmp_path / "inventory.json"))
    monkeypatch.setenv(TEMPLATES_ENV_VAR, str(tmp_path / "templates"))
    return tmp_path


def _runner(existing: dict[str, str] | None = None) -> FakeRunner:
    files = existing or {}

    def populate(checkout: Path) -> None:
        for relative, content in files.items():
            (checkout / relative).write_text(content, encoding="utf-8")

    return FakeRunner(outputs={REPO_VIEW: "main\n"}, on_clone=populate)


def _synced_files() -> dict[str, str]:
    header = (
        "# Managed by DevHub tools/repo (templates/common/sync); "
        "local changes are overwritten.\n"
    )
    return {"ci.yml": header + "b: main\n", "README.md": "custom\n"}


def _interactive(monkeypatch: pytest.MonkeyPatch, tty: bool, answer: str = "") -> None:
    monkeypatch.setattr(sys.stdin, "isatty", lambda: tty)
    monkeypatch.setattr("builtins.input", lambda _prompt: answer)


@pytest.mark.usefixtures("fleet")
def test_check_renders_active_repositories(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["check"]) == cli.EXIT_OK
    assert capsys.readouterr().out == "ok alpha: 2 file(s)\n"


def test_check_reports_invalid_inventory(fleet: Path) -> None:
    write_inventory(fleet / "inventory.json", {"inventory": {}})

    assert cli.main(["check"]) == cli.EXIT_ERROR


def test_check_accepts_explicit_paths(tmp_path: Path) -> None:
    write_inventory(tmp_path / "i.json", inventory_data())
    (tmp_path / "t").mkdir()

    args = ["check", "--inventory", str(tmp_path / "i.json")]
    assert cli.main([*args, "--templates", str(tmp_path / "t")]) == cli.EXIT_OK


@pytest.mark.usefixtures("fleet")
def test_plan_exits_two_with_changes(capsys: pytest.CaptureFixture[str]) -> None:
    runner = _runner()

    assert cli.main(["plan", "--diff"], runner=runner) == cli.EXIT_CHANGES
    out = capsys.readouterr().out
    assert "alpha (main): 2 change(s)" in out
    assert "  create ci.yml" in out
    assert "+b: main\n" in out
    assert runner.commands()[0] == ("gh", "auth", "status")
    assert not any("old" in cmd for cmd in runner.commands())


@pytest.mark.usefixtures("fleet")
def test_plan_exits_zero_without_changes(capsys: pytest.CaptureFixture[str]) -> None:
    runner = _runner(_synced_files())

    assert cli.main(["plan", "--repo", "alpha"], runner=runner) == cli.EXIT_OK
    assert "  seed-skip README.md" in capsys.readouterr().out


@pytest.mark.usefixtures("fleet")
def test_plan_rejects_unknown_repository() -> None:
    runner = _runner()

    assert cli.main(["plan", "--repo", "nope"], runner=runner) == cli.EXIT_ERROR
    assert runner.calls == []


@pytest.mark.usefixtures("fleet")
def test_plan_skips_explicitly_selected_archived_repository() -> None:
    runner = _runner()

    assert cli.main(["plan", "--repo", "old"], runner=runner) == cli.EXIT_OK
    assert runner.commands() == [("gh", "auth", "status")]


@pytest.mark.usefixtures("fleet")
def test_plan_aborts_when_gh_is_not_authenticated() -> None:
    runner = FakeRunner(fail_on=("gh", "auth", "status"))

    assert cli.main(["plan"], runner=runner) == cli.EXIT_ERROR
    assert len(runner.calls) == 1


@pytest.mark.usefixtures("fleet")
def test_apply_refuses_non_interactive_without_yes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _interactive(monkeypatch, tty=False)
    runner = _runner()

    assert cli.main(["apply"], runner=runner) == cli.EXIT_ERROR
    assert runner.calls == []


@pytest.mark.usefixtures("fleet")
def test_apply_with_yes_pushes_and_creates_pr(
    capsys: pytest.CaptureFixture[str],
) -> None:
    runner = _runner()

    assert cli.main(["apply", "--yes"], runner=runner) == cli.EXIT_OK
    commands = runner.commands()
    assert ("git", "add", "--", "ci.yml", "README.md") in commands
    assert any(cmd[:2] == ("git", "push") for cmd in commands)
    assert commands[-1][:3] == ("gh", "pr", "create")
    assert "alpha: pushed; PR created" in capsys.readouterr().out


@pytest.mark.usefixtures("fleet")
def test_apply_without_changes_creates_no_branch() -> None:
    runner = _runner(_synced_files())

    assert cli.main(["apply", "--yes"], runner=runner) == cli.EXIT_OK
    assert not any(cmd[0] == "git" for cmd in runner.commands())


@pytest.mark.usefixtures("fleet")
def test_apply_prompts_and_aborts_on_no(monkeypatch: pytest.MonkeyPatch) -> None:
    _interactive(monkeypatch, tty=True, answer="n")
    runner = _runner()

    assert cli.main(["apply"], runner=runner) == cli.EXIT_ERROR
    assert not any(cmd[0] == "git" for cmd in runner.commands())


@pytest.mark.usefixtures("fleet")
def test_apply_prompts_and_continues_on_yes(monkeypatch: pytest.MonkeyPatch) -> None:
    _interactive(monkeypatch, tty=True, answer="y")
    runner = _runner()

    assert cli.main(["apply", "-v"], runner=runner) == cli.EXIT_OK
    assert any(cmd[:2] == ("git", "push") for cmd in runner.commands())


@pytest.mark.usefixtures("fleet")
def test_apply_reports_command_failure() -> None:
    runner = _runner()
    failing = FakeRunner(
        outputs=runner.outputs, on_clone=runner.on_clone, fail_on=("git", "push")
    )

    assert cli.main(["apply", "--yes"], runner=failing) == cli.EXIT_ERROR

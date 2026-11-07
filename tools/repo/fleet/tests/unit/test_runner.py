import subprocess
from pathlib import Path
from typing import Any

import pytest

from repo_fleet.errors import CommandError
from repo_fleet.runner import REDACTED, SubprocessRunner, redact

pytestmark = pytest.mark.unit

TOKEN = "ghp_" + "a" * 36


def _fake_run(returncode: int, stderr: str = "") -> Any:
    captured: dict[str, Any] = {}

    def run(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        captured.update(args=args, **kwargs)
        return subprocess.CompletedProcess(args, returncode, "out\n", stderr)

    return run, captured


def test_subprocess_runner_passes_argument_list(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    run, captured = _fake_run(0)
    monkeypatch.setattr(subprocess, "run", run)

    result = SubprocessRunner().run(["git", "status"], cwd=tmp_path)

    assert result.stdout == "out\n"
    assert result.args == ("git", "status")
    assert captured["args"] == ["git", "status"]
    assert captured["cwd"] == tmp_path
    assert captured["check"] is False
    assert captured["capture_output"] is True
    assert captured["text"] is True
    assert captured["env"]["GIT_TERMINAL_PROMPT"] == "0"
    assert captured["env"]["GH_PROMPT_DISABLED"] == "1"


def test_subprocess_runner_raises_with_redacted_stderr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run, _ = _fake_run(128, f"fatal: bad token {TOKEN}\n")
    monkeypatch.setattr(subprocess, "run", run)

    with pytest.raises(CommandError) as excinfo:
        SubprocessRunner().run(["git", "push", "origin"])

    message = str(excinfo.value)
    assert "git push failed with exit code 128" in message
    assert TOKEN not in message
    assert REDACTED in message


def test_subprocess_runner_reports_missing_executable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def missing(*_: object, **__: object) -> None:
        raise FileNotFoundError("gh")

    monkeypatch.setattr(subprocess, "run", missing)

    with pytest.raises(CommandError, match="cannot run gh auth"):
        SubprocessRunner().run(["gh", "auth", "status"])


def test_subprocess_runner_removes_inherited_tokens_and_sets_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run, captured = _fake_run(0)
    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setenv("GH_TOKEN", TOKEN)
    monkeypatch.setenv("GITHUB_TOKEN", TOKEN)

    SubprocessRunner().run(
        ["apm", "outdated"],
        env={"GH_TOKEN": None, "GITHUB_TOKEN": None},
        timeout=30,
    )

    assert "GH_TOKEN" not in captured["env"]
    assert "GITHUB_TOKEN" not in captured["env"]
    assert captured["timeout"] == 30


def test_subprocess_runner_reports_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    def timeout(*_: object, **__: object) -> None:
        raise subprocess.TimeoutExpired(["apm", "update"], 30)

    monkeypatch.setattr(subprocess, "run", timeout)

    with pytest.raises(CommandError, match="apm update timed out after 30 seconds"):
        SubprocessRunner().run(["apm", "update"], timeout=30)


def test_redact_removes_known_token_formats() -> None:
    pat = "github_pat_" + "b" * 30
    assert redact(f"x {TOKEN} y {pat}") == f"x {REDACTED} y {REDACTED}"

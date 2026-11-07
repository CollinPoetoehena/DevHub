"""Test doubles and builders shared by unit and integration tests."""

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from repo_fleet.errors import CommandError
from repo_fleet.runner import CommandResult

OWNER = "octo"
CloneHook = Callable[[Path], None]


@dataclass
class FakeRunner:
    """Records calls; returns stdout for the longest matching argument prefix."""

    outputs: Mapping[tuple[str, ...], str] = field(default_factory=dict)
    fail_on: tuple[str, ...] | None = None
    on_clone: CloneHook | None = None
    calls: list[tuple[tuple[str, ...], Path | None]] = field(default_factory=list)

    def run(self, args: Sequence[str], *, cwd: Path | None = None) -> CommandResult:
        command = tuple(args)
        self.calls.append((command, cwd))
        if self.fail_on is not None and command[: len(self.fail_on)] == self.fail_on:
            raise CommandError(f"{' '.join(self.fail_on)} failed")
        if command[:3] == ("gh", "repo", "clone"):
            destination = Path(command[4])
            destination.mkdir(parents=True)
            if self.on_clone is not None:
                self.on_clone(destination)
        return CommandResult(command, 0, self._stdout(command), "")

    def commands(self) -> list[tuple[str, ...]]:
        return [command for command, _ in self.calls]

    def _stdout(self, command: tuple[str, ...]) -> str:
        matches = [
            prefix for prefix in self.outputs if command[: len(prefix)] == prefix
        ]
        if not matches:
            return ""
        return self.outputs[max(matches, key=len)]


def repository_entry(
    visibility: str = "public",
    profiles: Sequence[str] = ("common",),
    archived: bool = False,
) -> dict[str, object]:
    return {"visibility": visibility, "profiles": list(profiles), "archived": archived}


def inventory_data(
    repositories: Mapping[str, object] | None = None, owner: str = OWNER
) -> dict[str, object]:
    repos = {"alpha": repository_entry()} if repositories is None else repositories
    return {"inventory": {"owner": owner, "repositories": dict(repos)}}


def write_inventory(path: Path, data: Mapping[str, object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def write_template(templates: Path, relative: str, content: str | bytes) -> Path:
    target = templates / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        target.write_bytes(content)
    else:
        target.write_text(content, encoding="utf-8")
    return target

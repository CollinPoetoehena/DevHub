"""Compare rendered files with a checkout and decide what to write."""

import difflib
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Literal

from repo_fleet.errors import FleetError
from repo_fleet.templates import Mode, RenderedFile

Action = Literal["create", "update", "unchanged", "seed-skip"]
WRITE_ACTIONS: frozenset[Action] = frozenset({"create", "update"})


@dataclass(frozen=True)
class PlannedChange:
    path: PurePosixPath
    action: Action
    mode: Mode
    content: bytes
    diff: str | None = None

    @property
    def writes(self) -> bool:
        return self.action in WRITE_ACTIONS


@dataclass(frozen=True)
class RepoPlan:
    repository: str
    default_branch: str
    changes: tuple[PlannedChange, ...]

    @property
    def writes(self) -> tuple[PlannedChange, ...]:
        return tuple(change for change in self.changes if change.writes)

    @property
    def has_changes(self) -> bool:
        return bool(self.writes)


def plan_repo(
    rendered: Iterable[RenderedFile], checkout_dir: Path, *, include_diff: bool = False
) -> tuple[PlannedChange, ...]:
    return tuple(_plan_file(item, checkout_dir, include_diff) for item in rendered)


def write_changes(changes: Iterable[PlannedChange], checkout_dir: Path) -> None:
    for change in changes:
        if not change.writes:
            continue
        target = _checked_target(checkout_dir, change.path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(change.content)


def _plan_file(
    item: RenderedFile, checkout_dir: Path, include_diff: bool
) -> PlannedChange:
    target = _checked_target(checkout_dir, item.path)
    if not target.exists():
        diff = _diff(item.path, b"", item.content) if include_diff else None
        return PlannedChange(item.path, "create", item.mode, item.content, diff)
    if item.mode == "seed":
        return PlannedChange(item.path, "seed-skip", item.mode, item.content)
    if not target.is_file():
        raise FleetError(f"{item.path}: exists in the checkout but is not a file")
    current = target.read_bytes()
    if current == item.content:
        return PlannedChange(item.path, "unchanged", item.mode, item.content)
    diff = _diff(item.path, current, item.content) if include_diff else None
    return PlannedChange(item.path, "update", item.mode, item.content, diff)


def _checked_target(checkout_dir: Path, relative: PurePosixPath) -> Path:
    """Return the target path, refusing symlinks and paths outside the checkout."""
    root = checkout_dir.resolve()
    target = root.joinpath(*relative.parts)
    for candidate in (target, *target.parents):
        if candidate == root:
            break
        if candidate.is_symlink():
            raise FleetError(f"{relative}: refusing to write through a symlink")
    if not target.resolve().is_relative_to(root):
        raise FleetError(f"{relative}: resolves outside the checkout")
    return target


def _diff(path: PurePosixPath, before: bytes, after: bytes) -> str:
    lines = difflib.unified_diff(
        before.decode("utf-8", errors="replace").splitlines(keepends=True),
        after.decode("utf-8", errors="replace").splitlines(keepends=True),
        fromfile=f"a/{path}",
        tofile=f"b/{path}",
    )
    return "".join(lines)

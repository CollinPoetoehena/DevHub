from pathlib import Path, PurePosixPath

import pytest

from repo_fleet.errors import FleetError
from repo_fleet.planner import PlannedChange, RepoPlan, plan_repo, write_changes
from repo_fleet.templates import Mode, RenderedFile

pytestmark = pytest.mark.unit


def _file(path: str, content: bytes, mode: Mode = "sync") -> RenderedFile:
    return RenderedFile(PurePosixPath(path), content, mode, "common")


def _checkout(tmp_path: Path, files: dict[str, bytes]) -> Path:
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    for relative, content in files.items():
        target = checkout / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    return checkout


def test_plan_repo_classifies_actions(tmp_path: Path) -> None:
    checkout = _checkout(
        tmp_path, {"same.yml": b"a\n", "old.yml": b"old\n", "seeded.md": b"mine\n"}
    )
    rendered = [
        _file("new/file.yml", b"n\n"),
        _file("same.yml", b"a\n"),
        _file("old.yml", b"new\n"),
        _file("seeded.md", b"template\n", "seed"),
        _file("fresh.md", b"seed\n", "seed"),
    ]

    actions = {str(c.path): c.action for c in plan_repo(rendered, checkout)}

    assert actions == {
        "new/file.yml": "create",
        "same.yml": "unchanged",
        "old.yml": "update",
        "seeded.md": "seed-skip",
        "fresh.md": "create",
    }


def test_plan_repo_includes_unified_diff_on_request(tmp_path: Path) -> None:
    checkout = _checkout(tmp_path, {"a.yml": b"old\n"})

    without = plan_repo([_file("a.yml", b"new\n")], checkout)
    (change,) = plan_repo([_file("a.yml", b"new\n")], checkout, include_diff=True)

    assert without[0].diff is None
    assert change.diff == "--- a/a.yml\n+++ b/a.yml\n@@ -1 +1 @@\n-old\n+new\n"


def test_plan_repo_diff_for_created_file(tmp_path: Path) -> None:
    checkout = _checkout(tmp_path, {})

    (change,) = plan_repo([_file("a.yml", b"x\n")], checkout, include_diff=True)

    assert change.diff is not None
    assert "+x\n" in change.diff


def test_plan_repo_rejects_directory_target(tmp_path: Path) -> None:
    checkout = _checkout(tmp_path, {"dir/inner": b""})

    with pytest.raises(FleetError, match="not a file"):
        plan_repo([_file("dir", b"x\n")], checkout)


def test_plan_repo_refuses_symlinks(tmp_path: Path) -> None:
    checkout = _checkout(tmp_path, {})
    outside = tmp_path / "outside"
    outside.mkdir()
    (checkout / "linked").symlink_to(outside)

    with pytest.raises(FleetError, match="symlink"):
        plan_repo([_file("linked/a.yml", b"x\n")], checkout)


def test_write_changes_writes_only_create_and_update(tmp_path: Path) -> None:
    checkout = _checkout(tmp_path, {"keep.md": b"mine\n", "old.yml": b"old\n"})
    changes = plan_repo(
        [
            _file("keep.md", b"template\n", "seed"),
            _file("old.yml", b"new\n"),
            _file("deep/new.yml", b"n\n"),
        ],
        checkout,
    )

    write_changes(changes, checkout)

    assert (checkout / "keep.md").read_bytes() == b"mine\n"
    assert (checkout / "old.yml").read_bytes() == b"new\n"
    assert (checkout / "deep" / "new.yml").read_bytes() == b"n\n"


def test_repo_plan_reports_writes() -> None:
    create = PlannedChange(PurePosixPath("a"), "create", "sync", b"")
    same = PlannedChange(PurePosixPath("b"), "unchanged", "sync", b"")

    assert RepoPlan("r", "main", (create, same)).writes == (create,)
    assert RepoPlan("r", "main", (create, same)).has_changes
    assert not RepoPlan("r", "main", (same,)).has_changes

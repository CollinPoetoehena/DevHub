import json
from pathlib import Path
from typing import Any

import pytest

from repo_fleet import git_ops, sync, terraform_policy
from repo_fleet.errors import FleetError
from repo_fleet.inventory import Inventory, parse_inventory
from repo_fleet.paths import FleetPaths
from repo_fleet.planner import PlannedChange
from tests.fakes import FakeRunner, inventory_data, repository_entry, write_inventory

pytestmark = pytest.mark.unit


def _inventory(names: tuple[str, ...] = ("alpha",)) -> Inventory:
    return parse_inventory(
        inventory_data({name: repository_entry() for name in names}), "test"
    )


def _paths(tmp_path: Path, names: tuple[str, ...] = ("alpha",)) -> FleetPaths:
    inventory = write_inventory(
        tmp_path / "terraform" / "inventory.json",
        inventory_data({name: repository_entry() for name in names}),
    )
    templates = tmp_path / "templates"
    templates.mkdir(exist_ok=True)
    return FleetPaths(inventory, templates)


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _entry(name: str, checkout: Path) -> dict[str, Any]:
    target = checkout / "file.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(name, encoding="utf-8")
    return {
        "name": name,
        "default_branch": "main",
        "base_sha": "base",
        "status_digest": sync._digest(b""),
        "changes": [
            {
                "path": "file.txt",
                "action": "update",
                "mode": "sync",
                "digest": sync._digest(name.encode()),
            }
        ],
    }


def test_settings_apply_requires_content_preparation_before_apply(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = _paths(tmp_path)
    workdir = tmp_path / "work"
    workdir.mkdir()
    _write(
        workdir / sync.STATE_FILE,
        {"source_sha": "revision", "inventory_digest": "inventory", "settings": {}},
    )
    applied: list[bool] = []
    monkeypatch.setattr(sync, "_validate_source", lambda *_: None)
    monkeypatch.setattr(
        terraform_policy,
        "apply_plan",
        lambda *_: applied.append(True),
    )

    with pytest.raises(FleetError, match="metadata is missing or invalid"):
        sync.apply_settings(_inventory(), paths, FakeRunner(), workdir, tmp_path)

    assert applied == []


def test_prepared_output_tampering_blocks_settings_apply(
    tmp_path: Path,
) -> None:
    inventory = _inventory()
    workdir = tmp_path / "work"
    checkout = workdir / "checkouts" / "alpha"
    checkout.mkdir(parents=True)
    entry = _entry("alpha", checkout)
    entry["changes"][0]["digest"] = "0" * 64
    prepared = {
        "source_sha": "revision",
        "inventory_digest": "inventory",
        "repositories": [entry],
    }

    with pytest.raises(FleetError, match="digest changed"):
        sync._validate_prepared(
            prepared,
            {"source_sha": "revision", "inventory_digest": "inventory"},
            inventory,
            FakeRunner(),
            workdir,
            check_remote=False,
        )


def test_delivery_requires_successful_settings_apply(
    tmp_path: Path,
) -> None:
    workdir = tmp_path / "work"
    workdir.mkdir()
    _write(workdir / sync.STATE_FILE, {})
    _write(workdir / sync.PREPARED_FILE, {})

    with pytest.raises(FleetError, match="settings-applied.json"):
        sync.deliver(
            _inventory(),
            _paths(tmp_path),
            FakeRunner(),
            workdir,
            tmp_path,
        )


def test_delivery_continues_after_one_repository_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    inventory = _inventory(("alpha", "beta"))
    paths = _paths(tmp_path, ("alpha", "beta"))
    workdir = tmp_path / "work"
    entries = [_entry(name, workdir / "checkouts" / name) for name in ("alpha", "beta")]
    _write(
        workdir / sync.STATE_FILE,
        {
            "source_sha": "revision",
            "inventory_digest": "inventory",
            "settings": {"plan_digest": "saved-plan"},
        },
    )
    _write(
        workdir / sync.PREPARED_FILE,
        {
            "source_sha": "revision",
            "inventory_digest": "inventory",
            "repositories": entries,
        },
    )
    _write(
        workdir / sync.APPLIED_FILE,
        {
            "source_sha": "revision",
            "inventory_digest": "inventory",
            "prepared_digest": sync._file_digest(workdir / sync.PREPARED_FILE),
            "plan_digest": "saved-plan",
        },
    )
    monkeypatch.setattr(sync, "_validate_source", lambda *_: None)
    monkeypatch.setattr(sync, "_validate_prepared", lambda *_args, **_kwargs: None)
    delivered: list[str] = []

    def deliver_one(
        _runner: FakeRunner,
        slug: str,
        _branch: str,
        _checkout: Path,
        _changes: tuple[PlannedChange, ...],
        **_kwargs: str,
    ) -> git_ops.SyncResult:
        delivered.append(slug)
        if slug == "octo/alpha":
            raise FleetError("simulated delivery failure")
        return git_ops.SyncResult(pushed=True, pull_request="created #1")

    monkeypatch.setattr(git_ops, "sync_checkout", deliver_one)

    with pytest.raises(FleetError, match="delivery failed for 1"):
        sync.deliver(inventory, paths, FakeRunner(), workdir, tmp_path)

    assert delivered == ["octo/alpha", "octo/beta"]
    assert "changed=2 failed=1" in capsys.readouterr().out


def test_cleanup_only_removes_named_runner_temp_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path))
    workdir = tmp_path / "repo-fleet-sync-17-1"
    workdir.mkdir()
    (workdir / "saved-plan").write_text("private", encoding="utf-8")

    sync.cleanup(workdir)

    assert not workdir.exists()
    with pytest.raises(FleetError, match="refusing to clean"):
        sync.cleanup(tmp_path / "other")

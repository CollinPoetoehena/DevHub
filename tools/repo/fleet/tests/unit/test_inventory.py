import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from repo_fleet.errors import InventoryError
from repo_fleet.inventory import Repository, load_inventory, parse_inventory
from tests.fakes import inventory_data, repository_entry, write_inventory

pytestmark = pytest.mark.unit

Mutation = Callable[[dict[str, Any]], object]


def _inventory(data: dict[str, Any]) -> dict[str, Any]:
    inner: dict[str, Any] = data["inventory"]
    return inner


def _alpha(data: dict[str, Any]) -> dict[str, Any]:
    repo: dict[str, Any] = _inventory(data)["repositories"]["alpha"]
    return repo


def test_load_inventory_parses_sorted_repositories(tmp_path: Path) -> None:
    data = inventory_data(
        {
            "zeta": repository_entry(archived=True),
            "alpha": repository_entry("private", ["common", "python"]),
        }
    )
    inventory = load_inventory(write_inventory(tmp_path / "inv.json", data))

    assert inventory.owner == "octo"
    assert inventory.repositories == (
        Repository("alpha", "private", ("common", "python"), False),
        Repository("zeta", "public", ("common",), True),
    )
    assert [repo.name for repo in inventory.active()] == ["alpha"]
    assert inventory.find("zeta") == inventory.repositories[1]
    assert inventory.find("missing") is None
    assert inventory.slug(inventory.repositories[0]) == "octo/alpha"


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda d: d.update(extra=1), "(root) has unknown keys: ['extra']"),
        (lambda d: d.pop("inventory"), "(root) is missing keys: ['inventory']"),
        (lambda d: d.update(inventory=[]), "inventory must be an object"),
        (lambda d: _inventory(d).update(owner=""), "owner must be a non-empty"),
        (lambda d: _inventory(d).update(owner=7), "owner must be a non-empty"),
        (lambda d: _inventory(d).update(extra=1), "unknown keys: ['extra']"),
        (lambda d: _inventory(d).update(repositories=[]), "repositories must be"),
        (
            lambda d: _inventory(d)["repositories"].update({"bad/name": {}}),
            "name must match",
        ),
        (lambda d: _alpha(d).pop("archived"), "missing keys: ['archived']"),
        (lambda d: _alpha(d).update(topics=[]), "unknown keys: ['topics']"),
        (lambda d: _alpha(d).update(visibility="internal"), "visibility must be"),
        (lambda d: _alpha(d).update(visibility=["public"]), "visibility must be"),
        (lambda d: _alpha(d).update(archived="false"), "archived must be a boolean"),
        (lambda d: _alpha(d).update(archived=0), "archived must be a boolean"),
        (lambda d: _alpha(d).update(profiles=[]), "profiles must be a non-empty"),
        (lambda d: _alpha(d).update(profiles="common"), "profiles must be a non-empty"),
        (lambda d: _alpha(d).update(profiles=["common", 1]), "non-empty strings"),
        (
            lambda d: _alpha(d).update(profiles=["common", "common"]),
            "must be unique",
        ),
        (lambda d: _alpha(d).update(profiles=["python", "common"]), "start with"),
        (lambda d: _inventory(d)["repositories"].update(alpha=[]), "must be an obj"),
        (
            lambda d: _alpha(d).update(apm_stacks=["python", "python"]),
            "apm_stacks must be unique",
        ),
        (
            lambda d: _alpha(d).update(apm_stacks=["unknown"]),
            "unknown stacks",
        ),
        (
            lambda d: _alpha(d).update(apm_stacks="python"),
            "apm_stacks must be a list",
        ),
    ],
)
def test_parse_inventory_rejects_invalid_data(mutate: Mutation, message: str) -> None:
    data: dict[str, Any] = json.loads(json.dumps(inventory_data()))
    mutate(data)

    with pytest.raises(InventoryError, match="inv.json") as excinfo:
        parse_inventory(data, source="inv.json")

    assert message in str(excinfo.value)


def test_parse_inventory_rejects_non_object_root() -> None:
    with pytest.raises(InventoryError, match=r"\(root\) must be an object"):
        parse_inventory([], source="inv.json")


def test_parse_inventory_defaults_apm_stacks_to_empty() -> None:
    inventory = parse_inventory(inventory_data(), source="inv.json")

    assert inventory.repositories[0].apm_stacks == ()


def test_parse_inventory_accepts_apm_stacks() -> None:
    data = inventory_data({"alpha": repository_entry()})
    inventory = data["inventory"]
    assert isinstance(inventory, dict)
    repositories = inventory["repositories"]
    assert isinstance(repositories, dict)
    repository = repositories["alpha"]
    assert isinstance(repository, dict)
    repository["apm_stacks"] = ["python", "iac"]

    inventory = parse_inventory(data, source="inv.json")

    assert inventory.repositories[0].apm_stacks == ("python", "iac")


def test_load_inventory_reports_missing_file(tmp_path: Path) -> None:
    with pytest.raises(InventoryError, match="cannot read inventory"):
        load_inventory(tmp_path / "missing.json")


def test_load_inventory_reports_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "inv.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(InventoryError, match="invalid JSON"):
        load_inventory(path)


def test_load_inventory_rejects_duplicate_keys(tmp_path: Path) -> None:
    path = tmp_path / "inv.json"
    path.write_text('{"inventory": {}, "inventory": {}}', encoding="utf-8")

    with pytest.raises(InventoryError, match="duplicate keys"):
        load_inventory(path)

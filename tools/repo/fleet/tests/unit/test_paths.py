from pathlib import Path

import pytest

from repo_fleet.errors import FleetError
from repo_fleet.paths import (
    INVENTORY_ENV_VAR,
    TEMPLATES_ENV_VAR,
    FleetPaths,
    find_tool_root,
    resolve_paths,
)
from tests.fakes import inventory_data, write_inventory

pytestmark = pytest.mark.unit


def _tool_root(tmp_path: Path) -> Path:
    root = tmp_path / "tools" / "repo"
    write_inventory(root / "terraform" / "repositories.auto.tfvars.json", {})
    (root / "templates").mkdir()
    (root / "fleet" / "src").mkdir(parents=True)
    return root


def test_find_tool_root_searches_upward(tmp_path: Path) -> None:
    root = _tool_root(tmp_path)

    assert find_tool_root([tmp_path, root / "fleet" / "src"]) == root.resolve()


def test_find_tool_root_returns_none_without_match(tmp_path: Path) -> None:
    assert find_tool_root([tmp_path]) is None


def test_resolve_paths_prefers_arguments_over_environment(tmp_path: Path) -> None:
    env = {INVENTORY_ENV_VAR: "env.json", TEMPLATES_ENV_VAR: "env-templates"}

    paths = resolve_paths(Path("a.json"), Path("tpl"), environ=env, search_starts=[])

    assert paths == FleetPaths(Path("a.json"), Path("tpl"))


def test_resolve_paths_uses_environment(tmp_path: Path) -> None:
    env = {INVENTORY_ENV_VAR: "env.json", TEMPLATES_ENV_VAR: "env-templates"}

    paths = resolve_paths(None, None, environ=env, search_starts=[])

    assert paths == FleetPaths(Path("env.json"), Path("env-templates"))


def test_resolve_paths_discovers_missing_values(tmp_path: Path) -> None:
    root = _tool_root(tmp_path).resolve()

    paths = resolve_paths(
        Path("custom.json"), None, environ={}, search_starts=[root / "fleet"]
    )

    assert paths == FleetPaths(Path("custom.json"), root / "templates")


def test_resolve_paths_fails_when_nothing_is_found(tmp_path: Path) -> None:
    write_inventory(tmp_path / "x.json", inventory_data())

    with pytest.raises(FleetError, match="cannot locate tools/repo"):
        resolve_paths(None, None, environ={}, search_starts=[tmp_path])

"""Locate the inventory file and templates directory."""

import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

from repo_fleet.errors import FleetError

INVENTORY_RELATIVE_PATH = Path("terraform") / "repositories.auto.tfvars.json"
TEMPLATES_RELATIVE_PATH = Path("templates")
INVENTORY_ENV_VAR = "REPO_FLEET_INVENTORY"
TEMPLATES_ENV_VAR = "REPO_FLEET_TEMPLATES"


@dataclass(frozen=True)
class FleetPaths:
    inventory: Path
    templates: Path


def is_tool_root(candidate: Path) -> bool:
    return (candidate / INVENTORY_RELATIVE_PATH).is_file() and (
        candidate / TEMPLATES_RELATIVE_PATH
    ).is_dir()


def find_tool_root(starts: Iterable[Path]) -> Path | None:
    """Return the first directory, searching upward from each start, that holds
    both the inventory file and the templates directory."""
    for start in starts:
        resolved = start.resolve()
        for candidate in (resolved, *resolved.parents):
            if is_tool_root(candidate):
                return candidate
    return None


def default_search_starts() -> tuple[Path, ...]:
    return (Path(__file__).parent, Path.cwd())


def resolve_paths(
    inventory: Path | None,
    templates: Path | None,
    environ: Mapping[str, str] | None = None,
    search_starts: Iterable[Path] | None = None,
) -> FleetPaths:
    """Resolve paths with precedence: explicit argument, environment, discovery."""
    env = os.environ if environ is None else environ
    inventory = inventory or _env_path(env, INVENTORY_ENV_VAR)
    templates = templates or _env_path(env, TEMPLATES_ENV_VAR)
    if inventory is not None and templates is not None:
        return FleetPaths(inventory=inventory, templates=templates)

    starts = default_search_starts() if search_starts is None else search_starts
    root = find_tool_root(starts)
    if root is None:
        raise FleetError(
            "cannot locate tools/repo: pass --inventory and --templates or set "
            f"{INVENTORY_ENV_VAR} and {TEMPLATES_ENV_VAR}"
        )
    return FleetPaths(
        inventory=inventory or root / INVENTORY_RELATIVE_PATH,
        templates=templates or root / TEMPLATES_RELATIVE_PATH,
    )


def _env_path(environ: Mapping[str, str], name: str) -> Path | None:
    value = environ.get(name, "").strip()
    return Path(value) if value else None

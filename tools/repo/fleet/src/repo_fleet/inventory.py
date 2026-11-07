"""Load and validate the repository inventory shared with Terraform."""

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from repo_fleet.errors import InventoryError

REPOSITORY_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
VISIBILITIES = frozenset({"public", "private"})
REQUIRED_PROFILE = "common"
APM_STACKS = frozenset({"containerization", "go", "iac", "java", "python", "rust"})
TOP_LEVEL_KEYS = frozenset({"inventory"})
INVENTORY_KEYS = frozenset({"owner", "repositories"})
REPOSITORY_KEYS = frozenset({"visibility", "profiles", "archived"})
OPTIONAL_REPOSITORY_KEYS = frozenset({"apm_stacks"})


@dataclass(frozen=True)
class Repository:
    name: str
    visibility: str
    profiles: tuple[str, ...]
    archived: bool
    apm_stacks: tuple[str, ...] = ()


@dataclass(frozen=True)
class Inventory:
    owner: str
    repositories: tuple[Repository, ...]

    def find(self, name: str) -> Repository | None:
        return next((repo for repo in self.repositories if repo.name == name), None)

    def active(self) -> tuple[Repository, ...]:
        return tuple(repo for repo in self.repositories if not repo.archived)

    def slug(self, repository: Repository) -> str:
        return f"{self.owner}/{repository.name}"


def load_inventory(path: Path) -> Inventory:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as err:
        raise InventoryError(f"{path}: cannot read inventory: {err}") from err
    try:
        data = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except ValueError as err:
        raise InventoryError(f"{path}: invalid JSON: {err}") from err
    return parse_inventory(data, source=str(path))


def parse_inventory(data: object, source: str) -> Inventory:
    root = _require_object(data, source, "(root)", TOP_LEVEL_KEYS)
    inventory = _require_object(root["inventory"], source, "inventory", INVENTORY_KEYS)

    owner = inventory["owner"]
    if not isinstance(owner, str) or not owner.strip():
        raise InventoryError(f"{source}: inventory.owner must be a non-empty string")

    repositories = inventory["repositories"]
    if not isinstance(repositories, dict):
        raise InventoryError(f"{source}: inventory.repositories must be an object")
    parsed = tuple(
        _parse_repository(name, value, source)
        for name, value in sorted(repositories.items())
    )
    return Inventory(owner=owner, repositories=parsed)


def _parse_repository(name: str, value: object, source: str) -> Repository:
    key = f"inventory.repositories.{name}"
    if not REPOSITORY_NAME_PATTERN.fullmatch(name):
        raise InventoryError(
            f"{source}: {key}: name must match {REPOSITORY_NAME_PATTERN.pattern}"
        )
    fields = _require_object(
        value, source, key, REPOSITORY_KEYS, OPTIONAL_REPOSITORY_KEYS
    )

    visibility = fields["visibility"]
    if not isinstance(visibility, str) or visibility not in VISIBILITIES:
        raise InventoryError(
            f"{source}: {key}.visibility must be one of {sorted(VISIBILITIES)}"
        )

    archived = fields["archived"]
    if not isinstance(archived, bool):
        raise InventoryError(f"{source}: {key}.archived must be a boolean")

    return Repository(
        name=name,
        visibility=visibility,
        profiles=_parse_profiles(fields["profiles"], source, key),
        archived=archived,
        apm_stacks=_parse_apm_stacks(fields.get("apm_stacks", []), source, key),
    )


def _parse_profiles(value: object, source: str, key: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise InventoryError(f"{source}: {key}.profiles must be a non-empty list")
    if not all(isinstance(item, str) and item for item in value):
        raise InventoryError(f"{source}: {key}.profiles must contain non-empty strings")
    if len(set(value)) != len(value):
        raise InventoryError(f"{source}: {key}.profiles must be unique")
    if value[0] != REQUIRED_PROFILE:
        raise InventoryError(
            f"{source}: {key}.profiles must start with {REQUIRED_PROFILE!r}"
        )
    return tuple(value)


def _parse_apm_stacks(value: object, source: str, key: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise InventoryError(f"{source}: {key}.apm_stacks must be a list")
    if not all(isinstance(item, str) and item for item in value):
        raise InventoryError(
            f"{source}: {key}.apm_stacks must contain non-empty strings"
        )
    if len(set(value)) != len(value):
        raise InventoryError(f"{source}: {key}.apm_stacks must be unique")
    unknown = sorted(set(value) - APM_STACKS)
    if unknown:
        raise InventoryError(
            f"{source}: {key}.apm_stacks contains unknown stacks: {unknown}"
        )
    return tuple(value)


def _require_object(
    value: object,
    source: str,
    key: str,
    expected: frozenset[str],
    optional: frozenset[str] = frozenset(),
) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise InventoryError(f"{source}: {key} must be an object")
    missing = sorted(expected - value.keys())
    if missing:
        raise InventoryError(f"{source}: {key} is missing keys: {missing}")
    unknown = sorted(value.keys() - expected - optional)
    if unknown:
        raise InventoryError(f"{source}: {key} has unknown keys: {unknown}")
    return value


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    keys = [key for key, _ in pairs]
    duplicates = sorted({key for key in keys if keys.count(key) > 1})
    if duplicates:
        raise ValueError(f"duplicate keys: {duplicates}")
    return dict(pairs)

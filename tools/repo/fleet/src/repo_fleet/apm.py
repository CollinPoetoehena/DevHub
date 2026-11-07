"""Prepare APM package refreshes in disposable repository checkouts."""

import hashlib
import os
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from typing import Literal

import yaml

from repo_fleet.errors import FleetError
from repo_fleet.planner import PlannedChange
from repo_fleet.runner import CommandRunner
from repo_fleet.templates import RenderedFile

APM_VERSION = "0.35.0"
APM_TIMEOUT_SECONDS = 300
APM_MANIFEST = PurePosixPath("apm.yml")
APM_LOCK = PurePosixPath("apm.lock.yaml")
LEGACY_CALLER = PurePosixPath(".github/workflows/devhub-apm-sync.yml")
APM_CREDENTIAL_KEYS = (
    "GH_TOKEN",
    "GITHUB_TOKEN",
    "GH_ENTERPRISE_TOKEN",
    "GITHUB_ENTERPRISE_TOKEN",
    "TF_TOKEN_app_terraform_io",
    "TF_CLOUD_TOKEN",
    "GITHUB_APP_ID",
    "GITHUB_APP_INSTALLATION_ID",
    "GITHUB_APP_PEM_FILE",
    "ACTIONS_RUNTIME_TOKEN",
    "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
    "ACTIONS_ID_TOKEN_REQUEST_URL",
    "TF_CLI_CONFIG_FILE",
    "GIT_ASKPASS",
    "SSH_AUTH_SOCK",
)
TOKEN_ENV = {key: None for key in APM_CREDENTIAL_KEYS}
MANAGED_REPOSITORY = "collinpoetoehena/devhub"
MANAGED_PACKAGE = re.compile(
    rf"^{re.escape(MANAGED_REPOSITORY)}/packages/apm/"
    r"(containerization|go|iac|java|python|rust|common)(?:#([^#]+))?$",
    re.IGNORECASE,
)
UPDATED_ROW = re.compile(
    r"^\s+\[~\]\s+([A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)+)\s*$", re.MULTILINE
)
UPDATED_COUNT = re.compile(r"^\s+(\d+) updated\s*$", re.MULTILINE)
SHA256_HASH = re.compile(r"^sha256:[a-f0-9]{64}$")
LEGACY_CALLER_CONTENT = (
    b"# Managed by DevHub tools/repo (templates/common/sync); "
    b"local changes are overwritten.\n"
    b"name: DevHub APM sync\n"
    b"\n"
    b"on:\n"
    b"  push:\n"
    b"    branches: [main]\n"
    b"  schedule:\n"
    b'    - cron: "0 6 * * 1"\n'
    b"  workflow_dispatch:\n"
    b"\n"
    b"permissions: {}\n"
    b"\n"
    b"jobs:\n"
    b"  apm-sync:\n"
    b"    permissions:\n"
    b"      contents: write\n"
    b"      pull-requests: write\n"
    b"    # Tracks DevHub main on purpose so every repository gets sync fixes "
    b"without a template change.\n"
    b"    uses: CollinPoetoehena/DevHub/.github/workflows/apm-sync.yml@main "
    b"# zizmor: ignore[unpinned-uses]\n"
)

Freshness = Literal["CURRENT", "UPDATE_REQUIRED", "PINNED"]


class StrictSafeLoader(yaml.SafeLoader):
    pass


def _construct_mapping(
    loader: StrictSafeLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[object, object]:
    mapping: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            hash(key)
        except TypeError as err:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "unhashable mapping key",
                key_node.start_mark,
            ) from err
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


StrictSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)


@dataclass(frozen=True)
class APMManifest:
    required_stacks: tuple[str, ...]
    managed_refs: tuple[tuple[str, str], ...]
    pinned_stacks: tuple[str, ...]
    has_local_dependencies: bool


@dataclass(frozen=True)
class APMStatus:
    freshness: Freshness
    update_selectors: tuple[str, ...]


@dataclass(frozen=True)
class APMPreparation:
    changes: tuple[PlannedChange, ...]
    freshness: Freshness


def prepare_apm_sync(
    checkout: Path,
    runner: CommandRunner,
    rendered: Sequence[RenderedFile],
    required_stacks: tuple[str, ...],
    template_changes: tuple[PlannedChange, ...],
    include_diff: bool,
) -> APMPreparation:
    with TemporaryDirectory(prefix="repo-fleet-apm-gh-") as gh_config_dir:
        apm_environment = {
            **TOKEN_ENV,
            **{
                key: None
                for key in os.environ
                if key.startswith(
                    ("TF_", "GITHUB_", "ACTIONS_", "RUNNER_", "FLEET_SYNC_")
                )
                or (key.startswith("GH_") and "TOKEN" in key)
            },
            "GH_CONFIG_DIR": gh_config_dir,
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.hooksPath",
            "GIT_CONFIG_VALUE_0": os.devnull,
        }
        return _prepare_apm_sync(
            checkout,
            runner,
            rendered,
            required_stacks,
            template_changes,
            include_diff,
            apm_environment,
        )


def _prepare_apm_sync(
    checkout: Path,
    runner: CommandRunner,
    rendered: Sequence[RenderedFile],
    required_stacks: tuple[str, ...],
    template_changes: tuple[PlannedChange, ...],
    include_diff: bool,
    apm_environment: Mapping[str, str | None],
) -> APMPreparation:
    manifest_path = checkout / APM_MANIFEST
    if manifest_path.is_symlink() or (
        manifest_path.exists() and not manifest_path.is_file()
    ):
        raise FleetError(f"{APM_MANIFEST}: expected a regular file, not a symlink")
    original_manifest = manifest_path.read_bytes() if manifest_path.exists() else None
    seed = next((item.content for item in rendered if item.path == APM_MANIFEST), None)
    if original_manifest is None:
        if seed is None:
            raise FleetError(f"{APM_MANIFEST}: no seed template is available")
        manifest_path.write_bytes(seed)
    manifest = _load_manifest(manifest_path, required_stacks)
    lock_path = checkout / APM_LOCK
    if lock_path.is_symlink() or (lock_path.exists() and not lock_path.is_file()):
        raise FleetError(f"{APM_LOCK}: expected a regular file, not a symlink")
    old_lock = _load_lock(lock_path) if lock_path.exists() else None
    old_deployed = _deployed_files(old_lock) if old_lock is not None else frozenset()
    if old_lock is not None:
        _verify_deployed_files(checkout, old_lock)

    legacy_change = _legacy_caller_change(checkout, include_diff)
    _verify_cli(runner, checkout, apm_environment)
    status = _freshness(runner, checkout, manifest, apm_environment)
    gitignore = checkout / ".gitignore"
    if gitignore.is_symlink():
        raise FleetError(".gitignore: refusing APM sync through a symlink")
    original_gitignore = gitignore.read_bytes() if gitignore.exists() else None
    try:
        _apply_apm_update(runner, checkout, status, apm_environment)
    finally:
        _restore_file(gitignore, original_gitignore)

    if (
        original_manifest is not None
        and manifest_path.read_bytes() != original_manifest
    ):
        raise FleetError("apm.yml changed during APM sync; refusing to overwrite it")
    if lock_path.is_symlink() or not lock_path.is_file():
        raise FleetError(f"{APM_LOCK}: APM sync did not produce a regular lockfile")
    new_lock = _load_lock(lock_path)
    _verify_deployed_files(checkout, new_lock)
    new_deployed = _deployed_files(new_lock)
    allowed_paths = (
        {change.path for change in template_changes}
        | old_deployed
        | new_deployed
        | {APM_LOCK}
    )
    if original_manifest is None:
        allowed_paths.add(APM_MANIFEST)
    if legacy_change is not None:
        allowed_paths.add(LEGACY_CALLER)
    return APMPreparation(
        changes=_collect_changes(
            checkout,
            runner,
            allowed_paths,
            old_deployed,
            new_deployed,
            template_changes,
            legacy_change,
            include_diff,
        ),
        freshness=status.freshness,
    )


def _load_manifest(path: Path, required_stacks: tuple[str, ...]) -> APMManifest:
    data = _load_yaml(path)
    if not isinstance(data, dict):
        raise FleetError(f"{path}: APM manifest must be a mapping")
    dependencies = data.get("dependencies")
    if not isinstance(dependencies, dict):
        raise FleetError(f"{path}: dependencies must be a mapping")
    apm_dependencies = dependencies.get("apm")
    if not isinstance(apm_dependencies, list):
        raise FleetError(f"{path}: dependencies.apm must be a list")
    if not all(isinstance(item, str) and item.strip() for item in apm_dependencies):
        raise FleetError(f"{path}: dependencies.apm must contain strings")
    _validate_local_dependencies(path.parent, apm_dependencies)

    required = ("common", *required_stacks)
    refs: list[tuple[str, str]] = []
    pinned: list[str] = []
    managed_stacks = tuple(
        stack
        for dependency in apm_dependencies
        if (stack := _managed_dependency(dependency)) is not None
    )
    if len(managed_stacks) != len(set(managed_stacks)):
        raise FleetError(f"{path}: duplicate DevHub APM stack dependencies")
    found = set(managed_stacks)
    for dependency in apm_dependencies:
        match = MANAGED_PACKAGE.fullmatch(dependency)
        if match is None:
            continue
        stack, ref = match.groups()
        normalized_stack = stack.lower()
        if ref == "main":
            refs.append(
                (
                    normalized_stack,
                    f"{MANAGED_REPOSITORY}/packages/apm/{normalized_stack}",
                )
            )
        else:
            pinned.append(normalized_stack)
    missing = sorted(set(required) - found)
    if missing:
        raise FleetError(
            f"{path}: missing required DevHub APM dependencies: {', '.join(missing)}"
        )
    return APMManifest(
        required_stacks=required,
        managed_refs=tuple(refs),
        pinned_stacks=tuple(sorted(set(pinned))),
        has_local_dependencies=any(
            dependency.startswith(("./", "../", "/")) for dependency in apm_dependencies
        ),
    )


def _managed_dependency(dependency: str) -> str | None:
    match = MANAGED_PACKAGE.fullmatch(dependency)
    return match.group(1).lower() if match is not None else None


def _validate_local_dependencies(checkout: Path, dependencies: list[str]) -> None:
    root = checkout.resolve()
    for dependency in dependencies:
        if not dependency.startswith(("./", "../", "/")):
            continue
        path = PurePosixPath(dependency)
        if path.is_absolute() or "\\" in dependency or ".." in path.parts:
            raise FleetError(f"{dependency}: unsafe local APM dependency path")
        target = root.joinpath(*path.parts)
        for candidate in (target, *target.parents):
            if candidate == root:
                break
            if candidate.is_symlink():
                raise FleetError(
                    f"{dependency}: local APM dependency path is a symlink"
                )
        resolved = target.resolve()
        if not resolved.is_relative_to(root):
            raise FleetError(f"{dependency}: local APM dependency escapes checkout")
        package_manifest = resolved / "apm.yml"
        if (
            not resolved.is_dir()
            or package_manifest.is_symlink()
            or not package_manifest.is_file()
        ):
            raise FleetError(f"{dependency}: local APM dependency has no apm.yml")


def _freshness(
    runner: CommandRunner,
    checkout: Path,
    manifest: APMManifest,
    apm_environment: Mapping[str, str | None] | None = None,
) -> APMStatus:
    lock_path = checkout / APM_LOCK
    selectors = tuple(selector for _, selector in manifest.managed_refs)
    if not lock_path.is_file():
        return APMStatus("UPDATE_REQUIRED", selectors)
    if not selectors:
        if manifest.has_local_dependencies:
            return APMStatus("UPDATE_REQUIRED", ())
        return APMStatus("PINNED" if manifest.pinned_stacks else "CURRENT", ())
    result = runner.run(
        ["apm", "update", "--dry-run", "--target", "copilot", *selectors],
        cwd=checkout,
        env=TOKEN_ENV if apm_environment is None else apm_environment,
        timeout=APM_TIMEOUT_SECONDS,
    )
    freshness = _classify_update_output(result.stdout, manifest.managed_refs)
    if freshness == "CURRENT" and manifest.has_local_dependencies:
        return APMStatus("UPDATE_REQUIRED", ())
    return APMStatus(freshness, selectors if freshness == "UPDATE_REQUIRED" else ())


def _classify_update_output(
    output: str, managed_refs: tuple[tuple[str, str], ...]
) -> Freshness:
    requested = {stack for stack, _ in managed_refs}
    rows = tuple(UPDATED_ROW.finditer(output))
    count_matches = tuple(UPDATED_COUNT.finditer(output))
    count_match = count_matches[0] if len(count_matches) == 1 else None
    if count_match is None:
        if (
            not rows
            and not count_matches
            and output.strip().endswith(
                "[+] All dependencies already at their latest matching refs."
            )
        ):
            return "CURRENT"
        raise FleetError("APM 0.35.0 returned an unrecognized update plan")
    if "Update plan for apm.yml" not in output:
        raise FleetError("APM 0.35.0 returned an ambiguous update plan")
    updated = {match.group(1).lower() for match in rows}
    expected = {f"collinpoetoehena/devhub/packages/apm/{stack}" for stack in requested}
    if int(count_match.group(1)) != len(rows):
        raise FleetError("APM 0.35.0 update count does not match its update rows")
    if len(updated) != len(rows):
        raise FleetError("APM 0.35.0 update plan contains duplicate rows")
    if updated:
        if not updated <= expected:
            raise FleetError("APM update output contains an unrequested dependency")
        return "UPDATE_REQUIRED"
    if int(count_match.group(1)) != 0:
        raise FleetError("APM 0.35.0 returned an ambiguous update plan")
    return "CURRENT"


def _verify_cli(
    runner: CommandRunner,
    checkout: Path,
    apm_environment: Mapping[str, str | None] | None = None,
) -> None:
    result = runner.run(
        ["apm", "--version"],
        cwd=checkout,
        env=TOKEN_ENV if apm_environment is None else apm_environment,
        timeout=APM_TIMEOUT_SECONDS,
    )
    version_pattern = rf"(?<![\d.]){re.escape(APM_VERSION)}(?![\d.])"
    if re.search(version_pattern, result.stdout) is None:
        raise FleetError(
            f"APM CLI {APM_VERSION} is required; found {result.stdout.strip()!r}"
        )


def _apply_apm_update(
    runner: CommandRunner,
    checkout: Path,
    status: APMStatus,
    apm_environment: Mapping[str, str | None] | None = None,
) -> None:
    lock_path = checkout / APM_LOCK
    had_lock = lock_path.is_file()
    has_local_dependencies = _manifest_has_local_dependency(checkout)
    if not had_lock:
        args = ["apm", "install", "--only", "apm", "--target", "copilot"]
    elif status.freshness == "UPDATE_REQUIRED" and status.update_selectors:
        args = [
            "apm",
            "update",
            "--yes",
            "--target",
            "copilot",
            *status.update_selectors,
        ]
    else:
        args = []
    if args:
        runner.run(
            args,
            cwd=checkout,
            env=TOKEN_ENV if apm_environment is None else apm_environment,
            timeout=APM_TIMEOUT_SECONDS,
        )
    if status.freshness == "UPDATE_REQUIRED" and had_lock and has_local_dependencies:
        runner.run(
            ["apm", "install", "--only", "apm", "--target", "copilot"],
            cwd=checkout,
            env=TOKEN_ENV if apm_environment is None else apm_environment,
            timeout=APM_TIMEOUT_SECONDS,
        )


def _manifest_has_local_dependency(checkout: Path) -> bool:
    manifest = _load_yaml(checkout / APM_MANIFEST)
    dependencies = manifest.get("dependencies") if isinstance(manifest, dict) else None
    apm_dependencies = (
        dependencies.get("apm") if isinstance(dependencies, dict) else None
    )
    return isinstance(apm_dependencies, list) and any(
        isinstance(item, str) and item.startswith(("./", "../", "/"))
        for item in apm_dependencies
    )


def _legacy_caller_change(checkout: Path, include_diff: bool) -> PlannedChange | None:
    target = checkout / LEGACY_CALLER
    if target.is_symlink():
        raise FleetError(f"{LEGACY_CALLER}: legacy caller must not be a symlink")
    if not target.exists():
        return None
    if not target.is_file():
        raise FleetError(f"{LEGACY_CALLER}: legacy caller is not a regular file")
    current = target.read_bytes()
    if current != LEGACY_CALLER_CONTENT:
        raise FleetError(
            f"{LEGACY_CALLER}: customized legacy caller is preserved; "
            "remove it manually after review"
        )
    diff = None
    if include_diff:
        diff = (
            "\n".join(
                [
                    f"--- a/{LEGACY_CALLER}",
                    "+++ /dev/null",
                    *[f"-{line}" for line in current.decode().splitlines()],
                ]
            )
            + "\n"
        )
    target.unlink()
    return PlannedChange(LEGACY_CALLER, "delete", "sync", b"", diff)


def _load_lock(path: Path) -> Mapping[str, object]:
    data = _load_yaml(path)
    if not isinstance(data, dict) or not isinstance(data.get("dependencies"), list):
        raise FleetError(f"{path}: malformed APM lockfile")
    if not isinstance(data.get("apm_version"), str):
        raise FleetError(f"{path}: APM lockfile is missing apm_version")
    return data


def _deployed_files(lock: Mapping[str, object] | None) -> frozenset[PurePosixPath]:
    if lock is None:
        return frozenset()
    dependencies = lock.get("dependencies")
    if not isinstance(dependencies, list):
        raise FleetError(f"{APM_LOCK}: dependencies must be a list")
    files: set[PurePosixPath] = set()
    for dependency in dependencies:
        if not isinstance(dependency, dict):
            raise FleetError(f"{APM_LOCK}: dependency entry must be a mapping")
        deployed = dependency.get("deployed_files", [])
        if not isinstance(deployed, list) or not all(
            isinstance(path, str) for path in deployed
        ):
            raise FleetError(f"{APM_LOCK}: deployed_files must contain paths")
        files.update(_safe_relative_path(path) for path in deployed)
    return frozenset(files)


def _verify_deployed_files(checkout: Path, lock: Mapping[str, object]) -> None:
    deployed = _deployed_files(lock)
    hashes_by_path: dict[PurePosixPath, str] = {}
    dependencies = lock.get("dependencies")
    if not isinstance(dependencies, list):
        raise FleetError(f"{APM_LOCK}: dependencies must be a list")
    for dependency in dependencies:
        if not isinstance(dependency, dict):
            raise FleetError(f"{APM_LOCK}: dependency entry must be a mapping")
        hashes = dependency.get("deployed_file_hashes", {})
        if not isinstance(hashes, dict):
            raise FleetError(f"{APM_LOCK}: deployed_file_hashes must be a mapping")
        for relative, expected in hashes.items():
            if not isinstance(relative, str) or not isinstance(expected, str):
                raise FleetError(f"{APM_LOCK}: malformed deployed file hash")
            if not SHA256_HASH.fullmatch(expected):
                raise FleetError(f"{APM_LOCK}: malformed deployed file hash")
            path = _safe_relative_path(relative)
            if path in hashes_by_path and hashes_by_path[path] != expected:
                raise FleetError(f"{path}: conflicting APM deployment hashes")
            hashes_by_path[path] = expected
    if not set(hashes_by_path) <= deployed:
        raise FleetError(f"{APM_LOCK}: deployed hashes reference unlisted files")
    for relative in deployed:
        target = _safe_target(checkout, relative)
        if target.is_dir():
            continue
        expected = hashes_by_path.get(relative)
        if expected is None:
            if target.exists():
                raise FleetError(f"{relative}: managed file has no recorded hash")
            continue
        if target.exists() and not target.is_file():
            raise FleetError(f"{relative}: managed deployment is not a regular file")
        if target.exists():
            digest = f"sha256:{hashlib.sha256(target.read_bytes()).hexdigest()}"
            if digest != expected:
                raise FleetError(f"{relative}: managed APM file was locally modified")


def _collect_changes(
    checkout: Path,
    runner: CommandRunner,
    allowed_paths: set[PurePosixPath],
    old_deployed: frozenset[PurePosixPath],
    new_deployed: frozenset[PurePosixPath],
    template_changes: tuple[PlannedChange, ...],
    legacy_change: PlannedChange | None,
    include_diff: bool,
) -> tuple[PlannedChange, ...]:
    changed = _git_paths(runner, checkout)
    template_by_path = {change.path: change for change in template_changes}
    tracked = _tracked_paths(runner, checkout)
    changes: list[PlannedChange] = []
    for relative in sorted(changed):
        if relative.parts[0] == "apm_modules":
            continue
        if relative not in allowed_paths:
            raise FleetError(f"{relative}: APM sync changed an unowned path")
        target = checkout.joinpath(*relative.parts)
        if target.is_symlink():
            raise FleetError(f"{relative}: APM sync produced a symlink")
        template = template_by_path.get(relative)
        if not target.exists():
            if relative not in old_deployed and relative != LEGACY_CALLER:
                raise FleetError(f"{relative}: APM sync deleted an unowned path")
            change = (
                legacy_change
                if relative == LEGACY_CALLER
                else PlannedChange(relative, "delete", "sync", b"")
            )
            if change is not None:
                changes.append(change)
            continue
        if not target.is_file():
            raise FleetError(f"{relative}: APM sync produced a non-file path")
        action: Literal["create", "update"] = (
            "create" if relative not in tracked else "update"
        )
        mode = template.mode if template is not None else "sync"
        content = target.read_bytes()
        diff = None
        if include_diff and action == "create":
            diff = (
                "\n".join(
                    ["--- /dev/null", f"+++ b/{relative}"]
                    + [
                        f"+{line}"
                        for line in content.decode(errors="replace").splitlines()
                    ]
                )
                + "\n"
            )
        elif include_diff:
            diff = runner.run(
                ["git", "diff", "--no-ext-diff", "--", str(relative)],
                cwd=checkout,
            ).stdout
        changes.append(PlannedChange(relative, action, mode, content, diff))
    return tuple(changes)


def _git_paths(runner: CommandRunner, checkout: Path) -> set[PurePosixPath]:
    commands = (
        ["git", "diff", "--name-only", "-z"],
        ["git", "diff", "--cached", "--name-only", "-z"],
        ["git", "ls-files", "--others", "--exclude-standard", "-z"],
    )
    paths: set[PurePosixPath] = set()
    for args in commands:
        output = runner.run(args, cwd=checkout).stdout
        for raw in output.split("\0"):
            if raw:
                paths.add(_safe_relative_path(raw))
    return paths


def _tracked_paths(runner: CommandRunner, checkout: Path) -> set[PurePosixPath]:
    output = runner.run(["git", "ls-files", "-z"], cwd=checkout).stdout
    return {_safe_relative_path(path) for path in output.split("\0") if path}


def _safe_relative_path(raw: str) -> PurePosixPath:
    path = PurePosixPath(raw)
    if (
        not raw
        or path == PurePosixPath(".")
        or path.as_posix() != raw
        or "\\" in raw
        or path.is_absolute()
        or any(part in {"", ".", "..", ".git"} for part in path.parts)
    ):
        raise FleetError(f"{raw!r}: unsafe APM deployment path")
    return path


def _safe_target(checkout: Path, relative: PurePosixPath) -> Path:
    root = checkout.resolve()
    target = root.joinpath(*relative.parts)
    for candidate in (target, *target.parents):
        if candidate == root:
            break
        if candidate.is_symlink():
            raise FleetError(f"{relative}: managed deployment path is a symlink")
    if not target.resolve().is_relative_to(root):
        raise FleetError(f"{relative}: managed deployment path escapes checkout")
    return target


def _load_yaml(path: Path) -> object:
    try:
        return yaml.load(path.read_text(encoding="utf-8"), Loader=StrictSafeLoader)
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as err:
        raise FleetError(f"{path}: invalid YAML: {err}") from err


def _restore_file(path: Path, original: bytes | None) -> None:
    if original is None:
        path.unlink(missing_ok=True)
    elif not path.exists() or path.read_bytes() != original:
        path.write_bytes(original)

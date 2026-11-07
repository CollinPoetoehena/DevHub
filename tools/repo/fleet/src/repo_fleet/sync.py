import hashlib
import json
import logging
import os
import shutil
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

from repo_fleet import git_ops, terraform_policy
from repo_fleet.errors import FleetError
from repo_fleet.inventory import Inventory
from repo_fleet.paths import FleetPaths
from repo_fleet.planner import PlannedChange
from repo_fleet.runner import CommandRunner

LOGGER = logging.getLogger(__name__)
STAGES = frozenset({"settings-plan", "prepare", "settings-apply", "deliver", "cleanup"})
STATE_FILE = "preflight.json"
PREPARED_FILE = "prepared.json"
APPLIED_FILE = "settings-applied.json"
FLEET_BRANCH = "devhub/repo-sync"
FLEET_COMMIT_MESSAGE = "chore(repo): sync DevHub fleet"
FLEET_PR_TITLE = FLEET_COMMIT_MESSAGE
FLEET_PR_BODY_INTRO = (
    "Automated sync of repository settings, templates, and APM packages "
    "from DevHub.\n\nChanged files:\n"
)


def run_stage(
    stage: str,
    inventory: Inventory,
    paths: FleetPaths,
    runner: CommandRunner,
    workdir: Path,
) -> int:
    if stage not in STAGES:
        raise FleetError(f"unknown central sync stage: {stage}")
    if stage == "cleanup":
        cleanup(workdir)
        print("fleet sync stage=cleanup outcome=complete")
        return 0
    root = _validate_workdir(workdir, paths.inventory)
    if stage == "settings-plan":
        settings_plan(inventory, paths, runner, workdir, root)
    elif stage == "prepare":
        prepare(inventory, paths, runner, workdir, root)
    elif stage == "settings-apply":
        apply_settings(inventory, paths, runner, workdir, root)
    else:
        deliver(inventory, paths, runner, workdir, root)
    return 0


def settings_plan(
    inventory: Inventory,
    paths: FleetPaths,
    runner: CommandRunner,
    workdir: Path,
    root: Path,
) -> None:
    if any(workdir.iterdir()):
        raise FleetError("central sync work directory is not empty")
    from repo_fleet.cli import run_check

    run_check(inventory, paths)
    source_sha = _source_sha(root, runner)
    inventory_digest = _digest(paths.inventory.read_bytes())
    settings_dir = workdir / "terraform"
    settings_dir.mkdir(mode=0o700)
    settings_metadata = terraform_policy.prepare_plan(
        inventory, paths.inventory.parent, settings_dir, runner
    )
    _write_json(
        workdir / STATE_FILE,
        {
            "schema": 1,
            "source_sha": source_sha,
            "inventory_digest": inventory_digest,
            "settings": settings_metadata,
        },
    )
    _publish_digest("preflight_digest", workdir / STATE_FILE)
    print("fleet sync stage=settings-plan outcome=complete")


def prepare(
    inventory: Inventory,
    paths: FleetPaths,
    runner: CommandRunner,
    workdir: Path,
    root: Path,
) -> None:
    state = _load_json(workdir / STATE_FILE)
    _verify_published_digest("FLEET_PREFLIGHT_DIGEST", workdir / STATE_FILE)
    _validate_source(state, paths, root, runner)
    if (workdir / PREPARED_FILE).exists():
        raise FleetError("central sync preparation already exists")
    if not os.environ.get("GH_TOKEN") and not os.environ.get("GITHUB_TOKEN"):
        raise FleetError("repository contents credential is required for preparation")
    from repo_fleet.cli import checkout_plans

    git_ops.ensure_gh_auth(runner)
    checkout_root = workdir / "checkouts"
    checkout_root.mkdir(mode=0o700)
    plans = checkout_plans(
        inventory,
        paths,
        inventory.active(),
        runner,
        checkout_root,
        False,
        True,
    )
    entries = tuple(
        _prepared_repository(item.repository.name, item.checkout, item.plan, runner)
        for item in plans
    )
    prepared = {
        "schema": 1,
        "source_sha": state["source_sha"],
        "inventory_digest": state["inventory_digest"],
        "repositories": entries,
    }
    _write_json(workdir / PREPARED_FILE, prepared)
    _publish_digest("prepared_digest", workdir / PREPARED_FILE)
    changed = sum(bool(item["changes"]) for item in entries)
    print(
        "fleet sync stage=prepare outcome=complete "
        f"active={len(entries)} changed={changed}"
    )


def apply_settings(
    inventory: Inventory,
    paths: FleetPaths,
    runner: CommandRunner,
    workdir: Path,
    root: Path,
) -> None:
    state = _load_json(workdir / STATE_FILE)
    prepared = _load_json(workdir / PREPARED_FILE)
    _verify_published_digest("FLEET_PREFLIGHT_DIGEST", workdir / STATE_FILE)
    _verify_published_digest("FLEET_PREPARED_DIGEST", workdir / PREPARED_FILE)
    _validate_source(state, paths, root, runner)
    _validate_prepared(prepared, state, inventory, runner, workdir, check_remote=True)
    settings = state.get("settings")
    if not isinstance(settings, dict):
        raise FleetError("Terraform preflight metadata is missing")
    terraform_policy.apply_plan(
        inventory,
        paths.inventory.parent,
        workdir / "terraform",
        runner,
        settings,
    )
    _write_json(
        workdir / APPLIED_FILE,
        {
            "source_sha": state["source_sha"],
            "inventory_digest": state["inventory_digest"],
            "prepared_digest": _file_digest(workdir / PREPARED_FILE),
            "plan_digest": settings.get("plan_digest"),
        },
    )
    _publish_digest("applied_digest", workdir / APPLIED_FILE)
    print("fleet sync stage=settings-apply outcome=complete")


def deliver(
    inventory: Inventory,
    paths: FleetPaths,
    runner: CommandRunner,
    workdir: Path,
    root: Path,
) -> None:
    state = _load_json(workdir / STATE_FILE)
    prepared = _load_json(workdir / PREPARED_FILE)
    applied = _load_json(workdir / APPLIED_FILE)
    _verify_published_digest("FLEET_PREFLIGHT_DIGEST", workdir / STATE_FILE)
    _verify_published_digest("FLEET_PREPARED_DIGEST", workdir / PREPARED_FILE)
    _verify_published_digest("FLEET_APPLIED_DIGEST", workdir / APPLIED_FILE)
    _validate_source(state, paths, root, runner)
    _validate_prepared(prepared, state, inventory, runner, workdir, check_remote=True)
    if (
        applied.get("source_sha") != state.get("source_sha")
        or applied.get("inventory_digest") != state.get("inventory_digest")
        or applied.get("prepared_digest") != _file_digest(workdir / PREPARED_FILE)
        or applied.get("plan_digest") != state.get("settings", {}).get("plan_digest")
    ):
        raise FleetError("settings apply marker does not match prepared sync data")

    repositories = prepared.get("repositories")
    if not isinstance(repositories, list):
        raise FleetError("prepared repository list is invalid")
    failures = 0
    changed = 0
    for entry in repositories:
        if not isinstance(entry, dict):
            raise FleetError("prepared repository entry is invalid")
        changes = _restore_changes(entry, workdir)
        if not changes:
            continue
        changed += 1
        repository = inventory.find(str(entry.get("name", "")))
        if repository is None:
            raise FleetError("prepared repository is not in the inventory")
        checkout = workdir / "checkouts" / repository.name
        try:
            result = git_ops.sync_checkout(
                runner,
                inventory.slug(repository),
                str(entry["default_branch"]),
                checkout,
                changes,
                branch=FLEET_BRANCH,
                commit_message=FLEET_COMMIT_MESSAGE,
                pr_title=FLEET_PR_TITLE,
                pr_body_intro=FLEET_PR_BODY_INTRO,
            )
            pushed = "pushed" if result.pushed else "unchanged"
            print(f"fleet sync repository={repository.name} outcome={pushed}")
        except FleetError as err:
            failures += 1
            LOGGER.error("%s: delivery failed: %s", repository.name, err)
    print(
        "fleet sync stage=deliver "
        f"outcome={'failed' if failures else 'complete'} "
        f"changed={changed} failed={failures}"
    )
    if failures:
        raise FleetError(f"delivery failed for {failures} repository(s)")


def cleanup(workdir: Path) -> None:
    runner_temp = os.environ.get("RUNNER_TEMP")
    if not runner_temp:
        raise FleetError("RUNNER_TEMP is required for safe cleanup")
    target = workdir.absolute()
    parent = Path(runner_temp).resolve()
    if (
        target.is_symlink()
        or target.parent.resolve() != parent
        or not target.name.startswith("repo-fleet-sync-")
    ):
        raise FleetError(
            "refusing to clean outside the central sync temporary directory"
        )
    if target.exists():
        shutil.rmtree(target)


def _validate_workdir(workdir: Path, inventory_path: Path) -> Path:
    root = inventory_path.resolve().parents[3]
    target = workdir.absolute()
    runner_temp = os.environ.get("RUNNER_TEMP")
    if not runner_temp:
        raise FleetError("RUNNER_TEMP is required for central sync")
    parent = Path(runner_temp).resolve()
    if (
        target.is_symlink()
        or target.parent.resolve() != parent
        or not target.name.startswith("repo-fleet-sync-")
        or target.resolve().is_relative_to(root)
    ):
        raise FleetError("central sync work directory must be under RUNNER_TEMP")
    target.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(target, 0o700)
    return root


def _source_sha(root: Path, runner: CommandRunner) -> str:
    revision = runner.run(["git", "rev-parse", "HEAD"], cwd=root).stdout.strip()
    if not revision:
        raise FleetError("cannot identify the checked-out DevHub revision")
    expected = os.environ.get("GITHUB_SHA")
    if expected and revision != expected:
        raise FleetError("checked-out DevHub revision differs from the triggering SHA")
    if os.environ.get("GITHUB_ACTIONS") == "true":
        status = runner.run(
            ["git", "status", "--porcelain", "--untracked-files=all"], cwd=root
        ).stdout
        if status.strip():
            raise FleetError("DevHub checkout is not clean")
    return revision


def _validate_source(
    state: Mapping[str, Any],
    paths: FleetPaths,
    root: Path,
    runner: CommandRunner,
) -> None:
    if state.get("source_sha") != _source_sha(root, runner) or state.get(
        "inventory_digest"
    ) != _digest(paths.inventory.read_bytes()):
        raise FleetError("source revision or inventory changed after preflight")


def _prepared_repository(
    name: str, checkout: Path, plan: Any, runner: CommandRunner
) -> dict[str, Any]:
    base_sha = runner.run(["git", "rev-parse", "HEAD"], cwd=checkout).stdout.strip()
    branch = plan.default_branch
    _validate_remote_base(runner, checkout, branch, base_sha)
    changes = tuple(
        _serialize_change(change, checkout) for change in plan.changes if change.writes
    )
    status = runner.run(
        ["git", "status", "--porcelain", "--untracked-files=all"], cwd=checkout
    ).stdout
    return {
        "name": name,
        "default_branch": branch,
        "base_sha": base_sha,
        "status_digest": _digest(status.encode()),
        "changes": changes,
    }


def _validate_prepared(
    prepared: Mapping[str, Any],
    state: Mapping[str, Any],
    inventory: Inventory,
    runner: CommandRunner,
    workdir: Path,
    *,
    check_remote: bool,
) -> None:
    if prepared.get("source_sha") != state.get("source_sha") or prepared.get(
        "inventory_digest"
    ) != state.get("inventory_digest"):
        raise FleetError("prepared content does not match Terraform preflight")
    entries = prepared.get("repositories")
    if not isinstance(entries, list):
        raise FleetError("prepared repository list is invalid")
    active = tuple(item.name for item in inventory.active())
    names = tuple(
        entry.get("name") if isinstance(entry, dict) else None for entry in entries
    )
    if names != active:
        raise FleetError("prepared repository set differs from the active inventory")
    for entry in entries:
        if not isinstance(entry, dict):
            raise FleetError("prepared repository entry is invalid")
        repository = inventory.find(str(entry.get("name", "")))
        if repository is None or repository.archived:
            raise FleetError("prepared repository is not active")
        checkout = workdir / "checkouts" / repository.name
        if not checkout.is_dir() or checkout.is_symlink():
            raise FleetError(f"{repository.name}: prepared checkout is missing")
        current_status = runner.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=checkout,
        ).stdout
        if _digest(current_status.encode()) != entry.get("status_digest"):
            raise FleetError(f"{repository.name}: prepared checkout changed")
        _restore_changes(entry, workdir)
        if check_remote:
            if git_ops.default_branch(runner, inventory.slug(repository)) != entry.get(
                "default_branch"
            ):
                raise FleetError(
                    f"{repository.name}: default branch changed after preparation"
                )
            _validate_remote_base(
                runner,
                checkout,
                str(entry.get("default_branch", "")),
                str(entry.get("base_sha", "")),
            )


def _validate_remote_base(
    runner: CommandRunner, checkout: Path, branch: str, expected_sha: str
) -> None:
    if not branch or not expected_sha:
        raise FleetError("prepared default branch identity is missing")
    runner.run(["git", "check-ref-format", "--branch", branch], cwd=checkout)
    remote = runner.run(
        ["git", "ls-remote", "origin", f"refs/heads/{branch}"],
        cwd=checkout,
        env=git_ops.GIT_AUTH_ENV,
    ).stdout
    matches = tuple(
        line.split("\t", 1)[0]
        for line in remote.splitlines()
        if len(line.split("\t", 1)) == 2
        and line.split("\t", 1)[1] == f"refs/heads/{branch}"
    )
    if matches != (expected_sha,):
        raise FleetError("repository default branch changed after preparation")


def _serialize_change(change: PlannedChange, checkout: Path) -> dict[str, str]:
    digest = ""
    if change.action != "delete":
        target = checkout.joinpath(*change.path.parts)
        if target.is_symlink() or not target.is_file():
            raise FleetError(f"{change.path}: prepared output is not a regular file")
        digest = _file_digest(target)
    return {
        "path": str(change.path),
        "action": change.action,
        "mode": change.mode,
        "digest": digest,
    }


def _restore_changes(
    entry: Mapping[str, Any], workdir: Path
) -> tuple[PlannedChange, ...]:
    name = entry.get("name")
    raw_changes = entry.get("changes")
    if not isinstance(name, str) or not isinstance(raw_changes, list):
        raise FleetError("prepared changes are invalid")
    checkout = workdir / "checkouts" / name
    changes: list[PlannedChange] = []
    for raw in raw_changes:
        if not isinstance(raw, dict):
            raise FleetError("prepared change entry is invalid")
        relative = PurePosixPath(str(raw.get("path", "")))
        if (
            relative.is_absolute()
            or not relative.parts
            or any(part in {"", ".", ".."} for part in relative.parts)
        ):
            raise FleetError("prepared change path is invalid")
        action = raw.get("action")
        mode = raw.get("mode")
        if action not in {"create", "update", "delete"} or mode not in {"sync", "seed"}:
            raise FleetError("prepared change type is invalid")
        target = checkout.joinpath(*relative.parts)
        if action == "delete":
            if target.exists() or target.is_symlink():
                raise FleetError(f"{relative}: prepared deletion target changed")
            content = b""
        else:
            if target.is_symlink() or not target.is_file():
                raise FleetError(f"{relative}: prepared output is missing")
            content = target.read_bytes()
            if _digest(content) != raw.get("digest"):
                raise FleetError(f"{relative}: prepared output digest changed")
        changes.append(
            PlannedChange(
                path=relative,
                action=action,
                mode=mode,
                content=content,
            )
        )
    return tuple(changes)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        raise FleetError(
            f"central sync metadata is missing or invalid: {path.name}"
        ) from err
    if not isinstance(data, dict):
        raise FleetError(f"central sync metadata is invalid: {path.name}")
    return data


def _write_json(path: Path, data: Mapping[str, Any]) -> None:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    path.write_bytes(encoded)
    os.chmod(path, 0o600)


def _publish_digest(output_name: str, path: Path) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if os.environ.get("GITHUB_ACTIONS") == "true" and not output_path:
        raise FleetError("GitHub Actions output channel is unavailable")
    if output_path:
        with Path(output_path).open("a", encoding="utf-8") as output:
            output.write(f"{output_name}={_file_digest(path)}\n")


def _verify_published_digest(environment_name: str, path: Path) -> None:
    expected = os.environ.get(environment_name, "")
    if os.environ.get("GITHUB_ACTIONS") == "true" and not expected:
        raise FleetError(f"trusted {environment_name} handoff is missing")
    if expected and expected != _file_digest(path):
        raise FleetError(f"central sync {path.name} changed between stages")


def _file_digest(path: Path) -> str:
    try:
        return _digest(path.read_bytes())
    except OSError as err:
        raise FleetError(f"prepared file is missing: {path.name}") from err


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

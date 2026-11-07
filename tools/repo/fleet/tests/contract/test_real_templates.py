"""Contract between the fleet renderer, real inventory, and central workflow."""

import os
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath

import pytest
import yaml

from repo_fleet import apm, cli
from repo_fleet.inventory import load_inventory
from repo_fleet.paths import (
    INVENTORY_ENV_VAR,
    TEMPLATES_ENV_VAR,
    find_tool_root,
    resolve_paths,
)
from repo_fleet.templates import TemplateVariables, render_repository

pytestmark = pytest.mark.integration

FLEET_DIR = Path(__file__).resolve().parents[2]
TOOL_ROOT = FLEET_DIR.parent
DEVHUB_ROOT = TOOL_ROOT.parents[1]
WORKFLOW = DEVHUB_ROOT / ".github" / "workflows" / "apm-sync.yml"
LEGACY_CALLER = PurePosixPath(".github/workflows/devhub-apm-sync.yml")


@pytest.fixture(autouse=True)
def _no_path_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(INVENTORY_ENV_VAR, raising=False)
    monkeypatch.delenv(TEMPLATES_ENV_VAR, raising=False)


def test_package_discovers_real_tool_root() -> None:
    assert find_tool_root([FLEET_DIR / "src"]) == TOOL_ROOT


def test_check_passes_for_real_inventory_and_templates(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(["check"]) == cli.EXIT_OK
    assert "ok DevHub:" in capsys.readouterr().out


def test_common_template_does_not_deploy_apm_workflow_caller() -> None:
    paths = resolve_paths(None, None)
    inventory = load_inventory(paths.inventory)
    devhub = inventory.find("DevHub")
    assert devhub is not None
    variables = TemplateVariables.for_repository(inventory, devhub, "main")

    rendered = render_repository(paths.templates, devhub.profiles, variables)

    assert LEGACY_CALLER not in {item.path for item in rendered}
    assert not (DEVHUB_ROOT / LEGACY_CALLER).exists()


def test_devhub_apm_manifest_has_valid_local_and_managed_dependencies() -> None:
    paths = resolve_paths(None, None)
    inventory = load_inventory(paths.inventory)
    devhub = inventory.find("DevHub")
    assert devhub is not None

    manifest = apm._load_manifest(DEVHUB_ROOT / "apm.yml", devhub.apm_stacks)

    assert manifest.has_local_dependencies
    assert tuple(stack for stack, _ in manifest.managed_refs) == (
        "common",
        "containerization",
        "go",
        "iac",
        "java",
        "python",
        "rust",
    )


def test_pinned_apm_cli_accepts_canonical_devhub_selectors(
    tmp_path: Path,
) -> None:
    apm_cli = shutil.which("apm")
    if apm_cli is None:
        pytest.skip("APM CLI 0.35.0 is not installed")

    version = subprocess.run(
        [apm_cli, "--version"],
        cwd=tmp_path,
        capture_output=True,
        check=False,
        text=True,
        timeout=30,
    )
    assert version.returncode == 0, version.stderr
    version_pattern = rf"(?<![\d.]){re.escape(apm.APM_VERSION)}(?![\d.])"
    assert re.search(version_pattern, version.stdout) is not None

    root_manifest = yaml.safe_load((DEVHUB_ROOT / "apm.yml").read_text("utf-8"))
    assert isinstance(root_manifest, dict)
    root_dependencies = root_manifest.get("dependencies")
    assert isinstance(root_dependencies, dict)
    apm_dependencies = root_dependencies.get("apm")
    assert isinstance(apm_dependencies, list)
    selected_dependencies = tuple(
        dependency
        for dependency in apm_dependencies
        if isinstance(dependency, str)
        and apm._managed_dependency(dependency) in {"common", "python"}
    )
    selected_manifest = {
        "name": "apm-selector-contract",
        "version": "1.0.0",
        "target": "copilot",
        "dependencies": {"apm": selected_dependencies},
    }
    manifest_path = tmp_path / "apm.yml"
    original_manifest = yaml.safe_dump(selected_manifest, sort_keys=False)
    manifest_path.write_text(original_manifest, encoding="utf-8")
    parsed_manifest = apm._load_manifest(manifest_path, ("python",))
    selectors = tuple(selector for _, selector in parsed_manifest.managed_refs)
    assert selectors == (
        "collinpoetoehena/devhub/packages/apm/common",
        "collinpoetoehena/devhub/packages/apm/python",
    )

    environment = os.environ.copy()
    environment.pop("GH_TOKEN", None)
    environment.pop("GITHUB_TOKEN", None)
    result = subprocess.run(
        [
            apm_cli,
            "update",
            "--dry-run",
            "--target",
            "copilot",
            *selectors,
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        check=False,
        text=True,
        timeout=apm.APM_TIMEOUT_SECONDS,
    )

    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    assert "Update plan for apm.yml" in result.stdout
    assert "[+] collinpoetoehena/devhub/packages/apm/common" in result.stdout
    assert "[+] collinpoetoehena/devhub/packages/apm/python" in result.stdout
    assert manifest_path.read_text(encoding="utf-8") == original_manifest
    assert not (tmp_path / "apm.lock.yaml").exists()


def test_fleet_workflow_is_the_only_central_writer_and_scoped_to_main_paths() -> None:
    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    config = yaml.load(workflow_text, Loader=yaml.BaseLoader)

    assert isinstance(config, dict)
    triggers = config["on"]
    assert "workflow_dispatch" in triggers
    assert "workflow_call" not in triggers
    assert "schedule" not in triggers
    assert triggers["push"]["branches"] == ["main"]
    assert "packages/apm/**" in triggers["push"]["paths"]
    assert "tools/repo/**" in triggers["push"]["paths"]
    assert "apm.yml" in triggers["push"]["paths"]
    assert config["permissions"] == {"contents": "read"}
    sync_job = config["jobs"]["sync"]
    assert sync_job["if"] == "github.ref == 'refs/heads/main'"
    assert sync_job["environment"] == {"name": "apm-sync"}
    checkout = next(
        step
        for step in sync_job["steps"]
        if step.get("uses", "").startswith("actions/checkout@")
    )
    assert checkout["with"]["ref"] == "${{ github.sha }}"
    assert "cancel-in-progress: false" in workflow_text
    assert "${{ secrets.REPO_FLEET_SYNC_TOKEN }}" in workflow_text
    assert "${{ secrets.REPO_FLEET_SETTINGS_TOKEN }}" in workflow_text
    assert "${{ secrets.HCP_TERRAFORM_TOKEN }}" in workflow_text
    assert "gh auth setup-git" not in workflow_text
    for stage in (
        "settings-plan",
        "prepare",
        "settings-apply",
        "deliver",
        "cleanup",
    ):
        assert f"repo-fleet sync {stage}" in workflow_text
    steps = sync_job["steps"]
    prepare_step = next(
        step
        for step in steps
        if step.get("name") == "Prepare combined repository changes"
    )
    assert prepare_step["env"] == {
        "GH_TOKEN": "${{ secrets.REPO_FLEET_SYNC_TOKEN }}",
        "FLEET_PREFLIGHT_DIGEST": "${{ steps.settings_plan.outputs.preflight_digest }}",
    }
    settings_step = next(
        step
        for step in steps
        if step.get("name") == "Apply the exact saved settings plan"
    )
    assert settings_step["env"]["GITHUB_TOKEN"] == (
        "${{ secrets.REPO_FLEET_SETTINGS_TOKEN }}"
    )
    assert settings_step["env"]["TF_TOKEN_app_terraform_io"] == (
        "${{ secrets.HCP_TERRAFORM_TOKEN }}"
    )
    assert settings_step["env"]["FLEET_PREPARED_DIGEST"] == (
        "${{ steps.prepare.outputs.prepared_digest }}"
    )
    tools_workflow = (DEVHUB_ROOT / ".github/workflows/repo-tools.yml").read_text(
        encoding="utf-8"
    )
    assert "secrets." not in tools_workflow
    assert "repo-fleet sync " not in tools_workflow
    workflow_docs = (
        DEVHUB_ROOT / "docs/github-actions/workflows/apm-sync.md"
    ).read_text(encoding="utf-8")
    assert "## Table of Contents" in workflow_docs
    assert "## Why central push, not consumer pull" in workflow_docs
    assert "deployment branch" in workflow_docs
    assert "`main`" in workflow_docs

"""Contract between the fleet renderer, the real inventory, and DevHub's own files."""

from pathlib import Path

import pytest

from repo_fleet import cli
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
WORKFLOW = Path(".github") / "workflows" / "devhub-apm-sync.yml"


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


def test_devhub_workflow_matches_rendered_common_template() -> None:
    paths = resolve_paths(None, None)
    inventory = load_inventory(paths.inventory)
    devhub = inventory.find("DevHub")
    assert devhub is not None
    variables = TemplateVariables.for_repository(inventory, devhub, "main")

    rendered = render_repository(paths.templates, devhub.profiles, variables)

    workflow = next(item for item in rendered if str(item.path) == WORKFLOW.as_posix())
    assert workflow.mode == "sync"
    assert workflow.content == (DEVHUB_ROOT / WORKFLOW).read_bytes()

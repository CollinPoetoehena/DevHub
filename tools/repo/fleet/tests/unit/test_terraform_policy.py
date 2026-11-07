import copy
import io
import json
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

import pytest

from repo_fleet import terraform_policy
from repo_fleet.errors import FleetError
from repo_fleet.inventory import Inventory, parse_inventory
from repo_fleet.runner import CommandResult
from tests.fakes import FakeRunner, inventory_data, repository_entry

pytestmark = pytest.mark.unit


def _inventory(archived: bool = False) -> Inventory:
    return parse_inventory(
        inventory_data({"alpha": repository_entry(archived=archived)}), "test"
    )


def _repository_values(
    *,
    visibility: str = "public",
    allow_merge: bool = False,
    allow_squash: bool = True,
) -> dict[str, Any]:
    return {
        "name": "alpha",
        "visibility": visibility,
        "archived": False,
        "allow_merge_commit": allow_merge,
        "allow_squash_merge": allow_squash,
        "allow_rebase_merge": False,
        "delete_branch_on_merge": True,
    }


def _ruleset(name: str, rules: list[dict[str, Any]]) -> dict[str, Any]:
    bypass = (
        []
        if name == "default-branch-safety"
        else [
            {
                "actor_id": 5,
                "actor_type": "RepositoryRole",
                "bypass_mode": "pull_request",
            }
        ]
    )
    return {
        "name": name,
        "repository": "alpha",
        "target": "branch",
        "enforcement": "active",
        "conditions": [{"ref_name": [{"include": ["~DEFAULT_BRANCH"], "exclude": []}]}],
        "bypass_actors": bypass,
        "rules": rules,
    }


def _plan(*, update_merge: bool = False) -> dict[str, Any]:
    addresses = terraform_policy.expected_addresses(_inventory())
    old_repository = _repository_values()
    new_repository = _repository_values(allow_merge=update_merge)
    old_safety = _ruleset(
        "default-branch-safety", [{"deletion": True, "non_fast_forward": True}]
    )
    old_pr = _ruleset(
        "default-branch-pull-request",
        [
            {
                "pull_request": [
                    {
                        "required_approving_review_count": 1,
                        "allowed_merge_methods": ["squash"],
                    }
                ]
            }
        ],
    )
    new_pr = _ruleset(
        "default-branch-pull-request",
        [
            {
                "pull_request": [
                    {
                        "required_approving_review_count": 1,
                        "allowed_merge_methods": (
                            ["merge", "squash"] if update_merge else ["squash"]
                        ),
                    }
                ]
            }
        ],
    )
    permissions_before = {
        "repository": "alpha",
        "default_workflow_permissions": "read",
        "can_approve_pull_request_reviews": True,
    }
    permissions_after = dict(permissions_before)
    values = {
        'github_repository.active["alpha"]': (
            "github_repository",
            old_repository,
            new_repository,
        ),
        'github_workflow_repository_permissions.active["alpha"]': (
            "github_workflow_repository_permissions",
            permissions_before,
            permissions_after,
        ),
        'github_repository_ruleset.default_branch_safety["alpha"]': (
            "github_repository_ruleset",
            old_safety,
            copy.deepcopy(old_safety),
        ),
        'github_repository_ruleset.default_branch_pull_request["alpha"]': (
            "github_repository_ruleset",
            old_pr,
            new_pr,
        ),
    }
    return {
        "resource_changes": [
            {
                "address": address,
                "mode": "managed",
                "type": values[address][0],
                "change": {
                    "actions": (
                        ["update"]
                        if values[address][1] != values[address][2]
                        else ["no-op"]
                    ),
                    "before": values[address][1],
                    "after": values[address][2],
                    "after_unknown": {},
                },
            }
            for address in addresses
        ]
    }


def _state(inventory: Inventory) -> dict[str, Any]:
    resources = []
    for address, (resource_type, name) in terraform_policy.expected_addresses(
        inventory
    ).items():
        repository = inventory.find(name)
        assert repository is not None
        archived = repository.archived
        values = (
            {"name": name, "visibility": "public", "archived": archived}
            if resource_type == "github_repository"
            else {"repository": name}
        )
        resources.append({"address": address, "type": resource_type, "values": values})
    return {"values": {"root_module": {"resources": resources}}}


class TerraformRunner:
    def __init__(self, inventory: Inventory, plan: dict[str, Any]) -> None:
        self.inventory = inventory
        self.plan = plan
        self.commands: list[tuple[str, ...]] = []
        self.applies = 0
        self.state_serial = 1

    def run(
        self,
        args: Sequence[str],
        *,
        cwd: Path | None = None,
        env: Mapping[str, str | None] | None = None,
        timeout: float | None = None,
    ) -> CommandResult:
        command = tuple(args)
        self.commands.append(command)
        output = ""
        if command[:3] == ("terraform", "state", "list"):
            output = "\n".join(terraform_policy.expected_addresses(self.inventory))
        elif command[:3] == ("terraform", "state", "pull"):
            output = json.dumps(
                {"lineage": "test-lineage", "serial": self.state_serial}
            )
        elif command[:3] == ("terraform", "show", "-json"):
            output = json.dumps(
                self.plan if len(command) == 4 else _state(self.inventory)
            )
        elif command[:2] == ("terraform", "workspace"):
            output = "fleet\n"
        elif command[:2] == ("terraform", "plan"):
            plan_path = Path(command[command.index("-out") + 1])
            plan_path.write_bytes(b"saved-plan")
        elif command[:2] == ("terraform", "apply"):
            self.applies += 1
        return CommandResult(command, 0, output, "")


def test_state_requires_exact_adopted_resources_and_identities() -> None:
    inventory = _inventory()
    addresses = tuple(terraform_policy.expected_addresses(inventory))

    assert terraform_policy.validate_state(inventory, addresses, _state(inventory))

    with pytest.raises(FleetError, match="adoption is incomplete"):
        terraform_policy.validate_state(inventory, addresses[:-1], _state(inventory))

    wrong_state = _state(inventory)
    wrong_state["values"]["root_module"]["resources"][0]["values"]["name"] = "other"
    with pytest.raises(FleetError, match="identity differs"):
        terraform_policy.validate_state(inventory, addresses, wrong_state)


def test_archived_inventory_has_only_read_only_repository_state() -> None:
    inventory = _inventory(archived=True)
    addresses = tuple(terraform_policy.expected_addresses(inventory))

    assert addresses == ('github_repository.archived["alpha"]',)
    terraform_policy.validate_state(inventory, addresses, _state(inventory))


def test_workspace_requires_exact_identity_and_local_execution() -> None:
    response: dict[str, Any] = {
        "data": {
            "id": "ws-example",
            "attributes": {"name": "fleet", "execution-mode": "local"},
            "relationships": {"organization": {"data": {"id": "example"}}},
        }
    }

    assert (
        terraform_policy.validate_workspace_response(response, "example", "fleet")
        == "ws-example"
    )

    response["data"]["attributes"]["execution-mode"] = "remote"
    with pytest.raises(FleetError, match="identity or local execution"):
        terraform_policy.validate_workspace_response(response, "example", "fleet")


def test_cloud_init_uses_verified_workspace_environment(tmp_path: Path) -> None:
    runner = FakeRunner(outputs={("terraform", "workspace", "show"): "fleet\n"})
    environment = terraform_policy._terraform_environment(
        "test-token", "example", "fleet"
    )

    terraform_policy._run_init(tmp_path, runner, "fleet", environment)

    assert runner.commands() == [
        ("terraform", "init", "-input=false"),
        ("terraform", "workspace", "show"),
    ]
    assert all(
        env is not None
        and env["TF_CLOUD_ORGANIZATION"] == "example"
        and env["TF_WORKSPACE"] == "fleet"
        for env in runner.environments
    )


def test_cloud_init_rejects_a_different_selected_workspace(tmp_path: Path) -> None:
    runner = FakeRunner(outputs={("terraform", "workspace", "show"): "other\n"})
    environment = terraform_policy._terraform_environment(
        "test-token", "example", "fleet"
    )

    with pytest.raises(FleetError, match="different workspace"):
        terraform_policy._run_init(tmp_path, runner, "fleet", environment)


def test_workspace_verification_authenticates_to_the_fixed_hcp_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = {
        "data": {
            "id": "ws-example",
            "attributes": {"name": "fleet", "execution-mode": "local"},
            "relationships": {"organization": {"data": {"id": "example"}}},
        }
    }

    class Opener:
        request: Any = None
        authorization_header: str | None = None

        def open(self, request: Any, timeout: float) -> io.BytesIO:
            self.authorization_header = request.get_header("Authorization")
            self.request = request
            assert timeout == 20
            return io.BytesIO(json.dumps(response).encode())

    opener = Opener()
    monkeypatch.setattr(
        urllib.request,
        "build_opener",
        lambda *_handlers: opener,
    )

    assert terraform_policy.verify_workspace(
        {
            "TF_CLOUD_ORGANIZATION": "example",
            "TF_WORKSPACE": "fleet",
            "TF_TOKEN_app_terraform_io": "test-token",
            "GITHUB_TOKEN": "test-settings-token",
        }
    ) == ("example", "fleet", "ws-example")
    assert opener.request.full_url == (
        "https://app.terraform.io/api/v2/organizations/example/workspaces/fleet"
    )
    assert opener.authorization_header == "Be" + "arer " + "test-token"


def test_plan_allows_managed_merge_updates_without_weakening_protection() -> None:
    terraform_policy.validate_plan(_plan(update_merge=True), _inventory())


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda item: item["change"].update(actions=["create"]), "actions are blocked"),
        (
            lambda item: item["change"]["after"].update(visibility="private"),
            "visibility",
        ),
        (
            lambda item: item["change"]["after_unknown"].update(name=True),
            "value is unknown",
        ),
    ],
)
def test_plan_rejects_unsafe_actions_or_protected_repository_values(
    mutate: Callable[[dict[str, Any]], None], message: str
) -> None:
    plan = _plan()
    mutate(plan["resource_changes"][0])

    with pytest.raises(FleetError, match=message):
        terraform_policy.validate_plan(plan, _inventory())


def test_plan_rejects_weaker_rules_and_new_approval_capability() -> None:
    plan = _plan()
    safety = plan["resource_changes"][2]["change"]
    safety["after"]["rules"][0]["deletion"] = False
    with pytest.raises(FleetError, match="protection weakened"):
        terraform_policy.validate_plan(plan, _inventory())

    plan = _plan()
    permissions = plan["resource_changes"][1]["change"]
    permissions["actions"] = ["update"]
    permissions["before"]["can_approve_pull_request_reviews"] = False
    permissions["after"]["can_approve_pull_request_reviews"] = True
    with pytest.raises(FleetError, match="approval capability"):
        terraform_policy.validate_plan(plan, _inventory())


def test_plan_rejects_approval_decrease_and_bypass_expansion() -> None:
    plan = _plan()
    pull_request = plan["resource_changes"][3]["change"]
    pull_request["actions"] = ["update"]
    pull_request["after"]["rules"][0]["pull_request"][0][
        "required_approving_review_count"
    ] = 0
    with pytest.raises(FleetError, match="approvals may not decrease"):
        terraform_policy.validate_plan(plan, _inventory())

    plan = _plan()
    pull_request = plan["resource_changes"][3]["change"]
    pull_request["after"]["bypass_actors"].append(
        {"actor_id": 1, "actor_type": "RepositoryRole", "bypass_mode": "always"}
    )
    with pytest.raises(FleetError, match="bypass changed"):
        terraform_policy.validate_plan(plan, _inventory())


def test_plan_rejects_unknown_resources_and_workflow_write_permission() -> None:
    plan = _plan()
    plan["resource_changes"].append(
        {"address": 'github_repository.extra["other"]', "mode": "managed"}
    )
    with pytest.raises(FleetError, match="unknown or duplicate"):
        terraform_policy.validate_plan(plan, _inventory())

    plan = _plan()
    permissions = plan["resource_changes"][1]["change"]
    permissions["after"]["default_workflow_permissions"] = "write"
    with pytest.raises(FleetError, match="read-only"):
        terraform_policy.validate_plan(plan, _inventory())


def test_saved_plan_is_revalidated_and_applied_without_replanning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inventory = _inventory()
    runner = TerraformRunner(inventory, _plan())
    state_dir = tmp_path / "private"
    state_dir.mkdir()
    monkeypatch.setattr(
        terraform_policy,
        "verify_workspace",
        lambda: ("example", "fleet", "workspace-id"),
    )
    monkeypatch.setenv("TF_TOKEN_app_terraform_io", "test-token")
    monkeypatch.setenv("GITHUB_TOKEN", "test-settings-token")

    metadata = terraform_policy.prepare_plan(inventory, tmp_path, state_dir, runner)
    terraform_policy.apply_plan(inventory, tmp_path, state_dir, runner, metadata)

    assert runner.applies == 1
    apply_index = next(
        index for index, command in enumerate(runner.commands) if command[1] == "apply"
    )
    apply_command = runner.commands[apply_index]
    assert apply_command[-1] == str(state_dir / "settings.tfplan")
    assert not any(
        command[:2] == ("terraform", "plan")
        for command in runner.commands[apply_index + 1 :]
    )


def test_tampered_saved_plan_blocks_apply(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inventory = _inventory()
    runner = TerraformRunner(inventory, _plan())
    state_dir = tmp_path / "private"
    state_dir.mkdir()
    monkeypatch.setattr(
        terraform_policy,
        "verify_workspace",
        lambda: ("example", "fleet", "workspace-id"),
    )
    monkeypatch.setenv("TF_TOKEN_app_terraform_io", "test-token")
    monkeypatch.setenv("GITHUB_TOKEN", "test-settings-token")
    metadata = terraform_policy.prepare_plan(inventory, tmp_path, state_dir, runner)
    (state_dir / "settings.tfplan").write_bytes(b"tampered-plan")

    with pytest.raises(FleetError, match="saved plan changed"):
        terraform_policy.apply_plan(inventory, tmp_path, state_dir, runner, metadata)

    assert runner.applies == 0


def test_creation_plan_is_blocked_before_any_apply(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inventory = _inventory()
    plan = _plan()
    plan["resource_changes"][0]["change"]["actions"] = ["create"]
    runner = TerraformRunner(inventory, plan)
    state_dir = tmp_path / "private"
    state_dir.mkdir()
    monkeypatch.setattr(
        terraform_policy,
        "verify_workspace",
        lambda: ("example", "fleet", "workspace-id"),
    )
    monkeypatch.setenv("TF_TOKEN_app_terraform_io", "test-token")
    monkeypatch.setenv("GITHUB_TOKEN", "test-settings-token")

    with pytest.raises(FleetError, match="actions are blocked"):
        terraform_policy.prepare_plan(inventory, tmp_path, state_dir, runner)

    assert runner.applies == 0

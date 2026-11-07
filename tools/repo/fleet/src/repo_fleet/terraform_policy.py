import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping, Sequence
from http.client import HTTPMessage
from pathlib import Path
from typing import Any

from repo_fleet.errors import FleetError
from repo_fleet.inventory import Inventory
from repo_fleet.runner import CommandRunner

WORKSPACE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,89}$")
MANAGED_SETTINGS = frozenset(
    {
        "allow_merge_commit",
        "allow_squash_merge",
        "allow_rebase_merge",
        "delete_branch_on_merge",
    }
)
PROTECTED_PLAN_ATTRIBUTES = {
    "github_repository": (
        "name",
        "visibility",
        "archived",
        *MANAGED_SETTINGS,
    ),
    "github_repository_ruleset": (
        "name",
        "repository",
        "target",
        "enforcement",
        "conditions",
        "bypass_actors",
        "rules",
    ),
    "github_workflow_repository_permissions": (
        "repository",
        "default_workflow_permissions",
        "can_approve_pull_request_reviews",
    ),
}


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        request: urllib.request.Request,
        file: Any,
        code: int,
        message: str,
        headers: HTTPMessage,
        new_url: str,
    ) -> None:
        return None


def expected_addresses(inventory: Inventory) -> dict[str, tuple[str, str]]:
    expected: dict[str, tuple[str, str]] = {}
    for repository in inventory.repositories:
        key = json.dumps(repository.name)
        if repository.archived:
            expected[f"github_repository.archived[{key}]"] = (
                "github_repository",
                repository.name,
            )
            continue
        expected[f"github_repository.active[{key}]"] = (
            "github_repository",
            repository.name,
        )
        expected[f"github_workflow_repository_permissions.active[{key}]"] = (
            "github_workflow_repository_permissions",
            repository.name,
        )
        expected[f"github_repository_ruleset.default_branch_safety[{key}]"] = (
            "github_repository_ruleset",
            repository.name,
        )
        expected[f"github_repository_ruleset.default_branch_pull_request[{key}]"] = (
            "github_repository_ruleset",
            repository.name,
        )
    return expected


def validate_workspace_response(
    payload: object, organization: str, workspace: str
) -> str:
    if not isinstance(payload, dict):
        raise FleetError("HCP Terraform returned an invalid workspace response")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise FleetError("HCP Terraform returned an invalid workspace response")
    attributes = data.get("attributes")
    relationships = data.get("relationships")
    workspace_id = data.get("id")
    organization_data = (
        relationships.get("organization", {}).get("data")
        if isinstance(relationships, dict)
        and isinstance(relationships.get("organization"), dict)
        else None
    )
    if (
        not isinstance(workspace_id, str)
        or not workspace_id
        or not isinstance(attributes, dict)
        or attributes.get("name") != workspace
        or attributes.get("execution-mode") != "local"
        or not isinstance(organization_data, dict)
        or organization_data.get("id") != organization
    ):
        raise FleetError(
            "HCP Terraform workspace identity or local execution mode does not match"
        )
    return workspace_id


def verify_workspace(environ: Mapping[str, str] | None = None) -> tuple[str, str, str]:
    environment = os.environ if environ is None else environ
    organization = _required_value(environment, "TF_CLOUD_ORGANIZATION")
    workspace = _required_value(environment, "TF_WORKSPACE")
    token = _required_value(environment, "TF_TOKEN_app_terraform_io")
    _required_value(environment, "GITHUB_TOKEN")
    if not WORKSPACE_NAME_PATTERN.fullmatch(
        organization
    ) or not WORKSPACE_NAME_PATTERN.fullmatch(workspace):
        raise FleetError("HCP Terraform organization or workspace name is invalid")

    path = "/api/v2/organizations/{}/workspaces/{}".format(
        urllib.parse.quote(organization, safe=""),
        urllib.parse.quote(workspace, safe=""),
    )
    request = urllib.request.Request(
        f"https://app.terraform.io{path}",
        headers={
            "Content-Type": "application/vnd.api+json",
        },
    )
    try:
        auth_scheme = "Bearer"
        request.add_header("Authorization", f"{auth_scheme} {token}")
        opener = urllib.request.build_opener(_NoRedirectHandler())
        with opener.open(request, timeout=20) as response:
            payload = json.loads(response.read())
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as err:
        raise FleetError(
            "cannot verify the configured HCP Terraform workspace"
        ) from err
    return (
        organization,
        workspace,
        validate_workspace_response(payload, organization, workspace),
    )


def validate_state(
    inventory: Inventory, addresses: Sequence[str], state: object
) -> str:
    expected = expected_addresses(inventory)
    actual = set(addresses)
    if actual != set(expected):
        missing = sorted(set(expected) - actual)
        extra = sorted(actual - set(expected))
        raise FleetError(
            "Terraform state adoption is incomplete or unexpected "
            f"(missing={len(missing)}, extra={len(extra)})"
        )
    resources = _state_resources(state)
    if set(resources) != set(expected):
        raise FleetError("Terraform state resource values do not match its addresses")
    repositories = {item.name: item for item in inventory.repositories}
    for address, (resource_type, name) in expected.items():
        resource = resources[address]
        if resource.get("type") != resource_type:
            raise FleetError(f"{address}: unexpected Terraform resource type")
        values = resource.get("values")
        if not isinstance(values, dict):
            raise FleetError(f"{address}: Terraform state values are missing")
        repository_value = (
            values.get("repository")
            if resource_type != "github_repository"
            else values.get("name")
        )
        if repository_value != name:
            raise FleetError(f"{address}: Terraform state repository identity differs")
        repository = repositories[name]
        if resource_type == "github_repository" and (
            values.get("archived") is not repository.archived
            or values.get("visibility") != repository.visibility
        ):
            raise FleetError(f"{address}: archive or visibility state differs")
    return hashlib.sha256(
        json.dumps(state, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_plan(plan: object, inventory: Inventory) -> None:
    if not isinstance(plan, dict):
        raise FleetError("Terraform returned an invalid saved plan")
    if plan.get("deferred_changes") or plan.get("complete") is False:
        raise FleetError("Terraform plan is incomplete")
    changes = plan.get("resource_changes")
    drift = plan.get("resource_drift", [])
    if not isinstance(changes, list) or not isinstance(drift, list):
        raise FleetError("Terraform plan has no resource change list")

    expected = expected_addresses(inventory)
    by_address = {address: (kind, name) for address, (kind, name) in expected.items()}
    changes_by_address: dict[str, dict[str, Any]] = {}
    for resource_change in changes:
        if not isinstance(resource_change, dict):
            raise FleetError("Terraform plan contains an invalid resource change")
        address = resource_change.get("address")
        if (
            not isinstance(address, str)
            or address not in by_address
            or address in changes_by_address
            or resource_change.get("mode") != "managed"
            or resource_change.get("type") != by_address[address][0]
        ):
            raise FleetError("Terraform plan contains an unknown or duplicate resource")
        change = resource_change.get("change")
        if not isinstance(change, dict):
            raise FleetError(f"{address}: Terraform change details are missing")
        actions = change.get("actions")
        if actions not in (["no-op"], ["update"]):
            raise FleetError(
                f"{address}: create, delete, replace, import, and move "
                "actions are blocked"
            )
        if resource_change.get("previous_address") is not None or change.get(
            "importing"
        ):
            raise FleetError(f"{address}: resource moves and imports are blocked")
        changes_by_address[address] = resource_change

    drift_changes: list[tuple[str, dict[str, Any]]] = []
    for resource_drift in drift:
        if not isinstance(resource_drift, dict):
            raise FleetError("Terraform plan contains invalid drift data")
        address = resource_drift.get("address")
        if (
            not isinstance(address, str)
            or address not in by_address
            or resource_drift.get("mode") != "managed"
            or resource_drift.get("type") != by_address[address][0]
        ):
            raise FleetError("Terraform detected drift outside adopted resources")
        change = resource_drift.get("change")
        if not isinstance(change, dict) or change.get("actions") not in (
            ["no-op"],
            ["update"],
        ):
            raise FleetError(f"{address}: unsafe resource drift is blocked")
        if resource_drift.get("previous_address") is not None or change.get(
            "importing"
        ):
            raise FleetError(f"{address}: resource moves and imports are blocked")
        drift_changes.append((address, resource_drift))

    for address, resource_change in changes_by_address.items():
        resource_type, name = by_address[address]
        change = resource_change["change"]
        repository = inventory.find(name)
        if repository is None:
            raise FleetError(f"{address}: repository is not in the inventory")
        if repository.archived and change.get("actions") != ["no-op"]:
            raise FleetError(f"{address}: archived repositories are read-only")
        _validate_protected_values(
            address, resource_type, repository, change, changes_by_address
        )
    for address, resource_drift in drift_changes:
        resource_type, name = by_address[address]
        repository = inventory.find(name)
        if repository is None:
            raise FleetError(f"{address}: repository is not in the inventory")
        change = resource_drift["change"]
        if repository.archived and change.get("actions") != ["no-op"]:
            raise FleetError(f"{address}: archived repositories are read-only")
        _validate_protected_values(
            address, resource_type, repository, change, changes_by_address
        )
    if plan.get("output_changes"):
        raise FleetError("Terraform plan contains unexpected output changes")


def prepare_plan(
    inventory: Inventory,
    terraform_dir: Path,
    state_dir: Path,
    runner: CommandRunner,
) -> dict[str, str]:
    organization, workspace, workspace_id = verify_workspace()
    token = _required_value(os.environ, "TF_TOKEN_app_terraform_io")
    environment = _terraform_environment(token, organization, workspace)
    plan_path = state_dir / "settings.tfplan"
    plan_json_path = state_dir / "settings-plan.json"
    _run_init(terraform_dir, runner, workspace, environment)

    addresses = runner.run(
        ["terraform", "state", "list"], cwd=terraform_dir, env=environment
    ).stdout.splitlines()
    state_output = runner.run(
        ["terraform", "show", "-json"], cwd=terraform_dir, env=environment
    ).stdout
    try:
        state = json.loads(state_output)
    except json.JSONDecodeError as err:
        raise FleetError("Terraform returned an invalid state snapshot") from err
    validate_state(inventory, addresses, state)
    raw_state = _terraform_state(runner, terraform_dir, environment)
    state_digest = hashlib.sha256(
        json.dumps(raw_state, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    runner.run(
        [
            "terraform",
            "plan",
            "-input=false",
            "-no-color",
            "-lock-timeout=5m",
            "-out",
            str(plan_path),
        ],
        cwd=terraform_dir,
        env=environment,
    )
    plan_output = runner.run(
        ["terraform", "show", "-json", str(plan_path)],
        cwd=terraform_dir,
        env=environment,
    ).stdout
    try:
        plan = json.loads(plan_output)
    except json.JSONDecodeError as err:
        raise FleetError("Terraform returned an invalid saved plan") from err
    validate_plan(plan, inventory)
    plan_json_path.write_text(
        json.dumps(plan, sort_keys=True, separators=(",", ":")), encoding="utf-8"
    )
    return {
        "organization": organization,
        "workspace": workspace,
        "workspace_id": workspace_id,
        "state_digest": state_digest,
        "plan_digest": _file_digest(plan_path),
        "plan_json_digest": _file_digest(plan_json_path),
    }


def apply_plan(
    inventory: Inventory,
    terraform_dir: Path,
    state_dir: Path,
    runner: CommandRunner,
    metadata: Mapping[str, str],
) -> None:
    organization, workspace, workspace_id = verify_workspace()
    if (
        organization != metadata.get("organization")
        or workspace != metadata.get("workspace")
        or workspace_id != metadata.get("workspace_id")
    ):
        raise FleetError("HCP Terraform workspace changed after preflight")
    token = _required_value(os.environ, "TF_TOKEN_app_terraform_io")
    environment = _terraform_environment(token, organization, workspace)
    _run_init(terraform_dir, runner, workspace, environment)

    addresses = runner.run(
        ["terraform", "state", "list"], cwd=terraform_dir, env=environment
    ).stdout.splitlines()
    state_output = runner.run(
        ["terraform", "show", "-json"], cwd=terraform_dir, env=environment
    ).stdout
    try:
        state = json.loads(state_output)
        raw_state = _terraform_state(runner, terraform_dir, environment)
        plan_output = runner.run(
            ["terraform", "show", "-json", str(state_dir / "settings.tfplan")],
            cwd=terraform_dir,
            env=environment,
        ).stdout
        plan = json.loads(plan_output)
    except (OSError, json.JSONDecodeError) as err:
        raise FleetError(
            "saved Terraform preflight data is missing or invalid"
        ) from err
    validate_state(inventory, addresses, state)
    state_digest = hashlib.sha256(
        json.dumps(raw_state, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    validate_plan(plan, inventory)
    canonical_plan_digest = hashlib.sha256(
        json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if (
        state_digest != metadata.get("state_digest")
        or _file_digest(state_dir / "settings.tfplan") != metadata.get("plan_digest")
        or canonical_plan_digest != metadata.get("plan_json_digest")
        or _file_digest(state_dir / "settings-plan.json")
        != metadata.get("plan_json_digest")
    ):
        raise FleetError("Terraform state or saved plan changed after preflight")

    runner.run(
        [
            "terraform",
            "apply",
            "-input=false",
            "-no-color",
            "-lock-timeout=5m",
            str(state_dir / "settings.tfplan"),
        ],
        cwd=terraform_dir,
        env=environment,
    )
    final_addresses = runner.run(
        ["terraform", "state", "list"], cwd=terraform_dir, env=environment
    ).stdout.splitlines()
    final_state_output = runner.run(
        ["terraform", "show", "-json"], cwd=terraform_dir, env=environment
    ).stdout
    try:
        final_state = json.loads(final_state_output)
    except json.JSONDecodeError as err:
        raise FleetError("Terraform returned an invalid post-apply state") from err
    validate_state(inventory, final_addresses, final_state)


def _run_init(
    terraform_dir: Path,
    runner: CommandRunner,
    workspace: str,
    environment: Mapping[str, str | None],
) -> None:
    runner.run(
        ["terraform", "init", "-input=false"],
        cwd=terraform_dir,
        env=environment,
    )
    selected = runner.run(
        ["terraform", "workspace", "show"], cwd=terraform_dir, env=environment
    ).stdout.strip()
    if selected != workspace:
        raise FleetError("Terraform selected a different workspace than preflight")


def _terraform_environment(
    token: str, organization: str, workspace: str
) -> dict[str, str | None]:
    return {
        "TF_TOKEN_app_terraform_io": token,
        "TF_CLOUD_ORGANIZATION": organization,
        "TF_WORKSPACE": workspace,
        "TF_IN_AUTOMATION": "1",
        "GH_TOKEN": None,
        "TF_CLOUD_TOKEN": None,
        "GITHUB_APP_ID": None,
        "GITHUB_APP_INSTALLATION_ID": None,
        "GITHUB_APP_PEM_FILE": None,
    }


def _terraform_state(
    runner: CommandRunner,
    terraform_dir: Path,
    environment: Mapping[str, str | None],
) -> object:
    output = runner.run(
        ["terraform", "state", "pull"], cwd=terraform_dir, env=environment
    ).stdout
    try:
        return json.loads(output)
    except json.JSONDecodeError as err:
        raise FleetError("Terraform returned an invalid raw state snapshot") from err


def _required_value(environ: Mapping[str, str], key: str) -> str:
    value = environ.get(key, "").strip()
    if not value:
        raise FleetError(f"required environment setting {key} is missing")
    return value


def _state_resources(state: object) -> dict[str, dict[str, Any]]:
    if not isinstance(state, dict):
        raise FleetError("Terraform returned invalid state data")
    values = state.get("values")
    root = values.get("root_module") if isinstance(values, dict) else None
    if not isinstance(root, dict):
        raise FleetError("Terraform state has no root module")
    resources: dict[str, dict[str, Any]] = {}

    def visit(module: dict[str, Any]) -> None:
        entries = module.get("resources", [])
        if not isinstance(entries, list):
            raise FleetError("Terraform state contains invalid resource data")
        for resource in entries:
            if not isinstance(resource, dict) or not isinstance(
                resource.get("address"), str
            ):
                raise FleetError("Terraform state contains an invalid resource")
            resources[resource["address"]] = resource
        modules = module.get("child_modules", [])
        if not isinstance(modules, list):
            raise FleetError("Terraform state contains invalid module data")
        for child in modules:
            if not isinstance(child, dict):
                raise FleetError("Terraform state contains an invalid module")
            visit(child)

    visit(root)
    return resources


def _validate_protected_values(
    address: str,
    resource_type: str,
    repository: Any,
    change: dict[str, Any],
    changes_by_address: Mapping[str, dict[str, Any]],
) -> None:
    before = change.get("before")
    after = change.get("after")
    if not isinstance(before, dict) or not isinstance(after, dict):
        raise FleetError(f"{address}: protected before/after values are unavailable")
    unknown = change.get("after_unknown")
    for attribute in PROTECTED_PLAN_ATTRIBUTES[resource_type]:
        if _contains_unknown(
            unknown.get(attribute) if isinstance(unknown, dict) else None
        ):
            raise FleetError(f"{address}: protected Terraform value is unknown")
    if resource_type == "github_repository":
        _validate_repository_values(address, before, after, repository)
    elif resource_type == "github_workflow_repository_permissions":
        _validate_workflow_permissions(address, before, after, repository.name)
    else:
        _validate_ruleset_values(
            address, before, after, repository.name, changes_by_address
        )


def _validate_repository_values(
    address: str, before: dict[str, Any], after: dict[str, Any], repository: Any
) -> None:
    for values in (before, after):
        if (
            values.get("name") != repository.name
            or values.get("visibility") != repository.visibility
            or values.get("archived") is not repository.archived
        ):
            raise FleetError(
                f"{address}: name, visibility, or archive changes are blocked"
            )
    changed = _changed_keys(before, after)
    allowed = MANAGED_SETTINGS if not repository.archived else frozenset()
    if changed - allowed:
        raise FleetError(f"{address}: unknown repository setting changes are blocked")


def _validate_workflow_permissions(
    address: str, before: dict[str, Any], after: dict[str, Any], repository: str
) -> None:
    if before.get("repository") != repository or after.get("repository") != repository:
        raise FleetError(f"{address}: repository identity changed")
    if after.get("default_workflow_permissions") != "read":
        raise FleetError(f"{address}: Actions token permissions must remain read-only")
    if after.get("can_approve_pull_request_reviews") != before.get(
        "can_approve_pull_request_reviews"
    ):
        raise FleetError(f"{address}: changing Actions approval capability is blocked")
    if _changed_keys(before, after) - {"default_workflow_permissions"}:
        raise FleetError(f"{address}: unknown Actions permission changes are blocked")


def _validate_ruleset_values(
    address: str,
    before: dict[str, Any],
    after: dict[str, Any],
    repository: str,
    changes_by_address: Mapping[str, dict[str, Any]],
) -> None:
    expected_name = (
        "default-branch-safety"
        if address.startswith("github_repository_ruleset.default_branch_safety[")
        else "default-branch-pull-request"
    )
    if (
        before.get("name") != expected_name
        or after.get("name") != expected_name
        or before.get("repository") != repository
        or after.get("repository") != repository
        or before.get("target") != "branch"
        or after.get("target") != "branch"
        or before.get("enforcement") != "active"
        or after.get("enforcement") != "active"
        or before.get("conditions") != after.get("conditions")
        or not _default_branch_scope(after.get("conditions"))
        or before.get("bypass_actors") != after.get("bypass_actors")
    ):
        raise FleetError(f"{address}: ruleset scope, enforcement, or bypass changed")
    if not isinstance(before.get("rules"), list) or not isinstance(
        after.get("rules"), list
    ):
        raise FleetError(f"{address}: ruleset rules are unavailable")
    if address.startswith("github_repository_ruleset.default_branch_safety["):
        _validate_safety_rules(address, before["rules"], after["rules"])
        return
    _validate_pull_request_rules(
        address, before["rules"], after["rules"], repository, changes_by_address
    )


def _validate_safety_rules(
    address: str, before_rules: list[Any], after_rules: list[Any]
) -> None:
    if len(before_rules) != 1 or len(after_rules) != 1:
        raise FleetError(f"{address}: unknown safety rules are blocked")
    before, after = before_rules[0], after_rules[0]
    if not isinstance(before, dict) or not isinstance(after, dict):
        raise FleetError(f"{address}: safety rules are invalid")
    if after.get("deletion") is not True or after.get("non_fast_forward") is not True:
        raise FleetError(f"{address}: deletion or force-push protection weakened")
    if _changed_keys(before, after) - {"deletion", "non_fast_forward"}:
        raise FleetError(f"{address}: deletion or force-push protection weakened")


def _validate_pull_request_rules(
    address: str,
    before_rules: list[Any],
    after_rules: list[Any],
    repository: str,
    changes_by_address: Mapping[str, dict[str, Any]],
) -> None:
    if len(before_rules) != 1 or len(after_rules) != 1:
        raise FleetError(f"{address}: unknown pull-request rules are blocked")
    before, after = before_rules[0], after_rules[0]
    if not isinstance(before, dict) or not isinstance(after, dict):
        raise FleetError(f"{address}: pull-request rules are invalid")
    before_pull = _single_pull_request_rule(before)
    after_pull = _single_pull_request_rule(after)
    old_approvals = before_pull.get("required_approving_review_count")
    new_approvals = after_pull.get("required_approving_review_count")
    if (
        not isinstance(old_approvals, int)
        or isinstance(old_approvals, bool)
        or not isinstance(new_approvals, int)
        or isinstance(new_approvals, bool)
        or new_approvals < old_approvals
    ):
        raise FleetError(f"{address}: required approvals may not decrease")
    if after_pull.get("allowed_merge_methods") != _expected_merge_methods(
        repository, changes_by_address
    ):
        raise FleetError(f"{address}: pull-request merge methods differ from settings")
    if _changed_keys(before, after) - {"pull_request"}:
        raise FleetError(f"{address}: unknown pull-request protection changed")
    if _changed_keys(before_pull, after_pull) - {
        "required_approving_review_count",
        "allowed_merge_methods",
    }:
        raise FleetError(f"{address}: unknown pull-request protection changed")


def _single_pull_request_rule(values: dict[str, Any]) -> dict[str, Any]:
    pull_request = values.get("pull_request")
    if not isinstance(pull_request, list) or len(pull_request) != 1:
        raise FleetError("Terraform plan contains an unknown pull-request rule")
    rule = pull_request[0]
    if not isinstance(rule, dict):
        raise FleetError("Terraform plan contains an invalid pull-request rule")
    return rule


def _expected_merge_methods(
    repository: str, changes_by_address: Mapping[str, dict[str, Any]]
) -> list[str]:
    address = f"github_repository.active[{json.dumps(repository)}]"
    resource_change = changes_by_address.get(address)
    if resource_change is None:
        raise FleetError(f"{address}: repository change is missing from the plan")
    change = resource_change.get("change")
    values = change.get("after") if isinstance(change, dict) else None
    if not isinstance(values, dict):
        raise FleetError(f"{address}: planned merge settings are unavailable")
    return [
        method
        for attribute, method in (
            ("allow_merge_commit", "merge"),
            ("allow_squash_merge", "squash"),
            ("allow_rebase_merge", "rebase"),
        )
        if values.get(attribute) is True
    ]


def _default_branch_scope(conditions: object) -> bool:
    if not isinstance(conditions, list) or len(conditions) != 1:
        return False
    condition = conditions[0]
    if not isinstance(condition, dict):
        return False
    ref_name = condition.get("ref_name")
    if not isinstance(ref_name, list) or len(ref_name) != 1:
        return False
    refs = ref_name[0]
    return (
        isinstance(refs, dict)
        and refs.get("include") == ["~DEFAULT_BRANCH"]
        and refs.get("exclude") == []
    )


def _changed_keys(before: dict[str, Any], after: dict[str, Any]) -> set[str]:
    return {
        key for key in before.keys() | after.keys() if before.get(key) != after.get(key)
    }


def _contains_unknown(value: object) -> bool:
    if value is True:
        return True
    if isinstance(value, dict):
        return any(_contains_unknown(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_unknown(item) for item in value)
    return False


def _file_digest(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as err:
        raise FleetError(f"saved Terraform file is missing: {path.name}") from err

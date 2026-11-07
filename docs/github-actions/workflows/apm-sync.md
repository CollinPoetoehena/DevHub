# Central Repository Fleet Sync

[`apm-sync.yml`](../../../.github/workflows/apm-sync.yml) is the single DevHub-owned workflow that reconciles all Terraform-managed repository settings and prepares shared template and APM files for the complete active inventory. The historical filename is retained; the workflow is no longer an APM-only sync.

## Table of Contents

- [Ownership and design](#ownership-and-design)
- [Why central push, not consumer pull](#why-central-push-not-consumer-pull)
- [Triggers and repository scope](#triggers-and-repository-scope)
- [Execution stages](#execution-stages)
- [Settings safety gate](#settings-safety-gate)
- [Credentials and state](#credentials-and-state)
- [Bootstrap and adoption](#bootstrap-and-adoption)
- [Failure handling and recovery](#failure-handling-and-recovery)
- [Validation](#validation)

---

## Ownership and design

The workflow is the only fleet writer. Terraform owns the existing managed platform settings; `repo-fleet` reuses its template renderer, pinned APM CLI, inventory, branch lease, and pull-request helpers for content changes. `repo-tools.yml` remains validation-only.

```text
trusted DevHub main SHA
       |
       v
offline checks -> verify HCP workspace/state -> guarded saved plan
       |                                      |
       +-> prepare every active repo --------+
                                              v
                                    apply saved settings plan
                                              |
                                              v
                               one combined PR per changed repo
```

Each active repository gets at most one `devhub/repo-sync` branch and one PR containing all changed shared templates, APM lock/deployment files, a missing seed manifest, and an exact recognized legacy-caller removal. No-change repositories get no branch or PR. Archived entries are checked as adopted Terraform state but are not changed by the settings plan or file preparation.

---

## Why central push, not consumer pull

One central push workflow reads one inventory and one version of policy, then opens reviewable PRs in the managed repositories. It avoids deploying a second writer workflow and credential to every consumer, prevents consumer jobs from choosing a different DevHub revision, and lets one serialized run preflight the entire fleet before settings are applied. Consumers still review and merge their own content PRs; this workflow never writes to a consumer's default branch.

---

## Triggers and repository scope

The workflow runs on pushes to DevHub `main` that touch `tools/repo/**`, `packages/apm/**`, root `apm.yml` or `apm.lock.yaml`, or either fleet-related workflow. `workflow_dispatch` is also available, but the job is restricted to `refs/heads/main` and checks out `github.sha`, the triggering commit. There is no schedule, reusable caller, consumer-side workflow, or second fleet-sync workflow. Runs share a non-cancelling concurrency group.

---

## Execution stages

The single protected job runs these stages in order:

1. **Validate.** Install locked Python dependencies and pinned APM/Terraform tools, then validate the inventory and render all active templates without network access.
2. **Plan settings.** Verify HCP Terraform workspace identity and local execution mode, exact adopted resource addresses, and repository identities. Create a saved plan and reject unsafe or unknown actions.
3. **Prepare content.** Use the separate contents token to clone and prepare every active repository with existing combined template-plus-APM logic. Capture base revisions and digests before any settings are applied.
4. **Revalidate and apply.** Confirm the source SHA, inventory, prepared checkouts, default branches, remote base SHAs, workspace, state, and saved plan remain unchanged. Apply only that saved Terraform plan.
5. **Deliver.** Use the contents token to create or update the combined PRs from the exact prepared checkouts. APM is not rerun after settings apply.
6. **Clean up.** Always remove the job-local saved plan, JSON plan, metadata, and temporary checkouts. No plans or preparations are uploaded or retained.

The saved plan and all intermediate data live only in a private-permission directory under the ephemeral runner's temporary directory. They are never printed, uploaded as artifacts, or written into a repository. Each phase passes only the SHA-256 digest of its metadata through the protected job's step-output channel; later phases reject a changed plan, preparation, or apply marker.

---

## Settings safety gate

The gate accepts only no-op and in-place updates to the existing adopted resources. It rejects resource creation, deletion, replacement, imports, moves, unknown resources, incomplete plans, and unexpected output changes. It also requires exact repository names and inventory visibility/archive state.

Allowed managed changes are limited to merge settings and the default `GITHUB_TOKEN` permission tightening to read. The gate preserves Actions approval capability as-is and rejects enabling it. For branch rulesets it requires the existing default-branch scope, active enforcement, unchanged bypass actors, deletion and force-push protection, and a nondecreasing required approval count. Unknown or weakened protected values fail closed. Adding a repository or changing visibility, archive state, ruleset ownership, or approval capability requires a separately reviewed operator action; the automation never creates or imports resources.

---

## Credentials and state

Configure the existing `apm-sync` Actions environment with a deployment branch policy restricted to `main`. Store the following secrets there and configure the two workspace values as environment variables:

| Name | Use | Minimum intended access |
|---|---|---|
| `REPO_FLEET_SYNC_TOKEN` | Preparation and PR delivery only | Contents, pull requests, and workflow-file writes to the managed repositories |
| `REPO_FLEET_SETTINGS_TOKEN` | Terraform plan/apply only | Contents read, repository administration, and Actions settings access to the managed repositories |
| `HCP_TERRAFORM_TOKEN` | HCP Terraform state and workspace checks | Workspace-scoped state read/write and locking access |
| `TF_CLOUD_ORGANIZATION` | HCP Terraform organization identity | Environment variable, not a credential |
| `TF_WORKSPACE` | HCP Terraform workspace identity | Environment variable, not a credential |

The workflow `GITHUB_TOKEN` permissions remain read-only. Only the settings steps receive `REPO_FLEET_SETTINGS_TOKEN` as `GITHUB_TOKEN` and the HCP token. Only preparation and delivery receive `REPO_FLEET_SYNC_TOKEN` as `GH_TOKEN`. APM subprocesses run with isolated GitHub configuration and no GitHub, Actions, Terraform, or Git credential pointers. Git write operations use a temporary per-command helper and disable hooks; no global Git credential configuration is created.

Terraform uses the pre-created HCP Terraform workspace as durable, locked remote state, with **local execution mode** so the Actions runner performs Terraform commands. The HCP workspace must not have VCS-driven runs or remote execution enabled. Missing state, a workspace mismatch, or any mismatch in the full expected address set blocks the run; the runner never treats missing state as permission to create the fleet.

The empty `cloud` block selects the verified organization and workspace using `TF_CLOUD_ORGANIZATION` and `TF_WORKSPACE`; the runner invokes `terraform init -input=false` without backend configuration flags. See the [cloud block environment variables](https://developer.hashicorp.com/terraform/language/block/terraform#environment-variables-for-the-cloud-block).

---

## Bootstrap and adoption

An operator must complete setup before enabling the protected environment:

1. Create the HCP Terraform organization and workspace outside this workflow. Configure the workspace for local execution, disable VCS-driven runs and automatic apply, and grant the HCP token access only to that workspace.
2. Inspect any trusted existing Terraform state. If valid state exists, migrate it to the HCP workspace using Terraform's reviewed state migration process. If state does not exist, explicitly import every inventory repository and existing managed settings resource before enabling automation.
3. Adopt the exact resource addresses declared in [`tools/repo/terraform/`](../../../tools/repo/terraform/): active and archived repositories, active workflow permissions, and both active default-branch rulesets. Archived repositories have only the archived repository resource. Reconcile missing rulesets with a separately reviewed change. Do not remove state, add resources, or create imports to make an automated plan pass.
4. Set the environment variables and secrets above and verify the environment branch policy, repository token scopes, and HCP workspace mode.
5. Run the validation commands below. The first credentialed run must be deliberately authorized and reviewed; this implementation does not perform live setup or apply during development validation.

Terraform's standard [state migration](https://developer.hashicorp.com/terraform/cli/cloud/settings) and [import](https://developer.hashicorp.com/terraform/cli/commands/import) procedures remain operator-controlled. Never place state, plans, credentials, or migration backups in Git or public workflow artifacts.

---

## Failure handling and recovery

Any validation, credential, state, saved-plan, content-preparation, freshness, or tamper failure stops the job before settings apply and PR delivery. A settings apply failure suppresses all content PR delivery, including when a provider partially applied the saved plan. GitHub does not provide a fleet-wide transaction: inspect authoritative Terraform state and make any recovery a separately reviewed operation; do not assume closing a PR reverses settings.

After settings apply succeeds, repository deliveries are independent. The workflow attempts the remaining prepared repositories after an individual delivery failure, reports sanitized counts, and exits unsuccessfully if any delivery failed. A rerun starts from a fresh workspace/state and repository preflight. Lease conflicts and changed default-branch bases fail rather than overwriting concurrent work. Review, update, or close the resulting PRs in each consumer repository; no default branch is pushed.

---

## Validation

`repo-tools.yml` checks Terraform formatting/validation/tests and the Python fleet lint, type, unit, integration, and contract suites. Local checks do not use GitHub or HCP credentials:

```bash
cd tools/repo/terraform
terraform fmt -check -recursive
terraform init -backend=false -input=false
terraform validate
terraform test

cd ../fleet
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest --cov=repo_fleet --cov-report=term-missing
uv run repo-fleet check
uv run pip-audit
```

The workflow's settings plan/apply and remote repository delivery require the external bootstrap and credentials above. They are not run by local validation.

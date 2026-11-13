# Repository Fleet Management

The authoritative design and operating guide for my GitHub repositories. Terraform owns each repository as a platform resource: existence, visibility, merge settings, rulesets, and Actions permissions. The Python `repo-fleet` tool owns shared repository content: it renders per-profile templates and delivers them through pull requests. Both read one inventory.

The [repository-fleet ADRs](adrs/README.md) record the rationale for these tool boundaries, the shared inventory, and centralized fleet sync.

## Table of Contents

- [Scope and design](#scope-and-design)
  - [Why Terraform and Python](#why-terraform-and-python)
  - [Layout](#layout)
  - [Inventory](#inventory)
  - [Profiles](#profiles)
  - [Protection and solo reviews](#protection-and-solo-reviews)
  - [Deletion safety](#deletion-safety)
- [Architecture decisions](#architecture-decisions)
- [Authentication](#authentication)
- [State](#state)
- [Terraform operations](#terraform-operations)
  - [Adopt existing repositories](#adopt-existing-repositories)
  - [Add a repository](#add-a-repository)
  - [Archive or stop managing a repository](#archive-or-stop-managing-a-repository)
- [Templates](#templates)
- [Fleet operations](#fleet-operations)
- [APM sync](#apm-sync)
- [Rollout](#rollout)
- [Validation](#validation)

---

## Scope and design

```text
terraform/repositories.auto.tfvars.json   (single inventory)
          |                                  |
   Terraform (terraform/)            repo-fleet (fleet/)
   repository, rulesets,             templates/<profile>/{sync,seed}
   Actions permissions                       |
          |                          branch devhub/repo-sync -> pull request
   reviewed plan -> apply                    |
          v                                  v
                 GitHub repositories
```

### Why Terraform and Python

Each tool owns the part its model fits:

| Concern | Owner | Reason |
|---|---|---|
| Repository existence, visibility, settings, rulesets, Actions permissions | Terraform | Long-lived platform resources; state, imports, drift detection, and reviewable plans come from the [GitHub provider](https://registry.terraform.io/providers/integrations/github/6.13.0/docs) |
| Shared files such as workflows | `repo-fleet` | Git already versions file content; templating, diffs, and pull requests are natural in Python, and file contents stay out of Terraform state |
| APM packages | [Central APM sync](../../docs/github-actions/workflows/apm-sync.md) | DevHub checks the inventory and opens per-repository pull requests from one central workflow |

The [tool-boundary ADR](adrs/TOOL-BOUNDARIES.md) compares these responsibilities with Terraform-only and Python-only designs.

### Layout

| Path | Content |
|---|---|
| [`terraform/`](terraform/) | Terraform root, inventory, and [tests](terraform/tests/) |
| [`fleet/`](fleet/) | `repo-fleet` [uv](https://docs.astral.sh/uv/) project (`src/repo_fleet`, `tests/`) |
| [`templates/`](templates/) | Template files per profile |

### Inventory

[`terraform/repositories.auto.tfvars.json`](terraform/repositories.auto.tfvars.json) is the single source of truth. Terraform loads it automatically as the `inventory` variable; `repo-fleet` reads the same file. Repositories are listed explicitly; nothing is discovered from the account or local checkouts. The [shared-inventory ADR](adrs/SHARED-INVENTORY.md) records the format choice and alternatives.

```json
{
  "inventory": {
    "owner": "CollinPoetoehena",
    "repositories": {
      "example": { "visibility": "public", "profiles": ["common"], "archived": false, "apm_stacks": ["python"] }
    }
  }
}
```

The inventory requires each repository's visibility, profiles, and archive state. Optional `apm_stacks` selects stack APM packages (`containerization`, `go`, `iac`, `java`, `python`, or `rust`); common is always included. Omitted values default to an empty list. [`variables.tf`](terraform/variables.tf) and `repo-fleet` validate stack values alongside the required inventory fields. `repo-fleet` also rejects unknown keys. A profile without a template folder renders no files, so an unknown profile is caught by `terraform test` and `terraform plan`, which load the inventory; [CI](#validation) runs `terraform test` together with the fleet checks.

### Profiles

A profile names both a settings block in [`profiles.tf`](terraform/profiles.tf) and an optional template folder `templates/<profile>/`. Settings of later profiles override earlier ones; templates of different profiles must not target the same path. Only `common` exists: add a profile only when its policy actually differs.

The `common` profile:

- Allows squash merges only and deletes merged branches.
- Adds two rulesets on the default branch (`~DEFAULT_BRANCH`, so renaming the branch needs no change): `default-branch-safety` blocks deletion and force pushes without bypass, and `default-branch-pull-request` requires a pull request with one approval and squash merges.
- Sets the default `GITHUB_TOKEN` permission to read and allows repository workflows to create and approve pull requests. The central [APM sync](#apm-sync) uses its separately scoped fleet token.

Unmanaged settings such as description, topics, and features are ignored by Terraform, so they can be changed in GitHub without drift.

### Protection and solo reviews

GitHub does not let authors approve their own pull requests. The pull request ruleset therefore lets the repository admin role bypass it in `pull_request` mode only: an admin can merge their own pull request, but direct pushes to the default branch stay blocked. Rulesets on private repositories need [GitHub Pro](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets).

### Deletion safety

Several independent guards keep a repository from being deleted by accident:

1. `prevent_destroy` on every repository resource: Terraform refuses any plan that destroys one, including after removing it from the inventory.
2. `archive_on_destroy`: if a destroy is ever forced, the provider archives the repository instead of deleting it.
3. The credentials should lack the `delete_repo` scope, so GitHub itself refuses deletion; see [authentication](#authentication).
4. Default-branch rulesets block deletion and force pushes, and `repo-fleet` only pushes its own branch.

Archived repositories are a separate resource that ignores all changes, so Terraform never reactivates or edits them.

## Architecture decisions

| ADR | Decision |
|---|---|
| [Tool boundaries](adrs/TOOL-BOUNDARIES.md) | Keep repository platform settings in Terraform and shared content delivery in Python `repo-fleet`. |
| [Shared inventory](adrs/SHARED-INVENTORY.md) | Use one validated JSON inventory as the input to both tools. |
| [Central fleet sync](adrs/CENTRAL-FLEET-SYNC.md) | Reconcile settings centrally and deliver shared content through reviewed pull requests after preflight. |

---

## Authentication

Both tools use the [GitHub CLI](https://cli.github.com/) login of the operator; no credentials are stored in this repository or in Terraform variables.

```bash
gh auth login --scopes repo,workflow
gh auth status
```

- Terraform uses `GITHUB_TOKEN` when set, otherwise the provider falls back to `gh auth token`; see [provider authentication](https://registry.terraform.io/providers/integrations/github/6.13.0/docs#authentication).
- `repo-fleet` calls `gh` and `git`; the `workflow` scope is needed because templates write `.github/workflows/`.
- Do not grant `delete_repo`. Check the scopes with `gh auth status`.

---

## State

Terraform uses a pre-created HCP Terraform workspace as durable, locked remote state. The workspace must use local execution mode; the Actions runner performs Terraform commands while HCP Terraform stores and locks state. Configure `TF_CLOUD_ORGANIZATION`, `TF_WORKSPACE`, and `TF_TOKEN_app_terraform_io` for local operations. Do not initialize a fresh empty workspace against the inventory and apply: exact adopted resource addresses are a precondition, and missing state is not permission to create or import resources. The empty `cloud` block reads the organization and workspace from these environment variables; `-backend-config` is not valid for HCP Terraform. See the [Terraform cloud block reference](https://developer.hashicorp.com/terraform/language/block/terraform#environment-variables-for-the-cloud-block).

---

## Terraform operations

Run from `tools/repo/terraform` with the HCP Terraform workspace and token configured. Always apply a reviewed saved plan; never use `-auto-approve` or `-target`.

```bash
terraform init -input=false
terraform plan -out=tfplan
terraform show tfplan    # review
terraform apply tfplan
rm tfplan
```

### Adopt existing repositories

Creating a repository that already exists fails, so existing repositories are imported once. Import with [`import`](https://developer.hashicorp.com/terraform/cli/commands/import) per address:

```bash
terraform import 'github_repository.active["NAME"]' NAME
terraform import 'github_workflow_repository_permissions.active["NAME"]' NAME
terraform import 'github_repository.archived["NAME"]' NAME    # archived repositories
```

Rulesets are imported as `NAME:ID`. Look up existing ruleset IDs, import the ones matching `default-branch-safety` and `default-branch-pull-request`, and delete other old rulesets in GitHub after the plan shows equivalent protection:

```bash
gh api repos/CollinPoetoehena/NAME/rulesets --jq '.[] | "\(.id) \(.name)"'
terraform import 'github_repository_ruleset.default_branch_safety["NAME"]' NAME:ID
terraform import 'github_repository_ruleset.default_branch_pull_request["NAME"]' NAME:ID
```

Then plan and confirm that only intended in-place updates and new rulesets remain.

### Add a repository

1. Add the entry to the [inventory](#inventory) with `profiles: ["common"]` and `archived: false`.
2. Plan, review, and apply. The repository is created with an initial commit so the default branch exists for the rulesets.
3. Run `repo-fleet plan --repo NAME` and `repo-fleet apply --repo NAME` to open the template pull request.

### Archive or stop managing a repository

- **Archive:** archive it with `gh repo archive`, set `archived: true`, add a `moved` block from `github_repository.active["NAME"]` to `github_repository.archived["NAME"]`, and `terraform state rm` its rulesets and workflow permissions (archived repositories reject updates). Plan to confirm no destroy.
- **Stop managing:** `terraform state rm` every address of the repository, then remove the inventory entry. Removing only the entry is refused by `prevent_destroy`.
- **Delete:** an explicit manual action in GitHub, never through Terraform.

---

## Templates

Templates live in `templates/<profile>/` with two ownership modes:

| Folder | Behavior |
|---|---|
| `sync/` | Owned by DevHub: created and overwritten on every apply. A first line `# Managed by DevHub tools/repo (templates/<profile>/sync); local changes are overwritten.` is added (after a shebang if present). Only `#`-comment formats are allowed: `.yml`, `.yaml`, `.sh`, `.toml`, `.tf`, `.py`, `.cfg`, `CODEOWNERS`, `.gitignore`, `.gitattributes`, and `.editorconfig` |
| `seed/` | Created only when missing; afterwards the repository owns the file |

Files ending in `.tmpl` are rendered with Python's [`string.Template`](https://docs.python.org/3/library/string.html#template-strings) and the suffix is removed; other files are copied byte for byte, so GitHub Actions `${{ }}` expressions need no escaping. Available variables: `$owner`, `$repository`, `$visibility`, `$profiles` (comma-separated), and `$default_branch`; an unknown variable is an error and `$$` writes a literal `$`. Conflicting target paths, symlinks, and paths inside `.git` are rejected.

Removing a template does not delete the file from repositories; remove it there with a normal pull request.

Current templates:

| Profile | File | Purpose |
|---|---|---|
| `common` | [`seed/apm.yml.tmpl`](templates/common/seed/apm.yml.tmpl) | Seeds an APM manifest using the caller-supplied `$apm_dependencies`; choose the current shared-guideline and local-development packages using the [APM guide](../../packages/apm/README.md#package-design). Existing manifests remain repository-owned. |

---

## Fleet operations

Run from `tools/repo/fleet` with [uv](https://docs.astral.sh/uv/); Python 3.12 or later.

```bash
uv sync --locked
uv run repo-fleet check                   # offline: validate inventory, render all templates
uv run repo-fleet plan [--repo NAME] [--diff]
uv run repo-fleet apply [--repo NAME] [--yes]
uv run repo-fleet plan --apm [--repo NAME] [--diff]
uv run repo-fleet apply --apm [--repo NAME] [--yes]
```

| Command | Behavior | Exit codes |
|---|---|---|
| `check` | Loads the inventory and renders every active repository's templates without network access | 0 valid, 1 error |
| `plan` | Shallow-clones each active repository's default branch into a temporary directory and lists `create`, `update`, `unchanged`, or `seed-skip` per file | 0 no changes, 2 changes, 1 error |
| `apply` | Plans, asks for confirmation (or `--yes`; non-interactive sessions without it are refused), then per repository with changes commits to `devhub/repo-sync`, force-pushes it with a lease, and creates or updates one pull request | 0 success, 1 error or declined |
| `plan --apm` | Prepares APM updates and legacy-caller migration in temporary checkouts; exit 0 current, 2 changes, 1 error | 0 no changes, 2 changes, 1 error |
| `apply --apm` | Preflights every selected active repository before opening any pull requests, using `devhub/apm-sync` | 0 success, 1 error or declined |

Archived repositories are skipped. A repository without changes gets no branch or pull request; an unchanged branch is not pushed again. The tool never pushes the default branch. `--inventory` and `--templates`, or the `REPO_FLEET_INVENTORY` and `REPO_FLEET_TEMPLATES` environment variables, override the default paths.

---

## Central fleet sync

The [single central fleet workflow](../../docs/github-actions/workflows/apm-sync.md) owns all managed repository settings and combined template/APM content updates. It runs only in DevHub on relevant pushes to `main` or by manual dispatch, preflights the entire active inventory, applies only an allowed saved settings plan, then opens one combined `devhub/repo-sync` PR per changed repository. Archived repositories are verified in state but never mutated by sync. The [central-sync ADR](adrs/CENTRAL-FLEET-SYNC.md) records why the workflow is centralized and the safeguards that bound it. The APM CLI is pinned to 0.35.0; eligible `#main` dependencies are refreshed, commit-pinned dependencies are preserved, and local dependencies are redeployed when needed.

The DevHub `apm-sync` Actions environment must restrict deployments to `main` and hold separate `REPO_FLEET_SYNC_TOKEN`, `REPO_FLEET_SETTINGS_TOKEN`, and `HCP_TERRAFORM_TOKEN` secrets, plus `TF_CLOUD_ORGANIZATION` and `TF_WORKSPACE` variables. The HCP workspace must exist in local execution mode and contain the exact adopted Terraform resources before automation is authorized. The central guide documents required token scopes, bootstrap/adoption, safety gates, and failure recovery.

For manual content-only operations, authenticate `gh` with repository access and run `uv run repo-fleet plan --apm` followed by `uv run repo-fleet apply --apm`. The planner prepares all selected repositories before any PR writes. `--apm` is opt-in; regular `check`, `plan`, and `apply` keep their existing template-only behavior. A missing `apm.yml` is seeded from common plus configured `apm_stacks`; existing manifests are not rewritten. If an old `devhub-apm-sync.yml` caller exactly matches the known template it is removed with the APM changes; a customized caller is preserved and causes a safe error for manual review.

---

## Rollout

1. Create the HCP Terraform workspace in local execution mode and adopt all existing managed addresses through an operator-reviewed migration or import.
2. Configure the protected `apm-sync` environment with a `main`-only deployment policy, the separate secrets, and workspace variables.
3. Validate Terraform and `repo-fleet`; confirm the plan has no creation, deletion, replacement, import, or move actions.
4. Merge the central workflow and fleet implementation to DevHub `main`.
5. Dispatch the workflow deliberately and review the combined per-repository pull requests. Live state setup and initial adoption are never automated.

---

## Validation

[`repo-tools.yml`](../../.github/workflows/repo-tools.yml) runs the same checks on pull requests and pushes to `main` that touch these tools.

```bash
cd tools/repo/terraform
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
terraform test           # mock provider; no credentials or network calls to GitHub

cd ../fleet
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest            # unit, git integration against local bare repositories, and contract tests
uv run repo-fleet check
```

The contract tests check the real inventory and templates, ensure the common profile no longer deploys a reusable-workflow caller, and verify that the APM workflow is central and restricted to relevant pushes on `main` plus manual dispatch.

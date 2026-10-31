# GitHub Repository Management

The authoritative design and operating guide for my repository inventory and GitHub policy. Terraform manages repository existence, declared visibility, and rules. It does not create, copy, or synchronize project files.

## Table of Contents

- [Scope and design](#scope-and-design)
  - [Why automate](#why-automate)
  - [Design options](#design-options)
  - [Why Terraform](#why-terraform)
  - [Inventory and common profile](#inventory-and-common-profile)
  - [Protection and solo reviews](#protection-and-solo-reviews)
  - [What is not automated and why](#what-is-not-automated-and-why)
- [GitHub App authentication](#github-app-authentication)
- [State management](#state-management)
- [Adopt existing repositories](#adopt-existing-repositories)
- [Add and roll out a repository](#add-and-roll-out-a-repository)
- [Change policy or retire management](#change-policy-or-retire-management)
- [Validation](#validation)

---

## Scope and design

```text
inventory.tf: explicit repositories + common profile
                            |
main.tf: repository resources + main-branch rulesets
                            |
                Terraform plan -> reviewed apply
```

### Why automate

My repositories are a team with one maintainer. An explicit inventory and common policy keep settings consistent without repeating UI steps or remembering every convention. Git records decisions; Terraform plans expose drift and the impact of a policy change before applying it.

### Design options

| Option | Decision |
|---|---|
| Manual GitHub UI or individual `gh` commands | Good for exceptional operations, but does not maintain inventory and rules as reviewable desired state |
| Python or Go repository factory/controller | Requires custom validation, API behavior, reconciliation, error handling, and tests; changing language does not remove that maintenance |
| Python/Go for creation and templates, Terraform for rules | Two ownership models and an onboarding handoff without enough benefit for this small inventory |
| Terraform plus native GitHub templates or a scaffolder | Useful if scaffolding becomes frequent, but unnecessary for the few initial files currently needed |
| Terraform only | Chosen: the provider already handles repository creation, imports, settings, rules, and stateful plans |

There is no custom Python or Go command, generator, service, workflow engine, or parallel YAML inventory. This is one directly operated Terraform root, not a reusable module. See the [Terraform GitHub provider](https://registry.terraform.io/providers/integrations/github/6.13.0/docs) for supported resources.

### Why Terraform

The goal is consistent repository settings with minimal custom code and maintenance, not a repository factory. [Terraform](https://developer.hashicorp.com/terraform/docs) and the GitHub provider supply state tracking, imports, dependency ordering, and reviewable plans. A Python or Go implementation would require writing and maintaining API calls, authentication, drift comparisons, update logic, error handling, and tests for those same responsibilities.

Keeping one declarative configuration avoids that custom maintenance and an extra orchestration layer. The trade-off is maintaining Terraform state and reviewing provider upgrades; for this small inventory, that is simpler than owning a custom reconciliation tool. Terraform runs on demand, so drift is checked during a plan, not continuously.

### Inventory and common profile

[inventory.tf](inventory.tf) contains the explicit list of repositories and their visibility. It includes public repositories and the private homelab repository; visibility is declared policy, not inferred from names. Existing archived repositories remain archived rather than being silently reactivated. Nothing is discovered from local checkouts or automatically enrolled from the account.

The `profiles` map in [inventory.tf](inventory.tf) contains just `common`. All active repositories use it. It is an internal map so a genuinely different policy can be added later without introducing a reusable-module interface now. Do not add language-specific profiles when their policy is identical.

| File | Owns |
|---|---|
| [main.tf](main.tf) | Repository resources, private-adoption access guard, default-branch check, and main-branch rulesets |
| [inventory.tf](inventory.tf) | Repository names, visibility, archived status, and common policy |
| [versions.tf](versions.tf) | Terraform/provider versions, GitHub App provider configuration, and credential variables |
| [.terraform.lock.hcl](.terraform.lock.hcl) | Provider selection and package checksums; committed to Git |

### Protection and solo reviews

The common policy is:

- Squash merging enabled; merge commits and rebase merging disabled.
- `main` requires a pull request and one approving review.
- Main-branch deletion and force pushes are blocked.
- Repository destruction through Terraform is blocked by `prevent_destroy`.

**GitHub does not let a pull-request author approve their own PR.** There is no Terraform setting that changes this. To retain the one-approval rule without locking the sole developer out, repository administrators have an explicit [pull-request-only bypass](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository#granting-bypass-permissions-for-your-branch-or-tag-ruleset) of the review ruleset. Open the PR, inspect its diff, and deliberately use the merge bypass for your own work. This is an auditable merge exception, not an approving review, and cannot technically prove that you inspected the code. A second person is required for a real approval.

The bypass is role-based: it applies to repository administrators, not uniquely to one username. It does not grant direct pushes, and branch deletion/force-push protection remains separate from the bypassable review rule. Revisit this choice if other administrators are added. To enforce one independent approval without exceptions, remove the bypass and accept that another reviewer is required.

`prevent_destroy` protects against a Terraform deletion/replacement plan while its resource block remains in configuration. It is **not GitHub-side deletion protection**: removing the entire resource block removes that guard, and it cannot prevent deletion through GitHub's UI/API. No claim is made that an administrator is unable to delete a repository.

Archived repositories are retained in the existence inventory but do not receive mutable common policy while archived. Their resource uses `ignore_changes = all`: imported settings, including visibility, are read-only, not reconciled while archived. Import and preserve them. Changing `archived` moves the repository between resource categories; it is not an ordinary settings toggle. Back up state, deliberately resolve the old ruleset state, and migrate the repository address before any archive/unarchive rollout; do not remove destruction guards to force that transition.

Rules target exactly `refs/heads/main`, not an arbitrary default branch. Active repositories must already use `main` as their default; a postcondition rejects another branch. For new repositories, set the account's [default branch name](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-the-default-branch-name-for-your-repositories) to `main` first. GitHub's minimal `auto_init` creates the initial commit/README so the branch exists before rules are applied; no profile files or subsequent content are managed. This does not rename existing branches. A failed initialization/postcondition can leave a newly created repository requiring manual correction before retry.

Rulesets on public repositories are available with GitHub Free; private repositories require an eligible plan such as GitHub Pro for this personal account. Confirm current [ruleset availability](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) before rollout. Other existing rulesets and classic protections still apply; this configuration does not silently remove or bypass them.

### What is not automated and why

Not everything is automated, some tasks are intentionally left for manual handling because they either require human judgment, are infrequent or not valuable enough to not justify automation, or involve repository-specific decisions that cannot be generalized.

- **Repository templates and initial project files:** APM manifests such as `apm.yml`, workflows, README files, and other starter content are copied manually when needed. For a few repositories, a generator and its configuration, tests, and exceptions cost more to maintain than occasional copy/paste. GitHub's minimal initial README from `auto_init` is only used to establish a branch, not to scaffold a project.
- **Ongoing file synchronization:** this root does not update files across repositories or open synchronization PRs. That would require conflict handling, versioning, and decisions about local modifications. Each repository owns its content; reference the [common APM package](../../packages/apm/common/README.md) and shared workflows where appropriate rather than building another distribution mechanism.
- **End-to-end onboarding:** setting up the GitHub App, importing existing repositories, reviewing plans, copying project files, and preparing an existing default branch remain deliberate operator steps. Terraform owns repository existence and the declared policy, not the whole development workflow. See [adoption](#adopt-existing-repositories) and [repository rollout](#add-and-roll-out-a-repository).
- **Unrelated GitHub configuration:** settings outside the declared policy, such as topics, descriptions, Pages, and project-specific features, are not reconciled. The exclusions in [main.tf](main.tf) preserve those choices instead of taking ownership of every available setting.

Reconsider scaffolding only if repeated manual work becomes a measurable burden. A native GitHub template would be the first option for initial files; continuous synchronization is a separate requirement, not a reason to introduce Python or Go now.

---

## GitHub App authentication

Use an App installation for a dedicated automation identity rather than tying repository management to a personal access token. GitHub Apps provide explicit repository access, fine-grained permissions, and short-lived installation tokens; the installation can be revoked independently of personal account access. The provider handles JWT and installation-token generation, so no custom authentication code is needed. See GitHub's [reasons to use a GitHub App](https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/deciding-when-to-build-a-github-app).

Follow GitHub's [App registration guide](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app):

1. Open personal **Settings -> Developer settings -> GitHub Apps -> New GitHub App**.
2. Choose a unique name, such as `collin-devhub-repo-manager`, and use the DevHub repository URL as its homepage.
3. Disable Webhook **Active**. Leave callback URL, OAuth user authorization, device flow, and event subscriptions unused.
4. Grant repository **Administration: read and write** for repository/ruleset management, and **Contents: read and write** for repository initialization and [provider reads of merge settings](https://registry.terraform.io/providers/integrations/github/6.13.0/docs/resources/repository). Metadata read access is automatic. Do not grant unrelated account, Actions, or Workflows permissions: this configuration does not write workflow files.
5. Restrict installation to **Only on this account**, register the App, generate a private key, and record its App ID.
6. Install it on `CollinPoetoehena`, including the private homelab repository. **Only select repositories** limits existing-repository maintenance; add each enrolled repository to the installation. Automated creation and immediate management require an installation/token scope covering newly created repositories; **All repositories** is the broader, simpler account-wide option. Never treat missing access as permission to recreate an existing repository.
7. Record the installation ID from its installation settings URL. It differs from the App ID.

Store the PEM key outside the checkout with owner-only permissions; rotate it and never commit or log it. In Bash, supply the App and installation IDs and read the private key from protected storage:

```bash
unset GITHUB_TOKEN GH_TOKEN GITHUB_OWNER GITHUB_ORGANIZATION GITHUB_BASE_URL
read -r -p 'App ID: ' TF_VAR_github_app_id
read -r -p 'Installation ID: ' TF_VAR_github_app_installation_id
export TF_VAR_github_app_id TF_VAR_github_app_installation_id
TF_VAR_github_app_pem=$(cat "$HOME/.config/devhub/repo-manager.pem") || exit 1
export TF_VAR_github_app_pem
```

The PEM variable contains the **file contents**, not its path. Keep shell tracing disabled. [versions.tf](versions.tf) explicitly wires these three credential-only inputs into the provider's `app_auth` block; the repository inventory is not an input-variable interface. Explicit arguments avoid provider 6.x's empty-block validation dependency on already-populated authentication environment variables, so offline validation needs no real credentials. Explicit token environment variables are unset to avoid overriding App authentication. See [provider authentication and owner precedence](https://registry.terraform.io/providers/integrations/github/6.13.0/docs).

After operations, unset `TF_VAR_github_app_id`, `TF_VAR_github_app_installation_id`, and `TF_VAR_github_app_pem`. App creation/installation is an external bootstrap step, not managed by the App itself. There is no management GitHub Actions workflow in this setup.

---

## State management

[Terraform state](https://developer.hashicorp.com/terraform/language/state) maps configuration addresses to real GitHub objects and records their attributes. Import adopts an existing object into that mapping; apply records newly created objects. A normal plan refreshes managed objects and compares their current values with configuration, so out-of-band changes appear as drift.

State is required operational data, not another inventory to edit by hand:

- Configuration and the provider lockfile belong in Git.
- State, backups, saved plans, `.terraform/`, App keys, and credentials do not. State/plans can contain sensitive metadata even for public infrastructure.
- The default [local backend](https://developer.hashicorp.com/terraform/language/backend/local) stores state in this root directory. Use one working copy/state and one operator at a time; securely back it up outside Git after import/apply.
- Keep state on protected storage. Local locking coordinates processes using that file, not independent copies on multiple machines.
- Before changing machines, restore the same protected state. Do not initialize a fresh independent state against the same repositories.
- Introduce a private remote backend with shared locking and access controls before multiple operators or CI apply. Configure the chosen backend, back up state, and use `terraform init -migrate-state`; do not commit backend credentials.
- Lost state is recovered from backup or by deliberate re-import. An empty-state plan proposing creation of existing repositories must not be applied.

A saved plan is a sensitive, short-lived review artifact, not a state backup. Terraform can serialize sensitive input values, including the PEM credential, into a saved plan; `sensitive` hides display, not storage. Restrict its file permissions (for example, run operations under `umask 077`), never publish it as an artifact, and discard it after use. Apply only the reviewed plan for the current state. Terraform apply is not a transaction across repositories: partial success can occur, so inspect failures and produce a fresh plan rather than assuming rollback.

---

## Adopt existing repositories

Run commands from the DevHub root. Requirements: the declared Terraform version, registry access for initialization, an authenticated App with access to every adopted repository, and the required GitHub subscription.

```sh
terraform -chdir=tools/repo init -input=false
terraform -chdir=tools/repo fmt -check
terraform -chdir=tools/repo validate
```

Stop on a nonzero exit before continuing. Use the same state and credentials throughout adoption.

Before the first apply, import each existing inventory repository using the address for its resource category. Import only reads GitHub and writes local state; it does not apply the proposed policy. Existing rulesets also need import if they are to be adopted rather than created alongside existing policy. Inspect GitHub before deciding which is appropriate.

Resource addresses and import IDs:

| Inventory category/object | Terraform address | Import ID |
|---|---|---|
| Active repository | `github_repository.active["NAME"]` | `NAME` |
| Archived repository | `github_repository.archived["NAME"]` | `NAME` |
| Main safety ruleset | `github_repository_ruleset.main_safety["NAME"]` | `NAME:RULESET_ID` |
| PR review ruleset | `github_repository_ruleset.main_pull_request["NAME"]` | `NAME:RULESET_ID` |

For example:

```sh
terraform -chdir=tools/repo import 'github_repository.active["DevHub"]' DevHub
terraform -chdir=tools/repo import \
  'github_repository.archived["devhub-ansible-proxmox"]' devhub-ansible-proxmox
terraform -chdir=tools/repo state list
```

Repeat the repository import for every existing inventory entry, using its `archived` value to choose the address. The initial inventory has nine active and three archived repositories. The private-adoption data lookup deliberately fails if the App cannot access `devhub-homelab-private`; restore access rather than attempting to create it. Its existence is an adoption requirement.

Rulesets are named `main-safety` and `main-pull-request`. If these already exist, look up their IDs in GitHub and import using the table above. Otherwise their creation is expected in the first policy plan. Other rules with overlapping conditions can impose additional restrictions; inspect them rather than assuming this policy replaces them.

Do not continue if a repository is inaccessible or its visibility/archive status differs unexpectedly. Fix access or review the inventory, not a creation plan. After imports, compare `terraform state list` with the full inventory and back up state securely.

---

## Add and roll out a repository

This section owns the operational steps; the [ecosystem creation how-to](../../docs/how-to/CREATE-REPOSITORY.md) references it rather than repeating commands.

1. Add the exact repository name and explicit visibility to `local.repositories` in [inventory.tf](inventory.tf), selecting `common`. A new active entry has this shape:

   ```hcl
   devhub-example = {
     profile    = "common"
     visibility = "private"
     archived   = false
   }
   ```

   Replace the example name and choose visibility deliberately. Do not add a new profile for a language. Set the account's default branch for new repositories to `main` before creation.
2. If the repository already exists, grant App access and import it as described above. If it is intentionally new, Terraform creates it; no manual creation or Python command is required.
3. Validate, then save and inspect the plan:

   ```sh
   terraform -chdir=tools/repo fmt -check &&
   terraform -chdir=tools/repo validate &&
   terraform -chdir=tools/repo plan -input=false -out=policy.tfplan &&
   terraform -chdir=tools/repo show policy.tfplan
   ```

4. Check the owner, visibility, archive status, squash-only settings, main rules, approval count, and administrator bypass. Existing repositories must not be unexpectedly created, replaced, deleted, renamed, made public, or unarchived. New repositories should be created only for explicitly intended inventory additions. Rule creation is expected where no matching rule was imported.
5. Apply only the reviewed plan:

   ```sh
   terraform -chdir=tools/repo apply policy.tfplan &&
   terraform -chdir=tools/repo plan -input=false -detailed-exitcode
   ```

   The follow-up plan should exit `0` (no differences); `2` means differences remain and `1` means failure.
6. Verify the repository's settings in GitHub, back up state securely, and remove the saved plan. Copy initial project files manually and follow the common profile's PR workflow for subsequent changes.

Never use `-auto-approve`, `-target`, `-refresh=false`, or `-lock=false` as shortcuts around full-plan review.

---

## Change policy or retire management

- **Shared policy:** edit `local.profiles.common` in [inventory.tf](inventory.tf), then inspect every affected repository before applying. Repository merge options and the PR ruleset derive their allowed merge methods from the same profile.
- **Another profile later:** add a policy entry and explicitly assign only the intended repositories. Keep the current single profile until a real exception requires it.
- **Visibility:** inventory is authoritative for active repositories; archived metadata remains read-only. A change to `public` can disclose project contents; review explicitly. Git history/state are not permission controls.
- **Stop managing:** back up state; remove the repository and its managed rules from state using `terraform state rm`, and remove its inventory entry before any further plan/apply. Removing only inventory triggers destruction protection; weakening it is not the retirement workflow. GitHub objects remain in place.
- **Intentional deletion:** this is not a routine operation. Review and authorize it separately; do not casually remove lifecycle safeguards.
- **Rollback:** revert the intended policy and review/apply a fresh plan. Reverting a Git commit alone does not undo GitHub changes.

---

## Validation

From the DevHub root:

```sh
mkdir -p test-results
terraform -chdir=tools/repo fmt -check > test-results/terraform-fmt.log 2>&1 &&
terraform -chdir=tools/repo init -backend=false -input=false \
  > test-results/terraform-init.log 2>&1 &&
terraform -chdir=tools/repo validate > test-results/terraform-validate.log 2>&1
git diff --check
```

Check each exit status. These checks do not contact GitHub; initialization downloads the provider unless cached. Inspect resolved inventory/policy offline with `terraform console`. No permanent test harness is maintained for this root. Offline checks cannot establish App permissions, GitHub plan entitlement, actual rule enforcement, or access to the private repository. Those require a separately reviewed authenticated plan and authorized rollout.

Provider upgrades are deliberate: review release notes and schema, update the exact version, run `terraform init -upgrade`, commit the lockfile, and rerun checks. In particular, recheck ignored optional repository fields so upgrades cannot silently take ownership of unrelated settings.

Provider 6.13.0 emits deprecation warnings for preserving `has_downloads` in `ignore_changes` and reading the computed `default_branch` in the main-branch postcondition. The latter is not a deprecated default-branch configuration argument; it is a fail-fast check. Review both when upgrading the provider.

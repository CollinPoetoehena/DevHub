# APM Sync

[`apm-sync.yml`](../../../.github/workflows/apm-sync.yml) keeps a repository's [APM](https://microsoft.github.io/apm/) packages current. It checks cheaply whether anything is outdated, refreshes the packages only when needed, and opens or updates a single pull request only when files actually change. The manual commands remain in [updating APM packages](../../../packages/apm/README.md#updating-apm-packages-and-the-cli).

## Table of Contents

- [Usage](#usage)
- [Interface](#interface)
- [Behavior](#behavior)
- [Pull requests and tokens](#pull-requests-and-tokens)
- [Limitations](#limitations)

---

## Usage

Repositories call the workflow through the caller [`devhub-apm-sync.yml`](../../../tools/repo/templates/common/sync/.github/workflows/devhub-apm-sync.yml), the source of truth that the [repository fleet tool](../../../tools/repo/README.md#templates) deploys to every active repository, including DevHub:

```yaml
on:
  push:
    branches: [main]
  schedule:
    - cron: "0 6 * * 1"
  workflow_dispatch:

permissions: {}

jobs:
  apm-sync:
    permissions:
      contents: write
      pull-requests: write
    uses: CollinPoetoehena/DevHub/.github/workflows/apm-sync.yml@main
```

| Trigger | Why |
|---|---|
| Push to `main` | Detects changes to `apm.yml` or, in DevHub, to the local packages right after they merge |
| Weekly schedule (Monday 06:00 UTC) | Picks up new upstream commits when the repository itself is quiet |
| `workflow_dispatch` | Manual run, for example after a DevHub package release |

The push trigger has no `paths` filter: DevHub must react to package source changes, other repositories to manifest changes, and the template must stay identical everywhere. The [version check](#behavior) keeps unfiltered runs cheap. The caller references `@main` on purpose so fixes reach every repository without a template change; a broken workflow on `main` therefore affects all callers until it is reverted. GitHub disables scheduled workflows in public repositories after 60 days without activity.

---

## Interface

| Input | Default | Description |
|---|---|---|
| `apm-version` | `0.35.0` | APM CLI version; pinned because the check parses `apm outdated` output |
| `branch` | `devhub/apm-sync` | Fixed branch that carries the single update pull request |

| Secret | Required | Description |
|---|---|---|
| `token` | No | Token used to push the branch and open the pull request; see [tokens](#pull-requests-and-tokens) |

| Output | Description |
|---|---|
| `outdated` | `true` when the check found something to update |
| `pull-request-operation` | `created`, `updated`, `closed`, or `none`; empty when no sync ran |
| `pull-request-url` | URL of the update pull request, when one exists |

Permissions: the caller sets `permissions: {}` at the top level and grants the job `contents: write` and `pull-requests: write`, the maximum a called job can use. Inside, the `check` job uses only `contents: read`; the `sync` job uses both write permissions.

---

## Behavior

```text
check (read-only, ~1 min)                     sync (write, only when outdated)
  apm outdated + lock/manifest checks  --->     apm update --yes; apm install
  outdated=false: summary "up to date"          create-pull-request on fixed branch
                  sync skipped                    files changed  -> create or update PR
                                                  no file change -> no PR, "No changes, no update."
```

The `check` job sets `outdated=true` on the first matching rule:

1. `apm.lock.yaml` is missing.
2. The lockfile contains a local path dependency (`source: local`), such as DevHub's `./packages/apm/common`. Local sources have no commit to compare, so they are always redeployed.
3. `apm install --frozen --dry-run` fails: `apm.yml` and the lockfile disagree, for example after adding a dependency.
4. `apm outdated` fails; the update runs to be safe.
5. `apm outdated` reports outdated dependencies: a locked commit is behind the latest commit of its branch, tag, or the default branch for unpinned references.

Otherwise the job summary reports "APM packages are up to date: no changes, no update." and `sync` is skipped. Dependencies pinned to a full commit SHA can never be outdated; change the pin in `apm.yml` to update them. `apm outdated` reports `unknown` for references it cannot check, and those do not trigger an update. See the [`apm outdated`](https://microsoft.github.io/apm/reference/cli/outdated/) and [`apm update`](https://microsoft.github.io/apm/reference/cli/update/) references.

The `sync` job runs [`microsoft/apm-action`](https://github.com/microsoft/apm-action) in update mode, then `apm install` to redeploy local path dependencies, which `apm update` skips. Runs are serialized per repository.

---

## Pull requests and tokens

[`peter-evans/create-pull-request`](https://github.com/peter-evans/create-pull-request) commits only when the working tree changed. All runs use the same branch, so a later run updates the existing pull request instead of opening another; when the changes disappear, the pull request is closed and the branch deleted. The job summary reports the result. Merging the update pull request triggers a push run that then finds nothing to do.

By default the pull request is created with `GITHUB_TOKEN`. This requires the repository setting that allows Actions to create pull requests, which [Terraform manages](../../../tools/repo/README.md#profiles). Pull requests created with `GITHUB_TOKEN` do not [trigger other workflows](https://docs.github.com/en/actions/concepts/security/github_token#when-github_token-triggers-workflow-runs), so pull request checks do not run on them. To get checks, pass a `token` secret, such as a GitHub App installation token or a fine-grained personal access token with `contents: write` and `pull-requests: write` on the repository:

```yaml
    uses: CollinPoetoehena/DevHub/.github/workflows/apm-sync.yml@main
    secrets:
      token: ${{ secrets.APM_SYNC_TOKEN }}
```

---

## Limitations

- DevHub always runs `sync` because of its local dependency; without file changes it ends with no pull request.
- The check parses the `apm outdated` summary text, so APM CLI upgrades go through the `apm-version` input after verifying the output format.
- Remote dependencies pinned to a feature branch, such as DevHub's own `#manage-repos-automatically` references, stop resolving once that branch is deleted; point them back to the default branch first.

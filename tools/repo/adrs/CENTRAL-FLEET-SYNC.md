# ADR: Centralize Repository Fleet Synchronization in DevHub

## Context

Repository settings and shared files are managed across multiple GitHub repositories, but the policy, templates, and inventory are maintained in DevHub. The current [central workflow](../../../docs/github-actions/workflows/apm-sync.md) runs from DevHub's `main` branch, validates the complete active inventory, checks Terraform state and a saved settings plan, prepares content changes, and opens combined pull requests in affected repositories. It does not push shared content to consumer default branches.

The decision drivers are one version of fleet policy, reviewable consumer changes, bounded credentials, no unreviewed settings creation or deletion, and failure before any writes when preflight detects drift or an unsafe plan. Initial workspace creation and resource adoption remain operator-controlled rather than automated.

---

## Decision

Use one protected DevHub workflow as the fleet writer. Trigger it for relevant changes on `main` or deliberate manual dispatch, serialize fleet runs, validate the entire inventory, verify adopted Terraform state, and restrict settings changes to an explicitly allowed saved plan. Prepare shared content for all active repositories before settings apply; after successful apply, deliver changes as one combined pull request per changed repository. Never write managed shared content to consumer default branches.

Use separate credentials for Terraform settings and repository content operations, restrict environment deployment to `main`, and keep consumer review and merge as the boundary for shared file changes. Treat initial resource creation, imports, visibility/archive changes, and state adoption as separately reviewed operator actions.

This is a preflight-and-delivery workflow, not a fleet-wide transaction. A successful settings apply cannot be rolled back by closing content pull requests; failures after apply require inspection of authoritative state and a separately reviewed recovery.

---

## Consequences

### Positive

- **Consistent policy**: A central workflow evaluates one inventory and one trusted DevHub revision instead of relying on each consumer to host a synchronized writer.
- **Reviewable content**: Consumers receive pull requests and retain control of merging shared files into their default branches.
- **Bounded settings changes**: State checks and saved-plan validation reject creates, deletes, replacements, imports, unexpected resources, and disallowed settings changes before apply.
- **Reduced credential sprawl**: Consumer repositories do not each need a copy of the writer workflow and its fleet credentials.

### Negative

- **Central failure domain**: A workflow, token, or HCP workspace outage can pause updates across the managed fleet.
- **Setup burden**: The protected Actions environment, distinct tokens, HCP workspace, exact adopted state, and local-execution configuration require careful operator setup.
- **No atomic fleet transaction**: Terraform settings and per-repository pull requests cannot be committed as one operation; partial delivery after settings apply requires explicit diagnosis and rerun or recovery.
- **Central maintenance**: Changes to inventory shape, security gates, or delivery behavior must be validated in DevHub before affecting repositories.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| **Central DevHub push workflow**, a project-defined approach documented in the [fleet workflow guide](../../../docs/github-actions/workflows/apm-sync.md), using [GitHub Actions workflow triggers and environments](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions) and the [GitHub CLI pull-request command](https://cli.github.com/manual/gh_pr_create). | One trusted policy version can preflight the inventory and state before making changes; consumer files remain reviewable as pull requests; credentials can be separated by operation. | Requires protected environment and state setup, and GitHub does not provide an atomic transaction spanning settings and all consumer repositories. | Selected because it matches the central ownership of inventory and templates while preserving per-repository review and strict settings gates. | Reconsider if DevHub no longer owns fleet policy or if an alternative can preserve the same preflight, credential, and review boundaries with less central operational risk. |
| **Consumer pull workflows**, a project-defined approach using per-repository [GitHub Actions workflows](https://docs.github.com/en/actions/writing-workflows/about-workflows) that periodically or manually fetch DevHub policy. | Consumers can control their own update timing and may continue operating when the central workflow is unavailable. | Each repository needs a writer workflow and credentials; policy versions can diverge, and consumers would need access to or copies of inventory and update logic. Coordinating Terraform settings remains separate. | Repeating the writer and credentials in every consumer weakens the central ownership boundary and makes fleet-wide preflight more difficult. | Reconsider if consumers acquire separate owners, access requirements, or independent update schedules that justify distinct writers. |
| **Manual-only operations**, a project-defined approach using the [Terraform CLI](https://developer.hashicorp.com/terraform/cli) and `repo-fleet` commands documented in the [operating guide](../README.md). | Keeps every operation explicitly operator initiated and avoids an always-available automation workflow. The project already requires manual review for bootstrap and adoption. | Repeating fleet validation and preparation by hand is more error-prone; there is no single automated gate ensuring all active repositories are prepared before settings apply. | Manual-only operation is retained for bootstrap and exceptional changes, but does not provide a repeatable recurring sync for the managed fleet. | Reconsider if the fleet becomes small or infrequently changed enough that a central automated workflow no longer reduces operational risk. |

---

## Status

Proposed. The current implementation follows this workflow; separate approval of this ADR has not been recorded.

---

## Date

2026-11-13

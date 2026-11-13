# ADR: Separate Repository Settings from Shared Content Delivery

## Context

Repository fleet management has two different kinds of work. Repository existence, visibility, merge settings, rulesets, and Actions permissions are long-lived platform resources. Shared template files need rendering, comparison with repository contents, and delivery for review. The current [Terraform configuration](../terraform/) manages the platform resources; Python `repo-fleet` handles template and APM content using Git and GitHub CLI operations.

The decision drivers are reviewable settings changes, safe state and drift management, content changes proposed through pull requests, and avoiding a second implementation of Terraform's resource lifecycle.

---

## Decision

Use Terraform with the GitHub provider for repository resources and settings. Use Python `repo-fleet` for shared repository content, rendering templates and opening pull requests. Keep each tool within its natural ownership boundary: `repo-fleet` must not become a second settings manager, and Terraform must not be used as a content deployment mechanism.

This boundary does not eliminate coordination between the tools. Both consume the shared [repository inventory](SHARED-INVENTORY.md), and the [central sync workflow](CENTRAL-FLEET-SYNC.md) coordinates their guarded operation.

---

## Consequences

### Positive

- **Native settings lifecycle**: Terraform provides state, import, drift detection, and reviewable plans for long-lived repository resources.
- **Reviewable content delivery**: `repo-fleet` can render files, compare them with consumer repositories, and propose changes in pull requests rather than writing shared content directly to default branches.
- **Clear ownership**: Settings and file content have distinct owners, making it easier to reason about which tool is allowed to change each kind of repository state.

### Negative

- **Two toolchains**: Operators and CI must validate and configure Terraform and Python separately.
- **Coordination required**: A shared inventory and central workflow must keep resource identities and content operations aligned.
- **Boundary discipline**: New capabilities must be assigned deliberately; placing settings in `repo-fleet` or content in Terraform would duplicate or bypass the intended lifecycle.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [Terraform GitHub provider](https://registry.terraform.io/providers/integrations/github/6.13.0/docs): manage repository resources and settings using state and plans. Pair it with [GitHub CLI](https://cli.github.com/manual/) and the project-defined Python [`repo-fleet`](../README.md#fleet-operations) for shared file delivery. | Uses Terraform's resource lifecycle where it fits, while allowing content changes to be reviewed as ordinary repository pull requests. The existing provider and `repo-fleet` code directly implement these separate responsibilities. | Requires two languages, validation paths, and an integration contract; neither tool alone coordinates a whole fleet run. | Selected because platform settings and Git-versioned files have different review and lifecycle needs. The shared inventory and central workflow provide the coordination point without combining ownership. | Reconsider if the provider gains a content workflow that preserves pull-request review, or if maintaining the split becomes a demonstrated operational burden. |
| [Terraform `github_repository_file`](https://registry.terraform.io/providers/integrations/github/6.13.0/docs/resources/repository_file): have Terraform manage shared file contents alongside repository settings. | One state and plan could show settings and file changes together; Terraform already has the inventory and credentials for repository resources. | File contents become Terraform-managed state, and the resource's commit operation is not the project's pull-request-based review flow. Content templating and per-repository PR delivery would still need an adapter. | It couples ordinary file changes to the platform-resource lifecycle and does not provide the required review boundary for consumer content. | Reconsider if file changes can be prepared and delivered through the same review workflow without storing them in state or bypassing consumer review. |
| **Python for all fleet operations**, a project-defined approach using `repo-fleet` with [GitHub CLI](https://cli.github.com/manual/) and [Git](https://git-scm.com/docs): implement both settings and file changes in the same CLI. | One language and entry point could make day-to-day operations appear uniform and could share inventory parsing and command orchestration. | The tool would need to recreate state ownership, imports, drift detection, locking, and plan review for platform resources, increasing custom lifecycle and recovery logic. | The convenience of one CLI does not justify replacing Terraform's established resource lifecycle for settings that are already managed as infrastructure. | Reconsider if Terraform no longer meets required provider or workflow constraints and a suitable settings lifecycle exists outside a custom implementation. |

---

## Status

Proposed. The current implementation follows this split; separate approval of this ADR has not been recorded.

---

## Date

2026-11-13

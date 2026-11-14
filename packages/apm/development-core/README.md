# DevHub Local Development Core

`devhub-development-core` distributes local development agents and skills through [APM](https://microsoft.github.io/apm/). Its [`.apm/` source](.apm/) defines the roles and standalone procedures. Shared repository standards live separately in [`guidelines-core`](../guidelines-core/README.md); opt-in `development-*` packages add technology-specific guidance.

The [APM guide](../README.md) owns package selection and setup. The current workflow decisions are recorded in the [workflow ADR](../docs/adrs/workflow/AI-DEVELOPMENT-WORKFLOW.md) and [agent-and-skill ADR](../docs/adrs/workflow/WORKFLOW-AGENTS-AND-FOCUSED-SKILLS.md).

## Package contents

| Customization | Responsibility |
|---|---|
| [Planner](.apm/agents/planner.agent.md) | Separate planning phase, required for larger or consequential work and optional for small, understood edits; saves a plan and asks for approval. It does not implement. |
| [Implementation Orchestrator](.apm/agents/implementation-orchestrator.agent.md) | Single entry point for implementation requests, whether given directly or with an existing plan; selects SIMPLE or STANDARD execution. |
| [Implementer](.apm/agents/implementer.agent.md) | Implements one bounded assignment, including related tests, documentation, and validation; does not delegate or independently review. |
| [Reviewer](.apm/agents/reviewer.agent.md) | Fresh, read-only assessment of the integrated result for correctness, security, maintainability, and project conformance. |
| [Sharing Context skill](.apm/skills/sharing-context/SKILL.md) | Task-scoped context shared between fresh workers in STANDARD execution. |
| [ADR skill](.apm/skills/adr/SKILL.md) | Standalone procedure for significant architecture decisions, following project conventions. |
| [Draft GitHub Issue skill](.apm/skills/draft-github-issue/SKILL.md) | Standalone procedure for producing a reviewable issue draft; it does not publish or implement it. |
| [Commit Command skill](.apm/skills/commit-command/SKILL.md) | Analyzes all current changes and generates one copy-ready add/commit/push sequence; it never executes the commands. |

The manifest also references the upstream `create-agentsmd` and `acquire-codebase-knowledge` skills at `#HEAD`. APM resolves these against the source's default branch when resolving or refreshing dependencies; this is not a fixed commit or a live update. Existing lock files may retain resolved revisions until refreshed.

## Reuse registry

Maintain adapted content as described in [maintaining reused content](../README.md#maintaining-reused-content).

| Local skill | Source | Mode | Local changes |
|---|---|---|---|
| [commit-command](.apm/skills/commit-command/SKILL.md) | [awesome-copilot `git-commit`](https://github.com/github/awesome-copilot/blob/main/skills/git-commit/SKILL.md) | Adapted | Retains the message format, type table, and breaking-change guidance; uses a concise, command-generation-only workflow with one message for all current changes and explicit add/commit/push commands for user execution. Original import revision was not recorded. |

## Using the workflow

Keep planning and implementation separate. Larger, unclear, cross-cutting, or consequential work requires **Planner** and an approved saved plan before a fresh implementation session. Small, localized, already understood tasks may skip Plan. Select **Implementation Orchestrator** for all implementation, supplying either that small request or the approved plan's absolute path and current-version approval.

- **SIMPLE** is for obvious, localized, low-risk work. The orchestrator delegates to one fresh Implementer and runs proportional checks; it does not require an independent Reviewer.
- **STANDARD** covers other work or uncertainty. The orchestrator uses fresh, bounded exploration or research for substantial investigations, assigns dependency-aware implementation work, and parallelizes only independent tasks with isolated write ownership. It integrates and validates the result, then asks one fresh Reviewer for a read-only review of code, security, and project conventions. It sends blocking corrections to a fresh Implementer and has the Reviewer reassess the corrected result. Where the host permits, it prefers a reviewer model or provider different from implementation; otherwise it uses the available default. No model is fixed in the package.

Both modes finish with scoped documentation and ADR reconciliation, including omissions from earlier work in that scope but excluding unrelated areas. Missing or stale documentation goes to a new, fresh Implementer for a documentation-only update without separate review. The final response reports evidence and ends by invoking skill `commit-command` to generate commands for the user to execute after verification; the orchestrator does not stage, commit, or push.

STANDARD uses the standalone Sharing Context skill to give workers one task-scoped memory path and a consistent prompt contract; the orchestrator owns that shared file. The skill uses `<cwd>/tmp/MEMORY-<id>.md` by default and permits another shared, writable location if needed.

**Planner** asks questions in rounds, saves a unique `<cwd>/tmp/plan-<id>.md`, and stops for active review and approval. It never implements; hand its agreement to a fresh orchestrator session rather than continuing the planning conversation. Routine execution within that agreement stays autonomous; material scope or design changes require separate planning and renewed approval. Execution mode is distinct from planning need: a small, understood behavior change can require STANDARD validation without a full plan. The ADR and issue-drafting skills remain independent procedures, not workflow stages.

The [AI development workflow ADR](../docs/adrs/workflow/AI-DEVELOPMENT-WORKFLOW.md) owns overall workflow policy; the [agent-and-skill ADR](../docs/adrs/workflow/WORKFLOW-AGENTS-AND-FOCUSED-SKILLS.md) records current role boundaries. See [CONCEPTS.md](../docs/CONCEPTS.md) for general terminology.

## Validation

From this package directory, validate the source with:

```sh
apm compile --validate --local-only
```

In fresh sessions, check that the host offers the two entry roles and that:

- Small, understood requests can proceed directly; larger or consequential work requires a current approved plan and fresh implementation session before editing.
- SIMPLE work uses one fresh Implementer, proportional checks, and no independent review.
- STANDARD work follows bounded exploration/research, safe dependency-aware implementation, integration, and one fresh read-only Reviewer; blocking corrections are rechecked.
- Planner saves a unique plan, stops for active approval, and does not implement; material departures during execution stop for separate planning rather than silently redefining the agreement.
- STANDARD worker prompts share the task memory path and respect the single-writer contract.
- Reviewer model/provider preference falls back to the available default when the host does not support a different selection.
- Both modes reconcile scoped documentation and required ADRs, including earlier omissions; any documentation-only fixes use a fresh Implementer without separate review.
- Completion invokes skill `commit-command` by name and ends with one copy-ready command sequence for all current changes, without executing Git writes or pushing; unsafe states produce an explicit blocker instead.

Validate behavior separately in each intended host and scope. Source validation does not install or activate this package, prove host discovery or runtime behavior, synchronize local development package copies, or show that a model/provider preference was honored. See the [APM setup guidance](../README.md#repository-setup) and [ADR index](../docs/adrs/README.md).

---

The [changelog](CHANGELOG.md) is the history of package changes.

# APM Architecture Decision Records

These records capture significant decisions about DevHub's AI customization architecture and their trade-offs. Each ADR owns one specific decision; related records are grouped into topic folders and linked rather than combined into one large record. The [APM guide](../README.md) summarizes the selected design; [CONCEPTS.md](../CONCEPTS.md) owns general terminology.

The planning and implementation orchestration skill sources and the custom Implementer source exist. The package split and its distribution are transitional, and source presence does not establish runtime discovery or behavior. Synchronization is intentionally only a TODO, not an implemented or fully designed mechanism.

Follow the central [ADR guidelines](../../../docs/GUIDELINES.md#architecture-decision-records-adrs) for scope, placement, and referencing decisions.

## Distribution and synchronization

The [distribution-and-synchronization folder](distribution-and-synchronization/) separates the package manager, package boundaries, and future update automation.

| ADR | Decision |
|---|---|
| [APM distribution](distribution-and-synchronization/DISTRIBUTION.md) | Reuse APM's package-distribution lifecycle rather than build a custom resolver, installer, updater, and target mappings. |
| [Package design](distribution-and-synchronization/PACKAGE-DESIGN.md) | Keep shared standards in repository-facing `guidelines-core`; keep agents/skills in local `development-core` and stack-specific instruction maps with opt-in development stacks. |
| [Synchronization TODO](distribution-and-synchronization/SYNCHRONIZATION.md) | Explore an install script and `.bashrc` integration for local setup updates, and GitHub Actions instruction-update PRs for repositories; no implementation yet. |

---

## Workflow

The [workflow folder](workflow/) separates stage policy, the approved-plan contract, context isolation, workflow representation, model selection, and configuration.

| ADR | Decision |
|---|---|
| [AI development workflow](workflow/AI-DEVELOPMENT-WORKFLOW.md) | Use interactive Plan, autonomous Build and Test, human Verify, and final Observe, with a simple-edit exception. |
| [Approved plan and handoff](workflow/APPROVED-PLAN-AND-HANDOFF.md) | Capture a durable plan, obtain approval of its exact version, and carry the agreed contract into implementation. |
| [Focused sessions and specialist context](workflow/FOCUSED-SESSIONS-AND-SPECIALIST-CONTEXT.md) | Use phase-focused sessions and bounded specialist contexts when justified, carrying forward essential decisions and evidence. |
| [Reusable workflows as skills](workflow/REUSABLE-WORKFLOWS-AS-SKILLS.md) | The native agent runs planning and implementation procedures as skills; retain one focused custom Implementer. |
| [Model selection](workflow/MODEL-SELECTION.md) | Let the harness choose models for each task, with Copilot Fusion Standard as the default user-selected tier. |
| [Minimal agent configuration](workflow/MINIMAL-AGENT-CONFIGURATION.md) | Omit optional host-specific metadata by default; define role contracts while enforcing mandatory controls through the host. |

---

## AI customizations

The [AI-customizations folder](ai-customizations/) separates purpose/detail, reuse policy, and guidance ownership.

| ADR | Decision |
|---|---|
| [Customization purpose and detail](ai-customizations/AI-CUSTOMIZATION-CREATION.md) | Capture demonstrated context gaps with thin guidance that retains model reasoning and creativity. |
| [Reuse and tailoring](ai-customizations/REUSE-AND-TAILORING.md) | Prefer native capability and selective reuse, using 90/10 and 80/20 heuristics rather than quotas. |
| [Guidance layering](ai-customizations/GUIDANCE-INSTRUCTION-LAYERING.md) | Use root `AGENTS.md` for repository context and scoped shared instructions for standards, without duplicating procedures or role policy. |
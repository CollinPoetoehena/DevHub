# APM Architecture Decision Records

These records capture significant decisions about DevHub's AI customization architecture and their trade-offs. Each ADR owns one specific decision; related records are grouped into topic folders and linked rather than combined into one large record. The [APM guide](../../README.md) summarizes the selected design; [CONCEPTS.md](../CONCEPTS.md) owns general terminology.

The eight source packages implement the shared-guidelines and local-development split. Central repository-fleet delivery of APM and template changes through pull requests exists, but its current package contract does not cover the new eight-package split or `#HEAD` dependencies. Local development-scope installation, updates, and host discovery remain deferred. See the [synchronization record](distribution-and-synchronization/SYNCHRONIZATION.md) for the implemented boundary and remaining work.

Follow the central [ADR guidelines](../../../../docs/GUIDELINES.md#architecture-decision-records-adrs) for scope, placement, and referencing decisions.

## Distribution and synchronization

The [distribution-and-synchronization folder](distribution-and-synchronization/) separates the package manager, package boundaries, existing central repository delivery, and deferred local setup updates.

| ADR | Decision |
|---|---|
| [APM distribution](distribution-and-synchronization/DISTRIBUTION.md) | Reuse APM's package-distribution lifecycle rather than build a custom resolver, installer, updater, and target mappings. |
| [Package design](distribution-and-synchronization/PACKAGE-DESIGN.md) | Keep shared standards in repository-facing `guidelines-core`; keep agents/skills in local `development-core` and stack-specific instruction maps with opt-in development stacks. |
| [Synchronization status](distribution-and-synchronization/SYNCHRONIZATION.md) | Central repository-fleet APM/template PR delivery exists under a narrower manifest contract; local development-scope installation, updates, and discovery remain deferred. |

---

## Workflow

The [workflow folder](workflow/) records separate planning and implementation phases, the autonomous execution contract, role and skill structure, context isolation, model policy, and configuration. Obsolete records remain in Git history rather than as superseded ADR files.

| ADR | Decision |
|---|---|
| [Workflow agents and focused skills](workflow/WORKFLOW-AGENTS-AND-FOCUSED-SKILLS.md) | Use Planner and Implementation Orchestrator roles with Implementer and one Reviewer; skills provide focused standalone procedures. |
| [AI development workflow](workflow/AI-DEVELOPMENT-WORKFLOW.md) | Plan larger work interactively, approve the saved agreement, then hand off to fresh Orchestrator execution; small, understood tasks may skip Plan. Owns the integrated plan/handoff contract and SIMPLE/STANDARD modes. |
| [Focused sessions and specialist context](workflow/FOCUSED-SESSIONS-AND-SPECIALIST-CONTEXT.md) | Use fresh bounded workers and a fresh Reviewer when warranted, carrying task evidence through the `sharing-context` procedure. |
| [Model selection](workflow/MODEL-SELECTION.md) | Omit fixed model assignments; use host/user selection and prefer reviewer diversity only when available and permitted. |
| [Minimal agent configuration](workflow/MINIMAL-AGENT-CONFIGURATION.md) | Record current broad tool and delegation metadata accurately; host permissions, not prose, enforce controls. |

---

## AI customizations

The [AI-customizations folder](ai-customizations/) separates purpose/detail, reuse policy, and guidance ownership.

| ADR | Decision |
|---|---|
| [Customization purpose and detail](ai-customizations/AI-CUSTOMIZATION-CREATION.md) | Capture demonstrated context gaps with thin role contracts and focused procedures while retaining model reasoning. |
| [Reuse and tailoring](ai-customizations/REUSE-AND-TAILORING.md) | Prefer native capability and selective reuse, using role wrappers where they improve entry-point discovery and context ownership. |
| [Guidance layering](ai-customizations/GUIDANCE-INSTRUCTION-LAYERING.md) | Use root `AGENTS.md` for repository context and scoped shared instructions for standards, without duplicating procedures or role policy. |
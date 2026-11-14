# ADR: Use Role-Level Workflow Agents with Focused Skills

## Context

The development workflow needs recognizable roles for Planning and Implementation Orchestration, while reusable procedures should remain composable and independent of those roles. Skills and custom agents solve related but different problems: skills package capabilities and instructions; custom agents provide a selectable role contract and can define tools and delegation availability. A skill can be discovered or activated automatically where a host supports it, so this decision does not assume skills require explicit slash-command invocation.

The current `development-core` source contains four custom agents: [Planner](../../../development-core/.apm/agents/planner.agent.md), [Implementation Orchestrator](../../../development-core/.apm/agents/implementation-orchestrator.agent.md), [Implementer](../../../development-core/.apm/agents/implementer.agent.md), and [Reviewer](../../../development-core/.apm/agents/reviewer.agent.md). Planner and Orchestrator have `tools: ['*']`; Planner has `agents: ['*']`, while Orchestrator has `agents: ['*', 'Implementer', 'Reviewer']`. Implementer and Reviewer are marked `user-invocable: false`; Planner and Orchestrator remain user-invocable by default. No role pins a model. These fields describe package configuration, not host-enforced permissions.

The current local skill sources are `sharing-context`, `adr`, `draft-github-issue`, and `commit-command`; stack packages contribute their own task-focused skills. The [development-core manifest](../../../development-core/apm.yml) declares upstream `create-agentsmd` and `acquire-codebase-knowledge` skills. The local `commit-command` adaptation generates commands for user execution instead of executing commits itself. The previous planning and implementation-orchestration skill files are not present in the current package source. Package manifests and source files do not prove installation, discovery, or host behavior.

The [AI development workflow ADR](AI-DEVELOPMENT-WORKFLOW.md) owns the current SIMPLE/STANDARD execution contract. For terminology and the relationship between orchestration patterns, see [AI Customization Concepts: Orchestration](../../CONCEPTS.md#orchestration). The decision drivers here are easy-to-select entry roles, focused role boundaries, reusable skill procedures, limited duplication, portable capability packaging where supported, and context-aware implementation and review.

The package targets Copilot, but agent metadata is host-sensitive: the current [VS Code custom-agent reference](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference#_harness-compatibility) says `agents` is not supported by the Copilot harness. Therefore the source Orchestrator's `agents` list is not evidence that its workers are visible in every target host. Verify delegation in the intended environment; unavailable required delegation is a blocker, not permission to claim the worker ran.

---

## Decision

Use thin Planner and Implementation Orchestrator agents as role-level entry points. Keep the Implementer as the bounded implementation worker and use one Reviewer for independent assessment. Place reusable, standalone procedures in focused skills; agents may invoke or compose those procedures when relevant rather than embedding all procedure details in every role.

Role wrappers connect their responsibility to focused skills and host capabilities. In this setup, role selection makes it easier to find and choose Planning or Implementation Orchestration than selecting a low-level procedure that does not represent the user's intended role. Skill metadata still supports host discovery and automatic use; this is a preference for a clear role-level route, not a claim that skills are only manually invoked.

Keep planning and implementation as separate phases. Planner investigates and asks consequential questions in rounds, saves a unique plan under the invocation working directory's `tmp/`, and asks the user to approve that plan. Larger, unclear, cross-cutting, or consequential work requires this phase before a fresh Implementation Orchestrator session receives the approved artifact. Small, already understood tasks may go directly to the orchestrator. The [workflow ADR](AI-DEVELOPMENT-WORKFLOW.md) owns the planning threshold and handoff; the orchestrator executes rather than invoking Planner or combining both phases.

Keep shared engineering standards in instructions and repository guidance, not duplicated in role prompts. Use `sharing-context` to maintain task-scoped context for isolated workers, with the coordinator as the sole writer; workers read the shared memory and return findings. Use `adr` or another focused skill when its procedure is relevant. Skills can compose, but their use does not replace role contracts, independent review, host permission checks, or integration evidence.

This design uses documented [custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents), [Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills), and [subagents](https://code.visualstudio.com/docs/agents/run/subagents). Their discovery, selectable fields, skill activation, delegation, and permission behavior vary by host. Role prose and `tools: ['*']` do not establish authorization; the host and user retain control.

---

## Consequences

### Positive

- **Clear entry roles**: Users select Planner for the planning phase and Implementation Orchestrator for autonomous execution; small, already understood tasks can skip Plan without changing the implementation entry point.
- **Reusable procedures**: Focused skills such as context sharing and ADR authoring can be used independently or composed by more than one agent.
- **Bounded worker responsibilities**: Implementer and Reviewer separate edits from read-only assessment, while the Orchestrator owns assignment, integration, and completion evidence.
- **Reduced duplication**: Role definitions specify role and handoff contracts while repository instructions and skills own reusable standards and procedures.
- **Context separation**: Fresh workers and a fresh Reviewer can assess scoped tasks without inheriting the coordinator's entire conversation; shared context carries only relevant evidence.

### Negative

- **More files to maintain**: Four agent definitions plus focused skills require coherent ownership, routing, and host compatibility checks.
- **Not permission isolation**: The current agents declare broad `'*'` tools, and role prose is not enforcement; real restrictions remain host- and user-controlled.
- **Host-dependent discoverability**: Agent selection and automatic skill discovery vary by host and installation scope; source presence alone is insufficient evidence.
- **No guaranteed independence**: A fresh Reviewer or distinct role does not guarantee a different model, provider, or conclusion.
- **Coordination cost**: STANDARD work transfers context to workers and Reviewer and requires integration; `sharing-context` has a single-writer coordination obligation.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| **Skills-first workflow on the native agent**: place Planning and implementation orchestration procedures in [Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills) and let the existing host agent coordinate them. | Skills are task-oriented, progressively loaded, composable, and portable across compatible agents; the native agent avoids maintaining custom workflow personas. | The workflow and delegation contract remain attached to a general-purpose active agent rather than a recognizable role-level entry point. Skill discovery and activation still vary by host, and skills do not supply a separate agent role. | This setup prioritizes easy selection of Planning and Implementation Orchestration as named roles, while retaining skills for procedures. The current source also has actual role definitions and no planning/orchestration skill files. | A host's skill discovery and task routing make role selection equally clear, or role definitions become costly without improving findability or outcomes. |
| [Native agent with ad hoc instructions and skills](https://code.visualstudio.com/docs/agents/concepts/customization): rely on user prompts and skill descriptions without custom Planner, Orchestrator, Implementer, or Reviewer roles. | Keeps the fewest project-defined role files and maximizes use of the host's default capabilities. | Users must restate or discover the desired execution contract; consistent SIMPLE/STANDARD routing, worker ownership, and review handoff become less explicit. | Recurring role-level responsibilities merit stable selectors and contracts in this setup; a task-only skill is not a substitute for the whole role. | The host provides an equivalent persistent workflow entry point, or representative use shows no benefit from maintaining custom roles. |
| [Many narrowly specialized agents](https://code.visualstudio.com/docs/agents/run/subagents): add separate architect, researcher, tester, code reviewer, security reviewer, and language-specific implementation roles. | Can isolate substantial and recurring responsibilities and tailor context to each. | Increases role discovery, delegation routing, context transfer, and integration; specialized names do not prove capability or independence. | Four roles and focused skills cover the present needs without maintaining a permanent role for every operation or technology. | Evidence shows a stable responsibility needs distinct instructions, tools, ownership, or a separately verifiable output. |
| [One monolithic custom agent](https://code.visualstudio.com/docs/agent-customization/custom-agents): combine planning, implementation coordination, implementation, and review in one selectable persona. | Gives users one role to choose and keeps a single entry file. | Combines distinct editing and review responsibilities, complicates role boundaries, and makes a fresh independent review less natural; the body risks collecting unrelated procedures. | Separate Planner, Orchestrator, Implementer, and Reviewer roles give users and workers clearer responsibilities while focused skills remain reusable. | The role distinctions prove unnecessary in practice and a single agent can preserve fresh review and bounded ownership. |

These are project-defined workflow arrangements; references describe mechanisms, not endorsement of this role set.

---

## Status

Accepted: the user selected role-level Planner and Implementation Orchestrator agents, an Implementer and single Reviewer, and focused standalone skills for reusable procedures.

---

## Date

2026-11-14

---
# Changelog

- 2026-11-14: Clarified that planning is a separate required phase for larger or consequential work, while small, already understood tasks may proceed directly to implementation.

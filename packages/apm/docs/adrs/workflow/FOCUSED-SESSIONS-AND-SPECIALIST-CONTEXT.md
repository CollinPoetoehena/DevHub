# ADR: Focused Sessions and Specialist Context

## Context

Implementation coordination, bounded work, and independent review have different responsibilities and benefit from focused context. Long conversations can bury current requirements among earlier discussion and attempts. Separate role definitions alone do not reset accumulated context.

The [AI development workflow ADR](AI-DEVELOPMENT-WORKFLOW.md) defines the current autonomous execution contract, and [Workflow Agents and Focused Skills](WORKFLOW-AGENTS-AND-FOCUSED-SKILLS.md) records its roles. This record addresses the distinct context-separation choice: when to use fresh bounded worker contexts and how to carry relevant task information between them. Context separation is a practical organizational choice, not a guaranteed quality improvement or universal context-window threshold.

---

## Decision

Keep planning and implementation in separate sessions for larger or consequential work, as required by the [workflow ADR](AI-DEVELOPMENT-WORKFLOW.md). Begin the fresh execution session with the approved plan and relevant repository guidance, not the full exploratory transcript. Small, already understood tasks may skip the planning phase.

Use fresh, bounded subagent contexts for STANDARD assignments and independent review when supported by the host. The Orchestrator remains the single execution entry point. Each worker receives a self-contained assignment with relevant repository guidance, evidence, dependencies, ownership, and acceptance checks, then returns concise findings or validation evidence. Keep quick lookups direct and SIMPLE execution proportionate, with one Implementer rather than specialist fan-out.

Use the `sharing-context` skill to maintain one task-scoped MEMORY file for delegated work. The coordinator creates and owns the file, includes its path and read/update expectations in each worker prompt, reconciles worker updates against current source evidence, and remains the only writer unless an exclusive edit is assigned. If the preferred path is unavailable or unwritable, the skill permits a fallback to another permitted writable location accessible to all workers; it does not permit bypassing a denial. Workers report findings and updates rather than concurrently editing shared memory.

Fresh delegated contexts provide separation; merely defining separate roles does not. Carrying relevant repository guidance, decisions, dependencies, and evidence prevents isolation from dropping essential information. A fresh Reviewer context supports independent assessment but does not guarantee a different model or provider.

The practical motivation is the smart-zone heuristic: accumulated context can become difficult to use before a hard context limit is reached. This does not establish a universal threshold or promise better outcomes. The [concepts glossary](../../CONCEPTS.md#execution-and-context) explains the term and records the requested AI Coding Dictionary reference's availability caveat.

Main-agent configuration and model choices are owned separately by [minimal agent configuration](MINIMAL-AGENT-CONFIGURATION.md) and [model selection](MODEL-SELECTION.md).

---

## Consequences

### Positive

- **Focused assignments**: Fresh workers receive only the context required for their bounded tasks, keeping intermediate exploration out of the coordinator's working context.
- **Traceable handoffs**: Task-scoped memory carries verified findings, decisions, dependencies, and checks across isolated contexts.
- **Fresh review context**: The Reviewer assesses the integrated change without relying on the implementer's conversation history.
- **Separate phases**: Larger work carries an approved agreement into fresh execution context; small, understood tasks avoid unnecessary planning overhead.

### Negative

- **Handoff effort**: Relevant decisions, repository guidance, dependencies, and evidence must be explicitly carried into each delegated task.
- **Context loss risk**: An incomplete assignment or stale memory may omit nuance; workers must verify evidence against current sources.
- **Coordination cost**: Specialists use separate contexts and require clear ownership, integration, and review of returned evidence.
- **Shared-state discipline**: One writer must maintain task memory to prevent conflicting updates; fallback paths must remain permitted and accessible.
- **Host variation**: Subagent support and behavior vary by host; this decision does not assume uniform capabilities or enforceable role isolation.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [Fresh subagent contexts](https://code.visualstudio.com/docs/agents/run/subagents): delegate bounded STANDARD work and integrated review to separate contexts. | Limits irrelevant transcript transfer and supports distinct implementation and review contexts. | Requires self-contained prompts, context reconciliation, and coordination; hosts vary in delegation and model-selection support. | Selected when task size and independence justify delegation; SIMPLE work stays proportionate. | Host delegation is unavailable or the assignment is too small or coupled for useful isolation. |
| [One continuous context](https://code.visualstudio.com/docs/agents/concepts/context): perform investigation, implementation, and review in one accumulating conversation. | Retains conversational nuance and avoids handoff work. | Earlier exploration can obscure current scope, and self-review shares the implementer's context. | STANDARD work benefits from bounded ownership and a fresh Reviewer; a single context is still sufficient for SIMPLE work. | The task is small, sequential, and has no independent review requirement. |
| **Unbounded delegation**: a project-defined approach using [subagents](https://code.visualstudio.com/docs/agents/run/subagents) broadly without task-specific boundaries or ownership. | Can distribute many activities and expose work to specialist contexts. | More agents create handoffs, integration, and potential write conflicts; isolation alone does not establish correctness or independent review. | Delegation is conditional on task fit, with dependency and write-ownership boundaries and one context-memory writer. | A recurring, substantial workload demonstrates a need for additional capacity with clear ownership and evaluation. |
| **Carry the full conversation**: copy planning and implementation transcripts into every fresh worker assignment using documented [agent handoff mechanisms](https://code.visualstudio.com/docs/agent-customization/custom-agents). | May preserve details that were not captured in task memory. | Reintroduces exploratory detail and makes authoritative decisions harder to distinguish from discarded ideas. | Focused assignments and concise shared memory carry verified current evidence without requiring the full transcript. | A specific essential decision cannot be captured in concise task context; record it explicitly rather than defaulting to full transcripts. |

These are project-defined context-management choices; the references document host mechanisms, not endorsement of this policy.

---

## Status

Accepted: keep separate planning and implementation sessions for larger or consequential work; small, understood tasks may skip Plan. Use bounded worker and Reviewer contexts for STANDARD, with task-scoped `sharing-context` memory and one writer; SIMPLE uses one Implementer.

---

## Date

2026-11-13

---
# Changelog

- 2026-11-14: Replaced mandatory phase-session handoff with the current optional-Planner and delegated-worker model; documented task-scoped `sharing-context` memory, the coordinator's single-writer rule, and fresh Reviewer context.
- 2026-11-14: Restored separate planning and fresh-session execution for larger or consequential work, retaining the small-task exception and current worker-context design.

# ADR: Focused Sessions and Specialist Context

## Context

Interactive planning, implementation, and validation have different responsibilities and benefit from carrying the relevant agreement and evidence without carrying every exploratory transcript. Long conversations can bury current requirements among earlier discussion and attempts. Separate role definitions alone do not reset accumulated context.

The [workflow ADR](AI-DEVELOPMENT-WORKFLOW.md) chooses interactive Plan followed by autonomous Build and Test. The [skills-first ADR](REUSABLE-WORKFLOWS-AS-SKILLS.md) defines the native-agent workflow and retained Implementer. This record addresses the distinct context-separation choice: when to use separate phase sessions and, where useful, bounded specialist contexts. Context separation is a practical organizational choice, not a guaranteed quality improvement or universal context-window threshold.

---

## Decision

Use separate planning and implementation sessions for phase-focused context in complex planned work, staying in the same native Agent mode. The implementation session starts with the approved plan and relevant repository guidance, dependencies, and evidence; it does not depend on the planning transcript. The [approved-plan and handoff ADR](APPROVED-PLAN-AND-HANDOFF.md) owns the required artifact and approval contract.

When the task warrants delegation and the host supports it, use [subagents](https://code.visualstudio.com/docs/agents/run/subagents) for bounded tasks:

- **Plan specialists**: Use built-in research or exploration for contained evidence gathering where supported.
- **Build and Test specialists**: Use the custom Implementer and native code or security review for bounded work where supported; verify rather than assume review independence.

Each specialist works in a separate context window and returns concise findings, decisions, or validation evidence. The main agent coordinates and carries forward relevant results rather than accumulating every exploratory transcript. Provide each delegated task with the context and boundaries it needs. Do not add agents for small tasks: delegation has coordination, model-usage, and handoff costs.

Fresh phase sessions and isolated subagent invocations provide context separation; merely defining separate roles does not. Carrying relevant repository guidance, dependencies, approved decisions, and evidence prevents isolation from dropping essential information.

The practical motivation is the smart-zone heuristic: accumulated context can become difficult to use before a hard context limit is reached. This does not establish a universal threshold or promise better outcomes. The [concepts glossary](../../CONCEPTS.md#execution-and-context) explains the term and records the requested AI Coding Dictionary reference's availability caveat.

Main-agent configuration and model choices are owned separately by [minimal agent configuration](MINIMAL-AGENT-CONFIGURATION.md) and [model selection](MODEL-SELECTION.md).

---

## Consequences

### Positive

- **Focused phase context**: A fresh implementation session keeps the approved plan and execution evidence prominent without requiring the planning transcript.
- **Bounded exploration**: Specialists can return scoped findings or reviews without making every exploratory step part of the main agent's conversation.
- **Reduced unnecessary delegation**: Delegation is reserved for tasks that justify its coordination and context-transfer costs.

### Negative

- **Handoff effort**: Relevant decisions, repository guidance, dependencies, and evidence must be explicitly carried into a fresh session or delegated task.
- **Context loss risk**: An incomplete handoff may omit nuance; the approved plan and scoped task instructions must preserve essential constraints.
- **Coordination cost**: Specialists use separate contexts and require clear task boundaries, result integration, and review of returned evidence.
- **Host variation**: Subagent support and behavior vary by host; this decision does not assume uniform capabilities or enforceable role isolation.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [One continuous session](https://code.visualstudio.com/docs/agents/run/planning): plan, approve, implement, and test using a single accumulating conversation. | Retains conversational nuance and avoids explicit transfer between phase sessions. | Exploratory detail and earlier attempts can obscure the approved plan and current task. Role separation alone does not clear accumulated context. | A fresh execution context anchored on the approved plan better foregrounds the agreed scope for nontrivial work. | The task is small enough that planning and implementation do not need a distinct session, such as a direct simple edit. |
| [No subagent delegation](https://code.visualstudio.com/docs/agents/run/subagents): keep research, implementation, and review in the main agent's context. | Avoids delegation overhead, context-transfer work, and integration of specialist output. | The main context accumulates exploratory details and cannot isolate bounded work or obtain an independent review through another context. | The selected approach uses specialists only when their bounded work justifies the cost; it does not require delegation for every task. | Work is small, sequential, or tightly coupled enough that delegation would add more coordination than value. |
| [Unbounded or default delegation](https://code.visualstudio.com/docs/agents/run/subagents): split work broadly among specialists without limiting delegation to tasks with a clear boundary. | Can distribute many activities and expose work to specialized contexts. | More agents create more handoffs, integration, and model usage; returned context may be incomplete or conflicting. Isolation by itself does not establish correctness or independent review quality. | Delegation is conditional on task fit and host support, and each assignment must be bounded and integrated by the main agent. | A recurring, substantial task demonstrates a need for more specialist capacity with clear ownership and evaluation. |
| [Transfer the planning conversation](https://code.visualstudio.com/docs/agent-customization/custom-agents): start execution with the full planning transcript rather than a focused artifact and relevant context. | May preserve details that were discussed but omitted from a plan. | Reintroduces exploratory content and makes the authoritative agreement harder to distinguish from discarded options and unresolved discussion. | The approved plan and relevant repository context are the handoff; unresolved consequential matters block approval rather than being inferred from transcript history. | A specific essential decision cannot be captured in the approved artifact, in which case that decision should be recorded before approval rather than relying on the full transcript. |

These are project-defined context-management choices; the references document host mechanisms, not endorsement of this policy.

---

## Status

Accepted: the user explicitly chose phase-focused sessions and bounded specialist contexts when justified. This record extracts the context-separation decision from the [workflow ADR](AI-DEVELOPMENT-WORKFLOW.md); it does not claim that delegation is always available or required.

---

## Date

2026-11-13

---

# Changelog

- 2026-11-13: Clarified that fresh phase sessions use the same native mode and bounded work uses supported native capabilities and the retained Implementer, following the [skills-first decision](REUSABLE-WORKFLOWS-AS-SKILLS.md).
- 2026-11-13: Extracted focused-session and specialist-context guidance from the [workflow ADR](AI-DEVELOPMENT-WORKFLOW.md) so its rationale and trade-offs can be revisited independently. The extraction does not change policy.

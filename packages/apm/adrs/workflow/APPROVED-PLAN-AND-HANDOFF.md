# ADR: Approved Plan and Execution Handoff

## Context

For nontrivial work, a short request does not necessarily reveal the user's intent, scope boundaries, or preferred trade-offs. An autonomous draft can appear complete while encoding unexamined assumptions. Relying on conversation history alone also makes the approved agreement difficult to inspect or carry into implementation.

The [AI development workflow ADR](AI-DEVELOPMENT-WORKFLOW.md) establishes interactive Plan, autonomous Build and Test, human Verify, and Observe after acceptance. This record defines the plan artifact and handoff contract that let the user approve the intended work before autonomous implementation begins. The expected long-term value includes less avoidable rework, better understanding and retained ownership, and more satisfying participation; these are intended benefits, not measured guarantees.

Creating the plan together is part of the work, not merely a prerequisite to delegating it. The user actively investigates the problem, tests ideas against the current system, and decides which trade-offs are acceptable; the AI helps surface evidence and alternatives. Writing down the result makes that reasoning available for review and gives the user a concrete basis for directing execution, recognizing departures from the agreement, and understanding the delivered change. It also makes it less tempting to accept an apparently complete AI-generated plan without understanding its assumptions.

---

## Decision

For nontrivial planned work, save a task-specific Markdown plan using the owning repository's plan-location conventions. Make it understandable without the original conversation and include:

- **Problem and outcome**: The problem, desired result, and relevant current behavior.
- **Agreed scope**: Requirements, non-goals, and compatibility constraints.
- **Design reasoning**: Material choices, alternatives, and accepted assumptions.
- **Risks and questions**: Dependency and security considerations and unresolved questions.
- **Manageable work**: Implementation steps or work packages, dependencies, and boundaries.
- **Verification and observation**: Observable acceptance criteria, required tests and checks, and what to watch after acceptance.

The user and AI develop the plan interactively. The AI asks purposeful questions about uncertainty that could affect requirements, scope, design, dependencies, security, or acceptance; the user evaluates answers, challenges assumptions, and chooses between consequential trade-offs. Do not repeat resolved questions or require decisions on routine coding details. The user must understand the problem, what will and will not be built, and why.

Unresolved consequential questions block approval. The AI may draft the artifact, but the user actively verifies its contents and approves the exact saved version; approval of a file's existence is not approval of its contents. Any material change to that plan requires renewed discussion and approval. The artifact remains the execution reference and supports later inspection of delivered work against the original agreement.

For planned work, begin Build with the approved file and relevant repository guidance in the separate implementation session required by the [focused-sessions ADR](FOCUSED-SESSIONS-AND-SPECIALIST-CONTEXT.md), rather than relying on hidden planning-conversation history. Routine implementation choices within the approved boundaries remain autonomous. A newly discovered requirement, material design or dependency change, or security assumption that changes the agreement returns to interactive Plan for user discussion and renewed approval. Do not silently rewrite the plan to keep execution moving.

This full artifact and approval contract does not apply to a small, localized, already understood edit covered by the workflow ADR's [simple-edit exception](AI-DEVELOPMENT-WORKFLOW.md#simple-edit-exception).

---

## Consequences

### Positive

- **Active understanding**: Interactive clarification lets the user consider material choices before implementation makes them harder to inspect.
- **Inspectable agreement**: A durable file makes the approved scope and reasoning available during execution and later comparison.
- **Explicit handoff**: A fresh execution session can use the approved artifact and relevant repository context without depending on the planning transcript.
- **Change control**: Returning material changes to planning prevents execution from silently redefining the agreement.

### Negative

- **Planning effort**: Interactive clarification and an approval pass require user time; this cost is accepted for work with consequential uncertainty.
- **Artifact maintenance**: A plan can be incomplete or become stale. The user must assess its content, and meaningful changes require renewed approval.
- **Handoff omissions**: A fresh session lacks conversational nuance unless the plan and supplied repository context preserve what execution needs.
- **No guaranteed outcome**: A complete, approved plan does not guarantee implementation quality or eliminate later corrections.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [Interactive planning without a durable artifact](https://code.visualstudio.com/docs/agents/run/planning): discuss requirements with the user, then continue execution from conversation context. | Preserves nuance and avoids duplicating discussion in a separate file. It can be sufficient for a small, bounded task. | Important decisions can be scattered through the conversation, and a fresh execution session may not have a reliable record of the approved scope and rationale. | For nontrivial work, an inspectable artifact and explicit handoff are part of the approval contract. The workflow retains direct implementation for understood simple edits. | The work is a small, already understood edit that meets the simple-edit exception. |
| [Autonomous plan with one approval checkpoint](https://code.visualstudio.com/docs/agents/run/planning): have the AI infer and draft the plan before asking for a single acceptance. | Produces a written artifact and avoids frequent interruptions. A complete draft can help surface possible questions. | A polished draft can conceal assumptions; quick acceptance alone does not establish that the user considered consequential choices. | Drafting is allowed, but interactive clarification and active review must shape approval rather than be replaced by a single checkpoint. | Requirements and consequential choices are already supplied by the user, and the user actively checks the draft before approval. |

These are project-defined workflow choices. The references describe supporting host capabilities, not endorsement of this exact contract.

---

## Status

Accepted: the user explicitly chose interactive planning, an approved durable plan, and a handoff into autonomous execution for nontrivial work. This record extracts the artifact and handoff contract from the workflow ADR; it does not represent a new policy decision or claim that the workflow is implemented.

---

## Date

2026-11-13

---

# Changelog

- 2026-11-13: Clarified why collaborative plan creation and a durable handoff support human understanding, judgment, and control.
- 2026-11-13: Extracted the durable plan, approval, and execution-handoff decision from the [workflow ADR](AI-DEVELOPMENT-WORKFLOW.md) to give this independently revisitable contract a focused owner. The extraction does not change policy.

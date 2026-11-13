# ADR: Separate Planning and Implementation Agents

## Context

The [AI development workflow ADR](AI-DEVELOPMENT-WORKFLOW.md) establishes interactive Plan, autonomous Build and Test, human Verify, and Observe after acceptance; [approved plan and handoff](APPROVED-PLAN-AND-HANDOFF.md) defines the durable approval artifact, while [focused sessions and specialist context](FOCUSED-SESSIONS-AND-SPECIALIST-CONTEXT.md) owns context separation and bounded delegation.

This record decides the main-agent layout that gives the workflow two distinct owners. Drivers are phase-specific responsibilities and tool policies, explicit routing, independent evaluation, reusable procedures, and limited coordination complexity. The transitional customization setup is neither a constraint nor evidence that this layout is already implemented.

---

## Decision

Use **two user-facing main agents: Planner and Implementation Orchestrator**. Implementers and reviewers are subordinate roles, not additional main entry points. Keep both main agents focused on their role contracts; place reusable procedures in skills and refer to their owning records rather than duplicating workflow procedures.

```text
User <-> Planner
        | approved plan
        v
Implementation Orchestrator -> subordinate implementers/reviewers as needed
        |
        v
User Verify -> Observe
```

- **Planner**: Own repository investigation, interactive clarification, and preparing the plan for the user's explicit approval. Do not start implementation. Its permission policy must permit investigation and plan-artifact writing without unrestricted implementation access.
- **Implementation Orchestrator**: Own planned-work execution after the approved-plan handoff and the simple-edit entry path. Decompose work with dependencies and acceptance criteria, delegate bounded implementation, integrate the result, and coordinate validation and independent reviews within the agreed boundaries. Parallelize independent work only and avoid competing edits; material changes return to Planner and the user.
- **Simple edits**: Enter the orchestrator directly only when they meet the [workflow ADR's exception](AI-DEVELOPMENT-WORKFLOW.md#simple-edit-exception); do not manufacture task splits or extra implementers.
- **Handoff and approval**: Follow the [approved-plan and handoff ADR](APPROVED-PLAN-AND-HANDOFF.md); context isolation and optional specialists follow the [focused-sessions ADR](FOCUSED-SESSIONS-AND-SPECIALIST-CONTEXT.md).
- **Build, Test, Verify, and Observe**: Follow the [workflow ADR](AI-DEVELOPMENT-WORKFLOW.md), which remains the owner of stage policies and validation requirements.

Separate roles make interactive clarification and autonomous execution independently configurable and testable without a shared mode-switching state machine. This is preferred over a single convenient entry point. Skills supply reusable procedures; the two main roles do not require a large permanent specialist hierarchy.

[Custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents) provide role-specific instructions and tools; [skills](https://code.visualstudio.com/docs/agent-customization/agent-skills) provide reusable procedures. [Subagent capabilities](https://code.visualstudio.com/docs/agents/run/subagents) vary by harness, so verify required delegation and reviewer capabilities in the intended host. Approval and review statements in prompts are process rules, not hard security boundaries; use host permissions and CI for mandatory enforcement. Evaluate Planner for purposeful clarification, explicit uncertainty, complete plans, and not implementing prematurely. Evaluate the coordinator for dependency-aware delegation, integration, review remediation, and escalation of material changes. Also test the end-to-end handoff and simple-edit path.

Agent-definition scope and model choices belong to [minimal agent configuration](MINIMAL-AGENT-CONFIGURATION.md) and [model selection](MODEL-SELECTION.md). Creation, reuse, guidance layering, and distribution are owned by [AI customization creation](../ai-customizations/AI-CUSTOMIZATION-CREATION.md), [reuse and tailoring](../ai-customizations/REUSE-AND-TAILORING.md), [guidance and instruction layering](../ai-customizations/GUIDANCE-INSTRUCTION-LAYERING.md), [package design](../distribution-and-synchronization/PACKAGE-DESIGN.md), and [distribution](../distribution-and-synchronization/DISTRIBUTION.md).

---

## Consequences

### Positive

- **Independent roles**: Planning and implementation have separate instructions, tool policies, and evaluation cases; each can evolve without adding mode-switching logic to the other.
- **Clear ownership**: The Planner does not start implementation, and the orchestrator does not redefine the approved agreement.
- **Reusable procedures**: Shared skills avoid duplicated procedure detail, while subordinate roles keep the main entry-point layout small.

### Negative

- **Manual role selection**: The user must select the appropriate role and transfer the approved plan for planned work; there is no single universal entry point.
- **Context loss**: A fresh execution session may lose conversational nuance; the plan and relevant context must preserve what execution needs.
- **Contract maintenance**: Two agent definitions and their handoff need maintenance and end-to-end evaluation.
- **Coordination cost**: Delegation and independent reviews add usage and integration work; concurrency can create conflicts.
- **Enforcement limits**: Separate agents do not guarantee alignment, correctness, or security; required controls still depend on permissions, checks, human approval, and review evidence.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [One custom orchestrator](https://code.visualstudio.com/docs/agent-customization/custom-agents): a project-defined agent with planning and implementation modes and one user entry point. | Retains shared context and reduces the number of main agent definitions. The user does not need to select a separate role for execution. | Combines interactive clarification with autonomous execution, requiring phase transitions, approval state, and phase-specific tool rules in one role. Changes may affect both modes and expand the combined evaluation surface. | Both modes can be tested, but independent configuration, isolated evaluations, and permission boundaries are harder to maintain. Entry-point convenience does not outweigh this coupling for the selected workflow. | The host supplies reliable, enforceable phase transitions and the combined configuration remains simpler without weakening independent evaluation. |
| [One orchestration skill](https://code.visualstudio.com/docs/agent-customization/agent-skills): load a reusable two-phase procedure on the default agent, including delegation through the host. | Requires less custom agent configuration and packages the procedure for reuse. Explicit invocation can make the intended sequence easier to repeat. | Moves the same phase and approval logic into a skill while the default agent still owns both roles. A loaded procedure does not itself provide separate tool profiles or role-level context boundaries. | The requirement is distinct owners for alignment and execution, not just a reusable sequence. Moving coordination instructions does not remove the two-phase coupling. | A single default-agent tool policy is sufficient and reliable phase handling can be established without separate roles. |
| [Separate planning and implementation skills](https://code.visualstudio.com/docs/agent-customization/agent-skills): invoke modular procedures on the default agent without custom main agents. | Reuses procedures across compatible hosts and reduces custom-role maintenance. Users can explicitly choose which procedure to invoke. | Phase discipline and approval transitions still depend on the user and active default-agent configuration. The skills do not independently configure role toolsets or establish a fresh-session handoff. | Procedural modularity is useful but insufficient for the desired role separation. These skills are supporting components of the selected agents instead of replacements for them. | Manually selecting procedures and using the default tool policy meets the workflow's evaluation and boundary requirements. |
| [Native planning](https://code.visualstudio.com/docs/agents/run/planning) with a [custom implementation coordinator](https://code.visualstudio.com/docs/agent-customization/custom-agents): use the host's planning experience before a custom execution role. | Preserves a separate execution owner while reducing maintenance of custom planning behavior. It can reuse the host's planning and approval UI. | The quality of persistent questioning and completeness of the plan contract depend on the selected host. Compatibility and behavior require evaluation rather than assumptions about native planning. | Project-specific clarification and a stable, independently configurable planning contract are central requirements. A custom Planner gives them an explicit owner; this is not a claim that native planning cannot work. | Native planning demonstrably satisfies the clarification, plan-file, approval, and evaluation contract in the intended host. |
| [Default agent with instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions) or reusable prompts: guide the existing role without a dedicated workflow-agent pair. | Minimizes configuration and works well for manually steered requests. Repository guidance can still describe required checks and conventions. | Clarification, handoff, delegation, and review routing rely more heavily on session-level steering. The user must repeatedly establish responsibilities instead of selecting an independently configured owner. | This does not express the repeatable two-role workflow as clearly. It remains suitable for ordinary direct work, but is not the selected architecture for planned execution. | The workload is mostly simple edits and a dedicated coordinator no longer provides enough value to justify its maintenance. |
| [Larger custom-agent hierarchy](https://code.visualstudio.com/docs/agent-customization/custom-agents) using [subagents](https://code.visualstudio.com/docs/agents/run/subagents): add separate planning, architecture, task-management, implementation, and review layers. | More specialized responsibilities may isolate substantial context or provide distinct tool policies for demonstrated needs. | Each new layer introduces contracts, routing, handoffs, and evaluation obligations. More delegation also increases coordination and model usage without automatically improving results. | The current workflow needs only two main owners and necessary subordinate implementers and reviewers. Additional permanent layers are unjustified before a concrete responsibility gap is established. | A recurring, substantial gap warrants one focused specialist with a clear contract; add that role rather than expanding the hierarchy by default. |

The role arrangements above are project-defined compositions of documented mechanisms. Their comparative fit is architectural judgment for this workflow, not a measured performance claim.

---

## Status

Accepted: the user explicitly selected two different main agents. This records the architectural choice, not completion or validation of the future agent implementation.

---

## Date

2026-11-13

---

# Changelog

- 2026-11-13: Relocated from `packages/apm/adrs/SEPARATE-PLANNING-AND-IMPLEMENTATION-AGENTS.md`; workflow ownership and handoff details are linked to focused ADRs. Organization does not change the decision.

# ADR: Reusable Workflows as Skills

## Context

The [workflow](AI-DEVELOPMENT-WORKFLOW.md) requires interactive planning, approved handoff, implementation, testing, human verification, and observation. The [approved-plan contract](APPROVED-PLAN-AND-HANDOFF.md) and [focused-session decision](FOCUSED-SESSIONS-AND-SPECIALIST-CONTEXT.md) remain in force. Planning and execution are repeatable procedures rather than distinct personas. Maintaining custom main agents duplicates native orchestration and creates role-selection and compatibility overhead.

The user explicitly chose reusable procedures in the existing native Agent mode, retaining phase isolation and one focused implementation role. This decision concerns workflow representation, not package distribution or synchronization.

---

## Decision

The active built-in host agent orchestrates larger planned work in its existing native Agent mode. It invokes the [planning skill](../../development-core/.apm/skills/planning/SKILL.md) for interactive planning and the [implementation orchestration skill](../../development-core/.apm/skills/implementation-orchestration/SKILL.md) for execution. These are extensible procedures, not custom roles or a replacement agent loop. The active agent carries them out using the user's selected model or router and permission mode, including Autopilot where supported. Skills neither select those settings nor waive the user's approval of the exact plan.

Simple, clear tasks are ordinary requests to the native Agent and bypass both workflow skills; applicable guidance and checks still apply, without forced Implementer delegation. The implementation-orchestration skill is for approved-plan execution, not simple-task intake. For larger planned work, start a fresh planning session, clarify consequential choices, save the plan, review and approve its exact contents, then start a fresh execution session in the same native Agent mode. Carry the approved plan and relevant context into execution; material changes return to interactive planning and renewed approval. This takes more setup than immediately coding, but is intended to make the full task quicker by clarifying implementation before execution and reducing repeated instructions, refinements, rework, and errors. The plan is a working handoff artifact, not a required permanent repository record; see the [approved-plan contract](APPROVED-PLAN-AND-HANDOFF.md). User-facing invocation examples are in the [APM guide](../../README.md#choosing-a-workflow); slash invocation depends on the host, and agents do not execute slash commands internally.

Use only the custom [Implementer](../../development-core/.apm/agents/implementer.agent.md): a senior engineer for bounded implementation, without subdelegation. Its contract requires behavioral red-green-refactor tests for testable changes, directly related documentation and ADR skill use where appropriate, and focused work and validation. Approved-plan implementation assignments within the orchestration skill use this role, with proportionate delegation rather than artificial parallelism. Native research and exploration remain optional where useful and supported; do not rebuild a specialist hierarchy.

The orchestration workflow requires both independent native code and security reviews of the integrated change, in fresh assessment contexts and in parallel where supported. Obtain actual review evidence; naming a role does not establish independence. Correctable blocking findings return to an Implementer and the affected checks and reviews repeat. An unavailable required review or unresolved blocking finding prevents a successful completion claim; report the blocker rather than silently omit a review.

[Agent Skills](https://agentskills.io/what-are-skills) provide a portable format for reusable, progressively disclosed instructions; supporting tools and registries can discover or share them according to their own capabilities and scopes. Portability is a design goal, not a guarantee of identical discovery, invocation, model selection, permissions, or behavior. The native host remains responsible for orchestration; skill prose and role contracts are not technical permission enforcement. Verify host capabilities and apply actual permissions, checks, and human approval as appropriate.

The workflow skills and Implementer are available in the `development-core` source package; their presence does not establish consumer installation, runtime discovery, or compliance. [Package design](../distribution-and-synchronization/PACKAGE-DESIGN.md) and [distribution](../distribution-and-synchronization/DISTRIBUTION.md) record the implemented source split and the still-separate consumer setup; the [synchronization TODO](../distribution-and-synchronization/SYNCHRONIZATION.md) remains future work.

---

## Consequences

### Positive

- **Native orchestration**: The host's existing agent loop coordinates the procedures without users switching between custom main personas.
- **Reusable procedures**: Focused skills can evolve and be shared through compatible tools and registries independently of a custom main-agent definition.
- **Focused implementation**: One bounded Implementer adds a concrete test-first engineering contract without a permanent specialist hierarchy.
- **Preserved control**: Fresh sessions, an approved plan, and human verification remain explicit workflow boundaries.
- **Proportionate routing**: Simple, clear work stays on the native Agent's direct path rather than invoking a workflow skill or requiring a custom worker.
- **Less implementation churn**: Interactive preparation is intended to reduce the repeated direction and corrections needed during execution, while the plan itself does not have to outlive the completed work.

### Negative

- **Host variation**: Discovery, invocation, delegation, review independence, and model inheritance require verification in each intended host.
- **Process is not enforcement**: Skills and agent prose cannot guarantee approval, isolation, or permission restrictions; host controls and review evidence remain necessary.
- **Handoff and maintenance**: Fresh sessions require an accurate plan and context transfer, and both skills and the Implementer need evaluation as hosts evolve.
- **Review availability**: Either required native independent review may be unavailable; this blocks successful workflow completion until the requirement can be satisfied, rather than authorizing a weaker review substitute.

---

## Alternatives Considered

These are project-defined arrangements of documented mechanisms, not externally prescribed workflows.

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| **Separate reusable skills on the native agent**: project-defined planning and execution procedures using [Agent Skills](https://agentskills.io/what-are-skills) and the host's [agent capabilities](https://code.visualstudio.com/docs/agents/overview). | Reuses the host orchestrator and makes procedures independently extensible and discoverable in supporting tools; the user stays in one native mode. | Approval, phase transitions, discovery, and review depend on the user and host; skills do not supply separate enforced tool policies. | Selected: procedural reuse and fresh sessions satisfy the chosen boundaries without custom main-agent maintenance. | A tested host cannot support required discovery or workflow boundaries, or a stronger enforceable role boundary becomes necessary. |
| **Two custom main agents**: a project-defined [custom-agent](https://code.visualstudio.com/docs/agent-customization/custom-agents) arrangement for Planner and Implementation Orchestrator. | Separate role instructions and optional host configurations expose phase-specific responsibilities and permit independent evaluation. | Requires main-agent selection, handoff and two role contracts; tool restrictions and behavior still depend on the host. | The procedures do not need distinct personas when native orchestration and separate sessions suffice. | A demonstrated need for independently enforceable phase policies cannot be met through host/session controls and skills. |
| **One custom orchestration agent**: combine planning and execution in one [custom agent](https://code.visualstudio.com/docs/agent-customization/custom-agents). | Offers one selected role and a single place for workflow-specific guidance. | Reimplements or wraps native coordination and couples both procedures to a custom persona; approval and capability constraints still require verification. | Separate skills provide the reusable procedures without replacing the active native agent. | A recurring, verified capability or policy gap requires a distinct orchestrator beyond native behavior and skills. |
| **Native agent with ad hoc instructions**: steer each request using [custom instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions) and prompts, without reusable skills. | Minimal customization and suitable for isolated work; the host retains full flexibility. | Repeated planning and execution contracts must be restated or can drift, and procedures are less readily packaged for discovery. | The recurring procedures justify focused skills, while direct work remains suitable for simple edits. | The procedures cease to be recurring or host-native workflow features demonstrably satisfy them without maintained skills. |
| **Larger custom specialist hierarchy**: compose [custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents) and [subagents](https://code.visualstudio.com/docs/agents/run/subagents) for architecture, planning, implementation, and review. | Can isolate substantial specialist context or express different contracts where those are genuinely needed. | Adds routing, context transfer, integration, and evaluation costs; more roles do not guarantee independent review or correct results. | Built-in exploration and review plus one focused Implementer meet the present need without recreating a hierarchy. | A sustained, evidenced responsibility gap requires a specifically bounded role that native capabilities cannot meet. |

---

## Status

Accepted: the user explicitly approved skills-first native orchestration and one focused custom Implementer. Simple tasks bypass both workflow skills; larger execution requires a fresh session and approval of the exact saved plan. Source readiness does not establish host discovery or behavior.

---

## Date

2026-11-13

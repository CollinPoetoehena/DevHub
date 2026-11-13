# ADR: AI Development Workflow

## Context

AI-assisted work needs a deliberate workflow from deciding what to build through implementation, testing, and observing the result in use. A short request followed by autonomous planning and execution can leave consequential questions unanswered: the agent may fill gaps with plausible assumptions and produce something different from what the user intended. Passing automated checks alone also does not establish that the outcome meets the user's intent or behaves well over time.

The goal is not only a working output. The user wants to remain actively involved in understanding the problem, requirements, trade-offs, design choices, and manageable work packages. Reviewing and refining a plan is part of the engineering work, not administrative overhead to automate away.

The decision drivers are alignment before coding, informed human control, a durable and inspectable specification, retained project knowledge, autonomous implementation and testing within agreed boundaries, and feedback from actual use. Preserving critical thinking and enjoyment of the work is an explicit personal priority. These are intended benefits and preferences, not measured claims about productivity or cognitive effects.

Active participation is valuable in its own right. Defining the problem, examining the existing system, weighing alternatives, and shaping the plan together keep the user focused on the engineering rather than merely requesting an implementation and hoping the result is right. This makes the work more engaging and fulfilling for the user while retaining space to delegate mechanical execution. The user can explain the intended outcome and the reasons behind it, recognize a questionable assumption, and make informed changes later without relying entirely on the AI to interpret its own work.

The plan is therefore a tool for thinking and control, not just instructions for an agent. The AI can bring evidence, propose options, and challenge the user's ideas, but neither a plausible answer nor a polished document substitutes for the user's judgment. Discussing trade-offs before implementation makes it easier to steer the result, decide what is deliberately out of scope, and assess whether an unexpected discovery warrants a change of direction. This also reduces the risk of over-reliance: the human remains able to question, verify, maintain, and take responsibility for the result.

The workflow addresses recurring failure modes:

- **Misaligned intent**: Requirements are not always fully understood at the start, and the agent can build a plausible solution that misses what the user wanted. A brief request may leave important behavior, constraints, or trade-offs unstated, so the agent fills gaps with assumptions that are difficult to notice once they are embodied in code. Iterative discussion and an actively reviewed plan uncover those assumptions, explore alternatives and edge cases, and refine the intended outcome before implementation. This helps the user recognize what is being agreed to and gives both parties a shared basis for later verification. As David Thomas and Andrew Hunt observe in [The Pragmatic Programmer](https://www.amazon.co.uk/Pragmatic-Programmer-Anniversary-Journey-Mastery/dp/B0833F1T3V), people do not know their exact requirements from the outset; Matt Pocock relates this to agent misalignment in [The Agent Didn't Do What I Want](https://github.com/mattpocock/skills/tree/main#1-the-agent-didnt-do-what-i-want).
- **Unverified code**: Even an agreed design can produce broken behavior, and plausible-looking code is not evidence that it works in the actual system. Without feedback, an agent can build further changes on top of an incorrect assumption or leave a regression unnoticed until review. Small, deliberate steps with static checks, existing and focused automated tests, and relevant browser checks give the agent evidence it can use to detect and correct problems while their cause is still easier to isolate. Tests should exercise the intended behavior and meaningful edge cases, while the user still verifies that the result matches the agreed intent. Thomas and Hunt emphasize in [The Pragmatic Programmer](https://www.amazon.co.uk/Pragmatic-Programmer-Anniversary-Journey-Mastery/dp/B0833F1T3V) that progress depends on timely feedback and tasks should remain small enough to learn from it; Pocock applies this to agents in [The Code Doesn't Work](https://github.com/mattpocock/skills/tree/main#3-the-code-doesnt-work).
- **Eroding design**: Faster code generation can accumulate complexity faster if each change is judged only by whether it works now. Repeated local fixes, duplicated logic, and unclear responsibilities can make later changes harder to understand, test, and safely extend even when the immediate feature passes its checks. Continuously consider responsibilities, coupling, and maintainability rather than letting complexity spread through the codebase; keep callers' interfaces understandable while placing related complexity behind appropriate boundaries. Kent Beck advocates ongoing investment in system design in [Extreme Programming Explained](https://www.amazon.co.uk/Extreme-Programming-Explained-Embrace-Change/dp/0321278658), and John Ousterhout describes deep modules as providing substantial functionality through a simple interface in [A Philosophy Of Software Design](https://www.amazon.co.uk/Philosophy-Software-Design-2nd/dp/173210221X). Pocock connects these ideas to AI-accelerated complexity in [We Built A Ball Of Mud](https://github.com/mattpocock/skills/tree/main#4-we-built-a-ball-of-mud). Design attention is continuous, not a reason to introduce speculative abstractions.
- **Context drift**: Long conversations can bury requirements in exploratory detail and earlier attempts. Fresh phase sessions and bounded specialist contexts keep the current task and authoritative agreement prominent.
- **Passive reliance**: Delegating every decision can leave the user unable to explain or evaluate the result. Interactive Plan and human Verify preserve active understanding and ownership.

---

## Decision

Use four main stages: **Plan, Build, Test, and Observe**. Plan is interactive and human-in-the-loop; Build and Test are autonomous within an approved scope; Observe follows the user's final verification and acceptance of the tested result. The separate [approved-plan and handoff ADR](APPROVED-PLAN-AND-HANDOFF.md) owns the durable plan contract; the [focused-sessions ADR](FOCUSED-SESSIONS-AND-SPECIALIST-CONTEXT.md) owns context separation and specialist delegation.

The [VS Code AI development guides](https://code.visualstudio.com/docs/agents/guides/overview) cover planning, implementation, testing, and validation. The four stage names, human approval gates, and final Observe stage below are this project's chosen workflow, not a claim that the host prescribes this exact sequence.

```text
Plan: user + AI -> full .md plan -> user approval
                         |
Build: autonomous implementation
                         |
Test: existing suite + automated tests + reviews
                         |
Verify: user checks the outcome and approves
                         |
Observe: behavior in use + feedback -> next Plan
```

This workflow decision is independent of a particular agent layout. The [two-agent implementation ADR](SEPARATE-PLANNING-AND-IMPLEMENTATION-AGENTS.md) separately explains how the selected customizations implement it.

Verify is a human approval gate after Test, not a fifth autonomous stage. Build and Test may iterate, including test-first work; their separation identifies responsibilities and required evidence rather than prohibiting feedback loops.

### Plan

The user and AI investigate nontrivial work together. The AI asks purposeful follow-up questions about uncertainty that could affect requirements, scope, design, dependencies, security, or acceptance; the user evaluates the answers, challenges assumptions, and chooses between consequential trade-offs. Do not treat a brief request followed by "implement it" or a polished autonomous draft as sufficient alignment. The user should understand what will and will not be built, and why; routine coding details and resolved questions do not need repeated discussion.

The additional planning time is deliberately accepted to keep consequential choices visible and preserve the user's understanding and ownership. It is a workflow preference, not a guarantee of better results on every task. The [approved-plan and handoff ADR](APPROVED-PLAN-AND-HANDOFF.md) defines the durable artifact, required contents, exact-version approval, and execution handoff. Unresolved consequential questions block approval.

### Build

Start autonomous implementation within the approved plan. The execution session receives the approved file and relevant repository guidance; it does not rely on hidden planning-conversation history. Routine coding decisions within the agreed boundaries can be autonomous. A newly discovered requirement, material design or dependency change, or security assumption returns to interactive Plan for discussion and renewed approval when it changes the agreement. Do not silently rewrite the plan to keep execution moving. See the [approved-plan and handoff ADR](APPROVED-PLAN-AND-HANDOFF.md) for the contract.

### Test

The AI owns validation and review of integrated changes, not merely writing code and leaving verification to the user:

- **Existing test suite**: Run applicable repository suites using established commands, including regression checks for behavior that must remain unchanged. Run broader suites when required by the plan or change impact; new tests do not replace the existing suite.
- **Focused automated tests**: Add or update tests for introduced or fixed behavior and meaningful edge cases. For testable behavior changes, use red-green-refactor: confirm a test fails for the intended reason, implement until it passes, then refactor while keeping tests green. Use unit, integration, end-to-end, or browser checks appropriate to the change; do not create unrelated tests or tooling by default.
- **Build and static checks**: Run applicable build, type-check, linting, and security checks required by the owning component.
- **Independent reviews**: Obtain code and security reviews of integrated changes, remediate blocking findings, and repeat affected checks and reviews.
- **Evidence and limitations**: Report acceptance-criteria coverage, executed commands and results, review outcomes, and limitations. Failed or unavailable required checks block a successful completion claim; distinguish pre-existing failures from regressions.

### Human Verify gate

After Build and Test, the user verifies that the delivered behavior matches the approved intent and that the evidence is sufficient, then explicitly accepts or rejects the result. This can include trying the relevant user flow, inspecting observable output, and checking any limitations that automated tests cannot establish.

The final human review is focused rather than a repeat of every implementation-level check. AI testing and reviews do not remove human responsibility for acceptance. Rejection returns the work to Build and Test, or to Plan when the intended requirements change. Acceptance does not itself authorize a commit, merge, deployment, or external action beyond the user's granted scope.

### Observe

After acceptance, observe the change in actual use or the relevant deployed environment. This is distinct from proving acceptance criteria during Test: it checks whether real behavior and experience continue to match the intended outcome.

- **Behavior in use**: Watch relevant outcomes, errors, regressions, performance, or agent behavior using existing diagnostics, logs, metrics, and representative usage where appropriate.
- **User feedback**: Notice whether the change solves the original problem and whether usability, maintenance, or operational friction appears beyond the tested scenarios.
- **Learning and follow-up**: Record actionable observations and feed new requirements or fixes into the next Plan, rather than silently expand the completed scope.
- **Proportionate observation**: Choose the signals and observation period for the change's impact. Observation is not mandatory new monitoring infrastructure, continuous dashboard watching, or a reason to remain permanently on call.

### Simple-edit exception

Skip the separate planning session and full plan file for a small, localized edit whose intended behavior, scope, and verification are already clear, such as a typo correction or a narrowly defined mechanical change. Proceed directly to implementation with a concise statement of scope and proportionate checks.

The exception is based on uncertainty and impact, not only line count. If the edit exposes consequential questions, broader dependencies, or security-sensitive decisions, stop the fast path and establish an approved plan. Direct implementation does not waive applicable review or validation requirements.

---

## Consequences

### Positive

- **Active understanding**: The user reasons about requirements and trade-offs before code makes those choices harder to inspect or change.
- **Engaged participation**: Thinking through the problem and directing the plan make the work itself meaningful to the user, rather than reducing the user's role to prompting and hoping.
- **Inspectable agreement**: The approved plan exposes assumptions early and supplies a reference for implementation, testing, acceptance, and observation.
- **Autonomous execution**: Build and Test delegate repetitive implementation and verification while human attention stays on intent and consequential decisions.
- **Real-world feedback**: Observe connects tested results to actual use and supplies evidence for the next iteration.
- **Proportionate effort**: The simple-edit exception avoids turning a deliberate workflow into paperwork for changes that are already understood.

### Negative

- **Human availability**: Interactive planning and final Verify require time and attention. This cost is intentionally preferred over leaving important choices implicit.
- **Plan maintenance**: A saved plan can become stale or omit nuance; approval must be tied to its exact version, and meaningful changes need renewed discussion.
- **Passive-approval risk**: Asking questions or producing a file does not guarantee understanding. The user must actively assess the plan and outcome.
- **Verification limits**: Automated tests and AI reviews do not establish every property; the user still owns acceptance, and Observe can reveal issues after it.
- **Observation ownership**: Relevant follow-up needs an owner and proportionate effort, without turning every change into an indefinite monitoring obligation.

---

## Alternatives Considered

These are project-defined workflow choices, not externally standardized policies. The references describe supporting host capabilities, not endorsement of the proposed process.

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| **Fully autonomous planning and execution:** a project-defined flow using [agent capabilities](https://code.visualstudio.com/docs/agent-customization/custom-agents) to infer a plan, implement, and review from the initial request without an interactive approval boundary. | Requires less user involvement and can keep execution moving when requirements are already completely specified. It delegates both decision preparation and implementation. | Missing requirements may become unexamined assumptions before the user sees the result. The user has fewer opportunities to reason about the project and may become dependent on outputs they do not understand. | Active alignment and retained human understanding are primary goals, so removing the discussion would automate the part the user deliberately wants to own. Autonomous implementation remains valuable after approval. | A task is already fully specified and qualifies for the simple-edit exception; this is not a blanket replacement for interactive planning. |
| **Autonomous plan with one approval checkpoint:** a project-defined use of [planning capabilities](https://code.visualstudio.com/docs/agents/run/planning) where the AI drafts the entire plan before asking the user to accept it. | Produces an artifact and preserves a pre-execution approval opportunity with fewer conversational interruptions. A detailed draft can help the user identify questions. | A polished draft can conceal assumptions, and a quick approval does not establish that the user considered the alternatives. Questions that change the plan may still require an interactive round. | A checkpoint is necessary but insufficient: clarification and critical discussion must shape the plan, not merely follow an autonomous proposal. Drafting is allowed as part of the selected interactive process. | The user supplies complete requirements and actively checks the draft; unresolved consequential choices still trigger discussion before approval. |
| **Always require a full plan:** apply [planning capabilities](https://code.visualstudio.com/docs/agents/run/planning) and an approved Markdown artifact to every edit, including already understood mechanical changes. | Gives every task the same audit trail and eliminates judgment about when to plan. | Adds discussion and documentation effort where there are no consequential choices. This can encourage perfunctory approval and distract from tasks that genuinely need reasoning. | Deliberate planning is valuable because it resolves uncertainty, not because every edit needs a document. The simple-edit exception preserves proportionate effort without bypassing necessary checks. | A repository or regulated process explicitly requires a plan artifact for every change. |
| **Manual Build and Test with AI suggestions:** the user implements and validates each step while using [AI assistance](https://code.visualstudio.com/docs/agents/overview) for focused suggestions. | Keeps hands-on control throughout execution and is useful when implementation itself is the learning objective. The user can investigate each change immediately. | Repetitive coding, test execution, and review remain user-managed rather than delegated. Attention can be spent on mechanical steps instead of consequential decisions. | The selected default deliberately automates Build and Test after alignment, while retaining human Verify and Observe. This does not prohibit choosing hands-on work when that is the goal. | Learning through implementation or a change's risk makes continuous human involvement more valuable than autonomous execution. |
| **Finish at automated Test:** a project-defined flow that treats successful [testing and validation](https://code.visualstudio.com/docs/agents/guides/overview#_test-and-validate) as the endpoint without a human Verify gate or final Observe. | Provides a simple, repeatable endpoint and avoids additional acceptance and follow-up effort. | Tests can miss mismatched intent, usability problems, and behavior that appears only in actual use. A passing suite is not evidence that the user accepts the result. | Human Verify establishes acceptance, and Observe closes the feedback loop after it. Neither can be replaced by declaring that automated checks passed. | For a change with little ongoing impact, observation can be lightweight; this does not remove the human acceptance gate. |

---

## Status

Accepted: the user explicitly chose Plan, Build, Test, and Observe, with interactive planning, autonomous implementation and testing, human verification before observation, and a simple-edit exception. This records the workflow policy, not a claim that its automation is already implemented.

---

## Date

2026-11-13

---

# Changelog

- 2026-11-13: Expanded the rationale for active human understanding, control, and enjoyment, and connected alignment, feedback, and ongoing design to the referenced engineering ideas.
- 2026-11-13: Relocated from `packages/apm/adrs/AI-DEVELOPMENT-WORKFLOW.md`; the approved-plan contract and focused-session guidance are recorded in separate linked ADRs for independent reference. Organization does not change the decision.

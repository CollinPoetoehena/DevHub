# ADR: AI Development Workflow

## Context

AI-assisted work needs a deliberate workflow from deciding what to build through implementation, testing, and observing the result in use. A short request followed by autonomous planning and execution can leave consequential questions unanswered: the agent may fill gaps with plausible assumptions and produce something different from what the user intended. Passing automated checks alone also does not establish that the outcome meets the user's intent or behaves well over time.

The goal is not only a working output. The user wants to remain actively involved in understanding the problem, requirements, trade-offs, design choices, and manageable work packages. Reviewing and refining a plan is part of the engineering work, not administrative overhead to automate away.

The decision drivers are alignment before coding, informed human control, an inspectable specification through delivery, retained project knowledge, autonomous implementation and testing within agreed boundaries, and feedback from actual use. Preserving critical thinking and enjoyment of the work is an explicit personal priority. These are intended benefits and preferences, not measured claims about productivity or cognitive effects.

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

Use four main stages: **Plan, Build, Test, and Observe**. Keep two distinct working phases: interactive, human-in-the-loop **planning**, followed by autonomous **implementation and testing** within the agreed scope. Planning is required for larger, unclear, cross-cutting, or consequential work; small, localized, already understood tasks may skip it. Observe follows the user's final verification and acceptance of the tested result. This record owns the plan artifact and handoff contract; the [focused-sessions ADR](FOCUSED-SESSIONS-AND-SPECIALIST-CONTEXT.md) owns context separation and specialist delegation.

The [VS Code AI development guides](https://code.visualstudio.com/docs/agents/guides/overview) cover planning, implementation, testing, and validation. The four stage names, human approval gates, and final Observe stage below are this project's chosen workflow, not a claim that the host prescribes this exact sequence.

```text
Plan: user + Planner -> full .md plan -> user approval
      (required for larger work; optional for small, understood edits)
                         |
      fresh implementation session + approved plan
                         |
Build: Implementation Orchestrator -> SIMPLE or STANDARD
                         |
Test: existing suite + automated tests + reviews
                         |
Verify: user checks the outcome and approves
                         |
Observe: behavior in use + feedback -> next Plan
```

The [workflow-agent ADR](WORKFLOW-AGENTS-AND-FOCUSED-SKILLS.md) maps these phases to thin roles using focused skills. Planner owns Plan; Implementation Orchestrator is the single entry point for Build and Test, including the simple-edit path. Keeping one implementation entry point makes the workflow locally tailorable without requiring every task to take the full STANDARD route; it does not combine planning and implementation.

Verify is a human approval gate after Test, not a fifth autonomous stage. Build and Test may iterate, including test-first work; their separation identifies responsibilities and required evidence rather than prohibiting feedback loops.

### Plan

The user and Planner investigate larger or consequential work together before implementation. Planner uses rounds of purposeful questions about uncertainty that could affect requirements, scope, design, dependencies, security, or acceptance; the user evaluates the answers, challenges assumptions, and chooses between consequential trade-offs. Do not treat a brief request followed by "implement it" or a polished autonomous draft as sufficient alignment. The user should understand what will and will not be built, and why; routine coding details and resolved questions do not need repeated discussion.

Interactive planning takes time up front, but is intended to make the full task quicker: clarifying requirements and decisions before implementation should reduce repeated instructions, implementation refinements, avoidable rework, and errors. It also keeps consequential choices visible and preserves the user's understanding and ownership. This is the rationale for the workflow, not a measured or guaranteed productivity result.

Save a unique `<task-working-directory>/tmp/plan-<id>.md` that is understandable without the planning conversation. Include:

- **Problem and outcome**: Desired result, relevant current behavior, and supporting evidence.
- **Agreed scope**: Requirements, non-goals, compatibility constraints, and observable acceptance criteria.
- **Design reasoning**: Material choices, alternatives, and accepted assumptions.
- **Risks and questions**: Dependency and security considerations and unresolved questions.
- **Manageable work**: Work packages, owned file boundaries, dependencies, and safe parallel groups.
- **Validation and follow-up**: Required tests, integrated checks, review expectations, and human Verify and Observe activities.

Unresolved consequential questions block approval. The user actively reviews and approves the exact saved version, not merely the file's existence. Material revisions require renewed discussion and approval. Planner saves the plan and stops; it does not start implementation.

### Build

For planned work, start a fresh Implementation Orchestrator session with the approved plan's absolute path, confirmation of its current-version approval, and relevant repository guidance. Merely switching roles in the planning conversation is not a fresh handoff. The execution session does not rely on hidden planning history or repeat resolved decisions; routine coding choices within the agreed boundaries remain autonomous. A newly discovered requirement, material design or dependency change, or security assumption returns to the separate planning phase for discussion and renewed approval when it changes the agreement. Do not silently rewrite the plan to keep execution moving.

Implementation Orchestrator delegates edits to Implementer. SIMPLE handles obvious, localized, low-risk work with one fresh worker and proportional checks; STANDARD handles other work with dependency-aware assignments, safe parallelism, integrated validation, and an independent Reviewer. The execution mode and need for planning are separate judgments: a small, well-understood behavior change can need STANDARD checks without a full planning phase. STANDARD uses the `sharing-context` skill to pass concise task evidence to fresh workers, not to replace the approved plan.

Keep the plan available through handoff, implementation, testing, and user acceptance. It need not become a permanent repository record after completion; optional retention in a related issue or task outside the repository is sufficient unless project or organizational requirements say otherwise.

### Test

The AI owns validation and review of integrated changes, not merely writing code and leaving verification to the user:

- **Existing test suite**: Run applicable repository suites using established commands, including regression checks for behavior that must remain unchanged. Run broader suites when required by the plan or change impact; new tests do not replace the existing suite.
- **Focused automated tests**: Add or update tests for introduced or fixed behavior and meaningful edge cases. For testable behavior changes, use red-green-refactor: confirm a test fails for the intended reason, implement until it passes, then refactor while keeping tests green. Use unit, integration, end-to-end, or browser checks appropriate to the change; do not create unrelated tests or tooling by default.
- **Build and static checks**: Run applicable build, type-check, linting, and security checks required by the owning component.
- **Independent review**: In STANDARD, use one fresh, read-only Reviewer for code quality, security, and project conformance; remediate blocking findings and repeat affected checks and review. Prefer a different model/provider when supported and permitted, otherwise use the available model. SIMPLE does not require independent review. An unavailable required review blocks completion; a named reviewer does not guarantee independence.
- **Evidence and limitations**: Report acceptance-criteria coverage, executed commands and results, review outcomes, and limitations. Failed or unavailable required checks block a successful completion claim; distinguish pre-existing failures from regressions.

After either execution mode, reconcile all documentation and required ADRs within the changed scope, including omissions from this or earlier work; ignore unrelated areas. Delegate missing or stale documentation to a new, fresh Implementer for a documentation/ADR-only update, verify its result and applicable checks, and do not require a separate Reviewer for this simple update. Significant decisions follow project ADR conventions; routine edits do not need artificial records. End the evidence report by invoking skill `commit-command` to generate one add/commit/push sequence covering all current changes for the user to verify and execute, or report its safety blocker. The orchestrator does not execute those commands.

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

Skip the separate planning phase and full plan file for a small, localized task whose intended behavior, scope, and verification are already clear, such as a typo correction or a narrowly defined mechanical change. Give the request directly to Implementation Orchestrator, which uses SIMPLE when the low-risk criteria are met and otherwise STANDARD. Applicable guidance and proportionate checks still apply.

The exception is based on uncertainty and impact, not only line count. If the task exposes consequential questions, broader dependencies, or security-sensitive decisions, stop execution and complete the separate planning phase before proceeding. Direct work does not waive applicable review or validation requirements. For larger tasks, use the saved-plan approval and fresh-session handoff above.

---

## Consequences

### Positive

- **Active understanding**: The user reasons about requirements and trade-offs before code makes those choices harder to inspect or change.
- **Engaged participation**: Thinking through the problem and directing the plan make the work itself meaningful to the user, rather than reducing the user's role to prompting and hoping.
- **Inspectable agreement**: The approved plan exposes assumptions early and supplies a reference through implementation, testing, and acceptance; it need not become a permanent repository record.
- **Less implementation churn**: Resolving consequential questions before coding is intended to reduce repeated instruction, refinement, and mistakes, making the full workflow quicker despite its up-front planning time.
- **Autonomous execution**: Build and Test delegate repetitive implementation and verification while human attention stays on intent and consequential decisions.
- **Real-world feedback**: Observe connects tested results to actual use and supplies evidence for the next iteration.
- **Proportionate effort**: The simple-edit exception avoids turning a deliberate workflow into paperwork for changes that are already understood.

### Negative

- **Human availability**: Interactive planning and final Verify require time and attention. This cost is intentionally preferred over leaving important choices implicit.
- **Plan maintenance**: A plan can become stale or omit nuance while work is active; approval must be tied to its exact version, and meaningful changes need renewed discussion. Keeping it after completion is optional.
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
| **Planning only in conversation:** use [planning capabilities](https://code.visualstudio.com/docs/agents/run/planning) without a saved handoff artifact. | Preserves discussion nuance and avoids maintaining a second representation of the agreement. | Scope and decisions can be scattered through a transcript that a fresh implementation session cannot reliably inspect. | Larger work needs an explicit, reviewed agreement that remains available through implementation and acceptance. Small, already understood tasks may omit it. | The task qualifies for the simple-edit exception, or a project provides an equivalent reviewed specification artifact. |
| **Always require a full plan:** apply [planning capabilities](https://code.visualstudio.com/docs/agents/run/planning) and an approved Markdown artifact to every edit, including already understood mechanical changes. | Gives every task the same audit trail and eliminates judgment about when to plan. | Adds discussion and documentation effort where there are no consequential choices. This can encourage perfunctory approval and distract from tasks that genuinely need reasoning. | Deliberate planning is valuable because it resolves uncertainty, not because every edit needs a document. The simple-edit exception preserves proportionate effort without bypassing necessary checks. | A repository or regulated process explicitly requires a plan artifact for every change. |
| **Manual Build and Test with AI suggestions:** the user implements and validates each step while using [AI assistance](https://code.visualstudio.com/docs/agents/overview) for focused suggestions. | Keeps hands-on control throughout execution and is useful when implementation itself is the learning objective. The user can investigate each change immediately. | Repetitive coding, test execution, and review remain user-managed rather than delegated. Attention can be spent on mechanical steps instead of consequential decisions. | The selected default deliberately automates Build and Test after alignment, while retaining human Verify and Observe. This does not prohibit choosing hands-on work when that is the goal. | Learning through implementation or a change's risk makes continuous human involvement more valuable than autonomous execution. |
| **Finish at automated Test:** a project-defined flow that treats successful [testing and validation](https://code.visualstudio.com/docs/agents/guides/overview#_test-and-validate) as the endpoint without a human Verify gate or final Observe. | Provides a simple, repeatable endpoint and avoids additional acceptance and follow-up effort. | Tests can miss mismatched intent, usability problems, and behavior that appears only in actual use. A passing suite is not evidence that the user accepts the result. | Human Verify establishes acceptance, and Observe closes the feedback loop after it. Neither can be replaced by declaring that automated checks passed. | For a change with little ongoing impact, observation can be lightweight; this does not remove the human acceptance gate. |

---

## Status

Accepted: retain Plan, Build, Test, and Observe, with required separate planning for larger or consequential work, autonomous implementation and testing within the agreed scope, and human verification before observation. Small, understood tasks may skip Plan; all implementation uses Implementation Orchestrator with SIMPLE or STANDARD execution. Installation, discovery, and runtime behavior remain host-dependent.

---

## Date

2026-11-13

---
# Changelog

- 2026-11-14: Kept planning and implementation as separate phases, clarified the small-task exception, integrated the plan-artifact and handoff contract, and mapped execution to the current agents and SIMPLE/STANDARD modes. Removed the separate plan/handoff and superseded skills-first records; Git history retains their earlier contents.

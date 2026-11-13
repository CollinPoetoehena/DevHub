---
name: planning
description: 'Creates evidence-based plans for explicitly requested or consequential work, including clarified requirements, bounded work packages, dependencies, and acceptance checks.'
---

TODO: integrate grill-me skill from Matt Pocock here later.

# Planning

The orchestrator remains the host's native active Agent; it invokes this planning skill and the implementation-orchestration skill as appropriate, using the host-selected model/router and Autopilot when supported. Use this procedure when the user explicitly requests a plan or the requested change is consequential enough to require structured planning. Ordinary, clear tasks do not require a plan.

## Workflow

1. **Frame the request.** Establish goals, context, scope, non-goals, constraints, and any known acceptance criteria. Inspect relevant code and project guidance before asking questions that repository evidence can answer. Ask focused questions about consequential unresolved requirements, design choices, and edge cases; record assumptions separately from facts.
2. **Investigate and design.** Use bounded, read-only native research or exploration when useful; return concise evidence and keep the planning context focused. Do not depend on custom architect agents or a particular interrogation skill. Ground recommendations in observed conventions and evidence. For significant architectural decisions, use the existing `adr` skill to shape a draft and describe its approval needs; do not create a separate ADR unless authorized.
3. **Decompose.** Define work packages with stable IDs, dependencies, file/write boundaries, observable acceptance criteria, and relevant test and review checks. Note risks, resolved and unresolved questions, and where independent work is safe to parallelize. Unresolved consequential questions block plan approval.
4. **Save only the plan.** Follow an established project plan location when one exists. Otherwise use `<task-working-directory>/tmp/plan-<unique-id>.md`, creating a new, non-overwriting file for the current plan. Do not change ignore rules. If writing is blocked or unauthorized, present the draft and the blocker. During planning, do not implement or edit project files; write only the explicitly authorized plan artifact.
5. **Request exact approval.** Present the saved path and contents for explicit human approval. Changes to approved contents require renewed approval. Implementation must begin in a fresh native session with the exact absolute plan path and explicit approval of its current version. Never infer approval or unchanged contents from a file's presence.

## Plan Contents

Include goals and context; scope and non-goals; constraints; evidence-based design; accepted assumptions; risks; resolved and unresolved questions; work packages and dependencies; observable acceptance criteria; test and review checks; and separate human **Verify** and **Observe** follow-up.

## Boundaries

This skill provides a procedure to the existing native agent; it does not switch agent mode, choose a model, alter permissions, or enforce approval. The host controls its mode, model/router, and available capabilities. Autopilot is not human approval. Do not commit, push, deploy, perform destructive actions, or imply that a plan is approved without the required human approval.

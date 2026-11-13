---
name: planning
description: 'Creates evidence-based plans when requested or when work is consequential. Investigates context, clarifies material decisions, and defines bounded work packages with dependencies and acceptance checks.'
---

# Planning

Create a plan when the user requests one or the work is consequential. When this skill is used, always clarify the decision tree until there is shared understanding and enough detail for a clear, actionable plan.

## When to Use This Skill

- The user asks for a plan.
- The requested work is consequential enough to need structured planning.

## Workflow

1. **Investigate:** Establish goals, scope, constraints, and acceptance criteria. Inspect relevant evidence before asking questions answerable by research.
2. **Clarify:** Map decisions as a tree. Ask the full answerable frontier each round; number each question and give a recommendation phrased so “yes” accepts it. Find facts yourself; delegate bounded lookups when needed, ask independent questions while they run, and defer only dependent questions. Recompute the frontier after each answer and continue until every branch is resolved and the user confirms shared understanding. Do not silently assume answers or move on with unresolved decisions.
3. **Decompose:** Turn the confirmed understanding into a clear, evidence-based plan. Define work packages with stable IDs, dependencies, file boundaries, observable acceptance criteria, tests, and review checks. Note risks and safe parallel work. This ensures the work can be executed efficiently and in parallel where safe with multiple subagents. For significant architecture, use the `adr` skill to shape a draft and identify approval needs; do not create an ADR unless authorized.
4. **Save only the plan:** Use the established plan location, or create a new `<task-working-directory>/tmp/plan-<unique-id>.md`. Do not change ignore rules or implement the plan. If writing is blocked, present the draft and blocker.
5. **Request approval:** Present the saved plan for explicit approval before implementation. Any change requires renewed approval. Implementation starts in a fresh native session using the exact absolute path and current approved plan; Autopilot is not approval.

## Plan Contents

Include goals, scope, constraints, evidence, assumptions, risks, unresolved questions, work packages, dependencies, acceptance criteria, tests, review checks, and human **Verify** and **Observe** follow-up.

## Boundaries

Use the host's native agent, model, and capabilities; this skill does not change them or permissions. Do not commit, push, deploy, or perform destructive actions during planning, or imply approval without it.

---
description: "Use when designing or maintaining AI customizations like agents, skills, prompts, and instruction files."
applyTo: "**/*.agent.md,**/*.instructions.md,**/*.prompt.md,**/SKILL.md,**/AGENTS.md,**/copilot-instructions.md"
---

# AI Customization Instructions

- **Official guidance first**: Use the host's official customization skill (such as `agent-customization` in VS Code) and documentation for file formats and frontmatter. The pinned upstream [agents](https://github.com/github/awesome-copilot/blob/main/instructions/agents.instructions.md) and [agent skills](https://github.com/github/awesome-copilot/blob/main/instructions/agent-skills.instructions.md) instructions supply general authoring rules; this file adds DevHub's design rules.
- **Right primitive**: Agents define roles, tools, and models; skills hold on-demand procedures; scoped instructions hold standards; repository `AGENTS.md` holds local facts. Keep standards out of agents and do not duplicate them across files.
- **Single role, concise**: One responsibility per agent with explicit boundaries. Prefer short rules and tables over prose.

## Deterministic Workflows

- **Closed outcome sets**: Every decision point returns exactly one value from a fixed list, such as `PASS | IMPLEMENTATION_CHANGES | PLAN_CHANGES`. Define when each value applies, using first-match-wins rules when conditions can overlap.
- **One action per outcome**: Map each outcome to exactly one next step in a transition table. Do not allow implicit, free-form, or "as appropriate" transitions.
- **Separate status from outcome**: Report execution status (`COMPLETE | NEEDS_INPUT | BLOCKED | FAILED`) separately from the workflow outcome, so a failed step cannot look like a success. Any status other than `COMPLETE` stops the flow.
- **Conservative default**: Routing tables evaluate top to bottom; uncertainty falls through to the most controlled route.
- **Bounded loops and gates**: Cap correction and revision cycles, then stop with the blocker and the decision needed. Require explicit user approval at consequential gates; findings, plans, and diagnoses do not authorize changes, commits, or pushes.
- **Least privilege**: Grant only the tools a role needs and restrict delegation with `agents` allowlists. Use `user-invocable: false` for workers and `disable-model-invocation: true` for entry points. Prose is guidance, not enforcement; use tools, hooks, or CI for hard requirements.

## Reporting and Traceability

- **Structured report**: Every agent ends with a fixed `## Report` block containing at least agent, model, status, outcome, reason, guidance read, actions or changes, evidence (exact commands and `PASSED | FAILED | SKIPPED | BLOCKED`), decisions, deviations, and open items.
- **Aggregated trace**: Coordinating agents collect every worker report and present the selected route with its reason, a step trace (agent, configured and reported model, status, outcome, summary), the full reports, and the final result. Condense only verbose logs; never drop findings, failures, deviations, or validation results.
- **Report deviations**: Surface any route change, retry, skipped step, or limit reached with its reason. Report only what was observed; write `unknown` rather than guessing.

## Model Selection

- **Pin per role**: Every agent declares a `model` fallback list in frontmatter suited to its role: strongest reasoning models for planning and architecture, fast reliable models for routing, strong coding models for implementation, and low-cost models for low-risk work such as documentation. Use a different model family for review than for implementation to reduce shared blind spots.
- **Single source**: Frontmatter is authoritative; coordinators do not override worker models at invocation. Keep any model registry table in a coordinator in sync with the frontmatter.
- **Verify availability**: Use model names exactly as shown in the host's model picker, verify them against the [supported models](https://docs.github.com/en/copilot/reference/ai-models/supported-models), and revisit the lists when models are retired.

## Validation

- Verify behavior with representative scenarios in the intended harness, covering each route, outcome, gate, and limit; file presence and installation do not prove discovery or compliance. Record harness-specific limitations in the owning README.

---
description: "Use when designing or maintaining AI customizations like agents, skills, prompts, and instruction files."
applyTo: "**/*.agent.md,**/*.instructions.md,**/*.prompt.md,**/SKILL.md,**/AGENTS.md,**/copilot-instructions.md"
---

# AI Customization Instructions

- **Official guidance first**: Use the host's official customization skill (such as `agent-customization` in VS Code) and documentation for file formats and frontmatter. The pinned upstream [agents](https://github.com/github/awesome-copilot/blob/main/instructions/agents.instructions.md) and [agent skills](https://github.com/github/awesome-copilot/blob/main/instructions/agent-skills.instructions.md) instructions supply general authoring rules; this file adds DevHub's design rules.
- **Right primitive**: Agents define roles, tools, and models; skills hold on-demand procedures; scoped instructions hold standards; repository `AGENTS.md` holds local facts. Keep standards out of agents and do not duplicate them across files.
- **Single role, concise**: One responsibility per agent with explicit boundaries. Prefer short rules and tables over prose.
- **Scannable steps**: Start every numbered step in agents and skills with a short bold label that states what the step does, followed by the details, such as `1. **Analyze requirements.** Restate the goal, ...`.

## Deterministic Workflows

- **Closed outcome sets**: Every decision point returns exactly one value from a fixed list, such as `PASS | IMPLEMENTATION_CHANGES | PLAN_CHANGES`. Define when each value applies, using first-match-wins rules when conditions can overlap.
- **One action per outcome**: Map each outcome to exactly one next step in a transition table. Do not allow implicit, free-form, or "as appropriate" transitions.
- **Separate status from outcome**: Report execution status (`COMPLETE | NEEDS_INPUT | BLOCKED | FAILED`) separately from the workflow outcome, so a failed step cannot look like a success. Any status other than `COMPLETE` stops the flow.
- **Conservative default**: Routing tables evaluate top to bottom; uncertainty falls through to the most controlled route.
- **Bounded loops and gates**: Cap correction and revision cycles, then stop with the blocker and the decision needed. Require explicit user approval at consequential gates; findings, plans, and diagnoses do not authorize changes, commits, or pushes.
- **Self-checks and proof**: Give agents a fixed check before they return a result, such as a plan check or a pre-finding gate, and require evidence proportional to impact, such as proof for blocking findings. Accept an empty result, such as zero findings, as valid.
- **Least privilege**: Prefer only the tools a role needs when the harness reliably exposes them. The common agents deliberately use explicit `tools: ['*']` as the compatibility exception documented in the [tools and permissions design](https://github.com/CollinPoetoehena/DevHub/blob/main/packages/apm/README.md#agent-tools-and-permissions); do not silently narrow it or extend that exception to other environments. Restrict delegation with `agents` allowlists where supported. Use `user-invocable: false` for workers and `disable-model-invocation: true` for entry points. Prose is guidance, not enforcement; use host permissions, hooks, or CI for hard requirements.

## Reporting and Traceability

- **Structured report**: Every agent ends with a fixed `## Report` block containing at least agent, model, status, outcome, reason, references, actions or changes, evidence (exact commands and `PASSED | FAILED | SKIPPED | BLOCKED`), decisions, deviations, and open items.
- **Explicit references**: Reports list the references actually used, grouped as instructions (including `AGENTS.md`), skills, files read, and external sources, with `none` for an empty group. Never list items that were not read or applied.
- **Aggregated trace**: Coordinating agents collect every worker report and present the selected route with its reason, a step trace (agent, configured and reported model, status, outcome, summary), a references table per step, the full reports, and the final result. Condense only verbose logs; never drop findings, failures, deviations, or validation results.
- **Report deviations**: Surface any route change, retry, skipped step, or limit reached with its reason. Report only what was observed; write `unknown` rather than guessing.
- **Learning step**: Workflows end with a lightweight learning step triggered only by defined signals, such as review findings, deviations, failed validation, or user corrections. Lessons need evidence and go into their single owner: repository-owned files for repository lessons, the package source (never installed copies) for shared lessons. Changes to safeguards are proposed, not applied.

## Model Selection

- **Pin per role**: Every agent declares a `model` fallback list in frontmatter suited to its role: strongest reasoning models for planning and architecture, fast reliable models for routing, strong coding models for implementation, and low-cost models for low-risk work such as documentation. Use a different model family for review than for implementation to reduce shared blind spots.
- **Single source**: Frontmatter is authoritative; coordinators do not override worker models at invocation. Keep any model registry table in a coordinator in sync with the frontmatter.
- **Verify availability**: Use model names exactly as shown in the host's model picker, verify them against the [supported models](https://docs.github.com/en/copilot/reference/ai-models/supported-models), and revisit the lists when models are retired.

## Validation

- Verify behavior with representative scenarios in the intended harness, covering each route, outcome, gate, and limit; file presence and installation do not prove discovery or compliance. Record harness-specific limitations in the owning README.

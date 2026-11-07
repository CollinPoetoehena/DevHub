---
description: "Use when designing or maintaining AI customizations like agents, skills, prompts, and instruction files."
applyTo: "**/*.agent.md,**/*.instructions.md,**/*.prompt.md,**/SKILL.md,**/AGENTS.md,**/copilot-instructions.md"
---

# AI Customization Instructions

- **Official guidance first**: Use the host's official customization skill (such as `agent-customization` in VS Code) and documentation for file formats and frontmatter. The pinned upstream [agents](https://github.com/github/awesome-copilot/blob/main/instructions/agents.instructions.md) and [agent skills](https://github.com/github/awesome-copilot/blob/main/instructions/agent-skills.instructions.md) instructions supply general authoring rules; this file adds DevHub's design rules.
- **Right primitive**: Agents define roles and tools; skills hold on-demand procedures; scoped instructions hold standards; repository `AGENTS.md` holds local facts. Keep standards out of agents and do not duplicate them across files.
- **Single role, concise**: One responsibility per agent with explicit boundaries. Prefer short rules and tables over prose.
- **Scannable steps**: Start every numbered step in agents and skills with a short bold label that states what the step does, followed by the details, such as `1. **Analyze requirements.** Restate the goal, ...`.

## Deterministic Workflows

- **Closed outcome sets**: Every decision point returns exactly one value from a fixed list, such as `PASS | IMPLEMENTATION_CHANGES | PLAN_CHANGES`. Define when each value applies, using first-match-wins rules when conditions can overlap.
- **One action per outcome**: Map each outcome to exactly one next step in a transition table. Do not allow implicit, free-form, or "as appropriate" transitions.
- **Separate status from outcome**: Report execution status (`COMPLETE | NEEDS_INPUT | BLOCKED | FAILED`) separately from the workflow outcome, so a failed step cannot look like a success. Any status other than `COMPLETE` stops the flow.
- **Conservative default**: Routing tables evaluate top to bottom; uncertainty falls through to the most controlled route.
- **Bounded loops and gates**: Cap correction and revision cycles, then stop with the blocker and the decision needed. Require explicit user approval at consequential gates; findings, plans, and diagnoses do not authorize changes, commits, or pushes.
- **Self-checks and proof**: Give agents a fixed check before they return a result, such as a plan check or a pre-finding gate, and require evidence proportional to impact, such as proof for blocking findings. Accept an empty result, such as zero findings, as valid.
- **Tool access and enforcement**: The common agents deliberately request all host-available tools with `tools: ['*']` and omit `model` declarations, as documented in the [agent configuration guidance](https://github.com/CollinPoetoehena/DevHub/blob/main/packages/apm/README.md#agent-configuration). Preserve this shared compatibility policy unless it is deliberately revisited; do not treat tool selection as a guarantee of tool availability or as an approval boundary. Restrict delegation with `agents` allowlists where supported. Use `user-invocable: false` for workers and `disable-model-invocation: true` for entry points. Prose is guidance, not enforcement; use host permissions, hooks, or CI for hard requirements.

## Reporting and Traceability

- **Structured report**: Every agent ends with a fixed `## Report` block containing at least agent, tools actually used, status, outcome, reason, references, actions or changes, evidence (exact commands and `PASSED | FAILED | SKIPPED | BLOCKED`), decisions, deviations, and open items.
- **Explicit references**: Reports list the references actually used, grouped as instructions (including `AGENTS.md`), skills, files read, and external sources, with `none` for an empty group. Never list items that were not read or applied.
- **Aggregated trace**: Coordinating agents collect every worker report and present the selected route with its reason, a step trace (agent, tools actually used, status, outcome, summary), a references table per step, the full reports, and the final result. Condense only verbose logs; never drop findings, failures, deviations, or validation results. Report tool usage from observed calls, not from configured or available tools.
- **Report deviations**: Surface any route change, retry, skipped step, or limit reached with its reason. Report only what was observed; write `unknown` rather than guessing.
- **Learning step**: Workflows end with a lightweight learning step triggered only by defined signals, such as review findings, deviations, failed validation, or user corrections. Lessons need evidence and go into their single owner: repository-owned files for repository lessons, the package source (never installed copies) for shared lessons. Changes to safeguards are proposed, not applied.

## Model selection

- **Runtime-managed**: Common agents omit `model` declarations and coordinators do not pass model overrides. Follow the [APM guide's runtime-managed model-selection guidance](https://github.com/CollinPoetoehena/DevHub/blob/main/packages/apm/README.md#runtime-managed-model-selection) when discussing model choice.
- **Review independence**: A fresh context and independent assessment role reduce shared blind spots; do not claim that review uses a different model family unless that is observed and relevant to the specific run.

## Validation

- Verify behavior with representative scenarios in the intended harness, covering each route, outcome, gate, and limit; file presence and installation do not prove discovery or compliance. Record harness-specific limitations in the owning README.

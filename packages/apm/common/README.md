# DevHub Common Agent Package

`devhub-common` distributes reusable engineering agents, instructions, and skills through [APM](https://microsoft.github.io/apm/). [`.apm/`](.apm/) is the authoring source; [`apm.yml`](apm.yml) declares pinned upstream dependencies.

The [APM overview](../README.md) owns shared setup, authoring, and usage. This README describes the package contents, the Orchestrator workflow, and its limits.

## Table of Contents

- [Package contents](#package-contents)
- [Reuse registry](#reuse-registry)
- [Workflow](#workflow)
  - [Routing](#routing)
  - [Outcomes and transitions](#outcomes-and-transitions)
  - [Learning](#learning)
  - [Commit](#commit)
  - [Reports and trace](#reports-and-trace)
  - [Model selection](#model-selection)
- [Harness limitations](#harness-limitations)
- [Consumption and validation](#consumption-and-validation)

---

## Package contents

| Agent | Responsibility |
|---|---|
| [Orchestrator](.apm/agents/orchestrator.agent.md) | Explicitly selected coordinator for a fresh implementation session using an approved plan |
| [Implementer](.apm/agents/implementer.agent.md) | Scoped code, configuration, or documentation implementation and validation |
| [Architect](.apm/agents/architect.agent.md) | Optional design advice for exceptionally large tasks, subject to user approval |

Agents omit `model`, request `tools: ['*']`, and prefer native file editing over long shell edits to reduce approval prompts. Tool access does not override permissions. Workers set `user-invocable: false`; Orchestrator is the entry point when the user selects this workflow.

Common instructions cover [AI customization](.apm/instructions/ai-customization.instructions.md), [coding](.apm/instructions/coding.instructions.md), [documentation](.apm/instructions/documentation.instructions.md), [Git](.apm/instructions/git.instructions.md), [security](.apm/instructions/security.instructions.md), [testing](.apm/instructions/testing.instructions.md), and [GitHub Actions](.apm/instructions/github-actions.instructions.md). The [code-comments](.apm/skills/code-comments/SKILL.md) and [draft-github-issue](.apm/skills/draft-github-issue/SKILL.md) skills remain available. Opt-in [stack packages](../README.md#package-design) refine shared standards.

---

## Workflow

Use native Agent mode for ordinary tasks. For larger tasks, the user interactively plans and approves a written contract, saves an exact non-overwriting working-directory `tmp/plan-<id>.md` copy, then starts a fresh session with Orchestrator and explicitly confirms approval of that exact path. See the [handoff example and storage guidance](../README.md#choosing-a-workflow).

Orchestrator stops on missing, stale, changed, ambiguous, or unapproved plans; it does not infer approval from a file. It delegates dependency-aware packages, permits concurrent writes only with confirmed independence and isolation, preserves existing changes, and integrates and validates the result. It pauses for explicit approval of each optional Architect output; a material change also needs a revised, approved plan.

The integrated result requires applicable checks plus independent native code and security reviews. Findings that block completion return to implementers and the corrected result is re-reviewed. Unavailable or failed required checks or reviews are blockers, not successful substitutes.

### Model selection

No agent specifies a model and no invocation overrides one. The host chooses according to its own rules; the user selects Auto where offered. Delegated task size, risk, and cost intent are advisory and do not guarantee a model, price, or reviewer independence. See [runtime-managed model selection](../README.md#runtime-managed-model-selection).

---

## Harness limitations

The package targets the Copilot harness. VS Code distinguishes the Copilot harness's native `task` tool from Local's `runSubagent`; tools, delegation, model inheritance, and frontmatter support vary. `agents` allowlists are retained for harnesses that honor them, not claimed as Copilot enforcement. Wildcard tool access and instructions are not permission or approval boundaries.

Native planning and reviews are host capabilities, not custom skills or slash commands invoked by these agent files. Where agent-initiated native review is unavailable, the workflow reports a blocker; the user may run a supported native review and supply its result. Separate context supports independent assessment but does not guarantee different models. Installing a file does not establish discovery or actual behavior.

---

## Consumption and validation

Consumers use `CollinPoetoehena/DevHub/packages/apm/common`; DevHub's [root manifest](../../../apm.yml) also includes the local source. Follow [repository setup](../README.md#repository-setup) and [validation](../README.md#validation). Validate this source with `apm compile --validate --local-only`.

In fresh sessions, verify: ordinary work uses native Agent; `/plan` clarifies consequential ambiguity without implementing; the approved exact copy is not overwritten; missing, changed, ambiguous, and unapproved plans stop; scoped tasks respect dependencies and write isolation; Architect output waits for approval; and changes outside the contract stop. Confirm applicable checks and both native reviews actually run, blocking findings are corrected and re-reviewed, and unavailable capabilities are reported. Test CLI and VS Code Copilot harness separately; record what could not be exercised.

Version 2 replaces the previous routed specialist workflow. Reinstall and inspect managed deployment and stale artifacts using the documented [maintenance procedure](../README.md#maintenance-and-validation); preserve consumer-owned files. Source edits alone do not update installed copies or existing sessions.

---

## Reuse registry

The [manifest](apm.yml) pins individual awesome-copilot components at `60dcb90`: authoring instructions for agents, skills, instructions, prompts, and hooks; `create-agentsmd`, `acquire-codebase-knowledge`, and `git-commit` skills; and prompt-safety and DevOps instructions. These are upstream dependencies, not copies owned by this package.

The Architect's current design advice retains ideas from [ECC's architect](https://github.com/affaan-m/ECC/blob/main/agents/architect.md), simplified to options, trade-offs, and a recommendation. The [security instructions](.apm/instructions/security.instructions.md) adapt ideas from [ECC's security reviewer](https://github.com/affaan-m/ECC/blob/main/agents/security-reviewer.md) and [security-review skill](https://github.com/affaan-m/ECC/blob/main/skills/security-review/SKILL.md): secure defaults, review patterns, false positives, negative tests, and exposed-secret response. The retired Planner, Reviewer, and workflow-learning adaptations are recorded in [the changelog](CHANGELOG.md) and Git history, not retained as active copies.

[Matt Pocock's skills repository](https://github.com/mattpocock/skills/tree/main) is another useful reference for skill examples.

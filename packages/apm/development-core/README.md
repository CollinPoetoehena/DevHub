# DevHub Local Development Core

`devhub-development-core` distributes local workflow agents and skills through [APM](https://microsoft.github.io/apm/). [`.apm/`](.apm/) is the authoring source; [`apm.yml`](apm.yml) declares pinned upstream skill dependencies. Shared repository standards live separately in [`guidelines-core`](../guidelines-core/README.md); consumers may adopt those guidelines without this local development package.

The [APM overview](../README.md) owns package selection, setup, authoring, and usage. This README describes the local development contents and their limits.

This package contains both workflow skills and only the Implementer in [the agents directory](.apm/agents/), following the [skills-first ADR](../adrs/workflow/REUSABLE-WORKFLOWS-AS-SKILLS.md). Package source readiness does not establish installation, host discovery, or behavior.

## Table of Contents

- [Package contents](#package-contents)
- [Reuse registry](#reuse-registry)
- [Workflow](#workflow)
  - [Model selection](#model-selection)
- [Harness limitations](#harness-limitations)
- [Consumption and validation](#consumption-and-validation)

---

## Package contents

| Customization | Responsibility |
|---|---|
| [Planning skill](.apm/skills/planning/SKILL.md) | Interactive investigation, consequential clarification, dependency-aware plan, saved artifact, and explicit approval; no implementation |
| [Implementation-orchestration skill](.apm/skills/implementation-orchestration/SKILL.md) | Approved-plan execution, bounded Implementer assignments, integration, checks, independent reviews, and evidence |
| [Implementer agent](.apm/agents/implementer.agent.md) | Senior engineer implementing assigned work with behavior-focused red-green-refactor, directly related documentation, and validation; no subagents |
| [ADR skill](.apm/skills/adr/SKILL.md) | Significant decision records following the owning project's conventions |
| [Draft GitHub issue skill](.apm/skills/draft-github-issue/SKILL.md) | Reviewable issue drafts using repository conventions |

Planning and orchestration are procedures loaded by the current native agent, not roles requiring custom-agent selection. The host's active built-in agent, such as GitHub Copilot Agent mode, invokes either skill and coordinates its procedure using available tools and subagents. The user retains the selected model/router and permission mode, for example Autopilot where supported. The skills do not change those settings or waive human planning approval.

Skills compose and evolve independently and use the open skill format recognized by supporting tools and registries. Keep generic research, exploration, and review roles native where supported rather than maintaining an agent for every worker. Only the Implementer's specific no-subdelegation and test-first contract justifies a custom role. Its minimal name/description metadata omits model, tool, and visibility settings; actual availability and permissions remain host-controlled.

This package does not contain shared engineering instructions. Those live in the independent [`guidelines-core`](../guidelines-core/README.md) package. Opt-in `development-*` stack packages contain their own scoped instruction maps beside technology skills and references.

---

## Workflow

For simple, clear work, make an ordinary request to the native Agent. It uses applicable guidance and checks directly; neither workflow skill nor forced Implementer delegation is required. For larger work, invoke Planning to investigate evidence, clarify consequential choices, and save a plan. Review and approve the exact version, then start a fresh native Agent session for Implementation Orchestration with that plan path and explicit approval. See [invocation and storage examples](../README.md#choosing-a-workflow).

The skills own their procedures rather than duplicating them here. Planning must not implement or modify project files beyond an authorized plan artifact. Implementation Orchestration stops on missing, stale, changed, ambiguous, or unapproved plans; it does not infer approval from file presence. Routine decisions stay autonomous; material requirements, architecture, dependency, security, or scope changes need a revised approved plan.

Coordination uses dependency-aware, bounded work packages and safe write ownership; one Implementer is enough for sequential work. Parallel subagents or a host's fleet mechanism are optional only when tasks are genuinely independent and the mechanism is available. Built-in exploration returns concise evidence; use unique task-scoped notes in an authorized location when persistence is needed, not a shared global scratch path.

Orchestration coordinates dependency-aware, bounded Implementer work, integration checks, independent native code and security reviews, remediation, and truthful reporting. Findings that block completion return to implementers and the corrected result is re-reviewed. Unavailable or failed required checks or reviews are blockers, not successful substitutes. The user verifies and accepts the integrated outcome.

### Model selection

No agent specifies a model and no invocation overrides one. The host chooses according to its own rules; the user selects Auto where offered. Delegated task size, risk, and cost intent are advisory and do not guarantee a model, price, or reviewer independence. See [runtime-managed model selection](../README.md#runtime-managed-model-selection).

---

## Harness limitations

The package targets Copilot, while the skill instructions avoid host-specific tool catalogs. Skill descriptions support discovery; supporting hosts may expose them as slash commands. [VS Code's skill documentation](https://code.visualstudio.com/docs/agent-customization/agent-skills#_use-skills-as-slash-commands) describes its `/` menu. Other hosts may use different invocation and discovery mechanisms. Loading a skill is not switching agent modes. Omitted tool metadata and prose are not permission or approval boundaries.

These skills do not call native `/plan`, `/research`, or review slash commands internally. Native planning, research, and reviews remain separate host capabilities. Where required Implementer delegation or native review is unavailable, report a blocker; the user may supply a supported independent native review result for the current integrated change. Separate context supports independent assessment but does not guarantee different models. Installing a file does not establish discovery or actual behavior.

---

## Consumption and validation

Users who choose this workflow consume `CollinPoetoehena/DevHub/packages/apm/development-core`, optionally alongside relevant stack packages. Repositories separately choose whether to adopt [`guidelines-core`](../guidelines-core/README.md). DevHub's [root manifest](../../../apm.yml) selects only the local guidelines package. Follow [repository setup](../README.md#repository-setup) and [validation](../README.md#validation). Validate this source with `apm compile --validate --local-only`.

In fresh sessions, verify: ordinary work uses native Agent; Planning clarifies consequential ambiguity without implementing; existing plan filenames are not overwritten; a fresh execution session receives the exact plan path and explicit current-version approval; missing, stale, changed, ambiguous, and unapproved plans stop; direct large requests without plans return to planning; scoped tasks respect dependencies and write isolation; and material changes stop. For testable behavior changes, confirm focused red-green-refactor and regression checks; documentation-only assignments must not manufacture code tests. Confirm applicable checks and both native reviews actually run, blocking findings are corrected by a fresh Implementer and re-reviewed, and unavailable capabilities are reported. Test CLI and VS Code separately; static checks do not prove host behavior.

Source validation does not install or activate this package, establish supported host discovery, synchronize local copies, or change consumer-owned setup. Verify behavior in the intended host and scope. The [ADR index](../adrs/README.md) records current decisions; the [overview](../README.md) distinguishes ready package sources from deferred installation, discovery, and synchronization.

---

## Reuse registry

The [manifest](apm.yml) pins the `create-agentsmd`, `acquire-codebase-knowledge`, and `git-commit` skills from awesome-copilot at `60dcb90`. Shared authoring instructions, prompt-safety guidance, and DevOps principles belong to the separate [`guidelines-core`](../guidelines-core/README.md) package.

The planning and coordination design takes inspiration from the questioning and specification-implementation patterns referenced in [Matt Pocock's skills](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me). These are original, focused DevHub procedures, not vendored upstream content or implicit dependencies on a `grill-me` skill.

The [shared security guidelines](../guidelines-core/.apm/instructions/security.instructions.md) retain their documented adaptation of [ECC security-review ideas](https://github.com/affaan-m/ECC/blob/main/skills/security-review/SKILL.md). Historical planner, coordinator, architect, reviewer, and learning approaches remain in [the changelog](CHANGELOG.md) and Git history, not active source copies.

[Matt Pocock's skills repository](https://github.com/mattpocock/skills/tree/main) is another useful reference for skill examples.

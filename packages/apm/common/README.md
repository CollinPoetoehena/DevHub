# DevHub Common Agent Package

`devhub-common` distributes reusable engineering agents, instructions, and skills through [APM](https://microsoft.github.io/apm/). [`.apm/`](.apm/) is the authoring source; [`apm.yml`](apm.yml) declares pinned upstream dependencies.

The [APM overview](../README.md) owns shared setup, authoring, and usage. This README describes the package contents, the Orchestrator workflow, and its limits.

## Table of Contents

- [Package contents](#package-contents)
- [Reuse registry](#reuse-registry)
- [Workflow](#workflow)
  - [Routing](#routing)
  - [Outcomes and transitions](#outcomes-and-transitions)
  - [Commit](#commit)
  - [Reports and trace](#reports-and-trace)
  - [Models](#models)
- [Harness limitations](#harness-limitations)
- [Consumption and validation](#consumption-and-validation)

---

## Package contents

| Agent | Responsibility | Tools |
|---|---|---|
| [Orchestrator](.apm/agents/orchestrator.agent.md) | Entry point: routes, sequences, obtains approvals, reports the trace | read, search, agent, todo |
| [Planner](.apm/agents/planner.agent.md) | Requirements, approach, steps, acceptance criteria, validation | read, search, web |
| [Architect](.apm/agents/architect.agent.md) | Consequential design decisions with trade-offs | read, search, web |
| [Engineer](.apm/agents/engineer.agent.md) | Implementation, diagnosis, validation | read, search, edit, execute, web, todo |
| [Documenter](.apm/agents/documenter.agent.md) | Documentation-only changes, fact-checked against the code | read, search, edit, web |
| [Reviewer](.apm/agents/reviewer.agent.md) | Independent, evidence-based review without edits | read, search |

Only Orchestrator appears in the agent picker; the workers set `user-invocable: false`.

Instructions:

- [AI customization](.apm/instructions/common/ai-customization.instructions.md): deterministic workflow, reporting, and model-selection rules for authoring customizations.
- [Coding](.apm/instructions/common/coding.instructions.md), [documentation](.apm/instructions/common/documentation.instructions.md), and [Git](.apm/instructions/common/git.instructions.md): shared engineering standards.
- [Ansible](.apm/instructions/ansible.instructions.md), [Dockerfile](.apm/instructions/dockerfile.instructions.md), [GitHub Actions](.apm/instructions/github-actions.instructions.md), and [Python](.apm/instructions/python.instructions.md): scoped technology constraints.

Skills:

- [code-comments](.apm/skills/code-comments/SKILL.md): decides whether comments are warranted and writes, trims, or removes them; linked from the [coding instructions](.apm/instructions/common/coding.instructions.md#comments).
- [draft-github-issue](.apm/skills/draft-github-issue/SKILL.md): drafts issues without publishing or implementing them.

Reused upstream parts are listed in the [reuse registry](#reuse-registry).

---

## Reuse registry

Reused parts and their local changes, following the [reuse approach](../README.md#reuse-registry). Dependencies are declared in [`apm.yml`](apm.yml); adapted parts live in [`.apm/`](.apm/).

> Placeholder: complete this registry, including adapted parts and their local changes.

| Part | Source | Type | Local changes |
|---|---|---|---|
| `git-commit` skill | [awesome-copilot](https://github.com/github/awesome-copilot/tree/60dcb90/skills/git-commit) at `60dcb90` | Dependency | None |
| `agents` instructions | [awesome-copilot](https://github.com/github/awesome-copilot/blob/60dcb90/instructions/agents.instructions.md) at `60dcb90` | Dependency | None |
| `agent-skills` instructions | [awesome-copilot](https://github.com/github/awesome-copilot/blob/60dcb90/instructions/agent-skills.instructions.md) at `60dcb90` | Dependency | None |

---

## Workflow

The Orchestrator owns routing and approvals, Planner owns the approach, Architect owns consequential design decisions, Engineer and Documenter own delivery, and Reviewer owns assessment. Workers run as subagents and return to the Orchestrator, which stays the active conversation so it can ask questions, obtain approval, and consolidate results.

```text
User -> Orchestrator
          +-- R0 COMMIT         -> Engineer (COMMIT, git-commit skill) -> stop
          +-- R1 ANSWER         -> answer (Engineer DIAGNOSE if commands are needed)
          +-- R2 REVIEW         -> Reviewer -> findings, stop
          +-- R3 DIRECT_DOCS    -> Documenter -> done
          +-- R4 DIRECT_CHANGE  -> Engineer -> Reviewer
          +-- R5 PLANNED        -> Planner (-> Architect -> Planner)
                                     -> user approval -> Engineer or Documenter -> Reviewer

Reviewer: PASS -> done | IMPLEMENTATION_CHANGES -> same implementer | PLAN_CHANGES -> Planner
```

### Routing

The [Orchestrator routing table](.apm/agents/orchestrator.agent.md#routing-table) is evaluated top to bottom and the first match wins. A rule matches only when its condition clearly holds, so uncertainty falls through to `R5 PLANNED`. Documentation that defines future behavior, such as an ADR or proposed contract, is planning rather than documentation maintenance. Review-only, diagnosis-only, and plan-only requests never start implementation. Under R5, Documenter implements plans that change only documentation; Engineer implements all others, including documentation coupled to its changes.

### Outcomes and transitions

Each worker returns an execution status (`COMPLETE | NEEDS_INPUT | BLOCKED | FAILED`) and, when complete, exactly one outcome from a closed set. Each outcome maps to exactly one next step in the [transition table](.apm/agents/orchestrator.agent.md#transitions).

| Agent | Outcomes |
|---|---|
| Planner | `PLAN_READY`, `ARCHITECTURE_REQUIRED` |
| Architect | `DESIGN_READY` |
| Engineer | `IMPLEMENTED`, `DIAGNOSED`, `PLAN_CHANGES`, `COMMITTED` |
| Documenter | `DOCUMENTED`, `ENGINEERING_REQUIRED` |
| Reviewer | `PASS`, `IMPLEMENTATION_CHANGES`, `PLAN_CHANGES` |

Architect is invoked by the Orchestrator when Planner returns `ARCHITECTURE_REQUIRED`, rather than by Planner itself, so a single coordinator owns every transition and the trace and the workflow does not depend on nested subagent support. Documenter returns `ENGINEERING_REQUIRED` when documentation needs code changes or command-based verification; R3 then re-routes to R4, or R5 when R4 conditions do not hold, as a reported deviation. A plan requires explicit user approval before implementation, also after a revision. Correction cycles and plan revisions are each limited to two; reaching a limit stops the route as `BLOCKED` with the decision needed.

### Commit

A completed route that changed files ends with a copy-ready `/git-commit` command for the pinned [`git-commit`](https://github.com/github/awesome-copilot/tree/main/skills/git-commit) skill. It lists only the paths workers changed, uses one command per logical change, and carries a Conventional Commits message without `Co-authored-by:` trailers, as required by the [Git instructions](.apm/instructions/common/git.instructions.md). It is suggested only after review returned `PASS` or when the route requires no review.

The suggestion is not authorization. When the user explicitly authorizes the commit, rule `R0 COMMIT` delegates it to Engineer, which runs the skill, because Orchestrator has no terminal access. The user can also run the command in a chat whose agent has terminal access. Pushing is never part of the workflow and requires its own explicit authorization.

### Reports and trace

Every worker ends with a fixed `## Report` block: agent, model, status, outcome, reason, guidance read, changes or findings, validation evidence, decisions, deviations, and open items. The Orchestrator includes every report in full and adds the selected route with its reason, a step trace with the configured and reported model per step, and a result summary of changes, validation, review, deviations, and next decisions.

### Models

Each agent pins a role-specific `model` fallback list in its frontmatter; the first available model is used. Orchestrator does not override worker models, and its [agent registry](.apm/agents/orchestrator.agent.md#agent-registry) must stay in sync with the frontmatter.

| Agent | Models | Rationale |
|---|---|---|
| Orchestrator | Claude Sonnet 5.5, GPT-6.1 Terra | Reliable, fast classification and coordination |
| Planner, Architect | Claude Opus 5.5, GPT-6.1 Sol | Strongest reasoning for consequential decisions |
| Engineer | Claude Sonnet 5.5, GPT-5.3-Codex | Strong agentic coding; GPT-5.3-Codex is the long-term support fallback |
| Documenter | Claude Haiku 5.5, GPT-5.4 nano | Low-cost models for low-risk documentation work |
| Reviewer | GPT-6.1 Sol, Claude Opus 5.5 | A different model family from Engineer to reduce shared blind spots |

Names follow the [supported models](https://docs.github.com/en/copilot/reference/ai-models/supported-models) list. Verify them in the model picker and update the frontmatter and registry together when models are retired. The trace reports a model as `unknown` when the runtime does not expose it to the agent.

---

## Harness limitations

- The workflow targets the **Copilot** harness, selected as the session target in VS Code Chat. Copilot delegates to custom agents through its native `task` tool, enabled by the `agent` tool alias. See [Copilot subagents](https://code.visualstudio.com/docs/agents/run/subagents#_subagents-by-harness) and [Copilot custom agents](https://docs.github.com/en/copilot/reference/custom-agents-configuration).
- Copilot honors the `model` fallback lists, `user-invocable`, and `disable-model-invocation`. It does not accept the `agents` allowlist or handoffs, so the agent files keep `agents` only for the Local harness, and in Copilot the Orchestrator's delegation is restricted by its instructions and the workers' descriptions, not by an allowlist. See [harness compatibility](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference#_harness-compatibility).
- Workers start in a fresh context, so the Orchestrator passes guidance paths and prior results explicitly. Workers never ask the user directly; they return `NEEDS_INPUT` and the Orchestrator asks, which keeps approvals and the trace in one conversation.
- Routing tables, outcomes, and reports are instructions to the model, not an execution engine. Tool restrictions limit capabilities; `execute` is not a sandbox. Hard enforcement of transitions or approvals requires hooks, permissions, or a dedicated controller.

---

## Consumption and validation

Consumers identify this package as `CollinPoetoehena/DevHub/packages/apm/common`; DevHub's root [`apm.yml`](../../../apm.yml) uses `./packages/apm/common`. Follow the [repository setup](../README.md#repository-setup) and [validation procedure](../README.md#validation).

Validate sources with `apm compile --validate --local-only` from this directory. After reinstalling, start a fresh chat and repeat representative scenarios:

| Scenario | Expected behavior |
|---|---|
| Explain a function | R1; no edits |
| Review the current changes | R2; findings reported, no edits |
| Fix a README typo | R3; Documenter only |
| Document behavior that needs a command to verify | Documenter returns `ENGINEERING_REQUIRED`; re-routed to R4 or R5 as a reported deviation |
| Approved ADR-only plan | R5; Documenter, then Reviewer |
| Localized bug with a known test | R4; Engineer, then Reviewer |
| Proposed deployment ADR or cross-cutting change | R5; plan presented, implementation waits for approval |
| Plan needs a design decision | Architect, then Planner |
| Reviewer finds a defect | Correction by the same implementer, then renewed review |
| Engineer needs an unapproved design change | `PLAN_CHANGES`; replanning and approval |
| Validation fails or a limit is reached | No completion claim; `BLOCKED` or `FAILED` reported |
| Any route | Final response contains route, trace with models, and every agent report |
| Completed route with changes | Ends with a `/git-commit` command for only the changed paths; nothing is committed |
| User authorizes the commit | R0; Engineer commits via `git-commit` and reports the hash; no push |

Source edits do not update deployed customizations or running sessions.

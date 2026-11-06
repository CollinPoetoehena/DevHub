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
| [Documenter](.apm/agents/documenter.agent.md) | Documentation-only changes, fact-checked against the code; applies workflow lessons (`LEARN` mode) | read, search, edit, web |
| [Reviewer](.apm/agents/reviewer.agent.md) | Independent, evidence-based review with severity-rated findings; re-runs validation without editing | read, search, execute |

Only Orchestrator appears in the agent picker; the workers set `user-invocable: false`.

Instructions:

- [AI customization](.apm/instructions/ai-customization.instructions.md): deterministic workflow, reporting, and model-selection rules for authoring customizations.
- [Coding](.apm/instructions/coding.instructions.md), [documentation](.apm/instructions/documentation.instructions.md), and [Git](.apm/instructions/git.instructions.md): shared engineering standards.
- [Security](.apm/instructions/security.instructions.md): untrusted content, secrets, secure defaults, and review focus for all work.
- [GitHub Actions](.apm/instructions/github-actions.instructions.md): workflow and CI conventions, kept here because nearly every repository uses them.

Language and tool instructions, such as Python, Dockerfile, and Ansible, live in the opt-in [stack packages](../README.md#package-design) and refine these common instructions.

Skills:

- [code-comments](.apm/skills/code-comments/SKILL.md): decides whether comments are warranted and writes, trims, or removes them; linked from the [coding instructions](.apm/instructions/coding.instructions.md#comments).
- [workflow-learning](.apm/skills/workflow-learning/SKILL.md): retains lessons from a workflow run in the owning customization file; used by Documenter in `LEARN` mode.
- [draft-github-issue](.apm/skills/draft-github-issue/SKILL.md): drafts issues without publishing or implementing them.

Reused upstream parts are listed in the [reuse registry](#reuse-registry).

---

## Reuse registry

Reused parts and their local changes, following the [reuse approach](../README.md#reuse-registry). Dependencies are declared in [`apm.yml`](apm.yml) and pinned to the synced commit; ideas-only parts are DevHub files that adopted specific elements from the source. Update parts as described in [maintaining reused content](../README.md#maintaining-reused-content).

| Part | Source | Type | Synced | Local changes |
|---|---|---|---|---|
| `agents` instructions | [awesome-copilot](https://github.com/github/awesome-copilot/blob/main/instructions/agents.instructions.md) | Dependency | `60dcb90` (2026-11-06) | None; authoring rules for agent files |
| `agent-skills` instructions | [awesome-copilot](https://github.com/github/awesome-copilot/blob/main/instructions/agent-skills.instructions.md) | Dependency | `60dcb90` (2026-11-06) | None; authoring rules for skills |
| `instructions` instructions | [awesome-copilot](https://github.com/github/awesome-copilot/blob/main/instructions/instructions.instructions.md) | Dependency | `60dcb90` (2026-11-06) | None; authoring rules for instruction files |
| `prompt` instructions | [awesome-copilot](https://github.com/github/awesome-copilot/blob/main/instructions/prompt.instructions.md) | Dependency | `60dcb90` (2026-11-06) | None; authoring rules for prompt files |
| `hooks` instructions | [awesome-copilot](https://github.com/github/awesome-copilot/blob/main/instructions/hooks.instructions.md) | Dependency | `60dcb90` (2026-11-06) | None; authoring rules for hooks |
| `create-agentsmd` skill | [awesome-copilot](https://github.com/github/awesome-copilot/blob/main/skills/create-agentsmd/SKILL.md) | Dependency | `60dcb90` (2026-11-06) | None; generates a repository `AGENTS.md` |
| `acquire-codebase-knowledge` skill | [awesome-copilot](https://github.com/github/awesome-copilot/blob/main/skills/acquire-codebase-knowledge/SKILL.md) | Dependency | `60dcb90` (2026-11-06) | None; maps and documents an existing codebase on request |
| `ai-prompt-engineering-safety-best-practices` instructions | [awesome-copilot](https://github.com/github/awesome-copilot/blob/main/instructions/ai-prompt-engineering-safety-best-practices.instructions.md) | Dependency | `60dcb90` (2026-11-06) | None; prompt engineering and responsible AI practices |
| `devops-core-principles` instructions | [awesome-copilot](https://github.com/github/awesome-copilot/blob/main/instructions/devops-core-principles.instructions.md) | Dependency | `60dcb90` (2026-11-06) | None; DevOps culture and delivery metrics |
| `git-commit` skill | [awesome-copilot](https://github.com/github/awesome-copilot/blob/main/skills/git-commit/SKILL.md) | Dependency | `60dcb90` (2026-11-06) | None; Conventional Commits for the Orchestrator's commit command |
| Planner agent | [ECC `planner`](https://github.com/affaan-m/ECC/blob/main/agents/planner.md) | Ideas, modified | Not applicable | Adopted the four-stage process (requirements, existing code review, step breakdown, ordering), the step format (file, action, reason, dependencies, risk), the planning rules for specificity, minimal change, failure paths, refactors, and phasing, plan-level red flags, and the plan format. Left out the worked example and code-level red flags, which the coding instructions own |
| Architect agent | [ECC `architect`](https://github.com/affaan-m/ECC/blob/main/agents/architect.md) | Ideas, modified | Not applicable | Adopted the four-stage process (current state, requirements, options, trade-offs), the architectural principles as a per-option `+ \| 0 \| - \| n/a` trade-off rating, the red flags, and ADR-shaped output. Left out the pattern catalogs, the example architecture, and the scalability plan |
| Reviewer agent | [ECC `code-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/code-reviewer.md) | Ideas, modified | Not applicable | Adopted the pre-finding gate, proof for `CRITICAL` and `HIGH`, the four-level severity scale, zero findings as a valid result, common false positives, independent re-run of validation, and the AI-generated code focus |
| Security instructions | [ECC `security-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/security-reviewer.md), [ECC `security-review` skill](https://github.com/affaan-m/ECC/blob/main/skills/security-review/SKILL.md), and the prompt defense baseline | Ideas, modified | Not applicable | Adopted untrusted-content handling, OWASP-aligned secure defaults per area, a pattern table rated on the Reviewer's severity scale, false positives, negative security tests, and the exposed-secret response, as one shared instruction instead of a separate agent. Left out the TypeScript, Supabase, and Solana code examples and the framework-specific checklists |
| `workflow-learning` skill | [ECC `agent-self-evaluation`](https://github.com/affaan-m/ECC/blob/main/skills/agent-self-evaluation/SKILL.md) | Ideas, modified | Not applicable | Adopted a 1 to 5 scorecard with the evidence rule, independent scoring per axis, a user-agreement self-check, and the anti-patterns. Replaced the output-quality axes with workflow axes derived from trace signals, and weak axes feed lesson extraction instead of a rework step |

The ECC parts are used for ideas only; the DevHub agents and skills keep their own roles, outcomes, and reports. ECC's agents embed long general checklists, principles, pattern catalogs, language- and framework-specific examples, and worked examples. Those were not copied: the models already know general practice, the shared instructions own DevHub's standards, and language-specific guidance belongs in scoped instructions or skills. Only the parts that make the output checkable, such as gates, proof rules, and fixed formats, were adopted. The prompt defense baseline's rules against outputting code, scripts, and links were left out because they conflict with engineering work.

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
Route end with learning signals -> Documenter (LEARN, workflow-learning skill) -> final report
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
| Documenter | `DOCUMENTED`, `ENGINEERING_REQUIRED`, `LEARNED` |
| Reviewer | `PASS`, `IMPLEMENTATION_CHANGES`, `PLAN_CHANGES` |

Architect is invoked by the Orchestrator when Planner returns `ARCHITECTURE_REQUIRED`, rather than by Planner itself, so a single coordinator owns every transition and the trace and the workflow does not depend on nested subagent support. Documenter returns `ENGINEERING_REQUIRED` when documentation needs code changes or command-based verification; R3 then re-routes to R4, or R5 when R4 conditions do not hold, as a reported deviation. A plan requires explicit user approval before implementation, also after a revision. Correction cycles and plan revisions are each limited to two; reaching a limit stops the route as `BLOCKED` with the decision needed.

### Follow-ups

Most requests need one prompt: the route runs to completion and pauses only for plan approval, a `NEEDS_INPUT` question, or a `BLOCKED` decision. The Orchestrator classifies every later message by the [follow-up rules](.apm/agents/orchestrator.agent.md#follow-ups):

| Follow-up | Handling |
|---|---|
| Plan approval | Continues the route at implementation |
| Plan edits, or rejection with a reason | Planner revision, then approval again; counts toward the revision limit |
| Answer to `NEEDS_INPUT`, or decision after `BLOCKED` | Continues the route at the paused step |
| Commit authorization | `R0 COMMIT` |
| Correction, extension, or new question after a completed route | New request: routed again, with earlier results as inputs and a new trace that references the earlier route; also a learning signal when it corrects the result |

An ambiguous message is treated as a new request, so it never counts as approval. Limits start again per request.

### Learning

Learning is a lightweight, final step of the workflow, not a separate agent or route. When a route ends with a learning signal, such as a review finding, a plan change, a deviation, a failed validation, a blocked worker, or a user correction, the Orchestrator invokes Documenter once in `LEARN` mode with the evidence. Clean runs record `Learning: NONE` and skip the step.

Documenter applies the [workflow-learning skill](.apm/skills/workflow-learning/SKILL.md). It first scores the run on five fixed axes (routing, accuracy, completeness, validation, efficiency) from 1 to 5, citing evidence for every score below 5; every axis scored 3 or lower must yield a lesson or a stated reason it is not reusable. Lessons then go to their owner:

| Lesson about | Where it goes |
|---|---|
| This repository only, or a repository-owned file | Repository customizations: `AGENTS.md`, then a scoped instruction, then a local skill, then a local agent |
| A file deployed by this package, or a cross-repository convention | This package's `.apm/` source, edited directly when the current repository is DevHub or a DevHub clone is in the workspace, with a `CHANGELOG.md` entry; otherwise proposed |
| General knowledge from a reused upstream part | Proposed; upstream content is never edited |

Each lesson reports `UPDATED`, `PROPOSED`, or `ALREADY_COVERED`, with its evidence and owner, in the final report's Learning section. Installed copies listed in `apm.lock.yaml` are never edited, and changes to safeguards such as approvals, tools, routing, or commit policy are always proposed. Learning edits are not reviewed, get their own suggested commit, and reach consumers only after `apm install`.

### Commit

A completed route that changed files ends with a copy-ready `/git-commit` command for the pinned [`git-commit`](https://github.com/github/awesome-copilot/tree/main/skills/git-commit) skill. It lists only the paths workers changed, uses one command per logical change, and carries a Conventional Commits message without `Co-authored-by:` trailers, as required by the [Git instructions](.apm/instructions/git.instructions.md). It is suggested only after review returned `PASS` or when the route requires no review.

The suggestion is not authorization. When the user explicitly authorizes the commit, rule `R0 COMMIT` delegates it to Engineer, which runs the skill, because Orchestrator has no terminal access. The user can also run the command in a chat whose agent has terminal access. Pushing is never part of the workflow and requires its own explicit authorization.

### Reports and trace

Every worker ends with a fixed `## Report` block: agent, model, status, outcome, reason, references (instructions, skills, files read, and external sources actually used), changes or findings, validation evidence, decisions, deviations, and open items. The Orchestrator includes every report in full and adds the selected route with its reason, a step trace with the configured and reported model per step, a references table with one row per step including its own, and a result summary of changes, validation, review, deviations, and next decisions.

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
| Review finding fixed in a correction cycle | Learning step records the rule in its owner, or `ALREADY_COVERED` |
| Clean run without signals | `Learning: NONE`; no learning step |
| Lesson about a common agent, no DevHub source in the workspace | `PROPOSED` with the exact suggested text |
| User authorizes the commit | R0; Engineer commits via `git-commit` and reports the hash; no push |

Source edits do not update deployed customizations or running sessions.

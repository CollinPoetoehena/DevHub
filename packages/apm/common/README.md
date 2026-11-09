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

| Agent | Responsibility | Model field | Tools |
|---|---|---|---|
| [Orchestrator](.apm/agents/orchestrator.agent.md) | Entry point: routes, sequences, obtains approvals, reports the trace | Omitted (host-managed) | `['*']` |
| [Planner](.apm/agents/planner.agent.md) | Requirements, approach, steps, task contracts, acceptance criteria, validation | Omitted (host-managed) | `['*']` |
| [Architect](.apm/agents/architect.agent.md) | Consequential design decisions with trade-offs | Omitted (host-managed) | `['*']` |
| [Engineer](.apm/agents/engineer.agent.md) | Implementation, diagnosis, validation, and batch integration | Omitted (host-managed) | `['*']` |
| [Documenter](.apm/agents/documenter.agent.md) | Documentation-only changes, fact-checked against the code | Omitted (host-managed) | `['*']` |
| [Reviewer](.apm/agents/reviewer.agent.md) | Independent, evidence-based review with severity-rated findings; re-runs validation without editing | Omitted (host-managed) | `['*']` |
| [Learner](.apm/agents/learner.agent.md) | Evidence-based workflow evaluation and retained lessons in owning customization sources | Omitted (host-managed) | `['*']` |

The table matches each agent's `model` and `tools` frontmatter. The common agents omit `model`, so selection follows the host/session's selected or default model; this does not guarantee Auto. In a Copilot surface that offers Auto, select it in the host's model picker. The [APM guide's runtime-managed model selection](../README.md#runtime-managed-model-selection) owns the compatibility rationale and host-specific limits.

For requests routed to it, the Planner turns a high-level goal into a clearer, more complete implementation plan by making relevant requirements, constraints, assumptions, task contracts, and measurable acceptance criteria explicit, then organizing work into ordered, verifiable steps with validation. This reduces the burden on the user to formulate every detail manually and helps surface omissions or inconsistencies. The Planner supports human decisions rather than making unresolved consequential design choices or approving implementation: it requests missing input or Architect input when needed, and implementation waits for explicit user approval.

Tool access does not authorize every action. Orchestrator delegates delivery and commits; Planner, Architect, Documenter, and Learner are instructed not to run commands. Reviewer may run only inspection and check-mode validation without editing; Learner edits only the customization sources and changelog allowed by its skill. Only Orchestrator delegates under the role instructions; workers retain `agents: []` for harnesses that honor it. These are behavioral limits, not hard tool-level enforcement. See [harness limitations](#harness-limitations).

Host permissions and approvals still apply. Wildcard access does not guarantee runtime tool availability or remove all confirmation prompts; verify the intended harness after installation.

Only Orchestrator appears in the agent picker; the workers set `user-invocable: false`.

Instructions:

- [AI customization](.apm/instructions/ai-customization.instructions.md): deterministic workflow, reporting, and runtime-managed model-selection rules for authoring customizations.
- [Coding](.apm/instructions/coding.instructions.md), [documentation](.apm/instructions/documentation.instructions.md), and [Git](.apm/instructions/git.instructions.md): shared engineering standards.
- [Security](.apm/instructions/security.instructions.md): untrusted content, secrets, secure defaults, and review focus for all work.
- [Testing](.apm/instructions/testing.instructions.md): behavior-focused cases, edge conditions, assertions, determinism, regression checks, and project test tooling.
- [GitHub Actions](.apm/instructions/github-actions.instructions.md): workflow and CI conventions, kept here because nearly every repository uses them.

Language and tool instructions, such as Python, Dockerfile, and Ansible, live in the opt-in [stack packages](../README.md#package-design) and refine these common instructions.

Skills:

- [code-comments](.apm/skills/code-comments/SKILL.md): decides whether comments are warranted and writes, trims, or removes them; linked from the [coding instructions](.apm/instructions/coding.instructions.md#comments).
- [workflow-learning](.apm/skills/workflow-learning/SKILL.md): scores a workflow run and retains lessons in the owning customization file; used by Learner.
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
| `git-commit` skill | [awesome-copilot](https://github.com/github/awesome-copilot/blob/main/skills/git-commit/SKILL.md) | Dependency | `60dcb90` (2026-11-06) | None; applied internally by Engineer for R0 `COMMIT` |
| Planner agent | [ECC `planner`](https://github.com/affaan-m/ECC/blob/main/agents/planner.md) | Ideas, modified | Not applicable | Adopted the four-stage process (requirements, existing code review, step breakdown, ordering), the step format (file, action, reason, dependencies, risk), the planning rules for specificity, minimal change, failure paths, refactors, and phasing, plan-level red flags, and the plan format. Left out the worked example and code-level red flags, which the coding instructions own |
| Architect agent | [ECC `architect`](https://github.com/affaan-m/ECC/blob/main/agents/architect.md) | Ideas, modified | Not applicable | Adopted the four-stage process (current state, requirements, options, trade-offs), the architectural principles as a per-option `+ \| 0 \| - \| n/a` trade-off rating, the red flags, and ADR-shaped output. Left out the pattern catalogs, the example architecture, and the scalability plan |
| Reviewer agent | [ECC `code-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/code-reviewer.md) | Ideas, modified | Not applicable | Adopted the pre-finding gate, proof for `CRITICAL` and `HIGH`, the four-level severity scale, zero findings as a valid result, common false positives, independent re-run of validation, and the AI-generated code focus |
| Security instructions | [ECC `security-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/security-reviewer.md), [ECC `security-review` skill](https://github.com/affaan-m/ECC/blob/main/skills/security-review/SKILL.md), and the prompt defense baseline | Ideas, modified | Not applicable | Adopted untrusted-content handling, OWASP-aligned secure defaults per area, a pattern table rated on the Reviewer's severity scale, false positives, negative security tests, and the exposed-secret response, as one shared instruction instead of a separate agent. Left out the TypeScript, Supabase, and Solana code examples and the framework-specific checklists |
| `workflow-learning` skill | [ECC `agent-self-evaluation`](https://github.com/affaan-m/ECC/blob/main/skills/agent-self-evaluation/SKILL.md) | Ideas, modified | Not applicable | Adopted a 1 to 5 scorecard with the evidence rule, independent scoring per axis, a user-agreement self-check, and the anti-patterns. Replaced the output-quality axes with workflow axes derived from trace signals, and weak axes feed lesson extraction instead of a rework step |

The ECC parts are used for ideas only; the DevHub agents and skills keep their own roles, outcomes, and reports. ECC's agents embed long general checklists, principles, pattern catalogs, language- and framework-specific examples, and worked examples. Those were not copied: the models already know general practice, the shared instructions own DevHub's standards, and language-specific guidance belongs in scoped instructions or skills. Only the parts that make the output checkable, such as gates, proof rules, and fixed formats, were adopted. The prompt defense baseline's rules against outputting code, scripts, and links were left out because they conflict with engineering work.

---

## Workflow

The Orchestrator owns routing and approvals, Planner owns the approach, Architect owns consequential design decisions, Engineer and Documenter own delivery, Reviewer owns assessment, and Learner owns workflow evaluation and retained lessons. Workers run as subagents and return to the Orchestrator, which stays the active conversation so it can ask questions, obtain approval, and consolidate results.

```text
User -> Orchestrator
          +-- R0 COMMIT         -> Engineer (COMMIT, git-commit skill) -> stop
          +-- R1 ANSWER         -> answer (Engineer DIAGNOSE if commands are needed)
          +-- R2 REVIEW         -> Reviewer -> findings, stop
          +-- R3 DIRECT_DOCS    -> Documenter -> done
          +-- R4 DIRECT_CHANGE  -> Engineer -> Reviewer
          +-- R5 PLANNED        -> Planner (-> Architect -> Planner)
                                     -> user approval -> one worker or task batch
                                        -> Engineer integration for batches -> Reviewer

Reviewer: PASS -> done | R4 changes -> Engineer -> Reviewer
          R5 changes -> approved owners -> Engineer integration/validation -> Reviewer
          PLAN_CHANGES -> Planner -> user approval
Route end with learning signals -> Learner (workflow-learning skill) -> final report
```

### Routing

The [Orchestrator routing table](.apm/agents/orchestrator.agent.md#routing-table) is evaluated top to bottom and the first match wins. A rule matches only when its condition clearly holds, so uncertainty falls through to `R5 PLANNED`. Documentation that defines future behavior, such as an ADR or proposed contract, is planning rather than documentation maintenance. Review-only, diagnosis-only, and plan-only requests never start implementation. Under R5, Documenter owns standalone documentation tasks; Engineer owns code and documentation coupled to code. A single documentation-only task stays with Documenter. For an approved multi-task plan, the Orchestrator follows the task contracts and dependency rules, then one Engineer integrates and validates the bundle before Reviewer assesses it.

R5 plans identify each task by ID, owner, exact file scope, dependencies, deliverables, and acceptance checks. Read-only tasks may run in parallel. Write tasks run concurrently only when isolated worktrees or equivalent working copies are confirmed and there are no shared files or unresolved dependencies; otherwise writes are serialized. If a task fails or blocks, the Orchestrator stops dispatching, blocks dependent and not-yet-started tasks, and settles every running worker before ending the route. It requests cancellation only when the host explicitly supports cancellation and confirms it; otherwise it awaits each result. It collects final or partial reports from all started workers and does not report a terminal result or invoke Learner while a worker is active. Completed task work remains partial, and the incomplete bundle is not integrated until the user resolves the blocker. Simple work remains a single task and worker.

### Outcomes and transitions

Each worker returns an execution status (`COMPLETE | NEEDS_INPUT | BLOCKED | FAILED`) and, when complete, exactly one outcome from a closed set. Each outcome maps to exactly one next step in the [transition table](.apm/agents/orchestrator.agent.md#transitions). For R5 `IMPLEMENTATION_CHANGES`, findings go to the approved owners of the affected tasks: Documenter owns standalone documentation and Engineer owns code plus documentation coupled to code. This ownership also holds for a single docs-only task and a mixed bundle; Engineer does not author standalone documentation. After corrections finish, Engineer integrates and bundle-validates the corrections before Reviewer re-reviews. One correction round counts once against the two-cycle-per-request limit, not once per owner or rerun. R4 corrections stay with Engineer. `PLAN_CHANGES` goes to Planner and requires explicit user approval before implementation. Reviewer sees an R5 bundle only after Engineer completes final integration and validation.

| Agent | Outcomes |
|---|---|
| Planner | `PLAN_READY`, `ARCHITECTURE_REQUIRED` |
| Architect | `DESIGN_READY` |
| Engineer | `IMPLEMENTED`, `DIAGNOSED`, `PLAN_CHANGES`, `COMMITTED` |
| Documenter | `DOCUMENTED`, `ENGINEERING_REQUIRED` |
| Reviewer | `PASS`, `IMPLEMENTATION_CHANGES`, `PLAN_CHANGES` |
| Learner | `LEARNED` |

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

Learning is a lightweight, final step owned by the dedicated [Learner agent](.apm/agents/learner.agent.md), not a separate route or a Documenter mode to ensure consistent handling and traceability of learning signals (embedding in another agent would provide less control and traceability). When a route other than R0 ends with a learning signal, such as a review finding, a plan change, a deviation, a failed validation, a blocked worker, or a user correction, the Orchestrator invokes Learner once with the original request, acceptance criteria, full trace and worker reports, validation evidence, signals, and workspace roots. Clean runs record `Learning: NONE` and skip the step.

Learner applies the [workflow-learning skill](.apm/skills/workflow-learning/SKILL.md). It first scores the run on five fixed axes (routing, accuracy, completeness, validation, efficiency) from 1 to 5, citing evidence for every score below 5; every axis scored 3 or lower must yield a lesson or a stated reason it is not reusable. Its report includes the scorecard, lessons, changes, validation, references, and open items. Lessons then go to their owner:

| Lesson about | Where it goes |
|---|---|
| This repository only, or a repository-owned file | Repository customizations: `AGENTS.md`, then a scoped instruction, then a local skill, then a local agent |
| A file deployed by this package, or a cross-repository convention | This package's `.apm/` source, edited directly when the current repository is DevHub or a DevHub clone is in the workspace, with a `CHANGELOG.md` entry; otherwise proposed |
| General knowledge from a reused upstream part | Proposed; upstream content is never edited |

Each lesson reports `UPDATED`, `PROPOSED`, or `ALREADY_COVERED`, with its evidence and owner, in the final report's Learning section. A completed evaluation returns `LEARNED` even when no lesson qualifies, with `Lessons: NONE` and the reason. Installed copies listed in `apm.lock.yaml` are never edited, and changes to safeguards such as approvals, tools, routing, or commit policy are always proposed. Learning edits are not reviewed, get their own suggested commit, and reach consumers only after `apm install` and a fresh chat. A failed, incomplete, or invalid learning report is reported as a deviation and open item without changing the original route's status or re-invoking Learner.

### Commit

A completed route that changed files ends with copy-ready Git shell command(s) in fenced `bash` blocks, such as `git add -- 'path/to/file' && git commit -m 'type(scope): imperative summary'`. Commands list only route-owned paths, use one command per logical commit, quote each path and message, and follow the [Git instructions](.apm/instructions/git.instructions.md). If a changed path also contains pre-existing or unrelated changes, only route-owned hunks can be staged manually; the Orchestrator must not suggest adding the whole path. Commands are suggested only after review returned `PASS` or when the route requires no review.

The suggestion is not authorization. When the user explicitly authorizes a commit, rule `R0 COMMIT` delegates it to Engineer, which applies the pinned [`git-commit`](https://github.com/github/awesome-copilot/tree/main/skills/git-commit) skill internally and reports the resulting hash. The Orchestrator coordinates but does not commit, even though its tool list includes `execute`. Pushing is never part of the workflow and requires its own explicit authorization.

### Reports and trace

Every worker ends with a fixed `## Report` block: agent, tools used, status, outcome, reason, references (instructions, skills, files read, and external sources actually used), changes or findings, validation evidence, decisions, deviations, and open items. The Orchestrator includes every report in full and adds the selected route with its reason, a step trace aggregating tools actually used, a references table with one row per step including its own, and a result summary of changes, validation, review, deviations, and next decisions.

### Model selection

The common agents omit `model`, and Orchestrator does not pass model overrides when invoking workers. Copilot uses the selected or default host model according to the current surface's rules. Select Auto in the host picker only where it is offered; omission itself does not select Auto. This describes the Copilot harness, not the separate Local harness model-selection behavior. See the [APM guide's runtime-managed model selection](../README.md#runtime-managed-model-selection).

---

## Harness limitations

- The workflow targets the **Copilot** harness, selected as the session target in VS Code Chat. Copilot delegates to custom agents through its native `task` tool, included in the explicit wildcard tool request. See [Copilot subagents](https://code.visualstudio.com/docs/agents/run/subagents#_subagents-by-harness) and [Copilot custom agents](https://docs.github.com/en/copilot/reference/custom-agents-configuration).
- Harness support for custom-agent fields varies. `user-invocable` and `disable-model-invocation` are used for picker and invocation behavior where supported; the `agents` allowlist and handoffs are not supported in the Copilot harness, so the agent files retain `agents` for Local. In Copilot, the Orchestrator's delegation is guided by its instructions and worker descriptions, not enforced by an allowlist. See [harness compatibility](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference#_harness-compatibility).
- Workers start in a fresh context, so the Orchestrator passes guidance paths and prior results explicitly. Workers never ask the user directly; they return `NEEDS_INPUT` and the Orchestrator asks, which keeps approvals and the trace in one conversation.
- Routing tables, outcomes, reports, and role boundaries are instructions to the model, not an execution engine. The wildcard deliberately provides no per-role tool filter, and command execution is not a sandbox. Hard enforcement of transitions or approvals requires host permissions, hooks, or a dedicated controller; see [agent configuration](../README.md#agent-configuration).

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
| Small approved implementation task | One task contract and one owner |
| Independent planned tasks without confirmed workspace isolation | Serialized writes; no assumed parallel editing |
| Independent planned writes with confirmed isolation | Parallel task workers, one Engineer integration and validation step, then Reviewer |
| Parallel planned task fails while other workers run | Stop dispatching; block dependent and not-started tasks; cancel only with explicit host support and confirmation, otherwise await workers; collect all final or partial reports before terminal reporting or learning |
| Planned task fails or blocks | Completed work remains partial; do not integrate the incomplete bundle; no terminal result while any worker is active |
| Reviewer finds a defect in a single R5 docs-only task | Documenter corrects standalone docs; Engineer integrates and bundle-validates without authoring docs; Reviewer re-reviews |
| Reviewer finds defects in a mixed R5 bundle | Findings return to approved task owners; Documenter corrects standalone docs and Engineer corrects code/coupled docs; Engineer integrates and bundle-validates before Reviewer re-reviews |
| R5 review correction round | Counts as one cycle across all owners; no per-worker or rerun reset; two cycles maximum per request |
| Reviewer finds a defect in R4 | Engineer corrects, then Reviewer re-reviews |
| Reviewer returns `PLAN_CHANGES` | Planner revises; explicit user approval is required before implementation resumes |
| Engineer needs an unapproved design change | `PLAN_CHANGES`; replanning and approval |
| Validation fails or a limit is reached | No completion claim; `BLOCKED` or `FAILED` reported |
| Any route | Final response contains route, trace with tools used, and every agent report |
| Completed route with changes | Ends with copy-ready Git add-and-commit shell command(s) for only route-owned changes; nothing is committed |
| Review finding fixed in a correction cycle | Learner runs once, returns its scorecard and lessons, and records the rule in its owner, or `ALREADY_COVERED`; Documenter is not invoked for learning |
| Clean run without signals | `Learning: NONE`; no learning step |
| Signal with no reusable lesson | Learner returns `COMPLETE`, `LEARNED`, a scorecard, and `Lessons: NONE` with the reason |
| Learner lacks required trace evidence or returns an invalid report | Final report records the learning deviation and open item; original route status is preserved and Learner is not re-invoked |
| Learner proposes a safeguard change | `PROPOSED` with exact suggested text; no safeguard is edited |
| Lesson about a common agent, no DevHub source in the workspace | `PROPOSED` with the exact suggested text |
| User authorizes the commit | R0; Engineer commits via `git-commit` and reports the hash; no push or learning step |

Source edits do not update deployed customizations or running sessions.

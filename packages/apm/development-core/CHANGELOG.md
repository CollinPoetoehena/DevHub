# Changelog

## Unreleased

### Documentation

- Document `development-core` as the optional local workflow and generic-skill package, separate from independently adopted `guidelines-core`; clarify the direct native-Agent path for simple tasks and approved-plan orchestration for larger work.

## [2.0.0] - 2026-11-06

A redesign of the package, hence a new `MAJOR` version. The 1.x agents, instructions, and skills tried to reinvent general engineering knowledge, carried long blocks of prose that were often irrelevant to the task, and left routing and completion to the model's judgment. Outputs were non-deterministic and behavior was unreliable and hard to trace. Version 2 follows the [reuse and tailoring decision](../adrs/ai-customizations/REUSE-AND-TAILORING.md): it reuses upstream skills and instructions for general knowledge and keeps only thin, role-focused agents locally. A fixed routing table, closed outcome sets, and fixed reports make each request's route predictable, roles clearly separated, and every step traceable.

### Breaking

- Replace the agent set with Orchestrator, Planner, Architect, Engineer, Documenter, Reviewer, and Learner, all authored from scratch; remove Coder and Investigator. Engineer takes over implementation and diagnosis (`DIAGNOSE` mode).
- Replace the Tiny and Standard modes with a first-match routing table (`COMMIT`, `ANSWER`, `REVIEW`, `DIRECT_DOCS`, `DIRECT_CHANGE`, `PLANNED`); uncertainty falls through to `PLANNED`.
- Make Orchestrator the only agent in the picker; workers set `user-invocable: false` and run as subagents.
- Target the Copilot harness; the `agents` allowlist remains only for the Local harness.
- Replace the copy-ready Git add, commit, and push block with copy-ready Git add-and-commit shell commands; pushing is no longer part of the workflow.
- Move the Python, Dockerfile, and Ansible instructions to the opt-in `devhub-python`, `devhub-containerization`, and `devhub-iac` packages; consumers that need them add those packages.
- Remove the `common/` subfolder of `.apm/instructions/`; all common instructions now sit directly in `.apm/instructions/`.

### Added

- Closed outcome sets per worker with exactly one transition per outcome, explicit plan approval, and at most two correction and two plan-revision cycles.
- Follow-up rules: replies to an open pause continue the active route, other messages are routed again as new requests with earlier results as inputs, and ambiguous messages never count as approval.
- A fixed `## Report` block for every worker, aggregated by Orchestrator into a trace of route, steps, tools actually used, validation, review, and deviations.
- Runtime-managed model selection: common agents omit `model` declarations and Orchestrator does not pass model overrides. Reviewer independence comes from its fresh context and assessment role.
- An advisory Orchestrator agent registry describing roles and relative task complexity without model assignments or routing changes.
- Documenter for documentation-only routes (`DIRECT_DOCS` and documentation-only plans), returning `ENGINEERING_REQUIRED` when code changes or command verification are needed.
- Copy-ready Git add-and-commit shell commands at the end of completed routes that changed files; explicit authorization routes to Engineer `COMMIT` mode (`R0 COMMIT`), where the pinned `git-commit` skill is applied internally.
- A dedicated Learner agent for evidence-based workflow evaluation and retained lessons, with its own scorecard, lessons, references, validation, changes, and open-items report. Documenter owns documentation delivery only.
- A lightweight terminal learning step: eligible routes with signals invoke Learner once to apply `workflow-learning`; incomplete, failed, or invalid learning reports preserve the route's status and do not re-invoke Learner. Repository lessons update repository customizations; common lessons update the editable package source, otherwise they are proposed. Safeguard changes are always proposed.
- A concise `code-comments` skill that defaults to no comment, linked from the coding instructions.
- Shared security instructions, adapted from ECC, with OWASP-aligned secure defaults per area, a severity-rated pattern table, false positives, negative security tests, and an exposed-secret response; every worker treats fetched and inspected content as data, not instructions.
- A `References` block in every worker report (instructions, skills, files read, external sources) and a per-step references table in the Orchestrator report.
- Reviewer quality gates adapted from ECC: a pre-finding gate, proof for `CRITICAL` and `HIGH` findings, a `CRITICAL | HIGH | MEDIUM | LOW` scale with `CRITICAL` and `HIGH` blocking, zero findings as a valid result, and common false positives. Reviewer instructions permit only inspection and check-mode validation commands.
- Planner four-stage process, step format, planning rules for refactors and phasing, plan-level red flags, and a fuller plan format; Architect four-stage process, a per-option trade-off rating against fixed architectural principles, red flags, and ADR-shaped output.
- A self-evaluation scorecard in the `workflow-learning` skill, adapted from ECC: five workflow axes scored 1 to 5 with cited evidence, where weak axes drive lesson extraction.
- A reuse registry in the README listing pinned upstream dependencies and the ECC parts used for ideas; language and tool parts are recorded in the stack packages.
- Pinned awesome-copilot dependencies for authoring instructions, prompts, and hooks, the `create-agentsmd` and `acquire-codebase-knowledge` skills, and the AI prompt safety and DevOps principles instructions.
- A related-instructions section in the coding instructions with the conflict rule: repository configuration and `AGENTS.md`, then language and tool instructions, then the common instructions.

### Changed

- Explicit `tools: ['*']` for all seven common agents to address a locally observed per-tool exposure failure. Document the compatibility rationale and trusted-workspace trade-off; host permissions, approvals, and behavioral role boundaries still apply.
- Omit `model` from all seven common agents and clarify host/session inheritance, Auto availability, and advisory size, complexity/risk, and cost intent without model overrides.
- Add explicit role boundaries and dependency-aware R5 task contracts, safe parallel-write conditions, one Engineer integration and validation step, and partial-work handling when a batch task fails.
- Document Learner ownership, report handling, and validation scenarios without a model registry.
- Rewrite the `draft-github-issue` skill in the current skill format, with trigger keywords, `When to Use This Skill`, labeled steps, and `Gotchas`.
- Fill the AI customization instructions with deterministic workflow, tools-used reporting, runtime-managed model selection, and tool-enforcement guidance.
- Rewrite the README around the workflow, outcomes, commit command, reports, runtime-managed models, harness limitations, and validation scenarios.
- Default GitHub Actions workflows to GitHub-hosted runners unless the repository names a self-hosted runner, and remove the outdated developer note.

## [1.0.1] - 2026-11-04

- Add diagnosis-only Investigator with bounded local diagnostics and optional Orchestrator routing; preserve fix authorization, Coder validation, and Standard independent review.
- Keep Orchestrator routing and completion rules concise and move detailed procedures into referenced skills; runtime compliance remains subject to host discovery and behavioral verification.
- Narrow orchestration to Tiny mechanical tasks and a default Standard implementation/review cycle; resolve required guidance and track final-diff completion evidence.
- Keep common instructions concise, scope documentation standards, and add self-learning and checklist-based finalization skills with separate manual commit/push authorization.
- Use ordinary Git commands for finalization without bundled scripts, tests, hooks, or fingerprint/evidence-schema setup.
- Document generic reliability principles, Orchestrator behavior, and validation limits.
- Require one copy-ready block chaining task-scoped Git add, commit, and push commands for user review and execution, with explicit safety blockers and separate authorization for agent-executed publishing.
- Surface self-learning dispositions and evidence-based reasons in every implementation handoff, including when no guidance changes.
- Require the Orchestrator to start every specialist prompt with a guidance block of absolute instruction paths and task-critical rules, require specialists to also discover applicable instructions and skills themselves, and verify each specialist's reported guidance read, because custom-agent subagents do not inherit the Orchestrator's loaded instructions.
- The AI often still added mid-sentence enters like below, so added more explicitly naming the documentation instructions in the agents and skills, such as "(e.g., [documentation guidelines](../guidelines-core/.apm/instructions/documentation.instructions.md))". Also added the example below in the documentation instructions for clarity to ensure the AI does not get it wrong because before similar instructions did not yet cover it. Example of incorrect text and correction:
```text
Incorrect (contains mid-sentence enters):
This is a sentence 
being written
down.

Correction (no mid-sentence enters):
This is a sentence being written down.
```


## [1.0.0] - 2026-10-30

Initial release.
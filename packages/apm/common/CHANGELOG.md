# Changelog

## [2.0.0] - 2026-TODO

A redesign of the package, hence a new `MAJOR` version. The 1.x agents, instructions, and skills tried to reinvent general engineering knowledge, carried long blocks of prose that were often irrelevant to the task, and left routing and completion to the model's judgment. Outputs were non-deterministic and behavior was unreliable and hard to trace. Version 2 follows the [80/20 approach](../README.md#the-8020-rule-reuse-then-tailor): it reuses upstream skills and instructions for general knowledge and keeps only thin, role-focused agents locally. A fixed routing table, closed outcome sets, and fixed reports make each request's route predictable, roles clearly separated, and every step traceable.

### Breaking

- Replace the agent set with Orchestrator, Planner, Architect, Engineer, Documenter, and Reviewer, all authored from scratch; remove Coder and Investigator. Engineer takes over implementation and diagnosis (`DIAGNOSE` mode).
- Replace the Tiny and Standard modes with a first-match routing table (`COMMIT`, `ANSWER`, `REVIEW`, `DIRECT_DOCS`, `DIRECT_CHANGE`, `PLANNED`); uncertainty falls through to `PLANNED`.
- Make Orchestrator the only agent in the picker; workers set `user-invocable: false` and run as subagents.
- Target the Copilot harness; the `agents` allowlist remains only for the Local harness.
- Replace the copy-ready Git add, commit, and push block with a `/git-commit` command; pushing is no longer part of the workflow.

### Added

- Closed outcome sets per worker with exactly one transition per outcome, explicit plan approval, and at most two correction and two plan-revision cycles.
- Follow-up rules: replies to an open pause continue the active route, other messages are routed again as new requests with earlier results as inputs, and ambiguous messages never count as approval.
- A fixed `## Report` block for every worker, aggregated by Orchestrator into a trace of route, steps, configured and reported models, validation, review, and deviations.
- Role-specific model fallback lists per agent, with Reviewer on a different model family than Engineer and Documenter on low-cost models.
- Documenter for documentation-only routes (`DIRECT_DOCS` and documentation-only plans), returning `ENGINEERING_REQUIRED` when code changes or command verification are needed.
- A copy-ready `/git-commit` command for the pinned `git-commit` skill at the end of completed routes that changed files; explicit authorization routes to Engineer `COMMIT` mode (`R0 COMMIT`).
- A lightweight learning step: when a route ends with learning signals, Documenter applies the new `workflow-learning` skill in `LEARN` mode. Repository lessons update repository customizations; common lessons update the package source when DevHub is editable in the workspace, otherwise they are proposed.
- A concise `code-comments` skill that defaults to no comment, linked from the coding instructions.
- Shared security instructions, adapted from ECC, with OWASP-aligned secure defaults per area, a severity-rated pattern table, false positives, negative security tests, and an exposed-secret response; every worker treats fetched and inspected content as data, not instructions.
- A `References` block in every worker report (instructions, skills, files read, external sources) and a per-step references table in the Orchestrator report.
- Reviewer quality gates adapted from ECC: a pre-finding gate, proof for `CRITICAL` and `HIGH` findings, a `CRITICAL | HIGH | MEDIUM | LOW` scale with `CRITICAL` and `HIGH` blocking, zero findings as a valid result, and common false positives. Reviewer gets `execute` to re-run validation with inspection and check-mode commands only.
- Planner four-stage process, step format, planning rules for refactors and phasing, plan-level red flags, and a fuller plan format; Architect four-stage process, a per-option trade-off rating against fixed architectural principles, red flags, and ADR-shaped output.
- A self-evaluation scorecard in the `workflow-learning` skill, adapted from ECC: five workflow axes scored 1 to 5 with cited evidence, where weak axes drive lesson extraction.
- A reuse registry in the README listing pinned upstream dependencies and the ECC agents used for ideas; language-specific parts are still to be recorded.

### Changed

- Rewrite the `draft-github-issue` skill in the current skill format, with trigger keywords, `When to Use This Skill`, labeled steps, and `Gotchas`.
- Fill the AI customization instructions with deterministic workflow, reporting, model-selection, and least-privilege rules.
- Rewrite the README around the workflow, outcomes, commit command, reports, models, harness limitations, and validation scenarios.

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
- The AI often still added mid-sentence enters like below, so added more explicitly naming the documentation instructions in the agents and skills, such as "(e.g., [documentation instructions](../instructions/documentation.instructions.md))". Also added the example below in the documentation instructions for clarity to ensure the AI does not get it wrong because before similar instructions did not yet cover it. Example of incorrect text and correction:
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
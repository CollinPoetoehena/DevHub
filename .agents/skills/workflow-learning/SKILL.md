---
name: workflow-learning
description: 'Scores a completed workflow run on fixed axes with cited evidence, then turns weak axes and signals into durable improvements of AI customization files: AGENTS.md, scoped instructions, skills, or agents. Use by Learner after an Orchestrator route ends with learning signals such as review findings, plan changes, route deviations, failed validation, or user corrections. Updates repository customizations directly, updates the common package source when editable, and otherwise proposes the change.'
---

# Workflow Learning

Retain reusable lessons from a workflow run in the file that owns them, so the next run starts better. This is explicit maintenance of customization files, not model training.

Learner owns this workflow in Orchestrator routes and includes this skill's scorecard and lesson entries in its own report. Documenter owns documentation delivery, not learning.

## When to Use This Skill

- An Orchestrator route ended and its trace contains learning signals
- A user corrected a completed result and the correction reveals a missing rule

## Evaluate the Run

Score the run before extracting lessons, so lessons follow from evidence rather than impressions. Evaluate the delivered result against the original request, not against work that was not requested.

| Axis | Question | Signals that lower it |
|---|---|---|
| Routing | Was the route and step sequence right for the request? | Route deviation, `ENGINEERING_REQUIRED`, re-route, user correction of scope |
| Accuracy | Were the results and claims correct? | `CRITICAL` or `HIGH` findings, user correction of the result, contradicted report |
| Completeness | Did the result meet every requirement and acceptance criterion? | Unmet criterion, missing edge case, follow-up needed for requested scope |
| Validation | Was every claim backed by passing evidence? | `FAILED` or `SKIPPED` validation, Reviewer results differing from the implementer's |
| Efficiency | Did the route finish without avoidable rework? | Correction cycles, plan revisions, re-invoked reports, reached limits, `BLOCKED` or `FAILED` workers |

Scale: `5` no gap, `4` minor gap without impact, `3` notable gap on this axis, `2` gap that affected correctness or usability, `1` the request was not met on this axis.

- **Evidence rule:** every score below `5` cites its evidence: trace step, finding, validation result, or user statement. A `5` requires that no signal for the axis is present.
- **Score independently:** score each axis from its own signals; do not choose an overall impression first.
- **Weak axes drive lessons:** every axis scored `3` or lower yields a lesson candidate, or a stated reason that the gap is not reusable, such as a one-off mistake, a flaky failure, or an external outage.
- **Self-check:** before reporting, ask whether the user would agree with the scorecard given the trace; adjust scores that the evidence does not support.

## Steps

1. **Evaluate the run** with the scorecard above.
2. **Extract lessons.** For each weak axis and each remaining signal, decide whether it reveals a reusable gap: a rule, fact, or procedure that would have prevented the problem in future runs. Ignore one-off mistakes, flaky failures, and problems already fixed in the run unless the fix revealed a missing rule. Cite the evidence.
3. **Check coverage.** Search existing customizations for the rule. When it exists, the outcome is `ALREADY_COVERED`; note why it was missed, such as a vague description or an unmatched `applyTo` pattern, and fix that instead when it is the actual gap.
4. **Choose the scope.**
   - **Repository:** facts or conventions specific to this repository, or a correction of a repository-owned file.
   - **Common:** a gap in a file deployed by the common APM package, or a convention that applies across repositories.
   - **Upstream:** general knowledge that a reused upstream skill or instruction should cover. Never edit upstream content; propose adopting or updating an upstream part, or add a thin local rule only for a DevHub-specific deviation.
5. **Choose the owner** by the first fitting type: root `AGENTS.md` for repository facts and routes, then a scoped `*.instructions.md` for standards on matching files, then a skill for an on-demand procedure, then an agent for role, routing, or output behavior. Prefer extending an existing file over creating one.
6. **Locate the editable source** (see [ownership](#ownership)) and apply the outcome:
   - `UPDATED`: the source is editable. Make the smallest edit that states the rule, in the file's existing style.
   - `PROPOSED`: the source is not editable, or the change touches safeguards. Return the target path and the exact suggested text.
7. **Record common package changes** in that package's `CHANGELOG.md` under an `## [Unreleased]` section.

## Ownership

Classify a file before editing it:

- **Package-owned:** listed under a dependency's `deployed_files` in the consumer's `apm.lock.yaml`, typically under `.github/agents/`, `.github/instructions/`, and `.agents/skills/`. These are installed copies; never edit them, because reinstalling overwrites the change.
- **Repository-owned:** every other customization file in the repository, such as `AGENTS.md` or local instructions and skills. Edit directly. New repository rules go into repository-owned files, never into package-owned paths or file names.

For a package-owned file from the common package, find its source in this order:

1. **Current repository:** the package source exists at `packages/apm/common/.apm/`, as in DevHub itself.
2. **Workspace clone:** a DevHub clone exists in the same workspace, such as a sibling `DevHub/packages/apm/common/.apm/` folder.

Map the deployed path to the source: `.github/agents/<name>.agent.md` to `.apm/agents/<name>.agent.md`, `.github/instructions/<name>.instructions.md` to `.apm/instructions/**/<name>.instructions.md`, and `.agents/skills/<name>/` to `.apm/skills/<name>/`. Confirm the source file exists before editing. When no editable source is found, the outcome is `PROPOSED`.

## Gotchas

- **Evidence or nothing:** never retain a lesson without trace or user evidence, and never invent rationale. A run without a qualifying lesson yields `NONE`.
- **No self-congratulation:** a scorecard of `5`s without evidence is not an evaluation; a `5` holds only when no signal for the axis exists.
- **No scope creep or re-litigation:** do not lower scores for work the user did not request, and do not re-argue decisions the user approved. Judge the delivered result.
- **Preference is not evidence:** a lower score or a lesson needs a concrete correctness, completeness, validation, or rework impact, not a style preference.
- **Rules, not stories:** write the durable rule, not what happened in the run. Avoid `in this task`, `previously`, or names of the current change.
- **Smallest change:** one or two lines in the owning file usually suffice. Do not restructure files, duplicate a rule in several places, or add long examples.
- **Safeguards need approval:** changes that weaken or alter approvals, permissions, tools, review requirements, routing rules, or commit and push policy are always `PROPOSED`, never `UPDATED`.
- **Deployed copies go stale:** an edit to the common package source does not update installed copies or running sessions. Report that `apm install` in the consumer, and a new chat, are needed.
- **Other repository, other commit:** an edit in a sibling DevHub clone belongs to that repository's own commit; report its path separately.

## Report

Return the scorecard, then one entry per lesson:

```markdown
- Scorecard: Routing <n>, Accuracy <n>, Completeness <n>, Validation <n>, Efficiency <n>
  - <axis below 5>: <evidence>
- Lesson: <the durable rule>
  - Evidence: <trace step, finding, or user statement>
  - Axis: ROUTING | ACCURACY | COMPLETENESS | VALIDATION | EFFICIENCY
  - Scope: REPOSITORY | COMMON | UPSTREAM
  - Owner: <file path>
  - Outcome: UPDATED | PROPOSED | ALREADY_COVERED
  - Change: <applied edit, or the exact suggested text for PROPOSED>
- Not retained: <weak axis or signal with the reason it is not reusable, or "none">
```

When no lesson qualifies, return the scorecard and `Outcome: NONE` with the reason.

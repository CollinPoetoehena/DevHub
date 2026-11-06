---
name: workflow-learning
description: 'Turns evidence from a completed workflow into durable improvements of AI customization files: AGENTS.md, scoped instructions, skills, or agents. Use after an Orchestrator route ends with learning signals such as review findings, plan changes, route deviations, failed validation, or user corrections. Updates repository customizations directly, updates the common package source when editable, and otherwise proposes the change.'
---

# Workflow Learning

Retain reusable lessons from a workflow run in the file that owns them, so the next run starts better. This is explicit maintenance of customization files, not model training.

## When to Use This Skill

- An Orchestrator route ended and its trace contains learning signals
- A user corrected a completed result and the correction reveals a missing rule

## Steps

1. **Extract lessons.** For each signal in the trace, decide whether it reveals a reusable gap: a rule, fact, or procedure that would have prevented the problem in future runs. Ignore one-off mistakes, flaky failures, and problems already fixed in the run. Cite the evidence: trace step, finding, or user statement.
2. **Check coverage.** Search existing customizations for the rule. When it exists, the outcome is `ALREADY_COVERED`; note why it was missed, such as a vague description or an unmatched `applyTo` pattern, and fix that instead when it is the actual gap.
3. **Choose the scope.**
   - **Repository:** facts or conventions specific to this repository, or a correction of a repository-owned file.
   - **Common:** a gap in a file deployed by the common APM package, or a convention that applies across repositories.
   - **Upstream:** general knowledge that a reused upstream skill or instruction should cover. Never edit upstream content; propose adopting or updating an upstream part, or add a thin local rule only for a DevHub-specific deviation.
4. **Choose the owner** by the first fitting type: root `AGENTS.md` for repository facts and routes, then a scoped `*.instructions.md` for standards on matching files, then a skill for an on-demand procedure, then an agent for role, routing, or output behavior. Prefer extending an existing file over creating one.
5. **Locate the editable source** (see [ownership](#ownership)) and apply the outcome:
   - `UPDATED`: the source is editable. Make the smallest edit that states the rule, in the file's existing style.
   - `PROPOSED`: the source is not editable, or the change touches safeguards. Return the target path and the exact suggested text.
6. **Record common package changes** in that package's `CHANGELOG.md` under an `## [Unreleased]` section.

## Ownership

Classify a file before editing it:

- **Package-owned:** listed under a dependency's `deployed_files` in the consumer's `apm.lock.yaml`, typically under `.github/agents/`, `.github/instructions/`, and `.agents/skills/`. These are installed copies; never edit them, because reinstalling overwrites the change.
- **Repository-owned:** every other customization file in the repository, such as `AGENTS.md` or local instructions and skills. Edit directly. New repository rules go into repository-owned files, never into package-owned paths or file names.

For a package-owned file from the common package, find its source in this order:

1. The current repository contains the package source at `packages/apm/common/.apm/`, as DevHub itself does.
2. A DevHub clone in the same workspace, such as a sibling `DevHub/packages/apm/common/.apm/` folder.

Map the deployed path to the source: `.github/agents/<name>.agent.md` to `.apm/agents/<name>.agent.md`, `.github/instructions/<name>.instructions.md` to `.apm/instructions/**/<name>.instructions.md`, and `.agents/skills/<name>/` to `.apm/skills/<name>/`. Confirm the source file exists before editing. When no editable source is found, the outcome is `PROPOSED`.

## Gotchas

- **Evidence or nothing:** never retain a lesson without trace or user evidence, and never invent rationale. A run without a qualifying lesson yields `NONE`.
- **Rules, not stories:** write the durable rule, not what happened in the run. Avoid `in this task`, `previously`, or names of the current change.
- **Smallest change:** one or two lines in the owning file usually suffice. Do not restructure files, duplicate a rule in several places, or add long examples.
- **Safeguards need approval:** changes that weaken or alter approvals, permissions, tools, review requirements, routing rules, or commit and push policy are always `PROPOSED`, never `UPDATED`.
- **Deployed copies go stale:** an edit to the common package source does not update installed copies or running sessions. Report that `apm install` in the consumer, and a new chat, are needed.
- **Other repository, other commit:** an edit in a sibling DevHub clone belongs to that repository's own commit; report its path separately.

## Report

Return one entry per lesson:

```markdown
- Lesson: <the durable rule>
  - Evidence: <trace step, finding, or user statement>
  - Scope: REPOSITORY | COMMON | UPSTREAM
  - Owner: <file path>
  - Outcome: UPDATED | PROPOSED | ALREADY_COVERED
  - Change: <applied edit, or the exact suggested text for PROPOSED>
```

When no lesson qualifies, return `Outcome: NONE` with the reason.

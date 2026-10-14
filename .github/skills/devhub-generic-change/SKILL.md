---
name: devhub-generic-change
description: "Implement and verify generic code changes, features, or bug fixes using the owning project's conventions. Use for changes that do not need a tool-specific workflow."
---

> **Maintenance note for users:** This skill is maintained in [DevHub](https://github.com/CollinPoetoehena/DevHub/blob/main/.github/skills/devhub-generic-change/SKILL.md). This is provenance information only; AI agents do not need to follow the link to use the skill.

> **Invocation-specific instructions take precedence:** Follow explicit directions in the current skill invocation or accompanying request over conflicting defaults or procedures in this skill. For example, if the request says not to run tests, do not run them even if this workflow normally calls for tests, and report them as skipped. This does not override higher-priority system or developer instructions, host constraints, or applicable safety requirements.

# Generic Code Change

Act as a senior software engineer working in the current repository.

**Objective:** Implement the change described in the request. Use its expected behavior and acceptance criteria to define what "done" means. If there is no actionable objective, clarify it before making changes.

Read applicable repository instructions, policies, and project context first. Those define the architecture, conventions, security requirements, and validation commands; this generic workflow does not override them.

## Discover Project Guidance and Structure

Automatically discover the consuming project's guidance before editing; do not assume DevHub's layout or ask the user to find files you can locate yourself.

1. Identify the owning repository or package. Read applicable `AGENTS.md`, `.github/copilot-instructions.md`, relevant `.github/instructions/*.instructions.md`, and directory-specific guidance.
2. Check common entry points such as `README.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`, `DEVELOPMENT.md`, and coding, testing, or security guides under `docs/`, `doc/`, `documentation/`, `reference/`, and package-local directories.
3. Inspect relevant source and test directories, neighboring implementations, dependency manifests, build and lint configuration, `Makefile`, `Taskfile.yml`, and CI workflows. Discover the actual commands, supported versions, architecture, and test conventions rather than assuming a framework.
4. These are candidates, not required names. If they do not reveal the guidance or structure, inspect the repository layout, search filenames and contents for relevant conventions and commands, and follow links from existing entry points. Keep discovery scoped to the task and respect access restrictions.
5. Track the files actually read and used, distinguishing explicit rules from inferred conventions. When dedicated guidance is absent, use the nearest consistent patterns and report the limitation. Resolve only material remaining ambiguity with the user.

## Before Making Changes

1. Inspect the relevant implementation, call sites, tests, and validation commands. Keep exploration focused.
2. Identify affected files, expected behavior, risks, and assumptions. Resolve material ambiguity before proceeding.
3. For non-trivial work, share a concise plan before editing. For small, clear changes, proceed directly. If planning only was requested, stop after the plan.

## Implementation

1. Make the smallest maintainable change that meets the objective. Fix root causes rather than masking symptoms.
2. Follow existing conventions and reuse suitable code, dependencies, and test helpers. Avoid unrelated refactoring and unnecessary dependencies.
3. Preserve existing user changes. Do not overwrite changes unrelated to the request.
4. Add or update tests for changed behavior and relevant edge cases; add a regression test for bug fixes where practical.
5. Validate the touched behavior with the narrowest useful checks, escalating to broader tests, linting, type checks, and builds as warranted.
6. Fix failures introduced by the change and rerun affected checks. Report unrelated or pre-existing failures without expanding scope.
7. Update directly related documentation and keep it consistent with the implementation. If a changelog exists, update it accordingly.

## Constraints

- Do not expose secrets, credentials, or private data.
- Obtain approval before destructive operations or changes outside the agreed scope.
- Do not commit, push, deploy, disable tests, weaken checks, or alter expectations unless explicitly requested.
- If blocked by missing tools, access, or information, report the blocker and what is needed.

## Completion Report

Summarize the changes, key files, checks actually run and their results, checks skipped and why, plus remaining risks or manual steps. Clearly distinguish verified results from untested expectations.

Explicitly list the files used to establish project guidelines and structure, with links or paths and each file's role. Report missing dedicated guidance and any conventions inferred from existing code.

Before composing the commit message, inspect `git diff`, `git diff --cached`, and `git status --short`; review relevant untracked files too, since they are not included in those diffs. Base the message on the complete pending change set that `git add -A` will stage, including earlier session changes, not only the latest task or your own edits. Describe the combined scope without claiming ownership or validation of others' changes, and flag unrelated or unreviewed changes before offering the all-changes command.

For file changes in a Git repository, end the report with a copy-ready `sh` block containing `git add -A && git commit` with a concrete task-specific message, followed by `&& git push`. Do not add a co-author trailer. Follow the consuming repository's commit conventions. Inspect the branch and upstream; if no upstream exists, use `git push --set-upstream` with a verified remote and current branch. Do not leave placeholders or invent a push target. Before the block, warn that `git add -A` stages all changes, including unrelated edits, and ask the user to review the diff. These commands are for the user; do not commit or push unless explicitly requested. If no files changed, the task is outside Git, or a safe sequence is blocked, explain why the commands are omitted or incomplete.

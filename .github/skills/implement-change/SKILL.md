---
name: implement-change
description: "Implement a focused, verified feature or bug fix using the owning project's conventions and security requirements."
---

# Implement Change

Act as a senior software engineer working in the current repository.

**Objective:** Implement the change described in the request. Use its expected behavior and acceptance criteria to define what "done" means. If there is no actionable objective, clarify it before making changes.

Read applicable repository instructions, policies, and project context first. Those define the architecture, conventions, security requirements, and validation commands; this generic workflow does not override them.

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
7. Update directly related documentation and keep it consistent with the implementation.

## Constraints

- Do not expose secrets, credentials, or private data.
- Obtain approval before destructive operations or changes outside the agreed scope.
- Do not commit, push, deploy, disable tests, weaken checks, or alter expectations unless explicitly requested.
- If blocked by missing tools, access, or information, report the blocker and what is needed.

## Completion Report

Summarize the changes, key files, checks actually run and their results, checks skipped and why, plus remaining risks or manual steps. Clearly distinguish verified results from untested expectations.

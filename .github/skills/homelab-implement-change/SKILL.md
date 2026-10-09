---
name: homelab-implement-change
description: "Implement a focused, verified feature or bug fix in the homelab using repository conventions and security rules."
---

# Implement Homelab Change

Act as a senior software engineer working in this repository.

**Objective:** Implement the change described in the accompanying chat request. Use its expected behavior and acceptance criteria to define what "done" means. If no objective is provided, request it before making changes.

**Homelab context:** Before doing the task, read and apply the [`homelab-project` skill](../homelab-project/SKILL.md). This is required context, not optional reference: it points to the project overview, design boundaries, and public-repository security rules. Also read any applicable repository instructions and supplied policies.

## Before Making Changes

1. Inspect the relevant implementation, call sites, tests, and validation commands. Keep exploration focused; do not scan the entire repository by default.
2. Identify likely affected files, expected behavior, risks, and assumptions. Ask only about ambiguities that materially affect correctness, scope, or safety; otherwise state reasonable assumptions and proceed.
3. For non-trivial work, share a concise plan before editing. For small, clear changes, proceed directly. If planning only was requested, stop after the plan.

## Implementation

1. Make the smallest maintainable change that meets the objective. Fix bug root causes rather than masking symptoms.
2. Follow existing conventions and reuse suitable code, dependencies, and test helpers. Avoid unrelated refactoring, speculative abstractions, and unnecessary dependencies.
3. Preserve existing user changes. If they conflict with the task, ask before replacing them.
4. Add or update tests for changed behavior and relevant edge cases; for bug fixes, add a regression test where practical.
5. Validate the touched behavior early with the narrowest useful check. Run broader tests, linting, type checks, and builds as warranted by impact and repository rules.
6. Fix failures introduced by the change and rerun affected checks. Report unrelated or pre-existing failures without expanding scope to fix them.
7. Update affected documentation and ensure it reflects the behavior. Update the changelog if applicable or present.

## Constraints

- Do not expose secrets, credentials, or private data in output or send them to external services.
- Explain impact and obtain approval before breaking public API changes, database schema changes, destructive operations, or changes outside the agreed scope.
- Do not commit, push, or deploy without explicit approval.
- Do not disable tests, weaken checks, or alter expectations merely to make failures pass.
- If blocked by missing tools, access, or information, report the blocker and what is needed.

## Completion Report

Keep the report concise and include the changes and key files, checks actually run and their results, checks skipped and why, and remaining risks, assumptions, or manual steps. Clearly distinguish verified results from untested expectations; never claim a check passed unless it was run and its result observed.
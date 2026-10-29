---
name: devhub-python-change
description: "Implement or fix Python packages, applications, and scripts. Discover project conventions, preserve supported Python versions and public contracts, and validate using the actual project tooling and test setup."
---

> **Maintenance note for users:** This skill is maintained in [DevHub](https://github.com/CollinPoetoehena/DevHub/blob/main/docs/copilot/skills/devhub-python-change/SKILL.md). This is provenance information only; AI agents do not need to follow the link to use the skill.

> **Invocation-specific instructions take precedence:** Follow explicit directions in the current skill invocation or accompanying request over conflicting defaults or procedures in this skill. For example, if the request says not to run tests, skip them and report why. This does not override higher-priority system or developer instructions, host constraints, or applicable safety requirements.

# Python Change

Act as a senior software engineer working in the current repository.

Implement the requested Python change in the owning repository or package. Establish expected behavior and acceptance criteria; resolve material ambiguity before editing. This workflow is self-contained and does not require another skill.

---

## Discover Project Guidance and Structure

1. Identify the owning repository/package. Read applicable `AGENTS.md`, `.github/copilot-instructions.md`, relevant `.github/instructions/*.instructions.md`, and directory-specific guidance.
2. Inspect `README.md`, `CONTRIBUTING.md`, architecture, coding, testing, security, and documentation guides in `docs/`, `doc/`, `documentation/`, `reference/`, and package-local directories. Follow relevant entry-point links.
3. Inspect `pyproject.toml`, `setup.cfg`, `setup.py`, requirements and lock files, interpreter/version files, package layout, entry points, and neighboring implementations. Establish supported Python versions, dependency management, public APIs, and sync/async boundaries.
4. Read test contents and runner configuration, including relevant `tests/`, `test/`, `conftest.py`, `tox.ini`, `noxfile.py`, lint/type-check settings, build scripts, and CI workflows. Discover the actual environment and commands; do not assume pytest, uv, Poetry, Ruff, or a type checker is configured.
5. These names are candidates, not requirements. If they do not reveal the context, inspect the repository layout, search relevant filenames and contents, and follow existing links. Keep discovery scoped and respect access restrictions.
6. Track files actually used for guidance and structure, distinguishing explicit rules from inferred conventions. Report missing guidance; do not ask users to locate files you can discover yourself.

---

## Implement the Change

1. Inspect the affected implementation, callers, tests, and packaging boundaries. Share a concise plan for non-trivial work.
2. Make a focused change using established patterns and helpers. Preserve unrelated edits; avoid unrelated refactoring, dependency upgrades, or new tooling.
3. Preserve supported interpreter versions, import paths, public signatures, return shapes, exceptions, and serialization unless intentionally changing them. Do not use syntax or standard-library APIs newer than the supported minimum.
4. Follow local type-annotation conventions and existing models; use precise types and guards rather than broad `Any` or ignored diagnostics. Preserve async behavior, cancellation, resource cleanup, and context-manager use.
5. Surface errors through project-standard exceptions and logging. Do not hide failures with broad catches, silent defaults, or success-shaped fallbacks. Keep secrets out of source, logs, and examples.
6. Update directly related API, CLI, configuration, packaging, and usage documentation, and existing changelog entries as appropriate. Use the established dependency manager only when dependencies actually need changing.

---

## Docstrings and Comments

The rules below are self-contained. Optional background: [documentation concepts](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/engineering/Concepts.md#documentation); do not require this link to perform the task.

- Add or update a concise module docstring describing the purpose of new or materially changed source files when missing or inaccurate. Place it after required shebang/encoding lines and before imports, including `__future__` imports; preserve license and tool requirements.
- Use a first-statement docstring for new or materially changed functions, methods, and public classes where it clarifies their contract. Follow the project's format and document relevant inputs, outputs, exceptions, side effects, units, or async/resource constraints. Avoid repeating type annotations or boilerplate for trivial private helpers.
- Reserve inline comments for special reasoning: non-obvious edge cases, compatibility workarounds, ordering, security constraints, and trade-offs. Explain why, not obvious code.
- Decide length from complexity, audience, risk, and local style; use a short summary for simple code and expand for subtle contracts. Keep comments accurate, prefer clear code, and avoid unrelated headers in untouched, generated, or vendored files. Use established docstring checks when present.
- Document for a reader's task or meaningful risk, not maximum volume. Keep setup and usage in the README or linked guides, substantial rationale in design notes, contracts in docstrings, and local constraints near the code. Do not embed Python tutorials or repeat obvious syntax.
- Link shared practices once from the consuming project's README, not throughout source files. Record intentional deviations with their reason, scope, and consequences in the README or linked design notes; update central guidance if a deviation becomes shared practice. Use a local comment only for a specific implementation constraint.

---

## Tests and Validation

1. Establish whether meaningful tests exist in the owning package: empty files, scaffolding, TODOs, and trivial unrelated assertions are not behavioral coverage.
2. If meaningful tests exist, add or update focused coverage for changed behavior, relevant edge cases, and bug regressions using the existing suite. Preserve existing coverage and run the narrowest useful selectors.
3. If no meaningful tests exist, skip creating/running tests by default and explain why, including placeholder paths inspected. Do not add a test framework just for this change. Explicit test requests and applicable project requirements take precedence.
4. Use the discovered interpreter and project environment for existing format, lint, syntax, type-check, and packaging checks as applicable. Do not install dependencies or create environments merely for convenience; restore them only when required by a dependency change or a missing-dependency validation failure, following project policy.
5. Check command side effects first. Imports and tests may execute application code or contact services; use approved isolated targets and never alter production data without authorization.
6. Fix failures introduced by the change and rerun affected checks. Report missing tools, unrelated failures, checks skipped, and untested versions explicitly. Static checks do not prove runtime behavior across every supported interpreter.

---

## Completion Report

Summarize changes, key files, compatibility risks, checks actually run and their results, and skipped checks with reasons. State whether meaningful tests exist and what remains unverified. List the actual files used for project guidance and structure, their roles, inferred conventions, and missing dedicated guidance. Do not commit, push, deploy, weaken checks, or perform destructive operations unless explicitly requested.

Before composing the commit message, inspect `git diff`, `git diff --cached`, and `git status --short`; review relevant untracked files too. Describe the complete pending change set that `git add -A` will stage, including earlier session changes, not just this task. Flag unrelated or unreviewed changes without claiming ownership or validation of others' work.

**Git attribution default:** Copilot attribution is unnecessary by default. Omit `-m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"` and equivalent co-author trailers from generated commands and commit bodies, unless explicitly required by the user or applicable Copilot/repository instructions. Honor higher-priority instructions; do not change Git configuration or bypass hooks to suppress attribution.

For file changes in a Git repository, end with a copy-ready `sh` block containing `git add -A && git commit` with a concrete task-specific message following repository conventions, then `&& git push`. Inspect the branch, upstream, and remotes; without an upstream, use `git push --set-upstream` with a verified remote and current branch. Safely quote arguments; do not invent targets or leave placeholders. Before the block, warn that `git add -A` stages all changes, including unrelated edits, and ask the user to review the diff. These commands are for the user, not permission to execute them. If no files changed, the task is outside Git, or a safe sequence is blocked, explain why commands are omitted or incomplete.

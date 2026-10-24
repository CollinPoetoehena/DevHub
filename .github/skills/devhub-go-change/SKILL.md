---
name: devhub-go-change
description: "Implement or fix Go packages, modules, applications, and tools. Discover project conventions, preserve API and concurrency contracts, and validate with the actual Go toolchain and test setup."
---

> **Maintenance note for users:** This skill is maintained in [DevHub](https://github.com/CollinPoetoehena/DevHub/blob/main/.github/skills/devhub-go-change/SKILL.md). This is provenance information only; AI agents do not need to follow the link to use the skill.

> **Invocation-specific instructions take precedence:** Follow explicit directions in the current skill invocation or accompanying request over conflicting defaults or procedures in this skill. For example, if the request says not to run tests, skip them and report why. This does not override higher-priority system or developer instructions, host constraints, or applicable safety requirements.

# Go Change

Act as a senior software engineer working in the current repository.

Implement the requested Go change in the owning repository or module. Establish expected behavior and acceptance criteria; resolve material ambiguity before editing. This workflow is self-contained and does not require another skill.

---

## Discover Project Guidance and Structure

1. Identify the owning repository/module. Read applicable `AGENTS.md`, `.github/copilot-instructions.md`, relevant `.github/instructions/*.instructions.md`, and directory-specific guidance.
2. Inspect `README.md`, `CONTRIBUTING.md`, architecture, coding, testing, security, and documentation guides in `docs/`, `doc/`, `documentation/`, `reference/`, and package-local directories. Follow relevant entry-point links.
3. Inspect `go.mod`, `go.sum`, `go.work`, toolchain/version requirements, vendor policy, build tags, generated files, package layout, callers, and neighboring implementations. Establish module/workspace boundaries, supported platforms, public APIs, and dependency conventions.
4. Read relevant `*_test.go` files and runner configuration, lint settings, build scripts, `Makefile`, `Taskfile.yml`, and CI workflows. Discover actual commands, tags, environment requirements, and whether tests contact services; do not assume a particular linter or test framework.
5. These names are candidates, not requirements. If they do not reveal the context, inspect the repository layout, search relevant filenames and contents, and follow existing links. Keep discovery scoped and respect access restrictions.
6. Track files actually used for guidance and structure, distinguishing explicit rules from inferred conventions. Report missing guidance rather than inventing project requirements.

---

## Implement the Change

1. Inspect affected implementation, callers, tests, and module boundaries. Share a concise plan for non-trivial work.
2. Make a focused, idiomatic change using existing helpers and patterns. Preserve unrelated edits; avoid unrelated refactoring, dependency upgrades, and unnecessary interfaces or abstractions.
3. Preserve supported Go versions, build tags, platforms, exported APIs, zero-value behavior, and serialization contracts unless intentionally changing them. Do not raise the `go` or `toolchain` directive incidentally.
4. Return and wrap errors according to project conventions, preserving `errors.Is`/`errors.As` behavior where relevant. Do not discard errors, use panic for ordinary failures, or substitute silent success. Keep secrets out of code, logs, and examples.
5. Preserve context propagation, cancellation, goroutine lifetimes, channel ownership, locking, and resource cleanup. Do not introduce unbounded goroutines, leaked resources, data races, or blocking operations without clear ownership.
6. Update directly related API, CLI, configuration, and usage documentation, and existing changelog entries as appropriate. Change dependencies only when necessary; avoid broad `go get -u` or unrelated `go mod tidy` churn. Use generators only when relevant and understood.

---

## Documentation Comments

The rules below are self-contained. Optional background: [documentation concepts](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/engineering/Concepts.md#documentation); do not require this link to perform the task.

- Go has documentation comments, not Python-style docstrings. Add or update a concise package-purpose comment before a package clause in an appropriate file for new or materially changed packages when missing or inaccurate. Avoid repeating package documentation in every file; other new or materially changed files may have a short file-purpose header where useful.
- Preserve build constraints, required blank lines, license headers, generated markers, and directives in their required positions. Do not edit generated or vendored files just to add documentation.
- Document new or materially changed exported functions, methods, types, and other exported declarations with comments immediately before declarations, normally starting with the declared name. Explain relevant returns, errors, side effects, concurrency, ownership, or cancellation contracts. Document private helpers only when useful rather than repeating their signatures.
- Reserve inline comments for special, non-obvious reasoning, edge cases, workarounds, synchronization, or trade-offs. Choose length from complexity, audience, risk, and local style: short summaries for simple code, more detail for subtle contracts. Keep comments accurate and use established documentation checks when present.
- Document for a reader's task or meaningful risk, not maximum volume. Keep setup and usage in the README or linked guides, substantial rationale in design notes, contracts in declaration comments, and local constraints near the code. Do not embed Go tutorials or repeat obvious syntax.
- Link shared practices once from the consuming project's README, not throughout source files. Record intentional deviations with their reason, scope, and consequences in the README or linked design notes; update central guidance if a deviation becomes shared practice. Use a local comment only for a specific implementation constraint.

---

## Tests and Validation

1. Establish whether meaningful tests exist in the owning module/package. Empty scaffolding, TODOs, and trivial unrelated assertions are not behavioral coverage.
2. If meaningful tests exist, add or update focused tests for changed behavior, edge cases, and regressions using existing conventions. Preserve existing coverage and run the narrowest relevant package/test selectors.
3. If no meaningful tests exist, skip creating/running tests by default and explain why, including placeholders inspected. Do not introduce a test framework just for this change. Explicit test requests and applicable project requirements take precedence.
4. Format touched Go code with the project's formatter, normally `gofmt`, and use existing scoped build, vet, and lint checks as applicable. Respect module/workspace boundaries and build tags. Use race checks for changed concurrent behavior when supported and appropriate; report if not run. Do not install tooling or fetch dependencies unless needed by a dependency change or a missing-dependency validation failure, following project policy.
5. Inspect side effects before execution: tests, generators, builds, and package initialization can run code or access services. Use approved isolated targets; do not deploy or alter production data without authorization.
6. Fix failures introduced by the change and rerun affected checks. Report missing tools, unrelated failures, skipped checks, and untested platforms/toolchains. Static validation does not establish race freedom or runtime compatibility on all targets.

---

## Completion Report

Summarize changes, key files, API/concurrency risks, checks actually run and their results, and skipped checks with reasons. State whether meaningful tests exist and what remains unverified. List the actual files used for project guidance and structure, their roles, inferred conventions, and missing dedicated guidance. Do not commit, push, deploy, weaken checks, or perform destructive operations unless explicitly requested.

Before composing the commit message, inspect `git diff`, `git diff --cached`, and `git status --short`; review relevant untracked files too. Describe the complete pending change set that `git add -A` will stage, including earlier session changes, not just this task. Flag unrelated or unreviewed changes without claiming ownership or validation of others' work.

**Git attribution default:** Copilot attribution is unnecessary by default. Omit `-m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"` and equivalent co-author trailers from generated commands and commit bodies, unless explicitly required by the user or applicable Copilot/repository instructions. Honor higher-priority instructions; do not change Git configuration or bypass hooks to suppress attribution.

For file changes in a Git repository, end with a copy-ready `sh` block containing `git add -A && git commit` with a concrete task-specific message following repository conventions, then `&& git push`. Inspect the branch, upstream, and remotes; without an upstream, use `git push --set-upstream` with a verified remote and current branch. Safely quote arguments; do not invent targets or leave placeholders. Before the block, warn that `git add -A` stages all changes, including unrelated edits, and ask the user to review the diff. These commands are for the user, not permission to execute them. If no files changed, the task is outside Git, or a safe sequence is blocked, explain why commands are omitted or incomplete.

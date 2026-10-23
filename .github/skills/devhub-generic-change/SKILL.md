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

---

## Discover Project Guidance and Structure

Automatically discover the consuming project's guidance before editing; do not assume DevHub's layout or ask the user to find files you can locate yourself.

1. Identify the owning repository or package. Read applicable `AGENTS.md`, `.github/copilot-instructions.md`, relevant `.github/instructions/*.instructions.md`, and directory-specific guidance.
2. Check common entry points such as `README.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`, `DEVELOPMENT.md`, and coding, testing, or security guides under `docs/`, `doc/`, `documentation/`, `reference/`, and package-local directories.
3. Inspect relevant source and test directories, neighboring implementations, dependency manifests, build and lint configuration, `Makefile`, `Taskfile.yml`, and CI workflows. Read test contents and runner configuration to establish whether meaningful tests exist for the owning project or package; tests in an unrelated package do not establish a suite for the affected code. Discover the actual commands, supported versions, architecture, and test conventions rather than assuming a framework.
4. These are candidates, not required names. If they do not reveal the guidance or structure, inspect the repository layout, search filenames and contents for relevant conventions and commands, and follow links from existing entry points. Keep discovery scoped to the task and respect access restrictions.
5. Track the files actually read and used, distinguishing explicit rules from inferred conventions. When dedicated guidance is absent, use the nearest consistent patterns and report the limitation. Resolve only material remaining ambiguity with the user.

---

## Before Making Changes

1. Inspect the relevant implementation, call sites, tests, and validation commands. Keep exploration focused.
2. Identify affected files, expected behavior, risks, and assumptions. Resolve material ambiguity before proceeding.
3. For non-trivial work, share a concise plan before editing. For small, clear changes, proceed directly. If planning only was requested, stop after the plan.

---

## Implementation

1. Make the smallest maintainable change that meets the objective. Fix root causes rather than masking symptoms.
2. Follow existing conventions and reuse suitable code, dependencies, and test helpers. Avoid unrelated refactoring and unnecessary dependencies.
3. Preserve existing user changes. Do not overwrite changes unrelated to the request.
4. Apply the file, function, and inline documentation guidance below to new and materially changed code. Follow local syntax and conventions; keep documentation accurate without unrelated comment-only churn.
5. Update directly related documentation and keep it consistent with the implementation. If a changelog exists, update it accordingly.

---

## File, Function, and Inline Documentation

Use documentation to explain purpose, contracts, and reasoning, not to restate code. This guidance applies generically to programming languages such as Python, Go, and others, not specifically to YAML or configuration files. Apply it within the requested change, respecting applicable project instructions and language conventions.

1. **File purpose:** For a new source file, add a short top-level docstring or language-appropriate header explaining what the file provides, its responsibility, and any important usage constraints. For an existing file being materially changed, add or update that summary when missing or inaccurate. Preserve required shebangs, encoding declarations, licenses, generated-file markers, and language directives in their required positions. Do not edit generated or vendored files just to add documentation.
2. **Function contracts:** Add or update docstrings or language-appropriate documentation comments for new and materially changed functions, methods, and public types where they clarify a contract. Cover purpose, non-obvious inputs and outputs, units, errors, side effects, invariants, or concurrency requirements as relevant. Keep trivial private helpers brief or omit redundant documentation when local conventions permit; do not add boilerplate to every accessor. Put documentation where the language expects it, not indiscriminately inside function bodies: Python docstrings are the first statement, while Go documentation comments precede declarations.
3. **Inline reasoning:** Add inline or nearby block comments only for special, non-obvious details: surprising edge cases, compatibility workarounds, security constraints, ordering requirements, algorithm choices, or trade-offs. Explain why the code is necessary and, for a workaround, what would allow removal. Do not narrate assignments, loops, or obvious control flow.
4. **Proportionate length:** Decide length from complexity, audience, risk, and established style, not a fixed quota. A one-line purpose or function summary is often enough; expand only for information maintainers cannot reliably infer. Use the project's structured docstring format when present, without duplicating type annotations or signatures unnecessarily.
5. **Correctness and maintenance:** Prefer clear names and simple code over comments compensating for confusing design. Update or remove stale comments with the implementation, including misleading examples and documented defaults. Do not include secrets, speculative claims, commented-out code, or unrelated historical notes.
6. **Language and format fit:** Use native documentation mechanisms and preserve tool compatibility. Python supports module/function docstrings; Go uses package and declaration comments. For YAML, HCL, templates, and similar configuration formats, decide whether comments help based on the current file and established project style. Do not require a file header or introduce comments merely because a file is new or changed; a currently uncommented file can remain uncommented. Maintain existing useful comments and native descriptions as needed, and add a targeted comment only when it clarifies something non-obvious. Do not invent docstring syntax or add prose to formats that forbid comments.
7. **Review:** Check that documentation matches observable behavior, errors, and supported versions. Use established documentation linting or generation checks when present; do not introduce a documentation framework just for this change.

---

## Tests and Validation

Discover the consuming project's actual test setup; do not assume automated tests are present or required for every change.

1. Read test contents and runner configuration, not just directory names. Empty files, generated scaffolding, TODOs, commented examples, and trivial assertions unrelated to real behavior are not an implemented test suite.
2. If meaningful tests are implemented for the owning project or package, update or add coverage for changed behavior and relevant edge cases using that suite, including regression coverage for bug fixes where practical. Preserve existing coverage even if the suite does not yet cover the touched behavior. Run the narrowest relevant checks.
3. If no meaningful tests are implemented, skip adding or running automated tests by default and report why, including any placeholder paths inspected. For example, changing a standalone script without tests does not justify adding a suite. Do not introduce a framework, runner, dependencies, or test scaffolding merely for this change. Explicit user requests or applicable project requirements for tests take precedence; when tests are requested, follow discovered conventions and clarify material tooling or scope decisions if none exist.
4. Skipping tests does not skip other applicable validation. Use existing formatting, linting, syntax checks, type checks, and builds as appropriate, starting with the narrowest useful checks. Do not introduce tooling solely because a check is absent. For documentation-only changes, use existing documentation checks where available; do not run unrelated code tests or builds.
5. Inspect commands and their side effects before execution. Tests, builds, and manual checks that access external services, change data, or execute scripts require an approved safe target and appropriate authorization; discovery is not permission to run them.
6. Fix failures introduced by the change and rerun affected checks. Report unavailable tools, unrelated or pre-existing failures, and unverified behavior explicitly. Do not claim static checks prove runtime behavior.

---

## Constraints

- Do not expose secrets, credentials, or private data.
- Obtain approval before destructive operations or changes outside the agreed scope.
- Do not commit, push, deploy, disable tests, weaken checks, or alter expectations unless explicitly requested.
- If blocked by missing tools, access, or information, report the blocker and what is needed.

---

## Completion Report

**Git attribution default:** Copilot attribution is unnecessary by default. Omit `-m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"` and equivalent co-author trailers from generated commands and commit bodies, unless explicitly required by the user or applicable Copilot/repository instructions. Honor higher-priority instructions. This qualifies the no-trailer default below; do not change Git configuration or bypass hooks to suppress attribution.

Summarize the changes, key files, checks actually run and their results, checks skipped and why, plus remaining risks or manual steps. State whether meaningful tests were found, only placeholders were found, or tests were absent, and explain the resulting testing decision. Clearly distinguish verified results from untested expectations.

Explicitly list the files used to establish project guidelines and structure, with links or paths and each file's role. Report missing dedicated guidance and any conventions inferred from existing code.

Before composing the commit message, inspect `git diff`, `git diff --cached`, and `git status --short`; review relevant untracked files too, since they are not included in those diffs. Base the message on the complete pending change set that `git add -A` will stage, including earlier session changes, not only the latest task or your own edits. Describe the combined scope without claiming ownership or validation of others' changes, and flag unrelated or unreviewed changes before offering the all-changes command.

For file changes in a Git repository, end the report with a copy-ready `sh` block containing `git add -A && git commit` with a concrete task-specific message, followed by `&& git push`. Do not add a co-author trailer. Follow the consuming repository's commit conventions. Inspect the branch and upstream; if no upstream exists, use `git push --set-upstream` with a verified remote and current branch. Do not leave placeholders or invent a push target. Before the block, warn that `git add -A` stages all changes, including unrelated edits, and ask the user to review the diff. These commands are for the user; do not commit or push unless explicitly requested. If no files changed, the task is outside Git, or a safe sequence is blocked, explain why the commands are omitted or incomplete.

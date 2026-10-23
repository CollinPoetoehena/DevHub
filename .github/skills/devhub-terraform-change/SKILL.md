---
name: devhub-terraform-change
description: "Implement or fix Terraform modules and configurations. Discover project conventions, preserve infrastructure compatibility, and distinguish meaningful tests from placeholders before validating changes."
---

> **Maintenance note for users:** This skill is maintained in [DevHub](https://github.com/CollinPoetoehena/DevHub/blob/main/.github/skills/devhub-terraform-change/SKILL.md). This is provenance information only; AI agents do not need to follow the link to use the skill.

> **Invocation-specific instructions take precedence:** Follow explicit directions in the current skill invocation or accompanying request over conflicting defaults or procedures in this skill. For example, if the request says not to run tests, do not run them even if this workflow normally calls for tests, and report them as skipped. This does not override higher-priority system or developer instructions, host constraints, or applicable safety requirements.

# Terraform Change

Act as a senior software engineer working in the current repository.

Implement the requested Terraform change in the owning repository. Establish expected behavior, scope, and acceptance criteria; resolve material ambiguity before editing. This workflow is self-contained and does not require another skill.

---

## Discover Project Guidance and Structure

Automatically discover project guidance; do not assume the consuming repository follows DevHub's layout.

1. Read applicable `AGENTS.md`, `.github/copilot-instructions.md`, relevant `.github/instructions/*.instructions.md`, `README.md`, and `CONTRIBUTING.md`, including directory-specific instructions.
2. Look for architecture, coding, testing, security, and documentation guides in `docs/`, `doc/`, `documentation/`, `reference/`, and package-local directories. Follow relevant links and inspect neighboring modules and examples.
3. Inspect `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`, provider configuration, `.terraform.lock.hcl`, `modules/`, and `examples/` where present. Discover version constraints, module boundaries, input/output contracts, and consumers.
4. Inspect `tests/`, `test/`, `*.tftest.hcl`, Terratest code, `Makefile`, `Taskfile.yml`, lint configuration, and CI workflows to find the actual validation commands and whether tests have meaningful implementations.
5. These names are candidates, not requirements. If they do not reveal the guidance or structure, inspect the repository layout and search filenames and contents for relevant conventions and commands. Respect access restrictions and keep discovery scoped.
6. Track files actually used for guidelines and structure. Distinguish explicit rules from inferred patterns, and report when dedicated guidance is absent.

---

## Implement the Change

1. Inspect affected resources, expressions, inputs, outputs, examples, and consumers. Share a concise plan for non-trivial work.
2. Make a focused change following existing patterns; preserve unrelated user edits. Avoid unrelated refactoring, provider upgrades, or new tooling.
3. Preserve resource addresses, state compatibility, input types and defaults, and output contracts unless the request requires a change. Explain replacement risks and any necessary migration steps; do not manipulate state to hide incompatibility.
4. Use suitable types, validation, and descriptions for inputs. Keep credentials out of code and do not expose sensitive values in logs, outputs, or reports. Marking a value sensitive does not keep it out of state.
5. Update directly affected module documentation, examples, input/output tables, and existing changelog entries as appropriate. Use established generators when present.

---

## Comments and Code Documentation

- For HCL, YAML, and similar configuration files, decide whether comments help based on the current file and project conventions. Do not require top-of-file comments or introduce comments just because a file is new or changed; an uncommented file may remain uncommented. Maintain useful existing comments and preserve required license or tool headers; do not edit generated or vendored files just to add comments.
- Document public input/output contracts with native `description` attributes, including units, sensitivity, defaults, or constraints when not obvious. HCL has no Python-style module or function docstrings; do not invent them. The source-code documentation guidance is generic: for supporting scripts or test code in Python, Go, or other programming languages, add or update native file-purpose and function docstrings or declaration comments for new or materially changed code.
- Use inline comments only for non-obvious reasoning such as lifecycle choices, provider workarounds, dependency ordering, state compatibility, or replacement risks. Do not narrate resource attributes or repeat expressions.
- Decide length from complexity, risk, and local conventions: prefer a short useful summary, expanding only for subtle contracts. Update stale comments and use established documentation generators/checks where available; avoid unrelated documentation churn.

---

## Tests and Validation

DevHub Terraform projects generally do not have implemented automated tests. Discover the consuming project's actual state rather than assuming this applies everywhere.

1. Read test contents and their runner configuration. A directory, empty file, scaffold, commented example, or trivial assertion unrelated to real behavior is not an implemented test suite.
2. If meaningful tests are implemented, update or add coverage for the changed behavior and relevant edge cases using that suite, and run the narrowest relevant checks. Preserve existing coverage even if the suite does not yet cover the touched behavior.
3. If no meaningful tests are implemented, skip adding or running automated tests by default and report why, including any placeholder paths inspected. Do not introduce a test framework merely for this change. Explicit user requests or applicable project requirements for tests take precedence.
4. Skipping tests does not skip static validation. Use project-defined formatting, validation, and lint commands where available, such as scoped `terraform fmt -check` and `terraform validate`. Validation may require initialization; use `terraform init -backend=false` only when needed and permitted by project policy, without upgrading dependencies or accessing the remote backend.
5. Do not run `terraform test` blindly: tests can create real infrastructure. Run tests or plans that access providers, credentials, state, or external services only with an approved isolated target and understood side effects. Never apply, destroy, import, migrate state, or alter infrastructure without explicit authorization.
6. Fix failures introduced by the change and rerun affected checks. Report unavailable tools, uninitialized providers, unrelated failures, and unverified behavior explicitly; do not claim static validation proves deployment behavior.

---

## Completion Report

**Git attribution default:** Copilot attribution is unnecessary by default. Omit `-m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"` and equivalent co-author trailers from generated commands and commit bodies, unless explicitly required by the user or applicable Copilot/repository instructions. Honor higher-priority instructions. This qualifies the no-trailer default below; do not change Git configuration or bypass hooks to suppress attribution.

Summarize changes, key files, compatibility and replacement risks, commands actually run and results, and checks skipped with reasons. State whether meaningful tests were found or only placeholders, and identify remaining manual verification or migration steps.

Explicitly list the project files used for guidelines and structure, with links or paths and each file's role. Identify inferred conventions and missing dedicated guidance. Do not commit, push, deploy, weaken checks, or perform destructive operations unless explicitly requested.

Before composing the commit message, inspect `git diff`, `git diff --cached`, and `git status --short`; review relevant untracked files too, since they are not included in those diffs. Base the message on the complete pending change set that `git add -A` will stage, including earlier session changes, not only the latest task or your own edits. Describe the combined scope without claiming ownership or validation of others' changes, and flag unrelated or unreviewed changes before offering the all-changes command.

For file changes in a Git repository, end the report with a copy-ready `sh` block containing `git add -A && git commit` with a concrete task-specific message, followed by `&& git push`. Do not add a co-author trailer. Follow the consuming repository's commit conventions. Inspect the branch and upstream; if no upstream exists, use `git push --set-upstream` with a verified remote and current branch. Do not leave placeholders or invent a push target. Before the block, warn that `git add -A` stages all changes, including unrelated edits, and ask the user to review the diff. These commands are for the user; do not commit or push unless explicitly requested. If no files changed, the task is outside Git, or a safe sequence is blocked, explain why the commands are omitted or incomplete.

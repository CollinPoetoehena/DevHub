---
name: devhub-terraform-change
description: "Implement or fix Terraform modules and configurations. Discover project conventions, preserve infrastructure compatibility, and distinguish meaningful tests from placeholders before validating changes."
---

> **Maintenance note for users:** This skill is maintained in [DevHub](https://github.com/CollinPoetoehena/DevHub/blob/main/.github/skills/devhub-terraform-change/SKILL.md). This is provenance information only; AI agents do not need to follow the link to use the skill.

# Terraform Change

Implement the requested Terraform change in the owning repository. Establish expected behavior, scope, and acceptance criteria; resolve material ambiguity before editing. This workflow is self-contained and does not require another skill.

## Discover Project Guidance and Structure

Automatically discover project guidance; do not assume the consuming repository follows DevHub's layout.

1. Read applicable `AGENTS.md`, `.github/copilot-instructions.md`, relevant `.github/instructions/*.instructions.md`, `README.md`, and `CONTRIBUTING.md`, including directory-specific instructions.
2. Look for architecture, coding, testing, security, and documentation guides in `docs/`, `doc/`, `documentation/`, `reference/`, and package-local directories. Follow relevant links and inspect neighboring modules and examples.
3. Inspect `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`, provider configuration, `.terraform.lock.hcl`, `modules/`, and `examples/` where present. Discover version constraints, module boundaries, input/output contracts, and consumers.
4. Inspect `tests/`, `test/`, `*.tftest.hcl`, Terratest code, `Makefile`, `Taskfile.yml`, lint configuration, and CI workflows to find the actual validation commands and whether tests have meaningful implementations.
5. These names are candidates, not requirements. If they do not reveal the guidance or structure, inspect the repository layout and search filenames and contents for relevant conventions and commands. Respect access restrictions and keep discovery scoped.
6. Track files actually used for guidelines and structure. Distinguish explicit rules from inferred patterns, and report when dedicated guidance is absent.

## Implement the Change

1. Inspect affected resources, expressions, inputs, outputs, examples, and consumers. Share a concise plan for non-trivial work.
2. Make a focused change following existing patterns; preserve unrelated user edits. Avoid unrelated refactoring, provider upgrades, or new tooling.
3. Preserve resource addresses, state compatibility, input types and defaults, and output contracts unless the request requires a change. Explain replacement risks and any necessary migration steps; do not manipulate state to hide incompatibility.
4. Use suitable types, validation, and descriptions for inputs. Keep credentials out of code and do not expose sensitive values in logs, outputs, or reports. Marking a value sensitive does not keep it out of state.
5. Update directly affected module documentation, examples, input/output tables, and existing changelog entries as appropriate. Use established generators when present.

## Tests and Validation

DevHub Terraform projects generally do not have implemented automated tests. Discover the consuming project's actual state rather than assuming this applies everywhere.

1. Read test contents and their runner configuration. A directory, empty file, scaffold, commented example, or trivial assertion unrelated to real behavior is not an implemented test suite.
2. If meaningful tests are implemented, update or add coverage for the changed behavior and relevant edge cases using that suite, and run the narrowest relevant checks. Preserve existing coverage even if the suite does not yet cover the touched behavior.
3. If no meaningful tests are implemented, skip adding or running automated tests by default and report why, including any placeholder paths inspected. Do not introduce a test framework merely for this change. Explicit user requests or applicable project requirements for tests take precedence.
4. Skipping tests does not skip static validation. Use project-defined formatting, validation, and lint commands where available, such as scoped `terraform fmt -check` and `terraform validate`. Validation may require initialization; use `terraform init -backend=false` only when needed and permitted by project policy, without upgrading dependencies or accessing the remote backend.
5. Do not run `terraform test` blindly: tests can create real infrastructure. Run tests or plans that access providers, credentials, state, or external services only with an approved isolated target and understood side effects. Never apply, destroy, import, migrate state, or alter infrastructure without explicit authorization.
6. Fix failures introduced by the change and rerun affected checks. Report unavailable tools, uninitialized providers, unrelated failures, and unverified behavior explicitly; do not claim static validation proves deployment behavior.

## Completion Report

Summarize changes, key files, compatibility and replacement risks, commands actually run and results, and checks skipped with reasons. State whether meaningful tests were found or only placeholders, and identify remaining manual verification or migration steps.

Explicitly list the project files used for guidelines and structure, with links or paths and each file's role. Identify inferred conventions and missing dedicated guidance. Do not commit, push, deploy, weaken checks, or perform destructive operations unless explicitly requested.

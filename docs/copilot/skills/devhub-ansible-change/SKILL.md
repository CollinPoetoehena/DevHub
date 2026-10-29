---
name: devhub-ansible-change
description: "Implement or fix Ansible roles, playbooks, and collections. Discover project conventions, preserve idempotence and safe targeting, and distinguish meaningful tests from generated scaffolding."
---

> **Maintenance note for users:** This skill is maintained in [DevHub](https://github.com/CollinPoetoehena/DevHub/blob/main/docs/copilot/skills/devhub-ansible-change/SKILL.md). This is provenance information only; AI agents do not need to follow the link to use the skill.

> **Invocation-specific instructions take precedence:** Follow explicit directions in the current skill invocation or accompanying request over conflicting defaults or procedures in this skill. For example, if the request says not to run tests, do not run them even if this workflow normally calls for tests, and report them as skipped. This does not override higher-priority system or developer instructions, host constraints, or applicable safety requirements.

# Ansible Change

Act as a senior software engineer working in the current repository.

Implement the requested Ansible change in the owning repository. Establish expected behavior, scope, and acceptance criteria; resolve material ambiguity before editing. This workflow is self-contained and does not require another skill.

---

## Discover Project Guidance and Structure

Automatically discover project guidance; do not assume the consuming repository follows DevHub's layout.

1. Read applicable `AGENTS.md`, `.github/copilot-instructions.md`, relevant `.github/instructions/*.instructions.md`, `README.md`, and `CONTRIBUTING.md`, including directory-specific instructions.
2. Look for architecture, coding, testing, security, and documentation guides in `docs/`, `doc/`, `documentation/`, `reference/`, and package-local directories. Follow relevant links and inspect neighboring roles and playbooks.
3. Inspect `ansible.cfg`, `requirements.yml`, `galaxy.yml`, inventory structure, playbooks, and relevant `tasks/`, `defaults/`, `vars/`, `handlers/`, `templates/`, `files/`, `meta/`, and `plugins/` directories. Discover supported versions, platforms, variable precedence, dependencies, and role or collection boundaries. Do not expose inventory secrets.
4. Inspect `tests/`, `test/`, `molecule/`, collection test directories, lint configuration, `Makefile`, `Taskfile.yml`, and CI workflows to discover actual checks and whether tests have meaningful implementations.
5. These names are candidates, not requirements. If they do not reveal the guidance or structure, inspect the repository layout and search filenames and contents for relevant conventions and commands. Respect access restrictions and keep discovery scoped.
6. Track files actually used for guidelines and structure. Distinguish explicit rules from inferred patterns, and report when dedicated guidance is absent.

---

## Implement the Change

1. Inspect affected tasks, handlers, templates, variables, dependencies, and consumers. Share a concise plan for non-trivial work.
2. Make a focused change following existing patterns; preserve unrelated user edits. Avoid unrelated refactoring, dependency upgrades, or new tooling.
3. Prefer appropriate Ansible modules over shell commands. Preserve idempotence, use accurate change/failure conditions, and notify handlers only when appropriate. Do not mask failures or report success without evidence.
4. Preserve variable contracts, precedence, tags, supported platforms, and privilege boundaries unless a change is intended. Use safe defaults, appropriate file permissions, and project-standard secret handling; never expose credentials in output or examples.
5. Update directly related role or collection documentation, variable tables, dependencies, usage examples, and existing changelog entries as appropriate.

---

## Comments and Embedded Code Documentation

The rules below are self-contained. Optional background: [documentation concepts](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/engineering/Concepts.md#documentation); do not require this link to perform the task.

- For YAML, templates, and similar configuration files, decide whether comments help based on the current file and project conventions. Do not require top-of-file comments or introduce comments just because a file is new or changed; an uncommented file may remain uncommented. Maintain useful existing comments, preserving required licenses and template directives.
- Prefer descriptive task names, variable documentation, and collection argument specifications for normal behavior. Reserve inline comments for non-obvious conditions, ordering, idempotence decisions, platform workarounds, or security constraints; explain why, not obvious module arguments.
- The source-code documentation guidance is generic: for Python plugins, supporting scripts, or other programming-language code, add or update native file-purpose and function docstrings or declaration comments for new or materially changed code, covering relevant contracts, errors, and side effects. YAML itself has no docstrings; do not invent them.
- Choose length according to complexity and local conventions: one useful sentence may suffice; expand for subtle contracts. Avoid redundant private-helper boilerplate, keep comments accurate, and do not add unrelated headers to untouched, generated, or vendored files. Use existing documentation checks when present.
- Document for a reader's task or meaningful risk, not maximum volume. Keep role usage and operational procedures in the README or linked guides, substantial rationale in design notes, contracts in variable/argument documentation, and local constraints near affected tasks. Do not embed YAML or Ansible tutorials or repeat module arguments.
- Link shared practices once from the consuming project's README, not throughout task files. Record intentional deviations with their reason, scope, and consequences in the README or linked design notes; update central guidance if a deviation becomes shared practice. Use a local comment only for a specific implementation constraint.

---

## Tests and Validation

DevHub Ansible projects generally do not have implemented automated tests. Discover the consuming project's actual state rather than assuming this applies everywhere.

1. Read test contents and runner configuration, not just directory names. Generated `ansible-galaxy role init` content such as a basic `tests/test.yml` that only includes the role and a default inventory is scaffolding, not meaningful behavioral coverage. Empty Molecule scenarios, TODOs, or default/basic test files without real verification also count as placeholders. A meaningful scenario may verify outcomes in a separate verifier or idempotence step; inspect the whole scenario before classifying it.
2. If meaningful tests are implemented, update or add coverage for changed behavior and relevant edge cases using the existing suite. Run the narrowest relevant checks, including idempotence checks where established, on approved isolated targets. Preserve existing coverage even if it does not yet cover the touched behavior.
3. If no meaningful tests are implemented, skip adding or running automated tests by default and report why, including placeholder paths inspected. Do not introduce Molecule, another framework, or generated test scaffolding merely for this change. Explicit user requests or applicable project requirements for tests take precedence.
4. Skipping tests does not skip static validation. Use existing YAML, `ansible-lint`, template, and syntax checks as applicable. For a role, use an existing suitable wrapper playbook for `ansible-playbook --syntax-check`; do not treat a task file as a standalone playbook. Report missing dependencies or suitable validation entry points.
5. Inspect inventory, connection settings, and delegated tasks before executing any playbook or test. Do not run against production, use privilege escalation, or change managed hosts without explicit authorization. Check mode is not a sandbox: tasks can bypass it or have side effects, so `--check --diff` also requires an approved safe target and must not expose secrets.
6. Fix failures introduced by the change and rerun affected checks. Report unrelated failures and limitations explicitly; syntax and lint checks do not prove runtime behavior or idempotence.

---

## Completion Report

**Git attribution default:** Copilot attribution is unnecessary by default. Omit `-m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"` and equivalent co-author trailers from generated commands and commit bodies, unless explicitly required by the user or applicable Copilot/repository instructions. Honor higher-priority instructions. This qualifies the no-trailer default below; do not change Git configuration or bypass hooks to suppress attribution.

Summarize changes, key files, compatibility and operational risks, commands actually run and results, and checks skipped with reasons. State whether meaningful tests were found or only scaffolding, and identify remaining runtime or idempotence verification.

Explicitly list the project files used for guidelines and structure, with links or paths and each file's role. Identify inferred conventions and missing dedicated guidance. Do not commit, push, deploy, weaken checks, or perform destructive operations unless explicitly requested.

Before composing the commit message, inspect `git diff`, `git diff --cached`, and `git status --short`; review relevant untracked files too, since they are not included in those diffs. Base the message on the complete pending change set that `git add -A` will stage, including earlier session changes, not only the latest task or your own edits. Describe the combined scope without claiming ownership or validation of others' changes, and flag unrelated or unreviewed changes before offering the all-changes command.

For file changes in a Git repository, end the report with a copy-ready `sh` block containing `git add -A && git commit` with a concrete task-specific message, followed by `&& git push`. Do not add a co-author trailer. Follow the consuming repository's commit conventions. Inspect the branch and upstream; if no upstream exists, use `git push --set-upstream` with a verified remote and current branch. Do not leave placeholders or invent a push target. Before the block, warn that `git add -A` stages all changes, including unrelated edits, and ask the user to review the diff. These commands are for the user; do not commit or push unless explicitly requested. If no files changed, the task is outside Git, or a safe sequence is blocked, explain why the commands are omitted or incomplete.

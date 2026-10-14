---
name: devhub-docs
description: "Create or update documentation accurately, following the owning project's structure, terminology, and style."
---

> **Maintenance note for users:** This skill is maintained in [DevHub](https://github.com/CollinPoetoehena/DevHub/blob/main/.github/skills/devhub-docs/SKILL.md). This is provenance information only; AI agents do not need to follow the link to use the skill.

> **Invocation-specific instructions take precedence:** Follow explicit directions in the current skill invocation or accompanying request over conflicting defaults or procedures in this skill. For example, if the request says not to run documentation checks, do not run them even if this workflow normally calls for checks, and report them as skipped. This does not override higher-priority system or developer instructions, host constraints, or applicable safety requirements.

# Documentation

Create or update documentation for the request in the correct location and at the appropriate level of detail.

Before editing, read the relevant project instructions, existing documentation, and source material. Follow the owning project's terminology, structure, links, formatting, and security requirements. Do not invent product behavior or claim implementation details that have not been verified. If the repository has its own writing guidelines, read and apply them; they are project context, not part of this generic workflow.

## Discover Project Guidance and Structure

Automatically discover the consuming project's documentation guidelines and organization before editing. Do not assume DevHub's layout or ask the user to locate guidance that you can find in the repository.

1. Identify the owning repository or package and the documentation scope. Read applicable repository-wide and directory-specific instructions, such as `AGENTS.md`, `.github/copilot-instructions.md`, and relevant `.github/instructions/*.instructions.md` files.
2. Check common guidance files: `README.md`, `CONTRIBUTING.md`, `DOCUMENTATION.md`, `STYLEGUIDE.md`, `docs/README.md`, `docs/CONTRIBUTING.md`, and similarly named writing, style, or documentation guides. These are discovery candidates, not required files or a fixed naming convention.
3. Inspect common documentation structures: `docs/`, `doc/`, `documentation/`, `reference/`, `guides/`, and package-local documentation. Read the nearest README, overview, index, table of contents, and representative neighboring pages to determine placement, audience, terminology, heading conventions, and link style.
4. Where present, inspect documentation configuration and templates, such as `mkdocs.yml`, `mkdocs.yaml`, `docusaurus.config.*`, `docs/_config.yml`, `docs/conf.py`, `.vitepress/config.*`, or `SUMMARY.md`. Use these to understand navigation, source locations, generated content, and relevant checks; do not assume a documentation framework is in use.
5. If those locations do not reveal the guidance or structure, discover it yourself: inspect the repository and package layout, search filenames and content for documentation, writing, style, contribution, and navigation guidance, and follow relevant links from existing entry points. Keep the search scoped to the task and respect access restrictions.
6. Track the actual files read and what each establishes. Distinguish explicit writing rules from conventions inferred from examples. If no dedicated guidelines exist after discovery, follow applicable project instructions and the nearest consistent documentation patterns, and report that limitation. Ask the user only when an unresolved ambiguity materially affects the work.

## Writing and Editing

1. Identify the intended audience and purpose; keep the change focused on that purpose.
2. Reuse established sections and cross-link to authoritative explanations rather than duplicating them.
3. Keep examples safe and nonfunctional where credentials, addresses, or environment details are involved.
4. Update tables of contents, indexes, and directly affected links when adding, moving, or renaming content.
5. Preserve unrelated edits and avoid changing implementation files unless explicitly requested.

## Validation and Report

Check changed internal links where practical, review the diff for consistency and sensitive information, and run relevant documentation checks such as formatting or `git diff --check`. Report what changed and which checks were or were not run.

Explicitly list the project files used to establish documentation guidelines and structure, with links or paths and a brief explanation of each file's role (for example, writing rules, navigation, or neighboring-page conventions). Report only files actually read and used, not every discovery candidate. State when no dedicated writing guidelines or structural guidance were found and identify any conventions inferred from existing pages.

Before composing the commit message, inspect `git diff`, `git diff --cached`, and `git status --short`; review relevant untracked files too, since they are not included in those diffs. Base the message on the complete pending change set that `git add -A` will stage, including earlier session changes, not only the latest task or your own edits. Describe the combined scope without claiming ownership or validation of others' changes, and flag unrelated or unreviewed changes before offering the all-changes command.

For file changes in a Git repository, end the report with a copy-ready `sh` block containing `git add -A && git commit` with a concrete task-specific message, followed by `&& git push`. Do not add a co-author trailer. Follow the consuming repository's commit conventions. Inspect the branch and upstream; if no upstream exists, use `git push --set-upstream` with a verified remote and current branch. Do not leave placeholders or invent a push target. Before the block, warn that `git add -A` stages all changes, including unrelated edits, and ask the user to review the diff. These commands are for the user; do not commit or push unless explicitly requested. If no files changed, the task is outside Git, or a safe sequence is blocked, explain why the commands are omitted or incomplete.

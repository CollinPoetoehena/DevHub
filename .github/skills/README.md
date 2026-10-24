# Reusable Agent Skills

> **Official documentation:** [Adding agent skills for GitHub Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills), including [creating and adding a skill](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills#creating-and-adding-a-skill).
>
> The rest of this page describes DevHub's conventions and recommendations; use the official docs as the source of truth for supported Copilot behavior and formats.

Start with the shared [Create and maintain customizations](../AI.md#create-and-maintain-customizations) guidance for design, automatic context discovery, self-contained workflows, validation, and completion reports. This page adds skill-specific details. These skills are part of my [personal collection, reusable for personal projects and at work](../AI.md#personal-preferences-and-workplace-reuse); prefer project-specific additions rather than another generic collection.

DevHub maintains reusable, project-independent Agent Skills under `.github/skills/`. Each skill has its own directory containing a `SKILL.md`; the required YAML `name` matches the directory name. DevHub skill names use the `devhub-` prefix.

Skills capture reusable task instructions, repeatable processes, and multi-step workflows as well as specialized knowledge. Supporting scripts and resources are optional; a repeatable process can be useful as a skill on its own.

> **Prefer skills over prompt files:** Do not create new `.prompt.md` files for DevHub; use skills for reusable tasks and processes instead. VS Code has deprecated prompt files for Agent Host sessions, where they are not loaded, although they still work with the Local agent for now. See the [central recommendation](../AI.md#which-customization-should-i-use) and [official migration guidance](https://code.visualstudio.com/docs/agent-customization/migrate-customizations#_convert-prompt-files-to-skills). Ordinary one-off chat prompts remain appropriate.

---

## Table of contents

- [Available skills](#available-skills)
  - [Choosing a change skill](#choosing-a-change-skill)
  - [Comments and code documentation](#comments-and-code-documentation)
  - [Git attribution default](#git-attribution-default)
- [Use or install a skill](#use-or-install-a-skill)
- [Create a skill](#create-a-skill)
- [Examples beyond DevHub](#examples-beyond-devhub)

---

## Available skills

- [`devhub-ai-customization`](./devhub-ai-customization/SKILL.md) — create or maintain a self-contained DevHub skill or custom agent (mainly used in this DevHub repository itself, but reusable across other repositories as well).
- [`devhub-commit-message`](./devhub-commit-message/SKILL.md) — create a commit message and copy-ready Git handoff from all current changes, without editing files or committing.
- [`devhub-docs`](./devhub-docs/SKILL.md) — create or update documentation using the owning project's conventions (can be used for any project since it is not tied to DevHub-specific practices, it automatically adapts to the project's existing documentation structure and guidelines).
- [`devhub-generic-change`](./devhub-generic-change/SKILL.md) — implement and verify generic code changes using discovered project conventions and existing test setup, with detailed file/function documentation and selective inline-comment guidance.
- [`devhub-python-change`](./devhub-python-change/SKILL.md) — change Python packages, applications, and scripts with interpreter compatibility, docstrings, and project-specific validation.
- [`devhub-go-change`](./devhub-go-change/SKILL.md) — change Go packages and modules with API/concurrency safety, native documentation comments, and project-specific validation.
- [`devhub-terraform-change`](./devhub-terraform-change/SKILL.md) — change Terraform code with infrastructure-specific safety and validation.
- [`devhub-ansible-change`](./devhub-ansible-change/SKILL.md) — change Ansible roles and playbooks with idempotence, safe targeting, and validation.

Commit-message and Git handoff guidance is already included directly in all the other DevHub skills. Use `/devhub-commit-message` when you only need that step, such as after many manual changes or work with a general AI assistant without a skill. It reviews the complete pending change set, not just the latest edit, and does not require running another skill first.

Keeping it as a standalone skill gives this distinct, recurring task its own direct entry point without requiring a broader implementation or documentation workflow that is not needed. The overlap with other skills is intentional: it makes commit-message support discoverable and useful even when no other skill is active. See the shared [guidance on focused standalone skills](../AI.md#use-focused-standalone-skills) for the general rationale; this skill itself remains self-contained.

### Choosing a change skill

Every change skill begins with "Act as a senior software engineer working in the current repository." This sets the expectation to understand project context, fix root causes, preserve compatibility, make maintainable changes, and verify outcomes within the requested scope.

Use [`devhub-generic-change`](./devhub-generic-change/SKILL.md) for generic code changes, features, and bug fixes. When a tool needs more specific instructions, choose the matching tool-specific skill instead:

| Skill | Use for | Tool-specific additions |
| --- | --- | --- |
| [`devhub-python-change`](./devhub-python-change/SKILL.md) | Python packages, applications, and scripts | Interpreter compatibility, public contracts, typing, async/resource behavior, and native docstrings |
| [`devhub-go-change`](./devhub-go-change/SKILL.md) | Go packages, modules, applications, and tools | Toolchain/module boundaries, exported APIs, errors, concurrency, and native documentation comments |
| [`devhub-terraform-change`](./devhub-terraform-change/SKILL.md) | Terraform modules and configurations | Resource/state compatibility, replacement risks, provider-aware validation, and infrastructure side effects |
| [`devhub-ansible-change`](./devhub-ansible-change/SKILL.md) | Ansible roles, playbooks, and collections | Idempotence, variable precedence, handlers, inventories, and safe managed-host targeting |

The language- and tool-specific skills add compatibility, safety, documentation, and validation guidance tailored to their ecosystems. All five change skills discover the consuming project's actual test setup rather than assuming tests exist. If meaningful tests exist in the owning project or package, update or add coverage for the change using that suite; otherwise skip test creation and execution by default and report the reason. This also applies to standalone scripts without tests: a code change alone does not justify introducing a suite or framework. To add tests where none exist, explicitly request them, unless applicable project requirements already mandate them.

An existing `test/` or `tests/` directory alone is not evidence of implemented tests: generated Ansible role test playbooks and other default/basic scaffolding without real behavioral verification count as placeholders. DevHub Terraform and Ansible projects generally do not have implemented automated tests, but discovery establishes the consuming project's actual state.

Skipping tests does not skip applicable formatting, linting, syntax, or static validation. Explicit test requests and project requirements take precedence. Each change skill automatically discovers local guidance and structure, reports which files informed the work, and is self-contained; the tool-specific skills do not require invoking the generic skill first.

---

### Comments and code documentation

All change skills cover file-purpose summaries, function contracts, and selective inline comments. The generic change skill provides the most detailed guidance; each specialized skill includes its own concise, native equivalent and remains usable on its own.

The broader [documentation concepts](../../reference/engineering/Concepts.md#documentation) explain audience, placement, examples, maintenance, and why documentation should add value rather than maximize volume. This section describes how those practices are applied in AI workflows: the documentation skill handles prose and navigation, while change skills keep related explanations consistent with code. The essential rules remain inside each skill; this reference is optional background, not an installation or runtime dependency.

For new or materially changed programming-language source files and functions, add or update purpose and contract documentation where missing or inaccurate. This is generic guidance for Python, Go, and other code: use native module/function docstrings or package/declaration comments rather than forcing one syntax everywhere. Preserve required headers and directives, and avoid generated/vendor edits or unrelated documentation churn. Trivial private helpers do not need redundant boilerplate.

For YAML, HCL, templates, and similar configuration formats, comments are optional and should follow the current file and project conventions. Do not require file headers or introduce comments merely because a file is new or changed; an uncommented file can remain uncommented. Maintain useful existing comments and native descriptions, adding targeted comments only when they clarify non-obvious details.

Use inline comments only for non-obvious reasoning, constraints, edge cases, and workarounds, not narration of ordinary code. Decide length from complexity, audience, risk, and local conventions: a short summary may suffice, while subtle contracts need more detail. Keep documentation accurate as code changes.

Put setup and usage in the consuming project's README or linked guides, substantial rationale in design documentation, public contracts in native code documentation, and local implementation constraints near the affected code. Do not embed language tutorials, repeated best-practice links, or compliance reminders in source files.

Link shared practices once from the consuming project's README instead of copying them throughout its code. Document intentional exceptions with their reason, scope, and consequences in that README or linked design notes. Update the shared guidance if an exception becomes a shared decision. This is distinct from retaining concise essential rules inside standalone skills so they work independently.

### Git attribution default

DevHub skills explicitly omit `-m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"` and equivalent co-author trailers from generated Git handoffs by default; attribution is not necessary. Explicit user requests or applicable Copilot/repository instructions may require attribution, and higher-priority instructions still apply. Do not change Git configuration or bypass hooks to suppress it. Skills provide commands for review, not permission to commit or push.

---

## Use or install a skill

In a supported GitHub Copilot experience, provide the task and invoke the skill by name (for example, `/devhub-docs`) when available; Copilot may also load a skill when its description matches the task. Feature support and activation vary by Copilot product and agent harness.

See [Use external or centralized customizations across repositories](../AI.md#use-external-or-centralized-customizations-across-repositories) for repository-local installation, personal use across workspaces, and a centralized local source. Install the complete skill directory, not just `SKILL.md`, so its supporting resources remain available.

Each skill should be useful on its own. Do not build workflows that depend on Copilot chaining or invoking another skill; links to relevant background are fine, but every skill must state the process and constraints needed for its own task.

---

## Create a skill

Follow GitHub's [Creating and adding a skill](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills#creating-and-adding-a-skill) instructions for the supported folder structure and required `SKILL.md` frontmatter.

Apply the shared [authoring guidance](../AI.md#create-and-maintain-customizations), then add the skill-specific structure:

- Create `.github/skills/devhub-<short-name>/SKILL.md` with a matching lowercase, hyphenated YAML `name` and a concise `description` that explains the task and when to use the skill.
- Write the focused task procedure in the body. Add scripts or supporting resources only when useful, keep them inside the skill directory, and explain when to use them.
- Use AI to create and maintain the skill, including having it keep duplicated essential guidance consistent across skills when requirements change. Review the resulting diff yourself, verify that the skill remains accurate and self-contained for its task, and run relevant checks; AI assistance does not replace review.
- Immediately after the frontmatter, include the user-facing maintenance note linking to that exact skill's source in DevHub; label it as provenance, not required reading.
- Add or update the skill's entry in [Available skills](#available-skills).
- Include the [Git command handoff requirement](../AI.md#end-skill-reports-with-ready-to-run-git-commands) directly in the skill: end reports for Git-backed changes with `git add -A`, a concrete commit message, and the appropriate `git push` command. Warn about staging unrelated edits and do not execute the commands without authorization.
- Require the commit message to describe the full pending change set, including earlier session changes: inspect `git diff`, `git diff --cached`, and `git status --short`, and review relevant untracked files before composing it.
- State the [Git attribution default and its exceptions](#git-attribution-default) directly in every skill. For change skills, include self-contained, language-appropriate [comment and documentation guidance](#comments-and-code-documentation), keeping the generic skill the most detailed.
- For every change skill, place "Act as a senior software engineer working in the current repository." immediately after its title, as described in [Choosing a change skill](#choosing-a-change-skill).

The [`devhub-ai-customization` skill](./devhub-ai-customization/SKILL.md) provides the complete self-contained workflow for creating or maintaining a DevHub skill or agent.

---

## Examples beyond DevHub

For generic Copilot skills and examples, see [github/awesome-copilot](https://github.com/github/awesome-copilot) and the [awesome-copilot community library](https://awesome-copilot.github.com/). Review the content and bundled scripts before adding an external skill.

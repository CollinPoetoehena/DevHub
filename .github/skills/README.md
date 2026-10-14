# Reusable Agent Skills

> **Official documentation:** [Adding agent skills for GitHub Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills), including [creating and adding a skill](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills#creating-and-adding-a-skill).
>
> The rest of this page describes DevHub's conventions and recommendations; use the official docs as the source of truth for supported Copilot behavior and formats.

DevHub maintains reusable, project-independent Agent Skills under `.github/skills/`. Each skill has its own directory containing a `SKILL.md`; the required YAML `name` matches the directory name. DevHub skill names use the `devhub-` prefix.

Skills capture reusable task instructions, repeatable processes, and multi-step workflows as well as specialized knowledge. Supporting scripts and resources are optional; a repeatable process can be useful as a skill on its own.

> **Prefer skills over prompt files:** Do not create new `.prompt.md` files for DevHub; use skills for reusable tasks and processes instead. VS Code has deprecated prompt files for Agent Host sessions, where they are not loaded, although they still work with the Local agent for now. See the [central recommendation](../AI.md#which-customization-should-i-use) and [official migration guidance](https://code.visualstudio.com/docs/agent-customization/migrate-customizations#_convert-prompt-files-to-skills). Ordinary one-off chat prompts remain appropriate.

## Table of contents

- [Available skills](#available-skills)
  - [Choosing a change skill](#choosing-a-change-skill)
- [Use or install a skill](#use-or-install-a-skill)
- [Create a skill](#create-a-skill)
- [Examples beyond DevHub](#examples-beyond-devhub)

---

## Available skills

- [`devhub-create-ai-customization`](./devhub-create-ai-customization/SKILL.md) — create or maintain a self-contained DevHub skill or custom agent (mainly used in this DevHub repository itself, but reusable across other repositories as well).
- [`devhub-docs`](./devhub-docs/SKILL.md) — create or update documentation using the owning project's conventions (can be used for any project since it is not tied to DevHub-specific practices, it automatically adapts to the project's existing documentation structure and guidelines).
- [`devhub-generic-change`](./devhub-generic-change/SKILL.md) — implement and verify generic code changes using discovered project conventions (see specific skills below for more specific tool guidance, such as Ansible, etc.).
- [`devhub-terraform-change`](./devhub-terraform-change/SKILL.md) — change Terraform code with infrastructure-specific safety and validation.
- [`devhub-ansible-change`](./devhub-ansible-change/SKILL.md) — change Ansible roles and playbooks with idempotence, safe targeting, and validation.

### Choosing a change skill

Use [`devhub-generic-change`](./devhub-generic-change/SKILL.md) for generic code changes, features, and bug fixes. When a tool needs more specific instructions, choose the matching tool-specific skill instead:

| Skill | Use for | Tool-specific additions |
| --- | --- | --- |
| [`devhub-terraform-change`](./devhub-terraform-change/SKILL.md) | Terraform modules and configurations | Resource/state compatibility, replacement risks, provider-aware validation, and infrastructure side effects |
| [`devhub-ansible-change`](./devhub-ansible-change/SKILL.md) | Ansible roles, playbooks, and collections | Idempotence, variable precedence, handlers, inventories, and safe managed-host targeting |

These skills exist because infrastructure changes need additions to the generic code-change workflow, including a different approach to testing. DevHub Terraform and Ansible projects generally do not have implemented automated tests. Each skill discovers the consuming project's actual test setup: if meaningful tests exist, update or add coverage for the change; otherwise skip test creation and execution by default and report the reason. An existing `test/` or `tests/` directory alone is not evidence of implemented tests: generated Ansible role test playbooks and other default/basic scaffolding without real behavioral verification count as skipped.

Skipping tests does not skip applicable formatting, linting, syntax, or static validation. Explicit test requests and project requirements take precedence. Each change skill automatically discovers local guidance and structure, reports which files informed the work, and is self-contained; the tool-specific skills do not require invoking the generic skill first.

---

## Use or install a skill

In a supported GitHub Copilot experience, provide the task and invoke the skill by name (for example, `/devhub-docs`) when available; Copilot may also load a skill when its description matches the task. Feature support and activation vary by Copilot product and agent harness.

See [Use external or centralized customizations across repositories](../AI.md#use-external-or-centralized-customizations-across-repositories) for repository-local installation, personal use across workspaces, and a centralized local source. Install the complete skill directory, not just `SKILL.md`, so its supporting resources remain available.

Each skill should be useful on its own. Do not build workflows that depend on Copilot chaining or invoking another skill; links to relevant background are fine, but every skill must state the process and constraints needed for its own task.

---

## Create a skill

Follow GitHub's [Creating and adding a skill](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills#creating-and-adding-a-skill) instructions for the supported folder structure and required `SKILL.md` frontmatter.

For requests to create or maintain a skill or custom agent in DevHub, use the [`devhub-create-ai-customization` skill](./devhub-create-ai-customization/SKILL.md). The guidance below is general design context; that skill adds the DevHub-specific workflow and requirements.

Make the design choice deliberately. A skill is worthwhile when a repeatable workflow or specialized capability adds more value than the effort of creating and maintaining it. Do not create one for every small task or minor variation; combine closely related work when it shares a process, and split workflows only when the differences matter. Keep the skill self-contained rather than linking it to another skill as a required next step. This avoids an unreliable dependency chain and makes each skill usable even where cross-skill invocation is unsupported. Some duplication is acceptable; Copilot can help create and maintain the text, but a person should still review it.

When creating a reusable DevHub skill, use the `devhub-` prefix, keep the description clear about when Copilot should use it, and avoid assumptions about the consuming project's architecture or commands. Link to project-specific guidelines only when they are available in the consuming repository; the generic [`devhub-docs`](./devhub-docs/SKILL.md) workflow, for example, allows a repository to supply its own writing guidelines.

Build automatic context discovery into the skill: inspect project instructions, documentation, relevant code, manifests, configuration, and CI, then search beyond common filenames when needed. This keeps the skill generic across repositories and avoids requiring users to supply custom paths, guideline files, or commands already available in the project. Ask only for information or decisions that cannot be safely discovered, and never infer authorization from a discovered command. Require the completion report to identify the files actually used for guidelines and structure, plus inferred conventions or missing guidance.

---

## Examples beyond DevHub

For generic Copilot skills and examples, see [github/awesome-copilot](https://github.com/github/awesome-copilot) and the [awesome-copilot community library](https://awesome-copilot.github.com/). Review the content and bundled scripts before adding an external skill.

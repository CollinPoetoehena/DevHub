# Home Lab

This is the central documentation for my personal home lab. It covers the goals, design, and step-by-step setup from buying hardware to a running cluster with Kubernetes, monitoring, and GitOps automation.

> **Why in DevHub?**: The `homelab` is basically my *development platform* at home, which closely relates to `DevHub`: my central development hub. Therefore, everything related to my `homelab` is documented and managed within the `DevHub` repository for consistency and centralization.

---

## Table of Contents

- [Documentation Design](#documentation-design)
- [AI-Assisted Work](#ai-assisted-work)
- [Infrastructure Automation](#infrastructure-automation)
- [Reference](#reference)

---

## Documentation Design

The documentation has three main components:
1. **[Security and Public Repository](./docs/0_Security_and_Public_Repository.md)**: What is safe to publish, how to handle secrets, and what to do if sensitive information is exposed.
2. **[Design](./docs/1_Design/README.md)**: Overview of the home lab design, including personal goals, network topology, node setup, and overall architecture.
3. **[Setup](./docs/2_Setup/README.md)**: Step-by-step guide for setting up the home lab, using the design as a reference.

---

## AI-Assisted Work

> For broader guidance on AI concepts, tools, workflows, and usage, including how to use skills in VS Code and Copilot, see the [DevHub AI reference](../reference/AI.md).

Homelab skills use the **Agent Skills `SKILL.md` format**: each skill is a `SKILL.md` file inside `.github/skills/<skill-name>/`, with YAML frontmatter whose `name` matches the folder name. Every homelab skill must use the `homelab-` prefix (for example, `homelab-project` in `../.github/skills/homelab-project/SKILL.md`). Store future homelab skills in the DevHub repository-root `.github/skills/` directory, not in this nested `homelab/` folder, because VS Code discovers workspace skills from recognized skill directories at the workspace/repository root.

Use [`homelab-project`](../.github/skills/homelab-project/SKILL.md) for reusable homelab context. It directs AI assistants to the project overview, design boundaries, and security rules. Invoke `/homelab-project` followed by your question or task; compatible assistants may also load it automatically when relevant. For more specific tasks, choose a task skill that matches your current objective. All task skills below apply the project skill as required context in their `SKILL.md` files. Invoke the one that matches your task:

| Skill | Use it for | Invoke |
| --- | --- | --- |
| [`homelab-implement-change`](../.github/skills/homelab-implement-change/SKILL.md) | Focused homelab code changes and bug fixes. | `/homelab-implement-change <request>` |
| [`homelab-docs`](../.github/skills/homelab-docs/SKILL.md) | Creating or updating homelab Markdown documentation, following its structure and security conventions. | `/homelab-docs <request>` |

If you open `homelab/` by itself as a workspace, [its workspace settings](./.vscode/settings.json) enable `chat.useCustomizationsInParentRepositories` so VS Code can discover project skills in the parent DevHub repository. If the skills still do not appear, confirm that Agent Skills are enabled in your VS Code/Copilot setup, then reload the window or start a fresh chat.

---

## Reference

The [DevHub Reference](../reference/README.md) documentation in `DevHub` serves as a central repository and contains theoretical knowledge, useful commands, and quick-reference information that complements the setup documentation above.

> **Note:** The reference documentation is not in `homelab/docs/` because it is centralized in the `reference/` folder within `DevHub` for easier maintenance and reuse across multiple projects. See [DevHub Reference](../reference/README.md) for the full index and details.

---
# Home Lab

This is the central documentation for my personal home lab. It covers the goals, design, and step-by-step setup from buying hardware to a running cluster with Kubernetes, monitoring, and GitOps automation.

> **Why in DevHub?**: The `homelab` is basically my *development platform* at home, which closely relates to `DevHub`: my central development hub. Therefore, everything related to my `homelab` is documented and managed within the `DevHub` repository for consistency and centralization.

---

## Table of Contents

- [Documentation Design](#documentation-design)
- [AI-Assisted Work](#ai-assisted-work)
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

Homelab skills use the **Agent Skills `SKILL.md` format**: each skill is a `SKILL.md` file inside `.github/skills/<skill-name>/`, with YAML frontmatter whose `name` matches the folder name. Every homelab skill must use the `homelab-` prefix (for example, `homelab-project` in `.github/skills/homelab-project/SKILL.md`). Use this same format, location, and naming convention for any future homelab skills so they are project-scoped and discoverable as `/homelab-<skill-name>` commands in Copilot Chat.

The [homelab project skill](./.github/skills/homelab-project/SKILL.md) provides reusable project context: it directs AI assistants to the homelab overview, design boundaries, and security rules before they answer questions or make changes. Invoke it with `/homelab-project` followed by your question or task; compatible assistants may also load it automatically when relevant.

For a focused code change, invoke [`homelab-implement-change`](./.github/skills/homelab-implement-change/SKILL.md) with `/homelab-implement-change` followed by the requested change; it is instructed to apply the homelab project skill as required context. To create or edit homelab Markdown, use [`homelab-update-docs`](./.github/skills/homelab-update-docs/SKILL.md) with `/homelab-update-docs` and describe the documentation change; it also applies the project skill and its formatting and security conventions.

---

## Reference

The [DevHub Reference](../reference/README.md) documentation in `DevHub` serves as a central repository and contains theoretical knowledge, useful commands, and quick-reference information that complements the setup documentation above.

> **Note:** The reference documentation is not in `homelab/docs/` because it is centralized in the `reference/` folder within `DevHub` for easier maintenance and reuse across multiple projects. See [DevHub Reference](../reference/README.md) for the full index and details.

---
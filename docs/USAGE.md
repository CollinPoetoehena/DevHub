# Using DevHub

How to set up DevHub for my personal projects: the shared workspace, the AI customizations, and how projects link to DevHub's standards. DevHub is the central place for these instructions; personal project repositories link here instead of repeating them.

---

## Table of Contents

- [Personal project workspace](#personal-project-workspace)
- [AI customizations](#ai-customizations)
- [Applying DevHub standards in a project](#applying-devhub-standards-in-a-project)
- [Task-oriented how-tos](#task-oriented-how-tos)

---

## Personal project workspace

Clone DevHub and the personal projects you work on together under a shared parent folder, for example:

```text
devhub-workspace/
|-- DevHub/
|-- devhub-homelab/
|-- devhub-homelab-private/
`-- <other personal project>/
```

Open the parent folder in VS Code, or add the selected clones to a [multi-root workspace](https://code.visualstudio.com/docs/editing/workspaces/multi-root-workspaces). Use the shared workspace when working across multiple repositories, or open just one repository in a separate window when focusing on that project. Both approaches remain available; grouping repositories does not require always opening them together. Each clone remains its own Git repository with its own history, remote, and permissions, and private access is not required to work with the public projects.

One workspace makes it easier to navigate and edit related repositories together and gives AI tools access to their shared context. For example, when the homelab uses DevHub guidance or reusable code, an agent can inspect both the source and its consumer and make coordinated edits instead of relying on copied context. Keep the included repositories and AI context relevant to the task.

Keep machine-specific workspace files outside Git. Grouping repositories does not merge their permissions or install AI customizations; choose the workspace-root or repository-root setup below.

---

## AI customizations

The [APM design and setup guide](../packages/apm/README.md) owns the cross-repository AI configuration pattern: a common baseline in every repository, optional domain packages, and one root `AGENTS.md` for local guidance. Follow its [repository setup](../packages/apm/README.md#repository-setup), [activation checks](../packages/apm/README.md#verify-activation), and [maintenance procedure](../packages/apm/README.md#maintenance-and-validation). The [common package README](../packages/apm/common/README.md) owns package-specific contents and decisions.

Use the manifest and installation procedure in [repository setup](../packages/apm/README.md#repository-setup) for each consumer root. DevHub's [root manifest](../apm.yml) uses the local `./packages/apm/common` dependency for development.

For shared-folder use, you can also place an `apm.yml` in the parent folder (`devhub-workspace/` in the example), declare the same dependency, and run the install command from there. Opening that parent folder in VS Code makes the installed AI customizations available across its repositories, subject to host discovery support. This does not install them into each clone: keep a repository-level manifest and installation when you also want the customizations available with only that repository open. For a multi-root workspace, verify discovery in the selected host rather than assuming a parent-folder installation is loaded.

Select **Orchestrator** in VS Code Chat; refresh or reopen the chat if necessary. A manifest entry alone does not activate the package. Follow [repository setup](../packages/apm/README.md#repository-setup) and [choosing an agent](../packages/apm/README.md#choosing-an-agent) for discovery and host limitations.

Keep repository-specific agent context in a root `AGENTS.md` ([DevHub's file](../AGENTS.md)), linking to owning documentation instead of repeating it. Use the [authoring guidance](../packages/apm/README.md#authoring-repository-guidance) or [setup skill](../packages/apm/common/.apm/skills/setup-ai-customizations/SKILL.md). Scoped constraints and project-only procedures remain separate where needed; do not copy shared agents or assume local instructions override the baseline.

My default is **Auto** model selection where offered; choose an explicit model when results or cost warrant it. Options depend on the host and account; see [VS Code model selection](https://code.visualstudio.com/docs/agent-customization/language-models#use-auto-model-selection). If GitHub Copilot credits are exhausted, check the access, models, and limits available to your account in alternatives such as [Microsoft Copilot](https://www.microsoft.com/en-us/copilot/solutions/individuals); do not assume a particular model is included.

---

## Applying DevHub standards in a project

- Follow the shared [repository and package guidelines](GUIDELINES.md), and link to relevant DevHub guidance from the project README instead of copying it.
- Use the APM guide's [guidance layers](../packages/apm/README.md#how-guidance-is-layered) for shared standards and role guidance, and the [central backlog](how-to/TASK-TRACKING.md) for all personal projects, including the homelab.
- Keep project-specific decisions, setup, and exceptions in the project's own documentation.
- Follow [DevHub's project structure](ARCHITECTURE.md#separate-repositories) to decide whether work belongs in DevHub or in its own repository.

---

## Task-oriented how-tos

The [how-to index](how-to/README.md) provides task entry points. Start with [creating a repository](how-to/CREATE-REPOSITORY.md) for a new personal project; it links to the authoritative Terraform inventory, review, and rollout procedure rather than repeating it. Use [setting up a code editor](how-to/SET-UP-CODE-EDITOR.md) when preparing a new device or reinstalling VS Code, Git, and SSH.

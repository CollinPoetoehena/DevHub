# Using DevHub

How to set up DevHub for my personal projects: the shared workspace, the AI customizations, and how projects link to DevHub's standards. DevHub is the central place for these instructions; personal project repositories link here instead of repeating them.

---

## Table of Contents

- [Personal project workspace](#personal-project-workspace)
- [AI customizations](#ai-customizations)
- [Applying DevHub standards in a project](#applying-devhub-standards-in-a-project)

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

The [common APM package](../packages/apm/common/README.md) distributes reusable role agents, scoped language/tool instructions, and on-demand skills. Generic coding, documentation, and testing standards live in its shared common instruction file. See [concepts and layering](../packages/apm/common/README.md#ai-customizations-concepts-and-layering) for the division of responsibilities.

Declare `CollinPoetoehena/DevHub/packages/apm/common` under `dependencies.apm` in each consumer repository's `apm.yml`. DevHub's [root manifest](../apm.yml) uses the local `./packages/apm/common` dependency instead. With [APM installed](https://microsoft.github.io/apm/consumer/), open the consumer workspace root and run:

```sh
apm install --only apm --target copilot
```

For shared-folder use, you can also place an `apm.yml` in the parent folder (`devhub-workspace/` in the example), declare the same dependency, and run the install command from there. Opening that parent folder in VS Code makes the installed AI customizations available across its repositories, subject to host discovery support. This does not install them into each clone: keep a repository-level manifest and installation when you also want the customizations available with only that repository open. For a multi-root workspace, verify discovery in the selected host rather than assuming a parent-folder installation is loaded.

Select **Orchestrator** in VS Code Chat; refresh or reopen the chat if necessary. A manifest entry alone does not activate the package. Follow [installation](../packages/apm/common/README.md#installation) and [choosing an agent](../packages/apm/common/README.md#choosing-an-agent) for discovery and host limitations.

Keep repository-wide context in each project's `.github/copilot-instructions.md` ([DevHub's file](../.github/copilot-instructions.md)), scoped constraints in instruction files, and project-only procedures in skills. Follow [consumer-specific guidance](../packages/apm/common/README.md#consumer-specific-guidance) for extension locations and shared sibling packages; do not copy specialist agents or assume local instructions automatically override shared ones.

My default is **Auto** model selection where offered; choose an explicit model when results or cost warrant it. Options depend on the host and account; see [VS Code model selection](https://code.visualstudio.com/docs/agent-customization/language-models#use-auto-model-selection). If GitHub Copilot credits are exhausted, check the access, models, and limits available to your account in alternatives such as [Microsoft Copilot](https://www.microsoft.com/en-us/copilot/solutions/individuals); do not assume a particular model is included.

---

## Applying DevHub standards in a project

- Follow the shared [repository and package guidelines](GUIDELINES.md), and link to relevant DevHub guidance from the project README instead of copying it.
- Use the common package's [guidance layers](../packages/apm/common/README.md#how-guidance-is-layered) for shared standards and role guidance, and the [central backlog](TASK-TRACKING.md) for all personal projects, including the homelab.
- Keep project-specific decisions, setup, and exceptions in the project's own documentation.
- Follow [DevHub's project structure](ARCHITECTURE.md#separate-repositories) to decide whether work belongs in DevHub or in its own repository.

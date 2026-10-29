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

Open the parent folder in VS Code, or add the selected clones to a [multi-root workspace](https://code.visualstudio.com/docs/editing/workspaces/multi-root-workspaces). Include only the projects you regularly work on together; open a project on its own for isolated work. Each clone remains its own Git repository with its own history, remote, and permissions, and private access is not required to work with the public projects.

The workspace keeps shared guidance, reusable code, and their consumers together for navigation and coordinated work. Keep machine-specific workspace files outside Git. Grouping repositories does not merge their permissions or install AI customizations into every clone; use the consumer-root setup below and keep AI context focused on the task.

---

## AI customizations

The [common APM package](../packages/apm/common/README.md) distributes reusable role agents, scoped language/tool instructions, and on-demand skills. Generic coding, documentation, and testing standards live in their respective agents; there is no all-files general coding instruction. See [concepts and design](../packages/apm/common/README.md#ai-customizations-concepts-and-design) for the division of responsibilities.

Declare `CollinPoetoehena/DevHub/packages/apm/common` under `dependencies.apm` in each consumer repository's `apm.yml`. DevHub's [root manifest](../apm.yml) uses the local `./packages/apm/common` dependency instead. With [APM installed](https://microsoft.github.io/apm/consumer/), open the consumer workspace root and run:

```sh
apm install --only apm --target copilot
```

Select **Orchestrator** in VS Code Chat; refresh or reopen the chat if necessary. A manifest entry alone does not activate the package. Follow [Using the Orchestrator](../packages/apm/common/README.md#using-the-orchestrator) for discovery and host limitations.

Keep repository-wide context in each project's `.github/copilot-instructions.md` ([DevHub's file](../.github/copilot-instructions.md)), scoped constraints in instruction files, and project-only procedures in skills. Follow [project-specific guidance](../packages/apm/common/README.md#project-specific-guidance) for extension locations and shared sibling packages; do not copy specialist agents or assume local instructions automatically override shared ones.

My default is **Auto** model selection where offered; choose an explicit model when results or cost warrant it. Options depend on the host and account; see [VS Code model selection](https://code.visualstudio.com/docs/agent-customization/language-models#use-auto-model-selection). If GitHub Copilot credits are exhausted, check the access, models, and limits available to your account in alternatives such as [Microsoft Copilot](https://www.microsoft.com/en-us/copilot/solutions/individuals); do not assume a particular model is included.

---

## Applying DevHub standards in a project

- Follow the shared [repository and package guidelines](GUIDELINES.md), and link to relevant DevHub guidance from the project README instead of copying it.
- Use the common package's [agent standards](../packages/apm/common/README.md#agent-standards) for shared role guidance and the [central backlog](TASK-TRACKING.md) for all personal projects, including the homelab.
- Keep project-specific decisions, setup, and exceptions in the project's own documentation.
- Follow [DevHub's project structure](ARCHITECTURE.md#separate-repositories) to decide whether work belongs in DevHub or in its own repository.

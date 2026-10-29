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

The workspace keeps shared standards, reusable code, and their consumers in one window, so related changes and AI context stay consistent. See [grouping related repositories in VS Code workspaces](../reference/Code_Editor.md#grouping-related-repositories-in-vs-code-workspaces) for the generic rationale and trade-offs, and the rest of the [code editor guide](../reference/Code_Editor.md) for editor, account, and Git setup.

---

## AI customizations

TODO: explain here it uses the [apm/common/README.md](../packages/apm/common/README.md) for AI customizations, which defines the baseline instructions, language instructions, skills, and agents applied across the personal project workspace.

TODO: explain here the [copilot-instructions.md](../.github/copilot-instructions.md) for DevHub-specific AI customizations, which builds on top of the common instructions defined in the APM package (the common APM package uses these instructions for DevHub specific edits). TODO: reference to README.md section in the [apm/common/README.md](../packages/apm/common/README.md) that explains how to extend it and provide specific instructions for a project, etc.

TODO: add here shortly the old AI part with the model selection: auto model by default because it selects good, if needed or selects the more expensive model too often you can manually select but auto is best. And if credits done from GitHub Copilot, can use Microsoft Copilot with a good model like Claude Sonnet or another one also, etc.

---

## Applying DevHub standards in a project

- Link to the relevant DevHub guidance from the project README instead of copying it; see the [package README link](PROJECT-STRUCTURE.md#package-readme-link).
- Apply the shared [conventions and standards](CONVENTIONS_STANDARDS.md) and use the [central backlog](TASK-TRACKING.md) for all personal projects, including the homelab.
- Keep project-specific decisions, setup, and exceptions in the project's own documentation.
- Follow [DevHub's project structure](PROJECT-STRUCTURE.md#separate-repositories) to decide whether work belongs in DevHub or in its own repository.

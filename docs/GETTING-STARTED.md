# Getting Started

This guide covers getting started in DevHub, setting up a shared workspace, and using DevHub guidance from personal projects. DevHub is the central place for these instructions; personal project repositories link here instead of repeating them.

---

## Table of Contents

- [Getting started in this repository](#getting-started-in-this-repository)
- [Personal project workspace](#personal-project-workspace)
- [AI customizations](#ai-customizations)
- [Applying DevHub standards in a project](#applying-devhub-standards-in-a-project)
- [Task-oriented how-tos](#task-oriented-how-tos)

---

## Getting started in this repository

Clone DevHub and open the repository root in VS Code. Start with the [repository overview](../README.md), then follow [DevHub's own setup](../packages/apm/README.md#devhubs-own-setup) to install its local AI customization package. For where project and component documentation belongs, see [Documentation Design](GUIDELINES.md#documentation-design), especially [Documentation ownership](GUIDELINES.md#documentation-ownership).

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

Keep machine-specific workspace files outside Git. Grouping repositories does not merge their permissions or install AI customizations; use the repository-root setup below, optionally supplemented by a workspace-root installation.

---

## AI customizations

The [APM design and setup guide](../packages/apm/README.md) owns the cross-repository AI configuration pattern: a common baseline in every repository, optional domain packages, and one root `AGENTS.md` for local guidance. Follow its [repository setup](../packages/apm/README.md#repository-setup), [activation checks](../packages/apm/README.md#verify-activation), and [maintenance procedure](../packages/apm/README.md#maintenance-and-validation). The [common package README](../packages/apm/common/README.md) owns package-specific contents and decisions.

Use the manifest and installation procedure in [repository setup](../packages/apm/README.md#repository-setup) for each consumer root. DevHub's [root manifest](../apm.yml) uses the local `./packages/apm/common` dependency for development.

For shared-folder use, optionally add an `apm.yml` in the parent folder (`devhub-workspace/` in the example):

```yaml
name: devhub-workspace
version: 1.0.0
targets:
  - copilot
dependencies:
  apm:
    - CollinPoetoehena/DevHub/packages/apm/common
```

With APM installed, run from that workspace root:

```sh
apm install --only apm --target copilot
```

This is an additional convenience, not a replacement for a checked-in manifest/lockfile and installation in every consumer repository. It installs at the parent root, not into each clone. Follow the APM guide's dependency-reference and ownership guidance for both setups. Verify that the selected host discovers the parent-installed customizations, especially in multi-root workspaces; opening a shared folder does not guarantee discovery. Verify standalone repository use separately.

Use native Agent mode for ordinary work. For a complex task, use the [two-session workflow](../packages/apm/README.md#choosing-a-workflow): plan and approve first, then select **Orchestrator** in a fresh session with the saved approved plan. A manifest entry alone does not activate the package; follow [repository setup](../packages/apm/README.md#repository-setup) and [activation checks](../packages/apm/README.md#verify-activation).

Keep repository-specific agent context in a root `AGENTS.md` ([DevHub's file](../AGENTS.md)), linking to owning documentation instead of repeating it. Use the [authoring guidance](../packages/apm/README.md#authoring-repository-guidance) and APM [repository setup](../packages/apm/README.md#repository-setup). Scoped constraints and project-only procedures remain separate where needed; do not copy shared agents or assume local instructions override the baseline.

Follow the APM guide's [agent configuration](../packages/apm/README.md#agent-configuration) and [runtime-managed model selection](../packages/apm/README.md#runtime-managed-model-selection) for harness, permission, and model choices. Available models and costs vary by host, account, and policy; check the linked official references rather than assuming a particular model or plan is available.

---

## Applying DevHub standards in a project

- Follow the shared [repository and package guidelines](GUIDELINES.md), and link to relevant DevHub guidance from the project README instead of copying it.
- Use the APM guide's [guidance layers](../packages/apm/README.md#how-guidance-is-layered) for shared standards and role guidance, and the [central backlog](how-to/TASK-TRACKING.md) for all personal projects, including the homelab.
- Keep project-specific decisions, setup, and exceptions in the project's own documentation.
- Follow [DevHub's project structure](ARCHITECTURE.md#separate-repositories) to decide whether work belongs in DevHub or in its own repository.

---

## Task-oriented how-tos

The [how-to index](how-to/README.md) provides task entry points. Start with [creating a repository](how-to/CREATE-REPOSITORY.md) for a new personal project; it links to the authoritative Terraform inventory, review, and rollout procedure rather than repeating it. Use [setting up a code editor](how-to/SET-UP-CODE-EDITOR.md) when preparing a new device or reinstalling VS Code, Git, and SSH.

# DevHub Agent Guidance

DevHub is the central development hub for my personal projects. Start with the [repository overview](README.md) for its purpose and scope; it is public, but broad third-party compatibility is not a design goal.

## Shared baseline

- Follow the [common engineering instructions](packages/apm/common/.apm/instructions/common.instructions.md) and matching technology/tool instructions in the [common APM package](packages/apm/common/README.md). These supplement this repository's guidance; surface conflicts rather than assuming an override.
- The [root manifest](apm.yml) declares the local common package. Declaration is not activation; use the [AI setup guide](packages/apm/README.md#repository-setup) to install and verify it for the selected harness.

---

## Find the owning context

Read only the documentation relevant to the task, then inspect the affected implementation and configuration:

| Work | Entry point |
|---|---|
| Repository boundaries, placement, and release decisions | [Architecture](docs/ARCHITECTURE.md) and [repository/package guidelines](docs/GUIDELINES.md) |
| Packages and their component contracts | [Packages overview](packages/README.md), then the affected package's README and native metadata |
| Shared AI configuration and setup | [APM design and setup](packages/apm/README.md), then the [common package](packages/apm/common/README.md) or affected domain package |
| Shared automation | [Tools overview](tools/README.md), then the affected tool's README |
| Workspace and related repositories | [Using DevHub](docs/USAGE.md) |
| Issues, planning, and privacy | [Central task tracking](docs/how-to/TASK-TRACKING.md) |
| Retired approaches | [Archive](archive/README.md); do not treat historical material as active guidance |

---

## DevHub-specific working conventions

- Keep project-specific implementation and operational details in the owning project. Do not absorb sibling repositories into DevHub or change their files merely because they share a workspace.
- Keep reusable AI practices in package sources; keep DevHub-only context here or in its owning documentation. Edit APM sources, not installed copies, and preserve consumer-owned customizations during installation.
- Link to existing architecture, setup, and component documentation instead of copying it into instructions. Add inline guidance only for an agent-critical constraint or decision not adequately covered there.
- Use the affected component's documented validation commands, native configuration, and CI. DevHub is not one application with one repository-wide build or test command.
- Keep private project context out of public documentation and issues; follow the task-tracking guide's visibility rules.

---

## Instruction layout

DevHub uses this single root file, which routes agents to owning READMEs and focused documentation. No nested `AGENTS.md` files are needed for the current repository, and no duplicate repository-wide Copilot instruction file is maintained. Add a nested file only for a demonstrated gap that meets the [exception criteria](packages/apm/README.md#nested-instructions).

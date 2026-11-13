# DevHub Agent Guidance

DevHub is the central development hub for my personal projects. Start with the [repository overview](README.md) for its purpose and scope; it is public, but broad third-party compatibility is not a design goal.

## Shared baseline

- Read applicable shared engineering standards under [`guidelines-core` instructions](packages/apm/guidelines-core/.apm/instructions/), and use matching instruction maps in relevant opt-in [`development-*` stack packages](packages/apm/README.md#package-design) when available. These supplement DevHub's repository guidance; surface conflicts rather than assuming a universal host precedence.
- The [root manifest](apm.yml) declares only the local `guidelines-core` source. The workflow and stack packages are separate local-development choices. A manifest entry or validated source is not proof of installation or activation; use the [AI setup guide](packages/apm/README.md#repository-setup) to choose packages and verify the selected host and scope.

---

## Find the owning context

Read only the documentation relevant to the task, then inspect the affected implementation and configuration:

| Work | Entry point |
|---|---|
| Repository boundaries, placement, and release decisions | [Architecture](docs/ARCHITECTURE.md) and [repository/package guidelines](docs/GUIDELINES.md) |
| Packages and their component contracts | [Packages overview](packages/README.md), then the affected package's README and native metadata |
| Shared AI configuration and setup | [APM design and setup](packages/apm/README.md), then [`guidelines-core`](packages/apm/guidelines-core/README.md), [`development-core`](packages/apm/development-core/README.md), or the affected stack package |
| Shared automation | [Tools overview](tools/README.md), then the affected tool's README |
| Workspace and related repositories | [Getting started](docs/GETTING-STARTED.md) |
| Issues, planning, and privacy | [Central task tracking](docs/how-to/TASK-TRACKING.md) |
| Retired approaches | [Archive](archive/README.md); do not treat historical material as active guidance |

---

## DevHub-specific working conventions

- Keep project-specific implementation and operational details in the owning project. Do not absorb sibling repositories into DevHub or change their files merely because they share a workspace.
- Keep reusable AI practices in package sources; keep DevHub-only context here or in its owning documentation. Edit APM sources, not installed copies, and preserve consumer-owned customizations during installation.
- Handle simple, clear tasks directly in the native Agent with applicable guidance and checks; neither workflow skill nor forced Implementer delegation is required. For larger work, use Planning first, review and approve the exact saved plan, then start a fresh native Agent session for Implementation Orchestration. The [APM guide](packages/apm/README.md#choosing-a-workflow) owns the invocation examples and host limitations.
- Link to existing architecture, setup, and component documentation instead of copying it into instructions. Add inline guidance only for an agent-critical constraint or decision not adequately covered there.
- Use the affected component's documented validation commands, native configuration, and CI. DevHub is not one application with one repository-wide build or test command.
- Keep private project context out of public documentation and issues; follow the task-tracking guide's visibility rules.

---

## Instruction layout

DevHub uses this single root file, which routes agents to owning READMEs and focused documentation. No nested `AGENTS.md` files are needed for the current repository, and no duplicate repository-wide Copilot instruction file is maintained. Add a nested file only for a demonstrated gap that meets the [exception criteria](packages/apm/README.md#how-guidance-is-layered).

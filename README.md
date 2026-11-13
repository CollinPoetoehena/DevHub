# DevHub

**DevHub is my central development hub: the standards, reusable resources, and entry point I use for all my personal projects.** I maintain it primarily for myself: to record project decisions, keep useful guidance and tools easy to find, and connect the projects I work on. It is also public, so it can serve as a portfolio that shows how I approach development, automation, documentation, and ongoing learning.

The name reflects the purpose:

- **Dev** means development and DevOps: building, automating, and learning through practical work.
- **Hub** means a central place to navigate to the related resources and projects.

---

## Table of Contents

- [Why I Maintain DevHub](#why-i-maintain-devhub)
- [Standards for my personal projects](#standards-for-my-personal-projects)
  - [Public, but not a generic toolbox](#public-but-not-a-generic-toolbox)
- [Repository scope](#repository-scope)
- [Task tracking](#task-tracking)
- [What belongs in DevHub](#what-belongs-in-devhub)
- [Separate projects](#separate-projects)

> **Scope of this README:** This is a concise introduction to DevHub's purpose and structure, not a full explanation of every area or project. More detail belongs in the relevant documentation linked below; the root README should stay short enough to work as a clear entry point.

For documentation changes, follow the owning project's instructions and the shared [documentation guidelines](packages/apm/guidelines-core/.apm/instructions/documentation.instructions.md).

---

## Why I Maintain DevHub

For me, the greater value is in thinking and judgment, not memorizing facts. I care more about understanding why something works, analyzing unfamiliar problems, weighing trade-offs, and applying what I learn than being able to recall every detail. Knowing where to find information is part of that, but so is judging whether it is reliable, relevant, and appropriate for the situation.

An often-attributed Einstein quote captures this distinction, although I have not verified this exact wording in a primary source:

> “Why should I fill my brain with facts I can find in two minutes in any standard reference book?”

A related statement has a documented attribution: when asked about the speed of sound in 1921, Einstein reportedly explained that such information was readily available in books and emphasized:

> “The value of a college education is not the learning of many facts but the training of the mind to think.”
>
> — Albert Einstein, as reported in *The New York Times*, May 18, 1921; source details collected on [Wikiquote](https://en.wikiquote.org/wiki/Albert_Einstein).

For me, the lesson is not that knowledge is unimportant or that looking something up is enough. Foundational knowledge gives me the context to ask better questions, connect ideas, and recognize when an answer does not make sense. A reference can supply a command, definition, or technical detail; I still need to understand the problem, question assumptions, and decide whether that information applies. Collecting facts is not the goal: knowledge becomes valuable through understanding, sound judgment, and practical use.

This also means becoming comfortable with not knowing: asking questions, testing ideas, and learning through unfamiliar or uncomfortable work. Tools and technologies change, so I value the ability to keep learning and adapting more than memorizing today's answers. DevHub supports that mindset by keeping useful knowledge accessible and making my reasoning, assumptions, and decisions available to revisit as my understanding develops.

Writing down project-specific decisions, constraints, and setup helps me return to work without rediscovering its context. It does not create an obligation to record everything I learn. General knowledge belongs in authoritative documentation, not a parallel encyclopedia; the [reference retirement decision](archive/REFERENCE.md) explains why I no longer maintain one.

Maintaining DevHub is worthwhile because it turns individual problem-solving into resources I can reuse: across future tasks, across separate projects, and when reviewing why a decision was made. Shared scripts, workflows, and project guidance help me apply practices consistently without copying the same guidance into every project. I curate this for practical use, not exhaustive knowledge collection.

The public repository has a second purpose as a portfolio. It provides an honest view of the work behind my projects—not only finished code, but also the designs, trade-offs, automation, and learning that shaped them. The portfolio aspect is valuable, but it is secondary to the repository's role as a working hub for myself. I want it to remain useful and maintainable for my own development, rather than turn it into a showcase that is disconnected from the work I actually do.

---

## Standards for my personal projects

DevHub holds the guidance I apply to my personal projects: [repository and package guidelines](docs/GUIDELINES.md), [personal-project principles](docs/GUIDELINES.md#relaxation-and-enjoyment-over-productivity-and-pressure), [shared AI guidelines and local development customizations](packages/apm/README.md), [project boundaries](docs/ARCHITECTURE.md), automation, and tooling. Each project records its own setup, decisions, and exceptions; general technical background is linked to official sources where needed.

I manage my personal projects the way a professional team manages its projects, with consistent standards and practices; they are effectively a team with one developer. This is not to mimic enterprise or industry practice. It is worth the time because it adds real value: clear and consistent projects, automation and tooling that save me time, and documentation that keeps decisions self-explanatory when I return to a project later.

### Public, but not a generic toolbox

DevHub is not a collection of generic tools, AI skills, and other resources built for anyone to use. Its purpose is my personal development hub and the management of my personal projects, and those two goals conflict: you cannot do both well in one repository.

It remains public, so others can read and reuse what is useful, and it serves as my portfolio. Reuse is welcome, but it is not a design goal.

> **History:** DevHub previously tried to be both an open-source collection of generic tools and my personal project hub. That led to conflicts, a lack of focus, and noise and complexity that did not serve either goal. Tools for unknown users need broad compatibility, stable interfaces, configuration options, and support for environments I do not use; my own projects need fast iteration fitted to how I actually work. DevHub now focuses only on the latter.

---

## Repository scope

Each part of DevHub has a clear scope, so information has one home:

- **[`docs/`](./docs/)** contains DevHub's [shared guidelines](./docs/GUIDELINES.md), [architecture](./docs/ARCHITECTURE.md), [getting-started guide](./docs/GETTING-STARTED.md), concise [command cheat sheets](./docs/cheatsheets/README.md), and repository-wide [architecture decision records](./docs/adrs/README.md). The [APM overview](packages/apm/README.md) explains the independent shared-guideline and local-development package sources.
- **[`archive/`](./archive/README.md)** records retired approaches and their rationale, not an actively maintained technical knowledge base.
- **Area READMEs**, such as [`packages/README.md`](./packages/README.md) and [`tools/README.md`](./tools/README.md), own local commands and component contracts; [tool ADRs](./tools/adrs/README.md) record their durable design decisions.
- **[Root agent guidance](AGENTS.md)** routes AI agents to that owning context; [APM design and setup](packages/apm/README.md) explains the common baseline and repository-specific customization pattern.

---

## Task tracking

I track DevHub and all my personal projects, including the public and private homelab, in one private GitHub Project. They are parts of one personal development hub, even when permissions or release boundaries require separate repositories. Small tasks and a clear next step make it easy to pause and resume without keeping unfinished work in my head; see [Central DevHub Task Tracking](./docs/how-to/TASK-TRACKING.md) for the board, privacy rules, and workflow.

---

## What belongs in DevHub

DevHub is intended to grow through broadly reusable material, not by absorbing the implementation of every project:

- **[Tools](tools/README.md)** contains shared automation, including [repository fleet management](tools/repo/README.md) with Terraform and Python. [Tool ADRs](tools/adrs/README.md) link to rationale maintained alongside each owning tool.
- **[How-tos](docs/how-to/README.md)** provides task-oriented entry points, including creating a repository in the DevHub ecosystem and setting up my code editor, accounts, and Git.
- **[Getting started](docs/GETTING-STARTED.md)** explains how to set up DevHub and use shared guidance across related repositories.
- **[GitHub Actions](docs/github-actions/README.md)** documents reusable workflows and actions, including the [central APM sync](docs/github-actions/workflows/apm-sync.md) that prepares package-update pull requests across the repository inventory.
- **[APM customizations](packages/apm/README.md)** documents shared `guidelines-core` and the local `development-core` workflow plus opt-in `development-*` stacks.
- **[Reusable packages](packages/README.md)** groups related package work within DevHub. Package contents, dependencies, and release boundaries remain explicit; sharing a repository does not require one version for everything.

The [shared guidelines](docs/GUIDELINES.md) cover repository and package placement, naming, and setup. The [architecture guide](docs/ARCHITECTURE.md) summarizes current boundaries; [ADRs](docs/adrs/README.md) record the decision rationale and trade-offs. Native packaging details belong in the [Python Packaging User Guide](https://packaging.python.org/en/latest/overview/) and [Go module documentation](https://go.dev/doc/modules/developing).

I frequently change these resources together, so DevHub keeps them in one repository for coordinated maintenance. The [monorepo ADR](docs/adrs/DEVHUB-MONOREPO.md) records the rationale, alternatives, and accepted trade-offs.

This means more workflows and selective component validation within a shared repository boundary; sharing source does not establish artifact compatibility. Package and release boundaries follow consumer contracts, and publishing automation is not yet implemented; see the [release-boundary ADR](docs/adrs/RELEASE-BOUNDARIES-BY-MANAGED-CONTRACT.md).

DevHub can therefore grow while retaining a clear purpose: shared development resources and entry points, not unrelated service or environment implementations.

---

## Separate projects

Separate repositories are useful for independently operated services, different ownership, or different access requirements. Size, language, or independent package versions alone do not require a split; the [homelab repository ADR](docs/adrs/SEPARATE-HOMELAB-REPOSITORIES.md) records the current example:

- **[Home lab — devhub-homelab](https://github.com/CollinPoetoehena/devhub-homelab)** is part of DevHub, with separate public guidance and private implementation repositories for its distinct service lifecycle and access/publication boundaries. Its standards, personal workspace setup, and task tracking remain central here; actual configuration and operational secrets stay in the appropriate protected systems.

The distinction is about ownership and reuse, not whether a project is related to development. A homelab is a development platform, but its specific implementation is still a distinct project. DevHub links projects together and provides the generic material they share; it does not need to contain each project's implementation. [Getting started](docs/GETTING-STARTED.md) is the central setup guide for the shared workspace and AI customizations used across these projects.

> The home-lab setup previously lived in DevHub, but it has since been removed from this repository and is maintained in its own project for the above reasons. Some commits from the old setup may remain; they describe an obsolete configuration that is no longer used and therefore do not expose sensitive information.

---

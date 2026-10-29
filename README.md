# DevHub

**DevHub is my central development hub: the standards, reusable resources, and entry point I use for all my personal projects.** I maintain it primarily for myself: to organize what I learn, keep useful guidance and tools easy to find, and connect the projects I work on. It is also public, so it can serve as a portfolio that shows how I approach development, automation, documentation, and ongoing learning.

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

For documentation changes, follow the [Documentation Guidelines](docs/DOCUMENTATION.md).

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

Development work generates more information, decisions, commands, and lessons than I can reliably remember. Writing down what matters gives me an external reference I can return to, helps me explain my thinking clearly, and reduces the effort of rediscovering or relearning the same things. Documentation supports understanding and practical experience rather than replacing them; the [Reference](./reference/README.md#why-i-document) explains how I put this documentation approach into practice.

Maintaining DevHub is worthwhile because it turns individual problem-solving into knowledge I can reuse: across future tasks, across separate projects, and when reviewing why a decision was made. Shared scripts, generic workflows, and reference material also help me apply practices consistently without copying the same guidance into every project. I curate this for practical use rather than trying to document everything; information is useful when I can find it, understand its context, and keep it accurate.

The public repository has a second purpose as a portfolio. It provides an honest view of the work behind my projects—not only finished code, but also the designs, trade-offs, automation, and learning that shaped them. The portfolio aspect is valuable, but it is secondary to the repository's role as a working hub for myself. I want it to remain useful and maintainable for my own development, rather than turn it into a showcase that is disconnected from the work I actually do.

---

## Standards for my personal projects

DevHub holds the [standards I apply to all my personal projects](./docs/CONVENTIONS_STANDARDS.md): documentation and coding guidelines, engineering practices, AI customizations, automation, and tooling. The [reference](./reference/README.md) stays part of that: it holds the essential general knowledge the standards build on.

I manage my personal projects the way a professional team manages its projects, with consistent standards and practices; they are effectively a team with one developer. This is not to mimic enterprise or industry practice. It is worth the time because it adds real value: clear and consistent projects, automation and tooling that save me time, and documentation that keeps decisions self-explanatory when I return to a project later.

### Public, but not a generic toolbox

DevHub is not a collection of generic tools, AI skills, and other resources built for anyone to use. Its purpose is my personal development hub and the management of my personal projects, and those two goals conflict: you cannot do both well in one repository.

It remains public, so others can read and reuse what is useful, and it serves as my portfolio. Reuse is welcome, but it is not a design goal.

> **History:** DevHub previously tried to be both an open-source collection of generic tools and my personal project hub. That led to conflicts, a lack of focus, and noise and complexity that did not serve either goal. Tools for unknown users need broad compatibility, stable interfaces, configuration options, and support for environments I do not use; my own projects need fast iteration fitted to how I actually work. DevHub now focuses only on the latter.

---

## Repository scope

Each part of DevHub has a clear scope, so information has one home:

- **[`reference/`](./reference/README.md)** contains only general theory, practices, and commands. It may use examples from or link to other parts of DevHub, but contains no DevHub-specific conventions or decisions.
- **[`docs/`](./docs/README.md)** contains DevHub-specific documentation: its [project structure](./docs/PROJECT-STRUCTURE.md), standards, decisions, GitHub/AI guides, and [usage](./docs/USAGE.md). Copilot instructions, skills, and agents are also maintained in [`docs/copilot/`](./docs/copilot/); `.github/` holds only workflow configuration and symbolic links that keep them discoverable.
- **Area READMEs**, such as [`packages/README.md`](./packages/README.md) and [`tools/README.md`](./tools/README.md), own local commands and component contracts.

---

## Task tracking

I track DevHub and all my personal projects, including the public and private homelab, in one private GitHub Project. They are parts of one personal development hub, even when permissions or release boundaries require separate repositories. Small tasks and a clear next step make it easy to pause and resume without keeping unfinished work in my head; see [Central DevHub Task Tracking](./docs/TASK-TRACKING.md) for the board, privacy rules, and workflow.

---

## What belongs in DevHub

DevHub is intended to grow through broadly reusable material, not by absorbing the implementation of every project:

- **[Reference documentation](./reference/README.md)** collects general concepts, practical commands, and reusable guidance. Its [engineering reference](./reference/engineering/README.md) centralizes package design, language guidance, and software engineering principles so theory and best practices have one discoverable home.
- **[Tools](tools/README.md)** contains shared tooling that is not owned by one specific project.
- **[Personal setup](docs/COPILOT-SETUP.md)** uses one script under `tools/` to fast-forward a trusted clone and keep workspace instructions and AI customizations current.
- **[Generic GitHub workflows and AI customizations](docs/GITHUB.md)** explain how to use GitHub Copilot instructions, skills, and agents, and provide reusable GitHub Actions and skills.
- **[Reusable packages](packages/README.md)** groups related package work within DevHub. Package contents, dependencies, and release boundaries remain explicit; sharing a repository does not require one version for everything.

The [package design guide](./reference/engineering/Packages.md) covers reusable SDKs, specialized tools, scripts, and distribution. The [repository and project organization guide](reference/engineering/Repository_Organization.md) covers placement decisions, setup steps, and repository boundaries, with industry examples.

I frequently change these resources together. Keeping them in one larger repository avoids managing many repositories, making separate commits for coordinated changes, and copying or synchronizing reusable actions, workflows, and AI customization. As the sole maintainer, keeping many related repositories current within the same context would be unsustainable. The goal is convenient, coherent maintenance, not as many repositories as possible; see [why DevHub is one repository](docs/PROJECT-STRUCTURE.md#why-devhub-is-one-repository).

I accept more workflows, somewhat more complex CI selection, and a larger shared history because they cost less than distributing and coordinating the same setup across many closely related repositories. Path- and dependency-aware checks, component tags, and published package or container versions can keep validation and consumption selective; see [the trade-offs and mitigations](reference/engineering/Repository_Organization.md#where-the-complexity-lives).

DevHub can therefore grow while retaining a clear purpose: shared development resources and entry points, not unrelated service or environment implementations.

---

## Separate projects

Separate repositories are useful for independently operated services, different ownership, or different access requirements. Size, language, or independent package versions alone do not require a split:

- **[Home lab — devhub-homelab](https://github.com/CollinPoetoehena/devhub-homelab)** is part of DevHub, with separate public guidance and private implementation repositories for its distinct service lifecycle and access/publication boundaries. Its standards, personal workspace setup, and task tracking remain central here; actual configuration and operational secrets stay in the appropriate protected systems.

The distinction is about ownership and reuse, not whether a project is related to development. A homelab is a development platform, but its specific implementation is still a distinct project. DevHub links projects together and provides the generic material they share; it does not need to contain each project's implementation. [Using DevHub](docs/USAGE.md) is the central setup guide for the shared workspace and AI customizations used across these projects.

> The home-lab setup previously lived in DevHub, but it has since been removed from this repository and is maintained in its own project for the above reasons. Some commits from the old setup may remain; they describe an obsolete configuration that is no longer used and therefore do not expose sensitive information.

---

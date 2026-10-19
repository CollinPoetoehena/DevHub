# DevHub

**DevHub is my central development hub and entry point for the reusable resources and separate projects that support my development work.** I maintain it primarily for myself: to organize what I learn, keep useful guidance and tools easy to find, and connect the projects I work on. It is also public, so it can serve as a portfolio that shows how I approach development, automation, documentation, and ongoing learning.

The name reflects the purpose:

- **Dev** means development and DevOps: building, automating, and learning through practical work.
- **Hub** means a central place to navigate to the related resources and projects.

---

## Table of Contents

- [Why I Maintain DevHub](#why-i-maintain-devhub)
- [What belongs in DevHub](#what-belongs-in-devhub)
- [Separate projects](#separate-projects)

> **Scope of this README:** This is a concise introduction to DevHub's purpose and structure, not a full explanation of every area or project. More detail belongs in the relevant documentation linked below; the root README should stay short enough to work as a clear entry point.

For documentation changes, follow the [Documentation Guidelines](./DOCUMENTATION.md).

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

## What belongs in DevHub

DevHub is intended to grow through broadly reusable material, not by absorbing the implementation of every project:

- **[Reference documentation](./reference/README.md)** collects general concepts, practical commands, and guidance that can be reused across projects.
- **[Scripts](./scripts/README.md)** contains shared utility scripts that are not owned by one specific project.
- **[Local installation](./install/README.md)** provides a central installer with focused components, currently for personal AI customizations and login-time updates.
- **[Generic GitHub workflows and AI customizations](./.github/OVERVIEW.md)** explain how to use GitHub Copilot instructions, skills, and agents, and provide reusable GitHub Actions and skills.
- **[Packages](./packages/README.md)** is the index and shared publishing guidance for reusable components. The implementations themselves—such as Python packages, Ansible roles, Terraform modules, and Helm charts—belong in their own repositories, where they can be versioned, released, tested, and maintained independently.

These resources can be useful across several repositories, so keeping them centralized avoids duplication and gives generic guidance one place to evolve. DevHub can therefore become larger while retaining a clear purpose: the contents are shared resources or an entry point, not a collection of unrelated project implementations.

---

## Separate projects

Larger efforts with their own implementation, configuration, release cycle, or operational lifecycle should live in their own repositories and link back here for shared guidance:

- **[Home lab — devhub-homelab](https://github.com/CollinPoetoehena/devhub-homelab)** is a separate project for the home network and lab design, documentation, infrastructure implementation, and automation. It is part of the wider DevHub ecosystem, but has its own repository so its code, maintenance, pipelines, repository permissions, and project-specific secrets can be managed independently. This root README remains its DevHub entry point; see the [AI reference](./reference/AI.md#reusable-ai-workflows-and-agents) for general principles and the [GitHub Copilot guide](./.github/AI.md) for product-specific setup.

The distinction is about ownership and reuse, not whether a project is related to development. A homelab is a development platform, but its specific implementation is still a distinct project. DevHub links projects together and provides the generic material they share; it does not need to contain each project's implementation.

> The home-lab setup previously lived in DevHub, but it has since been removed from this repository and is maintained in its own project for the above reasons. Some commits from the old setup may remain; they describe an obsolete configuration that is no longer used and therefore do not expose sensitive information.

---

# DevHub

**DevHub is my central development hub and entry point for the reusable resources and separate projects that support my development work.** I maintain it primarily for myself: to organize what I learn, keep useful guidance and tools easy to find, and connect the projects I work on. It is also public, so it can serve as a portfolio that shows how I approach development, automation, documentation, and ongoing learning.

The name reflects the purpose:

- **Dev** means development and DevOps: building, automating, and learning through practical work.
- **Hub** means a central place to navigate to the related resources and projects.

## Table of Contents

- [Why I Maintain DevHub](#why-i-maintain-devhub)
- [What belongs in DevHub](#what-belongs-in-devhub)
- [Separate projects](#separate-projects)

> **Scope of this README:** This is a concise introduction to DevHub's purpose and structure, not a full explanation of every area or project. More detail belongs in the relevant documentation linked below; the root README should stay short enough to work as a clear entry point.

---

## Why I Maintain DevHub

Development work generates more information, decisions, commands, and lessons than I can reliably remember. Writing down what matters gives me an external reference I can return to, helps me explain my thinking clearly, and reduces the effort of rediscovering or relearning the same things. The [Reference](./reference/README.md#why-i-document) explains this documentation approach in more detail.

Maintaining DevHub is worthwhile because it turns individual problem-solving into knowledge I can reuse: across future tasks, across separate projects, and when reviewing why a decision was made. Shared scripts, generic workflows, and reference material also help me apply practices consistently without copying the same guidance into every project. I curate this for practical use rather than trying to document everything; information is useful when I can find it, understand its context, and keep it accurate.

The public repository has a second purpose as a portfolio. It provides an honest view of the work behind my projects—not only finished code, but also the designs, trade-offs, automation, and learning that shaped them. The portfolio aspect is valuable, but it is secondary to the repository's role as a working hub for myself. I want it to remain useful and maintainable for my own development, rather than turn it into a showcase that is disconnected from the work I actually do.

---

## What belongs in DevHub

DevHub is intended to grow through broadly reusable material, not by absorbing the implementation of every project:

- **[Reference documentation](./reference/README.md)** collects general concepts, practical commands, and guidance that can be reused across projects.
- **[Scripts](./scripts/README.md)** contains shared utility scripts that are not owned by one specific project.
- **[Generic GitHub workflows and AI skills](./.github/OVERVIEW.md)** provide reusable automation and agent workflows, including shared GitHub Actions and GitHub Copilot skills.
- **[Packages](./packages/README.md)** is the index and shared publishing guidance for reusable components. The implementations themselves—such as Python packages, Ansible roles, Terraform modules, and Helm charts—belong in their own repositories, where they can be versioned, released, tested, and maintained independently.

These resources can be useful across several repositories, so keeping them centralized avoids duplication and gives generic guidance one place to evolve. DevHub can therefore become larger while retaining a clear purpose: the contents are shared resources or an entry point, not a collection of unrelated project implementations.

---

## Separate projects

Larger efforts with their own implementation, configuration, release cycle, or operational lifecycle should live in their own repositories and link back here for shared guidance:

- **[Home lab — devhub-homelab](https://github.com/CollinPoetoehena/devhub-homelab)** is a separate project for the home network and lab design, documentation, infrastructure implementation, and automation. It is part of the wider DevHub ecosystem, but has its own repository so its code, maintenance, pipelines, repository permissions, and project-specific secrets can be managed independently. This root README remains its DevHub entry point; see the [AI reference](./reference/AI.md#coding-github-copilot-in-vs-code) for shared AI workflow guidance.

The distinction is about ownership and reuse, not whether a project is related to development. A homelab is a development platform, but its specific implementation is still a distinct project. DevHub links projects together and provides the generic material they share; it does not need to contain each project's implementation.

> The home-lab setup previously lived in DevHub, but it has since been removed from this repository and is maintained in its own project for the above reasons. Some commits from the old setup may remain; they describe an obsolete configuration that is no longer used and therefore do not expose sensitive information.

---
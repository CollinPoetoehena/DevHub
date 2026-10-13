# DevHub

**DevHub is my central development hub and entry point for the reusable resources and separate projects that support my development work.** It is a personal, public repository for general documentation, shared utilities, reusable automation, and links that help me find and maintain those projects.

The name reflects the purpose:

- **Dev** means development and DevOps: building, automating, and learning through practical work.
- **Hub** means a central place to navigate to the related resources and projects.

## What belongs in DevHub

DevHub is intended to grow through broadly reusable material, not by absorbing the implementation of every project:

- **[Reference documentation](./reference/README.md)** collects general concepts, practical commands, and guidance that can be reused across projects.
- **[Scripts](./scripts/README.md)** contains shared utility scripts that are not owned by one specific project.
- **[Generic GitHub workflows and AI skills](./.github/README.md)** provide reusable automation and agent workflows, including shared GitHub Actions and GitHub Copilot skills.
- **[Packages](./packages/README.md)** is the index and shared publishing guidance for reusable components. The implementations themselves—such as Python packages, Ansible roles, Terraform modules, and Helm charts—belong in their own repositories, where they can be versioned, released, tested, and maintained independently.

These resources can be useful across several repositories, so keeping them centralized avoids duplication and gives generic guidance one place to evolve. DevHub can therefore become larger while retaining a clear purpose: the contents are shared resources or an entry point, not a collection of unrelated project implementations.

## Separate projects

Larger efforts with their own implementation, configuration, release cycle, or operational lifecycle should live in their own repositories and link back here for shared guidance:

- **[Home lab — devhub-homelab](https://github.com/CollinPoetoehena/devhub-homelab)** is a separate project for the home network and lab design, documentation, infrastructure implementation, and automation. It is part of the wider DevHub ecosystem, but has its own repository so its code, maintenance, pipelines, repository permissions, and project-specific secrets can be managed independently. This root README remains its DevHub entry point; see the [AI reference](./reference/AI.md#coding-github-copilot-in-vs-code) for shared AI workflow guidance.

The distinction is about ownership and reuse, not whether a project is related to development. A homelab is a development platform, but its specific implementation is still a distinct project. DevHub links projects together and provides the generic material they share; it does not need to contain each project's implementation.

---
# DevHub Homelab

This repository contains the design, documentation, and implementation of my home network and homelab, from hardware and network architecture through infrastructure automation, Kubernetes, monitoring, and GitOps.

## Part of DevHub, maintained as a separate project

The homelab is part of the wider [DevHub development hub](https://github.com/CollinPoetoehena/DevHub/blob/main/README.md), but it is a distinct project with its own repository: [`devhub-homelab`](https://github.com/CollinPoetoehena/devhub-homelab). DevHub remains the central entry point for generic documentation, shared scripts, reusable GitHub workflows and AI skills, and links to separate projects. The [DevHub README's separate-projects section](https://github.com/CollinPoetoehena/DevHub/blob/main/README.md#separate-projects) explains this boundary.

Keeping the homelab in its own repository lets its implementation, issues, pull requests, releases, permissions, and maintenance evolve independently without losing the benefit of shared DevHub guidance. It can have project-specific CI/CD pipelines, repository secrets and environments, and automation tailored to infrastructure changes, while generic workflows and skills remain in DevHub. Repository separation does not itself secure secrets: follow the rules in [Security and Public Repository](./docs/0_Security_and_Public_Repository.md), and configure access and secret handling deliberately.

The separate boundary also makes it easier to grow the homelab without turning DevHub into a monorepo of implementations. Shared concepts and utilities stay in DevHub and are linked where useful; homelab design, configuration, and operational procedures stay here.

## Documentation

1. **[Security and Public Repository](./docs/0_Security_and_Public_Repository.md):** Publication rules, secrets handling, review requirements, and incident response.
2. **[Design](./docs/1_Design/README.md):** Goals, network topology, node setup, and overall architecture.
3. **[Setup](./docs/2_Setup/README.md):** Step-by-step implementation guidance, using the design as a reference.

The design documentation intentionally separates stable, tool-independent architecture from implementation choices. See the [Design README](./docs/1_Design/README.md) for the boundary, and the [hardware and software prerequisites](./docs/1_Design/README.md#documents-setup--scope) for where concrete choices belong.

## Shared DevHub resources

The [DevHub reference](https://github.com/CollinPoetoehena/DevHub/tree/main/reference) contains reusable concepts and commands, including the [AI reference](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/AI.md) and [network reference](https://github.com/CollinPoetoehena/DevHub/tree/main/reference/network). These are maintained centrally because they apply beyond this homelab.

DevHub also maintains generic [`docs`](https://github.com/CollinPoetoehena/DevHub/tree/main/.github/skills/docs) and [`implement-change`](https://github.com/CollinPoetoehena/DevHub/tree/main/.github/skills/implement-change) Agent Skills. This repository keeps homelab-specific context skills in [`.github/skills/`](./.github/skills/), which add its architecture and security rules to those generic workflows. A GitHub link is a reference, not an automatic skill installation; see the [AI reference's skill guidance](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/AI.md#coding-github-copilot-in-vs-code) and the [homelab skills README](./.github/skills/README.md).

## AI-assisted work

Use [`homelab-project`](./.github/skills/homelab-project/SKILL.md) for reusable homelab context. For implementation or documentation tasks that need that context, use [`homelab-implement-change`](./.github/skills/homelab-implement-change/SKILL.md) or [`homelab-docs`](./.github/skills/homelab-docs/SKILL.md); each layers homelab requirements on the matching generic DevHub skill. The [homelab skills README](./.github/skills/README.md) explains their use.

## Infrastructure automation

Automation implementation and requirements live with the homelab project. The shared DevHub [packages index](https://github.com/CollinPoetoehena/DevHub/blob/main/packages/README.md) and [reusable GitHub Actions workflows](https://github.com/CollinPoetoehena/DevHub/tree/main/.github/workflows) document generic resources that can be used by this and other projects.

# Reference

This folder contains theoretical knowledge, useful commands, quick references, and other supporting information related to this project. 

The goal of this folder is to provide a central place for technical knowledge and quick-reference information that complements the implementation and getting-started documentation. 

It is not intended to be a complete guide of Software Engineering/IT in general and all technologies and tools used in this project, but rather a curated and carefully selected collection of information that is highly relevant for myself and some of the projects I work on (e.g. homelab, Python packages, etc.).

## Why I Document

> “Your professional success and quality of life depend directly on your ability to manage information effectively.” — Tiago Forte

We consume far more information than we can reliably remember. Notes and references give important knowledge a place outside my memory, so I can find and use it again instead of repeatedly searching for it or relearning it. Writing also makes me slow down, decide what matters, and formulate my thoughts clearly. Turning an idea into words often reveals gaps, assumptions, or connections that were not obvious while the idea was still only in my head.

I document concepts, decisions, commands, and lessons that are useful beyond the moment I learn them. This creates a practical reference for future work, supports more consistent decisions, and makes it easier to apply knowledge across projects. The purpose is not to record everything or build an encyclopedia: it is to curate useful information, organize it so it can be retrieved, and keep it accurate enough to trust.

That is why this reference is centralized in DevHub rather than repeated in each project. General concepts belong here once; separate projects such as the [homelab](https://github.com/CollinPoetoehena/devhub-homelab) can link to that shared foundation and keep their own documentation focused on their specific design and implementation.

**Why not in specific projects like `homelab/docs/`?** This documentation is all generic and not tied to any single project, making it reusable across multiple projects and contexts. This avoids having to duplicate the same reference material in each project, and keeps the information centralized and easier to maintain. Finally, the project-specific documentation can focus on implementation details and use cases, while this reference folder provides the foundational and general knowledge.

## Contents

| File | Description |
|------|-------------|
| [AI.md](AI.md) | AI background, agents, prompt engineering, and how to use AI (and which model tier) effectively for Software Engineering work. |
| [Code_Editor.md](Code_Editor.md) | Personal code editor setup, account separation, Settings Sync, subscriptions, and Git with personal and work accounts. |
| [Software_Engineering_Principles.md](Software_Engineering_Principles.md) | Language-agnostic coding and design principles (DRY, KISS, YAGNI, SOLID, coupling/cohesion, Clean Architecture, Twelve-Factor, etc.). |
| [Network Reference](network/README.md) | Networking concepts (devices, subnets, IP addresses, DHCP, DNS, NAT, IPv6) and Linux networking commands. Split into multiple files — see the network README for the full index. |
| [OS and Related Hardware Reference](./os_hardware/README.md) | OS and related hardware concepts and theory. |
| [Storage_Background_Commands.md](Storage_Background_Commands.md) | Storage concepts (filesystems, mounting, LVM, RAID, NFS) and Kubernetes storage (Volumes, PV, PVC, StorageClass). |
| [Other Reference](other/README.md) | Other general reference material, including tmux terminal multiplexer reference. |
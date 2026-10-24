# Reference

This folder contains theoretical knowledge, useful commands, quick references, and other supporting information related to this project. 

The goal of this folder is to provide a central place for technical knowledge and quick-reference information that complements the implementation and getting-started documentation. 

It is not intended to be a complete guide of Software Engineering/IT in general and all technologies and tools used in this project, but rather a curated and carefully selected collection of information that is highly relevant for myself and some of the projects I work on (e.g. homelab, Python packages, etc.).

---

## Table of Contents

- [Scope and Tool Specificity](#scope-and-tool-specificity)
- [Why I Document](#why-i-document)
- [Contents](#contents)

---

## Scope and Tool Specificity

> “In engineering and IT, fundamentals endure while tools change.”

This is the guiding principle for DevHub's Reference: prioritize general concepts, durable fundamentals, and the reasoning needed to make good technical decisions. Networking, storage, operating-system behavior, programming, and data protection remain useful even as particular products, interfaces, and commands evolve or are replaced. Understanding those foundations makes it easier to evaluate new tools and apply what you know in different environments.

This reference is not intended to be a catalog of every possible product, platform, or command. Tools such as Kubernetes and specific networking products can have extensive, version-dependent behavior; reproducing all of that here would make the reference harder to maintain and could leave it out of date. Instead, DevHub includes only the tool-specific context or examples that help explain a broader concept, and links to the official documentation for current details and comprehensive instructions. The goal is to understand the fundamentals, not to collect every tool or duplicate its maintainers' documentation.

The [storage reference](storage/README.md) applies this approach to storage, with a brief Kubernetes-specific exception for orientation. The [network reference](network/README.md) focuses on reusable networking concepts and points to official documentation when a particular tool's behavior is involved. The [engineering reference](engineering/README.md) centralizes concise [language and tool practices](engineering/Languages_and_Tools.md), [generic concepts](engineering/Concepts.md), and package organization without maintaining a separate language tutorial collection.

---

## Why I Document

> “Your professional success and quality of life depend directly on your ability to manage information effectively.” — Tiago Forte

My broader view on thinking, judgment, and memory is explained in [Why I Maintain DevHub](../README.md#why-i-maintain-devhub). Here, the focus is on how documentation makes useful information clear, retrievable, and reusable.

Writing makes me slow down, decide what matters, and explain it clearly. Recording the reasoning, assumptions, and alternatives behind a decision preserves its context, so I can revisit it when circumstances change. Notes and references also reduce repeated searches and give useful concepts, commands, and lessons a stable place to return to.

I document concepts, decisions, commands, and lessons that are useful beyond the moment I learn them. This creates a practical reference for future work, supports more consistent decisions, and makes it easier to apply knowledge across projects. The purpose is not to record everything or build an encyclopedia: it is to curate useful information, organize it so it can be retrieved, and keep it accurate enough to trust.

That is why this reference is centralized in DevHub rather than repeated in each project. General concepts belong here once; separate projects such as the [homelab](https://github.com/CollinPoetoehena/devhub-homelab) can link to that shared foundation and keep their own documentation focused on their specific design and implementation.

**Why not in specific projects like `homelab/docs/`?** Most of this reference covers concepts and practices that can be reused across multiple projects and contexts, so documenting them here avoids duplication and makes them easier to maintain. A small number of tool-specific examples are included when they are especially useful, but they remain intentionally limited rather than trying to replace official product documentation. Project-specific documentation can therefore focus on its implementation details and use cases, while this reference provides the shared foundations.

---

## Contents

| File | Description |
|------|-------------|
| [AI.md](AI.md) | AI background, agents, prompt engineering, and how to use AI (and which model tier) effectively for Software Engineering work. |
| [Code_Editor.md](Code_Editor.md) | Personal code editor setup, account separation, Settings Sync, subscriptions, and Git with personal and work accounts. |
| [Engineering & Coding Reference](engineering/README.md) | Package design, language and component guidance, and [software engineering principles](engineering/Software_Engineering_Principles.md), centralized for reuse across projects. |
| [Network Reference](network/README.md) | Networking theory, general architecture (segmentation, trust zones and traffic flows), and Linux networking commands. Split into multiple files — see the network README for the full index. |
| [Compute Reference](compute/README.md) | General-purpose computer hardware fundamentals, component roles and inspection commands. |
| [Operating Systems Reference](os/README.md) | OS fundamentals across Linux, Windows and macOS, plus a general boot/install overview. |
| [Storage Reference](storage/README.md) | Storage media and architecture, data protection, Linux storage background and commands, plus a short Kubernetes-specific exception with links to official documentation. |
| [Other Reference](other/README.md) | Other general reference material, including background-process concepts and a focused tmux guide. |

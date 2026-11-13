# DevHub Project Structure

How DevHub is organized and why. This page records project boundaries and setup decisions; general technical details belong in the official documentation linked where needed.

---

## Table of Contents

- [Layout and scope](#layout-and-scope)
- [Why DevHub is a monorepo](#why-devhub-is-a-monorepo)
- [Separate repositories](#separate-repositories)
- [Release and versioning units](#release-and-versioning-units)
- [Placing new work](#placing-new-work)
- [Naming conventions](#naming-conventions)
- [Package README link](#package-readme-link)

---

## Layout and scope

| Path | Owns |
|---|---|
| [Root `AGENTS.md`](../AGENTS.md) | Repository-specific agent entry point, linked to owning documentation rather than duplicated in nested files |
| [`docs/`](.) | DevHub-specific [guidelines](GUIDELINES.md), architecture, usage, and selective [command cheat sheets](cheatsheets/README.md) |
| [`adrs/`](adrs/README.md) | Repository-wide architecture decision records |
| [`.github/`](../.github/) | Workflow configuration and Copilot-target customizations when installed; reusable workflows are documented in [`github-actions/`](github-actions/README.md) |
| [`archive/`](../archive/README.md) | Decision notices for retired approaches; historical content stays in Git history |
| [`packages/`](../packages/README.md) | Reusable packages, each with native metadata and its own release boundary |
| [`tools/`](../tools/README.md) | Shared automation, including [repository fleet management](../tools/repo/README.md) |

Each area's README owns the details of that area. The [root README](../README.md#repository-scope) summarizes this scope.

---

## Why DevHub is a monorepo

DevHub keeps shared project guidance, AI customizations, GitHub automation, tools, and reusable packages under common ownership. This is a bounded repository choice, not a claim that DevHub is one application, package, or release unit. Independently operated projects with distinct access or lifecycle requirements remain in their own repositories.

The [monorepo ADR](adrs/DEVHUB-MONOREPO.md) records the rationale, alternatives, accepted trade-offs, and conditions for revisiting this boundary. The [repository-boundary guidance](GUIDELINES.md#monorepo-or-polyrepo) gives general placement criteria.

---

## Separate repositories

The homelab is part of DevHub's wider personal-project ecosystem but has an independent service lifecycle and different access requirements. Its public guidance and private implementation/configuration live in separate homelab repositories; DevHub retains shared standards, workspace setup, and task tracking. The [homelab repository ADR](adrs/SEPARATE-HOMELAB-REPOSITORIES.md) records the boundary and alternatives.

---

## Release and versioning units

Set release boundaries by the artifacts maintained and offered to consumers under a shared compatibility contract, not by repository or directory boundaries. Preserve native package identities and use coordinated releases only when a tested combination is the supported offering. Publishing automation remains a placeholder. The [release-boundary ADR](adrs/RELEASE-BOUNDARIES-BY-MANAGED-CONTRACT.md) records the policy, trade-offs, and implementation limits.

---

## Placing new work

For placement criteria and setup steps, see the [shared guidelines for placing packages and components](GUIDELINES.md#placing-packages-and-components) and [setting up a project or package](GUIDELINES.md#setting-up-a-project-or-package).

---

## Naming conventions

For current rules, see the [repository and package naming conventions](GUIDELINES.md#naming-conventions).

---

## Package README link

For the recommended package README content and links, see the [shared guidelines](GUIDELINES.md#package-readme-links).

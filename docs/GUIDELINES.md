# Repository and Package Guidelines

These are shared, human-readable conventions for organizing DevHub and its projects. Each repository owns its own implementation, user-facing documentation, and exceptions.

---

## Table of Contents

- [Shared guidance and AI customizations](#shared-guidance-and-ai-customizations)
- [Choosing a repository boundary](#choosing-a-repository-boundary)
- [Placing packages and components](#placing-packages-and-components)
- [Setting up a project or package](#setting-up-a-project-or-package)
- [Naming conventions](#naming-conventions)
- [Package README links](#package-readme-links)

---

## Shared guidance and AI customizations

This file is the single home for shared, human-facing repository, package, and setup conventions. Project docs own user-facing concepts and usage, getting started, local setup, architecture decisions, and task tracking; see [Using DevHub](USAGE.md), [project architecture](ARCHITECTURE.md), and [task tracking](TASK-TRACKING.md). Link to those docs when useful instead of copying them into Copilot instructions.

Reusable AI role standards and workflow live in the [common APM package](../packages/apm/common/README.md), which is the authoring source for these customizations:

- Agents define role-owned standards: [Orchestrator](../packages/apm/common/.apm/agents/orchestrator.agent.md), [Architect](../packages/apm/common/.apm/agents/architect.agent.md), [Coder](../packages/apm/common/.apm/agents/coder.agent.md), [Documenter](../packages/apm/common/.apm/agents/documenter.agent.md), [Tester](../packages/apm/common/.apm/agents/tester.agent.md), and [Reviewer](../packages/apm/common/.apm/agents/reviewer.agent.md).
- Instructions express applicable AI-authoring or implementation constraints: [AI customization](../packages/apm/common/.apm/instructions/ai-customization.instructions.md), [Ansible](../packages/apm/common/.apm/instructions/ansible.instructions.md), [Dockerfile](../packages/apm/common/.apm/instructions/dockerfile.instructions.md), [GitHub Actions](../packages/apm/common/.apm/instructions/github-actions.instructions.md), and [Python](../packages/apm/common/.apm/instructions/python.instructions.md).
- Skills capture focused, repeatable procedures; the current shared example is [manage-skills](../packages/apm/common/.apm/skills/manage-skills/SKILL.md).

Do not duplicate shared role standards or this human guidance in instructions. Add an AI instruction only when a constraint is actionable, relevant to its scope, and needed to shape implementation; a personal preference or explanation for a decision can remain human guidance. Put consumer-specific constraints in that consumer's project context.

---

## Choosing a repository boundary

Keep related work together when it shares ownership and access, changes together, and is maintained or validated as a coordinated unit. Split it when a distinct service, owner, access requirement, operational lifecycle, or publication boundary makes independent work valuable. Size, language, or independent package versions alone do not require a repository split.

DevHub keeps shared development resources, tooling, guidance, and setup together because one maintainer frequently changes them in coordination; the [architecture guide](ARCHITECTURE.md#why-devhub-is-one-repository) records the rationale and accepted trade-offs. Distinct applications and services belong in their own repositories when those boundaries apply.

---

## Placing packages and components

- Keep implementation-local helpers with the application that uses them. Create a reusable package for a real public interface or consumer need.
- Treat the managed contract—not the directory count or programming language—as the release boundary. Independently versioned packages may share a repository; document the consumer contract and compatibility explicitly.
- Keep native package metadata and artifact identities. Add CI and release automation at the component's scope, including checks for affected consumers.
- Record the choice and exceptions in the owning project or package README, then track the work in the central DevHub backlog. Revisit the boundary when consumers or maintenance costs change.

For the architectural rationale and release examples, see [Release and versioning units](ARCHITECTURE.md#release-and-versioning-units).

---

## Setting up a project or package

- Give each project and package an owning README that explains its purpose, setup, supported use, and project-specific decisions. Keep detailed commands and operational procedures with the component.
- Before publishing a component, document its consumers, native metadata, validation commands, release tags, artifact destination, and upgrade or rollback steps.
- Link to shared DevHub guidance from the project's README instead of copying it. The [workspace and AI setup guide](USAGE.md) explains how consumers use shared resources.
- Consumers own their triggers, credentials, and deployment configuration when using shared automation.

Use the official [Python Packaging User Guide](https://packaging.python.org/en/latest/overview/) and [Go module documentation](https://go.dev/doc/modules/developing) for ecosystem-specific mechanics.

---

## Naming conventions

Use `devhub-{category}-{project}` for focused repositories. Broader existing names such as DevHub and devhub-homelab remain meaningful exceptions. Native package identifiers follow ecosystem requirements; a repository name does not override an existing import or module path.

---

## Package README links

Package READMEs own their setup, supported behavior, decisions, and exceptions. Link to relevant official ecosystem documentation rather than duplicating general technical references. When a package needs DevHub's project-specific architecture context, link it once:

```markdown
> For DevHub's project boundaries and release design, see
[DevHub architecture](https://github.com/CollinPoetoehena/DevHub/blob/main/docs/ARCHITECTURE.md).
This README covers this package's setup, usage, design decisions, and exceptions.
```

# DevHub Project Structure

How DevHub is organized and why. This page records project boundaries and setup decisions; general technical details belong in the official documentation linked where needed.

---

## Table of Contents

- [Layout and scope](#layout-and-scope)
- [Why DevHub is one repository](#why-devhub-is-one-repository)
  - [Sole maintainer](#sole-maintainer)
  - [Accepted trade-offs](#accepted-trade-offs)
- [Separate repositories](#separate-repositories)
- [Established repository structures](#established-repository-structures)
- [Release and versioning units](#release-and-versioning-units)
- [Placing new work](#placing-new-work)
- [Naming conventions](#naming-conventions)
- [Package README link](#package-readme-link)

---

## Layout and scope

| Path | Owns |
|---|---|
| [`docs/`](.) | DevHub-specific [guidelines](GUIDELINES.md), architecture, decisions, and usage |
| [`.github/`](../.github/) | Project instructions and workflow configuration |
| [`archive/`](../archive/README.md) | Decision notices for retired approaches; historical content stays in Git history |
| [`packages/`](../packages/README.md) | Reusable packages, each with native metadata and its own release boundary |
| [`tools/`](../tools/README.md) | Setup, repository management, and maintenance tooling not owned by one project |

Each area's README owns the details of that area. The [root README](../README.md#repository-scope) summarizes this scope.

---

## Why DevHub is one repository

The goal is not as many repositories as possible, but a structure that fits the work and the people maintaining it. DevHub's packages, tooling, setup, GitHub automation, and AI customizations meet that criterion: a change to a practice can touch project guidance, an instruction or skill, a workflow, and a package at the same time. Keep related work together when it shares ownership and access and is routinely changed or validated together; split it when distinct ownership, access, operation, or publication boundaries make independent work worthwhile.

Separate repositories for these parts caused recurring overhead:

- managing many repositories, each with its own settings, branch rules, and dependency updates;
- making a separate commit and pull request in each repository for one coordinated change;
- copying and synchronizing reusable actions, workflows, and AI customizations to every repository;
- distributing the same CI setup, such as adding GitHub Actions to each repository.

I often opened those repositories in one workspace anyway. That helped navigation, but did not remove the maintenance overhead; one repository does.

### Sole maintainer

I am the only maintainer of DevHub. With many separate but related repositories, every coordinated change multiplies the commits, reviews, releases, and synchronization I have to do myself, and keeping them all current within the same context becomes a maintenance burden that one person cannot sustain. There is no team, ownership, or access boundary between these parts that a split would serve, so splitting adds cost without a matching benefit.

### Accepted trade-offs

A single repository moves some complexity into the repository itself:

- more GitHub Actions workflows in one place;
- somewhat more complex CI selection, so a change only validates the affected components;
- a larger shared history.

These are accepted because they cost less than distributing and coordinating the same setup across many closely related repositories. The intended mitigations are selective checks that account for affected consumers, component-specific release tags, and explicit published versions rather than sibling-checkout dependencies. Publishing automation is still a placeholder; see [release and versioning units](#release-and-versioning-units).

This remains a choice for the current scope, not a permanent rule. Extract a component when a real boundary appears, such as a different owner, consumer, access requirement, or independently operated service. The [shared guidelines](GUIDELINES.md#choosing-a-repository-boundary) give the brief placement criteria.

---

## Separate repositories

The homelab is a distinct service and has different access requirements, so it has its own repositories:

- **Homelab:** [devhub-homelab](https://github.com/CollinPoetoehena/devhub-homelab) (public) and devhub-homelab-private (private) have their own lifecycle, permissions, pipelines, and private configuration. DevHub owns the shared guidance and the workspace and AI setup they use; the homelab repositories own its design and implementation.

The homelab is part of DevHub as my overall personal development hub, even though its source and private operational record need separate repositories. Shared standards, workspace setup, and [task tracking](TASK-TRACKING.md) stay central; implementation, access rights, and publication boundaries stay with the homelab. Other independently operated applications follow the same distinction: link to DevHub for shared guidance, but keep implementation in the owning project.

---

## Established repository structures

These repositories show different ways to keep related modules together (similar to how DevHub is structured as a collection of related modules under one repository); they are examples, not templates:

- [Kubernetes](https://github.com/kubernetes/kubernetes/tree/master/staging/src/k8s.io) stages many Go modules under one repository; it is not a single module but a collection of related modules maintained together.
- [AWS SDK for Java 2.x](https://github.com/aws/aws-sdk-java-v2) and [AWS SDK for Go v2 service modules](https://github.com/aws/aws-sdk-go-v2/tree/main/service) group related SDK modules in their repositories.
- [AWS SDK for Python v4](https://github.com/aws/aws-sdk-python/tree/develop/clients) organizes service clients under `clients/`; [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk) and [Azure SDK for Go](https://github.com/Azure/azure-sdk-for-go/tree/main/sdk) organize SDK packages under `sdk/`. For example, [`azure-ai-agents/pyproject.toml`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-agents/pyproject.toml) declares that package's metadata:

  ```text
  sdk/
  ├── ai/
  │   ├── azure-ai-agents/
  │   │   └── pyproject.toml
  │   ├── azure-ai-inference/
  │   └── azure-ai-projects/
  ├── compute/
  ├── storage/
  └── ...
  ```

  One repository contains many Python packages; it is not one giant Python distribution.
- [Backstage](https://github.com/backstage/backstage) stages many plugins and packages under one repository; it is not a single package but a collection of related components maintained together (under `backstage/package/` directories; one package per directory, similar to the multi-package SDK monorepos above).

---

## Release and versioning units

A managed thing is the unit I maintain, validate, and offer to consumers together. Choose its version boundary around that contract, not around directory count, programming language, or an assumption that every package needs a repository.

| Managed thing | Repository and release approach |
|---|---|
| A monitoring capability with a Python package and Helm chart deployed together | Keep both in one repository and use one coordinated capability release when tested combinations are the supported contract |
| DevHub's related setup script, shared automation, AI customizations, and documentation | Maintain together and use a DevHub release/ref for a coherent set; the shell updater follows a commit rather than requiring every component to share a package version |
| An SDK consumed independently by several applications | Give it its own version and compatibility contract, in DevHub with component tags or in its own repository when a real boundary warrants extraction |
| Several independently consumed packages | Keep independent versions and native manifests; share a repository when coordinated source maintenance is convenient |

A group release does not require inventing a mixed-language package. Keep Python metadata, chart metadata, image tags, and other native artifact identities. For lockstep releases, align their versions where valid; otherwise publish a release manifest listing the exact tested versions and compatibility constraints. Do not silently imply that an application and chart are compatible just because their version strings match.

For independent releases in one repository, use scoped tags such as `monitoring/v1.2.0` or `python-sdk/v0.4.0`, subject to ecosystem requirements such as [Go's module-version tag rules](https://go.dev/ref/mod#vcs-version). Build and validate affected components, including shared dependencies; publish immutable packages/images to the chosen registry and let consumers select explicit versions or digests.

These are supported design choices, not a claim that the placeholder [publishing workflow](GITHUB-ACTIONS.md) implements them. Define metadata ownership, tag format, validation, artifact destination, and consumer upgrade steps in the owning component's release guide before publishing.

---

## Placing new work

For placement criteria and setup steps, see the [shared guidelines for placing packages and components](GUIDELINES.md#placing-packages-and-components) and [setting up a project or package](GUIDELINES.md#setting-up-a-project-or-package).

---

## Naming conventions

For current rules, see the [repository and package naming conventions](GUIDELINES.md#naming-conventions).

---

## Package README link

For the recommended package README content and links, see the [shared guidelines](GUIDELINES.md#package-readme-links).

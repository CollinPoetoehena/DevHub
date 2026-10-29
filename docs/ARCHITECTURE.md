# DevHub Project Structure

How DevHub is organized and why. The generic decision process, trade-offs, and industry examples live in [Repository & Project Organization](../reference/engineering/Repository_Organization.md); this page records how DevHub applies them.

---

## Table of Contents

- [Layout and scope](#layout-and-scope)
- [Why DevHub is one repository](#why-devhub-is-one-repository)
  - [Sole maintainer](#sole-maintainer)
  - [Accepted trade-offs](#accepted-trade-offs)
- [Separate repositories](#separate-repositories)
- [Release and versioning units](#release-and-versioning-units)
- [Placing new work](#placing-new-work)
- [Naming conventions](#naming-conventions)
- [Package README link](#package-readme-link)

---

## Layout and scope

| Path | Owns |
|---|---|
| [`reference/`](../reference/README.md) | Generic theory, practices, and commands; no DevHub-specific conventions |
| [`docs/`](.) | DevHub-specific structure, conventions, decisions, and usage |
| [`.github/`](../.github/) | Workflow configuration and symbolic links to the Copilot definitions in [`docs/copilot/`](copilot/) |
| [`packages/`](../packages/README.md) | Reusable packages, each with native metadata and its own release boundary |
| [`tools/`](../tools/README.md) | Setup, repository management, and maintenance tooling not owned by one project |

Each area's README owns the details of that area. The [root README](../README.md#repository-scope) summarizes this scope.

---

## Why DevHub is one repository

The goal is not as many repositories as possible, but a structure that is convenient for work that is related and often changed together. DevHub's reference material, packages, tooling, setup, GitHub automation, and AI customizations meet that criterion: a change to a practice often touches its reference, an instruction or skill, a workflow, and a package at the same time.

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

These are accepted because they are solvable and cost less than distributing and coordinating the same setup across many closely related repositories. Path- and dependency-aware checks keep validation selective; component-prefixed Git tags release components independently; consumers that need one component can use a published version, such as a Python package or container image in Artifactory or another artifact registry. See [where the complexity lives](../reference/engineering/Repository_Organization.md#where-the-complexity-lives) for the generic mitigations.

This remains a choice for the current scope, not a permanent rule. Extract a component when a real boundary appears, such as a different owner, consumer, access requirement, or independently operated service.

---

## Separate repositories

Projects get their own repository when they are a different service or need different access rights, not because they are large or use another language.

- **Homelab:** [devhub-homelab](https://github.com/CollinPoetoehena/devhub-homelab) (public) and devhub-homelab-private (private) have their own lifecycle, permissions, pipelines, and private configuration. DevHub owns the shared guidance and the workspace and AI setup they use; the homelab repositories own its design and implementation.
- **Other personal projects:** An independently operated application keeps its implementation in its own repository and links to DevHub for shared standards.

The homelab is part of DevHub as my overall personal development hub, even though its source and private operational record need separate repositories. Shared standards, workspace setup, and [task tracking](TASK-TRACKING.md) stay central; implementation, access rights, and publication boundaries stay with the homelab.

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

For independent releases in one repository, use scoped tags such as `monitoring/v1.2.0` or `python-sdk/v0.4.0`, subject to ecosystem requirements (Go subdirectory tags, for example, have their own rules). Build and validate affected components, including shared dependencies; publish immutable packages/images to the chosen registry and let consumers select explicit versions or digests.

These are supported design choices, not a claim that the placeholder [publishing workflow](GITHUB-ACTIONS.md) implements them. Define metadata ownership, tag format, validation, artifact destination, and consumer upgrade steps in the owning component's release guide before publishing.

---

## Placing new work

1. Define the thing: purpose, consumers, access requirements, and what must be validated or deployed together.
2. Keep implementation-local helpers with their application. Add a reusable package only for a real public interface or consumer need.
3. Use DevHub for shared personal-development resources; use a separate repository for a distinct product/service, owner, or access boundary. Reuse an existing home when related changes are routinely coordinated.
4. Choose lockstep or independent versions explicitly using the managed contract above. Independent versioning alone does not require a repository split.
5. Add native metadata, the smallest useful README, relevant checks, and links from the owning entry point. Shared automation changes must validate affected consumers too.
6. Record the choice and exceptions in that README, then track the work in the central DevHub backlog. Revisit the boundary when consumers or maintenance costs change.

For the detailed generic assessment and migration steps, use [Repository & Project Organization](../reference/engineering/Repository_Organization.md).

---

## Naming conventions

Use `devhub-{category}-{project}` for focused repositories. The authoritative [naming standards and exceptions](CONVENTIONS_STANDARDS.md#repository-naming) cover categories, existing broader names, package identifiers, and registry requirements; do not maintain a second naming policy here.

---

## Package README link

Packages that follow DevHub's engineering practices link them once near the top of their README, instead of copying the shared guide:

```markdown
> For shared package design and engineering practices, see
[DevHub's Engineering & Coding Reference](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/engineering/README.md). This README covers this package's setup, usage, design decisions, and exceptions.
```

# DevHub Project Structure

How DevHub is organized and why. This page records project boundaries and setup decisions; general technical details belong in the official documentation linked where needed.

---

## Table of Contents

- [Layout and scope](#layout-and-scope)
- [Why DevHub is a monorepo](#why-devhub-is-a-monorepo)
  - [Coordinated development](#coordinated-development)
  - [Shared maintenance and contributor context](#shared-maintenance-and-contributor-context)
  - [Independent artifacts and releases](#independent-artifacts-and-releases)
  - [Why not a polyrepo for every component](#why-not-a-polyrepo-for-every-component)
  - [When a separate repository is better](#when-a-separate-repository-is-better)
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
| [Root `AGENTS.md`](../AGENTS.md) | Repository-specific agent entry point, linked to owning documentation rather than duplicated in nested files |
| [`docs/`](.) | DevHub-specific [guidelines](GUIDELINES.md), architecture, decisions, and usage |
| [`.github/`](../.github/) | Workflow configuration and Copilot-target customizations when installed |
| [`archive/`](../archive/README.md) | Decision notices for retired approaches; historical content stays in Git history |
| [`packages/`](../packages/README.md) | Reusable packages, each with native metadata and its own release boundary |
| [`tools/`](../tools/README.md) | Shared automation, including [Terraform repository inventory and policy](../tools/repo/README.md) |

Each area's README owns the details of that area. The [root README](../README.md#repository-scope) summarizes this scope.

---

## Why DevHub is a monorepo

DevHub groups related development resources under one maintainer: project guidance, shared AI customizations, GitHub automation, tools, and reusable packages. This is a repository boundary, not a claim that DevHub is one application, one package, or one release unit. The deciding factors are shared ownership and the practical frequency of changes that cross these areas—not a package-count threshold or a requirement to use one language.

These parts are often used and maintained together. A change to a shared practice can affect its documentation, an AI instruction or skill, a workflow, and the tool or package that applies it. Keeping that work in one repository lets the source, affected in-repository callers, and validation change together when appropriate. The [layout and scope](#layout-and-scope) describes what each area owns.

### Coordinated development

- **Review related changes together:** A pull request can show a change to shared guidance alongside the affected workflow, tool, or package. Reviewers can assess the intended practice and its implementation at the same revision instead of coordinating linked pull requests and compatible intermediate states.
- **Find impact in one checkout:** Maintainers can search package metadata, shared tooling, guidance, and in-repository callers together. This helps identify direct dependencies and duplicated implementations; it is not a complete inventory of external consumers or deployed versions.
- **Keep shared practices discoverable:** Contributors can locate existing automation and AI customizations before creating a separate copy. Shared guidance has a central home, while project-specific setup and exceptions remain with their owning project.
- **Give contributors and assistants a common source context:** Related implementation, documentation, tests, and design decisions can be inspected from the same source revision, subject to access restrictions. Co-location does not automatically load every file or replace deliberate context selection and verification.

For example, a change to a common AI customization or development standard may also require updates to its usage guidance and the project setup that consumes it. Those related changes can be reviewed together. If an independently published package must change, its release and consumer upgrade remain separate steps.

### Shared maintenance and contributor context

I am the sole maintainer of DevHub. Keeping related assets together means maintaining common repository settings, contribution conventions, and automation in one place instead of repeating repository-level setup for each component. It also gives me one entry point and shared history when returning to work after a break.

Many components share a specific setup: Python packages, for example, have similar packaging, linting, and testing conventions. A repository per package would multiply repository administration and adoption of those shared practices without necessarily adding a useful boundary. Keeping them together makes common setup easier to maintain while preserving package-specific requirements.

This reduces coordination and configuration drift, but does not eliminate component-specific maintenance. Packages still own their native metadata, dependencies, tests, supported interfaces, and consumer documentation. Shared workflows and standards can be maintained centrally; individual components still need configuration appropriate to their language and lifecycle.

### Independent artifacts and releases

DevHub contains different kinds of assets, including Python and Go packages, Helm charts, tools, documentation, and AI customizations. Sharing source history does not require consumers to install every package, use one runtime, or release all components together.

Each package retains its native metadata and release boundary. A consumer selects published versions or other explicit references, rather than relying on an implicit dependency on the current repository checkout. A related set of artifacts may use a coordinated release when that combination is the supported contract; independently consumed packages can keep independent versions. Publishing automation is not yet implemented for the release approaches described in [release and versioning units](#release-and-versioning-units).

### Why not a polyrepo for every component

A polyrepo gives each component its own repository, history, settings, and contribution workflow. That isolation is useful when it reflects a real boundary. For DevHub's related assets under one maintainer, a repository per component would often move work into cross-repository coordination rather than remove it.

| Concern | DevHub monorepo | Repository per component |
|---|---|---|
| Coordinated change | One pull request can show shared guidance, implementation, and affected in-repository callers together. | Related pull requests must be linked and kept compatible across repositories. |
| Impact discovery | Source and package metadata are searchable in one checkout. | Discovery requires multiple checkouts, cross-repository search, or a maintained catalog. |
| Shared standards and automation | Common definitions have one source location. | Reusable workflows help, but each repository still has to adopt and update its references and configuration. |
| Contributor workflow | One checkout provides context for related assets. | Individual checkouts are smaller, but multi-component changes require assembling compatible revisions. |
| Administration | Common settings and conventions are maintained together. | Repository-specific permissions and settings provide isolation but add setup and maintenance. |
| Release independence | Components need explicit metadata and release discipline. | Separate histories make source isolation explicit, but compatibility and release ordering still need management. |
| Access and failure isolation | Related assets share a repository access boundary, and broad workflow changes can affect other components. | Separate permissions and CI boundaries are easier to maintain. |

Neither layout removes the underlying scalability and workflow requirements: every component still needs appropriate CI/CD, dependency management, validation, and release discipline, whether it lives in one repository or many. The layout changes where that complexity is managed—selective checks and shared configuration in a monorepo, or distributed pipelines and cross-repository coordination in a polyrepo—not whether it exists.

Choose what fits the team size, ownership, usage, scope, and tooling rather than treating either layout as inherently simpler. Polyrepos can reduce overhead with shared tooling and automation; a monorepo also requires deliberate CI selection and release boundaries. DevHub's current shared ownership and closely related components favor a monorepo. Independent versions, external consumers, or different release cadences alone do not require a split, but neither do they justify keeping components together when a more meaningful boundary exists.

### When a separate repository is better

Separate a component when doing so supports genuinely distinct ownership, restricted access, product governance, or an independently operated lifecycle. These boundaries matter more than keeping every related project under one repository. For example, the homelab has separate repositories because it is an independently operated service with different access requirements; DevHub provides shared guidance and workspace setup without owning its implementation. See [separate repositories](#separate-repositories) for that boundary.

DevHub is therefore a bounded monorepo within a broader set of personal projects: shared development resources live here, while independently operated projects remain in their own repositories. The [shared guidelines](GUIDELINES.md#choosing-a-repository-boundary) provide placement criteria.

### Accepted trade-offs

A single repository also has costs:

- more workflows and component configurations in one place;
- more involved CI selection to validate affected components without needlessly validating everything;
- a larger shared history and a shared repository access boundary;
- the possibility that broad workflow or configuration changes affect unrelated components.

These trade-offs are accepted because they are proportionate to the shared ownership and coordinated maintenance of the current scope. Selective checks, component-specific release tags, and explicit published versions can limit coupling; co-location alone does not run cross-component checks or establish compatibility. The publishing workflow remains a placeholder; see [release and versioning units](#release-and-versioning-units).

This is a choice for the current scope, not a permanent rule. Reassess if the codebase grows enough that checkout size, tooling, or CI performance becomes a material constraint, or if ownership, access, operation, or publication boundaries change. Extract selected components when an independent repository addresses the demonstrated constraint better than improving the monorepo tooling.

---

## Separate repositories

The homelab is a distinct service and has different access requirements, so it has its own repositories:

- **Homelab:** [devhub-homelab](https://github.com/CollinPoetoehena/devhub-homelab) (public) and devhub-homelab-private (private) have their own lifecycle, permissions, pipelines, and private configuration. DevHub owns the shared guidance and the workspace and AI setup they use; the homelab repositories own its design and implementation.

The homelab is part of DevHub as my overall personal development hub, even though its source and private operational record need separate repositories. Shared standards, workspace setup, and [task tracking](how-to/TASK-TRACKING.md) stay central; implementation, access rights, and publication boundaries stay with the homelab. Other independently operated applications follow the same distinction: link to DevHub for shared guidance, but keep implementation in the owning project.

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
| DevHub's shared automation, AI customizations, and documentation | Maintain together and use a DevHub release/ref for a coherent set; independently published packages retain their own versions |
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

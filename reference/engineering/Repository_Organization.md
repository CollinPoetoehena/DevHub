# Repository & Project Organization

Practical guidance for deciding where code, packages, automation, and documentation belong. Use it when adding a component, creating a repository, or reconsidering an existing split. [Package Design & Organization](Packages.md) covers package interfaces, distribution, and release procedures; this guide covers the collaboration and maintenance boundaries around them.

This guide is generic. For one applied example, see how [DevHub's project structure](../../docs/PROJECT-STRUCTURE.md) uses it.

---

## Table of Contents

- [Choose boundaries, not repository counts](#choose-boundaries-not-repository-counts)
  - [Where the complexity lives](#where-the-complexity-lives)
- [Deciding where something belongs](#deciding-where-something-belongs)
  - [Decision process](#decision-process)
  - [Placement examples](#placement-examples)
- [Setting up a component or repository](#setting-up-a-component-or-repository)
  - [Scope, ownership, and layout](#scope-ownership-and-layout)
  - [Dependencies and releases](#dependencies-and-releases)
  - [CI, permissions, and shared automation](#ci-permissions-and-shared-automation)
- [Maintaining and revisiting boundaries](#maintaining-and-revisiting-boundaries)
  - [Consolidating or extracting existing work](#consolidating-or-extracting-existing-work)
  - [Using AI to review placement](#using-ai-to-review-placement)
- [Industry examples](#industry-examples)
  - [Azure SDK for Python](#azure-sdk-for-python)
  - [Azure SDK for Go](#azure-sdk-for-go)
  - [Kubernetes](#kubernetes)

---

## Choose boundaries, not repository counts

The goal is convenient, reliable maintenance, **not as many separate repositories as possible** and not one repository at any cost. Start with what is owned, reviewed, and frequently changed together. Separate work when a real product, access, or operational boundary makes that useful.

These are different boundaries:

| Boundary | What it determines |
|----------|--------------------|
| Repository | Git history, commits, pull requests, repository access, and repository-level configuration. |
| Project or component | A coherent capability with an owner and purpose; it can contain several artifacts. |
| Package or artifact | What consumers install or deploy, with explicit dependencies and compatibility expectations. |
| Release | The supported set of changes delivered together; it may cover one artifact or a coordinated set. |
| IDE workspace | Which checkouts are open together; it does not merge histories, permissions, commits, or releases. |

A Python package, Go module, Helm chart, or application does not automatically need its own repository. Conversely, opening several repositories in one workspace does not remove their separate settings, pull requests, dependency updates, and release coordination.

| Approach | Useful when | Cost to manage |
|----------|-------------|----------------|
| Monorepo | Related components share maintainers and frequently need coordinated changes. | Needs discoverable boundaries, dependency-aware checks, and deliberate release selection. |
| Polyrepo | Services, owners, access requirements, or operational lifecycles are genuinely separate. | Cross-repository work needs multiple commits and reviews; copied standards and automation can drift. |
| Hybrid | Shared engineering resources belong together, while products or runtime configuration need separate control. | Needs clear placement rules and maintained links between repositories. |

Repository size alone is not the deciding factor. A large, coherent repository can be easier to maintain than many small ones; a small repository can still be an unclear collection of unrelated work.

### Where the complexity lives

Splitting repositories does not remove complexity; it often moves it into distribution and coordination. Even with centrally maintained reusable workflows, each consuming repository still needs workflow callers, triggers, inputs, permissions, required checks, and updates to pinned references. Copied actions, workflow templates, and AI customization also need an update mechanism or drift independently.

A shared repository concentrates more of that maintenance in one place. It has costs too, but these can be managed without creating a repository for every component:

| Accepted cost | How to manage it | Remaining constraint |
|---------------|------------------|----------------------|
| More GitHub Actions workflows and jobs in one repository. | Reuse common jobs and workflows; select checks by changed paths and affected dependencies. | Shared tooling changes still need broader validation, and required checks must complete reliably. |
| More complex build and release selection. | Give components explicit manifests and release selectors; use component-specific Git tags where appropriate. | Tags identify source revisions; they do not themselves build or publish artifacts. |
| Consumers need only one component, not the whole source tree. | Publish versioned Python distributions, container images, or other artifacts to Artifactory or another suitable package/container registry. Consumers select supported versions; container digests can identify exact images. | Publication, dependency compatibility, consumer upgrades, and rollback still need ownership. |
| Larger Git history and checkouts. | Keep generated artifacts and binaries in artifact storage; use [partial clones and sparse checkouts](https://git-scm.com/docs/git-clone#Documentation/git-clone.txt---filterltfilter-specgt) or shallow CI checkouts where appropriate. | These reduce local transfer or checkout costs, not the repository's underlying history; release tooling may need tags or deeper history. |

These are available mitigations, not a claim that every mechanism is already implemented. Versioned artifacts decouple consumption from source layout: an application can install one Python package version or deploy one container image version without adopting every change in the hub. A separate repository is not required merely to distribute or version that artifact.

The comparison is therefore manageable centralized complexity versus repeated setup, distribution, and coordinated changes across repositories. For closely related work that frequently changes together under the same ownership and access rules, the former can be the smaller ongoing burden.

---

## Deciding where something belongs

### Decision process

Apply these questions in order:

1. **What is being added, and who needs it?** Name the capability, owner, consumers, and expected output. Check existing components and supported upstream tools before adding another implementation.
2. **Does it need a different access or trust boundary?** Different readers, external collaborators, confidential configuration, or production privileges can require a separate repository. Do not put restricted material into a broadly readable repository and rely on directory names or review ownership to hide it.
3. **Is it an independently operated service or product?** A service with its own deployment, on-call responsibility, operational approvals, and retirement plan is a strong candidate for a separate repository. Keep its service-specific code, tests, and deployment definition together unless a separate deployment boundary requires otherwise.
4. **What changes together in practice?** Look at recent changes, not just imagined architecture. If code, documentation, charts, workflows, and tooling repeatedly need coordinated edits by the same maintainers, prefer keeping them together.
5. **Is a new package enough?** Different installation needs or dependency footprints may justify a package or module boundary inside the existing repository. Independent versions alone do not require independent repositories.
6. **What does the split actually save?** Compare ownership, security, and build-isolation benefits with extra settings, commits, releases, dependency updates, and onboarding. A new language, directory, or small script is not sufficient justification by itself.
7. **Record the decision.** State why the component belongs here, what stays outside it, and which concrete change would justify revisiting the boundary. If no meaningful separation is needed, use the existing coherent home.

Do not treat this as a score where convenience can outweigh required access isolation. Permissions and confidentiality are constraints; convenience is a trade-off within those constraints.

### Placement examples

| Addition | Likely home | Create a separate boundary when |
|----------|-------------|---------------------------------|
| Reusable integration SDK | Shared package area, with focused domain modules or packages. | Ownership, access, consumers, or dependency costs make the current grouping unsuitable. |
| Shared monitoring library and reusable chart | Shared development hub if maintained and changed together. | They become an independently maintained product with a distinct lifecycle or audience. |
| Checks specific to one application | The application's repository, using shared libraries where useful. | They become a supported capability reused by other applications. |
| Application or service | Its product repository when operated independently. | Closely coupled services may instead share a repository if ownership and access align. |
| Generic CLI or helper script | Existing tooling area; package it when installation or compatibility matters. | It becomes a separately owned product or needs different distribution/access controls. |
| Reusable CI, AI guidance, or engineering documentation | Central development hub, with consumer-specific configuration kept locally. | Different governance or audiences make sharing inappropriate. |
| GitOps desired state | Environment/deployment repository when runtime approvals and privileges differ. | Application source and desired state can share a home only when their governance genuinely aligns. |
| Private environment configuration | Restricted environment repository or appropriate external configuration system. | Never move secrets into source control merely to simplify the layout. |

Language and tool boundaries need not be repository boundaries. A monitoring component can contain a Python package and Helm chart; a service can contain Go code, a container definition, and deployment templates. Keep reusable building blocks separate from the environment-specific decisions made by their consumers.

---

## Setting up a component or repository

### Scope, ownership, and layout

1. **Write a short scope statement:** purpose, maintainer, consumers, what belongs here, and what does not. Put this in the owning README or decision record rather than copying the whole shared guide.
2. **Choose the smallest useful home:** an existing module for internal functionality; a new package for a separate installation/API contract; a new repository only for a justified collaboration, product, or access boundary.
3. **Use a discoverable location:** group by capability or ecosystem where that helps navigation. Avoid catch-all directories and pre-creating empty categories for technologies not yet used.
4. **Give each real artifact its native metadata:** for example, Python packaging metadata, a Go `go.mod`, or a Helm `Chart.yaml`. Document how to build, validate, and use it; follow [language and tool conventions](Languages_and_Tools.md).
5. **Link it from the entry point:** readers should be able to find its owner, setup, public interface, release procedure, and supported capabilities without searching every directory. Link shared guidance instead of copying it.

An illustrative shared hub could use this layout; it is not a mandatory scaffold, and a real hub should only contain the components it actually needs:

```text
development-hub/
|-- packages/
|   |-- python/<package>/
|   `-- go/<module>/
|-- charts/<chart>/
|-- .github/
|   |-- actions/<action>/
|   `-- workflows/
|-- tools/
|-- docs/
`-- reference/
```

Different languages retain their own tooling and artifacts. A shared repository does not require one mixed-language package, common runtime, or artificial cross-language API.

### Dependencies and releases

1. **Make dependency direction explicit:** tools and applications may use an SDK; the SDK should not depend on every tool built on top of it. Keep service-specific orchestration out of generic libraries.
2. **Choose what is released together:** use independent component versions when consumers upgrade them separately. A coordinated version is also reasonable for a managed unit, such as a monitoring package and chart intentionally delivered together. Document which artifacts and compatibility guarantees a release covers.
3. **Make independent releases identifiable:** use unambiguous tags and artifact names, such as `python/storage/v1.2.0` and `charts/monitoring/v2.0.0`, where ecosystem rules permit. These are examples, not universal naming rules; nested Go modules have specific [module-version tag requirements](https://go.dev/ref/mod#vcs-version).
4. **Keep installs reproducible:** local development may use editable installs or workspaces; released consumers need declared dependencies and supported versions rather than accidental sibling-directory imports. Test the built artifact or published module path, not only the source checkout.
5. **Define adoption and rollback:** a shared repository can review related changes in one commit, but publishing artifacts and updating deployed consumers are not atomic. Record compatible version combinations and release ordering when one artifact requires another.

For detailed versioning and publication practices, see [Versioning and distribution](Packages.md#versioning-and-distribution). Do not promise independent releases until selection, tagging, building, and publication actually support them.

### CI, permissions, and shared automation

1. **Establish the baseline:** configure the appropriate maintainers, visibility, default branch, review requirements, and required checks. For a separate repository, also set its license, automation permissions, and deployment environments deliberately.
2. **Validate affected components:** map changed paths to checks and include downstream dependents. Changes to shared libraries, lockfiles, build tools, or workflow definitions may require broader validation; file-path filters alone do not capture the dependency graph.
3. **Keep required checks reliable:** use an always-running dispatcher or another supported design so skipped component work does not leave required checks pending. See GitHub's [path-filter behavior](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#onpushpull_requestpull_request_targetpathspaths-ignore).
4. **Publish deliberately:** documentation-only edits should not publish every artifact. Release only selected, validated components, with write credentials limited to the publication jobs that need them.
5. **Reuse maintained automation:** prefer callable [reusable workflows](https://docs.github.com/en/actions/sharing-automations/reusing-workflows) and shared actions over copying implementations into every repository. Consumers retain their triggers, inputs, permissions, and environment-specific decisions. A template is a starting copy, not a mechanism that keeps existing copies synchronized.
6. **Keep trust boundaries real:** review ownership such as [CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners) can route reviews but does not restrict directory read access. Required owner review also needs appropriate branch rules. Use separate repositories when readers must differ, and protected environments for deployment approvals where available.
7. **Share AI guidance intentionally:** centralize genuinely common guidance and keep project-specific exceptions with the project. Verify the editor's actual loading/setup behavior rather than assuming a sibling checkout's instructions automatically apply.
8. **Exercise the setup:** confirm a component change runs its checks and affected dependents, a shared-tooling change reaches all affected components, and a documentation-only change does not cause unrelated releases. Verify a clean checkout can follow the documented setup before relying on it.

These are setup decisions to implement and verify, not a statement that this repository already provides complete reusable workflows or dependency-aware release automation.

---

## Maintaining and revisiting boundaries

Keep the arrangement while it reduces real work. Warning signs include repeated cross-repository pull requests, copied actions/workflows or AI guidance drifting apart, and substantial time spent maintaining identical repository settings. Those can justify consolidation when access and ownership align.

Consider extraction when a component gains independent ownership or operations, needs different access, serves a largely unrelated audience, or creates measured tooling and build costs that selective validation cannot reasonably address. First check whether clearer directories, native package boundaries, or better CI solve the problem without a repository split.

A single workspace is useful for related repositories, but does not make every split free. Likewise, one repository makes a coordinated source change easier, but does not automatically make every component compatible or every deployment safe.

### Consolidating or extracting existing work

1. Inventory source, artifacts, owners, dependencies, licenses, release tags, workflows, and existing consumer URLs. Check uncommitted changes before moving anything.
2. Decide the destination's access and release model first. Audit candidate content and retained history for restricted data before any public consolidation; never assume deleting a current file removes its historical contents.
3. Plan identifier compatibility: repository URLs, Python distribution/import names, Go module paths, chart references, and workflow references may be public contracts. A source move does not require cosmetic renames.
4. Move only the agreed components, preserving appropriate history and attribution. Update affected imports, dependency paths, build contexts, documentation links, CI working directories, and release selectors.
5. Validate from clean checkouts and test consumer installation or workflow usage. Where repositories remain separate, verify the release/adoption order rather than relying on local sibling checkouts.
6. Update the central index and old entry points; archive or redirect the old home only after consumers have a supported path forward. Record remaining migration work explicitly.

### Using AI to review placement

Provide the scope, owners, access requirements, actual manifests, existing release process, and examples of changes that required coordination. Ask for the smallest justified boundary and the concrete costs of both grouping and splitting, not a generic monorepo recommendation.

Have the review distinguish observed facts from proposed setup, identify affected consumers and paths, and suggest checks that prove the move preserves installation, builds, and releases. Verify the result against the repository and official tool documentation; do not provide secrets, private configuration, or unrelated organizational context to an unapproved system.

---

## Industry examples

These projects demonstrate that one repository can contain many packages or modules. They do not prove that every team should use the same layout or adopt large-project tooling. For another large-scale perspective, see [Google's monorepo discussion](https://research.google/pubs/why-google-stores-billions-of-lines-of-code-in-a-single-repository/).

### Azure SDK for Python

The [Azure SDK for Python repository](https://github.com/Azure/azure-sdk-for-python) groups packages beneath service-area directories. A simplified excerpt:

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

Each named package directory represents a distinct Python distribution, not a separate Git repository and not one repository-wide Python package. For example, [azure-ai-agents](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents), [azure-ai-inference](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-inference), and [azure-ai-projects](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects) have their own package contents and release information.

The agents directory's [pyproject.toml](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-agents/pyproject.toml) contains tool configuration; its [setup.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-agents/setup.py) defines distribution metadata. The tree illustrates package placement, not a requirement that every package declare all metadata in `pyproject.toml`. The useful lesson is a package per meaningful capability inside a shared repository, with package-level dependencies and versions.

### Azure SDK for Go

The [Azure SDK for Go repository](https://github.com/Azure/azure-sdk-for-go) contains multiple Go modules under [sdk/](https://github.com/Azure/azure-sdk-for-go/tree/main/sdk). For example, [sdk/storage/azblob/go.mod](https://github.com/Azure/azure-sdk-for-go/blob/main/sdk/storage/azblob/go.mod) declares the blob-storage module and its dependencies.

This is not one indivisible Go module simply because it has one Git repository. The Python and Go SDKs also live in different repositories: shared purpose does not require every language to share a checkout. Apply the package/module separation where useful without copying their scale or repository count.

### Kubernetes

The [kubernetes/kubernetes repository](https://github.com/kubernetes/kubernetes) keeps core implementation and related components together. Its [staging area documentation](https://github.com/kubernetes/kubernetes/blob/master/staging/README.md) explains how authoritative source for modules such as `k8s.io/api`, `k8s.io/apimachinery`, and `k8s.io/client-go` lives under `staging/src/k8s.io/` and is published to separate repositories.

Kubernetes is therefore not an example of an entire organization contained in one repository: it combines coordinated source development with separately published modules and other repositories. Its staging/publishing machinery is a project-specific solution, not a prerequisite for a small development hub.

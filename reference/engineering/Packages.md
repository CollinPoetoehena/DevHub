# Package Design & Organization

Generic guidance for organizing, distributing, and maintaining reusable packages within a team. Language- and tool-specific practices belong in [Languages & Tools](Languages_and_Tools.md); general documentation, testing, and error-handling practices belong in [Engineering Concepts](Concepts.md).

For repository boundaries, project placement, monorepo/polyrepo decisions, and setup steps, see [Repository & Project Organization](Repository_Organization.md). A separate package does not automatically require a separate repository.

See [Scope and approach](README.md#scope-and-approach) for why these are illustrative considerations rather than a complete package-design specification, and where to explore further.

---

## Table of Contents

- [Package boundaries and ownership](#package-boundaries-and-ownership)
- [Package naming](#package-naming)
- [Team workflows and reusable layers](#team-workflows-and-reusable-layers)
  - [Working across languages](#working-across-languages)
- [Shared SDKs and specialized packages](#shared-sdks-and-specialized-packages)
  - [Why a shared SDK can be worth the effort](#why-a-shared-sdk-can-be-worth-the-effort)
  - [Keep the scope deliberate](#keep-the-scope-deliberate)
- [CLI tools and scripts](#cli-tools-and-scripts)
- [Package documentation and layout](#package-documentation-and-layout)
- [Versioning and distribution](#versioning-and-distribution)
  - [Creating a Git-based release](#creating-a-git-based-release)
  - [Deleting or withdrawing a release](#deleting-or-withdrawing-a-release)
  - [Ecosystem-specific distribution](#ecosystem-specific-distribution)

---

## Package boundaries and ownership

- Treat a reusable package as a supported product: define its purpose, owner, consumers, public interface, and compatibility expectations.
- Share code when it has multiple real consumers or prevents meaningful duplication and behavior drift; keep service-specific implementation with its service.
- Split packages for a genuine difference in domain, abstraction level, consumers, dependency footprint, permissions, or release cadence, not just because code is in a different directory.
- Keep the supported API small, dependencies explicit, and optional integrations separate when their cost is not justified for every consumer.

---

## Package naming

Repository names and installable package, module, chart, or import names are related but separate contracts; they do not have to be identical. Choose a convention once per project or team, record it in that project's own documentation, and record deliberate exceptions. For one applied convention, see [DevHub's naming conventions](../../docs/PROJECT-STRUCTURE.md#naming-conventions).

- **Recognizable pattern:** A prefix-type-topic pattern such as `<prefix>-<type>-<topic>` keeps origin, ecosystem, and capability visible, for example `acme-python-storage-tools` or `acme-go-backup`. A multi-component hub or product can use a broader name; a naming convention is not a reason to split it.
- **Clear, stable topics:** Use descriptive lowercase names, digits where useful, and hyphens between repository-name words. Avoid spaces, unnecessary abbreviations, and version numbers in names; versions belong in release metadata and tags. Describe what the component provides rather than naming every dependency or technology it uses.
- **Python names:** Adapt hyphens to underscores for importable identifiers: a distribution named `acme-python-storage-tools` can expose `acme_python_storage_tools`. Distribution names and import names are separate contracts; [distribution-name normalization](https://packaging.python.org/en/latest/specifications/name-normalization/) does not automatically create or rename the import package.
- **Go names:** The module path follows the actual repository location, while package declarations use short, valid Go identifiers rather than the full hyphenated repository name. For example, a repository named `acme-go-backup` might contain package `backup`. Follow the [Go module and package guidance](Languages_and_Tools.md#go), including major-version path rules where applicable.
- **Automation artifacts:** Use the ecosystem's own identifier rules rather than copying the repository name blindly. Ansible collections use `namespace.collection` with valid namespace and collection identifiers; roles have their own names. Helm chart names use lowercase letters, digits, and hyphens, not Python-style underscores. See [Ansible practices](Languages_and_Tools.md#ansible) and [Helm naming conventions](https://helm.sh/docs/chart_best_practices/conventions/#chart-names).
- **Registry requirements take precedence:** The public [Terraform Registry](https://developer.hashicorp.com/terraform/registry/modules/publish), for example, requires repository names in the form `terraform-<provider>-<name>`, even when a project's own convention differs for modules installed directly from Git. Identify ownership through the registry namespace and documentation instead of assuming one prefix works with every registry.
- **Preserve consumer compatibility:** Document repository, distribution, import, and registry identifiers in the package README when they differ. Do not rename established public identifiers merely for cosmetic consistency; a rename can affect dependency declarations, imports, source URLs, and release discovery, so provide a migration path when a change is necessary.

---

## Team workflows and reusable layers

Teams commonly combine official clients, a small amount of shared integration code, reusable infrastructure definitions, and application-specific workflows. They do not need a new library for every technology: first ask whether the need is simply to call a supported API or to provide a recurring team contract.

| Layer | Responsibility | Example |
|-------|----------------|---------|
| Vendor client or protocol | Product API communication, authentication mechanisms, request/response handling. | Use a supported cloud SDK or Kubernetes client instead of rebuilding its API. |
| Shared runtime package | Repeated domain operations, configuration boundaries, error contracts, and useful defaults. | An artifact-store interface used by several applications, backed by the vendor SDK. |
| Provisioning and deployment | Create and configure infrastructure, access policies, and deployed workloads. | Terraform modules for a bucket and permissions; Helm charts for an application. |
| CLI or automation | Coordinate a task using the runtime package and existing tools. | Upload a backup or inspect a deployment; keep task-specific decisions out of the SDK. |
| Consuming application | Business decisions, environment configuration, and adoption of supported package versions. | Select what to back up, which destination to use, and when the workflow should run. |

- **Separate provisioning from use:** Creating a storage bucket and uploading an object are different responsibilities. Provision resources through the infrastructure workflow; runtime code normally needs only the permissions required to use them, not permission to reconfigure the platform.
- **Add a contract, not a duplicate API:** A shared package can standardize a repeated artifact-upload workflow without reproducing every storage operation. A single uncomplicated upload may be clearer with direct SDK use. See [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) and [Kubernetes client libraries](https://kubernetes.io/docs/reference/using-api/client-libraries/) for examples of upstream capabilities to reuse.
- **Make ownership practical:** Assign maintainers, document supported consumers, review shared changes, and validate public behavior before release. Consumer teams choose and test upgrades; a central package is not permission to silently change every application.
- **Keep delivery proportionate:** Local development can use editable/source installs, consumers can use a known Git revision, and a registry can distribute built artifacts when that improves installation and governance. A private package registry is an option, not a prerequisite for internal reuse.
- **Grow from real needs:** Start with a small coherent capability and split packages when dependencies, consumers, or lifecycle justify it. Keep environment values and credentials outside package defaults, and avoid creating shared configuration or logging frameworks merely because the names sound reusable.

### Working across languages

- A repository can contain Python, Go, and infrastructure projects without making them one mixed-language package. Each keeps its own manifests, dependency management, supported runtime/toolchain, checks, and release artifact.
- Share contracts rather than forcing one language to import the other's implementation: a documented CLI with exit codes and structured output, an API, or a versioned configuration/data schema can connect independent tools.
- Introduce a cross-language boundary only when needed. Define error behavior and compatibility, test both sides, and avoid adding a service, foreign-function interface, or translation layer just because two languages exist.
- Share CI conventions and release automation where useful, but let packages validate and release independently. Choose languages for actual consumer and deployment needs rather than rewriting working code to appear more production-ready; see [Languages & Tools](Languages_and_Tools.md).

---

## Shared SDKs and specialized packages

Use a shared SDK when consumers need a supported interface to the same domain or platform. Its purpose is **consistency, not reinvention**: reuse vendor libraries and add only the shared contracts and integration behavior consumers actually need.

### Why a shared SDK can be worth the effort

An SDK can initially seem like more work than calling an API directly. The useful comparison is its design, release, and support cost versus independently implementing and maintaining the same integration in several consumers—not versus doing no work.

- **The alternative is often repeated code:** Authentication, timeouts, proxy configuration, error translation, and resource cleanup still need to happen. Several services calling the same integrations would otherwise implement and test that behavior independently, then gradually diverge as their copies change. Centralizing the recurring layer moves existing responsibility into one place rather than inventing a layer for its own sake. The saving is not just fewer lines: maintainers investigate an edge case once and preserve the correction centrally instead of rediscovering which consumers contain which variation. Without this package, it is **written** *N* times (violates DRY principle) and then **drifts** *N* ways (maintenance nightmare) because it lives in multiple places independently (e.g. in every service repository). **The package does not add a layer; it moves a layer that already existed in every repository into one *central* place.**
- **One supported interface:** Predictable clients, configuration, models, and errors reduce what each consumer must learn and maintain. Keep provider setup at construction or another clear boundary instead of spreading authentication details and payload translation throughout application logic. Resource-oriented operations and meaningful domain exceptions let callers express their intent without depending on every vendor's response format. Consistency also makes examples, onboarding, and reviews easier, but should not flatten genuine differences between providers or prevent direct use of an upstream feature.
- **Shared reliability:** Implement and test recurring connection, timeout, streaming, and retry behavior once where useful, then reuse it across integrations. For example, explicit timeouts can prevent an indefinitely blocked call, connection reuse avoids unnecessary setup, and streaming can keep a large response from being loaded entirely into memory. Make defaults and overrides explicit; retries must account for idempotency and side effects rather than being enabled indiscriminately. Shared mechanisms reduce duplicated reliability work, while each application still owns its deadlines, recovery policy, and operational requirements.
- **Contracts vendors do not provide:** Capture recurring domain expectations, such as requiring exactly one result, without rebuilding upstream models that already fit. A checked single-result operation can distinguish zero matches from ambiguous matches instead of leaving consumers to select the first item silently. Add provider-neutral models only when consumers genuinely need a shared shape, such as consistent DNS records across supported providers. These contracts preserve useful domain knowledge and reduce repeated translation, but should not become a complete duplicate of each vendor's schema or hide unsupported capabilities.
- **Fixes have one home:** A reviewed package release can carry a correction to multiple consumers instead of requiring separate implementations and tests in each repository. A regression test can protect the shared behavior, and release notes can explain the effect and any migration steps. This makes the supported implementation easier to identify and review, rather than searching for copied integrations that may have drifted. Consumers must still adopt the update and validate their integration; centralization does not update deployed applications automatically or eliminate the wider impact of a shared defect.
- **The investment must pay back:** Shared code introduces design work, ownership, documentation, compatibility commitments, release coordination, and a wider impact for defects. Compare those ongoing costs with the repeated work and operational risk actually removed; a central SDK is not automatically worthwhile because reuse sounds desirable. Prefer direct vendor-library use when integration is small, consumers do not share stable needs, or the abstraction costs more than the duplication it removes. Start with demonstrated common behavior, grow only when justified, and keep vendor-specific escape routes available rather than making every new feature wait for a wrapper release.

### Keep the scope deliberate

- Keep related integrations in one distribution when they share infrastructure, consumers, and coordinated changes; retain clear domain boundaries internally. Do not combine unrelated software merely to centralize it.
- Put specialized CLIs, operational tools, and frameworks in separate packages when their consumers, dependencies, or lifecycle differ. They may depend on the SDK; the SDK should not depend on optional tooling built on top of it.
- Do not build a complete shadow vendor API or take over application orchestration. Duplicating every endpoint and model creates a second compatibility burden that can lag behind upstream features and deprecations.
- Direct use of a vendor SDK, CLI, or API remains a valid option for provider-specific capabilities. The shared SDK should not become a mandatory bottleneck for functionality it does not need to own.
- Providing integration helpers does not transfer ownership of the underlying product or consumers' business/content decisions to SDK maintainers. Keep responsibility and decision authority explicit.
- Use established ecosystems as examples, not mandatory designs to copy: [Azure SDK](https://azure.github.io/azure-sdk/) and [Kubernetes clients](https://kubernetes.io/docs/reference/using-api/client-libraries/).

---

## CLI tools and scripts

- **Versioned tools:** Package a CLI or script when users need installation, dependencies, a stable interface, controlled upgrades, reproducibility, or rollback. A script can be a proper released artifact even when it is small.
- **SDK-backed tooling:** Keep command parsing, presentation, and operational workflows in the tool; reuse the SDK for domain behavior instead of embedding CLI concerns in the SDK.
- **Unreleased scripts:** A separate scripts repository is suitable for shared conveniences that do not need independent package releases or compatibility promises. They still belong in source control with ownership and usage notes; "not versioned" here means no separate artifact/release version, not no Git history.
- **Project-local scripts:** Keep scripts tied to one application's build or operations alongside that application rather than moving them into a shared repository merely for centralization.
- Reassess the boundary when an unreleased script becomes a dependency of other systems or requires a dependable upgrade path.

---

## Package documentation and layout

Link shared engineering guidance once, near the top of the package README, rather than copying it; keep package-specific instructions and exceptions in that README. For example:

```markdown
> For shared package design and engineering practices, see the
[team engineering guide](<link-to-shared-guide>). This README covers this package's setup, usage, design decisions, and exceptions.
```

> **Why no fixed template?** Earlier guidance included specific package templates. Packages now have the flexibility to choose documentation and source layouts that fit their type, size, and consumers: an Ansible collection, Python distribution, and Go module need not have identical structures. Keeping fixed templates here would duplicate evolving ecosystem guidance and create another set of examples to maintain. Use the relevant official conventions and the topics below as guidance, not a prescribed scaffold.

Use a README as the entry point. Packages may use whatever structure fits their ecosystem, size, and consumers; the following are useful topics, not a mandatory template or directory tree:

- **Purpose and contract:** What the package provides, intended consumers, supported interface, ownership, and important limitations.
- **Design:** Boundaries, dependencies, important decisions and reasons; link larger design topics from `docs/` when needed.
- **Development:** Prerequisites, local setup, dependency management, and relevant build, formatting, linting, or generation commands.
- **Testing, if applicable:** How to run meaningful checks, required fixtures or environments, and any safe-target constraints; distinguish placeholders from implemented tests.
- **Installation and usage:** Supported runtimes/platforms, how to install a released version, configuration, and a concise consumer example.
- **Releases and maintenance:** Versioning, publishing, compatibility/deprecation policy, changelog or release notes, and upgrade guidance.

Keep the actual source/build layout ecosystem-appropriate; see the package-structure links in [Languages & Tools](Languages_and_Tools.md). Link shared practices once rather than copying them into each README or scattering links throughout source files.

---

## Versioning and distribution

- Define the public compatibility contract and use [Semantic Versioning](https://semver.org/) where appropriate: major for breaking changes, minor for compatible features, patch for compatible fixes.
- Use the artifact ecosystem's version syntax. Publish distinct pre-release builds for validation and reserve stable versions for validated releases; never overwrite a published version.
- Preserve release history when renaming the same software. Coordinate changed repository/package identifiers and consumer URLs rather than resetting versions automatically.
- Publish reproducible artifacts from identifiable source revisions, automate shared release steps where practical, and make installation/version selection explicit.
- Document consumer impact, deprecations, and migration paths in release notes; keep package metadata, artifact versions, and source tags consistent.

### Creating a Git-based release

A version tag identifies the source revision for a release; it does not itself build a package, upload an artifact, or create a hosting platform's release entry. Teams can create tags manually or through CI after the intended checks pass. Use an annotated tag, or a signed tag when required by policy; see [Git tagging](https://git-scm.com/docs/git-tag).

For a repository using `1.0.0` as its tag format (verify the remote before publishing):

```sh
# Tag the latest commit
git tag -a 1.0.0 -m "Release 1.0.0"
git push --tags

# Or tag a specific commit with:
git log --oneline -n 10
git tag -a 1.0.0 <commit-id> -m "Release 1.0.0"
git push origin refs/tags/1.0.0
```

Publish the intended tag, not every local tag. Treat published tags as immutable; consumers can select a tag, while a full commit ID identifies the source even if someone later moves a tag. Reproducible builds also require controlled dependencies and build inputs.

### Deleting or withdrawing a release

Prefer a corrected version over deleting a published one. An incorrect, unconsumed tag may be removed after verifying its commit, remote, and impact; a shared tag requires coordination with consumers. Do not retag released code, amend shared history, or force-push a replacement as a normal release-fix procedure.

The following removes only the specified Git tag, locally and remotely. Inspect it first and execute deletion only when its consequences are understood and authorized:

```sh
git tag --list 1.0.0
git --no-pager show --no-patch 1.0.0
git tag -d 1.0.0
git push origin --delete refs/tags/1.0.0
```

A Git tag, a hosting-platform release entry, and a registry artifact are separate objects. Removing one does not automatically remove the others or invalidate cached copies. Use the ecosystem's withdrawal, deprecation, or retraction process where available; warn consumers and publish migration guidance rather than assuming deletion repairs an installed version.

### Ecosystem-specific distribution

- **Python:** Build and publish distributions with consistent package metadata and an ecosystem-supported version; a Git tag alone does not upload a wheel or source distribution. See [packaging and publishing](https://packaging.python.org/en/latest/tutorials/packaging-projects/) and [Python version specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/).
- **Go:** Module releases use version tags with a `v` prefix; module location and major-version rules can affect the tag and import path. See [publishing modules](https://go.dev/doc/modules/publishing), [module versioning](https://go.dev/doc/modules/version-numbers), and [retracting versions](https://go.dev/doc/modules/gomod-ref#retract). Deleting a tag does not erase versions already served by module proxies.
- **Other artifacts:** Use the supported registry/release process for charts, images, modules, or binaries. Keep source provenance and artifact versions aligned, and follow the relevant references in [Languages & Tools](Languages_and_Tools.md) instead of applying one ecosystem's commands everywhere.

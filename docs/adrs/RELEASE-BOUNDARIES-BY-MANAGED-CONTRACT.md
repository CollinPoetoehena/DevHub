# ADR: Set Release Boundaries by Managed Contract

## Context

DevHub contains different kinds of assets, including packages, Helm charts, tools, documentation, and AI customizations. They share source history but do not necessarily share consumers, runtimes, or compatibility requirements. Some artifacts may be consumed independently; others may form a capability that is tested and offered together.

Repository layout and directory count do not establish which artifacts must be compatible. Ecosystems also retain their own package metadata and versioning requirements, such as [Go module version tags](https://go.dev/ref/mod#vcs-version) and [Python package metadata and releases](https://packaging.python.org/en/latest/overview/). DevHub's publishing automation for the release approaches below is not yet implemented.

## Decision

Use the **managed contract**—the artifacts maintained, validated, and offered to consumers together—as the release boundary. Keep native metadata and artifact identities. Use a coordinated capability release when a tested combination is the supported contract; use independent versions or scoped tags when consumers select components independently. When a group release cannot express valid native versions, publish a release manifest with exact tested versions and compatibility constraints rather than implying compatibility from matching version strings.

Consumers select explicit published versions or immutable references such as image digests. The component owner documents release metadata, tags, validation, artifact destination, and consumer upgrade steps before publishing. This ADR records the release policy; it does not claim that publishing automation or any proposed release is already available.

## Consequences

### Positive

- **Consumer-facing versions**: The release version communicates the compatibility contract consumers actually select, rather than coupling unrelated components because they share a repository.
- **Tested combinations**: A group of artifacts can be validated and released together when their tested combination is the supported offering.
- **Native identities**: Manifests, registries, and ecosystem-specific identity remain intact instead of forcing mixed artifacts into one artificial package.

### Negative

- **Contract ownership**: Owners must identify the consumer-facing contract and maintain explicit metadata, validation, and upgrade guidance for each release unit.
- **Release bookkeeping**: Independent versions in one repository need scoped tags and selective build/validation rules; coordinated releases need a manifest or other unambiguous record when native version formats do not align.
- **Automation gap**: The policy does not supply release automation. Until that is implemented, publishing requires documented, component-appropriate procedures.

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| **Version by managed contract** (project-defined policy): release together only the artifacts whose tested combination is offered as one contract, while independently consumed components retain native versions; see [Go module version tags](https://go.dev/ref/mod#vcs-version), [Python packaging](https://packaging.python.org/en/latest/overview/), and [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases). | Reflects how consumers select and validate artifacts while supporting both a coordinated capability and independently consumed packages. It preserves native package metadata and makes compatibility explicit. | Requires each owner to define the contract, keep tags and manifests unambiguous, and validate affected artifacts and dependencies. Shared source does not automatically trigger compatible releases. | This aligns versions with actual consumer guarantees without imposing a repository-wide lockstep or assuming every directory is independently releasable. | Consumer contracts converge across the repository or a specific set of artifacts adopts a different, explicit compatibility agreement. |
| **One version for all of DevHub**: publish one repository-wide version for every package, tool, and other artifact; see [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases). | Gives users one release reference and can simplify a deliberately unified product with a single compatibility and adoption contract. | Unrelated components would share version changes and release timing. A repository release could be mistaken for a promise that all artifacts are compatible, although the repository contains distinct components and consumers. | DevHub is a collection of resources, not one application or package. One release version would obscure the independently managed contracts. | DevHub becomes one product with a single consumer-facing compatibility contract and coordinated release lifecycle. |
| **Version each package or directory independently**: assign every component a separate release regardless of whether artifacts are consumed or validated together; see [Go module version tags](https://go.dev/ref/mod#vcs-version) and [Python packaging](https://packaging.python.org/en/latest/overview/). | Gives independently consumed components clear version histories and avoids unrelated release coupling. Native ecosystems commonly provide component-level version metadata. | A capability made from multiple artifacts still needs a tested compatibility set and an upgrade path. Independent versions alone do not tell consumers which combinations are supported. Directory boundaries may not match the maintained consumer contract. | Independent versioning is appropriate when consumers select artifacts independently, but it is not sufficient for combinations maintained and offered together. | Every artifact is genuinely consumed and supported independently, with no coordinated capability release or compatibility set to communicate. |
| **Move every independently released component to its own repository**: align source repository boundaries with release boundaries. | Provides repository-level isolation and can make access, history, and component workflows independent. | Repository separation adds cross-repository coordination for shared source changes and does not eliminate dependency compatibility or release ordering. It is not required merely to publish independent versions. | Release independence alone is not a sufficient reason to split a repository; the current shared ownership and maintenance context remains useful. | A component also gains distinct ownership, access, operation, or governance needs that justify repository isolation. |

## Status

Proposed. This record captures the release design documented in DevHub; publishing implementation and separate approval of this ADR have not been recorded.

## Date

2026-11-13

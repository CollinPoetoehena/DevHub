# ADR: Keep DevHub as a Bounded Monorepo

## Context

DevHub contains shared project guidance, AI customizations, GitHub automation, tools, and reusable packages. One maintainer owns these related resources, and changes can span documentation, automation, and the components that use it. The [project structure](../ARCHITECTURE.md) distinguishes those areas; sharing a repository does not make them one application, package, or release.

The decision is about the boundary for DevHub's shared development resources, not a rule that every related personal project belongs in the same repository. Ownership, access requirements, independent operation, and demonstrated scale constraints can justify separate repositories.

## Decision

Keep DevHub as a bounded monorepo for shared development resources that have common ownership and are often maintained together. Keep each component's native metadata, validation, and release boundary explicit. Independently operated services and projects with distinct access requirements remain in their own repositories and link to DevHub's shared guidance where useful.

This boundary favors coordinated maintenance and a common source context for the current scope. It does not require lockstep releases, a universal runtime, or a single application build. Reassess the boundary if ownership, access, operation, publication, or material scale constraints change.

This follows industry practices for organizing related modules under a single repository while maintaining clear boundaries for each component's metadata, validation, and release process. These repositories show different ways to keep related modules together (similar to how DevHub is structured as a collection of related modules under one repository); they are examples, not templates:

- **Kubernetes staging**: [Kubernetes](https://github.com/kubernetes/kubernetes/tree/master/staging/src/k8s.io) stages many Go modules under one repository; it is not a single module but a collection of related modules maintained together.
- **AWS Java and Go SDKs**: [AWS SDK for Java 2.x](https://github.com/aws/aws-sdk-java-v2) and [AWS SDK for Go v2 service modules](https://github.com/aws/aws-sdk-go-v2/tree/main/service) group related SDK modules in their repositories.
- **Python and Azure SDKs**: [AWS SDK for Python v4](https://github.com/aws/aws-sdk-python/tree/develop/clients) organizes service clients under `clients/`; [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk) and [Azure SDK for Go](https://github.com/Azure/azure-sdk-for-go/tree/main/sdk) organize SDK packages under `sdk/`. For example, [`azure-ai-agents/pyproject.toml`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-agents/pyproject.toml) declares that package's metadata:

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
- **Backstage packages**: [Backstage](https://github.com/backstage/backstage) stages many plugins and packages under one repository; it is not a single package but a collection of related components maintained together (under `backstage/package/` directories; one package per directory, similar to the multi-package SDK monorepos above).

## Consequences

### Positive

- **Coordinated changes**: Related guidance, automation, packages, and in-repository callers can be reviewed and searched together; coordinated changes do not require compatible intermediate states across several repositories.
- **Shared maintenance**: Repository settings and conventions have one home for the resources maintained by the same owner.
- **Independent artifacts**: Components can remain independently packaged and versioned without multiplying repository-level administration solely because they use different languages or release cadences.

### Negative

- **Shared access boundary**: Material requiring different permissions must remain outside the repository or in a separately controlled repository.
- **Selective validation**: More components increase the need for careful workflow ownership so a broad configuration change does not cause unrelated effects.
- **Compatibility obligations**: A common checkout and history do not establish compatibility between artifacts or identify every external consumer. Native metadata, validation, release discipline, and compatibility documentation remain necessary.

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| **DevHub monorepo** (project-defined boundary): keep shared guidance, automation, tools, and packages in one repository; see [DevHub's documented layout](../ARCHITECTURE.md#layout-and-scope) and [Atlassian's monorepo overview](https://www.atlassian.com/git/tutorials/monorepos). | One checkout can provide source context for changes that span shared practices and their in-repository consumers. The single-maintainer setup avoids repeating repository-level settings for closely related assets. | All contents share an access boundary. CI selection, component-specific configuration, and release boundaries must be deliberate; co-location alone does not run checks or prove compatibility. | This matches current shared ownership and recurring cross-area maintenance. The alternatives add repository coordination without a demonstrated boundary for the shared resources. | Repository size or tooling becomes a material constraint, or ownership, access, operation, or publication boundaries become meaningfully distinct. |
| **Polyrepo by component**: put each package, tool, or documentation area in an independent repository; compare [Atlassian's monorepo overview](https://www.atlassian.com/git/tutorials/monorepos) and [GitHub repository visibility](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility). | Each component can have its own access, settings, history, workflow, and lifecycle. Smaller component checkouts may be useful when maintainers or consumers work independently. | Cross-component changes need coordinated reviews and compatible revisions. Shared guidance and automation need adoption and updates across repositories, while repository-level setup is repeated. | Most DevHub areas have the same owner and are maintained together. Separate repositories per component would move that work into cross-repository coordination without addressing a current isolation need. | A component gains distinct ownership, access requirements, independent operation, or publishing governance, or a concrete scale constraint makes extraction preferable to improving monorepo tooling. |

## Status

Proposed. This record captures the current direction documented in DevHub; separate approval of this ADR has not been recorded.

## Date

2026-11-13

# ADR: Keep Homelab Repositories Separate from DevHub

## Context

The homelab is part of DevHub as a personal development hub, but it is also an independently operated service with its own design, implementation, lifecycle, pipelines, and access requirements. DevHub owns shared guidance, workspace setup, and task tracking; the homelab repositories own the service.

The current arrangement uses a public `devhub-homelab` repository for shareable project material and a private `devhub-homelab-private` repository for restricted implementation and configuration. GitHub repository visibility is set at the repository boundary, not independently for folders; see [GitHub's repository visibility documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility).

## Decision

Keep homelab implementation and operational configuration outside DevHub. Maintain its public and private material in the homelab's own repositories, with DevHub continuing to provide shared standards, workspace setup, and task tracking. Keep restricted information in an appropriately protected system; a relationship between projects does not override access boundaries.

This is a project-specific boundary, not a requirement that every project using DevHub guidance receive its own repository.

## Consequences

### Positive

- **Independent lifecycle**: The homelab can manage its service lifecycle and pipelines independently from DevHub's shared resources.
- **Distinct access controls**: Public guidance and private implementation/configuration can use different repository access controls rather than sharing a single visibility boundary.
- **Clear hub ownership**: DevHub can remain a shared development hub without becoming the implementation owner for every project that uses its guidance.

### Negative

- **Cross-repository coordination**: Shared changes can require coordination across DevHub and the homelab repositories; contributors need to follow links and identify which repository owns a change.
- **Separate administration**: Repository settings, workflows, and documentation entry points are maintained separately.
- **Placement discipline**: The public/private split requires care about where material belongs; repository separation is not a substitute for checking whether content is appropriate for its destination.

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| **Separate public and private homelab repositories** (project-defined boundary): use a public repository for shareable guidance and a private repository for restricted implementation/configuration; see [GitHub repository visibility](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility) and [DevHub's boundary summary](../ARCHITECTURE.md#separate-repositories). | Keeps the homelab's lifecycle separate from DevHub while allowing public material and restricted configuration to have different repository-level access. | Requires coordination and ownership clarity across repositories; duplicated repository administration and links must be maintained. | This fits the distinct service lifecycle and access needs while leaving shared standards and setup in DevHub. | The service lifecycle or access requirements materially change, or a different approved storage arrangement can meet both requirements with less coordination. |
| **Place all homelab material in DevHub**: manage implementation and shared development resources under one repository boundary; see [GitHub repository visibility](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility). | One repository could make related guidance and implementation easier to locate and review together. | The homelab would share DevHub's access and repository lifecycle. Restricted configuration cannot be protected merely by placing it in a folder, and homelab operations would be coupled to the shared hub. | It does not fit the homelab's distinct service ownership and access requirements. | The homelab no longer needs a distinct lifecycle or restricted material, and its ownership and access model align with DevHub. |
| **Keep all homelab material in one separate repository**: choose one repository visibility for both public guidance and implementation; see [GitHub repository visibility](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility). | Gives the homelab one project home and avoids cross-repository coordination within the service. | A repository has one visibility setting. Making the whole repository public may expose restricted configuration; making it private would limit access to shareable public guidance. | The current material has different access requirements, so one repository boundary does not meet both needs. | There is no longer a need to publish guidance separately from restricted implementation, or an approved mechanism changes the required access boundary. |

## Status

Proposed. This record captures the current repository arrangement documented in DevHub; separate approval of this ADR has not been recorded.

## Date

2026-11-13

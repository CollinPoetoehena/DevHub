# ADR: Use APM for AI Customization Distribution

## Context

The shared instruction and development-setup packages need a maintained way to declare dependencies, select versions, install content, and update supported customization primitives. Copying files is possible, but owning a custom resolver, installer, and host-specific deployment mappings would recreate package-management work.

The decision drivers are declarative dependencies, repeatable distribution without a homegrown package manager, reviewable updates, and explicit consumer ownership. This record chooses the distribution mechanism; [package design](PACKAGE-DESIGN.md) separately owns the package split and destinations, and the [synchronization TODO](SYNCHRONIZATION.md) owns future update automation.

---

## Decision

Use [APM](https://microsoft.github.io/apm/) as the distribution mechanism for both customization packages. Consumers declare dependencies and their lock/update policy; APM resolves and deploys supported content. This decision does not require installing both packages at every destination.

### Why APM

Choose APM because it already owns the package-distribution lifecycle that both units need. Its manifest declares dependencies, its lockfile records resolved versions and content hashes, and its supported targets deploy customization primitives into host-specific locations. [Dependency updates](https://microsoft.github.io/apm/reference/cli/update/) use the same declared dependency model instead of a separately maintained synchronization mechanism.

- **Reuse distribution logic**: Delegate dependency resolution, pinning, installation, updates, and target-aware deployment to the package manager rather than design, implement, and maintain those capabilities ourselves.
- **One lifecycle for both units**: Instructions and the development setup can have different destinations and update policies while sharing the same package-management mechanism.
- **Reviewable inputs**: Manifests and lockfiles make selected sources and resolved content inspectable. Consumers still review provenance, licenses, permissions, and updates; pinning is not proof of safety or correct behavior.
- **Supported target mapping**: Reuse APM's maintained deployment mappings instead of hardcoding every primitive's destination in a custom distributor. Support is limited to the documented target matrix and must be verified for the chosen host.

Native plugins are a credible alternative for bundled workflows, and Git or manual synchronization can distribute files. APM is selected for its explicit dependency and deployment boundary, not because those alternatives cannot work. Any necessary local script should only bridge the consumer-selected scope to supported destinations, not reimplement package resolution or the installation/update engine. APM does not choose the consumer's scope or enforce runtime behavior.

APM's [target matrix](https://microsoft.github.io/apm/reference/targets-matrix/) defines deployment support and paths; it is not proof that a particular user/workspace scope is discovered. Installation, discovery, and correct behavior remain separate facts to verify during implementation.

---

## Consequences

### Positive

- **Managed distribution**: APM handles the package-distribution logic instead of making DevHub maintain its own dependency resolver, version/lock handling, installer, updater, and target mappings. Local integration remains limited to any necessary scope adapter.
- **Consistent package lifecycle**: Both units use the same dependency and deployment mechanism without coupling their installation destinations or update cadence.
- **Reviewable versions**: Declared dependencies and locked content let consumers inspect what an installation or update selects.

### Negative

- **Package-manager dependency**: Distribution depends on APM's supported primitives, target behavior, and evolving contracts. Package-manager updates need review, and consumer-selected local scopes may still require an adapter.
- **Scope verification**: Local synchronization and host discovery require explicit validation, especially for parent workspaces and direct repository sessions.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [APM](https://microsoft.github.io/apm/): declare customization dependencies, resolve and lock their content, and deploy supported primitives through target mappings. | Reuses an existing package lifecycle for both instructions and workflows; avoids owning a custom resolver, installer, and update engine. | Adds a package-manager dependency; target support and local scope integration still require validation. | Selected: package-management reuse and an explicit distribution boundary best fit the two-unit design. | APM no longer supports required primitives or destinations adequately, or another mechanism demonstrably reduces maintenance while preserving the required lifecycle. |
| [Native agent plugins](https://code.visualstudio.com/docs/agent-customization/agent-plugins), including [Copilot CLI plugins](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference): install bundles through the client's plugin system or marketplaces. | Reuses native discovery, installation, and update experiences and is attractive for a coherent development workflow. | Available primitives, installation scopes, and behavior depend on client and plugin format. The repository-instruction and separate local-workflow lifecycles would need validation against that contract. | APM provides the chosen manifest/lock and target-deployment boundary for both units without adding a separate plugin-management lifecycle. This is a fit judgment, not a claim that plugins lack versioning or cannot satisfy the design. | Native plugin management demonstrably covers both units' required scopes, reproducibility, and updates with less integration work. |
| [npx](https://docs.npmjs.com/cli/v11/commands/npx/): execute an installer or synchronization CLI from a local or remotely fetched npm package. | Reuses npm package delivery and caching; an explicit version can select the installer without requiring a global CLI installation. Convenient when Node.js/npm is already part of the environment. | Requires Node.js/npm and runs package code. npx is a command runner, not itself an AI customization package manager: deployment mappings, customization dependency/lock handling, updates, and ownership must be supplied by the invoked tool. | Avoids a global installer but does not by itself replace APM's distribution lifecycle. A custom npx-distributed CLI would still make DevHub own that logic unless an existing tool provides it. | An existing npm-delivered tool satisfies the required customization lifecycle and host scopes with less maintenance; using npx only to launch such a tool is not a competing architecture. |
| [Git submodules](https://git-scm.com/docs/git-submodule): pin a shared source repository at a commit within a consumer repository. | Reuses Git history and commit-based source selection; contributors can inspect the exact shared source revision. | Bringing source into the repository does not deploy primitives into host locations. Initialization, updates, and deployment adapters remain consumer responsibilities, and repository coupling is unnecessary for a local workflow setup. | Source versioning alone does not replace the customization package lifecycle or avoid owning deployment logic. | Shared source checkout is itself the desired contract and deployment is already handled by existing tooling. |
| **Custom copy/sync scripts or manual copies**, a project-defined approach using [native customization locations](https://code.visualstudio.com/docs/agent-customization/overview). | Allows arbitrary destinations and is quick for a small disposable setup without package metadata. | Version selection, dependency resolution, updates, ownership, collision handling, and host mappings become local responsibilities; unmanaged copies can drift. | It would rebuild distribution capabilities already supplied by APM. Retain only a narrow scope adapter where necessary, not a second package manager. | A disposable experiment needs no shared lifecycle, or a required destination needs a small adapter around the selected package manager. |

---

## Status

Accepted: the user selected APM as the distribution mechanism. Package boundaries and synchronization are separate records; migration, scripts, manifests, and runtime validation remain unimplemented.

---

## Date

2026-11-13

---

# Changelog

- 2026-11-13: Clarified why APM is selected over native plugins, Git submodules, and custom synchronization, including the benefit of reusing package-distribution logic rather than maintaining it locally. The two-unit architecture is unchanged.
- 2026-11-13: Added npx as an alternative, distinguishing npm-delivered CLI execution from the customization distribution lifecycle supplied by the invoked tool.
- 2026-11-13: Moved into the distribution-and-synchronization folder and extracted package boundaries into [package design](PACKAGE-DESIGN.md) and future automation into the [synchronization TODO](SYNCHRONIZATION.md). The APM choice and original decision date are unchanged.

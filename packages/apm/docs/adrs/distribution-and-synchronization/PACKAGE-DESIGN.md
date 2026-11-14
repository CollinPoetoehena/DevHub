# ADR: Separate Shared Guidelines from Local Development Packages

## Context

Shared guidelines are repository guidance: common standards should be present in every participating repository, available to contributors regardless of their agent or workflow. Generic agents and skills are a local development environment used by the team members who choose that workflow, not a dependency of the repository itself. Stack-specific guidance maps to the capabilities of its selected stack and belongs with that stack.

Installing both everywhere distributes the same development environment unnecessarily. It creates managed files, commits, synchronization work, and overlapping discovery for capabilities the repository does not need to carry. The decision drivers are clear boundaries, guidance available wherever repository work happens, independent workflow choice, and less distribution and maintenance overhead.

Use **guidelines** for the tool-independent concept; Copilot calls them instructions and Claude calls them rules. This terminology does not replace host-required filenames or establish cross-tool discovery. [Distribution](DISTRIBUTION.md) owns the choice of APM; this record owns package contents, consumers, and destinations.

---

## Decision

Maintain separate APM package families, with an independent shared baseline and opt-in local development stacks:

| Package | Responsibility and consumer | Intended destination |
|---|---|---|
| `guidelines-core` | Common engineering, security, testing, documentation, and AI-customization guidelines; no generic agents, skills, or stack-specific placeholders | Every repository adopting those standards, independently of a team member's workflow |
| `development-core` | Planner and Implementation Orchestrator entry roles, Implementer, one Reviewer, and focused generic skills; no shared guideline bundle | The selected local development scope of team members using the workflow |
| `development-python`, `development-go`, `development-rust`, `development-java`, `development-containerization`, `development-iac` | Opt-in technology skills/resources and scoped instruction maps that supplement common guidelines and route to their own stack's capabilities | The selected local development scope of users adopting those stacks |

Use these directory names under `packages/apm/` and `devhub-`-prefixed manifest identities, such as `devhub-guidelines-core` and `devhub-development-python`. Keep Python/FastAPI/Django together, Java/Kotlin/Spring Boot together, Docker/Kubernetes/Helm together, and Terraform/Ansible/Bicep together. Consumers choose relevant stacks rather than install every technology.

The goal is to **avoid unnecessary distribution**, not merely rename bundles. Common repository guidelines travel with the code; a team member's generic development workflow and optional stack capabilities do not need to travel with every repository. Separate the shared core at the source-package boundary rather than rely on filtering one mixed bundle during installation.

### Boundaries

- **Repository guidance**: Keep shared guidelines present in all participating repositories, including sessions started directly inside them. They apply whether the contributor uses the selected workflow, another workflow, or the default agent. Adopting `guidelines-core` must not install development agents or skills.
- **Team-member environment**: Install generic agents and skills only for team members who use them, in their chosen development scope. Updating that environment should not require commits to every repository they edit.
- **Repository-specific capabilities**: Keep local facts, commands, constraints, and genuinely repository-specific skills with their repository. A repo-specific capability needed by its contributors is different from a generic personal/team workflow.
- **Stack ownership**: Keep technology-specific instruction maps beside their stack skills and references. Each map states the common baseline, additional stack defaults/conventions/checks, and when to use available skills. It does not duplicate common standards or replace them with a mandatory skill dependency.
- **Independent dependencies**: Keep shared instruction dependencies in `guidelines-core` and generic skill dependencies in `development-core`. Stack packages may depend on `development-core` for required shared capabilities. Neither development packages nor their dependencies should automatically deploy the repository guideline package into the local scope; `guidelines-core` must not depend on development packages.
- **Independent ownership**: Consumers own dependency references, lock/update policy, destination, ignore policy, and local additions. Preserve existing files and review collisions rather than overwrite consumer customizations.
- **Private context**: Keep work-specific knowledge and secrets out of public generic packages. Package separation does not establish data-access or permission isolation.

The [guidance-layering ADR](../ai-customizations/GUIDANCE-INSTRUCTION-LAYERING.md) owns how rules compose, while the [AI development workflow](../workflow/AI-DEVELOPMENT-WORKFLOW.md) and [workflow-agent ADR](../workflow/WORKFLOW-AGENTS-AND-FOCUSED-SKILLS.md) own execution policy and role responsibilities. Neither requires the generic workflow to be copied into each repository. Repositories retain their declared tooling and constraints; stack maps supplement that context rather than override it. Common guidelines remain useful without the local development workflow.

The eight source packages implement these names and boundaries. `development-core` currently defines four roles in `.apm/agents/` and focused local `sharing-context`, `adr`, `draft-github-issue`, and `commit-command` skills; its [manifest](../../../development-core/apm.yml) separately declares only `create-agentsmd` and `acquire-codebase-knowledge` from Awesome Copilot. The stack manifests depend on `development-core`; `guidelines-core` declares upstream instruction dependencies. Local source validation confirms manifests and references; it does not establish consumer installation, host discovery, or runtime behavior. Installation and synchronization remain separate work.

Manifest refs and lock state have different lifecycles. Upstream `#HEAD` dependencies request a mutable Git ref at resolution time; APM's generated lockfile records the resolved commit and content hashes for reproducible installs. A `#HEAD` declaration does not continuously update installed content. APM's [update command](https://microsoft.github.io/apm/reference/cli/update/) re-resolves dependencies against their allowed refs; consumers must choose and review that update process.

### Consumer-selected scope

The consumer chooses the appropriate development-setup destination:

- **Personal and work split**: Separate setups may serve `~/projs/personal` and `~/projs/work`, with different agents, skills, package versions, or local policies. One possible CLI pattern is to start in the selected parent working directory and add intended repositories as task directories.
- **Team or project setup**: A work project may use an approved shared workflow rather than a personal one. Deliberate project-level installation is allowed when needed by that project; it is not the default for every generic capability.
- **User-wide setup**: A supported user location is suitable when one environment is appropriate across projects. Do not install conflicting profiles globally and assume the working directory isolates them.

Working directory, access to added directories, and customization discovery are different contracts. [CLI directory commands](https://docs.github.com/en/copilot/reference/cli-command-reference) do not prove inheritance of parent instructions, agents, or skills. Verify the host's discovery in the chosen scope and direct repository sessions. APM's target paths do not automatically implement a personal/work profile.

The [synchronization record](SYNCHRONIZATION.md) describes the existing central repository-PR delivery and its current manifest-contract limits, alongside deferred local development-scope updates. Both families use APM, but their consumers, update cadence, and distribution destinations remain independent.

---

## Consequences

### Positive

- **No redundant workflow distribution**: Generic workflow files remain in the team members' development environment rather than being copied and committed into repositories that do not need them.
- **Rules independent of workflow**: Every participating repository carries guidance even when a contributor chooses another or no custom workflow.
- **Clear package boundaries**: Standards describe how repository work should be done; the development setup describes how its users coordinate that work. Each package has a distinct consumer and lifecycle.
- **Less repository churn**: Agent/skill environment updates do not automatically create unrelated repository changes.
- **Consumer flexibility**: Personal, work, team, and project setups can select relevant technology stacks without installing unrelated skills or coupling repository standards to a workflow.

### Negative

- **Separate lifecycles**: Consumers must keep repository guidelines and their selected local workflow/stacks compatible; installing one family does not imply the other is present.
- **Discovery obligations**: Local scopes and direct repository sessions require verification instead of assuming inheritance.
- **More package surfaces**: Core plus stack packages need distinct manifests, dependencies, and selection. Stack instruction scopes and links must remain accurate without assuming every skill is installed.
- **Mutable upstream refs**: A `#HEAD` manifest reference can resolve to different content on a later update. Lockfiles preserve a selected resolution, but maintainers must review deliberate refreshes and avoid assuming the manifest is live synchronization.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [One APM bundle in every repository](https://microsoft.github.io/apm/): distribute standards, generic agents, and skills together. | A single manifest can recreate the complete setup for every contributor. | Generic workflow updates create repository churn, couple standards to personal workflow choices, and duplicate capabilities where a local setup already supplies them. | Repository rules need broad presence; generic development capabilities do not need repeated installation. | A team deliberately requires a fully repository-pinned workflow for every contributor. |
| **One shared guideline package containing every stack**: a project-defined bundle of common and language/tool rules using [APM](https://microsoft.github.io/apm/). | Fewer manifests and one guideline update surface; scoped files can limit task-specific context. | Every consumer receives guidance for unrelated technologies, and stack maps are separated from the skills/references they describe. | Keep the repository baseline common and technology maps with opt-in local stacks, accepting additional package-selection work. | The stack set is small and uniformly relevant, or separate stack ownership no longer provides enough value. |
| **One mixed core package with selective installation**: a project-defined bundle of guidelines, agents, and skills using [APM](https://microsoft.github.io/apm/). | Maintains one core source package while attempting different deployment subsets. | Destination separation depends on filtering support and configuration; a normal mixed install can distribute generic workflow files into repositories or duplicate repository standards locally. | Separate source packages make the consumer boundary explicit without relying on unverified selective installation. | Tested distribution mechanisms provide an equally clear boundary and the mixed source lifecycle offers a demonstrated benefit. |
| [User-only customizations](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference): keep both rules and workflow in a personal profile. | Avoids repository-managed customization files and makes one user's updates convenient. | Other contributors and direct repository sessions may lack shared standards; local profiles can mix personal and work assumptions. | Guidance must be available in participating repositories independently of a specific team member's profile. | A rule is truly personal and should not govern other contributors; keep that preference local. |

---

## Status

Accepted: the user selected `guidelines-core` for shared repository standards, separate local `development-core` agents/skills, and opt-in development stacks with their own instruction maps. The eight source packages now implement the split. Consumer installation, synchronization, and runtime discovery remain future work.

---

## Date

2026-11-13

---
# Changelog

- 2026-11-14: Updated `development-core` contents to the four-role and focused-skill design, and clarified that mutable `#HEAD` refs resolve through APM rather than continuously updating installations.
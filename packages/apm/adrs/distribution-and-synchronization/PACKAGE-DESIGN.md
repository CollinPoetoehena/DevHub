# ADR: Separate Repository Instructions from Team Development Workflows

## Context

Instructions are repository guidance: shared standards should be present in every participating repository, available to contributors regardless of their agent or workflow. Generic agents and skills are a development environment used by the team members who choose that workflow, not a dependency of the repository itself.

Installing both everywhere distributes the same development environment unnecessarily. It creates managed files, commits, synchronization work, and overlapping discovery for capabilities the repository does not need to carry. The decision drivers are clear boundaries, guidance available wherever repository work happens, independent workflow choice, and less distribution and maintenance overhead.

The transitional common-plus-language/tool-package layout is not a constraint. [Distribution](DISTRIBUTION.md) owns the choice of APM; this record owns what the packages contain, who consumes them, and where they belong.

---

## Decision

Maintain two distinct APM packages with different consumers and destinations:

| Package | Responsibility and consumer | Intended destination |
|---|---|---|
| Common instructions | Shared engineering, language, framework, and tool guidelines for work in participating repositories, independent of a particular team member's workflow | Every repository adopting those standards |
| AI development setup | Planner, Implementation Coordinator, necessary subordinate roles, and generic shared skills for the actual team members using the development workflow | Their selected local user/workspace/team/project development scope, not every repository by default |

The goal is to **avoid unnecessary distribution**, not merely rename two bundles. Repository instructions travel with the code because they describe standards applicable there. A team member's generic development workflow does not need to travel with every repository merely because that member works on it.

### Boundaries

- **Repository guidance**: Keep shared instructions present in all participating repositories, including sessions started directly inside them. They apply whether the contributor uses the selected workflow, another workflow, or the default agent.
- **Team-member environment**: Install generic agents and skills only for team members who use them, in their chosen development scope. Updating that environment should not require commits to every repository they edit.
- **Repository-specific capabilities**: Keep local facts, commands, constraints, and genuinely repository-specific skills with their repository. A repo-specific capability needed by its contributors is different from a generic personal/team workflow.
- **Central instruction package**: Replace separate Python, Go, Java, containerization, and other stack packages with scoped instruction files in the central package. This is the target design, not a migration already performed.
- **Independent ownership**: Consumers own dependency references, lock/update policy, destination, ignore policy, and local additions. Preserve existing files and review collisions rather than overwrite consumer customizations.
- **Private context**: Keep work-specific knowledge and secrets out of public generic packages. Package separation does not establish data-access or permission isolation.

The [guidance-layering ADR](../ai-customizations/GUIDANCE-INSTRUCTION-LAYERING.md) owns how rules compose, and the [two-agent ADR](../workflow/SEPARATE-PLANNING-AND-IMPLEMENTATION-AGENTS.md) owns workflow responsibilities. Neither requires the generic workflow to be copied into each repository.

### Consumer-selected scope

The consumer chooses the appropriate development-setup destination:

- **Personal and work split**: Separate setups may serve `~/projs/personal` and `~/projs/work`, with different agents, skills, package versions, or local policies. One possible CLI pattern is to start in the selected parent working directory and add intended repositories as task directories.
- **Team or project setup**: A work project may use an approved shared workflow rather than a personal one. Deliberate project-level installation is allowed when needed by that project; it is not the default for every generic capability.
- **User-wide setup**: A supported user location is suitable when one environment is appropriate across projects. Do not install conflicting profiles globally and assume the working directory isolates them.

Working directory, access to added directories, and customization discovery are different contracts. [CLI directory commands](https://docs.github.com/en/copilot/reference/cli-command-reference) do not prove inheritance of parent instructions, agents, or skills. Verify the host's discovery in the chosen scope and direct repository sessions. APM's target paths do not automatically implement a personal/work profile.

The [synchronization TODO](SYNCHRONIZATION.md) separately records future local update and repository-PR automation. Both units use APM, but their consumers, update cadence, and distribution destinations remain independent.

---

## Consequences

### Positive

- **No redundant workflow distribution**: Generic workflow files remain in the team members' development environment rather than being copied and committed into repositories that do not need them.
- **Rules independent of workflow**: Every participating repository carries guidance even when a contributor chooses another or no custom workflow.
- **Clear package boundaries**: Standards describe how repository work should be done; the development setup describes how its users coordinate that work. Each package has a distinct consumer and lifecycle.
- **Less repository churn**: Agent/skill environment updates do not automatically create unrelated repository changes.
- **Consumer flexibility**: Personal, work, team, and project setups can differ without splitting instruction ownership into language packages.

### Negative

- **Two lifecycles**: Consumers must keep instructions and their selected workflow compatible; installing one package does not imply the other is present.
- **Discovery obligations**: Local scopes and direct repository sessions require verification instead of assuming inheritance.
- **Central package breadth**: Language/tool rules share a package lifecycle; their scopes must prevent irrelevant instructions from distracting tasks.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [One APM bundle in every repository](https://microsoft.github.io/apm/): distribute standards, generic agents, and skills together. | A single manifest can recreate the complete setup for every contributor. | Generic workflow updates create repository churn, couple standards to personal workflow choices, and duplicate capabilities where a local setup already supplies them. | Repository rules need broad presence; generic development capabilities do not need repeated installation. | A team deliberately requires a fully repository-pinned workflow for every contributor. |
| [Separate language/tool APM packages](https://microsoft.github.io/apm/): keep common plus opt-in Python, Go, and other stack packages. | Consumers can select and version language guidance independently. | Adds manifests, dependencies, release surfaces, and package-selection decisions for content that can be scoped instruction files. | The design favors one central instruction package, with activation scoped inside its files rather than package topology. | A domain needs a genuinely independent contract or substantial executable capability, not merely a few instructions. |
| [User-only customizations](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference): keep both rules and workflow in a personal profile. | Avoids repository-managed customization files and makes one user's updates convenient. | Other contributors and direct repository sessions may lack shared standards; local profiles can mix personal and work assumptions. | Guidance must be available in participating repositories independently of a specific team member's profile. | A rule is truly personal and should not govern other contributors; keep that preference local. |

---

## Status

Accepted: the user selected separate instruction and development-setup packages and clarified their consumers and boundaries. Package migration and runtime discovery remain future implementation work.

---

## Date

2026-11-13

---

# Changelog

- 2026-11-13: Extracted the package split and scope reasoning from the combined distribution record; clarified that generic team-member workflows should not be distributed to every repository. The original package choice and decision date are preserved.

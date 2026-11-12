# DevHub AI Customizations and APM

[APM](https://microsoft.github.io/apm/) distributes reusable package-managed instructions and optional skills or stack/tool guidance. The native coding-agent harness owns execution: understanding the request, planning, tool use, editing, validation, iteration, and useful delegation. DevHub does not provide a second harness.

DevHub's change-delivery workflow is the repository-local native Copilot skill at [`.github/skills/orchestrate/SKILL.md`](../../.github/skills/orchestrate/SKILL.md). It is not part of an APM package and is not installed by APM. A file being present in a checkout does not prove that a particular Copilot client discovers or invokes it; verify discovery and behavior in the intended environment.

The goal is better engineering output with less repeated explanation, not a sophisticated customization system. The [retired orchestration experiment](../../archive/AI-CUSTOMIZATIONS.md#retired-v2-orchestration-layer) explains why this boundary matters.

This guide owns design, setup, and usage. The [common package](common/README.md) and [stack packages](#package-design) own their contents and provenance. The [common changelog](common/CHANGELOG.md) records baseline releases; [Getting Started](../../docs/GETTING-STARTED.md) owns shared-workspace arrangements.

## Table of Contents
TODO

---

## Why create AI customizations

Default agents are capable, but they do not know a repository's/project's conventions, architecture, or validation workflow, so the same context gets repeated in every chat. Customizations write that context down once in a form both agents and people can use:

- **Lasting standards and fundamentals:** coding principles, documentation rules, review discipline, and engineering workflow outlive any specific tool, language, or project. Capturing them once standardizes code and projects now and keeps paying off across a whole career. When tools change, add or swap a skill for the new tool while the fundamentals stay in place.
- **Consistent guidance without memorization:** standards are available across tasks without anyone needing to repeat every rule; tooling must enforce mandatory checks.
- **Document once, use twice:** conventions need documenting anyway. Written as instructions and skills, they guide AI automatically and remain readable for humans, so nobody has to memorize them.
- **Faster onboarding:** new contributors, and future me returning to an old project, benefit from institutional knowledge automatically.
- **Less repetition and drift:** shared expectations live in one versioned package instead of being re-explained in prompts or copied across repositories.
- **Predictable, reviewable workflows:** fixed roles, routes, and reports make AI-assisted work traceable and easier to verify.

GitHub Copilot already provides [delegation to subagents](https://code.visualstudio.com/docs/agents/run/subagents) in supported harnesses; the main agent can coordinate work without a custom orchestrator. That mechanism does not define your engineering workflow: roles, validation, review, and approvals depend on the project's stack, risks, and team conventions, so a universal preset would still need tailoring. Start with repository guidance and add skills or specialists where useful; introduce a thin orchestrator, such as [DevHub's workflow](common/README.md#workflow), when you need explicit, repeatable routing. Copilot supplies the mechanism; customizations describe the policy, while permissions and CI enforce hard boundaries.

Default setups are sufficient for many general tasks, but discovering repository context during a task is not the same as knowing which local conventions and checks are mandatory. Explicit guidance reduces that guesswork. Customizations complement the default agent and the human contributors; they do not replace engineering judgment or guarantee a result. Keep them small and relevant: overlapping instructions add maintenance, stale facts, and conflicts.

See for an example in the official documentation: [Before and after customization examples](https://awesome-copilot.github.com/learning-hub/before-after-customization-examples/). This is a simple illustration but it demonstrates the core idea: capturing repository-/project-specific knowledge once and reusing it consistently across tasks improves quality and reduces repetitive explanations significantly.

---

## Concepts

| Primitive | What it is | Use when |
|---|---|---|
| Repository instructions (`AGENTS.md`) | Repository or subtree context, when discovered by the host | Concise local facts and routes to owning documentation |
| Scoped instructions (`*.instructions.md`) | Instructions that may be project-wide, path-matched (`applyTo`), or selected by a task-relevant description, depending on the host | Short rules for matching work, such as coding or documentation standards |
| Skills (`SKILL.md`) | On-demand procedures with optional scripts and references; only the description loads until relevant | A specific, repeatable task such as committing, testing, or writing comments |
| Agents (`*.agent.md`) | Roles with their own instructions, tool selection, and allowed subagents | Distinct responsibilities, context isolation, or delegation |
| Hooks | Shell commands run at agent lifecycle events | Deterministic enforcement, such as blocking a command or running a formatter |
| Prompts (`*.prompt.md`) | Reusable, user-invoked requests | A recurring single request with parameters |

Instruction discovery depends on the host and harness: for example, project-wide and `applyTo`-matched instructions are included under their configured conditions in VS Code, while supported instruction types and scope vary across Copilot clients. A path match can select a file predictably, but neither selection nor instruction-following is guaranteed across tools. See the [VS Code](https://code.visualstudio.com/docs/agent-customization/custom-instructions) and [GitHub Copilot](https://docs.github.com/en/copilot/concepts/prompting-and-context/custom-instructions) documentation for current behavior.

Instructions can serve as reliable entry points in hosts that include them under the configured conditions: keep durable rules and orientation concise, then point to the relevant deeper documentation or skill and say when to follow or open it. A link is a map, not a claim that the linked content is automatically loaded.

Rules of thumb: most work needs it, use an instruction; a specific task needs it, use a skill; a different role, toolset, or model needs it, use an agent; it must always happen, use a hook, CI, or permissions, because instructions guide rather than enforce.

An agent can delegate to subagents: each runs in a fresh, isolated context and returns one result, which keeps the coordinator's context focused. Handoffs instead switch the active agent for the user.

Learn more:

- [Building custom agents](https://awesome-copilot.github.com/learning-hub/building-custom-agents/) and [agents and subagents](https://awesome-copilot.github.com/learning-hub/agents-and-subagents/)
- [Custom agents and subagents](https://docs.github.com/en/copilot/concepts/customizations/custom-agents#custom-agents-and-subagents) (GitHub Docs)
- [Creating effective skills](https://awesome-copilot.github.com/learning-hub/creating-effective-skills/)
- [Defining custom instructions](https://awesome-copilot.github.com/learning-hub/defining-custom-instructions/)
- [Before and after customization examples](https://awesome-copilot.github.com/learning-hub/before-after-customization-examples/)
- [Copilot configuration basics](https://awesome-copilot.github.com/learning-hub/copilot-configuration-basics/)
- [VS Code hooks](https://code.visualstudio.com/docs/agent-customization/hooks)

---

## Design

### Two stages of restraint: 90/10 and 80/20

These are design heuristics, not measured percentages or quotas:

1. **Before customizing, aim for 90/10:** let the product, native tools, repository tests, and clear requests do roughly 90% of the work. Own only the small amount of context/capability they lack. An 80/20 balance can fit unusual constraints; do not manufacture a custom 10% or 20%.
2. **When customization is justified, apply 80/20 reuse/tailoring:** reuse most of a suitable existing component and own only local differences. A 90/10 balance is even better when it fits. Installing nothing is better than installing irrelevant content.

Reuse does not mean adopting an entire collection. Verify scope, compatibility, license, permissions, and overlap before adoption.

### KISS and opportunity cost

Keep the simplest implementation that improves actual work. Do not try to reinvent AI, its harness, or generic engineering process. 

TODO: here reference to archive where the part is added about not doing current anymore.

### How much detail is enough

The built-in setup can already write code and understands basic language syntax. It may also apply familiar good practices, but it does not provide a complete, repository-specific engineering standard by default. Do not assume it will consistently choose your input-validation approach, error-handling policy, DRY and KISS trade-offs, or preferred language and tool patterns. This is the gap described in [why create AI customizations](#why-create-ai-customizations): knowing a technique is not the same as knowing when and how this project requires it.

Specify choices that change the result, not a basic language tutorial, such as:

| Detail | What to specify | Owning guidance |
|---|---|---|
| Engineering standards | Validate external input at boundaries, surface errors explicitly, reuse existing helpers (DRY), and prefer the simplest sufficient solution (KISS) | [Common instructions](common/README.md#package-contents) |
| Python patterns | Supported versions, typing and error-handling conventions, framework patterns, and exact lint/type-check/test commands | [Python package](python/README.md) and repository configuration |
| Docker builds | Layer caching: copy dependency manifests and install dependencies before copying frequently changing source; use the project's build and runtime stages | [Docker instructions](containerization/.apm/instructions/docker.instructions.md) |
| Helm input schemas | The required format and workflow: `@schema` annotations in values, constraints such as `enum` and `pattern`, and a generated, committed `values.schema.json` rather than hand-editing it | [Helm instructions](containerization/.apm/instructions/helm.instructions.md) |
| Local contracts | Compatibility limits, security boundaries, generated-file ownership, and the commands that prove the change works | Root `AGENTS.md`, owning documentation, and repository tooling |

Basic syntax, ordinary loops, or how to declare a function do not need repeating. Include version-specific syntax constraints or known model mistakes only when they affect this repository. Put short mandatory rules in scoped instructions and larger procedures or examples in skills; see [language and framework guidance](#language-and-framework-guidance). The common and opt-in stack packages supply these explicit standards, rather than relying on the built-in setup to infer them.

AI customizations are a means to an end. The goal is to build good, maintainable software, not to perfect the customizations. This work has no natural end: every language, framework, and tool can get another rule, reference, or example, and it is easy to spend more time tuning customizations than building the software they are meant to help with. Find the balance between three forces:

- **Usability:** enough guidance that agents follow the conventions and avoid known mistakes.
- **Maintainability:** every owned file must be kept current with its sources, tools, and models, so more files and more detail mean more maintenance.
- **Time:** time spent on customizations is time not spent building software.

The current setup is enough: the common package with the Orchestrator workflow and shared standards, plus one stack package per language or tool area, built from the [reference collections](#reference-collections). Do not go much further than that:

- **Do not over-perfect:** general guidance from good sources is enough. Do not rewrite copied content to make it perfect, add exhaustive rules, or anticipate every edge case.
- **Add specifics when encountered:** add a language, framework, or tool when a project actually uses it, and a rule when an agent got something wrong or a convention is missing. The [learning step](common/README.md#learning) records such lessons from real runs.
- **Source first, then tailor:** take new guidance from the reference collections or official documentation, copy it, and use AI to adapt it to the DevHub setup instead of writing it from scratch.
- **Stop at good enough:** when agents produce work that meets the standards with normal review, the customizations are done; spend the time on building instead.

### Why not install entire collections

Installing a whole collection, or depending on it wholesale, looks efficient but works against a reliable setup:

- **Simplicity:** collections are general-purpose and support many harnesses, languages, and workflows. That complexity is rarely needed, and every extra agent or skill competes for attention during discovery.
- **Noise:** unused agents, skills, and instructions add context, discovery conflicts, and maintenance without benefit.
- **Control and security:** a live dependency on a large community repository can change behavior, tools, or permissions on update. Selecting and pinning individual parts keeps every change reviewable.
- **Flexibility:** selected parts can be tailored to personal and team conventions without fighting upstream defaults.
- **Compatibility:** many collections target other harnesses, such as Claude Code or Cursor, whose assumptions do not map cleanly to Copilot.
- **Licensing and provenance:** selecting individual parts makes it clear which license and source applies to what.

### Reference collections

Inspect these before authoring anything. Ranked by fit for a Copilot-based setup; last checked November 2026, so rankings and contents may change:

| Rank | Collection | What it is |
|---|---|---|
| 1 | [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/main) | GitHub's community catalog of Copilot instructions, agents, skills, and plugins, including authoring guidelines for agents and skills. Copilot-native, so closest to this setup. |
| 2 | [anthropics/skills](https://github.com/anthropics/skills/tree/main) | Anthropic's public Agent Skills examples, from the authors of the skills format. |
| 3 | [affaan-m/ECC](https://github.com/affaan-m/ECC/tree/main) | Large multi-harness system with many specialist agents and language skills, such as Python, Go, and Java patterns and testing. |
| 4 | [obra/superpowers](https://github.com/obra/superpowers/tree/main) | Agentic skills framework and development methodology, such as planning, test-driven development, and debugging workflows. |
| 5 | [garrytan/gstack](https://github.com/garrytan/gstack) | An opinionated personal Claude Code setup with role-based tools; useful for ideas, less for direct reuse. |

Review each part's license, tools, harness assumptions, and behavior before adopting it.


---

## Customization types

Choose by the missing capability and activation scope, not the number of job titles a process could contain.

| Type | Purpose and activation | Use for | Avoid |
|---|---|---|---|
| Repository instructions (`AGENTS.md`, or supported equivalent) | Repository context discovered by the harness | Boundaries, consequential facts, commands, links to owning docs | Generic textbooks or duplicate shared rules |
| Scoped instructions (`*.instructions.md`) | Standing standards selected by `applyTo` and supported relevance rules | Short language/tool standards, validation commands, skill pointers | Loading every detailed reference for routine edits |
| Skill (`SKILL.md`) | On-demand request/procedure, selected by description or explicit invocation; may bundle assets | Reusable outcomes, specialized procedures, detailed references | Mandatory wrappers around all coding or planning |
| Prompt (`*.prompt.md`, legacy here) | Saved requests in supported Local sessions | Understanding/migrating older customizations | New Copilot workflows; use skills instead |
| Custom agent (`*.agent.md`) | A role/tool profile, optionally invoked in isolated subagent context | Deliberate tool control or focused responsibility | Reimplementing ordinary coding/planning/review loops |
| MCP server/connector | External systems exposed as tools | Needed GitHub, infrastructure, service, or database access | Speculative integrations and excessive privileges |
| Hook | Code at supported lifecycle events | A small targeted local guard/action | Expensive checks after every edit or hidden orchestration |
| Native tools, scripts, CI, permissions | Reproducible execution and enforceable controls | Tests, formatting, security checks, deployment gates | Trusting prose to enforce critical invariants |
| Package/plugin | Distribution of coherent components | Maintained shared context or a specific capability | Installing unrelated material because it is available |

### Choosing between nearby options

- **Instruction or skill:** a standing convention belongs in an instruction; a task procedure or longer reference belongs in a skill. Comments are a coding convention, not a separate skill.
- **Skill or prompt:** use skills for saved requests and procedures in this Copilot setup; do not maintain a duplicate legacy prompt.
- **Skill or agent:** a procedure does not inherently need another context. Use an agent when isolation or tool control adds value.
- **Domain instruction or agent:** Terraform rules belong in scoped guidance. A specialized language alone does not justify another agent.
- **Guidance or enforcement:** instructions guide decisions. Hooks can implement controls at supported events, but do not alone establish a complete security boundary. Use actual permissions, CI, and system boundaries for hard guarantees.

Descriptions are discovery surfaces; locations, patterns, and runtime support determine activation. A link does not automatically load its target. See the [official customization matrix](https://code.visualstudio.com/docs/agents/concepts/customization).

---

## How guidance is layered

### Anatomy: host, harness, runtime, and model

```text
You -> Copilot client (host and user interface; e.g. CLI or VS Code)
         |
         v
Copilot harness / SDK runtime (native Agent is the entry point)
  |  Context, conversation, tool loop, permissions, useful delegation
  |
  +-- Model selection: managed by the host/runtime
  |     No specific model or effort is required by DevHub
  |
  +-- Context layers
  |     Common APM: shared rules, optional skills and worker profiles
  |     Opt-in stacks: short scoped instructions -> skills -> references
  |     Repository AGENTS.md -> owning docs, commands, local constraints
  |     Current request: goal, scope, constraints, acceptance criteria
  |       (explicitly invoke /orchestrate for the delivery workflow)
  |
  +-- Tools: read/search/edit, terminal, web, configured MCP integrations
  |     Execution remains subject to host/runtime permissions
  |
  +-- Optional isolated subagents, only when useful
        Bounded scope, required context, acceptance criteria, stop condition
  |
  v
Changes + validation evidence -> diff / PR / CI -> review as warranted
```

The **host/client** presents editor/chat UI. The **harness** combines model calls, context, tools, permissions, and the agent loop. The **runtime** executes this system and its sessions (here through Copilot SDK/Agent Host). A **model** produces reasoning and tool requests; it is not the whole coding product. APM distributes configuration/context; it does not execute the loop or enforce permissions.

A custom agent defines a reusable role/tool profile; a **subagent** is an invocation in a separate context. Native Agent can delegate to built-in or custom workers. An **MCP server** exposes external capabilities as tools; **hooks** run code at supported lifecycle events. Merely mentioning an integration does not make it available.

Details: [agent harnesses](https://code.visualstudio.com/docs/agents/run/agent-harnesses), [Agent Host architecture](https://code.visualstudio.com/docs/agents/concepts/agent-host), [subagents](https://code.visualstudio.com/docs/agents/run/subagents), [Copilot Fusion](https://docs.github.com/en/copilot/concepts/models/copilot-fusion), and [Custom agents and sub-agent orchestration](https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/custom-agents).

### Context ownership and precedence

The diagram shows composition, not a universal precedence algorithm. Higher-priority platform rules and permissions still apply. In DevHub guidance, repository configuration/local constraints take precedence over shared defaults; language/tool rules refine general conventions. Surface unresolved conflicts.

- Personal cross-workspace preferences can live in the supported user profile.
- Shared conventions live in common; optional language/tool procedures live in the owning stack package.
- Repository facts and commands stay in root `AGENTS.md` or owning docs.
- Add nested `AGENTS.md` only for materially different subtree constraints a link cannot adequately express.
- A one-time requirement stays in the user request; do not automatically promote it to shared policy.

---

## Creating customizations

### The value gate

Before creating or expanding anything:

1. Identify an **observed recurring problem**, not a hypothetical improvement.
TODO: add here guidance on when to create customizations and when not to, etc.

| Situation | Decision |
|---|---|
TODO

### The 80/20 rule: reuse, then tailor

Search native capabilities, repository assets, and maintained sources before authoring.

| Fit | Approach |
|---|---|
| Existing product/tool solves it | Reuse without another customization |
| Component fits unchanged | Pinned dependency |
| Component needs local additions | Small scoped supplement |
| Useful content needs trimming/integration | Adapt, preserve attribution, record differences |
| No reusable source and benefit is clear | Smallest local component |
| Unique to one repository | Keep it there |

[awesome-copilot](https://github.com/github/awesome-copilot) and [ECC](https://github.com/affaan-m/ECC) are references, not installation checklists. Stars, pinning, and official provenance do not prove value, safety, or compliance.

TODO: add more explanation here

---

## Language and tool guidance

### Short entry points and on-demand references

Install common plus only stacks a repository uses: Python alone, containerization for Helm/Docker/Kubernetes, or IaC as needed. Unused packages contribute neither instruction files nor skill descriptions to that consumer.

Each stack has short file-scoped instructions with toolchain choices, mandatory rules, validation commands, and skill pointers. Skills supply patterns, gotchas, and focused `references/` files, opened only when relevant. This avoids including a large language reference on every matching edit while preserving its useful detail.

A Python testing task can open the testing reference without unrelated languages. Containerization groups related tools in one opt-in package; separate instruction scopes and skills distinguish Docker, Helm, and Kubernetes. Installation alone does not load every reference.

Skills depend on discovery and invocation; activation is not guaranteed. Explicit pointers in short instructions and fresh-session checks address that trade-off without forcing a large always-loaded file. Preserve existing reference substance rather than maintaining another tutorial.

### Framework scope

Dedicated FastAPI, Django, Spring Boot/JPA, and Ktor trees are absent. Models know ordinary framework use, and current shared usage does not justify another layer. Retained language/testing examples are illustrative, not adoption requirements.

Add framework guidance only when substantial project/team use needs a shared convention the model cannot infer. Keep one-off choices in the owning repository.

---

## Package design

[Common](common/README.md) supplies shared instructions and optional skills declared in its manifest. Stack packages add relevant language/tool guidance:

| Package | Adds |
|---|---|
| [Python](python/README.md) | Python instruction, skill, patterns/testing/tooling references |
| [Java](java/README.md) | Java/Kotlin instructions and skills, including coroutine guidance |
| [Go](go/README.md), [Rust](rust/README.md) | Language-specific instructions, skills, references |
| [Containerization](containerization/README.md) | Docker, Kubernetes, Helm instructions and skills |
| [IaC](iac/README.md) | Ansible, Terraform, Bicep instructions and skills |

```text
packages/apm/
  common/
    apm.yml, README.md, CHANGELOG.md
    .apm/instructions/common-*.instructions.md
    .apm/instructions/github-actions.instructions.md
    .apm/skills/draft-github-issue/SKILL.md
  <stack>/
    apm.yml, README.md, CHANGELOG.md
    .apm/instructions/<tool>.instructions.md
    .apm/skills/<tool>/SKILL.md
    .apm/skills/<tool>/references/
DevHub/.github/skills/orchestrate/SKILL.md  # repository-local; not an APM package
```

Selected upstream authoring instructions and optional skills are pinned dependencies in the [common manifest](common/apm.yml). Broad DevOps and prompt-engineering essays are not standing guidance. Comment standards live directly in [coding instructions](common/.apm/instructions/common-coding.instructions.md): comments explain why, not what, and should be concise.

Keep instruction sources flat: APM 0.35.0 scratch installation showed nested instructions could validate without deploying. Use `common-` filenames to distinguish shared guidance from same-named stack instructions.

Use portable upstream/source URLs for cross-package documentation links. APM 0.35.0 does not rewrite every relative cross-package link when moving instructions to the consumer's `.github/` directory; validate deployed links as well as source links.

Do not split every library into another package. Add project/domain or capability packages only when actual shared usage warrants them. Package selection controls installation; scopes and skills control use within that selection.

---

## Repository setup

Each consumer owns root `AGENTS.md`, manifest, lockfile, and deployment. A [parent workspace](../../docs/GETTING-STARTED.md#ai-customizations) is convenience, not a substitute.

DevHub's `/orchestrate` skill needs no APM setup: it is versioned directly at [`.github/skills/orchestrate/SKILL.md`](../../.github/skills/orchestrate/SKILL.md). Update it by editing that file; remove it by deleting that file. Then start a fresh Copilot session and verify explicit `/orchestrate` discovery and behavior. Do not infer discovery from the file's presence alone.

1. Preserve existing local guidance and consumer-owned customizations.
2. Declare common plus needed stacks, with an appropriate ref/lock policy:

   ```yaml
   name: personal-project
   version: 1.0.0
   target: copilot
   dependencies:
     apm:
       - CollinPoetoehena/DevHub/packages/apm/common#main
       - CollinPoetoehena/DevHub/packages/apm/python#main # only if used
   ```

3. Keep concise repository boundaries, commands, and owning-doc links in root `AGENTS.md`; do not duplicate shared standards.
4. With [APM installed](https://microsoft.github.io/apm/getting-started/installation/), run from the consumer root:

   ```sh
   apm install --only apm --target copilot
   ```

   Agents/instructions deploy under `.github/`; skills under `.agents/skills/`. Version intended deployment artifacts, manifest, and lock. Ignore caches such as `apm_modules/` and `.apm-local/`. Do not edit installed copies or force ownership/security collisions.
5. Start a fresh session in the intended harness. Verify relevant context, optional package skill discovery, and real validation. Installation, discovery, and good behavior are separate checks. In particular, APM package installation does not deploy DevHub's repository-local `/orchestrate` skill.

To stop consuming a package, remove its selector from `dependencies.apm` and run the install command to reconcile the manifest, lock, and deployment. Preview stale-package cleanup with `apm prune --dry-run`, then run `apm prune` to remove packages absent from the resolved dependency graph. This applies to APM-managed packages, not DevHub's native skill file.

---

## Usage

### Default setup

TODO

### Model choice and independent review

TODO

---

## Maintenance and validation

For APM-managed content, edit the owning package's `.apm/` sources, not deployed copies, and record package changes in its changelog and reuse registry. The native `/orchestrate` source is the tracked repository file `.github/skills/orchestrate/SKILL.md`, not an APM package. Retain only recurring, evidence-backed guidance worth future context/upkeep; no automatic policy edits after failures.

### Updating APM packages and the CLI

From a consumer root:

```sh
apm update --target copilot
```

For local APM source changes in DevHub, use `apm install --only apm --target copilot`. Review locks, deployments, and stale-file handling, then verify fresh-session activation. Updating the native `/orchestrate` skill requires editing the tracked `.github/skills/orchestrate/SKILL.md`; no APM update command applies to it. Upgrade the CLI through its documented installation method when needed. [Central sync](../../docs/github-actions/workflows/apm-sync.md) handles managed consumer updates through pull requests.

### Maintaining reused content

Preserve licenses and attribution. Each owning package records source commits/local adaptations:

1. Compare relevant upstream changes against the recorded commit; do not chase every revision.
2. Update the owning file, retaining useful substance/examples and the short-instruction/on-demand-reference boundary.
3. Inspect local conventions, compatibility, links, and contradictions between examples and normative rules.
4. Update provenance/changelog, run relevant checks, reinstall through APM.

For unchanged dependencies, update the pinned manifest ref and review deployment. Pinning prevents unexpected source drift; it does not prove usefulness or safety.

### Validation

From each affected package:

```sh
apm compile --validate --local-only
```

From a consumer root, verify deployment in a fresh scratch destination:

```sh
scratch=$(mktemp -d -t devhub-apm-check.XXXXXX)
apm install --only apm --target copilot --root "$scratch"
```

Check YAML, descriptions, instruction scopes, local links, reference preservation, and generated ownership. Verify selected stacks deploy and unselected stacks do not. Use focused fleet tests for generation rather than live fleet sync.

In a fresh target session, check native `/orchestrate` discovery and behavior, actual delegation controls where used, available tools, and repository guidance. Static frontmatter/install checks cannot prove discovery, enforcement, or good behavior. Report manual/runtime checks that remain unverified.

---

## References

- [VS Code customization overview](https://code.visualstudio.com/docs/agent-customization/overview) and [activation matrix](https://code.visualstudio.com/docs/agents/concepts/customization)
- [Agent harnesses](https://code.visualstudio.com/docs/agents/run/agent-harnesses) and [subagents](https://code.visualstudio.com/docs/agents/run/subagents)
- [Custom agents and sub-agent orchestration](https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/custom-agents)
- [Building custom agents](https://awesome-copilot.github.com/learning-hub/building-custom-agents/) and [agents and subagents](https://awesome-copilot.github.com/learning-hub/agents-and-subagents/)
- [Custom agents and subagents](https://docs.github.com/en/copilot/concepts/customizations/custom-agents#custom-agents-and-subagents) (GitHub Docs)
- [Creating effective skills](https://awesome-copilot.github.com/learning-hub/creating-effective-skills/)
- [Defining custom instructions](https://awesome-copilot.github.com/learning-hub/defining-custom-instructions/)
- [Before and after customization examples](https://awesome-copilot.github.com/learning-hub/before-after-customization-examples/)
- [Copilot configuration basics](https://awesome-copilot.github.com/learning-hub/copilot-configuration-basics/)
- [VS Code hooks](https://code.visualstudio.com/docs/agent-customization/hooks)
- [Anthropic: Building effective agents](https://www.anthropic.com/research/building-effective-agents), architectural guidance on starting simply and weighing complexity against cost
- [Copilot Fusion](https://docs.github.com/en/copilot/concepts/models/copilot-fusion) and [APM](https://microsoft.github.io/apm/)

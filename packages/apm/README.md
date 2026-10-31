# DevHub Agent Package Manager (APM) Packages

[APM](https://microsoft.github.io/apm/) distributes shared AI customizations to supported agent harnesses. DevHub uses it for a common baseline across personal projects, with repository-specific guidance in a root `AGENTS.md`. The harness loads the resulting context; APM does not execute the agent or guarantee compliance.

This guide owns personal AI usage principles and the shared concepts, setup, authoring, usage, maintenance, and validation of AI customizations. Package READMEs, such as [common](common/README.md) and [homelab](homelab/README.md), describe only their contents, dependencies, and package-specific decisions. [Using DevHub](../../docs/USAGE.md) owns shared-workspace arrangements.

---

## Table of Contents

- [Why customize AI](#why-customize-ai)
  - [Reuse before authoring](#reuse-before-authoring)
- [Design and ownership](#design-and-ownership)
  - [Choose the right customization](#choose-the-right-customization)
  - [How guidance is layered](#how-guidance-is-layered)
  - [Nested instructions](#nested-instructions)
- [Repository setup](#repository-setup)
  - [Verify activation](#verify-activation)
- [Authoring repository guidance](#authoring-repository-guidance)
  - [Consumer-specific guidance](#consumer-specific-guidance)
  - [Use the setup skill](#use-the-setup-skill)
- [AI usage](#ai-usage)
  - [Personal usage: stay the expert](#personal-usage-stay-the-expert)
  - [Prompt engineering](#prompt-engineering)
  - [The DRIVE method](#the-drive-method)
- [Working with agents](#working-with-agents)
  - [Recommended Chat setup](#recommended-chat-setup)
  - [Choosing an agent](#choosing-an-agent)
  - [Planning before implementation](#planning-before-implementation)
  - [Model selection](#model-selection)
- [Maintenance and validation](#maintenance-and-validation)
  - [Ongoing maintenance](#ongoing-maintenance)
  - [Updating APM packages and the CLI](#updating-apm-packages-and-the-cli)
  - [Validation](#validation)
- [DevHub's own setup](#devhubs-own-setup)
- [References](#references)
  - [Customization and distribution](#customization-and-distribution)
  - [Agent execution and model selection](#agent-execution-and-model-selection)
  - [Prompt engineering and AI background](#prompt-engineering-and-ai-background)

---

## Why customize AI

Default agents are useful for focused tasks, but cannot be expected to know a repository's recurring conventions, architecture, or validation workflow without that context. Instructions make stable expectations available; agents define roles; skills provide focused procedures; prompts express reusable requests. Customizations complement the default agent rather than replace it or guarantee a particular result.

Maintain shared expectations centrally and local context with its owner. This avoids repeatedly explaining the same standards or copying them across projects. Keep the context small and relevant: overlapping instructions add maintenance, stale facts, and potential conflicts.

### Reuse before authoring

Inspect existing package and host capabilities before creating another customization. Reuse suitable official or community resources for needs they already cover; extend local guidance only for a remaining DevHub-specific gap.

Review scope, license, prerequisites, source trust, and compatibility before declaring dependencies. Prefer selected primitives and reviewed references over importing entire collections. Host-provided capabilities may be sufficient without another package dependency.

Reused procedures supplement existing rules; they do not grant commit/push permission, bypass approvals, or justify unrelated tooling. See the [reference collections](#customization-and-distribution) for discovery and each package README for its selected dependencies.

---

## Design and ownership

```text
Shared APM packages -- APM install --> Harness-supported customizations
  common baseline                                   |
  optional domain guidance                          |
  reusable agents and skills                        v
                                            discovered task context
                                                    ^
Repository root AGENTS.md -- harness discovery ------+
  links to owning READMEs
  essential local constraints
```

| Layer | Owner and responsibility |
|---|---|
| [Common package](common/README.md) | Shared engineering, testing, and documentation standards; scoped technology/tool instructions; reusable agents and skills. Declare it in every personal project's manifest. |
| Optional domain package | Context genuinely shared by several related repositories. The [homelab package](homelab/) is an existing placeholder; add domain packages only for concrete reuse, not a speculative hierarchy. |
| Root `AGENTS.md` | The repository's agent-facing entry point: links to authoritative project documentation and essential local constraints. |
| Owning README or focused documentation | Human-facing purpose, architecture, component contracts, commands, and decisions. These remain authoritative rather than being copied into AI instructions. |
| Current request | The task, scope, and acceptance criteria; temporary requirements do not become permanent instructions automatically. |

This is composition, not a universal inheritance or override mechanism. Avoid contradictory guidance and surface conflicts. Shared rules belong in the common package, domain rules in the relevant domain package, and repository-only knowledge with its repository.

The same pattern scales to a team or organization: a common baseline plus selected team/domain packages and local repository guidance. More packages or instruction layers are justified by actual ownership and reuse, not organization size alone.

### Choose the right customization

The customization types answer different questions:

| Part | Responsibility | Typical content |
|---|---|---|
| Agent | **Who** performs the work | Role, responsibilities, workflow, boundaries, and expected output |
| Instruction | **Rules and context** for the work | Engineering standards, technology constraints, and repository conventions |
| Skill | **How** to perform a repeatable procedure | Steps, references, scripts, and task resources |
| Prompt | **What** reusable task to request | A user-invoked template with specific inputs |
| User request | **What** needs to be done now | Current scope and acceptance criteria |

| Need | Default |
|---|---|
| Persistent repository context | One root `AGENTS.md`, usable across harnesses that support it |
| Cross-cutting file/type constraints | Scoped instruction files, such as the common package's `*.instructions.md` with `applyTo` globs for Copilot |
| Distinct role, workflow, or capabilities | Reuse a common agent; author another only for a real gap |
| Repeatable specialized procedure | A skill, shared through APM or owned locally when project-specific |
| Reusable user-invoked request | A prompt |
| Personal preferences | Optional user-level configuration supported by the harness, not a substitute for repository setup |

Do not create both a root `AGENTS.md` and a repository-wide `copilot-instructions.md` merely because both formats exist. Add a harness-specific adapter only when required by a supported surface, keeping one authoritative source rather than independently maintained copies.

`AGENTS.md` is cross-agent, not universal. Custom agents, scoped instructions, skill locations, and discovery rules vary by harness. Verify the intended environment using the [official references](#references), rather than assuming that a Copilot installation serves every AI tool.

### How guidance is layered

```text
User request: scope and acceptance criteria
    |
    v
Entry point: Orchestrator (recommended), a specialist, or default agent
    |
    +-- Role definition (agent): responsibilities, boundaries, and workflow
    +-- Common instructions: engineering, testing, and documentation standards
    +-- Matching technology/tool instructions: shared packages and/or consumer
    +-- Root AGENTS.md: local constraints and routes to owning documentation
    |       |
    |       +--> Relevant README, architecture, component docs, scripts, or CI
    |
    +-- Relevant skills: focused procedures loaded when needed
    |
    v
Implementation / documentation / review, with validation and evidence
```

The diagram shows context composition, not precedence or a promise that every linked file loads automatically. The selected agent contributes role responsibilities and workflow, not a separate copy of every engineering rule. Repository links route it to the authoritative context needed for the task; read the relevant owner rather than loading every document.

Keep common standards in one shared instruction source rather than dispersing them among role definitions. Explicit references from agents and repository guidance help locate that source even when a task does not edit matching files. Scoped instructions add only the relevant constraints; their discovery and attachment remain harness-dependent.

For example, Coder and Reviewer both need the engineering baseline: keeping coding standards only in Coder would leave review and other roles without the same quality bar. Keep shared engineering, testing, and documentation expectations coherent in the common baseline, while scoped instructions supply specialized constraints. The common package's [design and execution flow](common/README.md#design) explains how its roles use this context.

### Nested instructions

Start with one root `AGENTS.md` and links to component READMEs. A nested file is exceptional and justified only when:

1. A component has materially different, consequential agent constraints or validation.
2. Including that guidance in the root would burden unrelated tasks.
3. A root link to the component's owning documentation does not adequately cover the need.

A different language, large folder, or separate package alone is insufficient. Record the reason in the owning documentation and verify nested discovery in the chosen harness. Do not rely on a universal "nearest file wins" rule.

---

## Repository setup

1. Inspect existing manifests, instructions, skills, documentation, and local changes. Preserve useful repository guidance and user-authored customizations; do not blindly replace an existing setup.
2. Declare the common dependency in the repository's `apm.yml`. For a new consumer, adapt this example to the repository's identity and reviewed dependency-reference conventions:

   ```yaml
   name: personal-project
   version: 1.0.0
   targets:
     - copilot
   dependencies:
     apm:
       - CollinPoetoehena/DevHub/packages/apm/common
   ```

   Preserve existing manifest settings. Add domain packages only when relevant; do not create copies of their source directories in consumers. Use reviewed references and the lockfile for reproducible dependency resolution.
3. Author one root `AGENTS.md` using the [guidance below](#authoring-repository-guidance). Keep shared rules in the package rather than copying them into the repository.
4. With [APM installed](https://microsoft.github.io/apm/getting-started/installation/), run from the consumer repository root for Copilot:

   ```sh
   apm install --only apm --target copilot
   ```

   For this target, installed agents and instructions are under `.github/`, and skills under `.agents/skills/`. Those package-installed files are deployment artifacts, not another authoring source. Keep local customizations distinct from package-owned paths and review collisions before accepting replacements. Resolve dependency or policy failures before treating setup as complete; do not bypass policy or force replacements to make a check succeed.
   Keep `apm_modules/` and `.apm-local/` ignored: they hold restored dependencies and local installation state. Version `apm.yml`, `apm.lock.yaml`, and reviewed target-owned customizations, including installed agents, instructions, and skills; do not blanket-ignore `.github/`, `.agents/`, or authored `.apm/` package sources. See APM's [what to commit](https://microsoft.github.io/apm/quickstart/#3-install-a-package).
5. Verify activation as described below. Keep a repository-level setup even when a parent-workspace install is used for convenience; verify standalone repository use separately.

Copilot natively reads installed instruction files, so root-context compilation is not needed for this setup. Other targets may require native adapters or `apm compile`; consult the target matrix and compile reference before selecting them. Compilation can write root context files, including `AGENTS.md`: inspect planned output in isolation and establish ownership before writing to a repository with an authored file. Do not overwrite local guidance to make shared instructions available.

### Verify activation

A manifest, successful installation, and instruction compliance are three different checks:

- **Static setup:** verify manifest and skill metadata, relative links, file scopes, and the absence of conflicting or duplicate guidance using the [validation procedure](#validation).
- **Deployment:** confirm that the intended target received the common instructions, scoped instructions, agents, and skills. Merely checking out the package does not activate it.
- **Host discovery:** in the selected harness, confirm the root repository guidance and installed customizations are discoverable. Refresh or start a new session after changes.
- **Behavior:** exercise a small task with an observable criterion that depends on a local convention. Inspect references or debug evidence where supported, plus the actual result and validation activity. Check one relevant scoped instruction and, when used, the setup skill.

For VS Code's Local harness, root `AGENTS.md` discovery is controlled by `chat.useAgentsMdFile` (enabled by default); nested discovery additionally requires `chat.useNestedAgentsMdFiles` (disabled by default). These settings do not control other harnesses. Shared-parent and multi-root discovery also need separate verification; see [workspace setup](../../docs/USAGE.md#personal-project-workspace).

Instructions guide behavior. Tests, CI, access controls, and approvals remain the mechanisms for verifying or enforcing requirements. Report missing discovery or unverified behavior explicitly; do not treat installation as proof of compliance.

---

## Authoring repository guidance

Always create a root `AGENTS.md` for a DevHub project, aiming for that one file. It gives compatible agents a stable entry point from which to find the relevant context. Read existing documentation and configuration first. Every instruction should supply useful agent context that is otherwise missing, or direct the agent to its authoritative source:

- Link to the root README for purpose and scope, and to architecture or guidelines for placement and decisions.
- Link to area READMEs for component details. Tell the agent to read the relevant owner, not every linked document for every task.
- Keep architecture, user-facing setup, and detailed procedures in their existing documentation. If needed information is missing, improve that owning document and link it rather than creating a parallel AI explanation.
- Include only essential agent-specific local constraints inline: unusual naming/style conventions, compatibility boundaries, sensitive operations, generated-source ownership, or a validation requirement the agent could otherwise miss.
- Do not repeat common engineering standards or facts already maintained in native metadata, scripts, or CI. Point to those sources for versions and commands instead of freezing a second copy.
- Preserve compatible existing instructions during migration. Remove duplicates only within the authorized scope, update their callers, and surface conflicts rather than inventing precedence.

Explicit Markdown links are also a discovery strategy: pair each link with a short direction about when to read it. For example, route package changes to the package README and boundary changes to the architecture guide. This steers an agent's next reads and searches instead of relying solely on automatic relevance discovery, which may miss important files. Links do not automatically load every target or guarantee that it is followed; retain the [activation and behavior checks](#verify-activation).

Keep links resolvable in the intended checkout. Use relative links for repository-owned files, and stable public source links for shared external guidance when sibling checkouts are optional. Do not put private paths, inventories, or operational values in public instructions.

Use concise Markdown and relative links. A root `AGENTS.md` does not need skill-style YAML frontmatter. Include only sections that serve the repository; for example:

```markdown
# Repository Agent Guidance

Read [README.md](README.md) for purpose and scope.
Follow the installed common baseline; see the repository's AI setup guide.

## Find the owning context

- Read the affected area's README for contracts and validation.
- Consult the architecture guide before changing component boundaries.

## Local constraints

- Record only consequential repository-specific agent guidance here.
```

The example is a structure, not content to copy unchanged. Replace generic directions with verified links and useful constraints from the actual repository.

### Consumer-specific guidance

Reuse common roles and add local constraints outside installed package-owned files:

```text
consumer/
  apm.yml
  AGENTS.md
  .github/instructions/
    service-api.instructions.md        # only when path targeting adds value
  .agents/skills/
    deploy-service/SKILL.md             # only for a project-specific procedure
```

For Copilot, a scoped instruction can target a service boundary without duplicating the root entry point:

```yaml
---
description: "Use when changing the service API."
applyTo: "src/api/**,tests/api/**"
---
```

Keep deployment environment, SDK, registry, and domain decisions in their owning documentation, with necessary agent-specific constraints linked or scoped locally. Select a shared domain package only when several repositories need that context. Neither a local file nor a selected package is an automatic override.

### Use the setup skill

The common package's [setup-ai-customizations skill](common/.apm/skills/setup-ai-customizations/SKILL.md) inspects and creates or updates this setup without duplicating project documentation. After installing the updated package, request:

```text
Use setup-ai-customizations to configure this repository for Copilot.
Reuse its existing documentation, preserve local customizations, and verify
the common APM baseline and root AGENTS.md.
```

For discussion only, explicitly request a proposal without edits or installation. The skill's package-documentation resolution and validation procedure account for the different source and installed layouts.

---

## AI usage

### Personal usage: stay the expert

Use AI as a colleague or assistant that amplifies my capabilities, not as a replacement for my thinking. These are personal reminders, not an exhaustive guide:

- **Stay the expert.** Understand and verify generated work, challenge assumptions, and reason independently or alongside AI. AI can make mistakes; responsibility for quality and final decisions stays with me.
- **Engineering judgment remains the differentiator.** Producing code is only part of engineering. Architecture, domain understanding, boundaries, technology trade-offs, priorities, scalability, maintainability, and testing, rollout, and operational risks require judgment. AI can explore options and expose blind spots; I must decide what fits the actual problem and own the consequences.
- **Maintain core skills.** Keep practicing writing, communication, coding, debugging, and problem-solving. Small tasks may be faster to do myself and provide useful practice; combine my own reasoning with AI feedback and implementation help where it adds value. Avoid dependence that weakens understanding or confidence without AI.
- **Use AI strategically, not maximally.** Brainstorming, research, explanations, reviews, code/tests, automation, and documentation can benefit. Complex, unfamiliar, or high-impact work especially benefits from exploring alternatives and challenging assumptions, while decision-making stays human. Optimize for speed, quality, learning, and insight, not the amount of AI used.
- **Keep context and sources trustworthy.** Start a fresh chat for a new task or stale context. Check claims against official documentation, actual code, tests, and logs rather than treating fluent answers as evidence. Use approved tools for work and do not share secrets or restricted information; a paid subscription alone does not establish safety.
- **The future of Software Engineering.** Less focus on manual typing, more on architecture, strategy, domain logic, and system thinking — engineers shift toward being architects, designers, analysts, reviewers, with value moving from writing code to problem-solving and engineering judgement.

> **Personal Conclusion:** AI is a game changer for Software Engineers and in general life — but only if used wisely. Use it as a powerful assistant that enhances your capabilities, accelerates learning, and improves the speed and quality of your work, while you remain the expert responsible for the thinking, decision-making, architecture, and problem-solving. The most effective engineers use AI to amplify their expertise, not replace it.

### Prompt engineering

Prompt engineering means shaping input to get more accurate, useful output:

- **Context first; scale planning to the task.** Give the goal, relevant code, project structure, documentation, constraints (including language/framework versions), and acceptance criteria. For complex or multi-part work, start a focused new chat, let AI analyze that context and propose a plan, then execute small steps using the agreed context and plan. For example, plan testing across the repository before implementing tests per domain/package; follow the [testing and validation standards](common/.apm/instructions/common.instructions.md#testing-and-validation). For one isolated test, function, or formatting fix, ask directly: unnecessary planning adds latency and token cost.
- **Show the target.** Supply examples of desired input/output or existing code/style to match; specify output format, length, and tone when needed.
- **Set boundaries.** State exclusions such as no unrelated edits or new dependencies. Assign a role when a particular review perspective helps.
- **Iterate and challenge.** Treat the first result as a draft, refine it with feedback, and request assumptions, trade-offs, and a concise explanation for difficult problems. An explanation is not proof of correctness.
- **Reuse what works.** Save recurring requests and procedures through the appropriate [customization type](#choose-the-right-customization), rather than rewriting or duplicating guidance.

See the official [OpenAI](https://developers.openai.com/api/docs/guides/prompt-engineering), [Gemini](https://ai.google.dev/gemini-api/docs/prompting-strategies), and [IBM](https://www.ibm.com/think/topics/prompt-engineering) guides for more detail.

### The DRIVE method

[DRIVE](https://www.robertpeake.com/ai/drive) (Robert Peake) is a five-step discipline for working with AI. AI makes producing work cheap, so the hard parts move to both ends: *judgment* at the front (what is worth doing, and to what standard) and *verification* at the back (whether the result is actually right). The middle can go to the machine; trust my practice, not the model.

```text
Decide --> Request --> Iterate --> Validate --> done --> Evolve
              ^                        |
              +------- not yet --------+
```

- **D - Decide:** define what "done" means and the standard, in one sentence, before any request. It keeps the task mine and tells the loop when to stop; without it, work is unbounded.
- **R - Request:** brief intent, context, constraints, success criteria, and assumptions; agree the plan first. Unstated assumptions are the usual cause of fluent but wrong results.
- **I - Iterate (can also be called Isolate):** read output as it takes shape and steer it; correct small errors early and test each suggestion against "done". Limit parallel agents to what I can still oversee. In other words, break down complex tasks into manageable parts and handle them sequentially to maintain control and accuracy.
- **V - Validate:** check the result against the criteria from Decide using evidence (tests, real figures, a second source), sized to the stakes. A confident tone is not evidence.
- **E - Evolve:** after the work, debrief and promote lessons into reusable context: standards, references, templates, or instructions (see [ongoing maintenance](#ongoing-maintenance)). Prune stale rules, and check whether I could redo the work without AI.

Decide frames the loop; Request, Iterate, and Validate repeat until "done" is met; Evolve improves what the next task starts from.

---

## Working with agents

Orchestration can coordinate analysis, implementation, validation, documentation, review, and corrections for larger tasks. Bounded specialist assignments provide focused context, clear ownership, and another opportunity to detect assumptions or coverage gaps. Parallelize genuinely independent work, not shared-file edits or dependent stages.

This can reduce repeated user-driven handoffs and make a consolidated result easier to review. It also adds coordination, model usage, and elapsed time, and does not guarantee an unbiased or defect-free result. Scale the workflow to the task: simple work should remain direct; substantial or high-risk work may warrant specialists and independent review.

Keep implementation and its tests with one owner; use review to assess correctness and test adequacy rather than making routine testing a separate handoff. Package READMEs describe the actual roles and restrictions they provide.

### Recommended Chat setup

For autonomous work in a trusted DevHub workspace:

1. In VS Code Chat, select **Copilot** as the session target, independently of the model and selected agent.
2. Select the common **Orchestrator**, a specialist, or the built-in **Agent** as appropriate. **Autopilot** lets work continue with fewer prompts where supported; it is an agent mode, not a replacement for the selected role.
3. Where policy permits and the risk is acceptable, the DevHub convenience setup turns terminal sandboxing off for trusted local tooling. This is optional, not a package requirement or a general fix for shell configuration errors.

Autopilot auto-approves tools; disabling terminal sandboxing removes its filesystem and network restrictions. Use this combination only with trusted content and actions you accept running with your account's access. Keep sandboxing enabled and use manual permissions otherwise. These controls are independent and never supersede organization policy; see the [execution references](#agent-execution-and-model-selection).

### Choosing an agent

The common Orchestrator is the recommended entry point for end-to-end tasks and handles simple work directly. Specialists or the default agent remain supported for focused work. Use custom roles only when their boundaries or workflow add value; do not invoke every role merely because it is available.

Delegation depends on the harness and configured tools/allowlists. Discovery descriptions do not grant tool capabilities, and role instructions are not a security sandbox. Verify support and ensure each assignment includes relevant common/project guidance, constraints, and acceptance criteria.

### Planning before implementation

For large or uncertain work, request a plan before edits:

```text
Analyze this request and propose an implementation plan. Do not edit files
or install anything. Identify dependencies, risks, and validation criteria.
Wait for approval before implementation.
```

For well-scoped work, request implementation directly. Review the final changes and evidence even when the workflow proceeds autonomously.

### Model selection

Prefer Auto where offered, choosing an explicit model when results or cost warrant it. Let the active harness handle routing rather than maintaining another package-level routing system.

Auto and Copilot Fusion expose different cost, quality, and effort controls depending on the surface and account. Model settings in a custom agent and subagent routing also depend on the host. Consult the official references for current availability and pricing; do not assume that all workers use the same model or receive the same discount.

---

## Maintenance and validation

### Ongoing maintenance

Maintain package sources under `.apm/`, not installed deployment copies. Keep package READMEs limited to contents, dependencies, and package-specific decisions; update this guide for shared design or procedures, and the owning project docs for local knowledge.

Review customizations when experience reveals a recurring gap or the supported workflow changes. Retain only reusable, evidence-backed lessons; update the appropriate source and its changelog where maintained. Report proposals when that owner cannot be edited. This is explicit documentation maintenance, not persistent model training or automatic self-modification.

Refresh consumer installations deliberately after source/dependency changes and review collisions first. Source edits do not refresh a running session or already installed agent. If behavior appears stale, compare source and deployed definitions before reinstalling, then start a fresh chat and verify behavior.

### Updating APM packages and the CLI

Run dependency updates from the consumer repository root. Inspect local changes first, then preview the plan without writing files:

```sh
apm update --target copilot --dry-run
```

Review the proposed additions, updates, removals, and source references. When acceptable, run the interactive update and confirm its plan:

```sh
apm update --target copilot
```

To update only the common package, select its dependency instead of updating everything:

```sh
apm update CollinPoetoehena/DevHub/packages/apm/common --target copilot
```

APM refreshes dependencies and deploys their supported customizations; a separate install is not normally needed after an update. Review resulting manifest, lockfile, and deployed-file changes, resolve policy or collision warnings, then start a fresh chat and repeat the [activation checks](#verify-activation). Do not use `--force` to discard authored customizations.

An update is not a reinstall of locked content: it can change dependency references, including full-SHA pins. Current APM documentation describes resolving an upstream annotated semantic-version tag and rewriting such pins after consent. Inspect the plan carefully; if you require a particular reviewed revision, choose it explicitly in the manifest rather than assuming an update preserves it. Use `apm install --only apm --target copilot --frozen` when restoring an existing, valid lockfile without upgrading references.

For local dependencies, such as DevHub's `./packages/apm/common`, edit and validate the source package, then run `apm install --only apm --target copilot` from the consumer root to refresh its deployment. This does not publish the package or upgrade remote consumers.

`apm update` updates packages, not the APM CLI. Upgrade the CLI using the method that installed it—for example, `brew upgrade apm` for Homebrew, or `apm self-update` for supported standalone installations. See the official [update](https://microsoft.github.io/apm/reference/cli/update/) and [self-update](https://microsoft.github.io/apm/reference/cli/self-update/) references for current options.

### Validation

From the affected APM package directory, validate local primitives without installing over workspace customizations:

```sh
apm compile --validate --local-only
```

This checks agents and instructions; separately validate skills' required metadata, directory/name agreement, description triggers, and resource links. Check instruction frontmatter/scopes, documentation links and headings, source ownership, and consumer references. Run relevant existing checks; documentation-only edits do not justify new test scaffolding.

When deployment validation is needed, use an explicitly resolved scratch directory with the supported `--root` option from the consumer root:

```sh
scratch=$(mktemp -d -t devhub-apm-check.XXXXXX) &&
apm install --only apm --target copilot --root "$scratch"
```

Use a fresh task-specific location, not an existing workspace or another user's directory. Resolve policy/dependency warnings and inspect output before claiming success; do not bypass policy or force replacement. Clean up only the specific scratch files you created. See the [APM command references](#customization-and-distribution) for other targets and options.

Static validation and isolated deployment do not establish host discovery or compliance. Complete the [activation checks](#verify-activation) with a representative task, relevant scoped guidance, and a failure/edge case where feasible. Distinguish passed, failed, skipped, and blocked checks in the report.

---

## DevHub's own setup

DevHub consumes the common package through its [root manifest](../../apm.yml), using a local dependency for development. Sources are maintained under each package's `.apm/` directories; installation does not synchronize later source edits automatically.

The [root AGENTS.md](../../AGENTS.md) links to the [repository overview](../../README.md), [packages](../README.md), [tools](../../tools/README.md), and focused project documentation. That navigation covers the current components, so **DevHub needs no nested `AGENTS.md` files** and maintains no duplicate repository-wide Copilot instruction file. Reconsider only when a demonstrated gap meets the [nested instruction criteria](#nested-instructions).

---

## References

This guide records DevHub's choices and essential concepts. Use these official sources for full theory, supported formats, commands, and current harness behavior:

### Customization and distribution

- [APM overview](https://microsoft.github.io/apm/): dependency management and the distinction between distribution and runtime.
- [APM primitive authoring](https://microsoft.github.io/apm/producer/author-primitives/): instructions, agents, skills, prompts, and package structure.
- [APM consumer guide](https://microsoft.github.io/apm/consumer/): installation, dependencies, and reproducibility.
- [APM targets matrix](https://microsoft.github.io/apm/reference/targets-matrix/): supported primitives, deployment locations, and target-specific limitations.
- [APM compile reference](https://microsoft.github.io/apm/reference/cli/compile/): root-context generation, options, and output ownership considerations.
- [AGENTS.md](https://agents.md/): the cross-agent repository instruction convention.
- [VS Code customization overview](https://code.visualstudio.com/docs/agent-customization/overview): customization types and harness selection.
- [VS Code custom instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions): file formats, scopes, discovery settings, and verification.
- [Copilot CLI custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions): discovery and combined instruction sources.
- [Agent Skills specification](https://agentskills.io/specification): skill metadata and packaging.
- [VS Code agent skills](https://code.visualstudio.com/docs/agent-customization/agent-skills) and [custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents): activation and role configuration.
- [APM install reference](https://microsoft.github.io/apm/reference/cli/install/): deployment options and scratch-root validation.
- [APM update reference](https://microsoft.github.io/apm/reference/cli/update/) and [CLI self-update](https://microsoft.github.io/apm/reference/cli/self-update/): dependency refresh, pin handling, and upgrading the tool itself.
- [GitHub awesome-copilot](https://github.com/github/awesome-copilot), [Microsoft skills](https://github.com/microsoft/skills), and [Anthropic skills](https://github.com/anthropics/skills): collections to inspect before authoring another primitive.

### Agent execution and model selection

- [VS Code Chat](https://code.visualstudio.com/docs/agents/run/chat-view) and [agent harnesses](https://code.visualstudio.com/docs/agents/run/agent-harnesses): session targets and role selection.
- [Subagents](https://code.visualstudio.com/docs/agents/run/subagents) and [custom-agent file reference](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference): delegation, tools, and allowlists.
- [Approvals and permissions](https://code.visualstudio.com/docs/agents/run/approvals), [terminal sandboxing](https://code.visualstudio.com/docs/agents/run/agent-sandboxing), and [trust and safety](https://code.visualstudio.com/docs/agents/concepts/trust-and-safety): autonomous execution and security boundaries.
- [Auto model selection](https://docs.github.com/en/copilot/concepts/models/auto-model-selection), [Copilot Fusion](https://docs.github.com/en/copilot/concepts/models/copilot-fusion), and [model comparison](https://docs.github.com/en/copilot/reference/ai-models/model-comparison): current routing, controls, availability, and pricing.

### Prompt engineering and AI background

- [OpenAI prompt engineering](https://developers.openai.com/api/docs/guides/prompt-engineering?api-mode=responses): practical prompting guidance.
- [Gemini prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies): provider-specific techniques.
- [IBM prompt engineering](https://www.ibm.com/think/topics/prompt-engineering): prompting concepts and techniques.
- [The DRIVE method](https://www.robertpeake.com/ai/drive): a five-step discipline for working with AI (Decide, Request, Iterate, Validate, Evolve).
- [IBM: What are AI agents?](https://www.ibm.com/think/topics/ai-agents): background on agent concepts and architectures.
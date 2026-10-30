# DevHub Common Agent Package

`devhub-common` is an [Agent Package Manager (APM)](https://microsoft.github.io/apm/) package of reusable engineering agents, shared instructions, and skills. The Orchestrator is the recommended entry point for complete tasks; specialists and the default Copilot Agent can also be used directly.

This package provides reusable team standards and workflows so agents can tailor their work to DevHub conventions instead of relying only on generic defaults. That investment pays off across projects: common expectations are maintained centrally, while each consumer can add its own architecture, tooling, and domain rules.

DevHub's human-facing repository and package conventions are in the [shared guidelines](../../../docs/GUIDELINES.md); this package owns reusable AI guidance.

## Table of Contents

- [AI customizations: concepts and layering](#ai-customizations-concepts-and-layering)
  - [Why create customizations and agents?](#why-create-customizations-and-agents)
  - [Reuse before authoring](#reuse-before-authoring)
  - [How guidance is layered](#how-guidance-is-layered)
- [Usage](#usage)
  - [Installation](#installation)
  - [Recommended Chat setup](#recommended-chat-setup)
  - [Choosing an agent](#choosing-an-agent)
  - [Planning before implementation](#planning-before-implementation)
  - [Consumer-specific guidance](#consumer-specific-guidance)
- [Design](#design)
  - [Why orchestrate](#why-orchestrate)
  - [Focused roles and testing ownership](#focused-roles-and-testing-ownership)
  - [Self-learning and maintenance feedback](#self-learning-and-maintenance-feedback)
  - [Model selection](#model-selection)
  - [Harness support](#harness-support)
  - [Package contents](#package-contents)
    - [Agents](#agents)
    - [Instructions](#instructions)
    - [Skills and prompts](#skills-and-prompts)
- [Maintenance and validation](#maintenance-and-validation)
  - [Ongoing maintenance](#ongoing-maintenance)
  - [Validation](#validation)
- [References](#references)
  - [Prompt engineering](#prompt-engineering)
  - [AI concepts](#ai-concepts)

---

## AI customizations: concepts and layering

[VS Code customization concepts](https://code.visualstudio.com/docs/agents/concepts/customization) and [APM primitives](https://microsoft.github.io/apm/producer/author-primitives/) describe how these pieces complement one another:

| Part | Responsibility | Typical content |
|---|---|---|
| Agent | **Who** performs the work | Role, responsibility, workflow, boundaries, and expected output |
| Instruction | **Rules and context** for the work | Shared engineering standards, technology/tool constraints, or repository conventions |
| Skill | **How** to perform a repeatable, specialized procedure | Steps, references, scripts, examples, and other task resources |
| Prompt | **What** reusable task to request | A user-invoked task template with specific inputs |
| User request | **What** needs to be done now | The current task and its acceptance criteria |

### Why create customizations and agents?

Copilot's default agent is designed to be useful across many projects and tasks, so it is a good choice for focused work and remains available alongside these customizations. It cannot be expected to know a team's recurring conventions, architecture, validation commands, or preferred workflows unless that context is provided.

Custom instructions make stable, recurring expectations available without asking users to restate them in every request. Custom agents are useful when work benefits from a distinct role, bounded responsibilities, a repeatable workflow, or a specific expected output. They make those expectations easier to discover and reuse; they do not replace the default agent or guarantee a particular result.

This package provides a maintained baseline that can be shared across repositories. Consumer projects add their own local context rather than copying the shared rules. Keep customizations focused and current: duplicating or overloading them adds noise, and maintaining overlapping copies can cause stale or conflicting guidance. Use the default agent when a custom role adds no clear value.

### Reuse before authoring

Create DevHub-owned customizations only for specific needs that existing capabilities do not adequately cover: the core [Orchestrator workflow](.apm/agents/orchestrator.agent.md), specialist boundaries, shared team standards, and project-specific procedures. For other tasks, reuse suitable official or community skills, instructions, prompts, and agents rather than reinventing them (saves time and maintenance effort). Check sources such as [GitHub's awesome-copilot community collection](https://github.com/github/awesome-copilot), [Microsoft's skills](https://github.com/microsoft/skills), and [Anthropic's skills](https://github.com/anthropics/skills) before authoring a new customization.

The [package manifest](apm.yml) selects two focused community skills rather than importing an entire collection:

| Dependency | Purpose |
|---|---|
| [git-commit](https://github.com/github/awesome-copilot/tree/5269f7ea2d6c3a9bfda5ed878b6726cf509121fd/skills/git-commit) | Inspect changes and create Conventional Commits when explicitly requested. |
| [webapp-testing](https://github.com/github/awesome-copilot/tree/5269f7ea2d6c3a9bfda5ed878b6726cf509121fd/skills/webapp-testing) | Test and debug local web interfaces with Playwright. |

APM supports these skill directories as [virtual package dependencies](https://microsoft.github.io/apm/consumer/install-packages/); their source repositories do not need an `apm.yml`. Consumers receive them transitively when installing this package. References are pinned to a commit so updates are deliberate and reviewable.

Before adding or updating a dependency, review its scope, license, prerequisites, and compatibility with applicable instructions. Reused procedures supplement DevHub guidance; they do not grant commit/push permission, bypass approval requirements, or justify unrelated tool installation. Extend the appropriate local primitive only for a remaining DevHub-specific gap, without copying upstream guidance. Host-provided capabilities can also be reused without declaring another dependency when they already meet the need.

### How guidance is layered

```text
User request
    |
    v
Entry point: Orchestrator (recommended), a specialist agent, or default Copilot Agent
    |
    +-- Role definition (agent, such as Coder): responsibilities, boundaries, and workflow
    +-- Common instructions (instructions/common.instructions.md): shared engineering, testing, and documentation standards
    +-- Matching technology/tool instructions: common package and/or consumer project
    +-- Consumer project instructions (e.g. project copilot-instructions.md, AGENTS.md): architecture, conventions, domain, and commands
    +-- Relevant skills: focused procedures loaded when needed
    |
    v
Implementation / documentation / review, with relevant validation and evidence
```

| Guidance layer | Scope and owner |
|---|---|
| Agent | Defines the role, not the complete set of rules for every repository. |
| Common instructions | One `common.instructions.md` file defines standards shared across roles and file types. |
| Technology/tool instructions | Additional instructions in this package apply only to their specified files or tasks, such as Python, Ansible, Dockerfiles, or GitHub Actions. |
| Project instructions | The consumer repository owns its own `copilot-instructions.md`, `AGENTS.md`, and scoped instructions for its architecture, tools, and domain. These are outside this common package. |
| Skills | Loaded when an agent needs a relevant repeatable procedure. |

> **Why not common instructions in an agent (e.g. coding standards in Coder)?** The common instructions are meant to provide a single source of truth for shared standards across all agents and tasks. Placing them within an agent could fragment the guidance and make it harder to maintain consistency across different roles and repositories. Other agents need access to the same shared standards to ensure coherent behavior and adherence to the overall policies. For example, the Review agent would also need to reference the same coding standards to perform accurate code reviews correctly and consistently on the output of the Coder agent.

The shared standards live in one common instruction file to keep policy simple and coherent. Splitting coding, testing, documentation, and other general rules across multiple files could make it unclear which combination applies or leave an agent without part of the baseline. A single file is easy for every common agent to reference, and its `applyTo: "**"` scope lets supported hosts attach it across file work. Agent definitions also reference it explicitly, which is important for analysis- or review-only tasks that may not modify matching files.

Instructions supplement one another. A project-specific instruction is not automatically an override of the common standards, and host behavior differs. Follow all applicable guidance and surface material conflicts rather than assuming a precedence rule. See [custom instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions) and [subagents](https://code.visualstudio.com/docs/agents/run/subagents) for current host behavior.

---

## Usage

### Installation

1. Open the **consumer workspace root** in VS Code. Its `apm.yml` must declare this package as a dependency; for this repository, [the root manifest apm.yml](../../../apm.yml) already points to `./packages/apm/common`.
2. From that workspace root, install the Copilot customizations:

   ```sh
   apm install --only apm --target copilot
   ```

3. Configure VS Code Chat using the [recommended setup](#recommended-chat-setup), then select **Orchestrator** for a coordinated task, or an individual specialist or the default Copilot Agent for direct work.

APM installs the common agents, instructions, and dependency skills into the consumer workspace; the package merely being checked out or listed in `apm.yml` does not activate it. Confirm the agents, instructions, and skills are discoverable in the selected host. Refresh or reopen the chat session if installation occurred while VS Code was open.

The common instructions are part of the installed setup and apply alongside the consumer's normal AI customizations. Add project context in the consumer repository—for example, `.github/copilot-instructions.md`, `AGENTS.md`, or appropriately scoped `*.instructions.md` files—rather than copying or replacing the common standards. Instructions are guidance, and support varies by harness.

### Recommended Chat setup

For autonomous work in a trusted DevHub development workspace:

1. In [VS Code Chat](https://code.visualstudio.com/docs/agents/run/chat-view), select **Copilot** as the **Session Target**. This selects the [Copilot agent harness](https://code.visualstudio.com/docs/agents/run/agent-harnesses), independently of the model or custom agent.
2. Select **Orchestrator** from the agent picker (or **Agent** for the built-in implementation role if you do not want to use Orchestrator). Select **Autopilot** from the mode picker to let the agent continue, retry, and work toward completion without repeated prompts (except for maybe some small approvals). In the Copilot harness, [Autopilot is an agent mode](https://code.visualstudio.com/docs/agents/run/approvals#_how-autopilot-works), not a permission level or a replacement for the selected custom agent.
3. Open **Permissions** and turn **Sandboxing for terminal** off for this session, where policy permits. This is the DevHub convenience recommendation for trusted workspaces to avoid sandbox-related restrictions interfering with local tooling and shell startup configuration such as `.bashrc`; it is not a requirement of the package or a general fix for shell configuration errors. See [terminal sandboxing](https://code.visualstudio.com/docs/agents/run/agent-sandboxing#_control-sandboxing-for-the-current-session).

Autopilot auto-approves tools, and turning terminal sandboxing off removes its file-system and network restrictions. Use this combination only when you trust the workspace, its dependencies, and the requested actions, and can accept those actions running with your account's access. Keep sandboxing enabled and use **Manual permissions** when that risk is not acceptable; never bypass organization policy. These controls are independent: Autopilot does not itself disable sandboxing. See [approvals and permissions](https://code.visualstudio.com/docs/agents/run/approvals) and [trust and safety](https://code.visualstudio.com/docs/agents/concepts/trust-and-safety).

### Choosing an agent

Use the Orchestrator by default for end-to-end tasks. It can handle simple work directly, use one specialist, or coordinate several independent assignments for a larger task.

Using individual agents or the default Copilot Agent directly is also supported. This is useful for focused work or when a user prefers to coordinate the steps themselves; installed common instructions and the selected agent's role guidance still apply where the host supports them.

These customizations make agent behavior more consistent with the team's standards and conventions. Generic agents can provide useful work, but may not know a team's preferred architecture, validation, documentation, or error-handling practices. This package supplies a reusable baseline; consumer instructions complete it with local context. Results still depend on the task, available evidence, and host support.

### Planning before implementation

For a very large or uncertain task, optionally ask the Orchestrator to analyze the request and propose a plan before implementing. This gives you a chance to agree on scope, dependencies, risks, and acceptance criteria before code changes begin:

```text
Analyze this request and create an implementation plan. Do not edit files or implement anything yet. Identify dependencies, risks, and validation criteria. Wait for my approval before implementation.
```

After reviewing and refining the plan, explicitly ask the Orchestrator to implement it. For well-scoped work, request implementation directly; the Orchestrator still scales planning and delegation to the task.

Detailed prompt engineering practices are outside this guide's scope. For background, see [Prompt engineering - Wikipedia](https://en.wikipedia.org/wiki/Prompt_engineering) and the [prompt engineering references](#prompt-engineering).

### Consumer-specific guidance

Reuse the common agents and add local constraints in the consumer repository:

```text
consumer/
  apm.yml                              # declares the common package
  .github/
    copilot-instructions.md            # essential repository-wide context
    instructions/
      service-api.instructions.md      # API-specific paths and constraints
  .github/skills/
    deploy-service/SKILL.md            # project-only procedure, if needed
```

For example, `copilot-instructions.md` can provide repository-wide architecture and tooling context, while `service-api.instructions.md` can specify an API contract or service boundary:

```yaml
---
description: "Use when changing the service API."
applyTo: "src/api/**,tests/api/**"
---
```

Keep deployment environments, registries, SDK choices, and domain rules in consumer-owned instructions, not reusable role definitions. Add a sibling APM package, such as the existing [homelab package](../homelab/), when several repositories share that context; declare it alongside common in consumers.

Instructions supplement one another; a more specific file is not an automatic override. Avoid contradictory rules and surface conflicts. Discovery and subagent support depend on the host: verify the installed agents, skills, and matching instructions in the intended environment.

---

## Design

| Part | Responsibility |
|---|---|
| Orchestrator | Recommended entry point; assesses complexity, plans, delegates when useful, reconciles results, and owns delivery. Handles simple work directly. |
| Specialist agents | Own focused roles and return their work and evidence to the Orchestrator. |
| Common and scoped instructions | Provide shared standards and applicable technology, tool, or project constraints to every role. |
| Skills | Supply repeatable procedures on demand. |
| APM | Packages and deploys customizations to supported host locations; it does not execute the workflow or enforce model compliance. |

```text
User request
     |
     v
Orchestrator
     |
     +-- Simple task: work directly, validate, and report
     |
     +-- Larger task: delegate only useful, bounded work
            |
            +--> Architect    design, contracts, trade-offs
            +--> Coder(s)     implementation, tests, relevant validation
            +--> Documenter(s) accurate, concise documentation
            +--> Reviewer     independent review, including test adequacy
                     |
                     +-- Each role uses applicable common/project instructions
                     |   and relevant skills
                     v
             Results, evidence, and blockers
                     |
                     v
       Orchestrator reconciles, verifies, and reports
```

The diagram shows possible responsibilities, not a required sequence or an instruction to invoke every role. The Orchestrator supplies each assignment's goal, context, constraints, and acceptance criteria. When work is genuinely independent, it can assign multiple bounded tasks in parallel, including separate code changes to multiple Coders or disjoint documents to multiple Documenters, if the selected harness supports it. Shared or dependent work should remain coordinated rather than split for concurrency.

### Why orchestrate

The additional orchestration and delegation layer is intended to improve the quality and autonomy of larger tasks. The [Orchestrator](.apm/agents/orchestrator.agent.md) can coordinate analysis, implementation, tests, review, documentation, and corrections without requiring the user to manually prompt each step. Protected environments may still require approvals according to their policies.

Key benefits of this approach are:

- **Specialized responsibilities**: [Architect](.apm/agents/architect.agent.md), [Coder](.apm/agents/coder.agent.md), [Documenter](.apm/agents/documenter.agent.md), and [Reviewer](.apm/agents/reviewer.agent.md) focus on distinct assignments with explicit boundaries and expected outputs. Coder owns implementation together with its tests and validation, avoiding an unnecessary handoff for work that belongs to the same change.
- **Independent review**: Reviewer checks the actual changes, surrounding behavior, and test adequacy rather than relying solely on the implementer's summary. This provides another opportunity to identify incorrect assumptions, missing failure paths, or regressions; it reduces reliance on self-review without guaranteeing an unbiased or defect-free result.
- **Fresh, focused context**: Each specialist receives a bounded assignment and the context needed to complete it. A separate context can keep the review or design discussion focused instead of requiring one conversation to carry every implementation detail and evaluate all of its own earlier decisions.
- **Consistent team standards**: Every common agent references the same engineering, testing, and documentation instructions, together with applicable project guidance. This gives implementation and review a shared quality bar instead of leaving each role to infer conventions independently.
- **Better overall quality**: Focused implementation, documentation, and review can improve correctness, maintainability, consistency, and completeness together. The Orchestrator reconciles these contributions against the requested outcome rather than considering a code change alone sufficient.
- **Clear acceptance criteria**: Assignments include the goal, constraints, dependencies, and conditions for completion. These criteria help specialists target the required behavior and let the Orchestrator identify missing work or unresolved blockers before reporting completion.
- **Iterative improvement**: Test failures or concrete review findings lead to corrections and further validation rather than treating the first generated solution as finished. The Orchestrator tracks whether the correction addresses the finding and reports a blocker if repeated attempts do not resolve it.
- **Parallel work where useful**: Independent code changes or disjoint documentation tasks can progress through multiple instances of the appropriate specialist when the harness supports it. Dependencies and shared-file ownership remain coordinated so concurrency does not simply create conflicting edits or duplicated work.
- **More autonomous execution**: The Orchestrator coordinates useful stages, supplies task context, and reconciles results without the user having to prompt every next step. Material decisions, missing requirements, and environment approvals still require user input when they cannot safely be resolved within the assignment.
- **Fewer interruptions**: A substantial task can progress through implementation, validation, review, and corrections in a coordinated run instead of repeated user-driven prompt cycles. The user can return to a consolidated result rather than repeatedly prompting the agent to test, update documentation, or address findings.
- **Less context switching**: During a longer run, the user can work on a related or unrelated task and return when a more complete result is available. This can make the elapsed runtime more useful than several short waits that repeatedly interrupt another activity.
- **More efficient final review**: The user can review implementation, tests, documentation, and findings together, with validation commands and remaining gaps reported explicitly. This makes it easier to assess what was delivered and what remains uncertain without reconstructing the evidence from intermediate interactions.
- **Scales with task complexity**: Simple work stays lightweight and can be handled directly without subagents or a formal plan. Larger or higher-risk tasks can use focused specialists and independent review where the additional context and coordination are justified.

Delegation adds coordination, model usage, and potentially a longer run. For small tasks, that overhead may not be worthwhile; the Orchestrator handles them directly. For substantial work, a longer coordinated run can be preferable to repeated user-driven interactions. Follow-up prompts may still be useful, and independent review is used when the task benefits from it rather than required for every small change.

> **Personal note:** I was honestly really surprised by the results after using this approach. The overall quality was noticeably better, not just in the code, but also in the documentation, testing, reviews, and completeness of the result. Although an orchestrated task can take longer to run, I found that this actually improved my productivity over the longer term. Instead of having many short interruptions where I had to review something, provide another prompt, wait for another change, and repeat the process, I could continue working on something else while the agents worked through the task. When I returned, there was a much more complete result that I could review all at once, step by step. For me, the longer autonomous runs, fewer interruptions, and higher-quality results made the overall workflow feel both more productive and more efficient.

### Focused roles and testing ownership

The [Coder](.apm/agents/coder.agent.md) is responsible for making its implementation and tests coherent. Testing is part of implementation: Coder adds or updates tests and runs relevant validation for its changes. A separate Tester is not included because making routine testing a handoff would fragment ownership and add a step for Coder to reconcile. The [Reviewer](.apm/agents/reviewer.agent.md) independently checks whether tests adequately cover changed behavior and flags gaps. This keeps the agent set small and focused; a few high-quality roles are more useful than many overlapping roles.

### Self-learning and maintenance feedback

The Orchestrator follows a bounded maintenance feedback loop: it identifies durable lessons, updates the relevant common customization when working in the repository that owns it, and otherwise reports proposed improvements to the user. This is explicit maintenance of the package, not persistent model training or a claim that agents autonomously change their own instructions in every repository.

Its final report describes meaningful changes by component, their impact, significant decisions, validation evidence, and remaining gaps. A **Self-learning and maintenance** section makes the feedback loop visible: the observed problem, why the lesson is reusable, where guidance was updated or merely proposed, and how the update was validated. If no durable lesson emerged, the report says so rather than inventing one. Report depth scales with the task; a large change needs more than file counts and a few implementation bullets.

### Model selection

The [Orchestrator](.apm/agents/orchestrator.agent.md) declares `model: auto` rather than pinning a specific model. The design delegates model selection to GitHub Copilot and the active harness instead of maintaining another routing system in this package. Where task-aware routing is supported, it can match task complexity to model capability while considering availability, latency, cost, and applicable policies. This avoids manually choosing a model for each step and aims to balance output quality with token and cost efficiency; it does not guarantee better results than every manual choice.

Use the controls available in your Copilot surface to express your preferences:

- **Auto model selection** offers task-optimization tiers where supported: **Efficiency** prioritizes cost, **Balance** balances cost, quality, and latency, and **Intelligence** prioritizes quality. GitHub documents a 10% model-cost discount for eligible paid-plan use of Auto in Copilot Chat or cloud agent; do not assume the same discount applies to every surface or routing mode.
- **Copilot Fusion**, where available instead of Auto in the picker, selects models and execution patterns at runtime. Its **Standard**, **High**, and **Max** effort levels let users choose quality, cost, and latency trade-offs without pinning a model for every step.

Available controls and how a custom agent's model setting interacts with the session selection depend on the host. This package does not configure a Fusion effort level or implement its own model-selection algorithm. Subagent model selection also follows the active harness's rules, not a package-wide guarantee that every worker uses Auto.

See GitHub's [Auto model selection](https://docs.github.com/en/copilot/concepts/models/auto-model-selection), [Copilot Fusion](https://docs.github.com/en/copilot/concepts/models/copilot-fusion), and [model comparison](https://docs.github.com/en/copilot/reference/ai-models/model-comparison) documentation for current availability, routing options, and pricing considerations.

### Harness support

In the VS Code **Local** harness, the Orchestrator's `agents` allowlist defines available workers and the `agent` tool enables delegation; the description helps discovery but does not itself grant that capability. Other Copilot harnesses or hosts may support different fields and delegation mechanisms. Verify the setup in the selected environment; see [subagent configuration](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference#_subagent-configuration) and [harness compatibility](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference#_harness-compatibility).

### Package contents

Sources are maintained directly in this package:

```text
common/
  apm.yml
  README.md
  CHANGELOG.md
  .apm/
    agents/
      orchestrator.agent.md
      architect.agent.md
      coder.agent.md
      documenter.agent.md
      reviewer.agent.md
    instructions/
      common.instructions.md
      ai-customization.instructions.md
      ansible.instructions.md
      dockerfile.instructions.md
      github-actions.instructions.md
      python.instructions.md
    skills/
      manage-skills/
        SKILL.md
```

#### Agents

- [Orchestrator](.apm/agents/orchestrator.agent.md): assesses complexity, plans, coordinates, verifies, and reports. Its subagent allowlist contains the four specialist roles below.
- [Architect](.apm/agents/architect.agent.md): analyzes design boundaries, contracts, alternatives, and implementation criteria.
- [Coder](.apm/agents/coder.agent.md): implements features and fixes, refactors code, adds or updates tests, and runs relevant validation. It owns a change until the implementation and tests are coherent; it is not renamed to another role to account for testing.
- [Documenter](.apm/agents/documenter.agent.md): produces and fact-checks documentation against implementation and verified behavior.
- [Reviewer](.apm/agents/reviewer.agent.md): independently reviews correctness, regressions, requirements, maintainability, and test coverage without editing.

There is no separate Tester agent. Keeping testing with Coder avoids an unnecessary implementation-to-testing handoff; the Reviewer provides a separate perspective on whether coverage and validation are adequate. Keep the overall agent set small and add a new role only when it has a distinct responsibility that is valuable to assign independently.

The specialist agents set `agents: []` to prevent nested delegation where the host honors that property. In VS Code Local, the Orchestrator's `agents` allowlist and `agent` tool configure delegation. Other hosts may differ; this is not a read-only security sandbox.

#### Instructions

- [Common instructions](.apm/instructions/common.instructions.md) are the single shared baseline for engineering, tests, and documentation. They apply across roles and file types, and are explicitly referenced from every agent.
- The remaining package instructions are more specific and apply only when their description or file scope matches: [AI customization](.apm/instructions/ai-customization.instructions.md), [Ansible](.apm/instructions/ansible.instructions.md), [Dockerfile](.apm/instructions/dockerfile.instructions.md), [GitHub Actions](.apm/instructions/github-actions.instructions.md), and [Python](.apm/instructions/python.instructions.md).
- Consumer repositories own their project-specific AI instructions outside this package, such as `copilot-instructions.md`, `AGENTS.md`, or scoped instruction files. These add local architecture, tools, commands, and domain constraints.

#### Skills and prompts

[manage-skills](.apm/skills/manage-skills/SKILL.md) guides autonomous skill creation and maintenance within the assigned scope: inspect existing capabilities, choose the right primitive, author or consolidate, validate, and report limitations. The [manifest](apm.yml) also declares the community skills described under [Reuse before authoring](#reuse-before-authoring); their sources remain upstream, outside the local tree above. Other available skills can be used without copying them into this package. This package currently defines no prompt files; prompts are appropriate for reusable, user-invoked task templates rather than persistent role rules or procedures.

---

## Maintenance and validation

### Ongoing maintenance

The reusable agents and common instructions are centrally maintained for consistent team standards. Review them when experience reveals a recurring gap or the supported workflow changes, not after every one-off task. Keep consumer-specific learnings with their owning projects.

Skills may need more frequent refinement because they capture concrete, evolving workflows. Verify their steps against the real process. Keep a generic skill in the common package, or package service/team workflows separately so consumers can reuse them.

When a task reveals a durable improvement, update the relevant customization and record the change in this package's [CHANGELOG](CHANGELOG.md). The Orchestrator reports proposed improvements when it cannot edit the repository that owns these shared files.

### Validation

Edit this package's `.apm/` sources and update this README when its design or contents change. There is no package-generation sync action in the current repository. The [root manifest](../../../apm.yml) declares `./packages/apm/common` as a local dependency; it does not itself install or activate the package.

From this package directory, validate local primitives without installing over workspace customizations:

```sh
apm compile --validate --local-only
```

This checks agents and instructions; also validate skill metadata and resource links. An isolated install from the repository root with `apm install --only apm --target copilot --root <scratch-directory>` checks deployment without replacing workspace customizations. For the Copilot target, agents and instructions land under `.github/`, and skills under `.agents/skills/`.

Use the [APM consumer guide](https://microsoft.github.io/apm/consumer/) for dependency installation and target options. After installation, check host discovery and exercise a representative task; static validation alone does not prove that the correct agent or skill was invoked. Keep consumer-specific customizations separate from installed package files.

---

## References

This guide covers the common package's setup, usage, and design decisions. General AI concepts, theory, and detailed prompt engineering practices are outside its scope; the following references provide background without duplicating it here.

### Prompt engineering

- [Prompt engineering - Wikipedia](https://en.wikipedia.org/wiki/Prompt_engineering): general overview and terminology.
- [Prompt engineering - OpenAI API](https://developers.openai.com/api/docs/guides/prompt-engineering?api-mode=responses): practical guidance for OpenAI models.
- [Prompt design strategies - Gemini API](https://ai.google.dev/gemini-api/docs/prompting-strategies): provider-specific guidance for Gemini models.

### AI concepts

- [Artificial intelligence - Wikipedia](https://en.wikipedia.org/wiki/Artificial_intelligence): overview of the broader field.
- [Machine learning - Wikipedia](https://en.wikipedia.org/wiki/Machine_learning): learning methods and their relationship to AI.
- [Large language model - Wikipedia](https://en.wikipedia.org/wiki/Large_language_model): background on the models underlying language-based assistants.
- [What are AI agents? - IBM](https://www.ibm.com/think/topics/ai-agents): agent concepts and architectures.

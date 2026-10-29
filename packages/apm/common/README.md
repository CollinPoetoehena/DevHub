# DevHub Common Agent Package

`devhub-common` is an [Agent Package Manager (APM)](https://microsoft.github.io/apm/) package of reusable engineering agents, skills, and scoped instructions. Start with the Orchestrator; extend project context without copying the specialist agents.

DevHub's human-facing repository and package conventions are in the [shared guidelines](../../../docs/GUIDELINES.md); this package owns the reusable AI role standards and workflows.

## Table of Contents

- [AI customizations: concepts and design](#ai-customizations-concepts-and-design)
- [Using the Orchestrator](#using-the-orchestrator)
- [Design and flow](#design-and-flow)
  - [Why orchestrate](#why-orchestrate)
- [Package contents](#package-contents)
  - [Agent standards](#agent-standards)
  - [Skills and instructions](#skills-and-instructions)
- [Project-specific guidance](#project-specific-guidance)
- [Maintenance and validation](#maintenance-and-validation)
  - [Ongoing maintenance](#ongoing-maintenance)

---

## AI customizations: concepts and design

[Understand agent customization](https://code.visualstudio.com/docs/agents/concepts/customization) explains how the customization types complement each other:

| Customization | What it is | Use it for |
|---|---|---|
| Agents | Reusable configurations for a role, combining instructions, tools, and optionally a model. | A defined responsibility, such as coordinating work, implementing code, or reviewing changes. |
| Skills | On-demand folders of instructions and optional scripts, examples, and resources. | A focused procedure an agent can load when a relevant task arises. |
| Instructions | Reusable context that guides coding practices and project requirements. | Rules that apply generally or to files selected by a scope/glob. |

These are guidance mechanisms, not guarantees: behavior and discovery depend on the agent harness and host. Use agents to define *who* performs a task, skills to teach *how* to perform a repeatable task, and instructions to provide relevant *context and constraints*. A subagent is an agent invoked by another agent for a focused task; in VS Code, see [Use subagents](https://code.visualstudio.com/docs/agents/run/subagents) and [Agents concepts](https://code.visualstudio.com/docs/agents/concepts/agents).

### How this package applies them

This package deliberately keeps generic coding guidance in the [**Coder**](.apm/agents/coder.agent.md) agent rather than putting it in all-files general instructions. The Coder owns the shared code standards for its implementation work; scoped language and project instructions add only the constraints that differ, such as Python conventions, a Go toolchain, or a service-specific API rule. This keeps role standards reusable while letting consumers extend them with targeted guidance.

Likewise, generic documentation and testing standards belong to the [**Documenter**](.apm/agents/documenter.agent.md) and [**Tester**](.apm/agents/tester.agent.md) agents. Shared workflow guidance belongs to the [**Orchestrator**](.apm/agents/orchestrator.agent.md), not an all-files instruction. Language/tool instruction files apply only to their specified files, and project-specific rules should live with the consumer project. The [AI customization instructions](.apm/instructions/ai-customization.instructions.md) apply specifically when authoring or maintaining customization files.

This is a deliberate design choice, not a claim that general instructions cannot contain coding standards. This package has no all-files coding instruction: keeping generic code standards in the Coder lets the same role work with focused, project-specific instruction sets without loading every project's rules into one global file.

### Design principles

- Be concise: capture the purpose, triggers, boundaries, essential steps, and expected outcome. Do not write enormous prompts.
- Give each rule one home: role standards in agents, repeatable procedures in skills, and language/tool/project constraints in scoped instructions.
- Prefer extending an existing customization over creating overlapping or conflicting guidance. Use specific descriptions and narrow instruction scopes.
- Keep detailed resources separate and load them only when needed. Add scripts or templates only when they materially help the workflow.
- Check current official documentation for metadata, locations, and host behavior; link to it instead of duplicating it.

For official details, see [custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents), [agent skills](https://code.visualstudio.com/docs/agent-customization/agent-skills), [custom instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions), the [Agent Skills specification](https://agentskills.io/), and [APM primitives](https://microsoft.github.io/apm/producer/author-primitives/).

---

## Using the Orchestrator

1. Open the **consumer workspace root** in VS Code. Its `apm.yml` must declare this package as a dependency; for this repository, the root manifest already points to `./packages/apm/common`.
2. From that workspace root, install the Copilot customizations:

   ```sh
   apm install --only apm --target copilot
   ```

3. Open VS Code Chat, select **Orchestrator** from the agent picker, and describe the outcome you want. Refresh or reopen the chat session if the agent was installed while VS Code was already open.

The package being present in a checkout or listed in `apm.yml` is not enough by itself; APM must install it into the workspace before VS Code can discover the agent. Confirm that the Orchestrator appears in the picker. Subagent delegation depends on the selected harness and its tool support.

---

## Design and flow

| Part | Responsibility |
|---|---|
| Orchestrator | Entry point: assess complexity, plan, delegate when useful, reconcile results, and own delivery. Handles simple work directly. |
| Specialist agents | Define a role, its boundaries, reusable standards, working approach, and output. |
| Skills | Provide repeatable, on-demand procedures; bundle scripts, references, or templates only when needed. |
| Instructions | Supply applicable workflow and project/language/tool constraints, not another copy of role standards. |
| APM | Package and deploy these primitives to supported host locations; it does not execute the workflow or enforce model compliance. |

```text
User request
     |
     v
Orchestrator
     |
     +-- Simple task: work directly, then verify and report
     |
     +-- More complex tasks: Focused assignments (parallel when independent)
            |
            +--> Architect    design, contracts, trade-offs
            +--> Coder        implementation
            +--> Documenter   accurate, concise documentation
            +--> Tester       behavioral verification
            +--> Reviewer     independent findings
                     |
                     +-- Each role uses, when applicable:
                     |     - package skills in .apm/skills/
                     |     - other available skills
                     |     - matching instruction files
                     |     - project code, tools, and evidence
                     |
                     v
             Results, evidence, blockers
                     |
                     v
               Orchestrator
                     |
                     v
       Reconcile / request corrections / verify
                     |
                     v
      Final outcome and validation summary
```

The diagram shows responsibilities, not a mandatory sequence or a requirement to invoke every agent. The orchestrator supplies each assignment's goal, context, constraints, and acceptance criteria; specialists return results rather than spawning another team. Skills and instructions also apply to direct orchestrator work when relevant.

### Why orchestrate

The additional orchestration and delegation layer is intended to improve the overall quality and autonomy of larger tasks. Instead of relying on a single agent to implement, validate, review, and document its own work, the [Orchestrator](.apm/agents/orchestrator.agent.md) can delegate parts of the task to specialized agents with independent responsibilities and fresh context.

Key benefits of this approach are:

- **Specialized responsibilities** – The specialist agents like [Coder](.apm/agents/coder.agent.md), [Reviewer](.apm/agents/reviewer.agent.md), [Tester](.apm/agents/tester.agent.md), [Architect](.apm/agents/architect.agent.md), and [Documenter](.apm/agents/documenter.agent.md) can each focus on the part of the task they are specifically designed for.
- **Independent review** – The agent reviewing or testing the implementation is not necessarily the same agent that created it, providing a fresh perspective that can catch issues or improvements the original implementation pass missed.
- **Better overall quality** – Multiple focused passes can improve not only the code itself, but also tests, documentation, architecture, consistency, and completeness of the final result.
- **Iterative improvement** – Findings from testing or review can result in further implementation and validation rather than treating the first generated solution as the finished result.
- **Fresh context** – Delegating work to another agent introduces a separate context and reasoning path instead of repeatedly asking the same context to evaluate its own decisions.
- **Better separation of concerns** – Implementation, review, testing, architecture, and documentation remain distinct responsibilities while still contributing to the same overall task.
- **More autonomous execution** – The [Orchestrator](.apm/agents/orchestrator.agent.md) can coordinate several stages of a task without requiring the user to manually prompt every next step.
- **Fewer interruptions** – Instead of several short implementation → review → fix → test → documentation interactions, a substantial task can progress through those stages in a longer coordinated run.
- **Less context switching for the user** – While the agents continue working through the task, the user can focus on something else and return when there is a more complete result to review.
- **More efficient final review** – The user can review the implementation, tests, documentation, and findings together and step by step, rather than repeatedly reviewing small intermediate changes.
- **Scales with task complexity** – The [Orchestrator](.apm/agents/orchestrator.agent.md) can use a lightweight approach for simple work and involve additional specialist agents when a task benefits from deeper implementation, validation, or review.

There is, of course, a trade-off. Delegation adds coordination, token usage, and potentially a longer overall run. For small and straightforward tasks, that additional overhead may not be worthwhile (smaller tasks are automatically handled without full orchestration by the [Orchestrator](.apm/agents/orchestrator.agent.md)). For more substantial tasks, this is an accepted trade-off: a longer autonomous run can be preferable to many shorter user-driven interactions when it results in a more thoroughly implemented, tested, reviewed, and documented outcome.

In the VS Code **Local** harness, the Orchestrator's `agents` allowlist defines the available workers and the `agent` tool enables delegation; the description helps discovery but does not itself grant that capability. Other Copilot harnesses or hosts may support different fields and delegation mechanisms, so the configuration should be verified for the selected harness. See [subagent configuration](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference#_subagent-configuration) and [harness compatibility](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference#_harness-compatibility).

For more details on each agent's role and responsibilities, refer to their respective documentation in the `.apm/agents` directory.

> **Personal note:** I was honestly really surprised by the results after using this approach. The overall quality was noticeably better, not just in the code, but also in the documentation, testing, reviews, and completeness of the result. Although an orchestrated task can take longer to run, I found that this actually improved my productivity over the longer term. Instead of having many short interruptions where I had to review something, provide another prompt, wait for another change, and repeat the process, I could continue working on something else while the agents worked through the task. When I returned, there was a much more complete result that I could review all at once, step by step. For me, the longer autonomous runs, fewer interruptions, and higher-quality results made the overall workflow feel both more productive and more efficient.

---

## Package contents

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
      tester.agent.md
      reviewer.agent.md
    instructions/
      ai-customization.instructions.md
      ansible.instructions.md
      dockerfile.instructions.md
      github-actions.instructions.md
      python.instructions.md
    skills/
      manage-skills/
        SKILL.md
```

### Agent standards

- [Architect](.apm/agents/architect.agent.md): evidence-based design, simple boundaries, alternatives, and implementation criteria.
- [Coder](.apm/agents/coder.agent.md): readable, focused code; reuse; type safety; explicit errors; behavior preservation and focused validation.
- [Documenter](.apm/agents/documenter.agent.md): code-verified facts, essential project decisions, official references, and consistent Markdown.
- [Tester](.apm/agents/tester.agent.md): meaningful behavioral tests, existing tooling, containerized Python tests, and reports under `test-results/`.
- [Reviewer](.apm/agents/reviewer.agent.md): non-editing review of correctness, regressions, requirement coverage, and verification gaps.

The [Orchestrator](.apm/agents/orchestrator.agent.md) coordinates these roles and allowlists them as subagents. In VS Code Local, the `agent` tool enables delegation and `agents` limits the worker list; the other listed built-in aliases preserve its ability to inspect and change code. In VS Code's Copilot harness, `agent` maps to its native delegation tool, but the `agents` allowlist is unsupported, so the available workers may differ. The description helps users discover the role; it does not grant delegation. This is not a read-only security sandbox. Specialist `agents: []` prevents nested delegation only in hosts that honor that field.

### Skills and instructions

[manage-skills](.apm/skills/manage-skills/SKILL.md) guides autonomous skill creation and maintenance within the assigned scope: inspect existing capabilities, choose the right primitive, author or consolidate, validate, and report limitations. Other available skills can be used without copying them into this package.

This package has no all-files general coding instruction. Generic code practices live in the [Coder](.apm/agents/coder.agent.md); documentation and testing standards live in their respective agents, and shared workflow guidance lives in the Orchestrator. Instructions are reserved for AI customization design and specific language/tool or project constraints, scoped with `applyTo` patterns. The [AI customization instructions](.apm/instructions/ai-customization.instructions.md) apply to agent, skill, prompt, and instruction files.

---

## Project-specific guidance

Reuse the common agents and add local constraints in the consumer repository:

```text
consumer/
  apm.yml                              # declares the common package
  .github/
    copilot-instructions.md             # essential repository-wide context
    instructions/
      service-api.instructions.md      # API-specific paths and constraints
  .github/skills/
    deploy-service/SKILL.md             # project-only procedure, if needed
```

For example, `copilot-instructions.md` can provide repository-wide context and guidance (on top of the common instructions defined in this APM package), while `service-api.instructions.md` can specify a supported API contract, service boundaries, or required verification command:

```yaml
---
description: "Use when changing the service API."
applyTo: "src/api/**,tests/api/**"
---
```

Keep deployment environments, registries, SDK choices, and domain rules in scoped instructions, not reusable role definitions. Add a sibling APM package, such as the existing [homelab package](../homelab/), when several repositories share that context; declare it alongside common in consumers.

Instructions supplement one another; a more specific file is not an automatic override. Avoid contradictory rules and surface conflicts. Discovery and subagent support depend on the host: verify the installed agents, skills, and matching instructions in the intended environment.

---

## Maintenance and validation

### Ongoing maintenance

The reusable agents are generally low-maintenance: define each role's purpose, boundaries, and quality bar carefully, then reuse it across tasks and projects. Review them when experience reveals a recurring gap or the supported workflow changes, not after every one-off task.

Skills may need more frequent refinement because they capture concrete, evolving workflows. That work is useful even without AI: teams already spend time following repeatable deployment, release, migration, or support procedures. A skill can make the steps reusable and easier to execute consistently. Use AI to draft or improve a skill itself (saves time and effort, and AI can create these with much higher consistency and quality, etc.), then verify its steps against the real process. Keep a generic skill in the common package, or package service/team workflows in a dedicated APM package so consumers can reuse them.

When a task reveals a durable improvement, update the relevant customization and record the change in this package's [CHANGELOG](CHANGELOG.md). Keep project-specific learnings in their owning repository. The Orchestrator is instructed to report proposed improvements in chat when it cannot edit the repository that owns these shared files.

### Validation

Edit this package's `.apm/` sources and update this README when its design or contents change. There is no package-generation sync action in the current repository. The [root manifest](../../../apm.yml) declares `./packages/apm/common` as a local dependency; it does not itself install or activate the package.

From this package directory, validate local primitives without installing over workspace customizations:

```sh
apm compile --validate --local-only
```

This checks agents and instructions; also validate skill metadata and resource links. An isolated install from the repository root with `apm install --only apm --target copilot --root <scratch-directory>` checks deployment without replacing workspace customizations. For the Copilot target, agents and instructions land under `.github/`, and skills under `.agents/skills/`.

Use the [APM consumer guide](https://microsoft.github.io/apm/consumer/) for dependency installation and target options. After installation, check host discovery and exercise a representative task; static validation alone does not prove that the correct agent or skill was invoked. Keep consumer-specific customizations separate from installed package files.

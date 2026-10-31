# DevHub Common Agent Package

`devhub-common` is the shared [Agent Package Manager (APM)](https://microsoft.github.io/apm/) package for reusable engineering agents, instructions, and skills. Its source is maintained in this directory; [`.apm/`](.apm/) contains the package customizations and [`apm.yml`](apm.yml) declares its pinned upstream skills.

The [DevHub APM overview](../README.md) owns shared concepts, repository setup, authoring, general agent usage, model selection, and maintenance. This README owns the common package's contents, orchestration design, execution flow, and constraints.

## Table of Contents

- [Package contents](#package-contents)
  - [Agents](#agents)
  - [Instructions](#instructions)
  - [Skills](#skills)
  - [Pinned upstream skills](#pinned-upstream-skills)
- [Design](#design)
  - [Why orchestrate](#why-orchestrate)
  - [Focused roles and testing ownership](#focused-roles-and-testing-ownership)
  - [Self-learning and maintenance feedback](#self-learning-and-maintenance-feedback)
- [Agent constraints](#agent-constraints)
- [Consumption](#consumption)

---

## Package contents

### Agents

| Agent | Responsibility |
|---|---|
| [Orchestrator](.apm/agents/orchestrator.agent.md) | Plans and coordinates engineering work. |
| [Architect](.apm/agents/architect.agent.md) | Analyzes architecture and defines boundaries and trade-offs. |
| [Coder](.apm/agents/coder.agent.md) | Implements changes, tests, and focused validation. |
| [Documenter](.apm/agents/documenter.agent.md) | Maintains accurate, concise documentation. |
| [Reviewer](.apm/agents/reviewer.agent.md) | Independently reviews changes and test adequacy. |

### Instructions

- [Common engineering instructions](.apm/instructions/common.instructions.md) provide shared engineering, testing, and documentation standards.
- [AI customization instructions](.apm/instructions/ai-customization.instructions.md) apply to agent, instruction, prompt, skill, and repository customization files.
- [Ansible](.apm/instructions/ansible.instructions.md), [Dockerfile](.apm/instructions/dockerfile.instructions.md), [GitHub Actions](.apm/instructions/github-actions.instructions.md), and [Python](.apm/instructions/python.instructions.md) instructions apply to their scoped files and tasks.

### Skills

| Skill | Purpose |
|---|---|
| [draft-github-issue](.apm/skills/draft-github-issue/SKILL.md) | Drafts a bounded, actionable issue without publishing it or implementing the work. |
| [manage-skills](.apm/skills/manage-skills/SKILL.md) | Guides creating, updating, reviewing, consolidating, and retiring skills. |
| [setup-ai-customizations](.apm/skills/setup-ai-customizations/SKILL.md) | Guides repository setup around the shared APM baseline and local project context. |

### Pinned upstream skills

[`apm.yml`](apm.yml) includes these skills from GitHub's [awesome-copilot](https://github.com/github/awesome-copilot) collection, both pinned to commit `5269f7ea2d6c3a9bfda5ed878b6726cf509121fd`:

| Skill | Purpose |
|---|---|
| [git-commit](https://github.com/github/awesome-copilot/tree/5269f7ea2d6c3a9bfda5ed878b6726cf509121fd/skills/git-commit) | Supports requested Git commits using Conventional Commits. |
| [webapp-testing](https://github.com/github/awesome-copilot/tree/5269f7ea2d6c3a9bfda5ed878b6726cf509121fd/skills/webapp-testing) | Supports testing and debugging local web interfaces with Playwright. |

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

The diagram shows possible responsibilities, not a required sequence or an instruction to invoke every role. The [Orchestrator](.apm/agents/orchestrator.agent.md) supplies each assignment's goal, context, constraints, and acceptance criteria. When work is genuinely independent, it can assign multiple bounded tasks in parallel, including separate code changes to multiple Coders or disjoint documents to multiple Documenters, if the selected harness supports it. Shared or dependent work should remain coordinated rather than split for concurrency.

### Why orchestrate

The additional orchestration and delegation layer is intended to improve the quality and autonomy of larger tasks. The Orchestrator coordinates analysis, implementation, tests, review, documentation, and corrections without requiring the user to manually prompt each step. Protected environments may still require approvals according to their policies.

The package's design provides:

- **Specialized responsibilities:** [Architect](.apm/agents/architect.agent.md), [Coder](.apm/agents/coder.agent.md), [Documenter](.apm/agents/documenter.agent.md), and [Reviewer](.apm/agents/reviewer.agent.md) receive bounded assignments with explicit ownership. Coder owns implementation together with its tests and validation.
- **Independent review:** Reviewer checks actual changes, surrounding behavior, and test adequacy rather than relying only on the implementer's summary. This creates another opportunity to detect assumptions, missing failure paths, or regressions; it does not guarantee unbiased or defect-free results.
- **Fresh, focused context:** Each specialist receives the context needed for its assignment rather than carrying every implementation detail in one conversation. The Orchestrator must supply that context explicitly.
- **Consistent standards and acceptance criteria:** Every common agent references the same engineering baseline and relevant project guidance. Assignments include observable completion criteria so contributions can be reconciled against the requested outcome.
- **Iterative correction:** Test failures and concrete review findings lead to corrections and further validation. Distinct unsuccessful attempts result in an explicit blocker rather than an unsupported completion claim.
- **Useful parallelism:** Independent implementation or documentation can progress through multiple instances of the appropriate role. Dependencies and shared-file ownership remain coordinated to avoid conflicting edits or duplicate work.
- **Fewer interruptions and easier final review:** A coordinated run can return implementation, tests, documentation, findings, and remaining gaps together. The user can work on something else during a longer run rather than repeatedly prompting each handoff.
- **Complexity-scaled effort:** Simple tasks remain direct and lightweight; larger or higher-risk tasks use specialists and independent review when their value justifies the added coordination and model usage.

Delegation can increase elapsed time and cost. For small tasks, that overhead may not be worthwhile; the Orchestrator handles them directly. For substantial work, a longer coordinated run can be preferable to repeated user-driven interactions. Material decisions and approvals still require user input when they cannot safely be resolved within the assignment.

> **Personal note:** I was honestly really surprised by the results after using this approach. The overall quality was noticeably better, not just in the code, but also in the documentation, testing, reviews, and completeness of the result. Although an orchestrated task can take longer to run, I found that this actually improved my productivity over the longer term. Instead of having many short interruptions where I had to review something, provide another prompt, wait for another change, and repeat the process, I could continue working on something else while the agents worked through the task. When I returned, there was a much more complete result that I could review all at once, step by step. For me, the longer autonomous runs, fewer interruptions, and higher-quality results made the overall workflow feel both more productive and more efficient.

### Focused roles and testing ownership

[Coder](.apm/agents/coder.agent.md) owns its implementation, tests, and focused validation as one coherent change. A separate Tester is not included because a routine handoff would fragment that ownership. [Reviewer](.apm/agents/reviewer.agent.md) independently assesses whether tests cover changed behavior and relevant failure paths. Keep the role set small; add another only for a genuinely distinct responsibility.

### Self-learning and maintenance feedback

The Orchestrator assesses observed failures, user corrections, and validation gaps before reporting. It retains only evidence-backed, reusable lessons, updates the relevant customization and changelog when working in the owning repository, and reports proposals otherwise. This is explicit package maintenance, not persistent model training or automatic self-modification.

Its report distinguishes outcome, changes, decisions, checks, learning and maintenance, remaining risks, and commit/push guidance. Report depth scales with the task; the learning assessment distinguishes applied updates, proposals, existing coverage, and no durable lesson. General maintenance and validation procedures remain in the [APM overview](../README.md#maintenance-and-validation).

Commit guidance persists across follow-up refinements while related changes remain uncommitted. The Orchestrator checks the worktree and updates the message and staging paths for the accumulated task, excluding unrelated or already committed work. Suggested commands are not executed without authorization.

---

## Agent constraints

- The Orchestrator is the package's recommended entry point for complete tasks. Its instructions scale the workflow to task complexity and keep simple work direct.
- The Orchestrator declares `model: auto` and the Architect, Coder, Documenter, and Reviewer as its available agents. Each specialist declares `agents: []` to disable nested delegation where the host honors that setting.
- Coder owns implementation tests and relevant validation. The package has no separate Tester role or routine Coder-to-Tester handoff.
- Each agent explicitly refers to the common instructions and the consumer repository's applicable guidance.
- Only the Orchestrator declares a model. Host support and availability determine which declared models, tools, agents, and customization files can be used; package metadata alone does not guarantee discovery or execution. See the overview's guidance on [working with agents](../README.md#working-with-agents) and [model selection](../README.md#model-selection).

---

## Consumption

Consumers identify this package as `CollinPoetoehena/DevHub/packages/apm/common`. DevHub's root [`apm.yml`](../../../apm.yml) uses the local dependency `./packages/apm/common`.

For the consumer manifest and installation process, follow the APM overview's [repository setup](../README.md#repository-setup). It also covers [consumer-specific guidance](../README.md#consumer-specific-guidance) and [validation](../README.md#validation); use the package source here rather than editing installed copies.

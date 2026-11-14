# Earlier AI Customizations

This note preserves the rationale for replacing the earlier customization layout, not a second maintained copy. Before I learned how to combine instructions, agents, and skills effectively, I put too much routine guidance into broad skills. I disliked the maintenance burden, overlapping rules, and especially the rigid, verbose `devhub-generic-change` workflow.

## Table of Contents

- [Historical layout](#historical-layout)
- [What did not work](#what-did-not-work)
- [Retired v2 orchestration layer](#retired-v2-orchestration-layer)
- [Current approach](#current-approach)

---

## Historical layout

Selected paths from the [earlier `.github/` tree](https://github.com/CollinPoetoehena/DevHub/tree/7f2fc1fb64219f8b8a51e0257c65a8b5e63be95d/.github):

```text
.github/
  agents/
    README.md
    devhub-architect.agent.md
    devhub-code-reviewer.agent.md
    devhub-documentation-specialist.agent.md
  instructions/
    README.md
  skills/
    README.md
    devhub-ai-customization/SKILL.md
    devhub-ansible-change/SKILL.md
    devhub-commit-message/SKILL.md
    devhub-docs/SKILL.md
    devhub-generic-change/SKILL.md
    devhub-go-change/SKILL.md
    devhub-python-change/SKILL.md
    devhub-terraform-change/SKILL.md
```

Later versions moved definitions under `docs/copilot/`. That folder is also removed rather than maintained as an inactive second setup; use Git history for the full contents. The instructions README explained placement and scope; it was not itself an automatically applied instruction file.

---

## What did not work

- The [generic-change skill](https://github.com/CollinPoetoehena/DevHub/blob/7f2fc1fb64219f8b8a51e0257c65a8b5e63be95d/.github/skills/devhub-generic-change/SKILL.md) wrapped ordinary coding in discovery, implementation, detailed documentation rules, validation, constraints, and completion reporting. Even with allowances for small tasks, it felt like an oversized workflow rather than focused assistance.
- Python and Ansible change skills repeated much of that discovery, documentation, testing, and reporting guidance. Improvements required checking several copies, with room for drift and conflicting expectations.
- General conventions and role responsibilities were mixed into task procedures. The broad fallback skill became another policy document to maintain instead of a reusable workflow with a distinct purpose.

The problem was this combination and scope, not skills themselves. Focused, reusable workflows remain useful.

---

## Retired v2 orchestration layer

The later all-purpose router assigned every request to fixed routes and many specialist roles, with exhaustive transition, reporting, and learning protocols. Universal routing reduced user choice for routine tasks; too many roles and detailed protocols made the workflow harder to understand, constrained judgment, and made it less adaptable to tasks and host capabilities. Its immediate replacement used native Agent mode by default and a user-selected two-session workflow for complex tasks, with planning and orchestration as skills. The [current role decision](../packages/apm/docs/adrs/workflow/WORKFLOW-AGENTS-AND-FOCUSED-SKILLS.md) replaces that skills-first representation while retaining distinct planning and implementation phases. Git history retains the retired definitions and records rather than maintaining superseded copies.

---

## Current approach

The [APM overview](../packages/apm/README.md) owns the maintained setup: independent shared guidelines, local workflow roles, and opt-in development stacks. Thin agents own roles and compose focused skills; Implementation Orchestrator handles both SIMPLE and STANDARD implementation, while Planner remains separate and is required for larger or consequential work. Small, understood tasks may skip planning. The [current role decision](../packages/apm/docs/adrs/workflow/WORKFLOW-AGENTS-AND-FOCUSED-SKILLS.md) explains why this differs from both the broad retired router and the later skills-first design.

Keep repository context and local constraints with the consumer; use the [authoring guidance](../packages/apm/README.md#authoring-repository-guidance) instead of forking shared role definitions. APM distributes files; it does not enforce compliance or guarantee discovery. See [current usage](../docs/GETTING-STARTED.md#ai-customizations) rather than treating this historical note as workflow instructions.

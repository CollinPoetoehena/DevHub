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

The later all-purpose router assigned every request to fixed routes and many specialist roles, with exhaustive transition, reporting, and learning protocols. Universal routing reduced user choice for routine tasks; too many roles and detailed protocols made the workflow harder to understand, constrained judgment, and made it less adaptable to tasks and host capabilities. The replacement uses native Agent mode by default and a user-selected two-session workflow for complex tasks. Planning and orchestration are reusable skill procedures invoked by the built-in agent, not custom main-agent modes. Git history retains the retired definitions rather than maintaining archived copies.

---

## Current approach

The [common APM package](../packages/apm/common/README.md) distributes shared customizations from one source:

- **Native agents retain coordination:** the active host agent invokes both workflow skills with the user's selected model and permission mode. Only the custom [Implementer](../packages/apm/common/.apm/agents/implementer.agent.md) remains for its bounded, test-first, no-subdelegation role.
- **Instructions supply shared standards and scoped constraints:** the common engineering baseline applies independently of workflow choice. Central instruction consolidation and distribution remain separate work.
- **Skills supply reusable, on-demand procedures:** [Planning](../packages/apm/common/.apm/skills/planning/SKILL.md) and [Implementation Orchestration](../packages/apm/common/.apm/skills/implementation-orchestration/SKILL.md) customize procedures without replacing the native agent loop. The [ADR](../packages/apm/common/.apm/skills/adr/SKILL.md) and [draft-github-issue](../packages/apm/common/.apm/skills/draft-github-issue/SKILL.md) skills serve focused tasks.
- **Projects extend rather than copy:** keep repository context and local constraints with the consumer; use the [authoring guidance](../packages/apm/README.md#authoring-repository-guidance) instead of forking shared role definitions.

This separates responsibilities, reduces duplicated rules, and keeps procedural detail out of routine work. APM distributes the files; it does not enforce compliance or guarantee discovery in every host. See [current usage](../docs/GETTING-STARTED.md#ai-customizations) and the official [VS Code customization concepts](https://code.visualstudio.com/docs/agents/concepts/customization).

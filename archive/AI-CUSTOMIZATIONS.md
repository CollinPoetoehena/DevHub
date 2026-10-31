# Earlier AI Customizations

This note preserves the rationale for replacing the earlier customization layout, not a second maintained copy. Before I learned how to combine instructions, agents, and skills effectively, I put too much routine guidance into broad skills. I disliked the maintenance burden, overlapping rules, and especially the rigid, verbose `devhub-generic-change` workflow.

## Table of Contents

- [Historical layout](#historical-layout)
- [What did not work](#what-did-not-work)
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

## Current approach

The [common APM package](../packages/apm/common/README.md) distributes shared customizations from one source:

- **Agents own roles:** Orchestrator, Architect, Coder, Documenter, and Reviewer. The Orchestrator handles simple work directly and delegates when useful; Coder owns testing with implementation.
- **Instructions supply shared standards and scoped constraints:** the common engineering baseline applies across roles; AI customization, Ansible, Dockerfiles, GitHub Actions, and Python add focused guidance.
- **Skills supply reusable, on-demand procedures:** the package currently includes [manage-skills](../packages/apm/common/.apm/skills/manage-skills/SKILL.md). Add a skill for a proven workflow, not another skills-only policy dump.
- **Projects extend rather than copy:** keep repository context and local constraints with the consumer; use the [consumer-specific guidance](../packages/apm/README.md#consumer-specific-guidance) instead of forking shared role definitions.

This separates responsibilities, reduces duplicated rules, and keeps procedural detail out of routine work. APM distributes the files; it does not enforce compliance or guarantee discovery in every host. See [current usage](../docs/USAGE.md#ai-customizations) and the official [VS Code customization concepts](https://code.visualstudio.com/docs/agents/concepts/customization).

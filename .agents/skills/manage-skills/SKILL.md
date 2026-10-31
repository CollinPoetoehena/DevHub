---
name: manage-skills
description: "Use when creating, updating, reviewing, consolidating, or retiring an agent skill, or capturing a proven repeatable workflow as a reusable skill."
---

# Create and Manage Skills

Maintain focused, discoverable skills without duplicating agent standards or project instructions.

## Procedure

1. **Establish the need.** Identify the repeated task, triggers, inputs, outcome, and acceptance checks. Inspect existing skills and applicable instructions first. Reuse or improve a matching skill; use an agent for a role or instructions for persistent constraints instead.
2. **Choose scope.** Follow the request and repository conventions. Shared DevHub capabilities belong in this package's `.apm/skills/<name>/`; project-only workflows belong in that project's supported skills directory, such as `.github/skills/<name>/`. Do not edit installed/generated copies or write to user-global locations without explicit scope.
3. **Author or update.** Use the minimal template below. Keep the name stable, lowercase alphanumeric with single hyphens, 1-64 characters, and identical to the directory name. Quote the description; state what the skill does and when it applies in at most 1024 characters.
4. **Keep it focused.** Be concise: include only prerequisites, actionable steps, necessary decisions, failure handling, and verification. Link to current official documentation instead of copying general theory. Add `references/`, `scripts/`, or `assets/` only when needed; reference bundled resources with relative links and load them on demand.
5. **Maintain safely.** Inspect callers and links before renaming, merging, or retiring a skill. Update references and remove only confirmed obsolete resources within scope. Preserve unrelated work; do not delete user-authored skills or publish changes without authorization.
6. **Validate.** Check YAML, required fields, name/directory agreement, description triggers, resource paths, and executable examples. For APM packages, run `apm compile --validate --local-only` from the package directory. Exercise a representative task and a relevant failure/edge case safely when feasible; check that a neighboring unrelated task would not trigger the skill. Verify discovery in the intended host, or explicitly report that runtime discovery was not checked.
7. **Report.** Summarize the skill's purpose, changes, validation, and any remaining limitations. Propose a new skill only for a proven reusable workflow, not after every one-off task.

## Minimal Template

```markdown
---
name: skill-name
description: "Use when performing <specific task and trigger conditions>."
---

# Skill Title

## Procedure

1. Inspect <inputs and prerequisites>.
2. Perform <focused steps, including failure handling>.
3. Verify <observable outcome and relevant edge cases>.

## Output

Return <deliverable, validation evidence, and blockers>.
```

## References

- [VS Code skills: locations, discovery, and frontmatter](https://code.visualstudio.com/docs/agent-customization/agent-skills)
- [Agent Skills specification](https://agentskills.io/specification)
- [APM skill packaging](https://microsoft.github.io/apm/producer/author-primitives/skills/)

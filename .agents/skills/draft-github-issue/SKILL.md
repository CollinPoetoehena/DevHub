---
name: draft-github-issue
description: 'Drafts one small, actionable GitHub Issue as copyable Markdown with context, scope, and verifiable acceptance criteria. Use when asked to write, draft, define, or refine an issue, bug report, feature request, or engineering task. Does not publish issues, manage labels or projects, or implement the work.'
---

# Draft a GitHub Issue

Turn a request into one small, actionable issue and return it as copyable Markdown. The skill only drafts: it does not create or update GitHub items, edit files, or implement the work.

## When to Use This Skill

- Writing a new issue for a bug, feature, or engineering task
- Refining an existing issue draft into a bounded, verifiable scope
- Splitting a large request into a first issue plus named follow-ups

## Steps

1. **Gather context.** Read the request, repository guidance, issue templates, and task-tracking conventions when available. Inspect relevant code or documentation to ground the draft; GitHub access is not required.
2. **Define the problem.** State the problem, why it matters, and the intended outcome before any solution. Keep one coherent scope, name exclusions or follow-ups, and link existing context instead of copying it.
3. **Structure the issue.** Use the [output template](#output), or a matching repository template when one exists. For bugs, add reproduction steps, expected versus actual behavior, and environment or evidence when known.
4. **Write acceptance criteria.** Write observable outcomes as unchecked checkboxes, each with how to verify it, including failure cases and preservation of existing behavior.
5. **Add planning details.** Add dependencies, risks, priority, and a rough estimate only when useful or required locally. When unknowns block implementation, scope the issue to the investigation that resolves them.
6. **Review the draft.** Check for a specific title, bounded scope, verifiable completion, and safe disclosure, then remove optional sections that add no value.

## Output

Return only the issue in a fenced Markdown block, without preamble. The first heading is the proposed title; the rest is the body.

````markdown
# <Concise, specific title>

## Context and goal
<Problem, impact, intended outcome, and relevant links.>

## Scope
<Included work and meaningful exclusions.>

## Acceptance criteria
- [ ] <Observable outcome and how to verify it.>

## Planning
<Priority and rationale, rough estimate with uncertainty, or dependencies, only when relevant.>

## Open questions
<Material unknowns and the next step to resolve them, only when needed.>
````

## Gotchas

- **Never invent facts:** no made-up issue numbers, labels, deadlines, estimates, or completed checks. Mark material unknowns explicitly instead.
- **Facts before causes:** separate observed behavior from suspected causes, so the implementer does not chase a guess.
- **Outcomes, not implementation:** acceptance criteria describe observable results; prescribe implementation only for real constraints.
- **Fence with four backticks:** the outer fence needs more backticks than any inner code block, or inner examples break the copyable block.
- **Safe disclosure:** omit secrets and private operational details, even when the target project board is private.

## References

- [GitHub issue templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/about-issue-and-pull-request-templates)
- [GitHub Projects best practices](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects)

---
name: draft-github-issue
description: "Use when asked to define, draft, or refine a GitHub Issue as Markdown for a bug, feature, or engineering task. Not for publishing issues, managing GitHub metadata, or implementing the work."
---

# Draft a GitHub Issue

Turn a request into one small, actionable issue. Return the issue in a copyable fenced Markdown block; do not create or update GitHub items, edit files, or implement the work.

## Procedure

1. Read the request, relevant repository guidance, issue templates, and task-tracking conventions when available. Use supplied context and inspect relevant code or documentation to ground the draft; do not require GitHub access.
2. Define the problem, why it matters, and the intended outcome before proposing a solution. Keep one coherent scope; name exclusions or linked follow-ups when useful. Link existing context rather than copying it.
3. Use the structure below, adapting to a relevant repository template. For bugs, include reproduction steps, expected versus actual behavior, and relevant environment or evidence when known. Distinguish observed facts from suspected causes.
4. Write observable acceptance criteria as unchecked checkboxes. Describe how to verify the result, including relevant failure cases and preservation of existing behavior. Avoid prescribing implementation details unless they are actual constraints.
5. Include dependencies, risks, priority, and a rough estimate only when useful or required locally. Do not invent facts, issue numbers, labels, deadlines, estimates, or completed checks. Mark material unknowns explicitly; if they prevent implementation, scope the issue to the investigation needed to resolve them.
6. Review for a descriptive title, bounded scope, verifiable completion, and safe disclosure. Omit secrets and private operational details, even when the intended project board is private.

## Output

Return only the issue in a fenced Markdown code block, with no preamble or commentary. Preserve Markdown syntax inside the block, including links, checkboxes, and any code examples. Use four backticks for the outer fence (or more if needed) so inner fenced examples remain intact. Use the first heading as the proposed GitHub title and the remainder as the body. Remove optional sections that add no value; replace placeholders with grounded content or explicit unknowns.

````markdown
# <Concise, specific title>

## Context and goal
<Problem, impact, intended outcome, and relevant links.>

## Scope
<Included work and meaningful exclusions.>

## Acceptance criteria
- [ ] <Observable outcome and how to verify it.>

## Planning
<Priority and rationale, rough estimate with uncertainty, or dependencies when relevant.>

## Open questions
<Material unknowns and the next step to resolve them, only when needed.>
````

## References

- [GitHub Projects best practices](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects)
- [GitHub issue templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/about-issue-and-pull-request-templates)

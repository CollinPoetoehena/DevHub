---
description: "Use when writing, updating, or verifying documentation, guides, READMEs, and Markdown examples."
applyTo: "**/*.md"
---

# Documentation Instructions

## General Guidelines

- **Terse and Succinct**: Essential details only, no verbose explanations
  - **Focus on decisions**: Record significant project-specific choices, constraints, alternatives, and consequences that cannot be inferred from the code; avoid documenting general theory or routine implementation details
  - **Link to authoritative sources**: For general knowledge like language, framework, or API details, link to the relevant official documentation instead of duplicating it; explain the project's specific usage or rationale where needed
- **Code is Truth**: Documentation must match code implementation exactly (if documenting code behavior or functionality); do not rely on assumptions or outdated knowledge
- **Fact-check Required**: Always verify documentation against actual code (including documentation that is not affected by the changes) to ensure documentation always remains accurate and up-to-date
- **Describe behavior, not edits**: Document what the code does; avoid change narration such as "I changed X, so it now does Y" or "This change now..."
- **Use authoritative sources**: When referencing external knowledge, always link to official documentation or other trusted sources rather than relying on memory or assumptions. Avoid explaining very large blocks of theory; prioritize linking to authoritative content instead
- **File references**: When referencing something from the codebase, provide a reference (e.g. [path/to/file](path/to/file)) rather than copying its content into the documentation without attribution
- **Text diagrams**: Use a small, plain-text diagram in a fenced code block when it makes a process, sequence, or component relationship materially easier to understand than prose or a list. Keep it accurate and simple; omit it when it adds little clarity or would become complex. Prefer text over a generated image such as PNG for lightweight, maintainable documentation
- **File names**: Follow general code documentation best practices for files; use descriptive, conventional names and follow the repository's existing casing and naming style. Examples include `README.md` for an overview, `GETTING-STARTED.md` for onboarding, `DEVELOPMENT.md` for local development, `DOCUMENTATION.md` for a documentation index, `GUIDELINES.md` for general guidelines, `CONTRIBUTING.md` for contribution guidance, `ARCHITECTURE.md` for system design, `API.md` for API reference, `DEPLOYMENT.md` for release and deployment steps, `RUNBOOK.md` for operational procedures, `SECURITY.md` for security policies, and `CHANGELOG.md` for release history. Avoid creating a second file for a topic already covered elsewhere; use the existing location or link to it

## Formatting Guidelines

- **Line wrapping and paragraph structure**: Avoid splitting sentences across lines unnecessarily; do not add enters mid-sentence within paragraphs. An explicit example is added below since AI often gets this wrong:
```text
Incorrect (contains mid-sentence enters):
This is a sentence 
being written
down.

Correction (no mid-sentence enters):
This is a sentence being written down.
```
- **No "Reading time" headers**: Never include estimated reading times
- **Avoid Emoji Usage**: Do not use emojis like ✅ ❌ ⚠️ for status indicators in code/examples since not all environments or readers may render them correctly
- **Plain Bullet Points**: No emoji bullets in feature lists or documentation sections, use standard markdown bullet points (`-` or `*`) instead
- **Headings & Splitting**: Use consistent heading levels and descriptive titles for sections and subsections; use `---` to separate major (level 2: `##`) sections
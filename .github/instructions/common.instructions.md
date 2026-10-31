---
description: "Apply shared engineering, testing, and documentation standards to work across DevHub projects."
applyTo: "**"
---

# Common Engineering Instructions

These standards apply across roles and projects. Follow them together with applicable technology-specific instructions and the consumer repository's AI customizations.

## Engineering

- **Focused Changes**: Make focused, complete changes that address the request without altering unrelated behavior.
- **Readability & Maintainability**: Write code that is easy to read and maintain, with clear structure and logical flow.
- **Documentation & Comments**: Code must be self-documenting with clear variable names, add inline comments only where necessary to explain non-obvious logic; avoid redundant or obvious comments. 
  - Comments explain "why", not "what", do not add comments when the code itself is easily understood.
  - **Documentation placement**: Put user-facing explanations, component designs, architecture decisions, workflows, and other high-level context in the owning README or other focused documentation, not in source code. Keep code comments and docstrings close to the code and concise: explain non-obvious intent, assumptions, edge cases, or special cases, and document public interfaces where needed. Avoid long blocks of prose in code; keep code itself clear, simple, and maintainable.
- **File Header**: Start scripts/modules with a short docstring (or language-appropriate header comment) stating their purpose, essential setup, and non-obvious assumptions or special cases; keep implementation details in the code.
- **DRY Principle**: Avoid duplication, abstract common logic into reusable constructs (e.g. functions, classes, modules, etc.). Reuse shared logic; avoid unnecessary abstractions and functionality.
- **YAGNI Principle**: Do not add functionality or abstractions that are not currently required; prefer the simplest solution that meets the task.
- **KISS Principle**: Keep It Simple, Stupid; prefer straightforward solutions over complex ones.
- **Single Responsibility & Separation of Concerns**: Keep each module or function focused, with clear naming and logical structure. Each function/module should have one clear responsibility and different concerns should be separated into distinct modules or layers.
- **Error Handling**: Clear error messages with actionable solutions. No vague "something went wrong" output.
- **Validation & Fail-fast**: Early validation of inputs with descriptive failures.
- **Consistency**: Maintain consistent coding style, naming conventions, and patterns throughout the codebase where applicable (e.g., indentation, spacing, naming schemes); avoid blindly following conventions without understanding their purpose. Read enough surrounding code and project guidance before editing. Search for existing patterns before introducing new ones.
- **Preserve Unrelated Work**: Preserve unrelated work. If existing changes conflict with the task, stop and ask rather than overwriting them.

## Testing and validation

- Treat tests and relevant validation as part of completing an implementation. Add or update meaningful tests for changed behavior and relevant edge/failure paths when the project has an established suite or the task requires it.
- Use existing test frameworks and commands. Do not add test scaffolding or tooling without a task requirement.
- Run the smallest relevant test, build, type-check, or lint command. Expand validation only when results warrant it.
- If no meaningful tests exist, do not add scaffolding or run tests by default (e.g. an Ansible role or playbook may not contain tests; adding them would be unnecessary). Report the skip and perform applicable non-test validation; follow explicit task or project requirements.
- Distinguish checks that passed, failed, were skipped, or were blocked. Never claim validation that was not performed, and report exact commands and outcomes.
- Do not use live infrastructure or expose secrets merely to validate a change.

## Documentation

- **Terse and Succinct**: Essential details only, no verbose explanations
  - **Focus on decisions**: Record significant project-specific choices, constraints, alternatives, and consequences that cannot be inferred from the code; avoid documenting general theory or routine implementation details
  - **Link to authoritative sources**: For general knowledge like language, framework, or API details, link to the relevant official documentation instead of duplicating it; explain the project's specific usage or rationale where needed
- **Code is Truth**: Documentation must match code implementation exactly
- **Fact-check Required**: Always verify documentation against actual code (including documentation that is not affected by the changes to ensure documentation always remains accurate and up-to-date)
- **Describe behavior, not edits**: Document what the code does; avoid change narration such as "I changed X, so it now does Y" or "This change now..."
- **Use authoritative sources**: When referencing external knowledge, always link to official documentation or other trusted sources rather than relying on memory or assumptions. Avoid explaining very large blocks of theory; prioritize linking to authoritative content instead.
- **File references**: When referencing something from the codebase, provide a reference (e.g. [path/to/file](path/to/file)) rather than copying its content into the documentation without attribution.
- **Text diagrams**: Actively look for opportunities to explain architecture, guidance layers, workflows, sequences, and ownership with a small plain-text diagram in a fenced code block; prefer including one when relationships or flow are central rather than relying only on prose or lists. Preserve useful diagrams when consolidating documentation: move them to the owning document and link to them instead of dropping them. Verify arrows, branches, and labels against actual behavior; distinguish optional paths from required sequences. Keep diagrams simple and maintainable, omit decorative or redundant ones, and prefer text over generated images such as PNG.
- **File names**: Follow general code documentation best practices for files; use descriptive, conventional names and follow the repository's existing casing and naming style. Examples include `README.md` for an overview, `GETTING-STARTED.md` for onboarding, `DEVELOPMENT.md` for local development, `DOCUMENTATION.md` for a documentation index, `GUIDELINES.md` for general guidelines, `CONTRIBUTING.md` for contribution guidance, `ARCHITECTURE.md` for system design, `API.md` for API reference, `DEPLOYMENT.md` for release and deployment steps, `RUNBOOK.md` for operational procedures, `SECURITY.md` for security policies, and `CHANGELOG.md` for release history. Avoid creating a second file for a topic already covered elsewhere; use the existing location or link to it.

Documentation formatting rules:

- **Line wrapping**: Avoid awkward source line breaks that leave short fragments mid-sentence. Wrap prose at natural phrase or clause boundaries, and indent continuation lines in list items.
- **No "Reading time" headers**: Never include estimated reading times
- **Avoid Emoji Usage**: Do not use emojis like ✅ ❌ ⚠️ for status indicators in code/examples since not all environments or readers may render them correctly
- **Plain Bullet Points**: No emoji bullets in feature lists or documentation sections, use standard markdown bullet points (`-` or `*`) instead
- **Headings & Splitting**: Use consistent heading levels and descriptive titles for sections and subsections; use `---` to separate major (level 2: `##`) sections
- **Table of Contents**: Include a table of contents for longer documentation files to improve navigation. List headings from levels `##` through `####` only; do not include headings below level `####`. Skip the table of contents for very short documentation files and for Copilot instruction files like `copilot-instructions.md`.

## Applicable instructions

- Read and follow this common instruction file for work across roles.
- Also follow matching technology-, tool-, task-, or file-specific instructions from this package and the consumer project (if applicable).
- Follow the consumer repository's standard AI customizations, such as `copilot-instructions.md`, `AGENTS.md`, or host-specific equivalents, as supported by the active harness. These sources supplement one another; do not assume one automatically overrides another. Surface material conflicts rather than silently choosing.

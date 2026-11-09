---
description: "Use for all engineering/code work: follow these coding instructions to ensure consistency, quality, and maintainability."
applyTo: "**"
---

# Coding Instructions

## Immutability (CRITICAL)

ALWAYS create new objects, NEVER mutate existing ones:

```
// Pseudocode
WRONG:  modify(original, field, value) → changes original in-place
CORRECT: update(original, field, value) → returns new copy with change
```

Rationale: Immutable data prevents hidden side effects, makes debugging easier, and enables safe concurrency.

## Core Principles

### KISS (Keep It Simple)

- Prefer the simplest solution that actually works
- Avoid premature optimization
- Optimize for clarity over cleverness

### DRY (Don't Repeat Yourself)

- Extract repeated logic into shared functions or utilities
- Avoid copy-paste implementation drift
- Introduce abstractions when repetition is real, not speculative

### YAGNI (You Aren't Gonna Need It)

- Do not build features or abstractions before they are needed
- Avoid speculative generality
- Start simple, then refactor when the pressure is real

## File Organization

MANY SMALL FILES > FEW LARGE FILES:
- High cohesion, low coupling
- 200-400 lines typical, with 800 lines as a soft maintainability ceiling for source files
- Test, generated, and vendored files may exceed the ceiling when their size is justified by their role
- Extract utilities from large modules
- Organize by feature/domain, not by type
- Avoid flat project structures; prefer organizing by feature or domain.

## Error Handling

ALWAYS handle errors comprehensively:
- Handle errors explicitly at every level
- Provide user-friendly error messages in UI-facing code
- Log detailed error context on the server side
- Never silently swallow errors

## Observability and Logging

- Log meaningful operational boundaries, significant events, and failures when they provide diagnostic value—not every function or line.
- Follow project logging conventions and established language facilities, such as Python `logging` or Go `log/slog`; do not require a particular logger or dependency.
- Use appropriate severity and structured, actionable context, including correlation identifiers where available.
- Avoid duplicate failure logs, excessive verbosity, and logs without diagnostic value.
- Never log secrets, tokens, passwords, or unnecessary personal data; follow the [Security Instructions](security.instructions.md).

## Input Validation

ALWAYS validate at system boundaries:
- Validate all user input before processing
- Use schema-based validation where available
- Fail fast with clear error messages
- Never trust external data (API responses, user input, file content)

## Naming Conventions

> **Language note**: This rule may be overridden by language-specific rules for languages where a pattern is not idiomatic. Casing and framework-specific prefixes belong to the applicable language or package rule.

Language-independent:

- Descriptive names: the name says what the thing holds or does, without a comment.
- Boolean names read clearly as claims under the applicable language or package convention.
- Where the language draws the distinction, constants and types are visually distinct from ordinary values in the form its language or package rule defines.

## Code Smells to Avoid

- **Deep Nesting**: Prefer early returns over nested conditionals once the logic starts stacking.
- **Magic Numbers**: Use named constants for meaningful thresholds, delays, and limits.
- **Long Functions**: Split large functions into focused pieces with clear responsibilities.

## Comments

- Add, edit, review, and remove code comments, doc comments, docstrings, markers, and suppressions with the [code-comments skill](../skills/code-comments/SKILL.md); the default is no comment.

## Code Quality Checklist

Before marking work complete:
- [ ] Code is readable and well-named
- [ ] Functions are small (approximately <50 lines)
- [ ] Files are focused (approximately <800 lines)
- [ ] No deep nesting (>4 levels)
- [ ] Proper error handling
- [ ] No hardcoded values (use constants or config where applicable)
- [ ] No mutation (immutable patterns used)

## Related Instructions

- **Documentation:** [documentation instructions](documentation.instructions.md) for Markdown, READMEs, and guides.
- **Security:** [security instructions](security.instructions.md) for untrusted content, secrets, and secure defaults.
- **Git:** [Git instructions](git.instructions.md) for commits and history.
- **Languages and tools:** the instructions of the opt-in stack packages, such as Python, Go, Java, containerization, and infrastructure as code, refine these rules for their files.

When instructions conflict, the most specific scope wins: the repository's own configuration and `AGENTS.md`, then language and tool instructions, then these common instructions.

---
description: "Use for all engineering work: load applicable guidance, preserve scope and unrelated work, validate outcomes, and report evidence honestly."
applyTo: "**"
---

# Common Engineering Instructions

- Resolve and read this baseline, applicable scoped instructions, repository entry guidance, and relevant owning documentation before work. Do not assume linked files or subagent context are loaded. Report missing required guidance and material conflicts instead of guessing precedence.
- Make focused, complete changes; preserve unrelated work and intended behavior. Inspect surrounding code, callers, contracts, and existing patterns before editing. Stop on conflicting user changes.
- Prefer the simplest reliable solution. Reuse existing helpers; avoid unnecessary abstractions, dependencies, and configuration. Keep modules and functions focused, names clear, and types sound.
- Fail early with actionable errors. Do not hide failures, invent defaults, expose secrets, or use live infrastructure merely to validate.
- Keep code self-documenting. Use concise purpose headers for scripts/modules and comments only for non-obvious intent or assumptions. Put user-facing design and workflow explanations in the owning documentation, not in the code. Keep code comments and docstrings close to the code and concise: explain non-obvious intent, assumptions, edge cases, or special cases, and document public interfaces where needed. Avoid long blocks of prose in code; keep code itself clear, simple, and maintainable.
- Update directly related documentation and verify affected claims against implementation. Use the [documentation instructions](documentation.instructions.md) for documentation work.
- Use existing tests and tooling; cover changed behavior and relevant edge/failure paths when a suite exists or the task requires tests. Run the smallest relevant check and expand only when necessary.
- If meaningful tests do not exist, do not add scaffolding by default. Explain the skip and perform applicable non-test checks. Documentation-only work needs no application tests unless documentation tests exist.
- Record exact commands and passed, failed, skipped, or blocked outcomes. Explain skips and verification limits; never claim checks, reviews, deployment, commits, or pushes without evidence.
- Commit and push are distinct actions requiring explicit authorization. Preserve unrelated staged work; do not bypass approvals, hooks, or policy.

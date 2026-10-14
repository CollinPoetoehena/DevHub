# Copilot Instructions

> **Official documentation:** [Adding repository custom instructions for GitHub Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions) and [custom instructions in VS Code](https://code.visualstudio.com/docs/agent-customization/custom-instructions).
>
> The rest of this page is DevHub-specific guidance that supplements those docs. Consult the official documentation for supported formats and behavior.

Start with the shared [Create and maintain customizations](../AI.md#create-and-maintain-customizations) guidance, especially [self-contained instructions](../AI.md#keep-each-customization-self-contained). This page adds instruction-specific locations, scope, and examples. See [Personal preferences and workplace reuse](../AI.md#personal-preferences-and-workplace-reuse) for why project-specific instructions should complement, not duplicate, the generic collection.

## Table of contents

- [Where instructions belong](#where-instructions-belong)
- [What to include](#what-to-include)

---

## Where instructions belong

Use instructions for recurring rules and context, not a multi-step task workflow.

- Repository-wide Copilot guidance belongs in `.github/copilot-instructions.md` at the root of the repository.
- Path-specific guidance belongs in `*.instructions.md` files under `.github/instructions/`, with supported `applyTo` frontmatter to scope it to matching files.
- Some Copilot environments also support `AGENTS.md`; it is an instruction format and is not the same as a custom agent definition.

The `.github/instructions/` directory is only needed for path-specific instruction files. It is not required for repository-wide instructions. This README documents the DevHub convention; it is not itself an instructions file.

---

## What to include

Keep instruction files concise, stable, and useful for the scope they cover. Include verified project context, standards, architecture constraints, and reliable build or validation commands. Put detailed, repeatable procedures in a skill instead. Do not put credentials or other secrets in instructions.

Example repository-wide guidance:

```markdown
# Repository guidance

- Follow the existing architecture and conventions in this repository.
- Use the documented project commands to build and test changes.
- Update directly affected documentation when behavior changes.
```

Example path-specific guidance:

```markdown
---
applyTo: "**/*.py"
---

Use the project's configured formatter and type checker for Python changes.
```

Review instructions against the target repository and selected Copilot host; supported formats and behavior can vary.

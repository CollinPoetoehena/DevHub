---
description: "Use when designing or maintaining AI agents, skills, prompts, and instruction files."
applyTo: "**/*.agent.md,**/*.instructions.md,**/*.prompt.md,**/SKILL.md,**/AGENTS.md,**/copilot-instructions.md"
---

# AI Customization Design

- Be concise: capture the essence, triggers, boundaries, and expected outcome. Do not write enormous prompts or duplicate guidance already supplied by another primitive.
- Use agents for role identity, responsibilities, boundaries, and workflow. Put shared engineering standards in the common instructions; use scoped instructions for technology-, tool-, task-, or project-specific constraints. Use skills for on-demand procedures.
- Inspect existing customizations before adding another. Extend an appropriate existing primitive rather than creating overlapping triggers or conflicting rules.
- Use specific descriptions for discovery and narrow `applyTo` globs for file instructions. Give skills valid names matching their directories.
- Keep detailed resources separate and load them only when needed. Add scripts, templates, or reference files only when they serve the workflow.
- Check current official documentation for supported frontmatter, locations, and invocation behavior; link to it instead of reproducing it. Do not promise deterministic compliance or unsupported precedence.
- Validate frontmatter, resource links, scope, and host discovery. Treat tool restrictions and instruction text as different mechanisms.

References: [VS Code customization](https://code.visualstudio.com/docs/agent-customization/overview), [agents](https://code.visualstudio.com/docs/agent-customization/custom-agents), [skills](https://code.visualstudio.com/docs/agent-customization/agent-skills), [instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions), [APM primitives](https://microsoft.github.io/apm/producer/author-primitives/).

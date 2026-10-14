# AI Customizations

This page is a generic guide to the main kinds of AI customizations: what they are for, how to choose among them, and how to reuse them across repositories. For supported product-specific formats and behavior, follow the official documentation linked from the relevant [instructions](./instructions/README.md), [skills](./skills/README.md), or [agents](./agents/README.md) guide.

Return to the [shared GitHub customizations overview](./OVERVIEW.md) for other topics.

## Table of contents

- [Which customization should I use?](#which-customization-should-i-use)
- [General design principles](#general-design-principles)
- [Use external or centralized customizations across repositories](#use-external-or-centralized-customizations-across-repositories)
  - [Copy into a repository or personal location](#copy-into-a-repository-or-personal-location)
  - [Keep a centralized local source](#keep-a-centralized-local-source)
- [Examples beyond DevHub](#examples-beyond-devhub)

---

## Which customization should I use?

Start with the smallest thing that solves the problem. A one-off prompt may be all you need.

| Customization | What it is for | Typical use |
| --- | --- | --- |
| Instructions | Persistent rules, preferences, or project context | Coding standards or architecture facts that should apply repeatedly |
| Skill | Reusable know-how, task instructions, or repeatable processes and workflows | A recurring task or multi-step process with consistent steps, constraints, or supporting resources |
| Prompt file (legacy) | A saved request or template invoked manually | Existing prompt files; use skills for new reusable tasks and processes |
| Agent | A specialized role with its own instructions and, where supported, tool configuration | A recurring specialist such as a planner, reviewer, or documentation assistant |
| MCP server | A connection that exposes tools or context from another system | Letting an AI interact with an external service |
| Hook | An action triggered at a defined point in an agent lifecycle | Enforcing or automating a command at a configured lifecycle event |

These mechanisms can overlap, but they solve different problems: instructions express rules, skills teach a task, prompts package a request, agents define a role, MCP servers provide capabilities, and hooks run configured actions. The availability and activation behavior of each feature depends on the AI product and host.

> **Use skills instead of prompt files:** For new DevHub customizations, do not create `.prompt.md` files; use skills for reusable task instructions and repeatable processes, including multi-step workflows. Skills are not limited to specialized knowledge or bundled scripts. The [VS Code prompt file documentation](https://code.visualstudio.com/docs/agent-customization/prompt-files) states that prompt files are deprecated and are not loaded in Agent Host sessions; they continue to work with the Local agent for now. [Migrate existing prompt files to skills](https://code.visualstudio.com/docs/agent-customization/migrate-customizations#_convert-prompt-files-to-skills). This recommendation concerns saved prompt files, not ordinary one-off chat prompts.

---

## General design principles

- Add a customization when it meaningfully improves quality, speed, or consistency enough to justify its creation and maintenance.
- Keep customizations focused, current, and appropriate to their audience.
- Keep task-specific input in the request; reusable guidance should not assume that every repository or user has the same context.
- Design reusable skills and agents to discover project instructions, structure, conventions, and commands automatically, searching beyond common locations when needed. This avoids per-repository configuration and asking users to repeat information already available in their project. Users still supply goals, unresolved decisions, and required authorization; discovery does not replace consent or justify guessing. Report the files used and any discovery limitations.
- A model instruction is guidance, not a security boundary or an enforcement mechanism by itself.
- Refer to the product's official documentation for supported formats, locations, activation, and capabilities.

For a broader comparison of customization types, see the [VS Code customization overview](https://code.visualstudio.com/docs/agents/concepts/customization).

---

## Use external or centralized customizations across repositories

This is the central place for cross-repository setup guidance. The approach is similar for agents, skills, and other file-based customizations; the specific file or directory to install and its supported discovery location differ. The individual guides describe how to create and use each type rather than repeating these setup steps.

A Markdown link to a customization is for discovery and reading; it does **not** install or activate it in another workspace. Review external content and any bundled scripts before adopting it, and check that its assumptions suit the consuming repository.

For Copilot, the following locations are documented by the official [custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents#_custom-agent-file-locations) and [Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills) guides:

| Type | What to install | Consuming repository | Personal use across repositories |
| --- | --- | --- | --- |
| Agent | The `.agent.md` file and any resources it references | `.github/agents/` | `~/.copilot/agents/` |
| Skill | The complete skill directory, including `SKILL.md` and supporting resources | `.github/skills/` | `~/.copilot/skills/` |

These are Copilot locations, not universal paths for every host or customization type. Check the selected product and harness documentation for supported discovery locations and activation behavior. For remote or Agent Host sessions, use locations on the machine where the agent runs, not necessarily your local desktop.

> **Automatic setup:** For automatic personal setup, use the central [DevHub installer](../install/README.md). It installs skills and agents from an isolated temporary checkout, keeps persistent managed snapshots, and supports checking for GitHub updates at shell login without touching development clones. See that guide for trust implications, conflict handling, and supported platforms. The manual options below remain useful for repository-local sharing or choosing a reviewed checkout.

### Copy into a repository or personal location

Clone DevHub (or another reviewed customization repository), then copy the desired items. For example, run these commands from the consuming repository root:

```sh
mkdir -p .github/agents .github/skills
cp /path/to/DevHub/.github/agents/devhub-code-reviewer.agent.md .github/agents/
cp -R /path/to/DevHub/.github/skills/devhub-docs .github/skills/
```

Replace `/path/to/DevHub` with your local clone path and the example names with the desired customizations. Copy any resources referenced by an agent as well, preserving its relative paths. Commit repository-local copies to share them with contributors.

For personal use across repositories without adding files to each project, copy to the user-level locations instead:

```sh
mkdir -p ~/.copilot/agents ~/.copilot/skills
cp /path/to/DevHub/.github/agents/devhub-code-reviewer.agent.md ~/.copilot/agents/
cp -R /path/to/DevHub/.github/skills/devhub-docs ~/.copilot/skills/
```

A copy is a snapshot: review and copy it again to adopt upstream changes. Avoid overwriting an existing customization without reviewing local adaptations.

> **Tip:** If your system supports symbolic links, you can use them to keep a centralized local source for your customizations instead of maintaining multiple copies (see [Keep a centralized local source](#keep-a-centralized-local-source)). This is the recommended approach for managing local customizations efficiently because you can update the source once (e.g. `git pull`) and have all linked locations reflect the changes automatically.

### Keep a centralized local source

If your selected host supports discovering customizations through symbolic links, you can keep one reviewed clone as the source instead of maintaining copies. For example, on Linux or macOS:

```sh
mkdir -p ~/.copilot/agents ~/.copilot/skills
ln -s /path/to/DevHub/.github/agents/devhub-code-reviewer.agent.md ~/.copilot/agents/devhub-code-reviewer.agent.md
ln -s /path/to/DevHub/.github/skills/devhub-docs ~/.copilot/skills/devhub-docs
```

Use absolute source paths and ensure the destinations do not already exist. Keep the clone at that path; moving or deleting it breaks the links. Changes in the clone affect every workspace using those links, so review upstream updates before pulling them. Agents with supporting resources need those resources accessible at the expected paths too.

Symbolic-link discovery depends on the host and environment; verify that the agent appears in the agent picker or that the skill is discoverable. If links are unsupported, use copies instead (see [Copy into a repository or personal location](#copy-into-a-repository-or-personal-location)). Personal paths and local links are machine-specific: they do not install customizations for collaborators or a cloud agent. Use repository-local copies when those environments need the same customizations.

---

## Examples beyond DevHub

For generic Copilot customizations and examples—including agents, skills, instructions, and prompts—see [github/awesome-copilot](https://github.com/github/awesome-copilot) and the [awesome-copilot community library](https://awesome-copilot.github.com/); these are curated collections of community-contributed resources in the official GitHub repository. Review the customization content and any bundled scripts before adopting them.

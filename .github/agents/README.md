# Custom Agents

> **Official documentation:** [Custom agents in VS Code](https://code.visualstudio.com/docs/agent-customization/custom-agents).
>
> The rest of this page describes DevHub's conventions and examples; follow the official documentation for the supported file format, locations, and host-specific behavior.

## Table of contents

- [DevHub agents](#devhub-agents)
- [Use an agent](#use-an-agent)
  - [Use agents in other repositories](#use-agents-in-other-repositories)
- [Create a repository agent](#create-a-repository-agent)
- [Examples beyond DevHub](#examples-beyond-devhub)

---

## DevHub agents

DevHub's repository custom agents are stored in this folder:

- [`devhub-code-reviewer.agent.md`](./devhub-code-reviewer.agent.md) — reviews changes and reports actionable findings without implementing fixes.
- [`devhub-documentation-specialist.agent.md`](./devhub-documentation-specialist.agent.md) — helps create, improve, and review documentation.
- [`devhub-architect.agent.md`](./devhub-architect.agent.md) — analyzes system structure and develops repository-grounded architecture recommendations.

They are examples of focused roles, not globally applicable rules. Reuse or adapt them only when they suit the consuming repository and task.

---

## Use an agent

In VS Code, open the Chat view, choose the intended custom agent from the agent/Chat mode picker, and then describe the task you want it to handle. Include relevant goals, scope, constraints, and context; the agent supplies its reusable role guidance, but it does not know task-specific requirements you have not provided. For example:

- Select **DevHub Architect** ([`.github/agents/devhub-architect.agent.md`](./devhub-architect.agent.md)) to analyze a system or design and provide a repository-grounded recommendation.
- Select **DevHub Documentation Specialist** ([`.github/agents/devhub-documentation-specialist.agent.md`](./devhub-documentation-specialist.agent.md)) to create or review documentation.
- Select **DevHub Code Reviewer** ([`.github/agents/devhub-code-reviewer.agent.md`](./devhub-code-reviewer.agent.md)) to review changes and report findings without implementing fixes.

Workspace agents are available when you open the repository in a Copilot host that supports their location and format. The exact picker steps and support vary by host; see the official [Custom agents in VS Code](https://code.visualstudio.com/docs/agent-customization/custom-agents) guide for using, managing, and troubleshooting them.

### Use agents in other repositories

See [Use external or centralized customizations across repositories](../AI.md#use-external-or-centralized-customizations-across-repositories) for repository-local installation, personal use across workspaces, and a centralized local source. Install the desired `.agent.md` file and any referenced resources in the supported agent location, then select the agent in the consuming workspace.

---

## Create a repository agent

For requests to create or maintain a DevHub skill or custom agent, use the [`devhub-create-ai-customization` skill](../skills/devhub-create-ai-customization/SKILL.md). The guidance below is general agent-design context; the skill adds the DevHub-specific workflow and requirements.

For a DevHub agent, add a Markdown file here using a `.agent.md` suffix. Give it a clear role name and description in its supported YAML frontmatter, then write role-specific instructions in the body. Use a `devhub-` prefix in the filename and agent name for DevHub-maintained agents.

Define the agent's responsibilities, boundaries, relevant context, and expected response. If the role should not edit files, say so and, where the host supports it, restrict its tools to inspection. Instructions alone do not technically prevent file changes.

Avoid creating an agent for every task variation. Use a skill for a repeatable task workflow and instructions for persistent repository rules. Keep the role self-contained; do not require it to invoke a particular skill.

Include automatic discovery of project instructions, documentation, structure, and relevant configuration, with a broader repository search when common locations are insufficient. This lets the same role work across repositories without making users supply discoverable paths or conventions. Users still provide goals, unresolved decisions, and authorization. Have the agent report which files informed its guidelines and structural understanding, and state any discovery limitations rather than inventing missing context.

The supported file locations and available frontmatter options can differ across Copilot hosts. Verify them in the official documentation before using options beyond the basic name and description.

---

## Examples beyond DevHub

For generic Copilot customizations and examples—including agents, skills, instructions, and prompts—see [github/awesome-copilot](https://github.com/github/awesome-copilot) and the [awesome-copilot community library](https://awesome-copilot.github.com/). Review the customization content and any bundled scripts before adopting them.

---
name: devhub-create-ai-customization
description: "Create or maintain a self-contained GitHub Copilot skill or custom agent for DevHub. Use when asked to create or improve a reusable skill or agent."
---

> **Maintenance note for users:** This skill is maintained in [DevHub](https://github.com/CollinPoetoehena/DevHub/blob/main/.github/skills/devhub-create-ai-customization/SKILL.md). This is provenance information only; AI agents do not need to follow the link to use the skill.

# Create a DevHub Skill or Custom Agent

Create exactly the requested kind of GitHub Copilot customization: either an Agent Skill or a custom agent. Do not create both unless asked. Keep the result useful outside one specific project unless the request explicitly requires project-specific context.

## Decide Whether It Adds Value

1. Identify the repeated problem and the intended users.
2. Prefer a direct prompt for one-off work. Create a customization only when reuse meaningfully improves quality, speed, or consistency enough to justify authoring and maintenance.
3. Avoid a new customization for every small task or variation. Combine closely related tasks when they share a process; split only where differences materially change the role or workflow.
4. Keep each skill self-contained. Do not instruct a skill to find, invoke, or depend on another skill: supported Copilot experiences do not provide a reliable skill-to-skill invocation contract. Informational links are fine, but include all required task steps and constraints in the skill itself. Limited duplication is preferable to an unreliable dependency chain.

## Design for Automatic Context Discovery

Use automatic discovery as much as possible, both while authoring a customization and in the workflow or role instructions you create. This keeps customizations reusable across repositories without requiring users to supply project-specific paths, conventions, commands, or custom configuration that the AI can discover itself.

1. Discover the owning repository or package and read applicable instructions, including `AGENTS.md`, `.github/copilot-instructions.md`, and relevant `.github/instructions/*.instructions.md`. Inspect the existing customization and nearby examples when updating one.
2. Look for `README.md`, `CONTRIBUTING.md`, architecture, development, testing, and style guides; relevant `docs/`, `doc/`, `documentation/`, `reference/`, and package-local content; manifests, tool configuration, build scripts, and CI workflows. Use actual content to establish project structure, commands, and conventions.
3. Treat common filenames and locations as starting points, not requirements. If they do not reveal the needed context, inspect the repository layout, search relevant filenames and contents, and follow existing entry-point links. Keep exploration scoped and respect access restrictions.
4. Encode the same discovery behavior in each resulting skill or agent, tailored to its task. Avoid hard-coded consuming-project paths, mandatory user-supplied guideline files, and setup parameters that can be inferred reliably from repository evidence. Keep DevHub authoring locations distinct from assumptions about consuming projects.
5. Do not invent missing context or treat discovered commands as permission to execute them. Preserve safety boundaries and ask for goals, material decisions, authorization, or inaccessible information only when these cannot be established safely through discovery.
6. Require completion reports to identify the files actually used for guidelines and structure, their roles, inferred conventions, and missing guidance. Do not claim discovery will always succeed or report unread files as evidence.

## Create a Skill

For DevHub, put each skill in `.github/skills/devhub-<short-name>/SKILL.md`.

1. Use a lowercase, hyphenated `devhub-` prefixed directory and matching YAML `name`.
2. Include the required `name` and a concise `description` that says what the skill does and when Copilot should use it.
3. Write a focused procedure in the Markdown body. Include the goal, scope, relevant inputs, safety constraints, validation, and expected output as needed for that task.
4. Include task-appropriate automatic discovery of the consuming project's instructions, structure, policies, and commands as described above, rather than requiring users to supply discoverable context.
5. Keep the skill self-contained. It may link to authoritative documentation or project-provided guidelines as optional context, but it must not require another skill or a remote URL as a substitute for an installed workflow.
6. Add scripts or supporting resources only when they materially help the skill; keep them inside its directory and explain their use.
7. For every DevHub-maintained skill, place this user-facing note immediately after the YAML frontmatter, before the title. Replace `<skill-name>` with the actual directory name so the URL points to that exact skill file, not the repository homepage. Keep the frontmatter first so skill discovery remains valid. The link is provenance, not required reading or a workflow dependency:

   > **Maintenance note for users:** This skill is maintained in [DevHub](https://github.com/CollinPoetoehena/DevHub/blob/main/.github/skills/<skill-name>/SKILL.md). This is provenance information only; AI agents do not need to follow the link to use the skill.

## Create a Custom Agent

For DevHub, put a repository custom agent in `.github/agents/devhub-<short-role>.agent.md`.

1. Give it a concise role-focused `name` and `description`.
2. Explain the role, task boundaries, relevant context to inspect, expected behavior, and response format in the body.
3. Configure tool access only when the target Copilot host supports it and the role benefits from a narrower tool set. Clearly distinguish requested behavior from an enforced restriction.
4. Do not make an agent depend on a skill being invoked. State the necessary role guidance directly in the agent, include task-appropriate automatic context discovery, and let the user supply the objective and any context that cannot be discovered.
5. For every DevHub-maintained agent, place this user-facing note immediately after the YAML frontmatter. Replace `<agent-filename>` with the actual filename, including `.agent.md`, so the URL points to that exact agent file:

   > **Maintenance note for users:** This agent is maintained in [DevHub](https://github.com/CollinPoetoehena/DevHub/blob/main/.github/agents/<agent-filename>). This is provenance information only; AI agents do not need to follow the link to use the agent.

## Update Existing Customization Lists

Automatically discover any existing catalog, index, or README that lists the project's skills or agents. In DevHub, these lists are in `.github/skills/README.md` and `.github/agents/README.md`; other repositories may use different locations.

- Add each new skill or agent to the appropriate existing list with a working relative link and a concise description, following its ordering and formatting conventions.
- When renaming, moving, or changing a customization's purpose, update its existing entry and directly affected references rather than adding a duplicate or leaving stale links.
- If no list exists after discovery, report that fact; do not create a new catalog unless requested or required by project guidance.

## Check the Result

- Confirm the file is in the requested kind's supported location, with correct extension and valid YAML frontmatter.
- Confirm the skill directory and its `name` match and begin with `devhub-`.
- Confirm every DevHub-maintained skill or agent has the user-facing maintenance note after its frontmatter, linking to its exact source file with no unresolved placeholders, without making the link required reading.
- Ensure the description makes intended activation clear, the content is focused, and there are no required skill-to-skill links or unsupported assumptions.
- Verify that automatic discovery is explicit, includes a fallback beyond common locations, and does not require unnecessary project-specific user inputs. Confirm the report identifies the project files actually used and discovery limitations.
- Confirm any existing customization lists and directly affected links are current, and include updated indexes or the absence of a list in the completion report.
- Follow current official documentation for details that depend on a particular Copilot host:
  - [Creating and adding a skill](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills#creating-and-adding-a-skill)
  - [Custom instructions in VS Code](https://code.visualstudio.com/docs/agent-customization/custom-instructions)
  - [Custom agents in VS Code](https://code.visualstudio.com/docs/agent-customization/custom-agents)
- Report the created or updated file and any host-specific behavior that remains unverified.

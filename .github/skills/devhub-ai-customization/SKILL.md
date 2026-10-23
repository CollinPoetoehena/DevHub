---
name: devhub-ai-customization
description: "Create or maintain a self-contained GitHub Copilot skill or custom agent for DevHub. Use when asked to create, update, rename, or improve a reusable skill or agent."
---

> **Maintenance note for users:** This skill is maintained in [DevHub](https://github.com/CollinPoetoehena/DevHub/blob/main/.github/skills/devhub-ai-customization/SKILL.md). This is provenance information only; AI agents do not need to follow the link to use the skill.

> **Invocation-specific instructions take precedence:** Follow explicit directions in the current skill invocation or accompanying request over conflicting defaults or procedures in this skill. For example, if the request limits which customizations to update, honor that scope rather than applying this workflow's broader defaults. This does not override higher-priority system or developer instructions, host constraints, or applicable safety requirements.

# Create and Maintain DevHub Skills and Custom Agents

Create or maintain exactly the requested kind of GitHub Copilot customization: either an Agent Skill or a custom agent. Do not create or update both unless asked. Keep the result useful outside one specific project unless the request explicitly requires project-specific context.

---

## Decide Whether It Adds Value

1. Identify the repeated problem and the intended users.
2. Prefer a direct prompt for one-off work. Create a customization only when reuse meaningfully improves quality, speed, or consistency enough to justify authoring and maintenance.
3. Avoid a new customization for every small task or variation. Combine closely related tasks when they share a process; split only where differences materially change the role or workflow.
4. Keep instructions, skills, and agents self-contained. Include the essential rules, workflow, and context in the customization itself; do not rely on another customization, a Git-hosted file, external documentation, or another URL to supply required material. Links may provide optional background, but the customization must remain usable if linked material is unavailable. If a skill needs supplemental resources, keep them in its own directory and explain when to use them; otherwise put the content directly in the skill or agent. Do not require a skill to find or invoke another skill: supported Copilot experiences do not provide a reliable skill-to-skill invocation contract. Limited duplication is preferable to an expanding, unreliable dependency chain. Use AI to maintain duplicated guidance consistently across skills when it changes, then review the full diff and confirm each skill still stands on its own; AI assistance does not replace human review.
5. DevHub is a personal collection usable for personal projects and at work where policy permits; generic workflows discover and follow the consuming project's requirements rather than impose personal preferences. Prefer project-specific additions over duplicating generic workflows. A separate team-generic collection is optional and adds maintenance; create one only when real shared differences justify it.

---

## Design for Automatic Context Discovery

Use automatic discovery as much as possible, both while authoring a customization and in the workflow or role instructions you create. This keeps customizations reusable across repositories without requiring users to supply project-specific paths, conventions, commands, or custom configuration that the AI can discover itself.

1. Discover the owning repository or package and read applicable instructions, including `AGENTS.md`, `.github/copilot-instructions.md`, and relevant `.github/instructions/*.instructions.md`. Inspect the existing customization and nearby examples when updating one.
2. Look for `README.md`, `CONTRIBUTING.md`, architecture, development, testing, and style guides; relevant `docs/`, `doc/`, `documentation/`, `reference/`, and package-local content; manifests, tool configuration, build scripts, and CI workflows. Use actual content to establish project structure, commands, and conventions.
3. Treat common filenames and locations as starting points, not requirements. If they do not reveal the needed context, inspect the repository layout, search relevant filenames and contents, and follow existing entry-point links. Keep exploration scoped and respect access restrictions.
4. Encode the same discovery behavior in each resulting skill or agent, tailored to its task. Avoid hard-coded consuming-project paths, mandatory user-supplied guideline files, and setup parameters that can be inferred reliably from repository evidence. Keep DevHub authoring locations distinct from assumptions about consuming projects.
5. Do not invent missing context or treat discovered commands as permission to execute them. Preserve safety boundaries and ask for goals, material decisions, authorization, or inaccessible information only when these cannot be established safely through discovery.
6. Require completion reports to identify the files actually used for guidelines and structure, their roles, inferred conventions, and missing guidance. Do not claim discovery will always succeed or report unread files as evidence.

---

## Create a Skill

For DevHub, put each skill in `.github/skills/devhub-<short-name>/SKILL.md`.

1. Use a lowercase, hyphenated `devhub-` prefixed directory and matching YAML `name`.
2. Include the required `name` and a concise `description` that says what the skill does and when Copilot should use it.
3. Write a focused procedure in the Markdown body. Include the goal, scope, relevant inputs, safety constraints, validation, and expected output as needed for that task.
4. Include task-appropriate automatic discovery of the consuming project's instructions, structure, policies, and commands as described above, rather than requiring users to supply discoverable context.
5. Include all essential task guidance directly in the skill. Do not require another customization, a file hosted on Git, external documentation, or another URL to provide steps, rules, or context needed to perform the task. Links may offer optional background only.
6. Add scripts or supporting resources only when they materially help the skill; keep them inside its directory, explain their use, and make clear how they contribute to the self-contained workflow.
7. For every DevHub-maintained skill, place this user-facing note immediately after the YAML frontmatter, before the title. Replace `<skill-name>` with the actual directory name so the URL points to that exact skill file, not the repository homepage. Keep the frontmatter first so skill discovery remains valid. The link is provenance, not required reading or a workflow dependency:

   > **Maintenance note for users:** This skill is maintained in [DevHub](https://github.com/CollinPoetoehena/DevHub/blob/main/.github/skills/<skill-name>/SKILL.md). This is provenance information only; AI agents do not need to follow the link to use the skill.

8. For every skill you create or maintain, add an invocation-specific precedence note near the top, immediately after its maintenance note when it has one. State that explicit directions in the current invocation or accompanying request override conflicting skill defaults or procedures, give an example such as honoring a request to skip tests, and clarify that higher-priority instructions, host constraints, and safety requirements still apply.
9. Use AI to create and maintain skills, including applying updates consistently to duplicated essential guidance when shared requirements change. This keeps self-contained skills practical to maintain. Review the complete diff, verify accuracy and independence in each affected skill, and run relevant checks; do not treat AI-generated edits as approved without review.

10. Include a self-contained completion-report requirement in every skill you create or update: for file changes in a Git repository, end the report with a copy-ready `sh` block containing `git add -A && git commit` with a concrete task-specific message, followed by `&& git push`. Do not add a co-author trailer. Follow the consuming repository's commit conventions. Inspect the branch and upstream; if no upstream exists, use `git push --set-upstream` with a verified remote and current branch. Do not leave placeholders or invent a push target. Before the block, warn that `git add -A` stages all changes, including unrelated edits, and ask the user to review the diff. Provide commands for the user, not permission to execute them: never commit or push unless explicitly requested. If no files changed, the task is outside Git, or a safe sequence is blocked, explain why the commands are omitted or incomplete.

11. Require the skill to inspect `git diff`, `git diff --cached`, and `git status --short`, and review relevant untracked files before composing the commit message. The message must describe the complete pending change set that `git add -A` will stage, including earlier session changes, not just the latest task or the AI's own edits. Require it to flag unrelated or unreviewed changes without claiming ownership or validation of others' work.

---

## Authoring Change Skills

Near the top of every change skill, immediately after its title, include: "Act as a senior software engineer working in the current repository." This establishes the expected engineering judgment: understand context, address root causes, preserve compatibility, keep changes maintainable, and verify outcomes within the requested scope.

When creating or maintaining a code-change skill, include the following guidance directly in that skill rather than requiring another skill to supply it. The documentation rules are generic programming-language guidance for Python, Go, and other code, not YAML-specific requirements. Keep the generic change skill the most detailed treatment; give specialized skills concise, language-appropriate rules.

1. Require concise file-purpose documentation at the top of new or materially changed source files when missing or inaccurate, using native module docstrings or header comments. Preserve shebangs, encoding declarations, licenses, generated markers, and language/tool directives in their required positions. Exclude generated and vendored files from comment-only edits.
2. Require native function/method docstrings or declaration comments for new and materially changed contracts, explaining relevant inputs, outputs, errors, side effects, and constraints. Python uses a first-statement docstring; Go uses comments before declarations. Do not force redundant boilerplate on trivial private helpers or add fake docstrings to YAML/HCL.
3. Reserve inline comments for special, non-obvious reasoning, edge cases, workarounds, ordering, and trade-offs. Explain why rather than narrating obvious code; prefer clear code over explanatory clutter.
4. Decide documentation length from complexity, audience, risk, and local style, not a fixed line count. Keep simple summaries short and expand for subtle contracts; update stale comments with code. Use existing documentation checks without adding unnecessary tooling.
5. Preserve each skill's self-contained discovery, safety, validation, and reporting. Tailor tests and compatibility checks to the language and actual project setup, rather than merely renaming the generic skill.
6. For YAML, HCL, templates, and similar configuration formats, make comments optional based on the current file and project conventions. Do not impose the source-code file-header requirement: an uncommented file may remain uncommented. Maintain useful existing comments and native descriptions; add comments only where they provide meaningful clarification.

---

## Git Attribution Default

For generated commit/push commands, no Copilot attribution is necessary by default. Explicitly omit `-m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"` and equivalent co-author trailers, including in a commit body. An explicit user request or applicable Copilot/repository instructions may require attribution; honor that requirement and higher-priority instructions. This qualifies every no-trailer default in this skill. Do not change Git configuration or bypass hooks to suppress attribution.

Include this default and its exceptions directly in every skill created or maintained, and verify them when checking the result.

---

## Create a Custom Agent

For DevHub, put a repository custom agent in `.github/agents/devhub-<short-role>.agent.md`.

1. Give it a concise role-focused `name` and `description`.
2. Explain the role, task boundaries, relevant context to inspect, expected behavior, and response format in the body.
3. Configure tool access only when the target Copilot host supports it and the role benefits from a narrower tool set. Clearly distinguish requested behavior from an enforced restriction.
4. Do not make an agent depend on a skill being invoked. State the necessary role guidance directly in the agent, include task-appropriate automatic context discovery, and let the user supply the objective and any context that cannot be discovered.
5. For every DevHub-maintained agent, place this user-facing note immediately after the YAML frontmatter. Replace `<agent-filename>` with the actual filename, including `.agent.md`, so the URL points to that exact agent file:

   > **Maintenance note for users:** This agent is maintained in [DevHub](https://github.com/CollinPoetoehena/DevHub/blob/main/.github/agents/<agent-filename>). This is provenance information only; AI agents do not need to follow the link to use the agent.

---

## Update Existing Customization Lists

Automatically discover any existing catalog, index, or README that lists the project's skills or agents. In DevHub, these lists are in `.github/skills/README.md` and `.github/agents/README.md`; other repositories may use different locations.

- Add each new skill or agent to the appropriate existing list with a working relative link and a concise description, following its ordering and formatting conventions.
- When renaming, moving, or changing a customization's purpose, update its existing entry and directly affected references rather than adding a duplicate or leaving stale links.
- If no list exists after discovery, report that fact; do not create a new catalog unless requested or required by project guidance.

---

## Check the Result

- Confirm the file is in the requested kind's supported location, with correct extension and valid YAML frontmatter.
- Confirm the skill directory and its `name` match and begin with `devhub-`.
- Confirm every DevHub-maintained skill or agent has the user-facing maintenance note after its frontmatter, linking to its exact source file with no unresolved placeholders, without making the link required reading.
- Confirm every skill created or maintained includes the invocation-specific precedence note near the top, with an example and the higher-priority instruction and safety caveat.
- Ensure the description makes intended activation clear and the content is focused. Confirm the skill contains its essential rules, workflow, and context without relying on another customization, Git-hosted file, external documentation, or URL; any links are optional context, and any supplemental skill resources are included in its directory and explained.
- Confirm agents likewise contain their essential task guidance directly rather than relying on linked material to supply required steps or context.
- Confirm every created or maintained change skill includes the senior software engineer role statement immediately after its title.
- Confirm every created or updated skill states the Git command handoff requirement directly, including a concrete commit message without a co-author trailer, safe push-target discovery, the all-changes warning, and no automatic commit or push.
- Confirm commit-message guidance requires reviewing unstaged and staged diffs plus status and relevant untracked files, and describes the full pending scope rather than only the latest task.
- Verify that automatic discovery is explicit, includes a fallback beyond common locations, and does not require unnecessary project-specific user inputs. Confirm the report identifies the project files actually used and discovery limitations.
- Confirm any existing customization lists and directly affected links are current, and include updated indexes or the absence of a list in the completion report.
- Follow current official documentation for details that depend on a particular Copilot host:
  - [Creating and adding a skill](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills#creating-and-adding-a-skill)
  - [Custom instructions in VS Code](https://code.visualstudio.com/docs/agent-customization/custom-instructions)
  - [Custom agents in VS Code](https://code.visualstudio.com/docs/agent-customization/custom-agents)
- Report the created or updated file and any host-specific behavior that remains unverified.

---

## Completion Report

Report the changes, files actually used for guidance and structure, updated catalogs, checks run and skipped, inferred conventions, missing guidance, and unverified host-specific behavior.

Before composing the commit message, inspect `git diff`, `git diff --cached`, and `git status --short`; review relevant untracked files too, since they are not included in those diffs. Base the message on the complete pending change set that `git add -A` will stage, including earlier session changes, not only the latest task or your own edits. Describe the combined scope without claiming ownership or validation of others' changes, and flag unrelated or unreviewed changes before offering the all-changes command.

For file changes in a Git repository, end the report with a copy-ready `sh` block containing `git add -A && git commit` with a concrete task-specific message, followed by `&& git push`. Do not add a co-author trailer. Follow the consuming repository's commit conventions. Inspect the branch and upstream; if no upstream exists, use `git push --set-upstream` with a verified remote and current branch. Do not leave placeholders or invent a push target. Before the block, warn that `git add -A` stages all changes, including unrelated edits, and ask the user to review the diff. These commands are for the user; do not commit or push unless explicitly requested. If no files changed, the task is outside Git, or a safe sequence is blocked, explain why the commands are omitted or incomplete.

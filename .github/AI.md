# AI Customizations

This page is a generic guide to the main kinds of AI customizations: what they are for, how to choose among them, and how to reuse them across repositories. For supported product-specific formats and behavior, follow the official documentation linked from the relevant [instructions](./instructions/README.md), [skills](./skills/README.md), or [agents](./agents/README.md) guide.

For general AI concepts, prompt-writing guidance, and the [framework for matching model capability and cost to a task](../reference/AI.md#4-tier-model-framework-credit-efficiency), see the [AI reference](../reference/AI.md). For coding, its practical rule explained in the [AI reference](../reference/AI.md#coding) is to use automatic model selection by default.

Return to the [shared GitHub customizations overview](./OVERVIEW.md) for other topics.

---

## Table of contents

- [Why I developed and use these customizations](#why-i-developed-and-use-these-customizations)
- [Which customization should I use?](#which-customization-should-i-use)
- [Model selection](#model-selection)
- [Approvals and permissions](#approvals-and-permissions)
- [Personal preferences and workplace reuse](#personal-preferences-and-workplace-reuse)
- [General design principles](#general-design-principles)
- [Create and maintain customizations](#create-and-maintain-customizations)
  - [Discover project context automatically](#discover-project-context-automatically)
  - [Keep each customization self-contained](#keep-each-customization-self-contained)
  - [Use focused standalone skills](#use-focused-standalone-skills)
  - [Validate and report the result](#validate-and-report-the-result)
  - [End skill reports with ready-to-run Git commands](#end-skill-reports-with-ready-to-run-git-commands)
- [Use external or centralized customizations across repositories](#use-external-or-centralized-customizations-across-repositories)
  - [Copy into a repository or personal location](#copy-into-a-repository-or-personal-location)
  - [Keep a centralized local source](#keep-a-centralized-local-source)
- [Examples beyond DevHub](#examples-beyond-devhub)

---

## Why I developed and use these customizations

I developed this collection to make the way I work with AI more repeatable and useful. Before, I typed many of the same expectations into each prompt: inspect the project first, follow existing conventions, preserve unrelated changes, validate the result, and explain what was done. Customizations let me capture what works for me instead of reconstructing that guidance for every task.

- **Productivity:** Less time spent writing long prompts and repeating corrections means more time for the actual problem. I can focus each request on its goal, scope, and constraints while reusing the workflow guidance. See [which customization to use](#which-customization-should-i-use) for choosing reusable guidance over repeating it in each prompt.
- **Consistency:** Instructions, skills, and agents capture my preferred working practices and output expectations. This gives recurring tasks a reliable baseline across sessions, reducing variation in how similar work is approached and reported without relying on me to remember every detail each time. See the [general design principles](#general-design-principles) and [customization authoring guidance](#create-and-maintain-customizations).
- **Automation:** Skills guide recurring steps such as discovering project context, making focused changes, running relevant checks, updating documentation, and preparing a Git handoff. Useful scripts or tools can support those steps, reducing manual coordination without removing approval requirements. See [automatic project-context discovery](#discover-project-context-automatically) and the [Git handoff guidance](#end-skill-reports-with-ready-to-run-git-commands).
- **Quality:** Explicit review and validation steps help reduce omissions, unsupported assumptions, and inconsistent results. Asking for evidence, skipped checks, and remaining risks makes the work easier to assess; customizations improve the process but do not guarantee correct output. See [validation and reporting](#validate-and-report-the-result) and [approval and permission guidance](#approvals-and-permissions).
- **Reuse across projects:** Automatic discovery lets the generic workflows adapt to each repository's own guidance and tooling. I can use the same collection for personal projects and, where policy permits, at work, instead of maintaining a separate generic setup for every repository. See [automatic project-context discovery](#discover-project-context-automatically) and [personal preferences and workplace reuse](#personal-preferences-and-workplace-reuse).
- **Continuous improvement:** When a prompt adjustment or lesson proves useful repeatedly, I can incorporate it into the relevant customization. The collection becomes a maintained record of working practices that I can refine and reuse, rather than a series of successful prompts lost in old chats. See [creating and maintaining customizations](#create-and-maintain-customizations) for how to capture and update that guidance.

In short, the value is not simply shorter prompts: it is a reusable, reviewable way to apply what works for me, with less repetition and more consistent execution. The maintenance is worthwhile when a customization supports recurring work; one-off requests still belong in ordinary prompts, and I remain responsible for reviewing the results.

---

## Which customization should I use?

Start with the smallest thing that solves the problem. A one-off prompt may be all you need.

Use skills and agents for recurring, generic tasks or roles where saved guidance improves consistency. For other tasks, use GitHub Copilot's general chat and agent capabilities directly; not every request needs a saved skill, agent, or instruction. You can still provide task-specific context and directions in the prompt.

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

## Model selection

**Use Auto in the chat session by default**, including when using DevHub skills and custom agents. In my experience, it generally selects an appropriate model and gets the task done reliably, with excellent token/credit cost efficiency compared with routinely choosing a more expensive model manually. Auto matches task complexity to suitable models, reserving more costly reasoning for work that needs it; this improves cost efficiency, not necessarily the number of tokens used. GitHub currently also offers a **10% discount on model costs for paid Copilot plans** when using Auto in supported experiences. See the [AI reference's automatic model selection guidance](../reference/AI.md#automatic-model-selection) for the detailed rationale, experience, trade-offs, and when to switch to manual selection, and GitHub's [Auto model selection documentation](https://docs.github.com/en/copilot/concepts/models/auto-model-selection) for current availability and discount terms.

**Choose the Balance tier by default for the Auto model selection.** It is generally my recommended option for everyday work: it weighs cost, answer quality, and latency against task complexity, saving costs while still providing good answers. **Efficiency** prioritizes cost and is also a useful option I sometimes explicitly select for straightforward work, such as simple documentation edits. **Intelligence** prioritizes quality and can favor higher-tier models that cost substantially more, though it does not route every task to an expensive model. I generally do not use it: in my experience, the low- and medium-cost models Balance usually selects get most work done perfectly, and even low-cost models have handled larger tasks successfully. Balance can still select a more capable model when needed; I have found it suitable even for very large and complex tasks without routinely paying for a higher-cost model. See GitHub's [Auto tier options](https://docs.github.com/en/copilot/concepts/models/auto-model-selection#auto-tier-options) for details.

Keep model selection in the chat/session controls rather than hard-coding it into reusable customizations:

- **Custom agents:** Omit the YAML `model` property by default so the agent inherits the session's selected/default model, including Auto when selected. Do not set `model: auto`: it is not a documented, portable supported frontmatter value and is unnecessary for inheritance. Only specify a fixed supported model when the task genuinely requires it. See the [custom agent configuration reference](https://docs.github.com/en/copilot/reference/custom-agents-configuration).
- **Skills:** Do not add a `model` property to `SKILL.md`. Skills provide instructions, not model selection; they use the model of the chat session or agent invoking them.

Exact defaults and model controls vary by host. Leaving the agent's model unset preserves the host's selection rather than forcing a particular model or attempting to enable Auto through frontmatter.

---

## Approvals and permissions

> **Official documentation:** Start with [Manage approvals and permissions in VS Code](https://code.visualstudio.com/docs/agents/run/approvals). For the GitHub Copilot CLI, see [Allowing and denying tool use](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/allowing-tools). These are product-specific controls; check the documentation for the Copilot host and version you use.

I generally want to review and approve commands and other potentially consequential actions, while avoiding repeated prompts for routine, low-risk work. In VS Code, **Manual permissions** is the default approval level: it applies the configured tool, URL, and terminal approvals. Organization-managed policies can require manual approval for specific tools. Within those constraints, configure narrow approvals for commands you trust rather than enabling blanket approval.

### Ask for the approval behavior you want

In a task prompt, make the desired approval boundary explicit. For example:

> Before running a terminal command, show me the exact command and its purpose, then wait for my approval. You may proceed without asking for read-only inspection commands. Always ask before commands that edit files, install dependencies, access the network, change Git history or remotes, deploy, or affect external systems.

Adapt the request to the task. You can require confirmation for every command, or let the agent proceed with clearly bounded read-only inspection and ask before changes. Name sensitive actions such as package installation, network access, file deletion, Git commit/push, deployment, or infrastructure changes. Avoid vague instructions such as "ask for approval when needed" when you want a specific boundary.

Prompt wording guides the agent; it does **not** change permission settings or override organization policy. If the tool's approval dialog appears, inspect the tool and its inputs and choose whether to allow it. An approval for one use is narrower than an approval for the session, workspace, or future uses.

### Reduce repetitive prompts without allowing everything

In VS Code, use **Chat: Manage Tool Approval** to review which tools are pre-approved or require confirmation. The `chat.tools.eligibleForAutoApproval` setting can make a tool always require manual approval. For terminal commands, `chat.tools.terminal.autoApprove` lets you allow or require confirmation for specific commands or patterns; a `false` rule requires approval rather than blocking the command. Disabling `chat.tools.terminal.enableAutoApprove` requires approval for every terminal command. These settings and their availability may depend on the host, session, and organization policy.

A practical approach is to auto-approve only specific, well-understood, low-risk commands you use repeatedly, such as read-only status or inspection commands. Keep approval required for commands that modify files, delete data, install software, contact services, alter Git history, push, deploy, or change infrastructure. Review compound commands as a whole; a command joined with `&&` can perform multiple actions. Do not grant broad terminal or global auto-approval just to silence prompts.

Manual permission mode can coexist with pre-approved low-risk tools or commands; manual does not necessarily mean every action prompts. If organization policy forces manual approval, prompt wording cannot bypass that policy, though you may still be able to reduce prompts through permitted, narrow approval settings. If settings are managed or unavailable, keep Manual permissions and approve individual requests as appropriate. Sandboxing is a separate control from approvals: it can restrict terminal file-system or network access, but does not itself replace approval review.

---

## Personal preferences and workplace reuse

DevHub's AI customizations are my personal preferences and curated collection: I maintain and use them myself, rather than presenting them as a team policy or a universal standard. I can use the same generic skills and agents for personal projects and at work, subject to the workplace's AI, security, and tooling policies.

Their workflows are project-independent because they [discover the consuming project's context automatically](#discover-project-context-automatically). They read that project's instructions, documentation, configuration, and existing patterns rather than imposing DevHub's repository layout or conventions. Others can reuse them for the same reason, provided the workflow and preferences suit their needs; generic does not mean it overrides local requirements.

**Prefer adding only project-specific customizations in each project.** Reuse the existing generic workflows instead of creating another generic collection for every project or team. Project-specific instructions, skills, or agents should capture genuinely local rules or capabilities that the generic setup cannot already discover.

If a team needs different shared generic guidance, it can maintain a similar central repository of team-owned customizations. That is an option, not a prerequisite for workplace use: it introduces another collection to review, distribute, update, and maintain. Create it only when real team-wide differences justify that extra maintenance; automatic discovery already makes DevHub's generic collection reusable across projects.

---

## General design principles

- Add a customization when it meaningfully improves quality, speed, or consistency enough to justify its creation and maintenance.
- Keep customizations focused, current, and appropriate to their audience.
- Keep task-specific input in the request; reusable guidance should not assume that every repository or user has the same context.
- In a skill, state near the top that explicit directions in its current invocation or accompanying request take precedence over conflicting skill defaults or procedures (for example, an explicit instruction to skip tests overrides the skill's usual test workflow). This precedence does not override higher-priority system or developer instructions, host constraints, or applicable safety requirements.
- Keep instructions, skills, and agents self-contained. Include the essential rules, workflow, and context they need directly in the customization instead of relying on another customization, a Git-hosted file, external documentation, or another URL to supply it. Links may provide optional background, but must not be required to understand or carry out the task. For a skill that needs supplemental files, keep those resources in its skill directory and explain their use; otherwise put the guidance directly in the skill or agent content. Limited duplication is acceptable.
- Design reusable skills and agents to discover project instructions, structure, conventions, and commands automatically, searching beyond common locations when needed. This avoids per-repository configuration and asking users to repeat information already available in their project. Users still supply goals, unresolved decisions, and required authorization; discovery does not replace consent or justify guessing. Report the files used and any discovery limitations.
- A model instruction is guidance, not a security boundary or an enforcement mechanism by itself.
- Refer to the product's official documentation for supported formats, locations, activation, and capabilities.

For a broader comparison of customization types, see the [VS Code customization overview](https://code.visualstudio.com/docs/agents/concepts/customization).

---

## Create and maintain customizations

> **Shared authoring guidance:** My other repositories, such as [devhub-homelab](https://github.com/CollinPoetoehena/devhub-homelab), link to this section as the central reference for creating AI customizations, rather than maintaining separate copies of the generic guidance.

This is the shared authoring guidance for DevHub's file-based AI customizations. Start here, then use the type-specific additions for [instructions](./instructions/README.md#what-to-include), [skills](./skills/README.md#create-a-skill), or [agents](./agents/README.md#create-a-repository-agent). For requests to create or maintain a DevHub skill or agent, the [`devhub-ai-customization` skill](./skills/devhub-ai-customization/SKILL.md) contains the complete executable workflow; it does not require following this page at runtime.

Use AI to create and maintain customizations, including applying updates consistently when shared guidance is duplicated across skills. Review the complete diff yourself, confirm each customization remains accurate and self-contained for its purpose, and run relevant checks before relying on the changes; AI assistance is an editing aid, not a substitute for review.

First identify the repeated problem, audience, and scope. Prefer ordinary GitHub Copilot chat or agent capabilities for one-off work or tasks that do not benefit from saved guidance. Add a customization only when its quality, speed, or consistency benefits justify authoring and maintenance. If it does not add enough value to justify its ongoing upkeep, use Copilot directly instead of creating and maintaining a customization. Combine closely related tasks that share a process; split them only when role or workflow differences materially matter. Prefer project-specific additions over duplicating an existing generic workflow.

Write a focused goal, boundaries, relevant inputs, safety constraints, validation, and expected output. Keep task-specific objectives in the user's request. Use supported locations and frontmatter for the selected host, with a clear name and description that explain when the customization applies. DevHub-maintained skill directories and agent filenames use the `devhub-` prefix.

For every skill, put a short precedence note near the top: explicit directions in the current invocation or accompanying request override conflicting workflow defaults in the skill. Give a concrete example where useful, such as honoring a request not to run tests, and clarify that higher-priority instructions, host constraints, and safety requirements still apply.

### Discover project context automatically

Build task-appropriate discovery into every reusable skill or agent, and perform it while authoring or updating the customization:

1. Identify the owning repository or package and read applicable project and directory instructions, such as `AGENTS.md`, `.github/copilot-instructions.md`, and relevant `.github/instructions/*.instructions.md`.
2. Inspect entry points, development, architecture, writing, and testing guides; relevant documentation and neighboring code; manifests, configuration, build scripts, and CI workflows. Use the actual content to establish local structure, terminology, constraints, and commands.
3. Treat common filenames as starting points, not mandatory inputs. If they do not reveal enough context, inspect the repository layout, search relevant filenames and contents, and follow existing entry-point links. Keep the search scoped and respect access restrictions.
4. Do not hard-code consuming-project paths or require users to supply discoverable conventions and commands. Users still provide goals, material unresolved decisions, authorization, and inaccessible information. A discovered command is not permission to execute it.
5. Require reports to identify the files actually read and used, each file's role, inferred conventions, and missing guidance. Do not invent context or claim discovery always succeeds.

For code-change workflows, discover whether meaningful tests are implemented in the owning project or package by reading test contents and runner configuration, not merely finding a test directory. The [generic, Terraform, and Ansible change skills](./skills/README.md#choosing-a-change-skill) update or add coverage using an existing meaningful suite; when tests are absent or only placeholders exist, they skip test creation and execution by default and report why. Explicit user requests or applicable project requirements can require adding tests where none exist. Do not introduce a framework merely because code changed, including for standalone scripts. Continue applicable existing formatting, linting, syntax, type, build, or documentation checks, and distinguish static validation from runtime verification.

Code-change guidance should also require concise comments for non-obvious reasoning, constraints, edge cases, or trade-offs, following the consuming project's style. Explain why rather than restating obvious code, and update or remove comments made inaccurate by a change.

### Keep each customization self-contained

Include the instructions and context needed to perform the task in the customization itself. Do not require another customization, Git-hosted file, external documentation page, or URL to supply essential rules, background, or workflow, and do not make one customization a mandatory next step. Links may supplement the content, but the customization must remain usable if the linked material is unavailable. When a skill needs supporting files, keep them in that skill's directory and explain when to use them; otherwise include the material directly in the skill or agent. Chains of references multiply dependencies and context, make installation and maintenance harder, and can fail when material is unavailable or invocation differs by host. A little more text and limited duplication are preferable; keep the duplicated essentials concise and review them when they change.

Because AI is used to create and maintain skills, it can also update repeated essential guidance consistently when requirements change across multiple skills. This makes modest duplication practical without turning skills into a chain of dependencies. Treat AI as an editing aid, not an authority: review the full diff yourself, confirm each skill remains accurate and self-contained for its intended task, and run relevant checks before relying on the update. See the [shared AI-assisted authoring guidance](#create-and-maintain-customizations) above.

The [VS Code guidance on effective instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions#_tips-for-writing-effective-instructions) recommends short, self-contained instructions, as mentioned in their documentation: "*Keep your instructions short and self-contained. Each instruction should be a single, simple statement. If you need to provide multiple pieces of information, use multiple instructions.*". DevHub's avoidance of required cross-customization chains is an authoring convention, not a claim that Copilot prohibits all references or supports a universal skill-to-skill invocation contract.

Informational links, user-facing provenance notes, and automatically discovered project documentation are still useful. They must not replace the customization's own essential procedure. Skills can bundle scripts and supporting resources inside their directory and load them when needed; self-contained does not mean every resource must be pasted into one file. Human-facing READMEs should link to this shared authoring section rather than duplicate it, while installed skills retain their complete runtime guidance.

### Use focused standalone skills

A focused skill can be useful on its own even when a broader skill already includes the same guidance as one step in a larger workflow. The broader skill serves users who want an end-to-end task; the standalone skill serves users who want only that distinct step, perhaps after manual work or using a general Copilot conversation. It gives that task its own clear description and entry point, without asking users to invoke a larger workflow that does not fit.

Keep the scope genuinely narrow and the procedure self-contained. Some duplication is a reasonable trade-off for direct discoverability and independent use. Do not create a separate skill for every minor variation, and do not make it a required dependency of broader skills; if the standalone skill adds no distinct value beyond the existing workflow, use Copilot directly instead.

### Validate and report the result

Check supported locations, extensions, frontmatter, activation descriptions, safety boundaries, and any bundled resources. For a DevHub skill, the YAML `name` must match its lowercase, hyphenated directory name. Every DevHub-maintained skill and agent has a user-facing maintenance note immediately after its frontmatter, linking to its exact source file in DevHub and explicitly stating that the link is provenance, not required reading.

Update existing catalogs and directly affected links for additions, renames, moves, or purpose changes. Review the diff for unrelated changes and sensitive information; run applicable checks and report what was checked, skipped, or remains host-specific and unverified. Keep local project instructions separate from generic workflow guidance.

### End skill reports with ready-to-run Git commands

Every DevHub skill that changes files in a Git repository should end its completion report with a copy-ready `sh` block that stages, commits, and pushes the result. Include this requirement directly in each skill, including newly created skills; do not make them follow this page or another skill to obtain it.

Use `git add -A`, a concrete, task-specific commit message following the consuming repository's conventions, and `git push`, joined with `&&` so a failed step stops the sequence. Do not add a co-author trailer. Do not leave message or branch placeholders for the user to replace. Inspect the branch and upstream before suggesting the commands: when there is no upstream, use `git push --set-upstream` with a verified remote and current branch; if no safe push target can be established, state the blocker rather than inventing one.

For example, when the current branch already has an upstream:

```sh
git add -A && git commit -m "docs(ai): centralize customization authoring guidance" && git push
```

DevHub omits co-author trailers as a personal preference: AI assistance does not need a separate author identity or email in the commit message. The person reviewing and committing the changes remains responsible for them.

Before composing the commit message, inspect `git diff`, `git diff --cached`, and `git status --short`; review relevant untracked files too, since they are not included in those diffs. Base the message on the complete pending change set that `git add -A` will stage, including earlier changes from a longer session, not just the latest task or the AI's own edits. Describe the combined scope accurately without claiming ownership or validation of changes made by others. Flag unrelated or unreviewed changes before offering the all-changes command.

Before the final block, remind the user to review the diff: `git add -A` stages **all** changes, including unrelated edits. These commands are for the user to execute; producing them is not authorization for the AI to commit or push. Do not execute them unless explicitly requested. If no files changed, the task is outside a Git repository, or a safe commit/push sequence is blocked, explain why the block is omitted or incomplete instead of fabricating a successful handoff.

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

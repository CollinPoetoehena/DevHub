# DevHub Agent Package Manager (APM) Packages

[APM](https://microsoft.github.io/apm/) distributes shared AI customizations to supported agent harnesses. DevHub uses it to give every personal project the same engineering baseline, with repository-specific context in a root `AGENTS.md`. The harness loads the resulting context; APM does not execute the agent or guarantee compliance.

This guide owns the general approach: why to customize AI, the concepts, the reuse-first design, setup, usage, and maintenance. Package READMEs, such as [common](common/README.md) and the stack packages ([python](python/README.md), [java](java/README.md), [go](go/README.md), [rust](rust/README.md), [containerization](containerization/README.md), and [iac](iac/README.md)), own their contents, design, and reuse registry. [Getting Started](../../docs/GETTING-STARTED.md) owns shared-workspace arrangements.

---

## Table of Contents

- [Why create AI customizations](#why-create-ai-customizations)
- [Concepts](#concepts)
- [Design](#design)
  - [The 80/20 rule: reuse, then tailor](#the-8020-rule-reuse-then-tailor)
  - [What to own: the 20%](#what-to-own-the-20)
  - [How much detail is enough](#how-much-detail-is-enough)
  - [Why orchestrate](#why-orchestrate)
  - [Deterministic by design](#deterministic-by-design)
  - [Why not install entire collections](#why-not-install-entire-collections)
  - [Reference collections](#reference-collections)
  - [Reuse registry](#reuse-registry)
  - [Official dependencies](#official-dependencies)
  - [Runtime-managed model selection](#runtime-managed-model-selection)
  - [Custom instructions in subagents](#custom-instructions-in-subagents)
  - [Agent configuration](#agent-configuration)
  - [How guidance is layered](#how-guidance-is-layered)
  - [Language and framework guidance](#language-and-framework-guidance)
  - [Package design](#package-design)
- [Repository setup](#repository-setup)
  - [Verify activation](#verify-activation)
- [Authoring repository guidance](#authoring-repository-guidance)
- [AI usage](#ai-usage)
  - [Personal usage: stay the expert](#personal-usage-stay-the-expert)
  - [Prompt engineering](#prompt-engineering)
- [Working with agents](#working-with-agents)
  - [Choosing an agent](#choosing-an-agent)
  - [Recommended Chat setup](#recommended-chat-setup)
- [Maintenance and validation](#maintenance-and-validation)
  - [Managing AI customizations](#managing-ai-customizations)
  - [Updating APM packages and the CLI](#updating-apm-packages-and-the-cli)
  - [Maintaining reused content](#maintaining-reused-content)
  - [Validation](#validation)
- [DevHub's own setup](#devhubs-own-setup)
- [References](#references)

---

## Why create AI customizations

Default agents are capable, but they do not know a repository's/project's conventions, architecture, or validation workflow, so the same context gets repeated in every chat. Customizations write that context down once in a form both agents and people can use:

- **Lasting standards and fundamentals:** coding principles, documentation rules, review discipline, and engineering workflow outlive any specific tool, language, or project. Capturing them once standardizes code and projects now and keeps paying off across a whole career. When tools change, add or swap a skill for the new tool while the fundamentals stay in place.
- **Consistent enforcement without memorization:** standards are applied on every task without anyone needing to remember every rule.
- **Document once, use twice:** conventions need documenting anyway. Written as instructions and skills, they guide AI automatically and remain readable for humans, so nobody has to memorize them.
- **Faster onboarding:** new contributors, and future me returning to an old project, benefit from institutional knowledge automatically.
- **Less repetition and drift:** shared expectations live in one versioned package instead of being re-explained in prompts or copied across repositories.
- **Predictable, reviewable workflows:** fixed roles, routes, and reports make AI-assisted work traceable and easier to verify.

Default setups give default context and behavior for agents which is sufficient for general tasks but lack repository- and tool-specific knowledge and therefore lead to worse quality outcomes (e.g. failing to follow Python conventions or project-specific rules, etc.). Customizations complement the default agent and the human contributors; they do not replace engineering judgment or guarantee a result. Keep them small and relevant: overlapping instructions add maintenance, stale facts, and conflicts.

See for an example in the official documentation: [Before and after customization examples](https://awesome-copilot.github.com/learning-hub/before-after-customization-examples/). This is a simple illustration but it demonstrates the core idea: capturing repository-/project-specific knowledge once and reusing it consistently across tasks improves quality and reduces repetitive explanations significantly.

---

## Concepts

| Primitive | What it is | Use when |
|---|---|---|
| Repository instructions (`AGENTS.md`) | Always-on context for one repository | Local facts and routes to owning documentation |
| Scoped instructions (`*.instructions.md`) | Standards attached by file pattern (`applyTo`) or description | Rules for most work on matching files, such as coding or documentation standards |
| Skills (`SKILL.md`) | On-demand procedures with optional scripts and references; only the description loads until relevant | A specific, repeatable task such as committing, testing, or writing comments |
| Agents (`*.agent.md`) | Roles with their own instructions, tool selection, and allowed subagents | Distinct responsibilities, context isolation, or delegation |
| Hooks | Shell commands run at agent lifecycle events | Deterministic enforcement, such as blocking a command or running a formatter |
| Prompts (`*.prompt.md`) | Reusable, user-invoked requests | A recurring single request with parameters |

Rules of thumb: most work needs it, use an instruction; a specific task needs it, use a skill; a different role, toolset, or model needs it, use an agent; it must always happen, use a hook, CI, or permissions, because instructions guide rather than enforce.

An agent can delegate to subagents: each runs in a fresh, isolated context and returns one result, which keeps the coordinator's context focused. Handoffs instead switch the active agent for the user.

Learn more:

- [Building custom agents](https://awesome-copilot.github.com/learning-hub/building-custom-agents/) and [agents and subagents](https://awesome-copilot.github.com/learning-hub/agents-and-subagents/)
- [Custom agents and subagents](https://docs.github.com/en/copilot/concepts/customizations/custom-agents#custom-agents-and-subagents) (GitHub Docs)
- [Creating effective skills](https://awesome-copilot.github.com/learning-hub/creating-effective-skills/)
- [Defining custom instructions](https://awesome-copilot.github.com/learning-hub/defining-custom-instructions/)
- [Before and after customization examples](https://awesome-copilot.github.com/learning-hub/before-after-customization-examples/)
- [Copilot configuration basics](https://awesome-copilot.github.com/learning-hub/copilot-configuration-basics/)
- [VS Code hooks](https://code.visualstudio.com/docs/agent-customization/hooks)

---

## Design

### The 80/20 rule: reuse, then tailor

Roughly 80% of useful AI customization already exists. Language patterns such as Python best practices, testing techniques, general coding principles, review methods, planning approaches, and authoring guidelines for agents and skills are built, maintained, and battle-tested by others. Reinventing them is a large amount of work and makes the setup very complex. An earlier DevHub setup did exactly that, and the result was long prompts, overlapping rules, and unreliable, inconsistent agent behavior.

This is the most important design rule, because it is easy to get lost in building AI customizations. It is the same principle as in normal engineering: nobody writes their own programming language or basic libraries; they reuse existing ones and add thin wrappers or configuration for their situation. AI customizations work the same way: reuse existing ones and tailor them, rather than building everything from scratch.

Keep it simple. When adopting a source, keep its substance: the reference collections below are well designed and widely used, so remove what does not apply and add only what is missing rather than rewriting them.

### What to own: the 20%

Own only what no external source can know:

- **Thin agents:** roles that act mainly as wrappers. They define routing, responsibilities, tools, models, outcomes, and reports, and delegate knowledge to skills and instructions. The [common package](common/README.md#workflow) defines DevHub's Orchestrator workflow.
- **Workflow and governance:** routing rules, approval gates, definition of done, and when review or planning is required.
- **Personal and project conventions:** documentation style, Git policy, naming, repository layout, and validation commands.
- **Tailoring of reused content:** removing what is not needed and adding DevHub-specific constraints.
- **Personal usage guidance:** how I work with AI, in [AI usage](#ai-usage).

Decide per reusable part:

| Situation | Approach |
|---|---|
| Official or authoritative, used unchanged | Pinned APM dependency |
| Useful unchanged, plus local rules | Pinned APM dependency, plus a scoped local instruction |
| Needs trimming or tailoring | Copy into the package with source and changes recorded in the registry |
| Unique to DevHub | Author locally |
| Unique to one repository | Keep in that repository, not in a shared package |

### How much detail is enough

The built-in setup can already write code and understands basic language syntax. It may also apply familiar good practices, but it does not provide a complete, repository-specific engineering standard by default. Do not assume it will consistently choose your input-validation approach, error-handling policy, DRY and KISS trade-offs, or preferred language and tool patterns. This is the gap described in [why create AI customizations](#why-create-ai-customizations): knowing a technique is not the same as knowing when and how this project requires it.

Specify choices that change the result, not a basic language tutorial, such as:

| Detail | What to specify | Owning guidance |
|---|---|---|
| Engineering standards | Validate external input at boundaries, surface errors explicitly, reuse existing helpers (DRY), and prefer the simplest sufficient solution (KISS) | [Common instructions](common/README.md#package-contents) |
| Python patterns | Supported versions, typing and error-handling conventions, framework patterns, and exact lint/type-check/test commands | [Python package](python/README.md) and repository configuration |
| Docker builds | Layer caching: copy dependency manifests and install dependencies before copying frequently changing source; use the project's build and runtime stages | [Docker instructions](containerization/.apm/instructions/docker.instructions.md) |
| Helm input schemas | The required format and workflow: `@schema` annotations in values, constraints such as `enum` and `pattern`, and a generated, committed `values.schema.json` rather than hand-editing it | [Helm instructions](containerization/.apm/instructions/helm.instructions.md) |
| Local contracts | Compatibility limits, security boundaries, generated-file ownership, and the commands that prove the change works | Root `AGENTS.md`, owning documentation, and repository tooling |

Basic syntax, ordinary loops, or how to declare a function do not need repeating. Include version-specific syntax constraints or known model mistakes only when they affect this repository. Put short mandatory rules in scoped instructions and larger procedures or examples in skills; see [language and framework guidance](#language-and-framework-guidance). The common and opt-in stack packages supply these explicit standards, rather than relying on the built-in setup to infer them.

AI customizations are a means to an end. The goal is to build good, maintainable software, not to perfect the customizations. This work has no natural end: every language, framework, and tool can get another rule, reference, or example, and it is easy to spend more time tuning customizations than building the software they are meant to help with. Find the balance between three forces:

- **Usability:** enough guidance that agents follow the conventions and avoid known mistakes.
- **Maintainability:** every owned file must be kept current with its sources, tools, and models, so more files and more detail mean more maintenance.
- **Time:** time spent on customizations is time not spent building software.

The current setup is enough: the common package with the Orchestrator workflow and shared standards, plus one stack package per language or tool area, built from the [reference collections](#reference-collections). Do not go much further than that:

- **Do not over-perfect:** general guidance from good sources is enough. Do not rewrite copied content to make it perfect, add exhaustive rules, or anticipate every edge case.
- **Add specifics when encountered:** add a language, framework, or tool when a project actually uses it, and a rule when an agent got something wrong or a convention is missing. The [learning step](common/README.md#learning) records such lessons from real runs.
- **Source first, then tailor:** take new guidance from the reference collections or official documentation, copy it, and use AI to adapt it to the DevHub setup instead of writing it from scratch.
- **Stop at good enough:** when agents produce work that meets the standards with normal review, the customizations are done; spend the time on building instead.

### Why orchestrate

A single default agent doing everything in one long conversation works for small tasks, but becomes unreliable for larger ones: context fills up with unrelated detail, the agent reviews its own work, and planning, implementation, and review all use the same model and tools. A thin orchestrator in front of focused worker agents addresses that:

- **Right-sized workflow:** a fixed routing table sends a typo fix straight to a worker and a cross-cutting change through planning, approval, implementation, and review, so effort matches risk instead of every task paying the full workflow cost.
- **One entry point:** developers select one agent instead of deciding which role, mode, or model each request needs.
- **Focused context:** each worker runs as a subagent in a fresh context with only its assignment, which keeps the coordinator's context small and reduces cross-task confusion.
- **Separation of duties:** each role has its own instructions and behavioral boundaries, while the common agents share the same explicit all-tools request. Reviewers are instructed not to edit and to run only inspection and check-mode validation; planners cannot implement. Review runs in a separate context. The common workflow's route determines whether a separate Reviewer step runs.
- **Human control where it matters:** approval gates before planned implementation and before commits keep consequential decisions with the user, while routine steps run autonomously.
- **Traceability and learning:** fixed outcomes and reports produce a trace of route, steps, tools used, validation, and deviations; its signals feed the [learning step](common/README.md#learning).

**Why the cycle improves the result:** the same agent that wrote a change is poor at finding its flaws. It remembers its reasoning, its shortcuts, and the dead ends it already ruled out, so it tends to confirm its own work. A reviewer that starts with a fresh context sees only the requirement, the plan, and the diff. It has no memory of the reasoning that produced them, so it is more likely to question assumptions the implementer took for granted. Review independence comes from the fresh context and role, not a particular model family, and a separate Reviewer step is route-dependent. Planning works the same way: a planner that does not write code is less likely to jump into implementation before the approach is clear.

**Why it saves time overall:** a multi-step cycle usually costs about the same wall-clock time as a long chain of manual prompts, but it changes where your effort goes. Consider a task that takes six prompts over about 30 minutes, with you reading each intermediate result, correcting drift, and re-explaining context. The orchestrated version may take a similar 30 minutes, but you write one request, approve the plan at a defined gate, and read one report at the end. Quality is higher on the first pass, so fewer rounds of rework follow; meaning you can spend less time on corrections and context management and focus on another related task in parallel for example. The exact numbers depend on the task. Small tasks gain little and should go straight to a worker or the default agent.

**Why the report matters:** the final report lists the route, each step, tools used, validation results, and deviations. You can judge what was done and what remains unverified without rereading the whole conversation, and those same signals drive learning, so later runs improve.

**Follow-up prompts:** one prompt is usually enough, but follow-ups are normal and part of the design. A route pauses only at defined points: plan approval, a question a worker cannot answer itself (`NEEDS_INPUT`), or a decision after a blocked step. Your reply continues the same route at that point. Plan edits go back to Planner as a bounded revision. After a route completes, a follow-up such as "also handle the empty case" or "that is wrong, use X" is routed again as a new request. The orchestrator passes the earlier plan, findings, and changed files as inputs, so you do not have to re-explain context. A correction of a completed result is also a learning signal, so the same mistake is less likely next time. An ambiguous reply is treated as a new request rather than as approval, so nothing is implemented or committed by accident. Committing is itself a follow-up: the report ends with a suggested command, and an explicit "commit" runs it. Start a new chat for unrelated work, since a long conversation grows the orchestrator's context and weakens the fresh-context benefit. See [Follow-ups](common/README.md#follow-ups) for the exact handling.

Orchestration has costs: more model calls, latency, and context passed between agents. Keep the orchestrator a router rather than another all-knowing agent, keep worker count small, and use the default agent directly for quick questions. See [Agents and subagents](https://awesome-copilot.github.com/learning-hub/agents-and-subagents/) for the underlying pattern and the [common workflow](common/README.md#workflow) for DevHub's implementation.

### Deterministic by design

What makes customizations reliable is the explicit, checkable part: fixed decisions, fixed formats, and fixed limits. Vague guidance such as "review when appropriate", "use good judgment", or "report what you did" gives a model room to decide differently each run, so the same request produces different routes, skipped steps, or reports that hide failures. The earlier 1.x agents had this problem: long prose, implicit handoffs, and free-form results led to unpredictable and unreliable behavior. The current design replaces that with explicit structure:

| Vague | Deterministic |
|---|---|
| "Decide whether planning is needed" | A routing table evaluated top to bottom, first match wins, and uncertainty falls through to the most controlled route |
| "Continue as appropriate" | A closed outcome set per agent, such as `PASS \| IMPLEMENTATION_CHANGES \| PLAN_CHANGES`, with exactly one next step per outcome |
| "Let me know if something went wrong" | Execution status (`COMPLETE \| NEEDS_INPUT \| BLOCKED \| FAILED`) separate from the outcome, so a failed step cannot look like success |
| "Fix the issues the reviewer found" | At most two correction cycles and two plan revisions, then `BLOCKED` with the decision needed |
| "Get approval for big changes" | Named gates: plan approval before implementation, explicit authorization before commits, never push |
| "Summarize your work" | A fixed `## Report` block per agent and an aggregated trace with route, steps, tools used, validation evidence, and deviations |
| "Be careful with edits" | Explicit role boundaries: Planner, Architect, and Reviewer do not edit; Orchestrator delegates delivery. These are behavioral limits, not tool filters; see [agent configuration](#agent-configuration) |
| "Only report real issues" | A pre-finding gate (exact line, concrete failure, context read, defensible severity), proof for `CRITICAL` and `HIGH`, and zero findings as a valid result |
| "Write a good plan" | A fixed step format (file, action, reason, dependencies, risk) and a check before the plan is returned |
| "Improve over time" | A learning step triggered only by listed signals, with a fixed owner order for each lesson |

Apply the same principle to every customization, not only agents:

- **Agents:** one role, explicit boundaries, deliberate [tool access](#agent-configuration), runtime-managed model selection, and a fixed report. See [Building custom agents](https://awesome-copilot.github.com/learning-hub/building-custom-agents/).
- **Skills:** a description with concrete trigger phrases, numbered steps, explicit decision rules, and gotchas instead of general advice. See [Creating effective skills](https://awesome-copilot.github.com/learning-hub/creating-effective-skills/).
- **Instructions:** short, specific, testable rules scoped with `applyTo`, such as "use `pathlib` for file paths" rather than "write clean code". See [Defining custom instructions](https://awesome-copilot.github.com/learning-hub/defining-custom-instructions/).

Determinism in prompts is still guidance, not enforcement: a model can ignore a rule. Use tools, permissions, hooks, or CI where a requirement must hold, and validate behavior with representative scenarios. The full rule set is in the [AI customization instructions](common/.apm/instructions/ai-customization.instructions.md), and the common package applies it in its [workflow](common/README.md#workflow).

### Why not install entire collections

Installing a whole collection, or depending on it wholesale, looks efficient but works against a reliable setup:

- **Simplicity:** collections are general-purpose and support many harnesses, languages, and workflows. That complexity is rarely needed, and every extra agent or skill competes for attention during discovery.
- **Noise:** unused agents, skills, and instructions add context, discovery conflicts, and maintenance without benefit.
- **Control and security:** a live dependency on a large community repository can change behavior, tools, or permissions on update. Selecting and pinning individual parts keeps every change reviewable.
- **Flexibility:** selected parts can be tailored to personal and team conventions without fighting upstream defaults.
- **Compatibility:** many collections target other harnesses, such as Claude Code or Cursor, whose assumptions do not map cleanly to Copilot.
- **Licensing and provenance:** selecting individual parts makes it clear which license and source applies to what.

### Reference collections

Inspect these before authoring anything. Ranked by fit for a Copilot-based setup; last checked November 2026, so rankings and contents may change:

| Rank | Collection | What it is |
|---|---|---|
| 1 | [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/main) | GitHub's community catalog of Copilot instructions, agents, skills, and plugins, including authoring guidelines for agents and skills. Copilot-native, so closest to this setup. |
| 2 | [anthropics/skills](https://github.com/anthropics/skills/tree/main) | Anthropic's public Agent Skills examples, from the authors of the skills format. |
| 3 | [affaan-m/ECC](https://github.com/affaan-m/ECC/tree/main) | Large multi-harness system with many specialist agents and language skills, such as Python, Go, and Java patterns and testing. |
| 4 | [obra/superpowers](https://github.com/obra/superpowers/tree/main) | Agentic skills framework and development methodology, such as planning, test-driven development, and debugging workflows. |
| 5 | [garrytan/gstack](https://github.com/garrytan/gstack) | An opinionated personal Claude Code setup with role-based tools; useful for ideas, less for direct reuse. |

Review each part's license, tools, harness assumptions, and behavior before adopting it.

### Reuse registry

Each package README keeps a reuse registry: one row per reused part, so origin, version, and local changes stay traceable. See the [common registry](common/README.md#reuse-registry).

| Part | Source | Type | Synced | Local changes |
|---|---|---|---|---|
| Name and link in the package | Original upstream link | `Dependency`, `Adapted`, `Authored`, or `Ideas, modified` | Upstream commit and copy date | `None`, or a short summary |

- **Dependency:** official or authoritative parts used unchanged, declared in `apm.yml` with a pinned ref. For example, GitHub's [agents](https://github.com/github/awesome-copilot/blob/main/instructions/agents.instructions.md) and [agent skills](https://github.com/github/awesome-copilot/blob/main/instructions/agent-skills.instructions.md) authoring instructions are used directly because they are official and need no tailoring.
- **Adapted:** parts copied into `.apm/` and standardized, with changes beyond the standardization recorded. For example, the [Python package](python/README.md#reuse-registry) adapts ECC's [python-patterns](https://github.com/affaan-m/ECC/blob/main/skills/python-patterns/SKILL.md) and [python-testing](https://github.com/affaan-m/ECC/blob/main/skills/python-testing/SKILL.md) as references of its `python` skill.
- **Authored:** DevHub content, such as instructions, skill indexes, and references for which no suitable source exists, condensed from official documentation where possible.
- **Ideas, modified:** DevHub content that adopted specific elements from a source, such as the common agents' gates and formats from ECC.

Keep the upstream license and notices for adapted parts. Update the registry whenever a reused part is synced, as described in [maintaining reused content](#maintaining-reused-content).

### Official dependencies

The common package depends directly on these parts of [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/main), the official GitHub Copilot customization repository, pinned to one commit in its [`apm.yml`](common/apm.yml). They are used without changes: they are official, follow GitHub Copilot's own best practices, and contain nothing specific to DevHub, so tailoring them would only add maintenance and drift from the official guidance. DevHub-specific rules go into separate files on top, such as the common [AI customization instructions](common/.apm/instructions/ai-customization.instructions.md).

| Dependency | Applies to | Purpose |
|---|---|---|
| [`agents` instructions](https://github.com/github/awesome-copilot/blob/main/instructions/agents.instructions.md) | `**/*.agent.md` | Authoring custom agents |
| [`agent-skills` instructions](https://github.com/github/awesome-copilot/blob/main/instructions/agent-skills.instructions.md) | `**/skills/**/SKILL.md` | Authoring skills |
| [`instructions` instructions](https://github.com/github/awesome-copilot/blob/main/instructions/instructions.instructions.md) | `**/*.instructions.md` | Authoring instruction files |
| [`prompt` instructions](https://github.com/github/awesome-copilot/blob/main/instructions/prompt.instructions.md) | `**/*.prompt.md` | Authoring prompt files |
| [`hooks` instructions](https://github.com/github/awesome-copilot/blob/main/instructions/hooks.instructions.md) | `.github/hooks/**`, `hooks/**` | Authoring hooks |
| [`create-agentsmd` skill](https://github.com/github/awesome-copilot/blob/main/skills/create-agentsmd/SKILL.md) | On request | Generating a repository `AGENTS.md` |
| [`acquire-codebase-knowledge` skill](https://github.com/github/awesome-copilot/blob/main/skills/acquire-codebase-knowledge/SKILL.md) | On request | Mapping and documenting an existing codebase |
| [`ai-prompt-engineering-safety-best-practices` instructions](https://github.com/github/awesome-copilot/blob/main/instructions/ai-prompt-engineering-safety-best-practices.instructions.md) | All files | Prompt engineering and responsible AI practices |
| [`devops-core-principles` instructions](https://github.com/github/awesome-copilot/blob/main/instructions/devops-core-principles.instructions.md) | All files | DevOps culture and delivery metrics |
| [`git-commit` skill](https://github.com/github/awesome-copilot/blob/main/skills/git-commit/SKILL.md) | On request | Conventional Commits, applied internally by Engineer for R0 `COMMIT` |

The first five are the official authoring guidance used for [managing AI customizations](#managing-ai-customizations). The [common registry](common/README.md#reuse-registry) records the pinned commit; update it as described in [maintaining reused content](#maintaining-reused-content).

### Runtime-managed model selection

The common agents omit `model` declarations and do not pass model overrides. The user can change a supported runtime selection without editing every agent, and a role such as Engineer can handle both small fixes and complex work without a fixed role tier. The [Orchestrator's agent registry](common/.apm/agents/orchestrator.agent.md#agent-registry) describes roles and relative task complexity; it is advisory, not a routing table or model assignment. Selection and inheritance depend on the session and harness; see [VS Code model selection](https://code.visualstudio.com/docs/agent-customization/language-models) and its [subagent rules](https://code.visualstudio.com/docs/agents/run/subagents).

> The problem of edit tools not being available was found only in Claude models (as of 2026-11-07); this is likely a bug and may be fixed in the future. However, even if that bug is fixed in the future, the auto-selection of models explained below is still the better option, as explained below (in short better cost effectiveness, flexibility per task type (not a hardcoded model for an agent, complexity of a task given to an agent may vary), etc.).

This design reduces manual model-list maintenance and the risk of stale identifiers, changed aliases, or pins that fail or silently behave differently across hosts. GitHub updates Fusion's model pool as models become available and are evaluated, but runtime selection does not guarantee compatibility or eliminate maintenance: workflow guidance, host support, and actual sessions still need checking.

For Copilot sessions, I prefer [Copilot Fusion](https://docs.github.com/en/copilot/concepts/models/copilot-fusion) when available. **Fusion Standard** is my preference for a cost/quality trade-off which I recommend always using; **High** or **Max** should generally be skipped because these result in very low cost effectiveness by selecting high models like Opus by default while in my experience the task can easily be handled by lower cost models. So, select **Standard** by default and avoid **High** and **Max** in general. Fusion can select a suitable model, reasoning effort, and execution pattern for task difficulty, but cost and quality depend on the actual task. Fusion operates separately from subagents and does not start them or guarantee routing or inheritance for each worker. For example, any adaptation between a simple and a complex Engineer task is contingent on the selection actually used in that session; verify host behavior rather than assume it.

Subagents isolate intermediate work from the coordinator's context, reducing unrelated context pollution, but repeated instructions and context can increase total tokens and cost. Neither delegation nor runtime selection guarantees savings. General coding-capable Claude and GPT models can both perform engineering work; quality and cost vary by model and task, so validate results rather than assume equivalence. Compare manually selected models using the official [model comparison](https://docs.github.com/en/copilot/reference/ai-models/model-comparison), [supported models](https://docs.github.com/en/copilot/reference/ai-models/supported-models), and [models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing) references. Deterministic routes, route-dependent review, and testing are defenses, not guarantees that every change is reviewed or correct.

### Custom instructions in subagents

When Copilot runs a custom agent as a subagent, it does not follow the repository's custom instructions by default; only agents the user selects do. Every worker agent in the shared packages therefore sets `include-custom-instructions: true`, so workers that plan, design, edit, document, or review apply the same `AGENTS.md`, coding, documentation, and other scoped standards as the entry agent. Without it, a worker only sees the context in its delegation prompt and can silently ignore project conventions. Entry agents such as the Orchestrator do not need it. See [creating custom agents for Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli).

VS Code recognizes the field for the Copilot harness, but [does not forward it](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference#_copilot-specific-configuration) when converting agent files for the session runtime. Keep it for runtimes that honor it, and keep passing applicable guidance paths in each delegation prompt, as the common Orchestrator does, rather than relying on the field alone.

### Agent configuration

All seven common agents explicitly declare `tools: ['*']` and omit `model`. The wildcard requests every tool available to the host; omitting `model` leaves model selection to the runtime. These are deliberate package-wide compatibility choices, not least-privilege boundaries or claims that every role needs every tool. Keep them as a shared invariant unless the design is deliberately revisited.

The wildcard follows a local compatibility failure: an invoked worker did not expose the declared file-edit tools and returned `BLOCKED`. Requesting `['*']` avoids depending on inconsistent per-tool aliases or filters across roles, but cannot create tools the host does not provide. In this trusted local setup, the owner also observed fewer repetitive allow prompts with the explicit wildcard; this is a local observation, not a portable guarantee. See GitHub's [tool configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration#tools) and VS Code's [custom-agent file reference](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference#_harness-compatibility).

Keep five separate questions in view:

- **Harness support:** the selected host and harness decide which agent-file fields, extension tools, and MCP integrations they support. See [moving to the Copilot harness](https://code.visualstudio.com/docs/agents/run/move-to-copilot#_why-move-to-the-copilot-harness).
- **Available tools:** the host, extensions, MCP servers, and current session determine what tools exist. A file-edit tool and a terminal-execution tool are separate capabilities.
- **Tool selection:** `tools: ['*']` requests all tools the host makes available; it does not guarantee availability or create missing capabilities.
- **Role and scope:** agent instructions describe permitted work, paths, command use, and delegation. They guide the agent; they are not hard enforcement.
- **Approvals and sandboxing:** host permission settings decide when actions need approval, while sandboxing limits some terminal access. These controls are separate, sandboxing does not cover every tool, and organization policy may restrict both. Review [approvals and permissions](https://code.visualstudio.com/docs/agents/run/approvals#_permission-levels) and [scoped approvals in Copilot sessions](https://code.visualstudio.com/docs/agents/run/approvals#_scope-approvals-in-copilot-sessions).

The wildcard can expose powerful operations, and role instructions or post-run review cannot undo leaked secrets, destructive commands, or live-system effects. Keep host permissions and confirmations appropriate to the workspace and your organization's policy; do not carry this compatibility choice unexamined into untrusted or production environments. The common workflow's review route is route-dependent, not a guarantee that every change receives a separate reviewer or a different model family.

To test actual file-edit capability in a fresh session, first prepare a disposable scratch directory and choose two new, explicit paths inside it: `engineer_probe.py` and `documenter_probe.md`. Do not point them at existing work. Send these as two successive requests to Orchestrator, replacing the paths with their absolute paths:

```text
First request: Have Engineer implement a tiny Python function named capability_probe that returns "engineer-ok" in <scratch>/engineer_probe.py. Use a direct file-edit tool only; do not use shell commands to create or edit files. Read the file back. Report the tools actually invoked and whether editing and readback succeeded. If the needed tool is unavailable, report BLOCKED and the missing capability.

Second request, after the first route finishes: Have Documenter write the single line "documenter-ok" in <scratch>/documenter_probe.md using a direct file-edit tool, then read it back. Do not run shell commands. Report the tools actually invoked and whether editing and readback succeeded; report BLOCKED and the missing capability if a needed tool is unavailable.
```

Let the normal routes and gates run; these requests do not authorize bypassing them. A separate, optional harmless command probe can test terminal execution when authorized; successful editing does not prove execution access. Inspect the returned trace and readback, not just tool declarations or static compilation. Remove only the two disposable files if appropriate; do not broadly delete the scratch directory or other work.

### How guidance is layered

```text
User request: scope and acceptance criteria
    |
    v
Entry agent (Orchestrator) -> worker agents: roles, tools, outcomes
    |
    +-- Reused instructions and skills: general knowledge (the 80%)
    +-- Common package instructions: personal standards (the 20%)
    +-- Stack packages: language and tool instructions, skills with references
    +-- Root AGENTS.md: local facts, routes to owning documentation
    +-- Scoped repository instructions: only when path targeting adds value
    |
    v
Implementation, documentation, review, with validation and a reported trace
```

The diagram shows context composition, not precedence or a promise that every file loads automatically. Keep each topic in one owner and link to it; do not copy standards into agents or repositories. Start with one root `AGENTS.md`; add a nested one only when a component has materially different, consequential constraints that a link cannot cover.

### Language and framework guidance

Language and framework guidance, such as Python, Go, FastAPI, or Spring Boot, can live in instructions, skills, or both. Collections differ: [awesome-copilot](https://github.com/github/awesome-copilot/tree/main) uses long instructions per language, while [ECC](https://github.com/affaan-m/ECC/tree/main) uses skills such as `python-patterns` and `python-testing` behind a short instruction. The choice comes down to when each primitive enters the context and what it costs:

| Primitive | When it enters the context | Cost | Best for |
|---|---|---|---|
| Instruction with `applyTo` | Automatically, whenever matching files are involved | The full text, every time | Short, mandatory rules and validation commands |
| Skill `SKILL.md` | When the model judges that the description matches | Only the description until used | Procedures, decision rules, gotchas |
| Skill `references/*.md` | Only when the skill points to it for the current task | Nothing until opened | Large topic detail: patterns, testing, tooling |

Each approach alone has a weakness. Instructions only load reliably, but a long language file is loaded on every edit of a matching file, including one-line fixes. Skills only are cheap, but loading depends on the model matching a description, so they are sometimes skipped. DevHub therefore combines them:

- **Language instruction:** short, scoped by `applyTo` to the language's files. It holds toolchain choices, mandatory rules, and exact validation commands, and it explicitly points to the language skill. Because the instruction loads deterministically, so does the pointer to the skill.
- **Language skill:** an index with steps and gotchas that opens one reference file per task, such as `references/testing.md` when writing tests. Detail that the task does not need never loads.
- **Framework skills:** separate skills, such as `fastapi` or `springboot`, rather than references. Framework files cannot be told apart by `applyTo` (FastAPI code is `*.py`), frameworks are optional per repository, and they have their own triggers. A framework instruction is the exception when the framework has distinctive files, such as Spring `application*.yml`.
- **Repository `AGENTS.md`:** states the stack, framework, and versions in use, so agents know which skills apply.

```text
Common instructions (language-neutral)     coding, security, documentation, Git
  +-- Language instruction (applyTo)       python.instructions.md: rules, commands, pointer
        +-- Language skill (on demand)     skills/python/SKILL.md: index and gotchas
        |     +-- references/patterns.md   idioms, typing, errors
        |     +-- references/testing.md    test layout, fixtures, mocking
        |     +-- references/tooling.md    toolchain and dependencies
        +-- Framework skills (on demand)   skills/fastapi/SKILL.md
Repository AGENTS.md                       stack, versions, and commands in use
```

Apply the [80/20 rule](#the-8020-rule-reuse-then-tailor) to the content as well. Models already know general idioms, so the owned parts, the instructions and skill indexes, keep only what changes the output: personal toolchain choices, version-specific rules, frequent model mistakes, and exact commands. Every file ends with links to the official documentation.

Most reference content is copied from the [reference collections](#reference-collections), mainly ECC skills and awesome-copilot instructions, and then standardized: one reference file per source, a standard header with the source link and a precedence rule, upstream skill framing removed, and official documentation links added. DevHub-specific defaults, such as toolchain choices or the Dockerfile rules, go into the instructions or an authored reference rather than into the copied text. Copying instead of depending on the collections gives full control over the content and its integration with DevHub conventions, while the main content still comes from well-maintained sources, which avoids the heavy work of writing and maintaining it from scratch. Official parts that need no tailoring remain pinned dependencies; see the [reuse registry](#reuse-registry).

### Package design

Packages are split so a repository loads the baseline and opts in to only the stacks it uses:

| Package | Contents | Installed |
|---|---|---|
| [common](common/README.md) | Agents, language-neutral instructions, workflow skills | Always |
| [python](python/README.md), [java](java/README.md), [go](go/README.md), [rust](rust/README.md) | Language instructions, language skills with references, and framework skills | Opt in per language |
| [containerization](containerization/README.md), [iac](iac/README.md) | Tool instructions and skills with references: Docker, Kubernetes, and Helm; Ansible, Terraform, and Bicep | Opt in per tool area |

Every stack package declares `devhub-common` as a dependency in its `apm.yml`, so the common agents and standards are always installed with it; stack packages only add to them.

Not every repository uses every language, and installing all of them would work against a reliable setup:

- **Discovery budget:** an instruction for files a repository does not have never loads, but every installed skill description competes for attention during discovery. A Python repository should not carry Java and Rust skills.
- **Noise:** unused guidance adds context, possible conflicts, and maintenance, the same reason DevHub does not [install entire collections](#why-not-install-entire-collections).
- **Independent versions:** each stack package has its own version, changelog, and reuse registry, so a Go update does not touch Python consumers.

A stack package has the same layout for every language or tool:

```text
packages/apm/<stack>/
  apm.yml
  README.md                                   contents and reuse registry
  CHANGELOG.md
  .apm/instructions/<name>.instructions.md    one per language or tool
  .apm/skills/<name>/SKILL.md                 index, steps, and gotchas
  .apm/skills/<name>/references/patterns.md   always present
  .apm/skills/<name>/references/<topic>.md    optional: conventions, testing, tooling, and similar
  .apm/skills/<framework>/SKILL.md            optional, one per framework
```

Every instruction states that the common instructions always apply and adds only its stack's rules on top; every instruction, skill, and reference ends with links to the official documentation.

Repositories with their own extras, such as the homelab repositories, use the common and stack packages plus their own `AGENTS.md` and repository customizations. A separate domain or project package is only worth it when several repositories share extras that fit no stack package; none is needed for now, so the former homelab placeholder package was removed.

> Note to self: Python is my primary language, but Java (with Kotlin), Go, and Rust packages exist as well. The layout is the same for each, the sources are available anyway, and reading through well-curated language guidance is a fun way to learn. Packages for languages I rarely use stay small until a project needs them.

---

## Repository setup

Each consumer repository needs its own checked-in `apm.yml` and `apm.lock.yaml`, plus installation from that repository root. The optional [parent-workspace setup](../../docs/GETTING-STARTED.md#ai-customizations) is an additional convenience, not a replacement.

1. Inspect existing manifests, instructions, skills, and documentation. Preserve useful local customizations rather than replacing them.
2. Declare the common dependency in `apm.yml`, adapted to the repository:

   ```yaml
   name: personal-project
   version: 1.0.0
   targets:
     - copilot
   dependencies:
     apm:
       - CollinPoetoehena/DevHub/packages/apm/common
       - CollinPoetoehena/DevHub/packages/apm/python # one entry per stack in use
   ```

   Add [stack packages](#package-design) only for the languages and tools the repository uses, add domain packages only when relevant, and use pinned references for reproducible resolution.
3. Author one root `AGENTS.md` as described in [authoring repository guidance](#authoring-repository-guidance).
4. With [APM installed](https://microsoft.github.io/apm/getting-started/installation/), run from the repository root:

   ```sh
   apm install --only apm --target copilot
   ```

   For Copilot, agents and instructions deploy under `.github/` and skills under `.agents/skills/`. These are deployment artifacts, not an authoring source. Version `apm.yml`, `apm.lock.yaml`, and the deployed customizations; keep `apm_modules/` and `.apm-local/` ignored. See APM's [what to commit](https://microsoft.github.io/apm/quickstart/#3-install-a-package). Resolve policy or collision failures rather than forcing replacements.
5. Verify activation.

### Verify activation

A manifest, a successful installation, and correct behavior are separate checks:

- **Static:** validate sources as described in [validation](#validation).
- **Deployment:** confirm the target received the agents, instructions, and skills.
- **Discovery:** start a fresh chat with the **Copilot** session target and confirm the Orchestrator appears and the root `AGENTS.md` is read. Discovery rules differ per harness.
- **Behavior:** run representative tasks, such as the scenarios in the [common package](common/README.md#consumption-and-validation), and check routing, reports, and validation.

Instructions guide behavior; tests, CI, permissions, and approvals enforce it. Report unverified discovery or behavior explicitly.

---

## Authoring repository guidance

Create one root `AGENTS.md` per project. Every line should supply context an agent would otherwise miss, or route it to the authoritative source:

- Link to the README for purpose and scope, to architecture or guidelines for decisions, and to area READMEs for component details. Say when to read each, rather than asking the agent to read everything.
- Inline only consequential local constraints: unusual conventions, compatibility boundaries, sensitive operations, generated-source ownership, or validation the agent could miss.
- Do not repeat shared standards from packages or facts maintained in metadata, scripts, or CI.
- Do not put private paths, inventories, or operational values in public instructions.

```markdown
# Repository Agent Guidance

Read [README.md](README.md) for purpose and scope.

## Find the owning context

- Read the affected area's README for contracts and validation.
- Consult the architecture guide before changing component boundaries.

## Local constraints

- Record only consequential repository-specific agent guidance here.
```

Add scoped instructions under `.github/instructions/` or local skills under `.agents/skills/` only for a demonstrated need, kept distinct from package-installed files.

---

## AI usage

> Note: this is an important additional section for myself personally to ensure I make the most of AI while maintaining core skills.

### Personal usage: stay the expert

Use AI as a colleague or assistant that amplifies my capabilities, not as a replacement for my thinking. These are personal reminders, not an exhaustive guide:

- **Stay the expert: Keep thinking, stay curious, and exercise your brain.** Do not blindly accept AI output or stop at a plausible answer. Understand (and ask if not clear) how and why things work, investigate what you do not understand, challenge assumptions, and keep reviewing and testing until you can explain and stand behind the result. Taking time to reason things through may be slower at first than simply accepting an answer, but it keeps my mind engaged, strengthens core skills, and helps me catch mistakes and make better decisions. Understanding how things work and seeing my skills grow is also part of what makes engineering fun and rewarding. Keep in mind, [“Slow is smooth, and smooth is fast.”](https://en.wiktionary.org/wiki/slow_is_smooth,_smooth_is_fast), which means that working carefully and methodically reduces mistakes and ultimately leads to greater speed and efficiency than rushing. Speed should be balanced with care, deliberation, and quality; precision and control eventually produce speed. AI can make mistakes; responsibility for quality and final decisions stays with me.
- **Engineering judgment remains the differentiator.** Producing code is only part of engineering. Architecture, domain understanding, boundaries, technology trade-offs, priorities, scalability, maintainability, and testing, rollout, and operational risks require judgment. AI can explore options and expose blind spots; I must decide what fits the actual problem and own the consequences.
- **Think first, rather than defaulting immediately to AI.** Pause to frame the problem, recall what I already know, and form an initial idea or hypothesis. Make a proportionate attempt myself before asking for help; independent thinking matters, but there is no need to stay stuck just to avoid using AI.
- **Ask myself questions and sketch to solidify understanding.** Can I explain this in my own words? Why does it work, what am I assuming, and what would change or fail under different conditions? Use those questions to find gaps, then investigate or ask AI for a focused explanation. Sketch figures, diagrams, relationships, or flows to make the idea concrete; physical paper is often quicker and easier for rough thinking, but digital drawing works too. The goal is better understanding, not a polished diagram.
- **Troubleshoot actively and learn from the process.** Do not just copy-paste commands and relay their output to AI. Understand why each command is suggested, how its options work, what it reads or changes, and what result would support or rule out the hypothesis before running it. Read and interpret the output myself, update my hypothesis, and ask about anything unclear. Use AI to help reason through the evidence and explain the cause and fix so I can recognize and investigate similar problems next time instead of just copy-pasting the commands and not learning from the process, resulting in full-dependency on AI which you want to avoid by applying the above.
- **Amplify skills, do not replace understanding and thinking (avoid "brain rot").** Let AI handle much of the coding, writing, and repetitive execution; I do not need to do every task manually to remain capable. Still, use small, familiar tasks as low-stakes practice: recall a common command such as `grep` or a basic SQL query, check `man <command>` or local documentation when needed, try a small example, or write a short routine email yourself. Repeating these simple tasks keeps everyday skills fluent and builds confidence working without AI; it may take a little longer, but that practice can be worthwhile. Save AI for work where it adds more value, especially unfamiliar, complex, repetitive, or time-consuming tasks, and use it to help when you are stuck. Whatever does the drafting or execution, understand the problem and result well enough to direct the work, review it critically, debug it, and verify it. Use AI to extend what I can do, not to become unable to reason or work without it; avoid deactivating your thinking because it leads to "brain rot".
- **Use AI strategically, not maximally.** Brainstorming, research, explanations, reviews, code/tests, automation, and documentation can benefit. Complex, unfamiliar, or high-impact work especially benefits from exploring alternatives and challenging assumptions, while decision-making stays human. Optimize for speed, quality, learning, and insight, not the amount of AI used.
- **Keep context and sources trustworthy.** Start a fresh chat for a new task or stale context. Check claims against official documentation, actual code, tests, and logs rather than treating fluent answers as evidence. Use approved tools for work and do not share secrets or restricted information; a paid subscription alone does not establish safety.
- **The future of Software Engineering.** Less focus on manual typing, more on architecture, strategy, domain logic, and system thinking — engineers shift toward being architects, designers, analysts, reviewers, with value moving from writing code to problem-solving and engineering judgement.

[DRIVE](https://www.robertpeake.com/ai/drive) (Robert Peake) is a five-step discipline for working with AI. AI makes producing work cheap, so the hard parts move to both ends: *judgment* at the front (what is worth doing, and to what standard) and *verification* at the back (whether the result is actually right). The middle can go to the machine; trust my practice, not the model.

```text
Decide --> Request --> Iterate --> Validate --> done --> Evolve
              ^                        |
              +------- not yet --------+
```

- **D - Decide:** define what "done" means and the standard, in one sentence, before any request. It keeps the task mine and tells the loop when to stop; without it, work is unbounded.
- **R - Request:** brief intent, context, constraints, success criteria, and assumptions; agree the plan first. Unstated assumptions are the usual cause of fluent but wrong results.
- **I - Iterate (can also be called Isolate):** read output as it takes shape and steer it; correct small errors early and test each suggestion against "done". Limit parallel agents to what I can still oversee. In other words, break down complex tasks into manageable parts and handle them sequentially to maintain control and accuracy.
- **V - Validate:** check the result against the criteria from Decide using evidence (tests, real figures, a second source), sized to the stakes. A confident tone is not evidence.
- **E - Evolve:** after the work, debrief and promote lessons into reusable context: standards, references, templates, or instructions (see [maintenance and validation](#maintenance-and-validation)). Prune stale rules, and check whether I could redo the work without AI.

Decide frames the loop; Request, Iterate, and Validate repeat until "done" is met; Evolve improves what the next task starts from.

> **Personal Conclusion:** AI is a game changer for software engineers and in life when used wisely. Let it do much of the drafting, coding, and routine work so I can focus on understanding the problem, making decisions, and solving the right things. But I must keep thinking, stay curious, try to understand what it produces, and review and verify what it produces rather than follow it blindly. That active understanding and growth is not just how I stay capable and responsible; it is also part of what makes the work enjoyable. AI should amplify my abilities, not replace my understanding or judgment; I remain responsible for the work and its consequences.

### Prompt engineering

Prompt engineering means shaping input to get more accurate, useful output:

- **Context first; scale planning to the task.** Give the goal, relevant code, project structure, documentation, constraints (including language/framework versions), and acceptance criteria. For complex or multi-part work, start a focused new chat, let AI analyze that context and propose a plan, then execute small steps using the agreed context and plan. For example, plan testing across the repository before implementing tests per domain/package; follow the [common coding instructions](common/.apm/instructions/coding.instructions.md). For one isolated test, function, or formatting fix, ask directly: unnecessary planning adds latency and token cost.
- **Show the target.** Supply examples of desired input/output or existing code/style to match; specify output format, length, and tone when needed.
- **Set boundaries.** State exclusions such as no unrelated edits or new dependencies. Assign a role when a particular review perspective helps.
- **Iterate and challenge.** Treat the first result as a draft, refine it with feedback, and request assumptions, trade-offs, and a concise explanation for difficult problems. An explanation is not proof of correctness.
- **Reuse what works.** Save recurring requests and procedures through the appropriate [customization type](#concepts), rather than rewriting or duplicating guidance.

See the official [OpenAI](https://developers.openai.com/api/docs/guides/prompt-engineering), [Gemini](https://ai.google.dev/gemini-api/docs/prompting-strategies), and [IBM](https://www.ibm.com/think/topics/prompt-engineering) guides for more detail.

---
---

## Working with agents

### Choosing an agent

Select the common **Orchestrator** for all engineering work. It routes each request with a fixed routing table, delegates to Planner, Architect, Engineer, Documenter, and Reviewer, asks for approval before planned implementation, invokes Learner for evidence-based workflow evaluation when learning signals occur, and ends with a trace of each step, tools used, and copy-ready Git add-and-commit shell command(s) when eligible. The [common package](common/README.md#workflow) owns the routes, outcomes, and reports. Use the built-in agent for quick ad hoc questions when the workflow adds nothing. This ensures consistent routing, accountability, and traceability across all engineering tasks.

### Recommended Chat setup

For agent work in a trusted DevHub workspace:

1. In VS Code Chat, select the **Copilot** session target for this workflow. The **Local** harness is the legacy implementation; review the [reasons to move](https://code.visualstudio.com/docs/agents/run/move-to-copilot#_why-move-to-the-copilot-harness) and compatibility before changing an existing setup.
2. Select **Orchestrator** and, when available, start with **Fusion Standard** as described in [runtime-managed model selection](#runtime-managed-model-selection). For this trusted workspace, I recommend **Assisted** as the default permission level when its reduced interruptions fit the risk; configure `chat.permissions.default` for new Copilot sessions. Assisted still prompts for actions the judge does not approve, and the LLM judge can make mistakes. **Manual** remains VS Code's default and requires confirmation for actions not otherwise approved.
3. **Autopilot** is a separate, higher-trust agent mode that auto-approves all tools; it is not an added safety layer on top of Assisted. Use it only when you accept that behavior and trust the workspace (recommended; I usually enable it by default).
4. For this trusted local setup, terminal sandboxing is left off to avoid its filesystem and network restrictions. This gives terminal commands broader access; sandboxing is independent of permission level and does not cover every tool. Keep or enable it when its restrictions better fit the task.

Review your own VS Code permission and approval settings before use, including `chat.permissions.default`, tool and URL approval scope, terminal approval, and sandbox settings. Do not copy settings blindly: choose the balance that fits your workspace, account, and organization policy. See the official [permission levels](https://code.visualstudio.com/docs/agents/run/approvals#_permission-levels), [scoped approvals](https://code.visualstudio.com/docs/agents/run/approvals#_scope-approvals-in-copilot-sessions), and [terminal sandboxing](https://code.visualstudio.com/docs/agents/run/agent-sandboxing) guidance.

---

## Maintenance and validation

Maintain package sources under `.apm/`, never installed copies. Update a package README and changelog with its changes, and this guide for the shared approach. Retain only reusable, evidence-backed lessons in their owning source; this is explicit maintenance, not model training. The common Orchestrator does this as a lightweight final [learning step](common/README.md#learning): repository lessons go into repository customizations, and common lessons into the common package source when it is editable in the workspace, or are otherwise proposed. Source edits do not refresh running sessions or installed customizations: reinstall, then start a fresh chat.

### Managing AI customizations

Creating or changing agents, skills, instructions, prompts, hooks, or `AGENTS.md` files follows the official GitHub Copilot guidance, not DevHub-specific rewrites of it. The [official dependencies](#official-dependencies) supply it: the [agents](https://github.com/github/awesome-copilot/blob/main/instructions/agents.instructions.md), [agent skills](https://github.com/github/awesome-copilot/blob/main/instructions/agent-skills.instructions.md), [instructions](https://github.com/github/awesome-copilot/blob/main/instructions/instructions.instructions.md), [prompt](https://github.com/github/awesome-copilot/blob/main/instructions/prompt.instructions.md), and [hooks](https://github.com/github/awesome-copilot/blob/main/instructions/hooks.instructions.md) instructions load automatically for matching files, and the [`create-agentsmd`](https://github.com/github/awesome-copilot/blob/main/skills/create-agentsmd/SKILL.md) skill helps write a repository `AGENTS.md`. On top of them, the common [AI customization instructions](common/.apm/instructions/ai-customization.instructions.md) add only DevHub's design rules: deterministic workflows, reports, model selection, and validation. In VS Code, the built-in `agent-customization` skill covers file formats and frontmatter as well.

### Updating APM packages and the CLI

From the consumer repository root, preview and then apply updates:

```sh
apm update --target copilot --dry-run
apm update --target copilot
```

To update only the common package:

```sh
apm update CollinPoetoehena/DevHub/packages/apm/common --target copilot
```

Review manifest, lockfile, and deployed-file changes, update the [reuse registry](#reuse-registry) when upstream parts change, and repeat the [activation checks](#verify-activation). For local dependencies, such as DevHub's `./packages/apm/common`, run `apm install --only apm --target copilot` to refresh the deployment. Upgrade the CLI itself with its install method, such as `brew upgrade apm` or `apm self-update`.

Repositories in the fleet do not need these steps routinely: the [APM sync workflow](../../docs/github-actions/workflows/apm-sync.md) checks for updates on every push to `main` and weekly, and opens a pull request only when files change.

### Maintaining reused content

Reused content stays maintainable because every part has one original source link, a synced commit, and a recorded list of local changes in its package's reuse registry. Update a part in five steps:

1. **Check upstream.** Open the source link from the registry and compare the upstream file with the synced commit, for example with the file's history or GitHub's compare view (`https://github.com/<owner>/<repo>/compare/<synced>...main`). Stop when nothing relevant changed.
2. **Copy the new content.** Replace the body of the local file with the new upstream content and reapply the standardization: keep the standard header and official references, and remove the upstream frontmatter, skill framing, and the sections listed under local changes.
3. **Check the diff.** Review `git diff` against the current version, so DevHub-specific changes recorded in the registry are not lost and new upstream content does not conflict with the common or stack instructions.
4. **Record the update.** Update the synced commit and date and the local changes in the registry, and add an entry to the package changelog.
5. **Validate.** Run the package [validation](#validation) and check the links.

For pinned dependencies, change the `#<commit>` ref in `apm.yml`, reinstall, and review the deployed-file changes the same way. Sync when you work on a package anyway or when upstream changed substantially; do not chase every upstream commit.

### Validation

From the package directory, validate agents and instructions without installing:

```sh
apm compile --validate --local-only
```

Separately check skill metadata, links, and instruction scopes. For deployment checks, install into a fresh scratch root:

```sh
scratch=$(mktemp -d -t devhub-apm-check.XXXXXX) &&
apm install --only apm --target copilot --root "$scratch"
```

Static validation and deployment do not prove discovery or behavior; complete the [activation checks](#verify-activation) and report passed, failed, skipped, and blocked checks.

---

## DevHub's own setup

DevHub consumes the common package through its [root manifest](../../apm.yml) as a local dependency. The [root AGENTS.md](../../AGENTS.md) routes agents to the [repository overview](../../README.md), [packages](../README.md), [tools](../../tools/README.md), and focused documentation, so DevHub needs no nested `AGENTS.md` files and no separate repository-wide Copilot instruction file.

---

## References

This guide records DevHub's choices and essential concepts. Use these official sources for full theory, supported formats, commands, and current harness behavior:

### Customization and distribution

- [APM overview](https://microsoft.github.io/apm/): dependency management and the distinction between distribution and runtime.
- [APM primitive authoring](https://microsoft.github.io/apm/producer/author-primitives/): instructions, agents, skills, prompts, and package structure.
- [APM consumer guide](https://microsoft.github.io/apm/consumer/): installation, dependencies, and reproducibility.
- [APM targets matrix](https://microsoft.github.io/apm/reference/targets-matrix/): supported primitives, deployment locations, and target-specific limitations.
- [APM compile reference](https://microsoft.github.io/apm/reference/cli/compile/): root-context generation, options, and output ownership considerations.
- [AGENTS.md](https://agents.md/): the cross-agent repository instruction convention.
- [VS Code customization overview](https://code.visualstudio.com/docs/agent-customization/overview): customization types and harness selection.
- [VS Code custom instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions): file formats, scopes, discovery settings, and verification.
- [Copilot CLI custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions): discovery and combined instruction sources.
- [Agent Skills specification](https://agentskills.io/specification): skill metadata and packaging.
- [VS Code agent skills](https://code.visualstudio.com/docs/agent-customization/agent-skills) and [custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents): activation and role configuration.
- [APM install reference](https://microsoft.github.io/apm/reference/cli/install/): deployment options and scratch-root validation.
- [APM update reference](https://microsoft.github.io/apm/reference/cli/update/) and [CLI self-update](https://microsoft.github.io/apm/reference/cli/self-update/): dependency refresh, pin handling, and upgrading the tool itself.
- [GitHub awesome-copilot](https://github.com/github/awesome-copilot), [Microsoft skills](https://github.com/microsoft/skills), and [Anthropic skills](https://github.com/anthropics/skills): collections to inspect before authoring another primitive.

### Agent execution and model selection

- [VS Code Chat](https://code.visualstudio.com/docs/agents/run/chat-view) and [agent harnesses](https://code.visualstudio.com/docs/agents/run/agent-harnesses): session targets and role selection.
- [Subagents](https://code.visualstudio.com/docs/agents/run/subagents) and [custom-agent file reference](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference): delegation, tools, and allowlists.
- [Custom agents configuration - GitHub Docs](https://docs.github.com/en/copilot/reference/custom-agents-configuration#tools): tool lists, aliases, and MCP tool selection; see the [common agent tool configuration](common/README.md#package-contents).
- [Approvals and permissions](https://code.visualstudio.com/docs/agents/run/approvals), [terminal sandboxing](https://code.visualstudio.com/docs/agents/run/agent-sandboxing), and [trust and safety](https://code.visualstudio.com/docs/agents/concepts/trust-and-safety): autonomous execution and security boundaries.
- [Auto model selection](https://docs.github.com/en/copilot/concepts/models/auto-model-selection), [Copilot Fusion](https://docs.github.com/en/copilot/concepts/models/copilot-fusion), and [model comparison](https://docs.github.com/en/copilot/reference/ai-models/model-comparison): current routing, controls, availability, and pricing.

### Prompt engineering and AI background

- [OpenAI prompt engineering](https://developers.openai.com/api/docs/guides/prompt-engineering?api-mode=responses): practical prompting guidance.
- [Gemini prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies): provider-specific techniques.
- [IBM prompt engineering](https://www.ibm.com/think/topics/prompt-engineering): prompting concepts and techniques.
- [The DRIVE method](https://www.robertpeake.com/ai/drive): a five-step discipline for working with AI (Decide, Request, Iterate, Validate, Evolve).
- [IBM: What are AI agents?](https://www.ibm.com/think/topics/ai-agents): background on agent concepts and architectures.

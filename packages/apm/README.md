# DevHub AI Customizations and APM

[APM](https://microsoft.github.io/apm/) distributes customization packages; the Copilot host and harness execute the work. This guide summarizes the selected architecture. [ADRs](docs/adrs/README.md) own decision reasoning, and [CONCEPTS.md](docs/CONCEPTS.md) owns general terminology.

The [source packages](#package-design) are separated by consumer: `guidelines-core` supplies shared repository guidance, while `development-core` and opt-in `development-*` packages supply local development capabilities. Thin Planner, Implementation Orchestrator, Implementer, and Reviewer agents compose focused skills, following the [roles-and-procedures decision](docs/adrs/workflow/WORKFLOW-AGENTS-AND-FOCUSED-SKILLS.md). Source readiness does not establish installation, host discovery, or synchronization.

## Table of Contents

- [Selected architecture](#selected-architecture)
- [Why create AI customizations](#why-create-ai-customizations)
- [Concepts](#concepts)
- [Choosing a workflow](#choosing-a-workflow)
- [How guidance is layered](#how-guidance-is-layered)
- [Package design](#package-design)
- [Agent configuration](#agent-configuration)
- [Repository setup](#repository-setup)
- [Maintenance and validation](#maintenance-and-validation)
- [Reference collections](#reference-collections)
- [Extra: Personal AI Usage Tips](#extra-personal-ai-usage-tips)

---

## Selected architecture

| Topic | Decision and rationale |
|---|---|
| Workflow | Separate Plan from Build and Test; larger work requires an approved plan and fresh execution session, while small, understood tasks may skip Plan. Implementation Orchestrator owns SIMPLE/STANDARD execution, followed by human Verify and Observe; see the [workflow ADR](docs/adrs/workflow/AI-DEVELOPMENT-WORKFLOW.md). |
| Roles and procedures | [Planner](development-core/.apm/agents/planner.agent.md) investigates and saves plans; [Implementation Orchestrator](development-core/.apm/agents/implementation-orchestrator.agent.md) coordinates execution. Focused skills supply reusable procedures; see the [role decision](docs/adrs/workflow/WORKFLOW-AGENTS-AND-FOCUSED-SKILLS.md). |
| Workers | [Implementer](development-core/.apm/agents/implementer.agent.md) owns bounded edits and checks; [Reviewer](development-core/.apm/agents/reviewer.agent.md) independently assesses quality, security, and project conformance without editing. |
| Shared context | STANDARD uses [sharing-context](development-core/.apm/skills/sharing-context/SKILL.md) to pass task memory to fresh workers, with serialized updates. |
| Guidance | Repository `AGENTS.md` plus shared scoped instructions; see the [layering ADR](docs/adrs/ai-customizations/GUIDANCE-INSTRUCTION-LAYERING.md). |
| Distribution | Use APM rather than maintain a custom package-distribution engine; see the [distribution ADR](docs/adrs/distribution-and-synchronization/DISTRIBUTION.md). |
| Package boundaries | Shared `guidelines-core` in participating repositories; agents/skills in local `development-core`, with instruction maps and skills in opt-in development stacks; see the [package-design ADR](docs/adrs/distribution-and-synchronization/PACKAGE-DESIGN.md). |
| Synchronization | [Repository fleet delivery](../../tools/repo/README.md#central-fleet-sync) exists under an older package contract; current-package integration and local development setup synchronization remain [separate work](docs/adrs/distribution-and-synchronization/SYNCHRONIZATION.md). |
| Customization depth | Thin guidance that preserves model reasoning and creativity; see the [creation ADR](docs/adrs/ai-customizations/AI-CUSTOMIZATION-CREATION.md). |
| Reuse | Native capabilities and selective tailoring, with upstream `#HEAD` references; see the [reuse ADR](docs/adrs/ai-customizations/REUSE-AND-TAILORING.md). |
| Model selection | Harness-managed routing, with Copilot Fusion Standard as the user default and a different reviewer model/provider preferred when supported; see the [model-selection ADR](docs/adrs/workflow/MODEL-SELECTION.md). |
| Role configuration | Explicit wildcard tools, role-specific worker listings and visibility, no fixed models; see the [configuration ADR](docs/adrs/workflow/MINIMAL-AGENT-CONFIGURATION.md). |

---

## Why create AI customizations

Capture durable standards, missing repository knowledge, and repeatable role boundaries once for humans and AI. Reuse native capabilities and suitable existing components; add only guidance that improves actual work. Specify outcomes and consequential constraints without taking the model through every detail.

The [creation ADR](docs/adrs/ai-customizations/AI-CUSTOMIZATION-CREATION.md) owns the purpose and detail boundary. The [reuse ADR](docs/adrs/ai-customizations/REUSE-AND-TAILORING.md) separately owns adoption decisions, source selection, and the 90/10 and 80/20 heuristics.

---

## Concepts

[CONCEPTS.md](docs/CONCEPTS.md) explains instructions, skills, agents, subagents, hooks, prompts, MCP, APM, and host/harness/model terminology, with authoritative references and the AI Coding Dictionary.

Separating vocabulary from project decisions keeps this README clean and the concepts clear without duplicating ADR reasoning.

---

## Choosing a workflow

Keep planning and implementation as two separate phases. Larger, unclear, cross-cutting, or consequential work first uses **Planner** to investigate and agree a saved plan; small, localized, already understood tasks may skip that phase. **Implementation Orchestrator** remains the single implementation entry point: give it the small request directly, or start a fresh execution session with the approved plan's absolute path and current-version approval. It chooses the execution mode:

- **SIMPLE**: obvious, localized, low-risk work with no behavior, security, dependency, configuration, or architectural impact. One fresh Implementer makes the edit and performs proportional checks; no independent review is required. Unexpected complexity escalates to STANDARD.
- **STANDARD**: all other work or uncertainty. Fresh workers investigate and implement bounded, dependency-aware tasks; only independent writes run in parallel. Integrated checks precede one fresh Reviewer covering quality, security, tests, and project conventions. Corrections return to Implementer and are rechecked.

The orchestrator works autonomously within the agreed request or plan and host permissions. It does not call Planner, combine the two phases, or repeatedly ask about resolved decisions. Missing required planning or a material change to the agreement stops execution for separate planning and approval; routine implementation choices remain autonomous. Required checks or independent review that cannot run are reported as blockers, not successes. Planning need and execution mode are separate: a small, well-understood behavior change can need STANDARD checks without a full plan.

**Planner** questions material choices in rounds, uses bounded built-in specialists, and saves only `<task-working-directory>/tmp/plan-<id>.md`. It stops for the user's active review and approval, without implementing. Keep that agreement available through execution and acceptance; retaining it afterward is optional unless project rules require it. The [workflow ADR](docs/adrs/workflow/AI-DEVELOPMENT-WORKFLOW.md#plan) owns its contents and handoff contract.

```text
Larger work -> Planner -> reviewed plan -> user approval -> stop
  -> fresh Implementation Orchestrator session with approved plan
Small, understood request -> Implementation Orchestrator directly
  SIMPLE   -> one Implementer -> proportional checks
  STANDARD -> fresh specialists + bounded Implementers -> integrated checks
           -> independent Reviewer -> fixes and rechecks as needed
  -> human Verify -> Observe
```

### Select a role

After installation and discovery verification, select the named custom agent using the host's supported picker or invocation mechanism. In VS Code, use the agent dropdown. The following are requests to the selected role, not skill slash commands:

```text
Planner: Investigate <change>, question material decisions, and save a plan.
Implementation Orchestrator: Make <small, understood change> and validate it.
Implementation Orchestrator: I approve the current plan at <absolute-plan-path>. Implement it.
```

Implementer and Reviewer are subagent-only workers in the source configuration, not additional user entry points. Native planning or review commands are separate host features, not aliases for these roles. Availability, syntax, metadata support, and delegation vary across hosts.

### Roles compose focused skills

Agents own the role, task lifecycle, and delegation boundaries; skills supply isolated reusable procedures such as [sharing-context](development-core/.apm/skills/sharing-context/SKILL.md), [ADR drafting](development-core/.apm/skills/adr/SKILL.md), and [issue drafting](development-core/.apm/skills/draft-github-issue/SKILL.md). Skills may call other skills without owning the whole implementation lifecycle. They may be discovered automatically or invoked explicitly; role selection makes the intended DevHub entry point visible without relying on selection of a workflow skill.

STANDARD uses the sharing-context skill before its first delegation. It manages a unique `<cwd>/tmp/MEMORY-<id>.md`, falls back to another permitted shared writable location when needed, and passes the absolute path and reading instructions in every worker prompt. The coordinator reconciles reports and serializes memory writes. These task artifacts are not the operating system's `/tmp` by default; consumers own their storage and ignore rules.

The [role decision](docs/adrs/workflow/WORKFLOW-AGENTS-AND-FOCUSED-SKILLS.md) owns the comparison with skills-first and other alternatives. The [workflow ADR](docs/adrs/workflow/AI-DEVELOPMENT-WORKFLOW.md) owns the single entry point and mode policy; [focused sessions and specialist context](docs/adrs/workflow/FOCUSED-SESSIONS-AND-SPECIALIST-CONTEXT.md) owns context isolation. Keep these wrappers thin and use native specialist capabilities where available rather than defining a role for every operation.

---

## How guidance is layered

Shared rules belong in repository-facing `guidelines-core`, independently of any local workflow; stack-specific instruction maps belong with their opt-in `development-*` packages. Each repository owns its root `AGENTS.md`, architecture, configuration, and local constraints. Specific language/tool guidelines refine shared defaults; agents and skills use those rules instead of copying them. Copilot consumes instruction files, while Claude calls its equivalent rules; retain the filenames and frontmatter required by the supported host. The packages are available as validated sources, but source organization does not prove installation, discovery, or runtime behavior.

See the [layering ADR](docs/adrs/ai-customizations/GUIDANCE-INSTRUCTION-LAYERING.md) for ownership, specificity, discovery limitations, and guidance versus enforcement.

### Authoring repository guidance

Prefer one concise root `AGENTS.md` linking to owning documentation and stating when to read it. Add nested guidance only for materially different subtree constraints that root links or scoped instructions cannot adequately express. Keep one-off requirements in the request and private project facts in their repository.

---

## Package design

The source design separates shared guidelines from local development packages:

- **Shared guidelines**: `guidelines-core` owns common engineering, security, testing, documentation, and AI-customization standards, adopted by participating repositories without agents or skills.
- **Local development core**: `development-core` owns the four workflow roles and focused generic skills, selected by team members using that workflow in a consumer-chosen local scope.
- **Opt-in development stacks**: `development-python`, `development-go`, `development-rust`, `development-java`, `development-containerization`, and `development-iac` own technology skills/resources and their scoped instruction maps.

`guidelines-core` is independently adopted by repositories for shared standards. `development-core` is selected by users who want the reusable workflow and generic skills; select only relevant `development-*` stacks alongside it. Each stack package depends on `development-core` for shared local capabilities, but does not install `guidelines-core`. Shared guidelines must not pull in workflow packages, and local development packages must not automatically deploy repository guidelines into the local scope. Stack instruction maps are the stack-bound exception, not copies of common standards. Genuinely repository-specific capabilities remain with their repository.

Consumers can choose user-wide, personal/work, team, or project-specific setups. For example, separate setups can serve `~/projs/personal` and `~/projs/work`, with Copilot CLI started in the chosen parent working directory and intended repositories added as task directories. File access does not prove customization inheritance; verify discovery in the chosen host and scope.

The [package-design ADR](docs/adrs/distribution-and-synchronization/PACKAGE-DESIGN.md) owns these boundaries and destinations. The [distribution ADR](docs/adrs/distribution-and-synchronization/DISTRIBUTION.md) separately chooses APM; the [synchronization TODO](docs/adrs/distribution-and-synchronization/SYNCHRONIZATION.md) records future automation. Eight package sources implement the split. Source validation does not install the packages, establish host discovery, or implement synchronization.

<a id="language-and-framework-guidance"></a>

### Language and tool guidance

Use scoped instruction maps within the relevant opt-in stack package. They refine the shared baseline and route to that stack's skills/resources. Add framework-specific rules when actual project use exposes a recurring convention or mistake; keep one-off choices local. Longer procedures belong in appropriate skills or references, not exhaustive always-loaded tutorials. Guidelines is the neutral term; retain the filenames and formats required by the intended AI tool.

---

## Agent configuration

Keep the four roles focused. All declare `tools: ['*']`; Planner declares `agents: ['*']`, and Implementation Orchestrator declares `agents: ['*', 'Implementer', 'Reviewer']`. Implementer and Reviewer set `user-invocable: false`. Other optional settings, including fixed models, are omitted. Wildcards permit available capabilities; they neither install tools nor override permissions or the roles' prose boundaries. The `agents` allowlist is a Local-harness field in the current [VS Code reference](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference); other harnesses can ignore it. Source removal does not prune old installed customizations or alter existing sessions.

Use the auto family / harness-managed router and **Copilot Fusion Standard by default**. Users can select a higher available tier when needed. The orchestrator prefers a different reviewer model or provider when the host permits selection; otherwise it uses the available model in a fresh reviewer context without blocking. No fixed per-role model is prescribed, and a fresh context alone does not establish provider diversity.

<a id="runtime-managed-model-selection"></a>

The [model-selection ADR](docs/adrs/workflow/MODEL-SELECTION.md) owns routing and tier rationale; the [configuration ADR](docs/adrs/workflow/MINIMAL-AGENT-CONFIGURATION.md) owns metadata and enforcement limitations. Agent and skill prose cannot enforce read-only access, independent review, or model choice; host permissions and actual tool and review evidence remain authoritative.

For model fundamentals and general capability/cost trade-offs, see [models and the agent loop](docs/CONCEPTS.md#models-and-the-agent-loop).

---

## Repository setup

The design separates repository guideline adoption from local workflow selection. A repository may declare `CollinPoetoehena/DevHub/packages/apm/guidelines-core` without adopting a workflow. A user who selects the workflow declares `development-core` and only the relevant stack packages. Consumers own dependency references, destinations, update policies, local context, and existing customization files.

The package source directories and manifests are ready for consumer selection. Use APM's documented commands and verify the host-specific destination and discovery for the chosen scope; DevHub has not implemented automatic local package installation, scope setup, or synchronization. The [package-design ADR](docs/adrs/distribution-and-synchronization/PACKAGE-DESIGN.md) owns package boundaries, and the [synchronization TODO](docs/adrs/distribution-and-synchronization/SYNCHRONIZATION.md) records future automation.

### DevHub's own setup

DevHub's [root manifest](../../apm.yml) declares only `guidelines-core`, not the generic local development environment. The eight source packages are in this directory; select `development-core` and any relevant stack separately when setting up a local development scope.

### Verify activation

During implementation, separately verify installation, discovery, and representative behavior in the intended CLI and VS Code scopes. Include parent-workspace and direct repository sessions where supported. Installed files do not prove activation or compliance.

---

## Maintenance and validation

### Maintaining reused content

Edit owning sources rather than installed copies; preserve consumer-owned additions. Review updates, attribution, licenses, permissions, compatibility, and collisions. The [reuse ADR](docs/adrs/ai-customizations/REUSE-AND-TAILORING.md) owns selective reuse and the stopping rule.

The [development-core manifest](development-core/apm.yml) and [guidelines-core manifest](guidelines-core/apm.yml) explicitly use `#HEAD` for upstream skills and authoring instructions. This intentionally follows the latest upstream default-branch revision when refreshed and resolved, rather than freezing a source commit. It is not a background updater: an existing lockfile can retain resolved revisions, and deployed files and running sessions do not update merely because upstream advances. Follow APM's [dependency guide](https://microsoft.github.io/apm/consumer/manage-dependencies/) and [lockfile reference](https://microsoft.github.io/apm/reference/lockfile-spec/) to refresh intentionally, inspect the resolved changes, and revalidate compatibility before use. Local stack dependencies remain local paths, not `#HEAD` references.

For later clarification of an ADR, the [ADR skill and template](development-core/.apm/skills/adr/SKILL.md) support an optional dated, same-document changelog. A substantially replaced decision follows supersession conventions.

### Validation

Run `apm compile --validate --local-only` from each of the eight source package directories. This validates local APM primitives without resolving upstream dependencies; separately check skill frontmatter, bundled links, and the [workflow scenarios](development-core/README.md). Static source validation does not establish host discovery or behavior. Package-source readiness does not install or activate customizations, synchronize consumer copies, prune installed files, or verify a host's destination mapping.

In each intended host, separately verify agent and skill discovery, required planning and fresh-session handoff for larger work, the small-task exception, SIMPLE/STANDARD selection, fresh-worker context sharing, dependency and write isolation, checks, and the independent Reviewer. Verify that only supported model and tool metadata takes effect; report unavailable capabilities rather than treating prose as proof.

---

## Reference collections

The [reuse ADR](docs/adrs/ai-customizations/REUSE-AND-TAILORING.md#source-selection-and-stopping) explains selection and review. Reference collections include [Awesome Copilot](https://github.com/github/awesome-copilot), [Anthropic Skills](https://github.com/anthropics/skills), [Matt Pocock's skills](https://github.com/mattpocock/skills/tree/main), [ECC](https://github.com/affaan-m/ECC), [Superpowers](https://github.com/obra/superpowers), and [gstack](https://github.com/garrytan/gstack). These are references, not installation checklists.

General terminology and official documentation links are in [CONCEPTS.md](docs/CONCEPTS.md).

---

## Extra: Personal AI Usage Tips

> Note: this is an important additional section for myself personally to ensure I make the most of AI while maintaining core skills. It is added at the bottom because it is extra for myself personally only, but still kept because it is a very important topic to understand and use correctly.

### Personal usage: stay the expert

Use AI as a colleague or assistant that amplifies my capabilities, not as a replacement for my thinking. These are personal reminders, not an exhaustive guide:

- **Stay the expert: Keep thinking, stay curious, and exercise your brain.** Do not blindly accept AI output or stop at a plausible answer. Understand (and ask if not clear) how and why things work, investigate what you do not understand, challenge assumptions, and keep reviewing and testing until you can explain and stand behind the result. Taking time to reason things through may be slower at first than simply accepting an answer, but it keeps my mind engaged, strengthens core skills, and helps me catch mistakes and make better decisions. Understanding how things work and seeing my skills grow is also part of what makes engineering fun and rewarding. Keep in mind, [“Slow is smooth, and smooth is fast.”](https://en.wiktionary.org/wiki/slow_is_smooth,_smooth_is_fast), which means that working carefully and methodically reduces mistakes and ultimately leads to greater speed and efficiency than rushing. Speed should be balanced with care, deliberation, and quality; precision and control eventually produce speed. AI can make mistakes; responsibility for quality and final decisions stays with me.
- **Engineering judgment remains the differentiator.** Producing code is only part of engineering. Solving problems, designing solutions, architecting systems, and weighing domain needs, boundaries, technology trade-offs, priorities, scalability, maintainability, and testing, rollout, and operational risks require my thinking and judgment. Break complex problems into manageable, executable tasks with clear boundaries, dependencies, and acceptance criteria; isolate tasks where they can genuinely stand alone. AI can propose a design or task breakdown and expose blind spots, but I must judge whether the proposed work is good: does it solve the right problem, fit the system, and justify its complexity? I decide what to pursue and own the consequences. For a related perspective on decomposing agent work into simple, composable workflows, see Anthropic's [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents).
- **Think first, rather than defaulting immediately to AI.** Pause to frame the problem, recall what I already know, and form an initial idea or hypothesis. Make a proportionate attempt myself before asking for help; independent thinking matters, but there is no need to stay stuck just to avoid using AI. Google's [People + AI Guidebook](https://pair.withgoogle.com/guidebook/) offers a human-centered design lens for thinking about how people work with AI.
- **Ask myself questions and sketch to solidify understanding.** Can I explain this in my own words? Why does it work, what am I assuming, and what would change or fail under different conditions? Use those questions to find gaps, then investigate or ask AI for a focused explanation. Sketch figures, diagrams, relationships, or flows to make the idea concrete; physical paper is often quicker and easier for rough thinking, but digital drawing works too. The goal is better understanding, not a polished diagram.
- **Troubleshoot actively and learn from the process.** Do not just copy-paste commands and relay their output to AI. Understand why each command is suggested, how its options work, what it reads or changes, and what result would support or rule out the hypothesis before running it. Read and interpret the output myself, update my hypothesis, and ask about anything unclear. Use AI to help reason through the evidence and explain the cause and fix so I can recognize and investigate similar problems next time instead of just copy-pasting the commands and not learning from the process, resulting in full-dependency on AI which you want to avoid by applying the above.
- **Amplify skills, do not replace understanding and thinking (avoid "brain rot").** Let AI handle much of the coding, writing, and repetitive execution; I do not need to do every task manually to remain capable. Still, use small, familiar tasks as low-stakes practice: recall a common command such as `grep` or a basic SQL query, check `man <command>` or local documentation when needed, try a small example, or write a short routine email yourself. Repeating these simple tasks keeps everyday skills fluent and builds confidence working without AI; it may take a little longer, but that practice can be worthwhile. Save AI for work where it adds more value, especially unfamiliar, complex, repetitive, or time-consuming tasks, and use it to help when you are stuck. Whatever does the drafting or execution, understand the problem and result well enough to direct the work, review it critically, debug it, and verify it. Use AI to extend what I can do, not to become unable to reason or work without it; avoid deactivating your thinking because it leads to "brain rot".
- **Use AI strategically, not maximally.** Brainstorming, research, explanations, reviews, code/tests, automation, and documentation can benefit. Complex, unfamiliar, or high-impact work especially benefits from exploring alternatives and challenging assumptions, while decision-making stays human. Optimize for speed, quality, learning, and insight, not the amount of AI used.
- **Keep context and sources trustworthy.** Start a fresh chat for a new task or stale context. Check claims against official documentation, actual code, tests, and logs rather than treating fluent answers as evidence. Use approved tools for work and do not share secrets or restricted information; a paid subscription alone does not establish safety.
- **Use voice input when typing slows you down.** You do not have to type every prompt: try [Windows Voice Typing](https://support.microsoft.com/en-us/accessibility/windows/use-voice-typing-to-talk-instead-of-type-on-your-pc) (`Windows + H`), [macOS Dictation](https://support.apple.com/guide/mac-help/use-dictation-mh40584/mac), or a tool like [Superwhisper](https://superwhisper.com/). Copilot is surprisingly tolerant of imperfect transcription; I have dictated entire feature specs and refactor plans while walking. Speaking can save typing time and let me stand up and think. Treat the transcript as a draft and review it for accuracy before sending.
- **The future of Software Engineering.** Less focus on manual typing, more on architecture, strategy, domain logic, and system thinking — engineers shift toward being architects, designers, analysts, reviewers, with value moving from writing code to problem-solving and engineering judgement.

[DRIVE](https://www.robertpeake.com/ai/drive) (Robert Peake) is a five-step discipline for working with AI. AI makes producing work cheap, so the hard parts move to both ends: *judgment* at the front (what is worth doing, and to what standard) and *verification* at the back (whether the result is actually right). The middle can go to the machine; trust my practice, not the model.

```text
Decide --> Request --> Iterate --> Validate --> done --> Evolve
              ^                        |
              +------- not yet --------+
```

- **D - Decide:** define what "done" means and the standard, in one sentence, before any request. It keeps the task mine and tells the loop when to stop; without it, work is unbounded.
- **R - Request:** brief intent, context, constraints, success criteria, and assumptions; agree the plan first. Unstated assumptions are the usual cause of fluent but wrong results.
- **I - Iterate (can also be called Isolate):** read output as it takes shape and steer it; correct small errors early and test each suggestion against "done". Keep execution bounded using the [focus and parallel sessions](#focus-and-parallel-sessions) guidance.
- **V - Validate:** check the result against the criteria from Decide using evidence (tests, real figures, a second source), sized to the stakes. A confident tone is not evidence.
- **E - Evolve:** after the work, debrief and promote lessons into reusable context: standards, references, templates, or instructions (see [maintenance and validation](#maintenance-and-validation)). Prune stale rules, and check whether I could redo the work without AI.

Decide frames the loop; Request, Iterate, and Validate repeat until "done" is met; Evolve improves what the next task starts from.

> **Personal Conclusion:** AI is a game changer for software engineers and in life when used wisely. Let it do much of the drafting, coding, and routine work so I can focus on understanding and solving the right problem. My part is still to think it through: design the solution, make architectural choices, break complex work into manageable tasks, and judge whether the proposed approach and finished result are actually good. I can use AI to help at every step without handing over those responsibilities. Keep thinking, stay curious, understand what it produces, and review and verify the work rather than follow it blindly. That active understanding and growth is not just how I stay capable and responsible; it is also part of what makes the work enjoyable. AI should amplify my abilities, not replace my understanding or judgment; I remain responsible for the work and its consequences.

### Focus and parallel sessions

VS Code supports managing sessions across workspaces and coordinating work across projects, but that capability is not a recommendation to maximize concurrency ([agent overview](https://code.visualstudio.com/docs/agents/overview), [session management](https://code.visualstudio.com/docs/agents/run/sessions/manage-sessions)). Context switching has a cost, so choose concurrency by task independence and how much review I can sustain ([research on interrupted work](https://doi.org/10.1145/1357054.1357072)); there is no universal optimum.

Even when sessions run in parallel, focus on one task at a time and prefer a few related tasks over many unrelated activities. Review the focused session's output; switch to another only when needed (writing down shortly where you left off and what to do next, such as in a temporary .txt file), such as to read and understand an approval request and click Allow if you agree, then return to your focus. Never approve an action blindly.

- Use one session for tightly coupled debugging or design, or consequential work that needs shared context and close review. Work sequentially when tasks depend on one another.
- Use 2–3 sessions for independent repositories or clearly separated tasks (such as code, documentation, and tests) with non-overlapping ownership. In one repository, parallel work can conflict through shared files or worktrees, or contend for processes; use isolated branches or worktrees where applicable and coordinate shared resources. For VS Code's delegation mechanics, see [subagents](https://code.visualstudio.com/docs/agents/run/subagents).
- Use more than 3 only for bounded, truly independent tasks I can still supervise. Increase concurrency only while review and validation maintain quality.

### Prompt engineering

Prompt engineering means shaping input to get more accurate, useful output:

- **Context first; scale planning to the task.** Give the goal, relevant code, project structure, documentation, constraints (including language/framework versions), and acceptance criteria. For complex or multi-part work, start a focused new chat, let AI analyze that context and propose a plan, then execute small steps using the agreed context and plan. For example, plan testing across the repository before implementing tests per domain/package; follow the shared [coding guidelines](guidelines-core/.apm/instructions/coding.instructions.md). For one isolated test, function, or formatting fix, ask directly: unnecessary planning adds latency and token cost. This aligns with [OpenAI's prompt engineering guidance](https://developers.openai.com/api/docs/guides/prompt-engineering) to provide clear instructions and relevant context.
- **Show the target.** Supply examples of desired input/output or existing code/style to match; specify output format, length, and tone when needed. Google's [Gemini prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies) also cover clear prompts and examples.
- **Set boundaries.** State exclusions such as no unrelated edits or new dependencies. Assign a role when a particular review perspective helps.
- **Iterate and challenge.** Treat the first result as a draft, refine it with feedback, and request assumptions, trade-offs, and a concise explanation for difficult problems. An explanation is not proof of correctness. Both [OpenAI](https://developers.openai.com/api/docs/guides/prompt-engineering) and [Google](https://ai.google.dev/gemini-api/docs/prompting-strategies) describe iterative refinement as part of effective prompting.
- **Reuse what works.** Save recurring requests and procedures through the appropriate [customization type](#concepts), rather than rewriting or duplicating guidance.

See the official [OpenAI](https://developers.openai.com/api/docs/guides/prompt-engineering), [Gemini](https://ai.google.dev/gemini-api/docs/prompting-strategies), and [IBM](https://www.ibm.com/think/topics/prompt-engineering) guides for more detail.
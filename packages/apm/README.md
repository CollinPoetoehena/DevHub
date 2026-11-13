# DevHub AI Customizations and APM

[APM](https://microsoft.github.io/apm/) distributes customization packages; the Copilot host and harness execute the work. This guide summarizes the selected architecture. [ADRs](adrs/README.md) own decision reasoning, and [CONCEPTS.md](CONCEPTS.md) owns general terminology.

The setup is in transition. Existing common and language/tool packages do not establish that this design is implemented. Agent definitions, manifests, installations, synchronization scripts, and runtime settings remain separate implementation work.

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
| Workflow | Interactive Plan, autonomous Build and Test, human Verify, then Observe; see the [workflow ADR](adrs/workflow/AI-DEVELOPMENT-WORKFLOW.md). |
| Main agents | Planner and Implementation Coordinator, supported by necessary subordinate roles and reusable skills; see the [two-agent ADR](adrs/workflow/SEPARATE-PLANNING-AND-IMPLEMENTATION-AGENTS.md). |
| Guidance | Repository `AGENTS.md` plus shared scoped instructions; see the [layering ADR](adrs/ai-customizations/GUIDANCE-INSTRUCTION-LAYERING.md). |
| Distribution | Use APM rather than maintain a custom package-distribution engine; see the [distribution ADR](adrs/distribution-and-synchronization/DISTRIBUTION.md). |
| Package boundaries | Instructions in participating repositories; generic workflows only in their users' development setup; see the [package-design ADR](adrs/distribution-and-synchronization/PACKAGE-DESIGN.md). |
| Synchronization | Future local setup synchronization and repository instruction-update PRs are a [TODO](adrs/distribution-and-synchronization/SYNCHRONIZATION.md), not implemented automation. |
| Customization depth | Thin guidance that preserves model reasoning and creativity; see the [creation ADR](adrs/ai-customizations/AI-CUSTOMIZATION-CREATION.md). |
| Reuse | Native-capability and selective tailoring heuristics; see the [reuse ADR](adrs/ai-customizations/REUSE-AND-TAILORING.md). |
| Model selection | Auto-family routing and Copilot Fusion Standard by default; see the [model-selection ADR](adrs/workflow/MODEL-SELECTION.md). |
| Role configuration | Minimal optional metadata with actual host enforcement; see the [configuration ADR](adrs/workflow/MINIMAL-AGENT-CONFIGURATION.md). |

---

## Why create AI customizations

Capture durable standards, missing repository knowledge, and repeatable role boundaries once for humans and AI. Reuse native capabilities and suitable existing components; add only guidance that improves actual work. Specify outcomes and consequential constraints without taking the model through every detail.

The [creation ADR](adrs/ai-customizations/AI-CUSTOMIZATION-CREATION.md) owns the purpose and detail boundary. The [reuse ADR](adrs/ai-customizations/REUSE-AND-TAILORING.md) separately owns adoption decisions, source selection, and the 90/10 and 80/20 heuristics.

---

## Concepts

[CONCEPTS.md](CONCEPTS.md) explains instructions, skills, agents, subagents, hooks, prompts, MCP, APM, and host/harness/model terminology, with authoritative references and the requested AI Coding Dictionary.

Separating vocabulary from project decisions keeps this README clean and the concepts clear without duplicating ADR reasoning.

---

## Choosing a workflow

For nontrivial work, start with **Planner** to investigate, clarify consequential choices, and produce a complete Markdown plan. Approve the exact saved version, then start a fresh session with **Implementation Coordinator**, supplying the approved plan and relevant repository context.

The coordinator owns implementation, integration, automated validation, and independent reviews. Material changes return to planning and approval. The user verifies and accepts the result before observing it in use. Small, localized edits whose intent, boundaries, and checks are already clear may enter implementation directly.

The [workflow ADR](adrs/workflow/AI-DEVELOPMENT-WORKFLOW.md) owns stage policy, testing requirements, and the simple-edit exception. [Approved plan and handoff](adrs/workflow/APPROVED-PLAN-AND-HANDOFF.md) owns the execution contract, while [focused sessions and specialist context](adrs/workflow/FOCUSED-SESSIONS-AND-SPECIALIST-CONTEXT.md) owns context isolation. The [two-agent ADR](adrs/workflow/SEPARATE-PLANNING-AND-IMPLEMENTATION-AGENTS.md) owns role responsibilities. These describe the intended workflow, not agents guaranteed to be available in the transitional installation.

---

## How guidance is layered

Shared rules live in the common-instructions package. Each repository owns its root `AGENTS.md`, architecture, configuration, and local constraints. Specific language/tool instructions refine shared defaults; agents and skills use those rules instead of copying them.

See the [layering ADR](adrs/ai-customizations/GUIDANCE-INSTRUCTION-LAYERING.md) for ownership, specificity, discovery limitations, and guidance versus enforcement.

### Authoring repository guidance

Prefer one concise root `AGENTS.md` linking to owning documentation and stating when to read it. Add nested guidance only for materially different subtree constraints that root links or scoped instructions cannot adequately express. Keep one-off requirements in the request and private project facts in their repository.

---

## Package design

The target design has two distribution units:

- **Common instructions**: One central package of engineering, language, framework, and tool instruction files, installed in every repository that chooses these standards.
- **AI development setup**: Agents and generic shared skills installed for the actual team members using that workflow, in a consumer-selected local scope rather than every repository by default.

Instructions belong with repository work; the generic workflow belongs to its users' development environment. That workflow is not a dependency of every repository they edit. Keeping the boundary explicit avoids unnecessary distribution, discovery overlap, and repository commits for team-member setup updates. Genuinely repository-specific capabilities remain with their repository.

Consumers can choose user-wide, personal/work, team, or project-specific setups. For example, separate setups can serve `~/projs/personal` and `~/projs/work`, with Copilot CLI started in the chosen parent working directory and intended repositories added as task directories. File access does not prove customization inheritance; verify discovery in the chosen host and scope.

The [package-design ADR](adrs/distribution-and-synchronization/PACKAGE-DESIGN.md) owns these boundaries and destinations. The [distribution ADR](adrs/distribution-and-synchronization/DISTRIBUTION.md) separately chooses APM; the [synchronization TODO](adrs/distribution-and-synchronization/SYNCHRONIZATION.md) records future automation. Separate Python, Go, and other stack packages are replaced in the target design by central instruction files; existing sources remain untouched during this transition.

<a id="language-and-framework-guidance"></a>

### Language and tool guidance

Use scoped instruction files rather than separate language/tool packages. Add framework-specific rules when actual project use exposes a recurring convention or mistake; keep one-off choices local. Longer procedures belong in appropriate skills or references, not exhaustive always-loaded tutorials.

---

## Agent configuration

Define what each role can and cannot do, its input/output, approval boundaries, and stop conditions. Omit explicit tools lists and other optional host-specific settings by default, with narrowly justified exceptions where real enforcement requires them.

Use the auto family / harness-managed router and **Copilot Fusion Standard by default**. Standard balances cost, quality, and latency for everyday work; users can select a higher available tier when needed. Omit per-role model overrides so the host's selection is inherited rather than assigning permanent models to roles whose task complexity varies.

The [model-selection ADR](adrs/workflow/MODEL-SELECTION.md) owns routing and tier rationale; the [minimal-configuration ADR](adrs/workflow/MINIMAL-AGENT-CONFIGURATION.md) owns metadata and enforcement limitations. Omitted tools do not mean restricted tools, and prose prohibitions are not permissions.

For model fundamentals and general capability/cost trade-offs, see [models and the agent loop](CONCEPTS.md#models-and-the-agent-loop).

---

## Repository setup

The design separates repository instruction installation from local workflow installation. Consumers own dependency references, destinations, update policies, local context, and existing customization files.

No migration commands or new package paths are specified here. Manifests, synchronization, and supported destinations will be implemented and tested separately; see the [package-design ADR](adrs/distribution-and-synchronization/PACKAGE-DESIGN.md) and [synchronization TODO](adrs/distribution-and-synchronization/SYNCHRONIZATION.md).

### DevHub's own setup

The [root manifest](../../apm.yml) and [existing package sources](./) remain transitional. They are not migrated by these records.

### Verify activation

During implementation, separately verify installation, discovery, and representative behavior in the intended CLI and VS Code scopes. Include parent-workspace and direct repository sessions where supported. Installed files do not prove activation or compliance.

---

## Maintenance and validation

### Maintaining reused content

Edit owning sources rather than installed copies; preserve consumer-owned additions. Review updates, attribution, licenses, permissions, compatibility, and collisions. The [reuse ADR](adrs/ai-customizations/REUSE-AND-TAILORING.md) owns selective reuse and the stopping rule.

For later clarification of an ADR, the [ADR skill and template](common/.apm/skills/adr/SKILL.md) support an optional dated, same-document changelog. A substantially replaced decision follows supersession conventions.

### Validation

These documents record architectural agreement, not runtime evidence. Implementation must validate distribution, discovery, inherited model/tool behavior, planning boundaries, handoff, delegation, checks, and independent reviews. Report unavailable capabilities rather than treating prose as proof.

---

## Reference collections

The [reuse ADR](adrs/ai-customizations/REUSE-AND-TAILORING.md#source-selection-and-stopping) explains selection and review. Reference collections include [Awesome Copilot](https://github.com/github/awesome-copilot), [Anthropic Skills](https://github.com/anthropics/skills), [Matt Pocock's skills](https://github.com/mattpocock/skills/tree/main), [ECC](https://github.com/affaan-m/ECC), [Superpowers](https://github.com/obra/superpowers), and [gstack](https://github.com/garrytan/gstack). These are references, not installation checklists.

General terminology and official documentation links are in [CONCEPTS.md](CONCEPTS.md).

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

- **Context first; scale planning to the task.** Give the goal, relevant code, project structure, documentation, constraints (including language/framework versions), and acceptance criteria. For complex or multi-part work, start a focused new chat, let AI analyze that context and propose a plan, then execute small steps using the agreed context and plan. For example, plan testing across the repository before implementing tests per domain/package; follow the [common coding instructions](common/.apm/instructions/coding.instructions.md). For one isolated test, function, or formatting fix, ask directly: unnecessary planning adds latency and token cost. This aligns with [OpenAI's prompt engineering guidance](https://developers.openai.com/api/docs/guides/prompt-engineering) to provide clear instructions and relevant context.
- **Show the target.** Supply examples of desired input/output or existing code/style to match; specify output format, length, and tone when needed. Google's [Gemini prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies) also cover clear prompts and examples.
- **Set boundaries.** State exclusions such as no unrelated edits or new dependencies. Assign a role when a particular review perspective helps.
- **Iterate and challenge.** Treat the first result as a draft, refine it with feedback, and request assumptions, trade-offs, and a concise explanation for difficult problems. An explanation is not proof of correctness. Both [OpenAI](https://developers.openai.com/api/docs/guides/prompt-engineering) and [Google](https://ai.google.dev/gemini-api/docs/prompting-strategies) describe iterative refinement as part of effective prompting.
- **Reuse what works.** Save recurring requests and procedures through the appropriate [customization type](#concepts), rather than rewriting or duplicating guidance.

See the official [OpenAI](https://developers.openai.com/api/docs/guides/prompt-engineering), [Gemini](https://ai.google.dev/gemini-api/docs/prompting-strategies), and [IBM](https://www.ibm.com/think/topics/prompt-engineering) guides for more detail.
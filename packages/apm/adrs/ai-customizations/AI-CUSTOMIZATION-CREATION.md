# ADR: Create Thin AI Customizations for Demonstrated Gaps

## Context

Default coding agents already provide reasoning, code generation, tool use, and delegation. They can know an engineering technique without knowing when this project requires it, which local constraints apply, or which checks establish correctness. Repeating those expectations in each chat is wasteful; replacing the model's judgment with exhaustive instructions is also wasteful.

The goal is maintainable software and informed human control, not a perfect customization framework. The decision drivers are durable shared knowledge, consistent local expectations, reuse of native capabilities, room for model reasoning and creativity, and sustainable maintenance.

---

## Decision

Create customizations to capture **missing context, consequential conventions, and repeatable role boundaries**, using the smallest layer that changes the result. Main agents remain thin owners of their responsibilities; shared instructions own standards, and skills hold useful task procedures. The [reuse and tailoring ADR](REUSE-AND-TAILORING.md) separately explains how to inspect existing capabilities, choose between native use, reuse, adaptation, and creation, and weigh ongoing ownership.

### Why customize

- **Lasting fundamentals**: Coding principles, documentation standards, and review discipline outlive individual tools. Capturing them once supports consistent practice while tools and models change.
- **Document once, use twice**: Human-readable conventions also guide the AI, helping new contributors and future maintainers without requiring memorization or repeated prompts.
- **Local knowledge**: Architecture constraints, validation commands, compatibility requirements, and observed mistakes are not reliably inferred from general model knowledge.
- **Reviewable control**: Explicit role inputs, outputs, approval boundaries, and checks make the workflow inspectable. Permissions and tooling enforce hard boundaries; prose alone does not.
- **Less drift**: Reusable guidance has a versioned owner rather than competing copies in chats and role definitions.

Copilot supplies [customization and delegation mechanisms](https://code.visualstudio.com/docs/agent-customization/custom-agents); DevHub supplies the policy needed by its projects. The [workflow ADR](../workflow/AI-DEVELOPMENT-WORKFLOW.md) and [two-agent ADR](../workflow/SEPARATE-PLANNING-AND-IMPLEMENTATION-AGENTS.md) own the selected workflow, rather than this record duplicating its steps.

### Start with existing capability; customize for value

Treat the active host and harness as the starting point, not a blank slate. First understand what its default agents, tools, context handling, delegation, permissions, and the repository's existing tooling already do. When they handle the task adequately, use them as-is. Recreating their general abilities in custom agents, wrappers, tools, or an orchestrator duplicates behavior and creates another layer to discover, test, and maintain without necessarily improving the result.

A customization earns its cost by closing a specific, recurring gap: for example, local constraints the model cannot infer, a standard that should be applied consistently, a repeatable procedure, or a distinct role contract that a default agent with instructions and skills cannot reliably fulfill. Prefer instructions for durable rules and skills for reusable procedures; add a custom agent only when its distinct responsibilities and boundaries improve the work. If no concrete gap or meaningful outcome can be named, keep the default setup. The [reuse and tailoring ADR](REUSE-AND-TAILORING.md) gives the practical selection and maintenance test.

### Detail: control the outcome, not every thought

Use high-level guidance, clear constraints, decision criteria, and verifiable outcomes. Leave the model free to investigate, reason, adapt, and discover a better approach within those boundaries. Thin wrappers should reuse as much of the model and harness's potential as possible, not reduce them to a rigid script.

Too many specific steps can encode assumptions that are wrong for another repository, force an unsuitable exploration order, and discourage useful alternatives. More text is not necessarily more control: it can bury the actual contract and increase maintenance. State what must remain true and what evidence is required, not exactly which file to open next or how to solve every detail. If you state too much procedural detail, you risk over-constraining the model and reducing its ability to adapt effectively and utilize its full potential and creativity; avoid that at all costs!

> See for more details official documentation links, such as [Agent Skills Best Practices](https://agentskills.io/skill-creation/best-practices#add-what-the-agent-lacks-omit-what-it-knows) and [Custom Agents in Copilot](https://code.visualstudio.com/docs/agent-customization/custom-agents).

| Area | Useful detail | Avoid |
|---|---|---|
| Engineering standards | Validate external input, surface failures, preserve compatibility, reuse existing helpers, and prefer the simplest sufficient design | Basic syntax tutorials and exhaustive lists of familiar techniques |
| Repository contracts | Actual version limits, local architecture boundaries, generated-file ownership, and configured validation commands | Guessed commands, stale paths, or shared rules containing one project's private facts |
| Role policy | Goal, input, output, approval/stop conditions, and delegation boundaries | A script for every investigation or a permanent specialist for every language |
| Known failure | A concise guardrail addressing a repeated, verified mistake | Speculative restrictions for every possible edge case |
| Deterministic procedure | Exact commands or ordered steps when reproducibility, safety, or a required format depends on them | Treating open-ended design, debugging, or implementation as a fixed recipe |

Flexibility does not waive security, approval, compatibility, or acceptance criteria. Be precise where those boundaries require precision, and use actual checks to test them. The [layering ADR](GUIDANCE-INSTRUCTION-LAYERING.md) assigns ownership; detailed references load when relevant rather than becoming an always-present tutorial.

---

## Consequences

### Positive

- **Model potential retained**: Explicit outcomes and boundaries permit adaptive reasoning and useful alternatives without surrendering control of intent.
- **Sustainable ownership**: Reuse and evidence-based additions keep the owned surface smaller and more purposeful.
- **Shared understanding**: Written local expectations support both human onboarding and AI-assisted execution.

### Negative

- **Judgment required**: Deciding what is a genuine gap and how much detail it needs cannot be reduced to a percentage or file-size rule.
- **Behavioral variance**: Flexible guidance is not deterministic compliance; representative evaluation, checks, and human review remain necessary.
- **Guidance maintenance**: Local constraints and known-failure guardrails must remain accurate as tools, models, and projects evolve.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [Default agent with ad hoc prompts](https://code.visualstudio.com/docs/agent-customization/custom-instructions): rely on each request to repeat all local expectations. | Avoids maintaining custom files and leaves full flexibility for one-off work. | Recurring standards and local constraints must be rediscovered or restated; important expectations can be omitted. | Reusable local knowledge has lasting value, even when the native agent performs the work. | A task has no recurring context gap and a clear prompt already suffices. |
| [Exhaustive custom workflow](https://code.visualstudio.com/docs/agent-customization/custom-agents): a project-defined layer prescribing every exploration and implementation step. | Makes expected sequencing visible and can suit tightly repeatable procedures. | Overconstrains open-ended work, embeds brittle assumptions, and creates a broad maintenance/evaluation surface. Prose still does not enforce the steps. | Control should focus on consequential boundaries and outcomes while retaining model reasoning. | A specific repeatable operation requires exact sequencing; isolate that procedure rather than script all engineering work. |

---

## Status

Accepted: the user selected thin, high-level customizations that preserve model creativity. The native/reuse heuristics are recorded separately in [reuse and tailoring](REUSE-AND-TAILORING.md); no workflow is implemented by these records.

---

## Date

2026-11-13

---

# Changelog

- 2026-11-13: Moved into the AI-customizations folder and extracted reuse ratios, source selection, and adoption trade-offs into [reuse and tailoring](REUSE-AND-TAILORING.md). The purpose/detail policy and original decision date are unchanged.
- 2026-11-13: Expanded the native-first value threshold and when owned agents or other layers are justified; clarified that [reuse and tailoring](REUSE-AND-TAILORING.md) owns the practical selection and maintenance test.

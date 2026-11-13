# AI Customization Concepts

This is a short glossary for the [APM overview](README.md), not a setup guide. Host support and activation rules change; check the linked documentation for current behavior.

The general concepts are listed here, for full details refer to the [References section](#references).

## Table of Contents

- [Guidance and reusable work](#guidance-and-reusable-work)
- [Roles and work transfer](#roles-and-work-transfer)
- [Orchestration](#orchestration)
- [Capabilities and controls](#capabilities-and-controls)
- [Execution and context](#execution-and-context)
  - [Execution and context (host and model)](#execution-and-context-host-and-model)
  - [Models and the agent loop](#models-and-the-agent-loop)
- [References](#references)

---

## Guidance and reusable work

- **Repository instructions** (`AGENTS.md` or a supported equivalent) give an agent repository or subtree context: boundaries, important facts, commands, and links to the owning documentation.
- **Scoped instructions** (such as `*.instructions.md`) apply standing rules to matching files or tasks when the selected host supports that format and scope. A matching path may select guidance, but neither adding a directory nor linking a document proves it is discovered, inherited, or followed. Instructions guide the model; they are not enforcement.
- **Skills** package a focused, repeatable capability or procedure, sometimes with scripts and references. In the Agent Skills standard, discovery is progressive: an agent can first see a skill's name and description, then load its instructions when relevant, and open supporting resources as needed. The active agent invokes the skill without needing another persona or agent mode; supporting hosts can expose it as a slash command. Activation, locations, and optional features depend on the host.
- **Prompts** are requests, often saved as reusable files and invoked explicitly. Unlike standing instructions, they are not automatically applied to every task. Prompt-file formats and support are host-specific.

---

## Roles and work transfer

- **Agent** is the role or configuration doing work in a session. A custom agent defines a reusable specialist role, usually with its own instructions and tool choices. Planning or orchestration can instead be a skill invoked by the existing built-in agent, with the user's selected model and permission mode unchanged; the coordinating agent remains present.
- **Subagent** is an invocation delegated a bounded task in a separate context. It may use a built-in or custom role and returns findings or work to the coordinating agent; do not assume it inherits the main conversation or all its context.
- **Handoff** transfers the active task to another agent or session, usually with selected context. It is not the same as a subagent returning a result. The host determines what state and context cross the handoff.

---

## Orchestration

**AI orchestration** coordinates agents, tools, context, and workflow steps toward a request's goal. It matters because clear responsibilities, work transfer, and approval points let systems handle multi-step work without requiring users to direct every action. The aim can be bounded autonomy: agents drive the work while people set constraints and approve consequential decisions.

For patterns and practical guidance, see Microsoft's [AI agent design patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns), IBM's [AI agent orchestration](https://www.ibm.com/think/topics/ai-agent-orchestration), JetBrains' [AI agent orchestration](https://www.jetbrains.com/pages/ai-agents/architecture/ai-agent-orchestration/), and the Copilot Academy [use-case guide](https://copilot-academy.github.io/workshops/copilot-customization/identify_use_cases), [customization handbook](https://copilot-academy.github.io/workshops/copilot-customization/copilot_customization_handbook), [custom agent developer guide](https://copilot-academy.github.io/workshops/copilot-customization/custom_agent_developer_guide), [agent skills developer guide](https://copilot-academy.github.io/workshops/copilot-customization/agent_skills_developer_guide), and [agentic workflows guide](https://copilot-academy.github.io/workshops/copilot-customization/agentic_workflows).

---

## Capabilities and controls

- **Capabilities** are the functional abilities an agent or skill can perform, often defined by its instructions, tools, and environment.
- **Controls** are the mechanisms to regulate or constrain agent behavior, including permissions, policies, and host-enforced rules.

---

## Execution and context

- **Tools** let an agent inspect information or take actions. Native tools are supplied by the host; additional tools may come from integrations. A tool being mentioned or configured does not prove it is available or authorized.
- **Hooks** are code run by a supported harness at configured workflow events, without relying on the model to request the action. Their events, configuration, and guarantees vary by harness; hooks alone are not a complete security boundary.
- **CI and permissions** are controls outside ordinary prose guidance. CI runs configured checks, while host or platform permissions limit or gate actions. Use these for requirements that must be checked or enforced; actual guarantees depend on their configuration.
- **MCP** (Model Context Protocol) is an open protocol through which an AI application connects to external context and capabilities via MCP servers. The server must be configured and permitted in the active environment.
- **APM and packages**: Agent Package Manager resolves and deploys declared customization components. An APM package groups reusable, maintained components for distribution. A package or manifest supplies configuration; it does not run the agent loop or prove that a deployed component is active.

### Execution and context (host and model)

- **Host/client** is the user-facing application or interface. The **harness** coordinates the model, context, tools, permissions, and agent loop. The **runtime** executes sessions and their tool interactions. Product boundaries and terminology can overlap; changing a model does not necessarily change the harness.
- **Context** is the information available to the model for a request, such as the prompt, conversation history, files, instructions, and tool results. It is limited, and a new session or delegated task may not include prior conversation.
- **Smart zone** is an informal heuristic for keeping context focused and useful rather than accumulating irrelevant history. It is not a defined token threshold or a guarantee of output quality.

### Models and the agent loop

An **AI model** is a trained system that produces outputs from inputs. A model generates responses from supplied context and can propose tool requests; it can answer questions, analyze information, and generate text or code. Its output can be incorrect and needs verification.

In an agent, the harness supplies context to the model, handles permitted tool requests, and returns tool results to the model for subsequent steps. The model generates the requests; the harness and tools carry out actions subject to their permissions. A host may select a model directly or use a router; for example, Copilot Fusion Standard selects one model per task, not independent multi-model review.

Models offer different capability, speed, and cost trade-offs. These illustrative tiers describe common uses rather than guaranteed performance or fixed prices:

| Relative cost | Typical use | Example GitHub Copilot models |
|---|---|---|
| Low | Simple questions, summarization, extraction, and repetitive tasks. Can also be used for implementation work if given a clear and well-defined plan (e.g. plan with medium to high cost; implement with low cost). | GPT-6 Luna, Claude Haiku 5.5 |
| Medium | Everyday writing, coding, analysis, planning, and moderately complex problem-solving. | GPT-6.1 Sol, Claude Sonnet 5.5 |
| High | Difficult reasoning, complex design, or long multi-step problems where additional capability is worthwhile. | GPT-6 Astra, Claude Opus 5.5 |

GPT, Claude, and other providers all offer capable models; task fit and capability/cost generally matter more than the provider name. Individual models still differ in strengths, features, and data handling. Availability depends on the plan and host, and actual cost depends on usage. See GitHub's [supported models](https://docs.github.com/en/copilot/reference/ai-models/supported-models), [model comparison](https://docs.github.com/en/copilot/reference/ai-models/model-comparison), and [pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing).

---

## References

- [AI Coding Dictionary](https://www.aihero.dev/ai-coding-dictionary)
- [VS Code customization concepts](https://code.visualstudio.com/docs/agents/concepts/customization), [custom instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions), [Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills), [custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents), and [prompt files](https://code.visualstudio.com/docs/agent-customization/prompt-files)
- [AI customization cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet)
- [VS Code subagents](https://code.visualstudio.com/docs/agents/run/subagents), [agent harnesses](https://code.visualstudio.com/docs/agents/concepts/agent-harnesses), [context](https://code.visualstudio.com/docs/agents/concepts/context), [tools](https://code.visualstudio.com/docs/agents/run/tools), and [hooks](https://code.visualstudio.com/docs/agent-customization/hooks)
- [VS Code permissions and approvals](https://code.visualstudio.com/docs/agents/run/approvals) and [Copilot Fusion](https://docs.github.com/en/copilot/concepts/models/copilot-fusion)
- [AGENTS.md format](https://agents.md), [Agent Skills specification](https://agentskills.io/specification.md), and [Model Context Protocol](https://modelcontextprotocol.io/introduction)
- [Agent Package Manager](https://microsoft.github.io/apm/)

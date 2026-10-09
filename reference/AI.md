# AI

Practical reference on AI — what it is, agents, prompt engineering, and how I use it (and think it should be used) as a Software Engineer, including a framework for picking the right tool/model for a given task and using paid credits efficiently.

> **Note:** This is a huge and fast-moving topic. This page intentionally stays short and opinionated rather than complete — it covers only what is useful for my own day-to-day work. The linked sources go into far more depth.

> **Scope and examples:** This guide focuses on reusable concepts and principles, while using tools such as GitHub Copilot and Microsoft 365 Copilot to make them concrete. The product-specific instructions and links are examples, not a commitment to document or continually maintain every tool in detail. If you use Codex or another assistant, the same principles generally apply; consult that tool's documentation for its equivalent setup and features, and adapt only the tool-specific details that matter rather than rewriting the whole guide and continually maintaining this document.

## Table of Contents

- [AI & ML Background](#ai--ml-background)
  - [What is AI & ML?](#what-is-ai--ml)
  - [Models, Harnesses & Example Models](#models-harnesses--example-models)
  - [AI Agents](#ai-agents)
  - [Prompt Engineering](#prompt-engineering)
- [Reusable AI Workflows and Agents](#reusable-ai-workflows-and-agents)
  - [Coding: GitHub Copilot in VS Code](#coding-github-copilot-in-vs-code)
  - [General Purpose: Microsoft 365 Copilot](#general-purpose-microsoft-365-copilot)
- [AI & Software Engineering — General Usage](#ai--software-engineering--general-usage)
  - [Conclusion](#conclusion)
- [Framework: Which AI Tool/Model for Which Task](#framework-which-ai-toolmodel-for-which-task)
  - [1. General purpose](#1-general-purpose)
    - [Billing/Cost of General‑purpose AI tools like Microsoft Copilot](#billingcost-of-generalpurpose-ai-tools-like-microsoft-copilot)
  - [2. Specific](#2-specific)
    - [Coding](#coding)
    - [Other Specific applications](#other-specific-applications)
- [4-Tier Model Framework (Credit Efficiency)](#4-tier-model-framework-credit-efficiency)
  - [Practical Rule of Thumb](#practical-rule-of-thumb)

---

## AI & ML Background

> **Note:** This section is deliberately short — AI/ML is a very large and fast-moving field. See the further reading links below each subsection for more depth and details, the section itself is kept concise.

### What is AI & ML?

**Artificial Intelligence (AI)** is, broadly, the field of building systems that perform tasks which normally require human intelligence — recognizing patterns, understanding language, reasoning, and generating content. **Machine Learning (ML)** is the main approach behind most modern AI: instead of hand-coded rules, a model learns patterns directly from large amounts of data. Most of the tools referenced on this page (ChatGPT, GitHub Copilot, Claude, Gemini, etc.) are built on **Large Language Models (LLMs)** — a type of ML model trained on huge amounts of text/code that predict and generate text, and that can be extended with tools/agents to take actions (search, run code, edit files, call APIs, etc.).

**Further reading:**

- [Artificial intelligence — Wikipedia](https://en.wikipedia.org/wiki/Artificial_intelligence)
- [Machine learning — Wikipedia](https://en.wikipedia.org/wiki/Machine_learning)
- [Large language model — Wikipedia](https://en.wikipedia.org/wiki/Large_language_model)
- [What is Artificial Intelligence (AI)? — IBM](https://www.ibm.com/topics/artificial-intelligence)
- [What is Machine Learning (ML)? — IBM](https://www.ibm.com/topics/machine-learning)
- [What are large language models (LLMs)? — IBM](https://www.ibm.com/topics/large-language-models)
- [What is Generative AI? — IBM](https://www.ibm.com/topics/generative-ai)
- [AI courses and articles — Google AI](https://ai.google/)
- [OpenAI Research](https://openai.com/research)

### Models, Harnesses & Example Models

A **model** is the underlying trained system that actually generates a response (reasons about the prompt and produces text/code). A **harness** (sometimes called a *scaffold* or *agent framework*) is the surrounding application that wraps a model with tools, context/memory management, and an execution loop — e.g. GitHub Copilot Chat, the ChatGPT app, or an IDE agent are all harnesses. The same underlying model can behave quite differently depending on the harness it runs in (which tools it can call, how much context it gets, etc.).

Vendors typically offer the same model family in multiple capability/cost tiers, for example:

- **Claude Sonnet / Claude Opus** (Anthropic) — Sonnet is a balanced, mid-tier model; Opus is Anthropic's most capable (and most expensive) model, meant for harder tasks.
- **GPT-5 / GPT-5 mini** (OpenAI) — a flagship model and a smaller, cheaper/faster one.
- **Gemini Pro / Gemini Flash** (Google) — Pro for more complex reasoning, Flash for fast/cheap responses.

See the [4-Tier Model Framework](#4-tier-model-framework-credit-efficiency) below for how to pick between tiers in practice.

**Further reading:**

- [Claude models overview — Anthropic](https://www.anthropic.com/claude)
- [OpenAI models documentation](https://platform.openai.com/docs/models)
- [Gemini models — Google AI](https://ai.google.dev/gemini-api/docs/models)

### AI Agents

An **agent** is an AI system (usually LLM-based) that doesn't just answer a question, but can take multi-step actions to accomplish a goal — searching a codebase, running commands, reading/writing files, calling APIs or other tools, and using the results to decide what to do next, in a loop, until the task is done (or it needs your input).

In practice (e.g. GitHub Copilot's *agent mode*), this means you can give it a task like "add a feature", "fix this bug", or "refactor this module", and it will explore the repository, make the edits across multiple files, run tests/builds, and iterate — instead of only suggesting a snippet for you to copy-paste. This makes agents very useful for larger or more repetitive tasks, but the same principle applies as everywhere else on this page: **you remain responsible for reviewing what it did.**

For practical ways to save and reuse specialist agent setups, see [Reusable AI Workflows and Agents](#reusable-ai-workflows-and-agents), including examples for GitHub Copilot and Microsoft 365 Copilot.

**Further reading:**

- [What are AI agents? — IBM](https://www.ibm.com/topics/ai-agents)
- [GitHub Copilot agent mode documentation](https://docs.github.com/en/copilot/concepts/agents)
- [Introduction to AI agents — Google Cloud](https://cloud.google.com/discover/what-are-ai-agents)

### Prompt Engineering

Prompt engineering is simply the practice of writing your input to an AI tool in a way that gets you better, more accurate, and more usable output. A few techniques/tips that consistently help:

- **VERY IMPORTANT: Provide the necessary context, let the AI analyze it and generate a plan & Break large tasks into smaller steps.** First provide the AI with all the context required (in a new chat of course to only focus on this task), let it analyze and generate a plan, then break the task into smaller steps and tackle them one by one. This is often much better because the AI first has a clear understanding of the overall goal before diving into individual steps, and it can now use the analyzed and full context along with the generated plan to guide its actions for all further requests effectively. For example, when generating tests for your code, first provide the AI with the full context (e.g. the full repository with the code, the project structure (e.g. via `tree`), any relevant documentation (e.g. `README.md`), any other relevant project context, etc.), let it analyze the context generate a testing plan, and then implement the tests step by step (e.g. per domain/sub-package), see details on this example in [DevHub/reference/python/Testing.md](./python/Testing.md#generating-tests-with-ai). *Vague or incomplete prompts get vague, incorrect and incomplete answers!* It may seem like unnecessary additional effort, but it is more than worth it in terms of **time saved and quality of output** (especially for complex or large-scale tasks). **Exception:** if you only want to change/update a single existing test or code file or a similar small, well-scoped piece of functionality, you don't need to go through the planning step first — you can just ask directly for that one (or small number of) changes. A single, well-scoped test/functionality is small and self-contained enough that a short plan adds overhead without adding value: there's no risk of context dilution or scope confusion when there's only one thing to change, so the extra planning step just costs you an additional round-trip (and tokens/credits) for no real benefit. **Finding the right balance:** As a general rule, the more context-heavy, multi-part, or ambiguous the task is, the more it benefits from the "plan first, then request incrementally" approach — this is where it really pays off, since it prevents the model from getting lost across many interdependent files or domains. For small, well-defined, single-purpose changes (like fixing one test, tweaking one function, or a quick formatting change), skip the plan and just ask directly: sending a smaller, targeted prompt also means less input (and often less output) for the model to process, which directly saves tokens/credits and gets you a faster answer. In short: **scale the effort of your prompt to the scale of the task** — use the structured, incremental workflow for large or complex work, and go straight to the point for small, isolated fixes/changes. 
- **Show, don't just tell.** Provide examples of the input/output format you want, or an existing piece of code/style to match.
Ask for a plan first or provide a plan yourself, then execute step by step, rather than one giant ambiguous request.
- **Be specific and give context.** State the goal, relevant context (e.g. project requirements, source code, documentation, project structure, etc.) and constraints (language, framework, versions), and what "done" looks like. *Vague or incomplete prompts get vague, incorrect and incomplete answers!*
- **Constrain the output** (format, length, style) when you need something specific, e.g. "respond only with a JSON object", "keep it to a short bullet list".
- **State what NOT to do**, when relevant (e.g. "don't change unrelated files", "don't add new dependencies").
- **Give it a role, when useful.** E.g. "review this as a senior security engineer" shifts the kind of feedback you get.
- **Iterate & Refine.** Treat the first answer as a draft — refine with follow-up questions instead of expecting a perfect result immediately.
- **Ask it to reason/explain, for hard problems.** Asking for step-by-step reasoning or trade-offs (instead of just "the answer") improves quality on non-trivial tasks.
- **Make it easy for yourself: reuse what works.** Save recurring prompts, instructions, and agent setups instead of rewriting them for every task. See [Reusable AI Workflows and Agents](#reusable-ai-workflows-and-agents) for the general principle and practical examples.

**Further reading:**

- [Prompt engineering — Wikipedia](https://en.wikipedia.org/wiki/Prompt_engineering)
- [Prompt engineering guide — OpenAI](https://platform.openai.com/docs/guides/prompt-engineering)
- [What is prompt engineering? — IBM](https://www.ibm.com/topics/prompt-engineering)
- [Prompting guide — Google Gemini](https://ai.google.dev/gemini-api/docs/prompting-strategies)

---

## Reusable AI Workflows and Agents
> For the practical VS Code setup, including which account to use for Settings Sync versus employer-provided subscriptions and how to separate Git identities, see [Code Editor](Code_Editor.md). This account guidance is included there because it is about configuring the editor and development environment, rather than an AI workflow.

**Make it easy for yourself:** If you regularly ask for similar work (e.g. implementing features, fixing bugs, reviewing code, or drafting documentation), reuse a small, maintained setup rather than rewriting the same context, constraints, and checks each time. This principle applies across AI tools, not just coding assistants:

- **Prompt templates / saved tasks:** reusable requests for a particular job, with a new objective or input each time.
- **Shared instructions:** stable preferences, conventions, and constraints that apply across tasks. Keep generic rules separate from project- or team-specific details.
- **Custom agents:** reusable specialist setups with a defined role, instructions, relevant knowledge, and permitted tools/actions, where supported. For example, a code reviewer or a documentation assistant.
- **Repeatable workflows:** a consistent sequence of steps and checks; use skills or other workflow features when your tool supports them and a saved prompt is not enough.

Start small, reuse what helps, and tailor it to your project and company policies. Supply fresh task-specific context, keep instructions and knowledge sources current, and test the setup on representative tasks before relying on it. **This guide explains the principle, not the exact templates, files, or complete setup you should use:** consult your tool's documentation for supported formats and configuration. Instructions guide the AI; they do not replace review, access controls, or enforced safeguards.

> **Find the right balance:** Do not create a template, agent, or workflow for everything; use them only where repeated use meaningfully improves speed, quality, or consistency enough to justify the effort of creating and maintaining them (i.e. it actually has added value). For one-off/very low frequency or simple tasks, a direct prompt may be more efficient. Balance scope too: one template can cover several genuinely similar tasks with shared instructions and checks, saving duplication and maintenance. Do not force entirely different tasks into one generic template, or create a separate template for every minor variation. Split only where the differences matter, and simplify or retire setups that cost more effort than the value they provide.

The two subsections below cover **coding**, using GitHub Copilot in VS Code as the example, and **general-purpose work**, using Microsoft 365 Copilot agents as the example. For guidance on choosing the right tool or model for a task, see [Framework: Which AI Tool/Model for Which Task](#framework-which-ai-toolmodel-for-which-task).

### Coding: GitHub Copilot in VS Code
> For separating the personal account used for editor Settings Sync from the work account used for an employer-provided Copilot subscription, see [Code Editor](Code_Editor.md). That account arrangement is editor setup, so it is documented there rather than as an AI workflow.

#### Agent harnesses in VS Code

A **harness** runs the agent workflow and coordinates its tools, permissions, context, and session; it is separate from the language model you select. See [VS Code agent harnesses](https://code.visualstudio.com/docs/agents/concepts/agent-harnesses) for the full explanation and [how to choose and use one](https://code.visualstudio.com/docs/agents/run/agent-harnesses). For this guide, the practical default is the **Copilot harness**:

- **Copilot:** the recommended default for day-to-day coding. It runs through Agent Host and supports continuing work across VS Code, GitHub Copilot CLI, and the Copilot app.
- **Claude or Codex:** choose these when you want to use their provider-specific agent workflows and capabilities in VS Code.
- **Cloud:** use a supported cloud agent for an independent task against a GitHub repository that can return a pull request.

> **Note:** Local is likely to be deprecated and should not be used for new work. This guide intentionally omits Local-specific explanation because it is not a recommended or stable workflow for Copilot-based coding.

The available tools, customizations, and permissions depend on the harness. Changing the model does not change the harness.

The following is the practical coding setup used as an example here. This is for the Copilot harness only: use Agent Skills for reusable workflows and `.github/copilot-instructions.md` for repository-wide guidance. `AGENTS.md` is another supported repository instruction format, not the same thing as a custom agent definition. See [Customize AI in VS Code](https://code.visualstudio.com/docs/copilot/customization/overview) for supported customization options.

**Practical example across many repositories:** In GitHub Copilot in VS Code, save a generic `implement-change.prompt.md` or `review-code.prompt.md` in your **user profile**, rather than copying it into every repository. You can similarly create a user-profile custom agent for a recurring role, such as code review, and user-level instructions for rules that genuinely apply everywhere. When you open another repository using that profile, invoke the saved prompt (e.g. `/implement-change`) or select the custom agent and provide the task-specific context. Keep each repository's architecture, conventions, and test commands in its own `.github/copilot-instructions.md` or `AGENTS.md`: this lets you reuse the workflow across projects without assuming they all work the same way. 

**Custom agent example:** Create a `code-reviewer.agent.md` through VS Code's agent customization UI, choosing user-profile storage for cross-repository use or `.github/agents/` for a repository-specific agent. Give it instructions to prioritize bugs, regressions, security risks, and missing tests; report findings with file references; and avoid editing files. Where supported, restrict its available tools to those needed for inspection. Select that agent in chat and provide the files or diff to review. A prompt defines a reusable task; a custom agent defines the specialist that carries it out. See [VS Code custom agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents).

**Saving, syncing, and backing up those settings:** For the recommended **Copilot harness**, user-profile customizations such as Agent Skills, shared instructions, and reusable prompt files are saved in VS Code profile data and can be synced across devices via **Settings Sync**. For the exact setup steps, see [Code Editor](Code_Editor.md), which explains how to enable backup settings and configure the sync account. This section only focuses on the AI-side workflow: the relevant practical point is that Copilot customizations are synced through the normal VS Code profile/settings backup flow, while repository-level files are **not covered by Settings Sync** and should be versioned in Git instead. Keep an independent backup or an approved private Git repository (e.g. a central repository called `workflows` or even inside this `DevHub` repository) for important personal templates and agents too, especially anything outside the synced categories; sync is not a substitute for a long-term backup. Never include secrets, and follow company policies before syncing work-related content to a personal account.

**Example prompt template for standard codebase work:** This is just one example of how to turn a recurring task (implementing a feature or bug fix) into a reusable prompt, not a complete or universally applicable template. Create your own tailored version and maintain it in your user profile or repository, not in this reference document. You can create separate prompts for other tasks, such as `generate-tests.prompt.md`, `review-code.prompt.md`, or `update-docs.prompt.md`, each with its own objective, constraints, and checks. For small, well-scoped changes, simplify or skip the planning steps as described above.
- **Why "act as a senior software engineer"?** It sets the intended perspective: consider maintainability, trade-offs, risks, and verification, not just producing code. It is a role cue, not a guarantee of expertise or correctness; the concrete instructions and your review still matter.
- **Model selection for this example:** The YAML header explicitly sets `model: Auto` to request automatic model selection rather than pinning a specific underlying model. This follows the [automatic model selection][automatic-model-selection] guidance: start with automatic selection for its balance of capability and credit efficiency, check the results and cost, and switch manually only when needed. If your VS Code/Copilot version does not recognize this value, omit the `model` field and select **Auto** in the chat model picker instead.
- **Use it with the Copilot harness:** Agent Host sessions do not load prompt files. Adapt this reusable workflow into an [Agent Skill](https://code.visualstudio.com/docs/agent-customization/agent-skills), for example at `.github/skills/implement-change/SKILL.md` for a repository or `~/.copilot/skills/implement-change/SKILL.md` for personal use across projects. Keep shared repository guidance in `.github/copilot-instructions.md`. Invoke the skill with `/implement-change Fix the login validation bug`, or let Copilot load it when its description matches the task. Skills can also be reused in Copilot CLI and the Copilot app.

```markdown
---
name: implement-change
description: Implement a focused, verified feature or bug fix using repository conventions.
agent: agent
model: Auto
argument-hint: Describe the change, expected behavior, and any constraints.
---

Act as a senior software engineer working in this repository.

**Objective:** Implement the change described in the accompanying chat request. Use its expected behavior and acceptance criteria to define what "done" means. If no objective is provided, ask for it before making changes.

**Before making changes:**

1. Read applicable repository instructions and supplied company policies.
2. Inspect the relevant implementation, call sites, tests, and validation commands. Keep exploration focused on the task; do not scan the entire repository by default.
3. Identify the likely affected files, expected behavior, risks, and assumptions. Ask only about ambiguities that materially affect correctness, scope, or safety; otherwise state reasonable assumptions and proceed.
4. For non-trivial work, share a concise plan before editing. For small, clear changes, proceed directly. If I requested planning only, stop after the plan.

**Implementation:**

1. Make the smallest maintainable change that meets the objective. Fix the root cause of bugs rather than masking symptoms.
2. Follow existing conventions/formats in the existing code and reuse suitable code, dependencies, and test helpers. Avoid unrelated refactoring, speculative abstractions, and unnecessary dependencies.
3. Preserve existing user changes. If they conflict with the task, ask before replacing them.
4. Add or update tests for the changed behavior and relevant edge cases; for bug fixes, add a regression test where practical.
5. Validate the touched behavior early with the narrowest useful check. Run broader tests, linting, type checks, and builds as warranted by the impact and repository rules.
6. Fix failures introduced by your changes and rerun affected checks. Report unrelated or pre-existing failures without expanding scope to fix them.
7. Update any documentation affected by the changes and ensure it accurately reflects the new behavior. Also update the CHANGELOG if applicable/present.

**Constraints:**

- Do not expose secrets, credentials, or private data in output or send them to external services.
- Explain the impact and obtain approval before making breaking public API changes, database schema changes, destructive operations, or changes outside the agreed scope.
- Do not commit, push, or deploy without my explicit approval.
- Do not disable tests, weaken checks, or alter expectations merely to make failures pass.
- If blocked by missing tools, access, or information, report the blocker and what is needed.

**Completion report:**

Keep the report concise:

- Changes made and key files affected.
- Checks actually executed, their results, and any checks skipped with reasons.
- Remaining risks, assumptions, and required manual steps.

Clearly distinguish verified results from untested expectations. Do not claim a check passed unless you ran it and observed that result.
```

### General Purpose: Microsoft 365 Copilot

The same principle applies outside your codebase. For example, use [Agent Builder in Microsoft 365 Copilot](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/agent-builder) to create a **Documentation Assistant** with reusable instructions such as "follow our documentation style, cite source documents, and flag missing information rather than inventing it." Connect approved knowledge sources, such as your team's SharePoint documentation, test it with representative requests, and then select the agent for recurring drafting or summarization tasks. This avoids re-entering the same role, style, and background each time; you still provide the specific task and review its output.

Share the agent with colleagues only where permitted, and check access to its underlying knowledge sources separately. Availability, knowledge-source capabilities, and costs depend on your license and organizational policies; this example refers to **Microsoft 365 Copilot**, not every consumer Microsoft Copilot experience. For actions, connectors, or more involved workflows, consider [Microsoft Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/). These agents are managed in Microsoft's service, not backed up through VS Code Settings Sync; keep an approved copy of important instructions and configuration notes. See also [Microsoft 365 Copilot agent concepts](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/agents-overview).

---

## AI & Software Engineering — General Usage

> **Note:** This is a general overview, not meant to be complete — just the concepts that matter day-to-day, condensed rather than fully detailed.

AI can massively increase your productivity as a Software Engineer — it helps you learn faster, understand better, work more efficiently, and be more creative, etc. **But your own thinking and expertise always remain the core.** Treat AI as a smart colleague or intern that supports you, NOT as a replacement for your role — always keep thinking critically. 

**Some general guidelines for using AI effectively in software engineering and in general life include (not meant to be exhaustive, just some important points):**

- **Where AI can help:** creativity & ideas (brainstorming solutions, architecture/design trade-offs), writing & documenting (docs, commit messages, PR descriptions, specs/comments), coding & technical tasks (debugging, explaining libraries/algorithms, code/tests, test generation, automation, refactoring ideas, etc.), learning & understanding (explaining complex topics, comparisons, summaries, quick Q&A instead of Googling/StackOverflow), and general productivity (planning, restructuring text, sharper communication, sanity-checking ideas), etc.
- **VERY IMPORTANT: Stay the expert:** use AI as support, understand and verify what it generates, keep reasoning through complex problems yourself, and remember that strategic choices, system design, and interpretation remain human work — AI can and will make mistakes, and you're the one who has to catch them. AI is a force multiplier, NOT a replacement for human engineering.
  - **Use it correctly:** combine thinking for yourself with using AI (think first, or in parallel, depending on the situation) rather than letting AI take over — this keeps you the expert, avoids dependency, keeps you in control of quality, and helps you learn more. AI is for *deepening, improving, and speeding up* work, not replacing it.
  - **Maintain and Develop Your Core Skills & Find the Right AI Balance:** use AI to amplify your capabilities, not replace them. Over-reliance on AI can lead to skill atrophy, weaker problem-solving abilities, and reduced confidence when AI is unavailable or incorrect. The goal is to find a *practical balance* between *maintaining and growing your own expertise* and *leveraging AI as a force multiplier*. The best engineers use AI as a *force multiplier* that enhances their productivity and growth while ensuring their own knowledge, judgment, and expertise continue to develop over time. Examples:
    - **Writing, communication, and documentation:** simple or less important emails and documentation are often good opportunities to practice and maintain your communication and writing skills. In many cases, these tasks are also faster to complete yourself than to spend time prompting, reviewing, and refining AI-generated output. However, AI can still provide value through drafting, restructuring, improving clarity, reviewing content, or accelerating routine work when the benefits outweigh the extra effort of prompting, reviewing, and refining the output. In many cases, simple, less important, or highly routine emails and documentation are quicker to write yourself and also provide valuable practice, while AI tends to be more beneficial when the content is important, complex, repetitive, time-consuming, or would clearly benefit from an additional review or quality improvement.
    - **Coding, debugging, and troubleshooting:** straightforward coding tasks, debugging, scripting, and troubleshooting are valuable opportunities to maintain and strengthen your technical foundations and problem-solving abilities. At the same time, AI can provide significant value through boilerplate generation, code suggestions, reviews, explanations, brainstorming, automation, test generation, alternative approaches, and identifying potential issues. Sometimes it is beneficial to solve something largely yourself to reinforce understanding and maintain your skills; other times, AI can significantly improve speed, quality, learning, or reduce repetitive work. In many cases, the most effective approach is a combination of both, where you remain actively involved in the problem-solving and decision-making process (e.g. design, overall architecture/code structure, etc.) while using AI to accelerate implementation, provide feedback, challenge assumptions, fill knowledge gaps, and handle more repetitive or time-consuming aspects of the work (e.g. producing the code, writing tests, documentation, etc.). The goal is not to maximize or minimize AI usage, but to find the right balance between *maintaining and growing your technical expertise* and *leveraging AI to work faster, better, and more effectively*.
    - **Larger, more complex, unfamiliar, or high-impact work:** for larger, more complex, unfamiliar, or high-impact tasks, AI can often provide even greater value through research, architecture and design discussions, code reviews, refactoring, information synthesis, solution exploration, and accelerating learning in unfamiliar domains. These types of tasks often involve more uncertainty, more information, more possible approaches, and a higher cost of mistakes, making AI particularly useful as a brainstorming partner, reviewer, sounding board, knowledge source, and analytical assistant. AI can help evaluate trade-offs, identify risks, challenge assumptions, uncover blind spots, explore alternative solutions, and rapidly process information that would otherwise take significantly longer to analyze manually. While final decisions, context awareness, and engineering judgment remain your responsibility, AI can greatly accelerate exploration, learning, decision-making, communication, and execution, allowing you to focus more on strategy, architecture, priorities, and solving the underlying business or technical problem.
    - **Overall goal:** use AI when it meaningfully improves speed, quality, learning, or insight, but continue exercising and developing your core skills in communication, writing, coding, troubleshooting, and problem-solving. **The goal is not to maximize AI usage or minimize it, but to find the right balance between *maintaining and growing your own expertise* and *leveraging AI as a force multiplier*. Some tasks are best done largely yourself, some are best done with AI assistance, and many benefit from a combination of both. The best engineers use AI strategically, applying it where it creates real value while ensuring their own knowledge, judgment, critical thinking, and technical capabilities continue to grow over time.**
  - **Coding is only one piece of building good software; Engineering judgement remains the differentiator:** Generating code faster, on its own, doesn't produce reliable, production-grade systems. In fact, writing code is often only a small part of the overall engineering effort. AI can generate individual functions, components, or even entire features, but someone still needs to design a coherent architecture, ensure the various pieces work together as a cohesive system, define clear boundaries and interfaces, make sound technology and trade-off decisions, prioritize work to maximize impact within finite time and resources, and keep the solution maintainable and adaptable as requirements evolve. Robust software requires *broader engineering thinking* that goes well beyond the code itself — such as designing for **scalability** as usage and data grow, proactively **identifying bottlenecks** (e.g. performance, architecture, process, etc.) before they become real problems, **anticipating future features** so today's design doesn't box you in later, and carefully weighing whether a change carries **risk of impacting customers** (e.g. downtime, data loss, breaking changes, regressions, etc.) before shipping it. That kind of *judgment* comes from engineering fundamentals — system design, testing and rollout strategy, monitoring, operational excellence, and experience, etc. — not from how fast you (or an AI) can generate code. AI can support this thinking (e.g. brainstorming scaling approaches, surfacing edge cases, reviewing a rollout plan, or generating implementation options), etc., but it can't replace the judgment needed to make the right call. That responsibility, as with everything else on this page, stays with you; *you remain the expert*.
  - **The future of Software Engineering:** less focus on manual typing, more on architecture, strategy, domain logic, and system thinking — engineers shift toward being *architects*, *designers*, *analysts*, *reviewers*, with value moving from writing code to **problem-solving and engineering judgement**.
- **Request paid AI tool(s) for work:** paid tools are faster, safer, more capable, and better at coding/documentation/long context, etc. — ask about access to tools like GitHub Copilot for coding, Microsoft Copilot for general purpose, etc., depending on what your company supports. A coding AI + general-purpose AI combo is ideal. See the [4-Tier Model Framework](#4-tier-model-framework-credit-efficiency) below for guidance.
- **Extra tips:** start a new chat now and then to avoid stale/biased context, reset memory occasionally, use dictation/voice typing to save time (built into most AI tools, or your OS — e.g. `Win + H` on Windows), and always combine AI with old-school research if needed (e.g. good search terms, StackOverflow, official documentation, logging/tracing) — the official docs remain authoritative when you're stuck or in doubt (e.g. the official documentation of a tool like Kubernetes, Python, etc.).

### Conclusion

AI is a game changer for Software Engineers and in general life — **but only if used wisely.** Use it as a powerful assistant that enhances your capabilities, accelerates learning, and improves the speed and quality of your work, while you remain the *expert* responsible for the thinking, decision-making, architecture, and problem-solving. The most effective engineers use AI to amplify their expertise, not replace it.

---

## Framework: Which AI Tool/Model for Which Task

> **Note:** Not intended to be 100% complete — just the general split that works well for me.

### 1. General purpose

Whatever general-purpose AI chat tool your company recommends/provides (e.g. ChatGPT, Microsoft Copilot, Google Gemini, etc.) — use this for general theory, explanations, learning, writing/documentation help, brainstorming, design/architecture, thinking, and any non(-application)-specific tasks (e.g. non-coding-specific tasks). This is typically already available to you at no extra effort/cost (e.g. it does not cost you *monthly credits* for GitHub Copilot if you use Microsoft Copilot for those tasks (see [Billing/Cost of General‑purpose AI tools like Microsoft Copilot](#billingcost-of-generalpurpose-ai-tools-like-microsoft-copilot) below), etc.), so it's a good default for anything that isn't tied to a specific codebase or specific application.

> **Reuse recurring general-purpose work:** Save templates or create a dedicated agent for repeated writing, summarization, or research tasks instead of re-entering the same instructions each time. See [Reusable AI Workflows and Agents: General Purpose](#general-purpose-microsoft-365-copilot) for a short Microsoft 365 Copilot agent example, including availability and policy considerations.

#### Billing/Cost of General‑purpose AI tools like Microsoft Copilot
General‑purpose AI services like Microsoft Copilot are typically billed at the **subscription or platform level**, meaning the cost of running AI models is *covered by the plan or license* you’re on rather than charged per prompt or per individual user (unlike GitHub Copilot’s individually metered credits). **Microsoft Copilot example:**
- **Personal Microsoft 365 subscription** — You personally have effectively unlimited Copilot usage because all AI compute is included in your license. Access to higher‑end reasoning models may still be **rate‑limited, feature‑restricted, or subject to fair‑use controls** depending on your subscription tier, but you are never billed per prompt or for selecting a more advanced model.
- **Organizational Microsoft 365 account** — You likewise have effectively unlimited personal usage, but all backend AI compute — including the higher cost of advanced reasoning models — is billed at the **tenant/organization level**. Organizations may implement **usage monitoring, throttling, access controls, departmental restrictions, or governance policies** to manage compute spend, ensure compliance, protect data, and control who can use higher‑end models or resource‑intensive features.

### 2. Specific

These are AI tools that are designed for specific tasks or applications, rather than being general-purpose. They often have deeper integration with particular platforms or workflows, making them more efficient for those contexts. Below I explain two categories I focus on: coding and other specific applications (e.g. Atlassian products, Microsoft 365 apps, etc.).

#### Coding

For coding specifically, my personal preference is **GitHub Copilot in VS Code**. This is usually available through your company because it helps engineers work faster and better — so what you actually use highly depends on what your company supports/provides. 

These tools are usually billed at the **individual user level**, meaning each user consumes credits or incurs costs based on their own usage rather than being covered by a broader subscription or organizational plan like general-purpose AI tools like Microsoft Copilot (see [Billing/Cost of General‑purpose AI tools like Microsoft Copilot](#billingcost-of-generalpurpose-ai-tools-like-microsoft-copilot)).

See the [4-Tier Model Framework](#4-tier-model-framework-credit-efficiency) below for how to pick a model tier within Copilot (or similar tools) efficiently and avoid wasting credits.

> **Reuse recurring coding work:** Maintain task-specific prompts, shared repository instructions, and specialist agents for implementation, testing, and code review. See [Reusable AI Workflows and Agents: Coding](#coding-github-copilot-in-vs-code) for the GitHub Copilot example, cross-repository reuse, and saving/syncing guidance.

> **Note:** This is just a reference with general explanation (as explained before), for the full tutorial and guide on how to use VS Code with GitHub Copilot, refer to the [official documentation and tutorials provided by GitHub](https://docs.github.com/en/copilot), such as [Getting Started with GitHub Copilot in VS Code](https://docs.github.com/en/copilot/get-started/quickstart?tool=vscode).

> For the practical account setup, see [Code Editor](Code_Editor.md). It covers using a personal account for portable editor settings and the work account that holds an employer-provided Copilot license, as well as separating Git identities and authentication. This account guidance is included there because it is about configuring the editor and development environment, rather than an AI workflow.

#### Other Specific applications
Many tools you already use have their own built-in AI features, which are often the fastest way to get something done because they already have full context of that application/data. Examples:

- **Atlassian products (Confluence, Jira)** — e.g. **Rovo**, for generating/summarizing documentation, searching across spaces, and answering questions grounded in your team's own content.
- Similar built-in AI assistants in other tools you use (e.g. Microsoft 365 Copilot in Office apps, IDE-integrated assistants, etc.)

Prefer these application-specific assistants when the task is scoped to that application/data, and fall back to a general-purpose tool otherwise.

> When an application supports saved prompts or custom agents, apply the same [reusable workflow principles](#reusable-ai-workflows-and-agents) to recurring tasks, adapting the setup to that application's supported features and permissions.

---

## 4-Tier Model Framework (Credit Efficiency)

> **Note:** This is the central framework I use to decide which model to reach for. It's mostly relevant for coding, since coding assistants are where I burn through the most credits, but the same 4 tiers apply to any other AI usage too (writing, research, brainstorming, etc.), not just coding. It is a **flexible** framework and also depends on the specific situation of course, but in general the principle is to match the model's capability (and cost) to the complexity and scope of the task at hand.

AI tools/assistants are usually metered by **credits** (a finite, often monthly, budget), and the higher-capability models consume credits far faster than lighter ones. Using the most expensive/highest-capability model for everything burns through that budget quickly for little extra benefit on routine work.

**A practical 4-tier framework (see also [AI & Software Engineering — General Usage](#ai--software-engineering--general-usage), such as remain the expert, keep your core skills, etc.):**

<a id="4-tier-framework-table"></a>

| Tier | Cost | Use for | Example models (Claude / GPT / Gemini) |
|---|---|---|---|
| **No cost** | **Free / included in your license** (see for how these are billed: [Billing/Cost of General‑purpose AI tools like Microsoft Copilot](#billingcost-of-generalpurpose-ai-tools-like-microsoft-copilot)) | General theory, explanations, brainstorming, design/architecture, thinking, learning, etc. — anything not tied to your actual codebase (you can of course still use it for coding-related tasks, but for actually changing the code these tools are less convenient than an integrated tool like GitHub Copilot), see [General purpose](#1-general-purpose) above. This also includes application‑integrated AI already covered by your license, such as Atlassian Confluence/Jira’s **Rovo** for generating, searching, and summarizing documentation (see [Specific applications](#2-specific) above). | Any general chat tool available to you (ChatGPT, Microsoft Copilot, Gemini, etc.), plus built‑in app AI like Confluence Rovo. **Tip:** In tools like Microsoft Copilot, you can manually switch to a higher‑tier reasoning model (e.g., `Claude Opus`, `Claude Sonnet`, `GPT‑5`, etc.) when needed (see details in the [*Practical Rule of Thumb*](#practical-rule-of-thumb) below for when to use higher‑tier reasoning models). |
| **Low cost** | Cheapest coding tier (see for billing with these AI tools: [Specific AI: Coding](#coding)) | Documentation/docs, simple/small fixes/changes in your codebase, simple/small test fixes/generations, quick questions, small scripts, formatting/rewording/grammar, etc. | Claude Haiku / GPT-5 Mini / Gemini Flash |
| **Medium cost** | Moderate (see for billing with these AI tools: [Specific AI: Coding](#coding)) | Most day-to-day coding tasks: features, Terraform/Kubernetes/Helm configs, CI/CD, troubleshooting, code review, refactoring, test generation, etc.; do not use it for simple things like documentation only, very small fixes/features, etc., use the low cost model for that. | Claude Sonnet / GPT-5 / Gemini Pro |
| **High cost** | Most expensive (see for billing with these AI tools: [Specific AI: Coding](#coding)) | ONLY for very large tasks and/or many things at once — large migrations, big multi-file/architectural changes, large-scale refactoring, deep root-cause debugging, security reviews, etc. Use sparingly, do not use it for the medium or low cost tasks explained above. | Claude Opus / GPT-5 (deep reasoning) / Gemini Pro (advanced reasoning) |

> **Personal experience:** For the **no-cost** tier, the specific tool has rarely mattered much to me and they are all good (e.g. ChatGPT, Gemini, Microsoft Copilot), so you can just use the one that is available to you. General-purpose tools such as Microsoft Copilot and ChatGPT are often comparable for learning, brainstorming, explanations, and documentation. For **coding**, however, I've generally had the best experience with **[automatic model selection][automatic-model-selection] in GitHub Copilot** (for example, *Optimize for: Balance*). In my experience, it consistently selects the most appropriate model at a significantly lower credit cost than I would achieve manually, while still producing high-quality results. The underlying coding models themselves (e.g. Claude, GPT, Gemini, etc.) are often more similar than people expect, so the exact model usually matters less than providing good context, reviewing the output, and verifying that the result meets your requirements. See details in [automatic model selection][automatic-model-selection].

### Practical Rule of Thumb
[automatic-model-selection]: #automatic-model-selection
[4-tier-framework-table]: #4-tier-framework-table

**Practical rule of thumb:** For *general, non-coding tasks*, start with the **no-cost tier**, switching to a higher-reasoning model when needed. For *coding tasks*, use [automatic model selection][automatic-model-selection] by default. If you select a model manually for coding tasks (as explained in [automatic model selection][automatic-model-selection]), start with a **lower-tier** model and move up to a **medium- or higher-tier** model only when the task becomes more complex or the results are insufficient. The **no-cost tier** is also useful for *general-purpose work* and as a *fallback* if you run out of coding credits.
1. **General / non‑coding / not in your repository:** Use the **no‑cost** tier for anything that isn’t tied to your codebase — general theory, explanations, documentation, research, planning, and learning. The **default/automatic model** (e.g., Microsoft Copilot’s standard model) is usually sufficient here. When you need deeper reasoning — such as architectural exploration, algorithm design, or complex technical research — you can optionally switch to a **higher‑tier reasoning model** (e.g., `Claude Opus`, `Claude Sonnet`, `GPT‑5`, etc.) even in the no‑cost tier, since these tasks don’t consume coding credits from GitHub Copilot for example.
    - **Note:** The *default/automatic* model is usually sufficient here and should generally be your starting point. While many tools allow you to manually select a more advanced reasoning model (e.g. Claude Opus, Claude Sonnet, GPT‑5, etc.), these models usually still have restricted or limited access. Because of this, it's usually best to stay on *default/automatic* and only switch when you have a clear need for deeper reasoning, such as architectural exploration, algorithm design, difficult root-cause analysis, or complex technical research. This gives you the best balance between capability, availability, and cost efficiency. See for details on how these AI tools are billed: [Billing/Cost of General‑purpose AI tools like Microsoft Copilot](#billingcost-of-generalpurpose-ai-tools-like-microsoft-copilot).
2. **Coding / in your repository:** Use **[automatic model selection][automatic-model-selection]** by default. In my experience, it consistently chooses a more appropriate model at a much lower credit cost than manual selection while still handling all work well, from documentation and bug fixes to refactoring, tests, CI/CD, and larger development tasks. Only switch to **manual model selection** if automatic selection repeatedly produces poor results or consistently chooses unsuitable models. When selecting manually, use the **low tier** for simple tasks, the **medium tier** for most day-to-day development work, and the **high tier** only for exceptionally large or complex work as explained in the [table in this section][4-tier-framework-table]. If your coding credits run out, fall back to the **no-cost tier** and optionally use a higher-tier reasoning model such as `Claude Opus`, `Claude Sonnet`, or `GPT-5` when needed. Other general points here:<a id="automatic-model-selection"></a>
    - **Use automatic model selection by default when it offers a discount (for example, GitHub Copilot's 10% discount), but check that the selected model matches the [table in this section][4-tier-framework-table]. If it does not, switch back to manual selection:** Automatic selection chooses a model for each request, using provider-specific signals such as task complexity, the amount and type of context, the requested mode, model availability, expected response speed, and usage or credit cost. Its choices may not always match the model you would have chosen, so a discount alone does not mean it is the best fit. **Keep automatic selection enabled by default when it consistently gives reliable results and chooses models that broadly match the framework above**. When the tool shows which model it selected, check it and review the response quality. Watch for patterns: the model may be too weak for the task, or unnecessarily expensive; frequent use of a higher-cost model for tasks that do not need it can cost you more. Do not choose an expensive, high-tier model just because it is available: most tasks do not need one, and using it routinely can consume credits quickly for little added benefit. Switch to manual selection if automatic selection repeatedly chooses unsuitable models, gives inconsistent results, offers too little control, or picks a model that does not match the task's tier. When selecting manually, choose the lowest-cost model that can reliably do the work, and move up only when the task genuinely requires more capability or a cheaper model has struggled, as described in the table above. **Pro tip for credit efficiency:** If the initially chosen low-cost model from the automatic selection (e.g. GPT low-cost) doesn't work well for a specific task, try switching to a different provider's low-cost model (e.g. Claude low-cost) *before* upgrading to a higher-cost tier. Automatic selection often already identifies the correct cost tier, so staying within that tier but trying a different provider can save considerable additional credits while losing almost no time — you'll know quickly whether it works, and since auto-select usually gets it right on the first try anyway, you're not losing anything by testing this strategy. Only move up to a higher tier if the low-cost models across different providers consistently underperform. In my experience, GitHub Copilot's automatic selection with "optimize for: Balance" (= *Balances cost/speed and capability based on task complexity.*) consistently gives good responses for almost all tasks and has saved me a significant number of credits compared with choosing a medium-cost model by default. I mean really significant: tasks that would normally consume around 500 to 1000 credits when I manually selected a medium-cost model such as Claude Sonnet often used only about 1 to 10 credits with automatic selection. For larger tasks, automatic selection usually identified the need for a more capable model on its own and still tended to use considerably fewer credits because of the smarter model selection and available context. Most of my work, including documentation, simple coding tasks, bug fixes, new features, tests, and general development work, was handled very well at a much lower cost. I have been particularly impressed by how well automatic selection chooses the appropriate model for the task. In practice, it almost always selected a suitable low-, medium-, or higher-cost model without any manual intervention (even if I thought it may need a higher-cost model, it handled the task well with the model it selected). Even for larger tasks, including substantial refactors and more involved development work, its choices were generally very good and produced the results I expected. Only in relatively rare cases with exceptionally large or complex tasks did I feel the need to manually choose a higher-capability model. Even then, the automatic selection was often still reasonable and usable. The specific models chosen vary depending on the provider and the models available at the time, but in general I have found the selected models across providers to perform well (so not only Claude but also the other models such as GPT models, etc.). Because of this, I recommend leaving automatic selection enabled by default. It provides an excellent balance between quality and credit consumption while still selecting more capable models when they are genuinely needed. Although it is still worth checking which model was chosen and how many credits were consumed, automatic selection has consistently been one of the most effective ways for me to reduce credit usage without sacrificing quality at all. **In short, use automatic selection by default when it offers a worthwhile discount and reliably chooses an appropriate tier. In my experience, GitHub Copilot has done this consistently and saved me a huge number of credits. Check the selected model and the results, switch to manual selection if automatic selection repeatedly misses the mark, and choose the lowest-cost model that can reliably handle the task.**
    - **Usage note and tip for coding if using general-purpose AI like Microsoft Copilot (e.g. if your GitHub Copilot credits run out):** You can reuse the same core instructions and structure from a GitHub Copilot prompt, but adapt it to Microsoft Copilot's chat workflow rather than copying VS Code-specific YAML, file paths, or slash-command syntax. See [Reusable AI Workflows and Agents](#reusable-ai-workflows-and-agents) for the example template and workflow principles. Provide codebase context by uploading relevant files or a project archive, then ask for file-based outputs when appropriate. Apply the proposed changes locally and review them with VS Code's Git integration, `git diff`, or another diff tool; run your own tests and checks before relying on them.
    - **Reduce context per interaction:** Reduce the context provided for each interaction: make sure to reset your session when switching between tasks (i.e., open a new chat). Reducing context size is not just about efficient token usage — it also focuses the model's attention on what you actually need, which tends to yield better results. This matters because most metered tools bill or throttle based on the number of input and output tokens per request, and in chat-based sessions each new message typically re-sends the *entire* prior conversation history — so a long-running session can cost several times more per turn than a fresh one, purely due to accumulated baggage, even if the model still has to "read" (and you pay for) irrelevant old files or discussion that no longer add value. A smaller, focused context also reduces the chance of the model mixing up unrelated tasks or producing overly long/hedged answers, which can trigger extra follow-up prompts just to correct course — so resetting your session between tasks is an essentially free way to cut token usage while keeping (or improving) output quality.
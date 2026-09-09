# AI

Practical reference on AI — what it is, agents, prompt engineering, and how I use it (and think it should be used) as a Software Engineer, including a framework for picking the right tool/model for a given task and using paid credits efficiently.

> **Note:** This is a huge and fast-moving topic. This page intentionally stays short and opinionated rather than complete — it covers only what is useful for my own day-to-day work. The linked sources go into far more depth.

## Table of Contents

- [AI & ML Background](#ai--ml-background)
  - [What is AI?](#what-is-ai)
  - [Models, Harnesses & Example Models](#models-harnesses--example-models)
  - [AI Agents](#ai-agents)
  - [Prompt Engineering](#prompt-engineering)
- [AI & Software Engineering — General Usage](#ai--software-engineering--general-usage)
  - [Conclusion](#conclusion)
- [Framework: Which AI Tool/Model for Which Task](#framework-which-ai-toolmodel-for-which-task)
  - [1. General purpose](#1-general-purpose)
  - [2. Specific](#2-specific)
- [4-Tier Model Framework (Credit Efficiency)](#4-tier-model-framework-credit-efficiency)

---

## AI & ML Background

> **Note:** This section is deliberately short — AI/ML is a very large and fast-moving field. See the further reading links below each subsection for more depth and details, the section itself is kept concise.

### What is AI?

Artificial Intelligence (AI) is, broadly, the field of building systems that perform tasks which normally require human intelligence — recognizing patterns, understanding language, reasoning, and generating content. **Machine Learning (ML)** is the main approach behind most modern AI: instead of hand-coded rules, a model learns patterns directly from large amounts of data. Most of the tools referenced on this page (ChatGPT, GitHub Copilot, Claude, Gemini, etc.) are built on **Large Language Models (LLMs)** — a type of ML model trained on huge amounts of text/code that predict and generate text, and that can be extended with tools/agents to take actions (search, run code, edit files, call APIs, etc.).

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

In practice (e.g. GitHub Copilot's *agent mode*), this means you can give it a task like "add a feature", "fix this bug", or "refactor this module", and it will explore the repository, make the edits across multiple files, run tests/builds, and iterate — instead of only suggesting a snippet for you to copy-paste. This makes agents very useful for larger or more repetitive tasks, but the same principle applies as everywhere else on this page: **you stay responsible for reviewing what it did.**

**Further reading:**

- [What are AI agents? — IBM](https://www.ibm.com/topics/ai-agents)
- [GitHub Copilot agent mode documentation](https://docs.github.com/en/copilot/concepts/agents)
- [Introduction to AI agents — Google Cloud](https://cloud.google.com/discover/what-are-ai-agents)

### Prompt Engineering

Prompt engineering is simply the practice of writing your input to an AI tool in a way that gets you better, more accurate, and more usable output. A few techniques/tips that consistently help:

- **Be specific and give context.** State the goal, relevant constraints (language, framework, versions), and what "done" looks like. Vague prompts get vague answers.
- **Show, don't just tell.** Provide examples of the input/output format you want, or an existing piece of code/style to match.
- **Break large tasks into smaller steps.** Ask for a plan first or provide a plan yourself, then execute step by step, rather than one giant ambiguous request.
- **Give it a role, when useful.** E.g. "review this as a senior security engineer" shifts the kind of feedback you get.
- **Iterate.** Treat the first answer as a draft — refine with follow-up questions instead of expecting a perfect result immediately.
- **Ask it to reason/explain, for hard problems.** Asking for step-by-step reasoning or trade-offs (instead of just "the answer") improves quality on non-trivial tasks.
- **Constrain the output** (format, length, style) when you need something specific, e.g. "respond only with a JSON object", "keep it to a short bullet list".
- **State what NOT to do**, when relevant (e.g. "don't change unrelated files", "don't add new dependencies").

**Further reading:**

- [Prompt engineering — Wikipedia](https://en.wikipedia.org/wiki/Prompt_engineering)
- [Prompt engineering guide — OpenAI](https://platform.openai.com/docs/guides/prompt-engineering)
- [What is prompt engineering? — IBM](https://www.ibm.com/topics/prompt-engineering)
- [Prompting guide — Google Gemini](https://ai.google.dev/gemini-api/docs/prompting-strategies)

---

## AI & Software Engineering — General Usage

> **Note:** This is a general overview, not meant to be complete — just the concepts that matter day-to-day, condensed rather than fully detailed.

AI can massively increase your productivity as a Software Engineer — it helps you learn faster, understand better, work more efficiently, and be more creative, etc. **But your own thinking and expertise always remain the core.** Treat AI as a smart colleague or intern that supports you, NOT as a replacement for your role — always keep thinking critically. 

**Some general guidelines for using AI effectively in software engineering and in general life include (not meant to be exhaustive, just some important points):**

- **Where AI can help:** creativity & ideas (brainstorming solutions, architecture/design trade-offs), writing & documenting (docs, commit messages, PR descriptions, specs/comments), coding & technical tasks (debugging, explaining libraries/algorithms, example code/tests, automation, refactoring ideas), learning & understanding (explaining complex topics, comparisons, summaries, quick Q&A instead of Googling/StackOverflow), and general productivity (planning, restructuring text, sharper communication, sanity-checking ideas), etc.
- **Use it correctly:** combine thinking for yourself with using AI (think first, or in parallel, depending on the situation) rather than letting AI take over — this keeps you the expert, avoids dependency, keeps you in control of quality, and helps you learn more. AI is for *deepening, improving, and speeding up* work, not replacing it.
- **Stay the expert:** use AI as support, understand and verify what it generates, keep reasoning through complex problems yourself, and remember that strategic choices, system design, and interpretation remain human work — AI can and will make mistakes, and you're the one who has to catch them. AI is a force multiplier, NOT a replacement for human engineering.
- **The future of Software Engineering:** less focus on manual typing, more on architecture, strategy, domain logic, and system thinking — engineers shift toward being *architects*, *designers*, *analysts*, *reviewers*, with value moving from writing code to problem-solving.
- **Request paid AI tool(s) for work:** paid tools are faster, safer, more capable, and better at coding/documentation/long context, etc. — ask about access to tools like GitHub Copilot for coding, Microsoft Copilot for general purpose, etc., depending on what your company supports. A coding AI + general-purpose AI combo is ideal. See the [4-Tier Model Framework](#4-tier-model-framework-credit-efficiency) below for guidance.
- **Extra tips:** start a new chat now and then to avoid stale/biased context, reset memory occasionally, use dictation/voice typing to save time (built into most AI tools, or your OS — e.g. `Win + H` on Windows), and always combine AI with old-school research (good search terms, StackOverflow, official documentation, logging/tracing) — the official docs remain authoritative when you're stuck or in doubt.

### Conclusion

AI is a game changer for Software Engineers and in general life — **but only if used wisely.** Use it as a powerful assistant that strengthens your expertise, while you remain the critical thinker, the architect, and the problem solver.

---

## Framework: Which AI Tool/Model for Which Task

> **Note:** Not intended to be 100% complete — just the general split that works well for me.

### 1. General purpose

Whatever general-purpose AI chat tool your company recommends/provides (e.g. ChatGPT, Microsoft Copilot, Google Gemini, etc.) — use this for general theory, explanations, learning, writing/documentation help, brainstorming, and any non-specific tasks (e.g. non-coding-specific tasks). This is typically already available to you at no extra effort/cost (e.g. it does not cost you *monthly credits* for GitHub Copilot if you use Microsoft Copilot for those tasks, etc.), so it's a good default for anything that isn't tied to a specific codebase or specific application.

### 2. Specific

**Coding**

For coding specifically, my personal preference is **GitHub Copilot in VS Code**. This is usually available through your company because it helps engineers work faster and better — so what you actually use highly depends on what your company supports/provides. See the [4-Tier Model Framework](#4-tier-model-framework-credit-efficiency) below for how to pick a model tier within Copilot (or similar tools) efficiently and avoid wasting credits.

> **Note:** This is just a reference with general explanation (as explained before), for the full tutorial and guide on how to use VS Code with GitHub Copilot, refer to the [official documentation and tutorials provided by GitHub](https://docs.github.com/en/copilot), such as [Getting Started with GitHub Copilot in VS Code](https://docs.github.com/en/copilot/get-started/quickstart?tool=vscode).

**Other Specific applications**

Many tools you already use have their own built-in AI features, which are often the fastest way to get something done because they already have full context of that application/data. Examples:

- **Atlassian products (Confluence, Jira)** — e.g. **Rovo**, for generating/summarizing documentation, searching across spaces, and answering questions grounded in your team's own content.
- Similar built-in AI assistants in other tools you use (e.g. Microsoft 365 Copilot in Office apps, IDE-integrated assistants, etc.)

Prefer these application-specific assistants when the task is scoped to that application/data, and fall back to a general-purpose tool otherwise.

---

## 4-Tier Model Framework (Credit Efficiency)

> **Note:** This is the central framework I use to decide which model to reach for. It's mostly relevant for coding, since coding assistants are where I burn through the most credits, but the same 4 tiers apply to any other AI usage too (writing, research, brainstorming, etc.), not just coding. It is a **flexible** framework and also depends on the specific situation of course, but in general the principle is to match the model's capability (and cost) to the complexity and scope of the task at hand.

AI tools/assistants are usually metered by **credits** (a finite, often monthly, budget), and the higher-capability models consume credits far faster than lighter ones. Using the most expensive/highest-capability model for everything burns through that budget quickly for little extra benefit on routine work.

**A practical 4-tier framework:**

| Tier | Cost | Use for | Example models (Claude / GPT / Gemini) |
|---|---|---|---|
| **No cost** | Free / included in your license (no metered credits, unlike GitHub Copilot's coding credits) | General theory, explanations, and learning, etc. — anything not tied to your actual codebase (see [General purpose](#1-general-purpose) above) — as well as specific application-integrated AI already included in your license, e.g. Atlassian Confluence/Jira's **Rovo** for generating, searching, and summarizing documentation (see [Specific applications](#2-specific) above), etc. | Whatever general chat tool is available to you (ChatGPT, Microsoft Copilot, Gemini, etc.), plus built-in app AI like Confluence Rovo |
| **Low cost** | Cheapest coding tier | Docs, simple/small changes in your codebase, quick questions, small scripts, formatting/rewording/grammar, etc. | Claude Haiku / GPT-5 Mini / Gemini Flash |
| **Medium cost** | Moderate | Most day-to-day coding tasks: features, Terraform/Kubernetes/Helm configs, CI/CD, troubleshooting, code review, refactoring, etc. | Claude Sonnet / GPT-5 / Gemini Pro |
| **High cost** | Most expensive | ONLY for very large tasks and/or many things at once — large migrations, big multi-file/architectural changes, large-scale refactoring, deep root-cause debugging, security reviews, etc. Use sparingly. | Claude Opus / GPT-5 (deep reasoning) / Gemini Pro (advanced reasoning) |

> **Personal experience:** for the **no cost** tier, it hasn't really mattered much which tool I use — for example Microsoft Copilot and ChatGPT are very comparable. But for all the **coding** tiers (low through high), I've generally found the **Claude models** perform noticeably better than the alternatives (at least as of 2026).

**Practical rule of thumb**: start at the **low** or **medium** tier by default (depending on the task, such as quick edits or small scripts for low, and day-to-day coding for medium, etc.), and only escalate to the **high** tier when the task genuinely needs it (large blast radius, high complexity, or the cheaper tier already struggled) — since credits are finite, save the expensive model for when it actually matters.

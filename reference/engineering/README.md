# Engineering & Coding Reference

Concise engineering guidance shared across projects, part of the [Reference](../README.md). Keep each topic in one place rather than duplicating language tutorials, package templates, and design notes.

---

## Table of Contents

- [Scope and approach](#scope-and-approach)
- [Contents](#contents)

---

## Scope and approach

This area follows the broader Reference [Scope and Tool Specificity](../README.md#scope-and-tool-specificity). The engineering guides are deliberately selective and illustrative, not exhaustive specifications, complete tutorials, or checklists of everything a project must implement. They highlight the main concepts, useful practices, and decisions worth preserving.

- **Practical scope:** Focus on reusable engineering practices, conventions, and decision criteria for packages, applications, and automation. Include brief conceptual context or an illustrative example when it helps explain a choice, but link to official documentation for fundamental theory, complete APIs, syntax, and version-dependent behavior. This is a practical decision guide, not an exhaustive reference or a requirement to adopt every listed practice.
- **Decisions over copied theory:** Preserve the choice, relevant constraints and alternatives, and why an approach is useful. An upstream tutorial can explain a language feature; it cannot recover a project's reasons for selecting it. Keep broadly reusable reasoning here and actual project-specific decisions with the owning project, rather than turning either into another general-purpose tutorial.
- **Brief and authoritative:** Use short, scannable bullets containing the practice or decision, its rationale where needed, and direct links for more detail, especially official language and tool documentation. Avoid long narrative walkthroughs and copied theory; expand only enough to understand the choice or avoid a meaningful mistake. Documentation should not need rewriting whenever an equivalent implementation changes.
- **Explore beyond the summary:** Follow the linked official documentation and reliable online sources for complete explanations and current details. AI can help explore a concept, compare options, or explain unfamiliar code, but verify its claims against authoritative sources and the actual project context. These summaries provide orientation, not a replacement for learning or checking the tools being used.
- **One source of truth:** Keep shared guidance in the appropriate guide within this engineering reference, including language- and package-type-specific practices, rather than creating competing design pages in every consumer repository. The [contents](#contents) separate related topics without duplicating them. Consuming projects, including those in separate repositories, should link here once from their README, using section links where useful; their own documentation covers behavior, setup, decisions, and intentional exceptions rather than copying shared guidance.
- **Use code as the implementation example:** A detail does not need a separate explanation merely because that exact setup is not documented online. For example, routine logging configuration can be understood from the working code instead of being duplicated as a walkthrough here or in large source comments. If a choice matters for consistent behavior or prevents a recurring mistake, capture the practice and reason briefly; document public contracts and non-obvious local constraints where readers need them.
- **Maintainability matters:** Every copied explanation creates another item to review and keep accurate. Stale theory, duplicated examples, and contradictory guidance become liabilities even when they originally seemed helpful. Prefer an authoritative link and a small amount of durable reasoning; remove redundant material rather than measuring completeness by volume. The [documentation concept](Concepts.md#documentation) explains this burden, appropriate placement, and my personal shift toward concise documentation.
- **Keep guidance versioned and accessible:** Maintain shared engineering guidance in a Git repository so related guidance and code changes can be reviewed and versioned in their owning repositories, searched together in the IDE, and read offline after cloning. A separate documentation service can support collaboration, but should not be required to retrieve essential engineering context. READMEs can link directly to the relevant guide or section; individual source comments do not need to repeat those links. Cross-repository changes still need coordination, and consumers should check that the current guidance applies to their supported versions.

---

## Contents

| Guide | Scope |
|-------|-------|
| [Languages & Tools](Languages_and_Tools.md) | Short practices and authoritative references for languages, runtimes, and tools; framework details stay with their official docs and consuming projects. |
| [Repository & Project Organization](Repository_Organization.md) | Repository boundaries, placement decisions, component setup, CI and release separation, migration steps, and industry examples. |
| [Package Design & Organization](Packages.md) | Package boundaries, naming, team SDKs, specialized tools, scripts, documentation, and releases. |
| [Engineering Concepts](Concepts.md) | SDLC, system-level reuse, automation, security, observability, error handling, testing, lifecycle, modeling, and practical documentation guidance. |
| [Software Engineering Principles](Software_Engineering_Principles.md) | Design principles, their trade-offs, and a linked short list. |

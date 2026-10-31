---
description: "Use when writing, updating, or verifying documentation, guides, READMEs, and Markdown examples."
applyTo: "**/*.md"
---

# Documentation Standards

- Be terse: explain project-specific behavior, decisions, constraints, and consequences, not routine implementation details or general theory.
- Verify affected and relevant surrounding claims, examples, links, and diagrams against actual implementation/configuration. Flag uncertainty; do not invent facts or perform an unrelated repository-wide documentation audit.
- Describe behavior, not the editing history. Link to owning code and authoritative external documentation instead of copying explanations.
- Keep each topic in its existing owning README or focused document; avoid parallel explanations and unnecessary files. Follow existing descriptive naming and casing.
- Use a small fenced plain-text diagram when relationships or flow benefit from it. Preserve useful diagrams in their owning document; verify arrows and distinguish required and optional steps.
- Wrap prose at natural boundaries and indent list continuations. Use consistent headings and `---` between major level-two sections.
- Add a table of contents for longer documents, covering levels two through four. Omit it for short documents and agent instruction files.
- Use plain bullets, no emoji status indicators, and no reading-time headers.

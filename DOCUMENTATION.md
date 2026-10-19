# Documentation Guidelines

These guidelines apply to documentation maintained in DevHub. Keep each page focused and follow the owning area's terminology and structure.

---

## Table of contents

- [Structure and navigation](#structure-and-navigation)
- [Writing and maintenance](#writing-and-maintenance)

---

## Structure and navigation

- Use one `#` heading for the page title, `##` for main sections, and `###` for subsections; do not skip heading levels.
- Include a table of contents linking to the page's main sections. Nest subsection links where useful, and keep the links current when headings change.
- Separate consecutive `##` sections with a standalone `---` line, with a blank line above and below it. This includes the boundary after the table of contents.
- Keep entry-point READMEs concise. Put detailed guidance in the owning area's documentation and link to it rather than duplicating it.
- Use relative Markdown links for repository files and heading anchors for sections. Update affected indexes and incoming links when adding, moving, or renaming pages.
- Keep the [Reference](reference/README.md) focused on reusable concepts and fundamentals rather than trying to document every product or tool. When a topic depends on a specific tool, explain only the general context needed here and link to that tool's official documentation for current, complete usage and configuration details.

---

## Writing and maintenance

- Write concise, practical explanations for the intended audience. Follow nearby terminology, formatting, and examples.
- Verify claims against source material or official documentation. Distinguish DevHub conventions from product behavior, and mark unfinished guidance clearly.
- Keep reusable guidance generic; place project-specific implementation details in the owning project's repository.
- Treat official project documentation as the source of truth for tool-specific behavior, commands, configuration, and version-dependent details. Use DevHub to explain the underlying concepts and link readers to the official docs when deeper or current product guidance is needed.
- Use safe example values and never include credentials or other sensitive information.
- Review changed links, table-of-contents anchors, and formatting; run relevant documentation checks and `git diff --check`.

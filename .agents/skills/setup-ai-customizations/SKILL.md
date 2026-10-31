---
name: setup-ai-customizations
description: "Use when setting up, reviewing, or planning repository AI customizations: the common APM baseline, root AGENTS.md, optional domain packages, scoped instructions, or exceptional nested guidance."
---

# Set Up Repository AI Customizations

Create a small, maintainable repository setup that layers the shared DevHub APM baseline with local project context.

## Procedure

1. **Confirm scope.** Treat a plan-only request as read-only: inspect and report proposed changes without editing or installing. Work only in the requested repository; do not install globally or modify sibling/workspace repositories unless explicitly requested. Ask a question only when a missing decision prevents a safe setup.
2. **Inspect before editing.** Identify the repository root and read its APM manifest and lockfile, existing `AGENTS.md` files, Copilot instructions, scoped instructions, package manifests, owning READMEs, and documented validation/setup commands. Check repository status and preserve unrelated work and authored customizations. Do not overwrite or regenerate an existing `AGENTS.md` or other local guidance wholesale.
3. **Find the design authority when available.** In the DevHub source tree, the package-level overview is `packages/apm/README.md` and the common package guide is `packages/apm/common/README.md`. In a consumer, resolve the common package from its `apm.yml` and lockfile and inspect the corresponding package under `apm_modules/`; a known DevHub source checkout is another option. Do not mistake the consumer's root `README.md` for either overview just because this skill is installed under `.agents/skills/`. If neither source is available, say so and proceed only from verified repository conventions; do not invent missing design guidance.
4. **Build the local context with the right primitives.**
   - Declare the common APM package at the repository root only if it is missing, following the repository's existing dependency source and pinning conventions. Keep domain packages opt-in: add or reference one only when the repository needs that domain guidance.
   - Create or carefully update a concise root `AGENTS.md` in every repository as the entry point. Pair verified links to owning architecture, engineering, and usage documentation with directions about when to read them. This steers context selection instead of relying solely on automatic discovery, but does not guarantee that linked files are loaded. Add only necessary local constraints; do not restate general standards.
   - Put cross-cutting rules in scoped instructions with accurate file globs, role identity and responsibilities in agents, repeatable procedures in skills, and reusable task requests in prompts. Before adding a nested `AGENTS.md`, confirm all three conditions: its constraints are distinct and consequential; putting them in the root guidance would burden unrelated tasks; and a root link to the owning README is insufficient. Language, size, or package boundaries alone do not justify nesting. Improve missing owning documentation and link to it from the root rather than adding a parallel explanation to `AGENTS.md`.
   - Do not create a duplicate `.github/copilot-instructions.md` by default. Add a harness-specific adapter only when the actual host needs it, keep it limited to host-specific context, and avoid contradictory copies of root guidance.
5. **Deploy only when requested.** Review the explicit target and existing deployment paths before installing. For Copilot, use an explicit target, such as `apm install --only apm --target copilot`, from the consumer root after confirming its manifest; do not run a compile step for Copilot. Treat policy or dependency warnings and incomplete dry-run previews as unresolved checks even when the command exits successfully. Resolve them before deployment; never use `--force` or bypass policy. Stop and report conflicts rather than replacing local authored or generated customizations. Do not install to another target, global location, or sibling repository without authorization.
6. **Verify and report.** Check changed manifests and instruction metadata, file/glob links, root-to-document links, and that no general standards were duplicated. When deployment was requested, inspect installed files and verify discovery in the intended host separately; file presence does not prove runtime discovery, and a successful dry-run is not proof of deployment or complete dependency resolution. Check host support for `AGENTS.md` and scoped instructions rather than assuming it. Separately verify behavior with a representative task that exercises a local repository convention, a task covered by any new scoped instruction, and a relevant failure or edge case when feasible. Instructions guide behavior, not enforce it. Report these results separately, along with what was created, preserved, deployed, discovered, and any unresolved warnings or unavailable checks.

## Output

Summarize the resulting repository layout, common and optional package configuration, preserved customizations, validation and deployment evidence, and remaining gaps. For plan-only work, provide the proposed changes and checks without modifying files.

## Source navigation

These links are for the DevHub source tree; installed paths differ. The overview's [repository setup](../../../../README.md#repository-setup), [authoring guidance](../../../../README.md#authoring-repository-guidance), [nested-instruction criteria](../../../../README.md#nested-instructions), and [activation checks](../../../../README.md#verify-activation) provide the broader design.

- [Common package contents](../../../apm_modules/_local/common/README.md)

# Reusable Agent Skills

This directory contains generic Agent Skills that describe repeatable work, independent of one particular project. Each skill lives in its own directory with a `SKILL.md` file whose YAML `name` matches that directory. The current generic skills are:

- [`implement-change`](./implement-change/SKILL.md) — implement and verify a focused code change.
- [`docs`](./docs/SKILL.md) — create or update documentation using the owning project's conventions.

## Use a skill

In GitHub Copilot in VS Code, invoke a skill by its name (for example, `/implement-change` or `/docs`) and provide the task and any project-specific context. Compatible Copilot experiences may also load an applicable skill based on its description. See the [AI reference](../../reference/AI.md#coding-github-copilot-in-vs-code) for the broader setup and usage guidance.

These skills are versioned in DevHub as reusable starting points. A link to a GitHub `SKILL.md` is useful as a human reference, but does not install or load the skill into another repository. To make a skill available there, copy its complete skill directory into that repository's recognized `.github/skills/` directory, or install it in a supported user-profile skill location for reuse across workspaces. Keep project architecture, security requirements, and validation commands in that project's own instructions or context skill; do not assume this generic skill knows them.

For example, the separate [devhub-homelab](https://github.com/CollinPoetoehena/devhub-homelab) project keeps its homelab-specific context alongside the project and layers it on top of the generic documentation and implementation workflows. For why shared workflows belong here while project implementations live separately, see the [DevHub README](../../README.md#what-belongs-in-devhub).

---
description: "Use when editing GitHub Actions workflows, reusable actions, or scripts invoked by CI."
applyTo: "**/.github/workflows/**,**/.github/actions/**"
---

# GitHub Actions Guidelines

Use general best practices for GitHub Actions and follow the common guidelines.

Specifically for GitHub Actions, in addition to general best practices:

- Use GitHub-hosted runners by default; use a self-hosted runner only when the repository's `AGENTS.md` or existing workflows name one.
- Reuse organization- or repository-provided workflows and actions for shared pipeline steps instead of copying their implementations into consumers.
- Keep longer shell/Python logic in separate script files; workflows and actions should invoke the same tooling used locally.
- Preserve existing protected environments, permissions, and secret boundaries; grant only the permissions required by each job.
- Apply this guidance to scripts used by workflows even when they live outside `.github`; do not broaden automatic matching to every script in a repository.

Use relevant available skills for additional procedures and references.
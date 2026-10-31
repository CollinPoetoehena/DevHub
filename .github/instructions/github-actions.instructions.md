---
description: "Use when editing GitHub Actions workflows, reusable actions, or scripts invoked by CI."
applyTo: "**/.github/workflows/**,**/.github/actions/**"
---

# DevHub GitHub Actions Instructions

Developer note (Copilot may ignore this note): these instructions are distributed in the common APM package. See the [Copilot setup guide](https://github.com/CollinPoetoehena/devhub/blob/master/docs/COPILOT-SETUP.md) for installation and maintenance.

- All team workflows should use these runners:
  - TODO: here state you can use general-purpose runners if applicable
  - TODO: here later state the self-hosted runner used by DevHub if applicable
- Reuse DevHub workflows/actions for shared pipeline steps instead of copying their implementations into consumers.
- Keep longer shell/Python logic in separate script files; workflows and actions should invoke the same tooling used locally.
- Preserve existing protected environments, permissions, and secret boundaries; grant only the permissions required by each job.
- Apply this guidance to scripts used by workflows even when they live outside `.github`; do not broaden automatic matching to every script in a repository.
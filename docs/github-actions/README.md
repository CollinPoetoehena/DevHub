# GitHub Actions

Documentation for DevHub's reusable GitHub Actions: [reusable workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) that other repositories call, and [custom actions](https://docs.github.com/en/actions/sharing-automations/creating-actions/about-custom-actions) they use as steps.

## Why the documentation lives here

`.github/workflows/` and `.github/actions/` contain only definitions, which GitHub executes. Explanations of design, triggers, permissions, and limitations would bloat those files and mix documentation with executable configuration. Each reusable workflow and action is an independent component, so each gets one document here that explains it fully.

## Layout

| Folder | Content |
|---|---|
| [`workflows/`](workflows/README.md) | One document per reusable workflow in [`.github/workflows/`](../../.github/workflows/) |
| [`actions/`](actions/README.md) | One document per action in `.github/actions/<name>/` |

## Adding a workflow or action

1. Add the definition: `.github/workflows/<name>.yml` with `on: workflow_call`, or `.github/actions/<name>/action.yml`.
2. Add `workflows/<name>.md` or `actions/<name>.md` with its purpose, usage, interface (inputs, secrets, outputs), required permissions, behavior, and limitations, and list it in that folder's README.
3. Follow the [GitHub Actions instructions](../../.github/instructions/github-actions.instructions.md).

Workflows that only run in DevHub itself, such as [`repo-tools.yml`](../../.github/workflows/repo-tools.yml), are documented by the component they validate.

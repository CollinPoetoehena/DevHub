# Homelab Agent Skills

These project-specific skills add homelab context to the generic workflows maintained in [DevHub](https://github.com/CollinPoetoehena/DevHub/tree/main/.github/skills). Install or invoke the generic workflow together with the matching homelab context skill:

| Skill | Purpose |
|---|---|
| [`homelab-project`](./homelab-project/SKILL.md) | Project goals, design boundaries, and public-repository security requirements. |
| [`homelab-implement-change`](./homelab-implement-change/SKILL.md) | Homelab context for the generic [`implement-change`](https://github.com/CollinPoetoehena/DevHub/blob/main/.github/skills/implement-change/SKILL.md) workflow. |
| [`homelab-docs`](./homelab-docs/SKILL.md) | Homelab context for the generic [`docs`](https://github.com/CollinPoetoehena/DevHub/blob/main/.github/skills/docs/SKILL.md) workflow. |

Invoke `/homelab-project` for general homelab questions. For implementation and documentation tasks, use `/homelab-implement-change` or `/homelab-docs` and make the corresponding generic workflow available to the assistant as described in the [DevHub skills README](https://github.com/CollinPoetoehena/DevHub/blob/main/.github/skills/README.md). The project-specific skills provide context; the generic skills provide the reusable task workflow.

VS Code discovers repository skills from recognized skill directories in the opened workspace. While this project is nested in DevHub, open the `homelab/` folder as its own workspace to discover these project skills; after extraction, open the `devhub-homelab` repository itself. A GitHub link to a skill is a reference, not a remote installation mechanism; install or copy the generic skill as described in DevHub's [AI reference](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/AI.md#coding-github-copilot-in-vs-code).

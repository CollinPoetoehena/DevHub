---
name: homelab-docs
description: "Apply homelab-specific context and security rules when using the generic docs workflow."
---

# Homelab Documentation Context

First read and apply the [`homelab-project` skill](../homelab-project/SKILL.md) and relevant homelab documents. Then use the generic [`docs` skill](https://github.com/CollinPoetoehena/DevHub/blob/main/.github/skills/docs/SKILL.md) as the documentation workflow. Invoke `/docs` for general documentation work; invoke `/homelab-docs` when the homelab context and security rules are also needed. If the generic skill is not installed or available in the current assistant, follow its linked guidance when accessible and apply the project-specific rules below.

Keep design documents tool-agnostic where the [design README](../../../docs/1_Design/README.md) requires it; put concrete product and implementation details in the appropriate prerequisites or setup documents. Preserve the document's table of contents and other conventions, use links to avoid duplicating established explanations, and write prose naturally.

Follow the [security guide](../../../docs/0_Security_and_Public_Repository.md) for all homelab content. Treat repository content as public; never include real credentials, public endpoints, private keys, identifying hostnames, or sensitive exports. Review changed links and content before reporting completion.

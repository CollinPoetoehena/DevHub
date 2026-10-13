---
name: homelab-implement-change
description: "Apply homelab-specific context and security rules when using the generic implementation workflow."
---

# Homelab Implementation Context

First read and apply the [`homelab-project` skill](../homelab-project/SKILL.md), then use the generic [`implement-change` skill](https://github.com/CollinPoetoehena/DevHub/blob/main/.github/skills/implement-change/SKILL.md) as the implementation workflow. Invoke `/implement-change` for general changes; invoke `/homelab-implement-change` when homelab-specific context and security rules are also needed. If the generic skill is not installed or available in the current assistant, follow its linked guidance when accessible and apply the project-specific rules below.

Follow the goals and design boundaries in the [homelab README](../../../README.md) and [design README](../../../docs/1_Design/README.md). Apply the public-repository requirements in the [security guide](../../../docs/0_Security_and_Public_Repository.md) to code, configuration, documentation, command output, and generated files. In particular, do not introduce real credentials, public endpoints, identifying hostnames, private decryption keys, or sensitive state. Keep tool-specific implementation in setup documents and the relevant project files rather than adding product details to tool-independent design documents.

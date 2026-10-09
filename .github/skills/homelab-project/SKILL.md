---
name: homelab-project
description: "Use when working on the DevHub homelab: answering questions, changing documentation or configuration, designing infrastructure, or reviewing security and public-repository content."
---

# Homelab Project

Use this skill whenever working on the homelab so recommendations and changes follow the project's purpose, design boundaries, and public-repository security requirements.

## Read the Project Guidance

Before making recommendations or changes, consult these sources in order:

1. [Homelab README](../../../homelab/README.md) for project scope, structure, and links to the wider DevHub reference.
2. [Design README](../../../homelab/docs/1_Design/README.md) for architecture and the distinction between stable, tool-independent design and tool-specific implementation.
3. [Security and Public Repository](../../../homelab/docs/0_Security_and_Public_Repository.md) for what may be published, secrets handling, review requirements, and incident response.

Read the specific design or setup documents relevant to the request as well. Treat the security guide as mandatory for all changes, including documentation, code, configuration, examples, logs, and generated files.

## Working Rules

- Preserve the homelab's documented goals and existing design decisions. Keep design documents tool-agnostic where the design README requires it; put concrete product and implementation details in the appropriate prerequisites or setup documents.
- Assume all repository content is public. Never add real credentials, public IP addresses, globally routable IPv6 addresses, homelab domains or hostnames, VPN secrets, or sensitive exports. Use reserved documentation values and nonfunctional placeholders.
- Use the established secrets-management mechanism for the relevant system. Never commit plaintext secrets, private decryption keys, vault passwords, Terraform state, saved plans, or rendered files containing decrypted secrets.
- Review all changed and generated content for sensitive details before declaring work complete. If a secret may already have been exposed, recommend revoking or rotating it; deleting it from the current file is not sufficient.
- Make focused changes, follow existing repository conventions, and update directly related documentation or links when behavior or guidance changes.
- Validate links and formatting for documentation changes; run the smallest relevant checks for configuration or code changes and report any checks that could not be run.

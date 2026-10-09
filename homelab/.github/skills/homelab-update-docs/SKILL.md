---
name: homelab-update-docs
description: "Create or update homelab Markdown documentation using the existing project structure, formats, and security guidance."
---

# Update Homelab Documentation

Before editing, read and apply the [`homelab-project` skill](../homelab-project/SKILL.md), then inspect the relevant existing Markdown documents and follow their structure and conventions.

Keep changes concise, accurate, and in the correct design or setup document. Preserve established patterns such as table of contents sections and `---` separators where the surrounding documents use them. Wrap prose naturally; do not insert manual line breaks in the middle of sentences. Use Markdown links and safe example values, and follow the [security guide](../../../docs/0_Security_and_Public_Repository.md) so no real secrets or identifying public details are added.

Check changed links and run `git diff --check`. Report what was updated and any validation not performed.

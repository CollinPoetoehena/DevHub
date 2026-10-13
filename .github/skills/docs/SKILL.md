---
name: docs
description: "Create or update documentation accurately, following the owning project's structure, terminology, and style."
---

# Documentation

Create or update documentation for the request in the correct location and at the appropriate level of detail.

Before editing, read the relevant project instructions, existing documentation, and source material. Follow project-specific terminology, structure, links, formatting, and security rules. Do not invent product behavior or claim implementation details that have not been verified.

## Writing and Editing

1. Identify the intended audience and purpose; keep the change focused on that purpose.
2. Reuse established sections and cross-link to authoritative explanations rather than duplicating them.
3. Keep examples safe and nonfunctional where credentials, addresses, or environment details are involved.
4. Update tables of contents, indexes, and directly affected links when adding, moving, or renaming content.
5. Preserve unrelated edits and avoid changing implementation files unless explicitly requested.

## Validation and Report

Check changed internal links where practical, review the diff for consistency and sensitive information, and run relevant documentation checks such as formatting or `git diff --check`. Report what changed and which checks were or were not run.

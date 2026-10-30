---
description: "Use when editing Ansible playbooks, roles, inventories, variables, or templates for infrastructure."
applyTo: "**/playbooks/**,**/roles/**,**/inventory/**,**/inventories/**,**/group_vars/**,**/host_vars/**,**/ansible.cfg"
---

# DevHub Ansible Instructions

Developer note (Copilot may ignore this note): these instructions are distributed in the common APM package. See the [Copilot setup guide](https://github.com/CollinPoetoehena/devhub/blob/master/docs/COPILOT-SETUP.md) for installation and maintenance.

- Reuse the repository's inventory, environment groups, roles, and variable layout; keep environment-specific settings out of shared tasks.
- Prefer idempotent Ansible modules over shell commands. Where commands are necessary, define accurate change/failure conditions.
- Keep credentials in the repository's established secret mechanism, not plaintext inventories or templates; prevent secret-bearing task output.
- Limit validation to the intended inventory and hosts; do not apply playbooks to live infrastructure merely to validate an edit.
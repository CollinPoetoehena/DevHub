---
description: "Use when editing Ansible playbooks, roles, inventories, variables, or templates: mandatory rules and validation commands on top of the common instructions."
applyTo: "**/ansible/**,**/playbooks/**,**/roles/**,**/inventory/**,**/inventories/**,**/group_vars/**,**/host_vars/**,**/ansible.cfg"
---

# Ansible Instructions

These rules add Ansible specifics to the [common instructions](https://github.com/CollinPoetoehena/DevHub/tree/main/packages/apm/common) of `devhub-common` (coding, security, documentation, and Git), which always apply. Where they differ, these rules refine the common ones; the repository's own configuration and `AGENTS.md` take precedence over both.

## Skills

- Apply the `ansible` skill for naming, style, secret management, and linting conventions.

## Rules

- Reuse the repository's inventory, environment groups, roles, and variable layout; keep environment-specific settings out of shared tasks.
- Prefer idempotent Ansible modules over shell commands. Where commands are necessary, define accurate change and failure conditions with `changed_when`, `failed_when`, `creates`, or `removes`.
- Use fully qualified collection names, such as `ansible.builtin.copy`, and give every play and task a name that starts with a verb.
- Keep credentials in the repository's established secret mechanism, not plaintext inventories or templates; prevent secret-bearing task output with `no_log: true`.
- Set `become: true` only on the tasks or plays that need privileges.
- Limit validation to the intended inventory and hosts; do not apply playbooks to live infrastructure merely to validate an edit.

## Validation

Run from the Ansible root; use the repository's configured commands when they differ:

```sh
ansible-lint
yamllint .
ansible-playbook --syntax-check -i <inventory> <playbook>
```

Run `ansible-playbook --check --diff --limit <hosts>` only against hosts the user approved.

## References

- [Ansible documentation](https://docs.ansible.com/ansible/latest/)
- [Ansible tips and tricks](https://docs.ansible.com/ansible/latest/tips_tricks/index.html)
- [ansible-lint](https://ansible.readthedocs.io/projects/lint/)
- [Ansible Vault](https://docs.ansible.com/ansible/latest/vault_guide/index.html)

---
description: "Use when editing Ansible playbooks, roles, inventories, variables, or templates: essential conventions and validation commands alongside the common guidelines."
applyTo: "**/ansible/**,**/playbooks/**,**/roles/**,**/inventory/**,**/inventories/**,**/group_vars/**,**/host_vars/**,**/ansible.cfg"
---

# Ansible Guidelines

Use general best practices for Ansible and follow the common guidelines in `devhub-guidelines-core`.

Specifically for Ansible, in addition to general best practices:

Repository configuration, owning documentation, and `AGENTS.md` may refine or override these shared defaults. When applicable sources conflict, follow higher-priority policy and surface unresolved conflicts rather than assuming universal host precedence.

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

Use the `ansible` skill for additional Ansible procedures and references.

## References

- [Ansible documentation](https://docs.ansible.com/ansible/latest/)
- [Ansible tips and tricks](https://docs.ansible.com/ansible/latest/tips_tricks/index.html)
- [ansible-lint](https://ansible.readthedocs.io/projects/lint/)
- [Ansible Vault](https://docs.ansible.com/ansible/latest/vault_guide/index.html)

Use relevant available skills for additional procedures and references.

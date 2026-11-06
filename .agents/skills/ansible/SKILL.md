---
name: ansible
description: 'Ansible conventions: task and play naming, idempotent modules, fully qualified collection names, privilege escalation, inventory and group_vars layout, Ansible Vault secret management, YAML style, task ordering, and ansible-lint and yamllint checks. Use when writing, reviewing, or linting Ansible playbooks, roles, inventories, or variables.'
---

# Ansible

Index for Ansible work. The Ansible and common instructions take precedence over the reference.

## When to Use This Skill

- Writing or reviewing playbooks, roles, or tasks
- Organizing inventories, `group_vars`, or `host_vars`
- Managing secrets with Ansible Vault
- Linting or dry-running playbooks

## Steps

1. **Write or change playbooks and roles.** Open [references/patterns.md](references/patterns.md) for naming, idempotency, module selection, privileges, style, and task ordering.
2. **Handle secrets.** Follow the secret management section in [references/patterns.md](references/patterns.md), using the repository's established mechanism.
3. **Validate.** Run the validation commands from the Ansible instructions and report each result.

## Gotchas

- **Commands always report changed:** `command` and `shell` tasks report a change on every run; set `changed_when`, or use `creates` or `removes`.
- **`vars` override `defaults`:** put values users should override in a role's `defaults/main.yml`; `vars/main.yml` has much higher precedence.
- **`when` is already Jinja:** write `when: enable_feature`, not `when: "{{ enable_feature }}"`.
- **Handlers run late and once:** notified handlers run at the end of the play, once; use `ansible.builtin.meta: flush_handlers` when a later task depends on them.
- **Check mode skips commands:** `--check` does not run `command` and `shell` tasks unless they set `check_mode: false`, so a check run can miss failures.

## References

- [Ansible documentation](https://docs.ansible.com/ansible/latest/)
- [Variable precedence](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html#understanding-variable-precedence)

# Ansible

Reusable [Ansible](https://docs.ansible.com/) roles and playbooks, used for configuration management and application deployment.

Each role lives in its own dedicated repository. This file serves as the index and reference for all Ansible roles, and documents conventions shared across them.

## Dev-Hub

This repository ([dev-hub](https://github.com/CollinPoetoehena/dev-hub)) is the central reference for all Ansible roles. It holds:

- This index file ([Ansible.md](Ansible.md)) — register new roles here and link their repositories.
- Conventions, structure guidelines, and usage patterns documented below.
- All shared publishing logic: GitHub Actions workflows, helper scripts, and any other CI/CD tooling used to release or validate roles. Individual role repositories reference or reuse these centrally managed pipelines rather than duplicating them.

## Structure

Each role repository follows the [Ansible Role Directory Structure](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html#role-directory-structure):

```
<role-name>/
├── tasks/
│   └── main.yml      # Entry point — all tasks for this role
├── defaults/
│   └── main.yml      # Default variable values (lowest precedence)
├── vars/
│   └── main.yml      # Role variables (higher precedence than defaults)
├── handlers/
│   └── main.yml      # Handlers triggered by notify
├── templates/
│   └── *.j2          # Jinja2 templates
├── files/            # Static files to copy to managed hosts
├── meta/
│   └── main.yml      # Role metadata and dependencies
└── README.md         # Role documentation
```

Only the directories actually needed by a role are included — empty placeholder directories are omitted.

## Role Naming Convention

Roles follow the [Ansible Galaxy naming convention](https://galaxy.ansible.com/docs/contributing/creating_role.html): lowercase letters, digits, and underscores only. Names should be descriptive and scoped to what the role configures, e.g. `docker`, `nginx`, `java_install`.

## Usage

Each role repository contains its own README with usage instructions. The general pattern for referencing a role via `ansible-galaxy`:

```bash
ansible-galaxy role install git+https://github.com/CollinPoetoehena/<role-repo>.git,main
```

Or declare it in a `requirements.yml` file:

```yaml
roles:
  - name: <role-name>
    src: git+https://github.com/CollinPoetoehena/<role-repo>.git
    version: main
```

Then install with:

```bash
ansible-galaxy install -r requirements.yml
```

## Roles

| Role | Repository | Description |
|------|------------|-------------|
| _(none yet)_ | | Roles will be listed here as they are added |

## README Template

When creating a new role repository, use the following template as the starting point for its `README.md`:

```markdown
# <role-name>

> Part of [dev-hub/Ansible](https://github.com/CollinPoetoehena/dev-hub/blob/main/Ansible.md) — see that file for conventions, structure guidelines, and the full role index.

<Short description of what this role does.>

## Requirements

List any dependencies or prerequisites here.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| | | |

## Usage

```yaml
- hosts: all
  roles:
    - role: <role-name>
```
```

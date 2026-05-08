# Ansible

Reusable [Ansible](https://docs.ansible.com/) roles and playbooks, used for configuration management and application deployment.

Each role lives in its own dedicated repository. This file serves as the index and reference for all Ansible roles, and documents conventions shared across them.

## Dev-Hub

This repository ([dev-hub](https://github.com/CollinPoetoehena/dev-hub)) is the central reference for all Terraform modules, see [README.md](README.md) for the full design and index of all component types.

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

Roles follow the [Ansible Galaxy naming convention](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_reuse_roles.html): lowercase letters, digits, and underscores only. Names should be descriptive and scoped to what the role configures, e.g. `docker`, `nginx`, `java_install`.

Role repositories are named using the pattern `ansible-role-<topic>`, where `<topic>` matches the role name (e.g. `ansible-role-docker`, `ansible-role-nginx`, `ansible-role-java_install`).

## Usage

Each role repository contains its own README with usage instructions. The general pattern for referencing a role via `ansible-galaxy`:

```bash
ansible-galaxy role install git+https://github.com/CollinPoetoehena/<role-repo>.git,main
```

Or declare it in a `requirements.yml` file:

```yaml
roles:
  - name: <role-name>
    src: https://github.com/CollinPoetoehena/<role-repo>.git
    scm: git
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

Requirements file example (same directory as ansible.cfg, create a file called requirements.yml):
```yaml
---
roles:
  - name: <role-name>
    src: https://github.com/CollinPoetoehena/<role-name>.git
    scm: git
    version: <version or branch>
``` 

Then install with: 
```sh
# NOTE: Example of roles path for -p is "roles/" (you can also specify this in ansible.cfg)
ansible-galaxy install -r requirements.yml -p <path/to/roles>
```

Example playbook using this role (e.g. site.yml):
```yaml
- hosts: all
  roles:
    - role: <role-name>
```

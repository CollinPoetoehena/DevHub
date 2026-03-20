# Ansible

Reusable [Ansible](https://docs.ansible.com/) roles and playbooks, used for configuration management and application deployment.

## Structure

Each role lives in its own subdirectory under `ansible/roles/` and follows the [Ansible Role Directory Structure](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html#role-directory-structure):

```
ansible/
├── roles/
│   └── <role-name>/
│       ├── tasks/
│       │   └── main.yml      # Entry point — all tasks for this role
│       ├── defaults/
│       │   └── main.yml      # Default variable values (lowest precedence)
│       ├── vars/
│       │   └── main.yml      # Role variables (higher precedence than defaults)
│       ├── handlers/
│       │   └── main.yml      # Handlers triggered by notify
│       ├── templates/
│       │   └── *.j2          # Jinja2 templates
│       ├── files/            # Static files to copy to managed hosts
│       ├── meta/
│       │   └── main.yml      # Role metadata and dependencies
│       └── README.md         # Role documentation
└── README.md
```

Only the directories actually needed by a role are included — empty placeholder directories are omitted.

## Role Naming Convention

Roles follow the [Ansible Galaxy naming convention](https://galaxy.ansible.com/docs/contributing/creating_role.html): lowercase letters, digits, and underscores only. Names should be descriptive and scoped to what the role configures, e.g. `docker`, `nginx`, `java_install`.

## Usage

Reference a role from this repository in your playbook using `ansible-galaxy`:

```bash
# Install a role directly from this repository
ansible-galaxy role install git+https://github.com/CollinPoetoehena/dev-hub.git#/ansible/roles/<role-name>,main
```

Or declare it in a `requirements.yml` file:

```yaml
roles:
  - name: <role-name>
    src: git+https://github.com/CollinPoetoehena/dev-hub.git#/ansible/roles/<role-name>
    version: main
```

Then install with:

```bash
ansible-galaxy install -r requirements.yml
```

## Roles

| Role | Description |
|------|-------------|
| _(none yet)_ | Roles will be listed here as they are added |

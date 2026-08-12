# mgmtvm

> Part of [dev-hub/Ansible](https://github.com/CollinPoetoehena/dev-hub/blob/main/Ansible.md) — see that file for conventions, structure guidelines, and the full role index.

Configures a Management VM that serves as the access point to workloads (typically residing in a Management DMZ). The role installs and configures all tooling required to manage infrastructure.

> **User, group, sudo, and SSH key management are not part of this role.**  
> Use the [ansible-role-users](https://github.com/CollinPoetoehena/ansible-role-users) role for that. Apply it alongside this role in your playbook (see example below).

## Requirements

- **OS**: RHEL 8+ or a compatible Enterprise Linux (EL) distribution (Rocky Linux, AlmaLinux, CentOS Stream). Uses `dnf` throughout.
- **Ansible**: 2.14+

## Features

| Feature | Controlled by |
|---------|--------------|
| Azure CLI | `install_azure_cli` |
| Kubernetes tools (kubectl, kubeadm, helm) | `install_k8s_tools` |
| Python virtual environment | `install_python_venv` |
| Ansible (inside venv) | `install_ansible` |
| Development & debugging tools | `install_dev_tools` |

## Variables

### Feature flags

| Variable | Default | Description |
|----------|---------|-------------|
| `install_azure_cli` | `true` | Install Azure CLI from the Microsoft RPM repository |
| `install_k8s_tools` | `true` | Install kubectl, kubeadm, and helm |
| `install_python_venv` | `true` | Create a Python virtual environment at `mgmtvm_venv_path` |
| `install_ansible` | `true` | Install Ansible inside the virtual environment |
| `install_dev_tools` | `true` | Install development and debugging packages (git, vim, jq, htop, …) |

### Kubernetes

| Variable | Default | Description |
|----------|---------|-------------|
| `kubectl_version` | `"1.29"` | Major.minor version for the k8s repo; applies to both kubectl and kubeadm. Patch version is resolved by the pkgs.k8s.io repository. |
| `helm_version` | `""` | Helm package version to install (e.g. `"3.14.0"`). Empty installs the latest version available in EPEL. |

### Azure CLI

| Variable | Default | Description |
|----------|---------|-------------|
| `azure_cli_version` | `""` | Azure CLI package version to install (e.g. `"2.60.0"`). Empty installs the latest version available in the Microsoft RPM repo. |

### Python / Ansible

| Variable | Default | Description |
|----------|---------|-------------|
| `mgmtvm_venv_path` | `"/opt/venv"` | Filesystem path where the Python virtual environment is created |
| `mgmtvm_pip_packages` | `[]` | Extra pip packages to install inside the virtual environment |
| `ansible_version` | `""` | Ansible version to install in the venv (e.g. `"9.5.1"`). Empty installs the latest version. |

## Usage

### Requirements file

```yaml
---
roles:
  - name: mgmtvm
    src: https://github.com/CollinPoetoehena/ansible-role-mgmtvm.git
    scm: git
    version: 1.0.0
  # User/group/sudo/SSH key management is handled by a separate role:
  - name: users
    src: https://github.com/CollinPoetoehena/ansible-role-users.git
    scm: git
    version: 1.0.0
```

Then install with:

```sh
# NOTE: Example of roles path for -p is "roles/" (you can also specify this in ansible.cfg)
ansible-galaxy install -r requirements.yml -p <path/to/roles>
```

### Example playbook

> **Note:** User, group, sudo, and SSH key management are handled by [ansible-role-users](https://github.com/CollinPoetoehena/ansible-role-users).  
> Variables and usage examples for that role are intentionally omitted here — keeping them in one place avoids duplication and means only that role's README needs updating if its interface changes.

```yaml
---
- hosts: mgmtvm
  become: true
  vars:
    kubectl_version: "1.29"

    # Extra Python packages for infrastructure automation
    mgmtvm_pip_packages:
      - boto3
      - azure-mgmt-compute

  roles:
    - role: mgmtvm   # installs tooling
    - role: users    # manages OS users, groups, sudo, and SSH keys (see ansible-role-users)
```

### Selective execution with tags

```sh
# Only install tools
ansible-playbook site.yml --tags packages

# Only manage users (users role)
ansible-playbook site.yml --tags users

# Only configure SSH keys (users role)
ansible-playbook site.yml --tags ssh
```
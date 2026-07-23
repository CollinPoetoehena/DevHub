# Ansible Configuration Management

TODO: this is now just added as a start from my earlier K8sLab project, update with HomeLab specific stuff, etc. and remove all the K8sLab stuff, etc.

This directory contains Ansible playbooks and roles for configuring and managing the TransacFlow infrastructure, including the jump host (bastion), management VM (tooling), and Kubernetes cluster nodes (control plane and workers).

## Overview

Ansible is used for automated configuration management of all infrastructure components after they are provisioned by Terraform. This includes:
- Jump host (bastion) setup for secure access
- Management VM setup with tooling installation (kubectl, helm, ansible, Azure CLI)
- Kubernetes cluster bootstrapping using Kubeadm
- Container runtime configuration (containerd/CRI-O)
- Network plugin (CNI) installation
- System hardening and security configuration
- Ongoing maintenance and updates

## Directory Structure

```
ansible/
├── ansible.cfg              # Ansible configuration file
├── dta.yml                  # Inventory file for DTA (Development/Test/Acceptance) environment
├── prod.yml                 # Inventory file for production environment
├── site.yml                 # Main playbook that orchestrates all roles 
├── group_vars/              # Global group variables
├── host_vars/               # Host-specific variables
└── roles/                   # Ansible roles (reusable pieces of configuration) for different responsibilities
    ├── common/              # Base configuration for all nodes
    ├── jump_host/           # Jump host/bastion configuration for secure SSH access
    ├── mgmt_vm/             # Management VM with tooling (kubectl, helm, ansible, Azure CLI, etc.)
    ├── container_runtime/   # Container runtime installation
    ├── k8s_control_plane/   # Kubernetes control plane setup
    ├── k8s_worker/          # Kubernetes worker node setup
    └── networking/          # CNI plugin configuration
```
**site.yml** is the conventional name for the top‑level playbook that defines and runs your entire infrastructure in one place. Historically, Ansible borrowed ideas from configuration‑management tools like Puppet and CFEngine, where the top‑level file described the entire site configuration, meaning all hosts, all roles, all environments, the whole infrastructure "site". So, `site.yml` is the **conventional name for the master playbook that orchtestrates everything in your infrastructure**. It is not about a wesbite, but about your "site" as in "your whole environment".

## Role Architecture

The roles are structured around **responsibility**, not individual machines. This provides a scalable, production-ready layout:

### Shared/Reusable Roles
- **common**: Base packages, users, SSH configuration, firewall rules
- **container_runtime**: Containerd or CRI-O installation and configuration
- **networking**: CNI plugin deployment (Calico, Cilium, Flannel)

### Infrastructure-Specific Roles
- **jump_host**: Bastion/jump box for secure SSH access to private network
- **mgmt_vm**: Management VM with all operational tooling (kubectl, helm, ansible, Azure CLI, git)
- **k8s_node**: K8s components including control plane components (API server, controller-manager, scheduler, etcd) and worker node components (kubelet, kube-proxy); can distinguish between control plane node and worker node via tags or inventory groups

## Usage

### Prerequisites
- Ansible 2.9+ installed on the control machine
- SSH access to all target hosts
- Python 3 installed on target hosts
- Terraform infrastructure already provisioned

### Running Playbooks
TODO: make this specific later, these are still example commands
**Full cluster setup:**
```bash
ansible-playbook -i inventories/dta/hosts.yml site.yml
```

**Dry run (check mode):**
```bash
ansible-playbook -i inventories/dta/hosts.yml site.yml --check
```

**With verbose output:**
```bash
ansible-playbook -i inventories/dta/hosts.yml site.yml -vvv
```

## Playbook Flow

The `site.yml` playbook orchestrates role application:

1. **Jump Host**: Applies `common` and `jump_host` roles (bastion/SSH gateway)
2. **Management VM**: Applies `common` and `mgmt_vm` roles (operational tooling)
3. **Control Plane**: Applies `common`, `container_runtime`, and `k8s_node` roles with control plane tags
4. **Workers**: Applies `common`, `container_runtime`, and `k8s_node` roles with worker node tags
5. **Networking**: Applies CNI configuration across the cluster

## Integration with Terraform

Ansible consumes Terraform outputs for dynamic configuration:
- VM IP addresses and hostnames
- Network CIDR ranges
- Resource group names
- SSH key paths

This can be automated using Terraform's `local-exec` provisioner or by manually extracting outputs.

## Best Practices

- **Idempotency**: All tasks are idempotent and can be run multiple times safely
- **Separation of Concerns**: Each role has a single, clear responsibility
- **Environment Isolation**: DTA and production inventories are completely separate
- **Version Control**: All playbooks, roles, and inventory files are version-controlled
- **Testing**: Use `--check` mode before applying changes to production
- **Documentation**: Each role has its own README with specific details

## Troubleshooting

**Connection Issues:**
```bash
ansible all -i inventories/dta/hosts.yml -m ping
```

**Check Ansible Facts:**
```bash
ansible all -i inventories/dta/hosts.yml -m setup
```

**Syntax Check:**
```bash
ansible-playbook site.yml --syntax-check
```

# devhub-ansible-k8s

> Part of [DevHub/Ansible](https://github.com/CollinPoetoehena/DevHub/blob/main/packages/Ansible.md) — see that file for conventions, structure guidelines, and the full role index.

Configures a host with Kubernetes (control plane or worker node) using Ansible.

Primarily used for my personal [homelab in DevHub](https://github.com/CollinPoetoehena/DevHub/blob/main/homelab/README.md) but also suitable for other small-scale lab environments.

**TODO: fill this in below further when this role is fully done:**
## Requirements

- TODO

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| | | |

## Usage

Requirements file example (same directory as ansible.cfg, create a file called requirements.yml):
```yaml
---
roles:
  - name: devhub.k8s
    src: https://github.com/CollinPoetoehena/devhub-ansible-k8s.git
    scm: git
    version: 1.0.0
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
    - role: devhub.k8s
```

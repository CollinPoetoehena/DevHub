# Terraform

> **TODO:** Move this Terraform configuration into a dedicated repository, following the structure and conventions in the [DevHub Terraform reference](../../packages/Terraform.md).

Terraform owns VM provisioning; [Ansible](../ansible/roles/devhub.proxmox/README.md) owns the Proxmox hosts and prepares cloud-init templates. It then configures the guests after provisioning.

- [Proxmox VM module](modules/proxmox-vm/README.md): clone one or more Linux VMs from keyed configurations, with per-VM resources, workload VLAN and cloud-init login/network.
- [Example root configuration](examples/proxmox-vm/main.tf): consumes the module without embedding credentials.

## Running the example

Requires Terraform 1.7+ (below 2.0), Proxmox compatible with `bpg/proxmox` 0.116.x, an existing template and datastore, and a VLAN-aware bridge. The example uses the Ansible Ubuntu template ID `9001`, VM ID `120` and workload VLAN `20`; check availability and adapt these locally before planning. No infrastructure is created by `init`, `validate` or the mocked module tests.

Supply `PROXMOX_VE_ENDPOINT` and `PROXMOX_VE_API_TOKEN` through an approved runtime secret mechanism. The endpoint includes HTTPS and port 8006; the token format is `user@realm!token-id=<YOUR_SECRET>`. Use the least-privilege automation identity prepared by Ansible, not a root login. Do not paste real values into tracked files, command history, logs or chat.

TLS verification remains enabled. Trust the Proxmox certificate's issuing CA on the workstation and use an endpoint matching the certificate; do not work around certificate errors by disabling verification. This module clones existing templates and uses native cloud-init settings, so it does not require provider SSH access or upload snippets.

From this directory:

```bash
cd examples/proxmox-vm
export TF_VAR_node_name='<YOUR_PROXMOX_NODE>'
export TF_VAR_ssh_public_key_file="$HOME/.ssh/id_ed25519.pub"
terraform init
terraform validate
terraform plan
```

Before a real plan or apply, configure an approved secured remote backend with encryption, locking, access controls and backups in the root configuration. The example deliberately supplies no backend credentials or site-specific configuration. Review the plan locally before explicitly choosing to apply it; provisioning and destruction are not part of the automated tests.

Keep real configuration and credentials outside Git. Local variable files, state and common saved-plan extensions are ignored here, but arbitrary plan filenames and redirected output are not automatically protected. Never commit generated state, plans or real endpoint data. Follow [Security and Public Repository](../docs/0_Security_and_Public_Repository.md#terraform-and-infrastructure-state).

## Offline behavior checks

After downloading the provider, tests use a mocked provider and need no Proxmox endpoint, token or running host:

```bash
terraform fmt -check -recursive
terraform -chdir=modules/proxmox-vm init -backend=false
terraform -chdir=modules/proxmox-vm validate
terraform -chdir=modules/proxmox-vm test
```

These verify configuration and input validation, not actual cloning, cloud-init completion, guest connectivity or host permissions. Verify those separately on an approved deployment.

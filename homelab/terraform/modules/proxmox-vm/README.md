# Proxmox VM module

Creates one or more Linux VMs by **fully cloning an existing cloud-init template on the same Proxmox node**, using `bpg/proxmox` 0.116.x. Configure VMs in the `vms` map; each map entry creates one independent VM. Full clones are independent of the source template after creation; linked clones, ISO installs, cross-node cloning, extra disks and custom cloud-init snippets are outside this module's scope.

The parent root configuration owns authentication, TLS and state/backend configuration. See the [Terraform guide](../../README.md) and [complete example](../../examples/proxmox-vm/main.tf). No provider configuration or credentials belong inside the module.

## Usage

Each `vms` map key is the stable Terraform instance key. Keep keys unchanged when editing a VM to avoid changing its Terraform address. Each VM requires its own destination ID, VLAN and public SSH key list; optional values use the defaults below.

```hcl
module "vms" {
  source = "../../modules/proxmox-vm"

  vms = {
    web = {
      name            = "example-web"
      node_name       = var.node_name
      vm_id           = 120
      template_vm_id  = 9001
      vlan_id         = 20
      ssh_public_keys = [trimspace(file(pathexpand(var.ssh_public_key_file)))]
    }
    worker = {
      name            = "example-worker"
      node_name       = var.node_name
      vm_id           = 121
      template_vm_id  = 9001
      vlan_id         = 30
      ssh_public_keys = [trimspace(file(pathexpand(var.ssh_public_key_file)))]
      cpu_cores       = 4
      memory_mb       = 4096
    }
  }
}
```

## Migrating from the single-VM interface

The `vms` input and map-shaped outputs replace the former scalar inputs and outputs. The resource address also changes from `proxmox_virtual_environment_vm.this` to `proxmox_virtual_environment_vm.this["<key>"]`. For an existing deployment, move its state entry to the key used for that VM before planning, replacing the module name and map key as needed:

```bash
terraform state mv \
  'module.vm.proxmox_virtual_environment_vm.this' \
  'module.vm.proxmox_virtual_environment_vm.this["example-vm"]'
```

Terraform state is sensitive. Use the approved backend and handle state backups securely. Review the plan after the move and do not apply if it proposes replacing or destroying an existing VM unexpectedly.

## Template contract

Provide an existing compatible cloud-init template with a Linux boot disk on `scsi0`, a cloud-init drive on `ide2`, and the QEMU guest agent installed and running inside the guest. Select a unique destination VM ID; do not reuse the template ID. Host template creation is outside this module's scope.

The module uses VirtIO networking and a VirtIO SCSI controller, enables the guest agent and disk discard, and defaults to IPv4 DHCP plus IPv6 SLAAC. The bridge/switch must carry the chosen VLAN, and DHCP/Router Advertisements must exist there. It does not create VLANs, network services, firewall policies or host storage. For a static IPv4 address, provide `ipv4_address` in CIDR notation and optionally `ipv4_gateway`; a gateway with DHCP is rejected.

Cloud-init creates a non-root user with public SSH keys and no password supplied by Terraform. Use a trusted cloud image with password authentication disabled and no inherited credentials. Configuration management and guest hardening remain Ansible's responsibility. A successful Terraform operation is not a guarantee that cloud-init or application setup has completed.

## Inputs

The module input is a nonempty `map(object(...))`; the fields below are set separately for each VM.

| Field | Default | Purpose |
| --- | --- | --- |
| `name` | Required | Single-label VM hostname. |
| `node_name` | Required | Existing node with the template. |
| `vm_id` | Required | Unique destination VM ID across this map, 100-999999999. |
| `template_vm_id` | Required | Existing source template VM ID; must differ from this VM's ID. |
| `vlan_id` | Required | Workload VLAN, 2-4094; no implicit native/management network. |
| `ssh_public_keys` | Required | Nonempty list of OpenSSH public keys; never private keys. |
| `datastore_id` | `local-lvm` | Storage for the full clone, boot disk and cloud-init drive. |
| `cpu_cores` | `2` | Positive integer core count. |
| `cpu_type` | `host` | CPU model; choose a common model for migration across unlike hosts. |
| `memory_mb` | `2048` | Dedicated memory in MiB, at least 512. |
| `disk_size_gb` | `20` | Boot disk GiB, **at least the template's disk size**. |
| `bridge` | `vmbr0` | Existing VLAN-aware bridge. |
| `ipv4_address` | `dhcp` | DHCP or static IPv4 CIDR, e.g. `192.0.2.120/24`. |
| `ipv4_gateway` | `null` | Static IPv4 gateway, e.g. `192.0.2.1`; omit for DHCP. |
| `username` | `ubuntu` | Non-root cloud-init user; override for other distributions if needed. |
| `started` | `true` | Start after provisioning. |
| `on_boot` | `true` | Start when the host boots; independent of `started`. |

Terraform cannot check source disk size offline: cloning cannot shrink a disk, so check the template before reducing `disk_size_gb`. Larger disks also require guest filesystem growth. Changes to immutable clone settings may replace the VM; always review a plan before applying, especially for stateful workloads.

## Outputs

`vm_id`, `name`, `node_name`, `ipv4_addresses` and `ipv6_addresses` are maps keyed by the corresponding `vms` input key. Address values remain nested lists grouped by interface, exactly as reported by the guest agent; they can include loopback/link-local addresses and are not a filtered Ansible inventory. A stopped guest or unavailable guest agent cannot provide reliable address discovery.

See [validation commands](../../README.md#offline-behavior-checks) for mocked tests that do not provision infrastructure.

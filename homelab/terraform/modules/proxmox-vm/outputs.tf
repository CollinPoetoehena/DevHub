output "vm_id" {
  description = "Proxmox VM IDs keyed by the corresponding vms input key."
  value = {
    for key, vm in proxmox_virtual_environment_vm.this :
    key => vm.vm_id
  }
}

output "name" {
  description = "VM hostnames keyed by the corresponding vms input key."
  value = {
    for key, vm in proxmox_virtual_environment_vm.this :
    key => vm.name
  }
}

output "node_name" {
  description = "Hosting Proxmox nodes keyed by the corresponding vms input key."
  value = {
    for key, vm in proxmox_virtual_environment_vm.this :
    key => vm.node_name
  }
}

output "ipv4_addresses" {
  description = "IPv4 addresses grouped by interface and keyed by VM; may include loopback addresses."
  value = {
    for key, vm in proxmox_virtual_environment_vm.this :
    key => vm.ipv4_addresses
  }
}

output "ipv6_addresses" {
  description = "IPv6 addresses grouped by interface and keyed by VM; may include loopback and link-local addresses."
  value = {
    for key, vm in proxmox_virtual_environment_vm.this :
    key => vm.ipv6_addresses
  }
}

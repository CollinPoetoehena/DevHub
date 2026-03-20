// All outputs are maps keyed by VM name, matching the input var.vms map.
// Access a specific VM's value with for example: module.vm.private_ip_addresses["k8s-worker-1"]

output "vm_ids" {
  description = "Map of VM name to VM resource ID"
  value       = { for k, v in azurerm_linux_virtual_machine.main : k => v.id }
}

output "private_ip_addresses" {
  description = "Map of VM name to private IP address"
  value       = { for k, v in azurerm_network_interface.main : k => v.private_ip_address }
}

output "public_ip_addresses" {
  description = "Map of VM name to public IP address (only VMs with assign_public_ip = true)"
  value       = { for k, v in azurerm_public_ip.main : k => v.ip_address }
}

output "nic_ids" {
  description = "Map of VM name to NIC ID"
  value       = { for k, v in azurerm_network_interface.main : k => v.id }
}

output "ssh_commands" {
  description = "Map of VM name to SSH command (only VMs with a public IP)"
  value = {
    for k, v in azurerm_public_ip.main :
    k => "ssh ${var.admin_username}@${v.ip_address}"
  }
}

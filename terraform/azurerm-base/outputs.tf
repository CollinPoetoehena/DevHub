# =============================================================================
# Network Component Outputs
# =============================================================================
# ---------------------------------------------------------------------------
# Virtual Networks
# ---------------------------------------------------------------------------

output "vnet_ids" {
  description = "Map of VNet key to VNet resource ID."
  value       = { for k, v in azurerm_virtual_network.main : k => v.id }
}

output "vnet_names" {
  description = "Map of VNet key to VNet name as created in Azure."
  value       = { for k, v in azurerm_virtual_network.main : k => v.name }
}

output "peering_ids" {
  description = "Map of peering key to peering resource ID."
  value       = { for k, v in azurerm_virtual_network_peering.main : k => v.id }
}

# ---------------------------------------------------------------------------
# Network Security Groups
# ---------------------------------------------------------------------------

output "nsg_ids" {
  description = "Map of NSG key to NSG resource ID."
  value       = { for k, v in azurerm_network_security_group.main : k => v.id }
}

# ---------------------------------------------------------------------------
# Subnets
# ---------------------------------------------------------------------------

output "subnet_ids" {
  description = "Map of subnet key to subnet resource ID."
  value       = { for k, v in azurerm_subnet.main : k => v.id }
}

output "subnet_names" {
  description = "Map of subnet key to subnet name as created in Azure."
  value       = { for k, v in azurerm_subnet.main : k => v.name }
}

# =============================================================================
# Virtual Machine Component Outputs
# =============================================================================

// vm_ids is keyed by VM name. All other outputs are keyed by "<vm-name>-<nic-name>".
// Access a specific value with e.g.: module.base.nic_ids["app-server-mgmt-nic"]

output "vm_ids" {
  description = "Map of VM name to VM resource ID."
  value       = { for k, v in azurerm_linux_virtual_machine.main : k => v.id }
}

output "vm_names" {
  description = "Map of VM name to VM name as created in Azure (same as key, included for consistency with other outputs)."
  value       = { for k, v in azurerm_linux_virtual_machine.main : k => v.name }
}

output "private_ip_addresses" {
  description = "Map of NIC key (<vm-name>-<nic-name>) to private IP address."
  value       = { for k, v in azurerm_network_interface.main : k => v.private_ip_address }
}

output "public_ip_addresses" {
  description = "Map of NIC key (<vm-name>-<nic-name>) to public IP address (only NICs with assign_public_ip = true)."
  value       = { for k, v in azurerm_public_ip.main : k => v.ip_address }
}

output "nic_ids" {
  description = "Map of NIC key (<vm-name>-<nic-name>) to NIC resource ID."
  value       = { for k, v in azurerm_network_interface.main : k => v.id }
}

output "nic_names" {
  description = "Map of NIC key (<vm-name>-<nic-name>) to NIC name as created in Azure."
  value       = { for k, v in azurerm_network_interface.main : k => v.name }
}

output "ssh_commands" {
  description = "Map of NIC key (<vm-name>-<nic-name>) to ready-to-use SSH command (only NICs with a public IP)."
  value = {
    for k, v in local.nics : k => "ssh ${var.vms[v.vm_name].admin_username}@${azurerm_public_ip.main[k].ip_address}"
    if v.assign_public_ip
  }
}

output "local_formatted_nics" {
  description = "The local.nics map, included as an output for debugging/visibility purposes."
  value       = local.nics
}

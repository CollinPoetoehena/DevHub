# =============================================================================
# VM Module - Creates Multiple VMs with Network Connectivity
# =============================================================================
# Accepts a map of VM definitions and creates all resources via for_each.
# Resources created per VM:
#   - Public IP          (only for VMs with assign_public_ip = true)
#   - Network Interface  (one per VM, attached to the correct subnet)
#   - Linux VM           (the compute resource)
# =============================================================================

# Public IP — only for VMs that need external access (e.g. jump host)
# https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/public_ip
resource "azurerm_public_ip" "main" {
  for_each = { for k, v in var.vms : k => v if v.assign_public_ip }

  name                    = "${each.key}-pip"
  location                = var.location
  resource_group_name     = var.resource_group_name
  allocation_method       = "Dynamic"
  sku                     = "Basic"
  ip_version              = "IPv4"
  idle_timeout_in_minutes = 4

  tags = var.tags
}

# Network Interface — one per VM, placed in the subnet specified per VM
# https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/network_interface
resource "azurerm_network_interface" "main" {
  for_each = var.vms

  name                = "${each.key}-nic"
  location            = var.location
  resource_group_name = var.resource_group_name

  ip_configuration {
    name                          = "ip-config"
    subnet_id                     = each.value.subnet_id
    private_ip_address_allocation = "Dynamic"
    # Attach public IP only for VMs that have one, null otherwise
    public_ip_address_id = each.value.assign_public_ip ? azurerm_public_ip.main[each.key].id : null
  }

  tags = var.tags
}

# Linux Virtual Machine — one per entry in var.vms
# https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/linux_virtual_machine
resource "azurerm_linux_virtual_machine" "main" {
  for_each = var.vms

  name                = each.key
  location            = var.location
  resource_group_name = var.resource_group_name
  size                = each.value.size
  admin_username      = each.value.admin_username

  # Disable password authentication for security — SSH keys only
  disable_password_authentication = true

  network_interface_ids = [
    azurerm_network_interface.main[each.key].id
  ]

  # Add the SSH public key for authentication via the corresponding private key
  admin_ssh_key {
    username   = each.value.admin_username
    public_key = each.value.ssh_public_key
  }

  os_disk {
    caching              = each.value.os_disk.caching
    storage_account_type = each.value.os_disk.storage_account_type
    disk_size_gb         = each.value.os_disk.disk_size_gb
  }

  source_image_reference {
    publisher = each.value.image.publisher
    offer     = each.value.image.offer
    sku       = each.value.image.sku
    version   = each.value.image.version
  }

  computer_name = each.key # Hostname used for the VM

  tags = var.tags
}

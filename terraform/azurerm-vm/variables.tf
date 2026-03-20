// Map of VMs to create. The map key becomes the VM name.
// Every property needed to fully define a VM lives here — no shared per-VM config outside this variable.
// Only infrastructure context (location, resource group, tags) is expressed as separate variables below.
variable "vms" {
  description = "Map of VMs to create. Key is the VM name."
  type = map(object({
    size             = string // Azure VM size, e.g. Standard_D4s_v5
    subnet_id        = string // Resource ID of the subnet to place the NIC in
    assign_public_ip = bool   // Whether to create and attach a public IP
    admin_username   = string // Admin username for the VM
    ssh_public_key   = string // SSH public key for authentication (sensitive)

    image = object({
      publisher = string
      offer     = string
      sku       = string
      version   = string
    })

    os_disk = object({
      disk_size_gb         = number
      caching              = optional(string, "ReadWrite")
      storage_account_type = optional(string, "StandardSSD_LRS")
    })
  }))
}

variable "location" {
  description = "Azure region where resources will be created."
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group."
  type        = string
}

variable "tags" {
  description = "Tags to apply to all resources."
  type        = map(string)
  default     = {}
}

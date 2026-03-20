// Map of VMs to create. The map key becomes the VM name.
// Every property needed to fully define a VM lives here — no shared per-VM config outside this variable.
// Only infrastructure context (location, resource group, tags) is expressed as separate variables below.
variable "vms" {
  description = "Map of VMs to create. Key is the VM name."
  type = map(object({
    // General VM properties
    size           = string // Azure VM size, e.g. Standard_D4s_v5
    admin_username = string // Admin username for the VM
    ssh_public_key = string // SSH public key for authentication (sensitive)

    // List of NICs to attach to this VM. Each NIC name produces a resource named <vm-name>-<nic-name>
    nics = list(object({
      name             = string                // NIC name — final resource name: <vm-name>-<nic-name>
      subnet_id        = string                // Resource ID of the subnet to place this NIC in
      assign_public_ip = optional(bool, false) // Whether to create and attach a public IP to this NIC
    }))

    // Image reference for the VM. All fields are required to avoid ambiguity.
    image = object({
      publisher = string
      offer     = string
      sku       = string
      version   = string
    })

    // OS disk configuration for the VM
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

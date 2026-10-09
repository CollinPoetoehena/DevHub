variable "vms" {
  description = "VM configurations keyed by stable Terraform instance keys."
  type = map(object({
    name            = string
    node_name       = string
    vm_id           = number
    template_vm_id  = number
    vlan_id         = number
    ssh_public_keys = list(string)
    datastore_id    = optional(string, "local-lvm")
    cpu_cores       = optional(number, 2)
    cpu_type        = optional(string, "host")
    memory_mb       = optional(number, 2048)
    disk_size_gb    = optional(number, 20)
    bridge          = optional(string, "vmbr0")
    ipv4_address    = optional(string, "dhcp")
    ipv4_gateway    = optional(string)
    username        = optional(string, "ubuntu")
    started         = optional(bool, true)
    on_boot         = optional(bool, true)
  }))
  nullable = false

  validation {
    condition     = length(var.vms) > 0
    error_message = "vms must contain at least one VM configuration."
  }

  validation {
    condition = alltrue([
      for vm in values(var.vms) :
      try(
        length(vm.name) <= 63 &&
        can(regex("^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$", vm.name)) &&
        length(trimspace(vm.node_name)) > 0 &&
        vm.vm_id >= 100 && vm.vm_id <= 999999999 && floor(vm.vm_id) == vm.vm_id &&
        vm.template_vm_id >= 100 && vm.template_vm_id <= 999999999 && floor(vm.template_vm_id) == vm.template_vm_id &&
        vm.vm_id != vm.template_vm_id &&
        length(trimspace(vm.datastore_id)) > 0 &&
        vm.cpu_cores >= 1 && floor(vm.cpu_cores) == vm.cpu_cores &&
        length(trimspace(vm.cpu_type)) > 0 &&
        vm.memory_mb >= 512 && floor(vm.memory_mb) == vm.memory_mb &&
        vm.disk_size_gb >= 1 && floor(vm.disk_size_gb) == vm.disk_size_gb &&
        length(trimspace(vm.bridge)) > 0 &&
        vm.vlan_id >= 2 && vm.vlan_id <= 4094 && floor(vm.vlan_id) == vm.vlan_id &&
        (vm.ipv4_address == "dhcp" || can(cidrnetmask(vm.ipv4_address))) &&
        (vm.ipv4_gateway == null || can(cidrnetmask("${vm.ipv4_gateway}/32"))) &&
        (vm.ipv4_address != "dhcp" || vm.ipv4_gateway == null) &&
        vm.username != "root" &&
        can(regex("^[a-z_][a-z0-9_-]{0,31}$", vm.username)) &&
        length(vm.ssh_public_keys) > 0 &&
        alltrue([
          for key in vm.ssh_public_keys :
          can(regex("^(ssh-ed25519|ssh-rsa|ecdsa-sha2-nistp(256|384|521)) [A-Za-z0-9+/]+={0,3}( [^\\r\\n]*)?$", key))
        ]),
        false
      )
    ])
    error_message = "Every VM must have a valid hostname, node, distinct VM/template IDs, resource sizes, VLAN, IPv4 configuration, non-root username and at least one single-line OpenSSH public key."
  }

  validation {
    condition = length(distinct([
      for vm in values(var.vms) : vm.vm_id
    ])) == length(var.vms)
    error_message = "Each VM must have a unique vm_id."
  }
}

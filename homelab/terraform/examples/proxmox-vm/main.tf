terraform {
  required_version = ">= 1.7.0, < 2.0.0"

  required_providers {
    proxmox = {
      source  = "bpg/proxmox"
      version = "~> 0.116.0"
    }
  }
}

provider "proxmox" {
  insecure = false
}

variable "node_name" {
  description = "Existing node containing the cloud-init template."
  type        = string
}

variable "ssh_public_key_file" {
  description = "Local path to an OpenSSH public key (not the private key)."
  type        = string
}

module "vm" {
  source = "../../modules/proxmox-vm"

  vms = {
    example-vm = {
      name            = "example-vm"
      node_name       = var.node_name
      vm_id           = 120
      template_vm_id  = 9001
      vlan_id         = 20
      ssh_public_keys = [trimspace(file(pathexpand(var.ssh_public_key_file)))]
    }
  }
}

output "vm_id" {
  value = module.vm.vm_id
}

output "ipv4_addresses" {
  value = module.vm.ipv4_addresses
}

output "ipv6_addresses" {
  value = module.vm.ipv6_addresses
}

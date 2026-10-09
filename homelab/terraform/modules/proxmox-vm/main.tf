resource "proxmox_virtual_environment_vm" "this" {
  for_each = var.vms

  name          = each.value.name
  node_name     = each.value.node_name
  vm_id         = each.value.vm_id
  description   = "Managed by Terraform."
  started       = each.value.started
  on_boot       = each.value.on_boot
  boot_order    = ["scsi0"]
  scsi_hardware = "virtio-scsi-single"

  clone {
    vm_id        = each.value.template_vm_id
    datastore_id = each.value.datastore_id
    full         = true
  }

  agent {
    enabled = true
  }

  cpu {
    cores = each.value.cpu_cores
    type  = each.value.cpu_type
  }

  memory {
    dedicated = each.value.memory_mb
  }

  disk {
    datastore_id = each.value.datastore_id
    interface    = "scsi0"
    size         = each.value.disk_size_gb
    discard      = "on"
    iothread     = true
  }

  network_device {
    bridge  = each.value.bridge
    model   = "virtio"
    vlan_id = each.value.vlan_id
  }

  initialization {
    datastore_id = each.value.datastore_id
    interface    = "ide2"

    ip_config {
      ipv4 {
        address = each.value.ipv4_address
        gateway = each.value.ipv4_gateway
      }

      ipv6 {
        address = "auto"
      }
    }

    user_account {
      username = each.value.username
      keys     = each.value.ssh_public_keys
    }
  }

  lifecycle {
    precondition {
      condition     = each.value.vm_id != each.value.template_vm_id
      error_message = "Each vm_id must differ from its template_vm_id."
    }

    precondition {
      condition     = each.value.ipv4_address != "dhcp" || each.value.ipv4_gateway == null
      error_message = "ipv4_gateway must be omitted for every VM using DHCP."
    }
  }
}

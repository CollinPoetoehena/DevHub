mock_provider "proxmox" {
  mock_resource "proxmox_virtual_environment_vm" {
    defaults = {
      ipv4_addresses = [["127.0.0.1"], ["192.0.2.120"]]
      ipv6_addresses = [["::1"], ["2001:db8::120"]]
    }
  }
}

variables {
  vms = {
    example-vm = {
      name            = "example-vm"
      node_name       = "example-node"
      vm_id           = 120
      template_vm_id  = 9001
      vlan_id         = 20
      ssh_public_keys = ["ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA test-only"]
    }
  }
}

run "default_clone" {
  command = plan

  assert {
    condition = (
      proxmox_virtual_environment_vm.this["example-vm"].clone[0].vm_id == 9001 &&
      proxmox_virtual_environment_vm.this["example-vm"].clone[0].full &&
      proxmox_virtual_environment_vm.this["example-vm"].clone[0].datastore_id == "local-lvm" &&
      proxmox_virtual_environment_vm.this["example-vm"].vm_id == 120 &&
      proxmox_virtual_environment_vm.this["example-vm"].node_name == "example-node"
    )
    error_message = "Each map entry must fully clone its selected template on the requested node and datastore."
  }

  assert {
    condition = (
      proxmox_virtual_environment_vm.this["example-vm"].cpu[0].cores == 2 &&
      proxmox_virtual_environment_vm.this["example-vm"].cpu[0].type == "host" &&
      proxmox_virtual_environment_vm.this["example-vm"].memory[0].dedicated == 2048 &&
      proxmox_virtual_environment_vm.this["example-vm"].disk[0].size == 20 &&
      proxmox_virtual_environment_vm.this["example-vm"].disk[0].interface == "scsi0" &&
      proxmox_virtual_environment_vm.this["example-vm"].agent[0].enabled &&
      proxmox_virtual_environment_vm.this["example-vm"].started &&
      proxmox_virtual_environment_vm.this["example-vm"].on_boot
    )
    error_message = "Default resources, boot disk, guest agent and startup settings must be applied."
  }

  assert {
    condition = (
      proxmox_virtual_environment_vm.this["example-vm"].network_device[0].bridge == "vmbr0" &&
      proxmox_virtual_environment_vm.this["example-vm"].network_device[0].vlan_id == 20 &&
      proxmox_virtual_environment_vm.this["example-vm"].network_device[0].model == "virtio" &&
      proxmox_virtual_environment_vm.this["example-vm"].initialization[0].interface == "ide2" &&
      proxmox_virtual_environment_vm.this["example-vm"].initialization[0].ip_config[0].ipv4[0].address == "dhcp" &&
      proxmox_virtual_environment_vm.this["example-vm"].initialization[0].ip_config[0].ipv6[0].address == "auto" &&
      proxmox_virtual_environment_vm.this["example-vm"].initialization[0].user_account[0].username == "ubuntu" &&
      proxmox_virtual_environment_vm.this["example-vm"].initialization[0].user_account[0].keys == var.vms["example-vm"].ssh_public_keys
    )
    error_message = "The VM must wire VLAN networking, DHCP/SLAAC and its cloud-init public keys."
  }
}

run "custom_configuration" {
  command = plan

  variables {
    vms = {
      example-vm = merge(var.vms["example-vm"], {
        cpu_cores    = 4
        cpu_type     = "x86-64-v2-AES"
        memory_mb    = 4096
        disk_size_gb = 40
        datastore_id = "example-storage"
        bridge       = "vmbr1"
        vlan_id      = 30
        username     = "debian"
        ipv4_address = "192.0.2.120/24"
        ipv4_gateway = "192.0.2.1"
        started      = false
        on_boot      = false
      })
    }
  }

  assert {
    condition = (
      proxmox_virtual_environment_vm.this["example-vm"].cpu[0].cores == 4 &&
      proxmox_virtual_environment_vm.this["example-vm"].cpu[0].type == "x86-64-v2-AES" &&
      proxmox_virtual_environment_vm.this["example-vm"].memory[0].dedicated == 4096 &&
      proxmox_virtual_environment_vm.this["example-vm"].disk[0].size == 40 &&
      proxmox_virtual_environment_vm.this["example-vm"].disk[0].datastore_id == "example-storage" &&
      proxmox_virtual_environment_vm.this["example-vm"].clone[0].datastore_id == "example-storage" &&
      proxmox_virtual_environment_vm.this["example-vm"].initialization[0].datastore_id == "example-storage" &&
      proxmox_virtual_environment_vm.this["example-vm"].network_device[0].bridge == "vmbr1" &&
      proxmox_virtual_environment_vm.this["example-vm"].network_device[0].vlan_id == 30 &&
      proxmox_virtual_environment_vm.this["example-vm"].initialization[0].user_account[0].username == "debian" &&
      proxmox_virtual_environment_vm.this["example-vm"].initialization[0].ip_config[0].ipv4[0].address == "192.0.2.120/24" &&
      proxmox_virtual_environment_vm.this["example-vm"].initialization[0].ip_config[0].ipv4[0].gateway == "192.0.2.1" &&
      !proxmox_virtual_environment_vm.this["example-vm"].started &&
      !proxmox_virtual_environment_vm.this["example-vm"].on_boot
    )
    error_message = "Custom resources, storage, network, user and startup settings must reach the VM."
  }
}

run "multiple_vms" {
  command = plan

  variables {
    vms = {
      web = merge(var.vms["example-vm"], {
        name  = "example-web"
        vm_id = 121
      })
      worker = merge(var.vms["example-vm"], {
        name    = "example-worker"
        vm_id   = 122
        vlan_id = 30
      })
    }
  }

  assert {
    condition = (
      length(proxmox_virtual_environment_vm.this) == 2 &&
      proxmox_virtual_environment_vm.this["web"].vm_id == 121 &&
      proxmox_virtual_environment_vm.this["web"].name == "example-web" &&
      proxmox_virtual_environment_vm.this["worker"].vm_id == 122 &&
      proxmox_virtual_environment_vm.this["worker"].name == "example-worker" &&
      proxmox_virtual_environment_vm.this["worker"].network_device[0].vlan_id == 30 &&
      output.vm_id == { web = 121, worker = 122 }
    )
    error_message = "Every VM map entry must create an independent VM and appear under the same output key."
  }
}

run "outputs" {
  command = apply

  assert {
    condition = (
      output.vm_id == { example-vm = 120 } &&
      output.name == { example-vm = "example-vm" } &&
      output.node_name == { example-vm = "example-node" } &&
      output.ipv4_addresses["example-vm"] == tolist([tolist(["127.0.0.1"]), tolist(["192.0.2.120"])]) &&
      output.ipv6_addresses["example-vm"] == tolist([tolist(["::1"]), tolist(["2001:db8::120"])])
    )
    error_message = "Outputs must preserve VM identity and nested guest-agent addresses keyed by VM."
  }
}

run "reject_empty_vms" {
  command = plan

  variables {
    vms = {}
  }

  expect_failures = [var.vms]
}

run "reject_native_vlan" {
  command = plan

  variables {
    vms = {
      example-vm = merge(var.vms["example-vm"], { vlan_id = 1 })
    }
  }

  expect_failures = [var.vms]
}

run "reject_out_of_range_vlan" {
  command = plan

  variables {
    vms = {
      example-vm = merge(var.vms["example-vm"], { vlan_id = 4095 })
    }
  }

  expect_failures = [var.vms]
}

run "reject_invalid_resources" {
  command = plan

  variables {
    vms = {
      example-vm = merge(var.vms["example-vm"], {
        cpu_cores    = 1.5
        memory_mb    = 0
        disk_size_gb = 0
      })
    }
  }

  expect_failures = [var.vms]
}

run "reject_empty_keys" {
  command = plan

  variables {
    vms = {
      example-vm = merge(var.vms["example-vm"], { ssh_public_keys = [] })
    }
  }

  expect_failures = [var.vms]
}

run "reject_private_key" {
  command = plan

  variables {
    vms = {
      example-vm = merge(var.vms["example-vm"], {
        ssh_public_keys = ["-----BEGIN OPENSSH PRIVATE KEY-----"]
      })
    }
  }

  expect_failures = [var.vms]
}

run "reject_root_login" {
  command = plan

  variables {
    vms = {
      example-vm = merge(var.vms["example-vm"], { username = "root" })
    }
  }

  expect_failures = [var.vms]
}

run "reject_invalid_hostname" {
  command = plan

  variables {
    vms = {
      example-vm = merge(var.vms["example-vm"], { name = "-invalid-name" })
    }
  }

  expect_failures = [var.vms]
}

run "reject_invalid_vm_ids" {
  command = plan

  variables {
    vms = {
      example-vm = merge(var.vms["example-vm"], {
        vm_id          = 99
        template_vm_id = 9001.5
      })
    }
  }

  expect_failures = [var.vms]
}

run "reject_duplicate_vm_ids" {
  command = plan

  variables {
    vms = {
      web = merge(var.vms["example-vm"], {
        name = "example-web"
      })
      worker = merge(var.vms["example-vm"], {
        name = "example-worker"
      })
    }
  }

  expect_failures = [var.vms]
}

run "reject_invalid_ipv4" {
  command = plan

  variables {
    vms = {
      example-vm = merge(var.vms["example-vm"], {
        ipv4_address = "2001:db8::120/64"
        ipv4_gateway = "invalid"
      })
    }
  }

  expect_failures = [var.vms]
}

run "reject_dhcp_gateway" {
  command = plan

  variables {
    vms = {
      example-vm = merge(var.vms["example-vm"], { ipv4_gateway = "192.0.2.1" })
    }
  }

  expect_failures = [var.vms]
}

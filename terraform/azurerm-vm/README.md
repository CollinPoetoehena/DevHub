# azurerm-vm

Terraform module that creates one or more [Azure Linux Virtual Machines](https://azure.microsoft.com/en-us/products/virtual-machines/) from a single `vms` map, along with all required networking resources (NICs, optional public IPs, NSG associations).

## Requirements

| Name | Version |
|------|---------|
| Terraform | `>= 1.0` |
| [hashicorp/azurerm](https://registry.terraform.io/providers/hashicorp/azurerm/latest) | `>= 3.0` |

The `azurerm` provider must be configured by the root module before calling this module.

## Resources Created

| Resource | Description |
|----------|-------------|
| `azurerm_linux_virtual_machine` | One Linux VM per entry in `var.vms` |
| `azurerm_network_interface` | One NIC per VM |
| `azurerm_public_ip` | One public IP per VM where `assign_public_ip = true` |

> **NSG design note:** This module does not attach an NSG to NICs. NSGs should be applied at the subnet level (e.g. via the `azurerm-network` module), which covers all resources in the subnet consistently and is the recommended Azure approach. If a specific VM needs its own NSG rules as an exception, an `azurerm_network_interface_security_group_association` can be added in the calling root module. However, this is not recommended, the NSGs should be applied at the subnet level for simplicity and consistency (VMs are ephemeral and can be recreated, subnets are persistent, so per-VM NSGs add unnecessary complexity).

## Usage

```hcl
module "vms" {
  source = "git::https://github.com/CollinPoetoehena/dev-hub.git//terraform/azurerm-vm?ref=main"

  resource_group_name = "my-rg"
  location            = "westeurope"

  vms = {
    "jump-host" = {
      size             = "Standard_B1s"
      subnet_id        = "/subscriptions/.../subnets/public-subnet"
      assign_public_ip = true
      admin_username   = "azureuser"
      ssh_public_key   = file("~/.ssh/id_rsa.pub")
      image = {
        publisher = "Canonical"
        offer     = "0001-com-ubuntu-server-jammy"
        sku       = "22_04-lts-gen2"
        version   = "latest"
      }
      os_disk = {
        disk_size_gb = 30
      }
    }
    "app-server" = {
      size             = "Standard_D2s_v5"
      subnet_id        = "/subscriptions/.../subnets/private-subnet"
      assign_public_ip = false
      admin_username   = "azureuser"
      ssh_public_key   = file("~/.ssh/id_rsa.pub")
      image = {
        publisher = "Canonical"
        offer     = "0001-com-ubuntu-server-jammy"
        sku       = "22_04-lts-gen2"
        version   = "latest"
      }
      os_disk = {
        disk_size_gb         = 64
        storage_account_type = "Premium_LRS"
      }
    }
  }

  tags = {
    environment = "dev"
    project     = "my-project"
  }
}
```

## Inputs

| Name | Description | Type | Required |
|------|-------------|------|----------|
| `vms` | Map of VM definitions. Key becomes the VM name. | `map(object)` | yes |
| `vms[*].size` | Azure VM size (e.g. `Standard_D2s_v5`) | `string` | yes |
| `vms[*].subnet_id` | Resource ID of the subnet to place the NIC in | `string` | yes |
| `vms[*].assign_public_ip` | Whether to create and attach a public IP | `bool` | yes |
| `vms[*].admin_username` | Admin username for the VM | `string` | yes |
| `vms[*].ssh_public_key` | SSH public key for VM authentication | `string` | yes |
| `vms[*].image.publisher` | Image publisher (e.g. `Canonical`) | `string` | yes |
| `vms[*].image.offer` | Image offer | `string` | yes |
| `vms[*].image.sku` | Image SKU | `string` | yes |
| `vms[*].image.version` | Image version (e.g. `latest`) | `string` | yes |
| `vms[*].os_disk.disk_size_gb` | OS disk size in GB | `number` | yes |
| `vms[*].os_disk.caching` | OS disk caching mode | `string` | no (default: `ReadWrite`) |
| `vms[*].os_disk.storage_account_type` | OS disk storage type | `string` | no (default: `StandardSSD_LRS`) |
| `location` | Azure region | `string` | yes |
| `resource_group_name` | Resource group name | `string` | yes |
| `tags` | Tags to apply to all resources | `map(string)` | no |

## Outputs

| Name | Description |
|------|-------------|
| `vm_ids` | Map of VM name → VM resource ID |
| `private_ip_addresses` | Map of VM name → private IP address |
| `public_ip_addresses` | Map of VM name → public IP address (only for VMs with `assign_public_ip = true`) |
| `nic_ids` | Map of VM name → NIC ID |
| `ssh_commands` | Map of VM name → ready-to-use SSH command (only for VMs with a public IP) |

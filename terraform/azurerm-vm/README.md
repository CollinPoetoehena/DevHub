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
| `azurerm_network_interface` | One NIC per entry in `vms[*].nics`, named `<vm-name>-<nic-name>` |
| `azurerm_public_ip` | One public IP per NIC where `assign_public_ip = true` |

> **NSG design note:** This module does not attach an NSG to NICs. NSGs should be applied at the subnet level (e.g. via the `azurerm-network` module), which covers all resources in the subnet consistently and is the recommended Azure approach. If a specific VM needs its own NSG rules as an exception, an `azurerm_network_interface_security_group_association` can be added in the calling root module. However, this is not recommended, the NSGs should be applied at the subnet level for simplicity and consistency (VMs are ephemeral and can be recreated, subnets are persistent, so per-VM NSGs add unnecessary complexity).

## Design

Everything needed to define a VM — size, credentials, NICs, image, and OS disk — lives inside the `vms` map so each VM is fully self-contained. The only variables outside `vms` are `location`, `resource_group_name`, and `tags`: these are pure infrastructure context that applies to every resource the module creates, not to any single VM. This way the module is easy to use and understand, and adding a new VM is as simple as adding a new entry to the `vms` map.

The alternative is to add more variables outside the `vms` map for each aspect of the VM definition (e.g. a separate variable for NIC definitions, another for image definitions, etc.) and then require the user to correlate these with the correct VM via some key or index. This adds unnecessary complexity and indirection without any real benefit, since all the information needed to define a VM is already available at the time of defining the VM in the `vms` map.

Therefore, the `vms` map is the single source of truth for VM definitions, and all related information (including NICs) is nested within it for clarity and ease of use. This does have the drawback of having to add some additional computations/formatting in `locals.tf` to produce the final flattened maps needed for resource creation and outputs, but this is a small price to pay for the improved usability and maintainability of the module interface.

## Usage

```hcl
module "vms" {
  source = "git::https://github.com/CollinPoetoehena/dev-hub.git//terraform/azurerm-vm?ref=main"

  resource_group_name = "my-rg"
  location            = "westeurope"

  vms = {
    "jump-host" = {
      size           = "Standard_B1s"
      admin_username = "azureuser"
      ssh_public_key = file("~/.ssh/id_rsa.pub")

      nics = [
        # mgmt-nic: management NIC with a public IP for external SSH access
        {
          name             = "mgmt-nic"
          subnet_id        = "/subscriptions/.../subnets/public-subnet"
          assign_public_ip = true
        },
        # internal-nic: internal NIC for communication with private resources
        {
          name      = "internal-nic"
          subnet_id = "/subscriptions/.../subnets/private-subnet"
        },
      ]

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

    # app-server: private VM reachable only via the jump host
    "app-server" = {
      size           = "Standard_D2s_v5"
      admin_username = "azureuser"
      ssh_public_key = file("~/.ssh/id_rsa.pub")

      nics = [
        # internal-nic: no public IP — SSH via: ssh -J azureuser@<jump-host-public-ip> azureuser@<app-server-private-ip>
        {
          name      = "internal-nic"
          subnet_id = "/subscriptions/.../subnets/private-subnet"
        },
      ]

      image = {
        publisher = "Canonical"
        offer     = "0001-com-ubuntu-server-jammy"
        sku       = "22_04-lts-gen2"
        version   = "latest"
      }
      os_disk = {
        disk_size_gb = 64
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
| `vms[*].admin_username` | Admin username for the VM | `string` | yes |
| `vms[*].ssh_public_key` | SSH public key for VM authentication | `string` | yes |
| `vms[*].nics` | List of NICs to attach. Each NIC name produces a resource named `<vm-name>-<nic-name>` | `list(object)` | yes |
| `vms[*].nics[*].name` | NIC name — final resource name: `<vm-name>-<nic-name>` | `string` | yes |
| `vms[*].nics[*].subnet_id` | Resource ID of the subnet to place this NIC in | `string` | yes |
| `vms[*].nics[*].assign_public_ip` | Whether to create and attach a public IP to this NIC | `bool` | no (default: `false`) |
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
| `vm_names` | Map of VM name → VM name as created in Azure |
| `private_ip_addresses` | Map of NIC key (`<vm-name>-<nic-name>`) → private IP address |
| `public_ip_addresses` | Map of NIC key (`<vm-name>-<nic-name>`) → public IP address (only NICs with `assign_public_ip = true`) |
| `nic_ids` | Map of NIC key (`<vm-name>-<nic-name>`) → NIC resource ID |
| `nic_names` | Map of NIC key (`<vm-name>-<nic-name>`) → NIC name as created in Azure |
| `ssh_commands` | Map of NIC key (`<vm-name>-<nic-name>`) → ready-to-use SSH command (only NICs with a public IP) |
| `local_formatted_nics` | The `local.nics` map, included as an output for debugging/visibility purposes |

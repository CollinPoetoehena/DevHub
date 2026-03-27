# terraform-azurerm-base

> Part of [dev-hub/Terraform](https://github.com/CollinPoetoehena/dev-hub/blob/main/Terraform.md) — see that file for conventions, structure guidelines, and the full module index.

Terraform module that creates a base Azure infrastructure stack in a single call — networking and Linux VMs. Each resource group is fully optional; supply only the variables you need and the rest are skipped.

## Requirements

| Name | Version |
|------|---------|
| Terraform | `>= 1.0` |
| [hashicorp/azurerm](https://registry.terraform.io/providers/hashicorp/azurerm/latest) | `>= 3.0` |

The `azurerm` provider must be configured by the root module before calling this module.

## Design

- **Flat module — no submodules.** All resources live in a single `main.tf` with comment blocks separating each logical section. Keeping everything in one module avoids the Terraform limitation where every module boundary requires its own full `variables.tf` and `outputs.tf` (Terraform has no mechanism to re-export variables or outputs), meaning all shared variables (`location`, `resource_group_name`, `tags`) would have to be declared multiple times for no real benefit. Therefore, for a small, cohesive set of resources like this base stack, a flat module with clear comment sections gives the same logical separation at zero extra cost while maximizing simplicity and maintainability.

- **`vms` map is the single source of truth for VM definitions.** Everything needed to define a VM — size, credentials, NICs, image, and OS disk — lives inside the `vms` map so each VM is fully self-contained. The only variables outside `vms` are `location`, `resource_group_name`, and `tags`: these are pure infrastructure context that applies to every resource the module creates, not to any single VM. This way the module is easy to use and understand, and adding a new VM is as simple as adding a new entry to the `vms` map. The alternative is to add more variables outside the `vms` map for each aspect of the VM definition (e.g. a separate variable for NIC definitions, another for image definitions, etc.) and then require the user to correlate these with the correct VM via some key or index. This adds unnecessary complexity and indirection without any real benefit, since all the information needed to define a VM is already available at the time of defining the VM in the `vms` map. This does have the drawback of having to add some additional computations in `locals.tf` to produce the final flattened maps needed for resource creation and outputs, but this is a small price to pay for the improved usability and maintainability of the module interface.

- **NSGs are applied at the subnet level, not per NIC.** This covers all resources in the subnet consistently and is the recommended Azure approach. If a specific VM needs its own NSG rules as an exception, an `azurerm_network_interface_security_group_association` can be added in the calling root module. However, this is not recommended — NSGs should stay at the subnet level for simplicity and consistency (VMs are ephemeral and can be recreated, subnets are persistent, so per-VM NSGs add unnecessary complexity).

```
terraform-azurerm-base/
├── main.tf       # All resources: network and VMs (comment-separated sections)
├── variables.tf  # All input variables (comment-separated sections)
├── outputs.tf    # All outputs (comment-separated sections)
├── locals.tf     # Derived locals (NIC flattening for VM for_each)
└── README.md
```

Each resource group is opt-in via its variable defaults:
- **Networking**: leave `vnets`, `subnets`, etc. as `{}` to skip.
- **VMs**: leave `vms` as `{}` to skip.

## Resources Created

| Resource | Description |
|----------|-------------|
| `azurerm_virtual_network` | One VNet per entry in `var.vnets` |
| `azurerm_virtual_network_peering` | One peering per entry in `var.peerings` |
| `azurerm_network_security_group` | One NSG per entry in `var.nsgs` |
| `azurerm_subnet` | One subnet per entry in `var.subnets` |
| `azurerm_subnet_network_security_group_association` | Associates NSGs to subnets via `var.nsg_associations` |
| `azurerm_public_ip` | One public IP per NIC where `assign_public_ip = true` |
| `azurerm_network_interface` | One NIC per entry in `vms[*].nics`, named `<vm-name>-<nic-name>` |
| `azurerm_linux_virtual_machine` | One Linux VM per entry in `var.vms` |

## Usage

```hcl
module "base" {
  source = "git::https://github.com/CollinPoetoehena/dev-hub.git//terraform/azurerm-base?ref=main"

  resource_group_name = "my-rg"
  location            = "westeurope"
  tags = {
    environment = "dev"
    project     = "my-project"
  }

  # ---------------------------------------------------------------------------
  # Networking
  # ---------------------------------------------------------------------------

  # Hub-and-spoke: hub VNet for shared services, spoke VNet for workloads
  vnets = {
    "hub-vnet"   = { address_space = "10.0.0.0/16" }
    "spoke-vnet" = { address_space = "10.1.0.0/16" }
  }

  # Peering is unidirectional in Azure — declare both directions for full connectivity.
  # Use remote_vnet_key to reference a VNet created by this module (ID resolved internally).
  # Use remote_vnet_id for VNets outside this module (e.g. in another resource group).
  peerings = {
    "hub-to-spoke" = {
      vnet_key                = "hub-vnet"
      remote_vnet_key         = "spoke-vnet"
      allow_forwarded_traffic = true
    }
    "spoke-to-hub" = {
      vnet_key                = "spoke-vnet"
      remote_vnet_key         = "hub-vnet"
      allow_forwarded_traffic = true
    }
  }

  nsgs = {
    # Hub NSG: allows SSH from anywhere into the jump host subnet
    "hub-nsg" = {
      security_rules = [
        {
          name                       = "allow-ssh"
          priority                   = 100
          direction                  = "Inbound"
          access                     = "Allow"
          protocol                   = "Tcp"
          source_port_range          = "*"
          destination_port_range     = "22"
          source_address_prefix      = "*"
          destination_address_prefix = "*"
        }
      ]
    }
    # Spoke NSG: allows internal traffic from the hub address space only
    "spoke-nsg" = {
      security_rules = [
        {
          name                       = "allow-from-hub"
          priority                   = 100
          direction                  = "Inbound"
          access                     = "Allow"
          protocol                   = "*"
          source_port_range          = "*"
          destination_port_range     = "*"
          source_address_prefix      = "10.0.0.0/16"
          destination_address_prefix = "*"
        }
      ]
    }
  }

  subnets = {
    "hub-subnet"   = { vnet_key = "hub-vnet",   address_prefix = "10.0.1.0/24" }
    "spoke-subnet" = { vnet_key = "spoke-vnet", address_prefix = "10.1.1.0/24" }
  }

  nsg_associations = {
    hub-subnet   = "hub-nsg"
    spoke-subnet = "spoke-nsg"
  }

  # ---------------------------------------------------------------------------
  # Virtual Machines
  # ---------------------------------------------------------------------------

  vms = {
    "jump-host" = {
      size           = "Standard_B1s"
      admin_username = "azureuser"
      ssh_public_key = file("~/.ssh/id_rsa.pub")

      nics = [
        # mgmt-nic: management NIC with a public IP for external SSH access
        {
          name             = "mgmt-nic"
          subnet_id        = "/subscriptions/.../subnets/hub-subnet"
          assign_public_ip = true
        },
        # internal-nic: internal NIC for communication with private resources
        {
          name      = "internal-nic"
          subnet_id = "/subscriptions/.../subnets/spoke-subnet"
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
        # internal-nic: no public IP — SSH via jump host
        {
          name      = "internal-nic"
          subnet_id = "/subscriptions/.../subnets/spoke-subnet"
        },
      ]

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
}
```

## Inputs

### Shared

| Name | Description | Type | Required |
|------|-------------|------|----------|
| `resource_group_name` | Resource group name | `string` | yes |
| `location` | Azure region | `string` | yes |
| `tags` | Tags to apply to all resources | `map(string)` | no |

### Networking

| Name | Description | Type | Required |
|------|-------------|------|----------|
| `vnets` | Map of VNets to create. Key is the VNet name. | `map(object)` | no |
| `vnets[*].address_space` | CIDR address space for the VNet (e.g. `10.0.0.0/16`) | `string` | yes |
| `peerings` | Flat map of VNet peering connections. Azure peering is unidirectional; declare both sides for full mesh. | `map(object)` | no |
| `peerings[*].vnet_key` | Key from `var.vnets` — the local VNet that initiates the peering | `string` | yes |
| `peerings[*].remote_vnet_key` | Key from `var.vnets` — the remote VNet to peer with; resource ID resolved internally | `string` | yes |
| `peerings[*].allow_forwarded_traffic` | Allow traffic forwarded from the remote VNet | `bool` | no (default: `false`) |
| `peerings[*].allow_gateway_transit` | Allow the remote VNet to use this VNet's gateway | `bool` | no (default: `false`) |
| `peerings[*].use_remote_gateways` | Use the remote VNet's gateway for routing | `bool` | no (default: `false`) |
| `nsgs` | Map of NSGs to create. Key is the NSG name. | `map(object)` | no |
| `nsgs[*].security_rules` | List of security rules for the NSG | `list(object)` | no |
| `subnets` | Map of subnets to create. Key is the subnet name. | `map(object)` | no |
| `subnets[*].vnet_key` | Key from `var.vnets` — the VNet this subnet belongs to | `string` | yes |
| `subnets[*].address_prefix` | CIDR prefix for the subnet (e.g. `10.0.1.0/24`) | `string` | yes |
| `nsg_associations` | Map of subnet key → NSG key (from `var.nsgs`) to associate | `map(string)` | no |

### Virtual Machines

| Name | Description | Type | Required |
|------|-------------|------|----------|
| `vms` | Map of VM definitions. Key becomes the VM name. Leave empty (`{}`) to skip creation. | `map(object)` | no |
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

## Outputs

### Networking

| Name | Description |
|------|-------------|
| `vnet_ids` | Map of VNet key → VNet resource ID |
| `vnet_names` | Map of VNet key → VNet name as created in Azure |
| `peering_ids` | Map of peering key → peering resource ID |
| `nsg_ids` | Map of NSG key → NSG resource ID |
| `subnet_ids` | Map of subnet key → subnet resource ID |
| `subnet_names` | Map of subnet key → subnet name as created in Azure |

### Virtual Machines

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

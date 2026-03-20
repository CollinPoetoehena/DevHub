# azurerm-network

Terraform module that creates a complete Azure network stack — Virtual Networks, Network Security Groups, and Subnets — in a single call.

## Requirements

| Name | Version |
|------|---------|
| Terraform | `>= 1.0` |
| [hashicorp/azurerm](https://registry.terraform.io/providers/hashicorp/azurerm/latest) | `>= 3.0` |

The `azurerm` provider must be configured by the root module before calling this module.

## Design

This module is intentionally kept **flat** — no submodules. All resources (VNets, NSGs, Subnets) live in a single `main.tf`, with comment blocks separating each logical section.

```
azurerm-network/
├── main.tf       # All resources: VNets, NSGs, Subnets (comment-separated)
├── variables.tf  # All input variables (comment-separated)
├── outputs.tf    # All outputs (comment-separated)
└── README.md
```

**Why flat instead of submodules?**
Terraform has no mechanism to re-export variables or outputs — every module boundary requires its own full `variables.tf` and `outputs.tf`. Splitting this into submodules would mean declaring every variable and output at least twice with no real benefit. For a small, cohesive group of resources like networking, a flat module with clear comment sections gives the same logical separation at zero extra cost.

## Resources Created

| Resource | Description |
|----------|-------------|
| `azurerm_virtual_network` | One VNet per entry in `var.vnets` |
| `azurerm_virtual_network_peering` | One peering per entry in `var.peerings` |
| `azurerm_network_security_group` | One NSG per entry in `var.nsgs` |
| `azurerm_subnet` | One subnet per entry in `var.subnets` |
| `azurerm_subnet_network_security_group_association` | Associates NSGs to subnets via `var.nsg_associations` |

## Usage

```hcl
module "network" {
  source = "git::https://github.com/CollinPoetoehena/dev-hub.git//terraform/azurerm-network?ref=main"

  resource_group_name = "my-rg"
  location            = "westeurope"

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
}
```

## Inputs

| Name | Description | Type | Required |
|------|-------------|------|----------|
| `resource_group_name` | Resource group name | `string` | yes |
| `location` | Azure region | `string` | yes |
| `vnets` | Map of VNets to create. Key is the VNet name. | `map(object)` | yes |
| `vnets[*].address_space` | CIDR address space for the VNet (e.g. `10.0.0.0/16`) | `string` | yes |
| `peerings` | Flat map of VNet peering connections. Azure peering is unidirectional; declare both sides for full mesh. | `map(object)` | no |
| `peerings[*].vnet_key` | Key from `var.vnets` — the local VNet that initiates the peering | `string` | yes |
| `peerings[*].remote_vnet_key` | Key from `var.vnets` — the remote VNet to peer with; resource ID resolved internally | `string` | yes |
| `peerings[*].allow_forwarded_traffic` | Allow traffic forwarded from the remote VNet (not originated there) | `bool` | no (default: `false`) |
| `peerings[*].allow_gateway_transit` | Allow the remote VNet to use this VNet's gateway | `bool` | no (default: `false`) |
| `peerings[*].use_remote_gateways` | Use the remote VNet's gateway for routing (requires `allow_gateway_transit` on the remote side) | `bool` | no (default: `false`) |
| `nsgs` | Map of NSGs to create. Key is the NSG name. | `map(object)` | no |
| `nsgs[*].security_rules` | List of security rules for the NSG | `list(object)` | no |
| `subnets` | Map of subnets to create. Key is the subnet name. | `map(object)` | yes |
| `subnets[*].vnet_key` | Key from `var.vnets` — the VNet this subnet belongs to | `string` | yes |
| `subnets[*].address_prefix` | CIDR prefix for the subnet (e.g. `10.0.1.0/24`) | `string` | yes |
| `nsg_associations` | Map of subnet key → NSG key (from `var.nsgs`) to associate | `map(string)` | no |

## Outputs

| Name | Description |
|------|-------------|
| `vnet_ids` | Map of VNet key → VNet resource ID |
| `vnet_names` | Map of VNet key → VNet name as created in Azure |
| `peering_ids` | Map of peering key → peering resource ID |
| `nsg_ids` | Map of NSG key → NSG resource ID |
| `subnet_ids` | Map of subnet key → subnet resource ID |
| `subnet_names` | Map of subnet key → subnet name as created in Azure |

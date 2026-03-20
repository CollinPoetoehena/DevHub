# azurerm-keyvault

Terraform module that creates an [Azure Key Vault](https://azure.microsoft.com/en-us/products/key-vault) with configurable access policies for managing keys, secrets, and certificates.

## Requirements

| Name | Version |
|------|---------|
| Terraform | `>= 1.0` |
| [hashicorp/azurerm](https://registry.terraform.io/providers/hashicorp/azurerm/latest) | `>= 3.0` |

The `azurerm` provider must be configured by the root module before calling this module.

## Resources Created

| Resource | Description |
|----------|-------------|
| `azurerm_key_vault` | Azure Key Vault with soft-delete and optional access policy |

## Usage

```hcl
module "keyvault" {
  source = "git::https://github.com/CollinPoetoehena/dev-hub.git//terraform/azurerm-keyvault?ref=main"

  key_vault_name      = "my-keyvault"
  location            = "westeurope"
  resource_group_name = "my-rg"
  tenant_id           = "00000000-0000-0000-0000-000000000000"

  # Optional: grant a user/service principal access to the vault
  user_object_id = "00000000-0000-0000-0000-000000000000"
}
```

## Inputs

| Name | Description | Type | Required |
|------|-------------|------|----------|
| `key_vault_name` | Name of the Key Vault | `string` | yes |
| `location` | Azure region | `string` | yes |
| `resource_group_name` | Resource group name | `string` | yes |
| `tenant_id` | Azure tenant ID | `string` | yes |
| `user_object_id` | Object ID of the user/principal to grant access. Leave empty (`""`) to skip creating an access policy. | `string` | no |

## Outputs

| Name | Description |
|------|-------------|
| `key_vault_id` | Resource ID of the Key Vault |
| `key_vault_name` | Name of the Key Vault |

## Notes

- Soft-delete is mandatory in Azure and is set to the minimum retention period of 7 days.
- Purge protection is disabled to allow immediate cleanup during development.
- The optional access policy grants the specified principal Get/List/Create/Update on keys, Get/List/Set/Delete on secrets, and Get/List on certificates.

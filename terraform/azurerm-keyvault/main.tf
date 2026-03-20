# =============================================================================
# Key Vault Module - Azure Key Vault with Access Policies
# =============================================================================
# This module creates an Azure Key Vault with configurable access policies
# to control access to keys, secrets, and certificates.
#
# Azure Key Vault is used to securely store and manage sensitive information
# =============================================================================

// https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault
resource "azurerm_key_vault" "main" {
  name                            = var.key_vault_name
  location                        = var.location
  resource_group_name             = var.resource_group_name
  tenant_id                       = var.tenant_id
  sku_name                        = "standard"
  enabled_for_deployment          = true
  enabled_for_template_deployment = true
  enabled_for_disk_encryption     = false
  
  # Soft delete is mandatory in Azure (cannot be fully disabled)
  # Set minimum retention period and disable purge protection for easier cleanup
  soft_delete_retention_days      = 7      # Minimum allowed (7-90 days)
  purge_protection_enabled        = false  # Allows immediate purge if you have permissions
  
  # Conditionally create access policy for user access
  # If user_object_id is empty, no access policy is created
  dynamic "access_policy" {
    # Creates 1 policy if user_object_id provided, 0 if empty
    for_each = var.user_object_id != "" ? [1] : []
    content {
      tenant_id = var.tenant_id
      object_id = var.user_object_id

      # Allow user to manage keys (create, read, update)
      key_permissions = [
        "Get",
        "List",
        "Create",
        "Update",
      ]

      # Allow user to manage secrets (CRUD operations)
      secret_permissions = [
        "Get",
        "List",
        "Set",
        "Delete",
      ]

      # Allow user to read certificates
      certificate_permissions = [
        "Get",
        "List",
      ]
    }
  }
}

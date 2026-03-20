variable "key_vault_name" {
  description = "Key Vault name."
  type        = string
}

variable "location" {
  description = "Azure region where resources will be created."
  type        = string
}

variable "user_object_id" {
  description = "Object ID of the user/principal that needs access to Key Vault."
  type        = string
  default     = ""
}

variable "tenant_id" {
  description = "Azure tenant ID."
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group."
  type        = string
}

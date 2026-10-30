# Manage repository metadata and main-branch governance using GitHub App credentials.
terraform {
  required_version = ">= 1.9, < 2.0"

  required_providers {
    github = {
      source  = "integrations/github"
      version = "= 6.13.0"
    }
  }
}

provider "github" {
  owner = "CollinPoetoehena"

  app_auth {
    id              = var.github_app_id
    installation_id = var.github_app_installation_id
    pem_file        = var.github_app_pem
  }
}

variable "github_app_id" {
  description = "GitHub App ID, supplied through TF_VAR_github_app_id."
  type        = string
  nullable    = false
}

variable "github_app_installation_id" {
  description = "GitHub App installation ID, supplied through TF_VAR_github_app_installation_id."
  type        = string
  nullable    = false
}

variable "github_app_pem" {
  description = "Private key contents, supplied through TF_VAR_github_app_pem; never commit this value."
  type        = string
  sensitive   = true
  nullable    = false
}

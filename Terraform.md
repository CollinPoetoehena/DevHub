# Terraform

Reusable [Terraform](https://developer.hashicorp.com/terraform) modules, used as Infrastructure as Code (IaC).

Each module lives in its own dedicated repository. This file serves as the index and reference for all Terraform modules, and documents conventions shared across them.

## Dev-Hub

This repository ([dev-hub](https://github.com/CollinPoetoehena/dev-hub)) is the central reference for all Terraform modules, see [README.md](README.md) for the full design and index of all component types.

## Structure

Each module repository follows the [Terraform Module Structure](https://developer.hashicorp.com/terraform/language/modules/develop/structure):

```
<module-name>/
├── main.tf
├── variables.tf
├── outputs.tf
├── locals.tf (optional)
├── README.md
└── modules/
```

Where:
- `main.tf` contains the main Terraform configuration for the module.
- `variables.tf` defines the input variables for the module.
- `outputs.tf` defines the output values from the module.
- `locals.tf` is optional and can be used for any local values or computations needed by the module.
- `README.md` provides documentation specific to the module, including usage instructions, input/output descriptions, and any other relevant information.
- `modules/` is an optional directory for any nested modules that this module may use internally.

## Module Naming Convention

Each module follows the standard [Terraform Naming Convention](https://developer.hashicorp.com/terraform/registry/modules/publish): `terraform-<PROVIDER>-<NAME>`

Where:
- `<PROVIDER>` is the name of the cloud provider or service (e.g., `aws`, `azurerm`, etc.).
- `<NAME>` is a brief description of the module's functionality or the resource it manages (e.g., `vpc`, `vm`, `network`, etc.).

## Usage

Each module repository contains its own README with usage instructions. The general pattern for referencing a module:

```hcl
module "example" {
  source = "git::https://github.com/CollinPoetoehena/<module-repo>.git?ref=main"
}
```

## Modules

| Module | Repository | Description |
|--------|------------|-------------|
| azurerm-vm | *(link)* | Creates one or more Azure Linux VMs with NICs and optional public IPs |
| azurerm-keyvault | *(link)* | Creates an Azure Key Vault with an optional access policy for keys, secrets, and certificates |
| azurerm-network | *(link)* | Creates a full Azure network stack — VNets, NSGs, and Subnets — in a single call |

## README Template

When creating a new module repository, use the following template as the starting point for its `README.md`:

```markdown
# terraform-<PROVIDER>-<NAME>

> Part of [dev-hub/Terraform](https://github.com/CollinPoetoehena/dev-hub/blob/main/Terraform.md) — see that file for conventions, structure guidelines, and the full module index.

<Short description of what this module does.>

## Requirements

| Name | Version |
|------|---------|
| | |

## Design
<Any design notes or implementation details worth mentioning.>

## Resources Created

| Resource | Description |
|----------|-------------|
| | |

## Usage

```hcl
module "example" {
  source = "git::https://github.com/CollinPoetoehena/terraform-<PROVIDER>-<NAME>.git?ref=main"

  # required variables
}
```

## Inputs

| Name | Type | Default | Description |
|------|------|---------|-------------|
| | | | |

## Outputs

| Name | Description |
|------|-------------|
| | |
```

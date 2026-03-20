# Terraform

Reusable [Terraform](https://developer.hashicorp.com/terraform) modules, used as Infrastructure as Code (IaC).

## Structure

Each module lives in its own subdirectory under `terraform/` and follows the [Terraform Module Structure](https://developer.hashicorp.com/terraform/language/modules/develop/structure):

```
terraform/
└── <module-name>/
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
Each module follows the standard [Terraform Naming Convention](https://developer.hashicorp.com/terraform/registry/modules/publish), which is: `terraform-<PROVIDER>-<NAME>`

Where:
- `<PROVIDER>` is the name of the cloud provider or service (e.g., `aws`, `azurerm`, etc.).
- `<NAME>` is a brief description of the module's functionality or the resource it manages (e.g., `vpc`, `ec2`, `s3`, `eks`, etc.).

This is applied via the `terraform` folder, so the module directories are named `<provider>-<name>`, e.g. `azurerm-vm`, `azurerm-network`, etc. This naming convention makes it clear at a glance which provider and resource type each module is for, and is consistent with common Terraform module naming practices.

## Usage

Reference a module from this repository directly in your Terraform configuration:

```hcl
module "example" {
  source = "git::https://github.com/CollinPoetoehena/dev-hub.git//terraform/<module-name>?ref=main"
}
```

## Modules

| Module | Description |
|--------|-------------|
| [azurerm-vm](./azurerm-vm/README.md) | Creates one or more Azure Linux VMs with NICs and optional public IPs |
| [azurerm-keyvault](./azurerm-keyvault/README.md) | Creates an Azure Key Vault with an optional access policy for keys, secrets, and certificates |
| [azurerm-network](./azurerm-network/README.md) | Creates a full Azure network stack — VNets, NSGs, and Subnets — in a single call |
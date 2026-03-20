# Terraform

Reusable Terraform modules.

## Structure

Each module lives in its own subdirectory under `terraform/`:

```
terraform/
└── <module-name>/
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    └── README.md
```

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
| _(none yet)_ | |

TODO: add here short description later per module, and link to the module's README.md for more details.
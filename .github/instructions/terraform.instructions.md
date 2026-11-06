---
description: "Use when writing or reviewing Terraform configurations, modules, variables, or tests: mandatory rules and validation commands on top of the common instructions."
applyTo: "**/*.tf,**/*.tfvars,**/*.tftest.hcl,**/.terraform.lock.hcl"
---

# Terraform Instructions

These rules add Terraform specifics to the [common instructions](https://github.com/CollinPoetoehena/DevHub/tree/main/packages/apm/common) of `devhub-common` (coding, security, documentation, and Git), which always apply. Where they differ, these rules refine the common ones; the repository's own configuration and `AGENTS.md` take precedence over both.

## Skills

- Apply the `terraform` skill for security, modularity, maintainability, style, documentation, and testing conventions.

## Rules

- Constrain Terraform with `required_version`, pin every provider in `required_providers`, and commit `.terraform.lock.hcl`.
- Give every variable and output a `description` and `type`, and mark secret values `sensitive = true`.
- Never commit state, credentials, or secret `*.tfvars`; supply secrets through environment variables such as `TF_VAR_<name>` or a secret manager.
- Store shared state in a remote backend with locking.
- Create modules only for groups of related resources, and keep the module hierarchy shallow.
- Use `for_each` with stable keys instead of `count` for collections, and `moved` blocks when renaming resources.
- Review a `terraform plan` for every change; never run `apply` or `destroy` without explicit user authorization, and never to validate an edit.

## Validation

Run from the configuration or module directory; use the repository's configured commands when they differ:

```sh
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
tflint --recursive
terraform test
```

Run `terraform test` when the module has `.tftest.hcl` files, and `terraform plan` only with credentials the user approved.

## References

- [Terraform documentation](https://developer.hashicorp.com/terraform/docs)
- [Terraform style guide](https://developer.hashicorp.com/terraform/language/style)
- [Dependency lock file](https://developer.hashicorp.com/terraform/language/files/dependency-lock)
- [Terraform tests](https://developer.hashicorp.com/terraform/language/tests)
- [TFLint](https://github.com/terraform-linters/tflint)

---
description: "Use when writing or reviewing Terraform configurations, modules, variables, or tests: essential conventions and validation commands alongside the common guidelines."
applyTo: "**/*.tf,**/*.tfvars,**/*.tftest.hcl,**/.terraform.lock.hcl"
---

# Terraform Guidelines

Use general best practices for Terraform and follow the common guidelines in `devhub-guidelines-core`.

Specifically for Terraform, in addition to general best practices:

Repository configuration, owning documentation, and `AGENTS.md` may refine or override these shared defaults. When applicable sources conflict, follow higher-priority policy and surface unresolved conflicts rather than assuming universal host precedence.

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

Use the `terraform` skill for additional Terraform procedures and references.

## References

- [Terraform documentation](https://developer.hashicorp.com/terraform/docs)
- [Terraform style guide](https://developer.hashicorp.com/terraform/language/style)
- [Dependency lock file](https://developer.hashicorp.com/terraform/language/files/dependency-lock)
- [Terraform tests](https://developer.hashicorp.com/terraform/language/tests)
- [TFLint](https://github.com/terraform-linters/tflint)

Use relevant available skills for additional procedures and references.

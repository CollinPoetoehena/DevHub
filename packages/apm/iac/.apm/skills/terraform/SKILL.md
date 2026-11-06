---
name: terraform
description: 'Terraform conventions: security and secret handling, modularity, maintainability, variables and outputs, style and file layout, documentation with terraform-docs, and tests with .tftest.hcl. Use when writing, reviewing, refactoring, or testing Terraform configurations and modules.'
---

# Terraform

Index for Terraform work. The Terraform and common instructions take precedence over the reference.

## When to Use This Skill

- Writing or reviewing Terraform configurations or modules
- Designing variables, outputs, and module boundaries
- Refactoring resources without recreating them
- Writing Terraform tests or module documentation

## Steps

1. **Write or change configuration.** Open [references/patterns.md](references/patterns.md) for security, modularity, maintainability, style, and documentation.
2. **Write tests.** Follow the testing section in [references/patterns.md](references/patterns.md) with `.tftest.hcl` files.
3. **Validate.** Run the validation commands from the Terraform instructions and report each result.

## Gotchas

- **`count` indexes shift:** removing an item from a list used with `count` recreates every later resource; use `for_each` with stable keys.
- **Renames destroy resources:** renaming a resource address destroys and recreates it unless a `moved` block maps the old address.
- **`sensitive` does not protect state:** sensitive values are hidden in output but stored in plain text in the state; protect the state backend.
- **Module `depends_on` defers reads:** `depends_on` on a module defers its data sources to apply time and makes plans less precise.
- **Lock files pin providers:** `.terraform.lock.hcl` fixes provider versions and checksums; update it with `terraform init -upgrade`.

## References

- [Terraform documentation](https://developer.hashicorp.com/terraform/docs)
- [Refactoring with moved blocks](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring)

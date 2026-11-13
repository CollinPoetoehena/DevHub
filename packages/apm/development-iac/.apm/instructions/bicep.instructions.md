---
description: "Use when writing or reviewing Azure Bicep templates or parameter files: essential conventions and validation commands alongside the common guidelines."
applyTo: "**/*.bicep,**/*.bicepparam"
---

# Bicep Guidelines

Use general best practices for Bicep and follow the common guidelines in `devhub-guidelines-core`.

Specifically for Bicep, in addition to general best practices:

Repository configuration, owning documentation, and `AGENTS.md` may refine or override these shared defaults. When applicable sources conflict, follow higher-priority policy and surface unresolved conflicts rather than assuming universal host precedence.

## Rules

- Use lowerCamelCase symbolic names that describe the resource, and declare parameters at the top with `@description`.
- Mark secret parameters with `@secure()`, and never return secrets or keys in outputs.
- Reference resources through symbolic names and the `existing` keyword instead of `resourceId()` or explicit `dependsOn`.
- Use the latest stable API version of each resource type, and prefer Azure Verified Modules where they fit.
- Keep environment-specific values in `.bicepparam` files, with defaults that are safe and low-cost for test environments.
- Run `what-if` and deployments only against subscriptions and resource groups the user approved.

## Validation

Run from the template directory; use the repository's configured commands when they differ:

```sh
az bicep build --file main.bicep
az bicep lint --file main.bicep
```

Use the `bicep` skill for additional Bicep procedures and references.

## References

- [Bicep documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [Bicep best practices](https://learn.microsoft.com/azure/azure-resource-manager/bicep/best-practices)
- [Bicep linter](https://learn.microsoft.com/azure/azure-resource-manager/bicep/linter)
- [Azure Verified Modules](https://azure.github.io/Azure-Verified-Modules/)

Use relevant available skills for additional procedures and references.

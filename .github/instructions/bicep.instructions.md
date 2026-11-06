---
description: "Use when writing or reviewing Azure Bicep templates or parameter files: mandatory rules and validation commands on top of the common instructions."
applyTo: "**/*.bicep,**/*.bicepparam"
---

# Bicep Instructions

These rules add Bicep specifics to the [common instructions](https://github.com/CollinPoetoehena/DevHub/tree/main/packages/apm/common) of `devhub-common` (coding, security, documentation, and Git), which always apply. Where they differ, these rules refine the common ones; the repository's own configuration and `AGENTS.md` take precedence over both.

## Skills

- Apply the `bicep` skill for naming, structure, parameters, resource references, and security conventions.

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

## References

- [Bicep documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [Bicep best practices](https://learn.microsoft.com/azure/azure-resource-manager/bicep/best-practices)
- [Bicep linter](https://learn.microsoft.com/azure/azure-resource-manager/bicep/linter)
- [Azure Verified Modules](https://azure.github.io/Azure-Verified-Modules/)

---
name: bicep
description: 'Azure Bicep conventions: naming, parameter and variable declarations, resource references, unique resource names, child resources, outputs, and security. Use when writing, reviewing, or linting Bicep templates and parameter files for Azure deployments.'
---

# Bicep

Index for Bicep work. The Bicep and common instructions take precedence over the reference.

## When to Use This Skill

- Writing or reviewing Bicep templates or modules
- Designing parameters, variables, outputs, and resource names
- Referencing existing resources or child resources

## Steps

1. **Write or change templates.** Open [references/patterns.md](references/patterns.md) for naming, structure, parameters, variables, resource references, resource names, child resources, and security.
2. **Validate.** Run the validation commands from the Bicep instructions and report each result.

## Gotchas

- **Outputs are stored:** deployment outputs are visible in the deployment history; never output secrets.
- **Explicit `dependsOn` is rarely needed:** referencing a symbolic name, such as `storageAccount.id`, creates the dependency.
- **Name rules differ per resource:** length, character, and uniqueness limits vary; for example, storage account names allow only lowercase letters and digits.
- **`uniqueString()` is deterministic:** it returns the same value for the same inputs, so include the scope, such as `resourceGroup().id`.

## References

- [Bicep documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [Resource naming rules](https://learn.microsoft.com/azure/azure-resource-manager/management/resource-name-rules)

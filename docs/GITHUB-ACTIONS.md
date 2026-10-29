# Reusable GitHub Actions Workflows

> **TODO:** Reusable workflows are not developed yet. Implement and validate them before use; the guidance below describes the intended approach.

Return to the [shared GitHub customizations overview](GITHUB.md) for other topics.

The [`.github/workflows/`](../.github/workflows/) directory holds GitHub Actions workflows that provide common automation for multiple repositories. A project can call a reusable workflow instead of copying its implementation, while keeping its own trigger, inputs, permissions, secrets, and project-specific jobs in its repository.

The current [`publish.yml`](../.github/workflows/publish.yml) is a placeholder; it does not yet define a callable reusable workflow. Before adopting it from another repository, implement and validate the reusable workflow interface (`workflow_call`, inputs, secrets, outputs, and permissions) and document the supported contract here.

Once a workflow is callable, a consumer generally references it using the repository-qualified path and a ref, for example:

```yaml
jobs:
  publish:
    uses: CollinPoetoehena/DevHub/.github/workflows/publish.yml@main
```

Use a maintained branch or, for stricter supply-chain pinning, a reviewed commit SHA according to the consumer's policy. A workflow reference does not automatically grant access to secrets: explicitly pass only the required secrets, use the narrowest permissions, and configure environment protection in the repository that owns the deployment credentials.

Keep workflows generic enough for multiple consumers. Put project-specific packaging, tests, deployment settings, and credentials in the consuming repository, and follow the separation described in the [DevHub README](../README.md#what-belongs-in-devhub).

# Helm

Reusable [Helm](https://helm.sh/) charts, used for packaging and deploying Kubernetes applications.

Each chart lives in its own dedicated repository. This file serves as the index and reference for all Helm charts, and documents conventions shared across them.

## DevHub

This repository ([DevHub](https://github.com/CollinPoetoehena/DevHub)) is the central reference for all Helm charts, see [README.md](README.md) for the full design and index of all component types.

## Structure

Each chart repository follows the [Helm Chart File Structure](https://helm.sh/docs/topics/charts/#the-chart-file-structure):

```
<chart-name>/
├── Chart.yaml
├── values.yaml
├── README.md
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    └── _helpers.tpl
```

Where:
- `Chart.yaml` contains the chart metadata (name, version, description, etc.).
- `values.yaml` defines the default configuration values for the chart.
- `README.md` provides documentation specific to the chart, including usage instructions, values descriptions, and any other relevant information.
- `templates/` contains the Kubernetes manifest templates rendered by Helm.

## Naming Convention

See [DevHub Global Naming Convention](./README.md#repositories--naming-conventions) for the overall naming rules applied across all DevHub components. Specifically for Helm, you can find some general tips in the [Helm best practices](https://helm.sh/docs/chart_best_practices/conventions/#chart-names). 

## Usage

Each chart repository contains its own README with usage instructions. The general pattern for installing a chart:

```bash
helm install <release-name> oci://ghcr.io/CollinPoetoehena/<chart-repo> --version <version>
```

Or add it as a dependency in your `Chart.yaml`:

```yaml
dependencies:
  - name: <chart-name>
    version: "<version>"
    repository: "oci://ghcr.io/CollinPoetoehena/<chart-repo>"
```

Then install with:

```bash
helm dependency update
helm install <release-name> .
```

## Charts

| Chart | Repository | Description |
|-------|------------|-------------|
| _(none yet)_ | | Helm Charts will be listed here as they are added |

## README Template

When creating a new chart repository, use the following template as the starting point for its `README.md`:

```markdown
# <package-name following the naming convention>

> Part of [DevHub/Helm](https://github.com/CollinPoetoehena/DevHub/blob/main/packages/Helm.md) — see that file for conventions, structure guidelines, and the full chart index.

<Short description of what this chart deploys.>

## Usage

```bash
helm install <release-name> oci://ghcr.io/CollinPoetoehena/<chart-name> --version <version>
```

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| | | | |

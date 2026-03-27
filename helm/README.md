# Helm

Reusable [Helm](https://helm.sh/) charts, used for packaging and deploying Kubernetes applications.

## Structure

Each chart lives in its own subdirectory under `helm/` and follows the [Helm Chart File Structure](https://helm.sh/docs/topics/charts/#the-chart-file-structure):

```
helm/
└── <chart-name>/
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

## Chart Naming Convention

Chart names use lowercase letters, digits, and hyphens only, following the [Helm best practices](https://helm.sh/docs/chart_best_practices/conventions/#chart-names). Names should be descriptive and scoped to what the chart deploys, e.g. `nginx`, `prometheus-stack`, `cert-manager`.

## Usage

Reference a chart from this repository directly using the Helm CLI:

```bash
# Install a chart directly from this repository
helm install <release-name> oci://ghcr.io/CollinPoetoehena/dev-hub/helm/<chart-name> --version <version>
```

Or add it as a dependency in your `Chart.yaml`:

```yaml
dependencies:
  - name: <chart-name>
    version: "<version>"
    repository: "oci://ghcr.io/CollinPoetoehena/dev-hub/helm"
```

Then install with:

```bash
helm dependency update
helm install <release-name> .
```

## Charts

| Chart | Description |
|-------|-------------|
| _(none yet)_ | Charts will be listed here as they are added |

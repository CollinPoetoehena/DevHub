---
name: helm
description: 'Helm chart patterns and testing: chart structure, Chart.yaml, values naming and documentation, input validation with @schema annotations and helm-schema, named templates and helpers, labels, images, RBAC, dependencies, CRDs, and chart tests with helm lint, kubeconform, helm-unittest, and chart-testing. Use when creating, changing, reviewing, or testing Helm charts, values, or templates.'
---

# Helm

Index for Helm work. Open only the reference the task needs; the Helm, Kubernetes, and common instructions take precedence over the references.

## When to Use This Skill

- Creating a chart or changing `Chart.yaml`, values, or templates
- Designing values and their schema for users who override them
- Adding chart dependencies, CRDs, or RBAC resources
- Writing or running chart tests

## Steps

1. **Write or change a chart.** Open [references/patterns.md](references/patterns.md) for chart structure, `Chart.yaml`, values, templates and helpers, labels, images, RBAC, dependencies, and CRDs.
2. **Validate the values.** Annotate every new or changed value with an `@schema` block and regenerate `values.schema.json` with helm-schema, as described in the values schema section of [references/patterns.md](references/patterns.md).
3. **Test the chart.** Add or update helm-unittest tests for every changed template, then follow [references/testing.md](references/testing.md) for linting, the schema check, rendering, chart-testing, and release tests.
4. **Check the rendered manifests.** Apply the Kubernetes instructions to the output of `helm template`.
5. **Validate.** Run the validation commands from the Helm instructions and report each result.

## Gotchas

- **`default` overrides explicit `false`:** `default true .Values.enabled` turns a user's `false` into `true`; use `hasKey` or `ternary` for booleans.
- **Lists replace, maps merge:** overriding a list in values replaces it completely, while maps merge key by key.
- **Dashed keys break dot notation:** read keys such as `gitlab-runner` with `index .Values "gitlab-runner"`.
- **YAML comments still render:** a `#` comment around a `required` call still runs it; use template comments `{{- /* */ -}}` instead.
- **`lookup` is empty offline:** `lookup` returns nothing during `helm template` and client-side dry runs, so templates must handle the empty result.
- **Stale schemas break validation:** a value added without regenerating `values.schema.json` is rejected as an unknown key, and a changed constraint is not enforced; run `helm-schema --check`.
- **CRDs are installed once:** Helm installs CRDs from `crds/` but never upgrades or deletes them.

## Related Skills

- `kubernetes`: workload patterns for the rendered manifests.

## References

- [Helm documentation](https://helm.sh/docs/)
- [Chart best practices](https://helm.sh/docs/chart_best_practices/)
- [helm-schema](https://github.com/dadav/helm-schema)
- [helm-unittest](https://github.com/helm-unittest/helm-unittest)

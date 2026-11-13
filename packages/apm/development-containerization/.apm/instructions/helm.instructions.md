---
description: "Use when writing or reviewing Helm charts, values, or templates: chart, values, and template conventions and validation commands alongside the common guidelines."
applyTo: "**/Chart.yaml,**/Chart.lock,**/values*.yaml,**/values.schema.json,**/templates/**/*.yaml,**/templates/**/*.tpl,**/templates/NOTES.txt"
---

# Helm Guidelines

Use general best practices for Helm and follow the common guidelines in `devhub-guidelines-core`.

Specifically for Helm, in addition to general best practices:

Repository configuration, owning documentation, and `AGENTS.md` may refine or override these shared defaults. When applicable sources conflict, follow higher-priority policy and surface unresolved conflicts rather than assuming universal host precedence.

For rendered manifests, see the Kubernetes guidelines and use the `kubernetes` skill for additional procedures.

## Rules

- Increase the chart `version` (SemVer) for every chart change, and keep `appVersion` quoted.
- Name values in camelCase, prefer flat values, use maps instead of lists for items users override, and document every value with a comment that starts with its name.
- Validate all input: annotate every value with an `@schema` block, including constraints such as `pattern`, `enum`, and `required`, and generate `values.schema.json` with helm-schema; never edit the generated schema, and commit it with `values.yaml`.
- Cover every template with helm-unittest tests in the chart's `tests/` directory, and update them in the same change as the template.
- Put one resource per template file, named after its kind in dashed notation, and prefix every defined template with the chart name, such as `mychart.fullname`.
- Use `include` with `nindent` for helpers, `quote` for strings, and `required` for mandatory values.
- Take images from values with a fixed tag or digest; never default to `latest`.
- Never put secret values in `values.yaml` defaults; reference existing Secrets or the repository's secret mechanism.
- Use `https` repositories and patch-level ranges such as `~1.2.3` for dependencies, add a `condition` to optional ones, and commit `Chart.lock`.

## Validation

Run from the repository root; use the repository's configured commands when they differ:

```sh
helm-schema --chart-search-root <chart> --check
helm lint --strict <chart>
helm template <release> <chart> | kubeconform -strict -summary
helm unittest <chart>
```

Use the `helm` skill for additional Helm procedures and references.

## References

- [Helm chart best practices](https://helm.sh/docs/chart_best_practices/)
- [Charts](https://helm.sh/docs/topics/charts/)
- [Chart template guide](https://helm.sh/docs/chart_template_guide/)
- [helm lint](https://helm.sh/docs/helm/helm_lint/)
- [helm-schema](https://github.com/dadav/helm-schema)
- [helm-unittest](https://github.com/helm-unittest/helm-unittest)

Use relevant available skills for additional procedures and references.

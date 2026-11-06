---
description: "Use when writing or reviewing Helm charts, values, or templates: mandatory chart, values, and template rules and validation commands on top of the common instructions."
applyTo: "**/Chart.yaml,**/Chart.lock,**/values*.yaml,**/values.schema.json,**/templates/**/*.yaml,**/templates/**/*.tpl,**/templates/NOTES.txt"
---

# Helm Instructions

These rules add Helm specifics to the [common instructions](https://github.com/CollinPoetoehena/DevHub/tree/main/packages/apm/common) of `devhub-common` (coding, security, documentation, and Git), which always apply. Where they differ, these rules refine the common ones; the repository's own configuration and `AGENTS.md` take precedence over both.

## Skills

- Apply the `helm` skill before adding or changing charts, values, templates, or chart tests; it opens one reference per task.
- Apply the Kubernetes instructions and the `kubernetes` skill to the rendered manifests.

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

## References

- [Helm chart best practices](https://helm.sh/docs/chart_best_practices/)
- [Charts](https://helm.sh/docs/topics/charts/)
- [Chart template guide](https://helm.sh/docs/chart_template_guide/)
- [helm lint](https://helm.sh/docs/helm/helm_lint/)
- [helm-schema](https://github.com/dadav/helm-schema)
- [helm-unittest](https://github.com/helm-unittest/helm-unittest)

# Helm Testing

DevHub chart testing, based on the official [Helm documentation](https://helm.sh/docs/), [helm-unittest](https://github.com/helm-unittest/helm-unittest), and [chart-testing](https://github.com/helm/chart-testing). Repository configuration and the Helm, Kubernetes, and common instructions take precedence over this reference.

## Test Levels

| Level | Tool | Needs a cluster | Checks |
|---|---|---|---|
| Lint | `helm lint --strict` | No | Chart structure, `Chart.yaml`, template errors, values schema |
| Schema | `helm-schema --check` | No | `values.schema.json` matches the `@schema` annotations in `values.yaml` |
| Render and schema | `helm template` with kubeconform | No | Rendered manifests against Kubernetes schemas |
| Unit | helm-unittest | No | Template output for specific values; required for every chart |
| Chart changes | chart-testing (`ct`) | `ct install` only | Lint, version increase, and install of changed charts |
| Release | `helm test` | Yes | Behavior of an installed release |

Run the levels that do not need a cluster for every change; run cluster levels only against a cluster the user approved. Every chart has a generated values schema and helm-unittest tests.

## Lint and Render

```sh
helm dependency build mychart
helm lint --strict mychart
helm lint --strict mychart -f mychart/ci/production-values.yaml
helm-schema --chart-search-root mychart --check
helm template my-release mychart | kubeconform -strict -summary
helm template my-release mychart --set 'tenants[0]=TOOLONG'  # must fail: the schema rejects invalid input
```

Keep representative values files in `ci/`, such as `ci/production-values.yaml`; chart-testing uses them automatically, and the lint and render commands above can use them explicitly.

## Unit Tests

Every chart has unit tests. helm-unittest renders templates with given values and asserts on the output, without a cluster. Tests live in `tests/` inside the chart, with files ending in `_test.yaml`, one suite per template:

```yaml
# tests/deployment_test.yaml
suite: deployment
templates:
  - deployment.yaml
tests:
  - it: uses the configured image tag
    set:
      image.repository: registry.example.com/team/app
      image.tag: "1.2.3"
    asserts:
      - equal:
          path: spec.template.spec.containers[0].image
          value: registry.example.com/team/app:1.2.3
  - it: fails without an image repository
    set:
      image.repository: null
    asserts:
      - failedTemplate:
          errorMessage: image.repository is required
```

```yaml
# tests/configmap_test.yaml
suite: configmap
templates:
  - configmap.yaml
tests:
  - it: renders one entry per tenant
    set:
      tenants: [aia, cld]
    asserts:
      - isKind:
          of: ConfigMap
      - exists:
          path: data.aia
      - exists:
          path: data.cld
      - notExists:
          path: data.dcs
```

```sh
helm plugin install https://github.com/helm-unittest/helm-unittest
helm unittest mychart
```

Cover the values that change the output: optional resources toggled by `enabled` flags, overridden images, lists such as `tenants`, `required` failures, and labels and selectors. Add or update tests in the same change as the template.

## Chart Changes in CI

chart-testing lints only the charts changed against the target branch, checks that their `version` increased, and can install them in a test cluster:

```sh
ct lint --target-branch main --charts mychart
ct install --target-branch main --charts mychart
```

## Release Tests

A release test is a Pod or Job in `templates/tests/` with the `helm.sh/hook: test` annotation; it passes when the container exits with code 0.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "mychart.fullname" . }}-test-connection"
  labels:
    {{- include "mychart.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": test
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  restartPolicy: Never
  containers:
    - name: wget
      image: busybox:1.37
      command: ["wget"]
      args: ["{{ include "mychart.fullname" . }}:{{ .Values.serverPort }}"]
```

```sh
helm test my-release
```

## References

- [helm lint](https://helm.sh/docs/helm/helm_lint/)
- [helm template](https://helm.sh/docs/helm/helm_template/)
- [Chart tests](https://helm.sh/docs/topics/chart_tests/)
- [helm-unittest](https://github.com/helm-unittest/helm-unittest)
- [helm-schema](https://github.com/dadav/helm-schema)
- [chart-testing](https://github.com/helm/chart-testing)
- [kubeconform](https://github.com/yannh/kubeconform)

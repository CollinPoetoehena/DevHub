# Helm Patterns

DevHub chart patterns, based on the [Helm chart best practices](https://helm.sh/docs/chart_best_practices/) and [helm-schema](https://github.com/dadav/helm-schema). Repository configuration and the Helm, Kubernetes, and common instructions take precedence over this reference.

## Chart Structure

Create new charts with `helm create` so helper names follow the conventions, then remove what the chart does not need.

```text
mychart/
  Chart.yaml            # chart metadata and dependencies
  Chart.lock            # locked dependency versions
  values.yaml           # documented defaults
  values.schema.json    # generated from @schema annotations in values.yaml
  README.md             # usage and values overview
  charts/               # packaged dependencies (generated)
  crds/                 # CustomResourceDefinitions, installed before templates
  templates/
    _helpers.tpl        # named templates, no output
    deployment.yaml
    service.yaml
    serviceaccount.yaml
    NOTES.txt           # short post-install usage notes
    tests/
      test-connection.yaml  # release test, run by helm test
  tests/
    deployment_test.yaml  # helm-unittest unit tests
```

## Chart.yaml

```yaml
apiVersion: v2
name: mychart
description: One sentence that describes what the chart deploys.
type: application
version: 1.4.0          # chart version, SemVer, bumped on every chart change
appVersion: "2.7.1"     # version of the packaged application, quoted
kubeVersion: ">=1.29.0-0"
dependencies:
  - name: postgresql
    version: ~16.4.0
    repository: https://charts.example.com
    condition: postgresql.enabled
```

- Chart names use lowercase letters, digits, and dashes, and match the directory name.
- `version` follows SemVer and changes whenever any chart file changes; `appVersion` tracks the application independently.
- Add custom metadata under `annotations`; other unknown fields are rejected.

## Values

```yaml
# replicaCount is the number of pods for the Deployment.
replicaCount: 2

image:
  # image.repository is the container image without tag.
  repository: registry.example.com/team/app
  # image.tag is a fixed tag or digest; defaults to the chart appVersion when empty.
  tag: ""
  # image.pullPolicy is the Kubernetes image pull policy.
  pullPolicy: IfNotPresent

# serverPort is the HTTP port the application listens on.
serverPort: 8080
```

- **Naming:** start with a lowercase letter and use camelCase; never initial capitals or dashes.
- **Flat over nested:** prefer `serverPort` to `server.port`; nest only when a group of related values has at least one required value.
- **Types:** quote all strings; YAML coerces values such as `false`, `"false"`, and large integers differently.
- **Overridable items:** use maps, such as `servers.foo.port`, instead of lists, so users can override one item with `--set`.
- **Documentation:** document every value with a comment that starts with the value's name.
- **Schema:** annotate every value with an `@schema` block and generate `values.schema.json` from it, as described in [values schema](#values-schema).

## Values Schema

Every chart validates its input with a `values.schema.json`. Helm applies it to the final merged values, including `-f` files and `--set` overrides, on `install`, `upgrade`, `lint`, and `template`, so invalid input fails before anything reaches the cluster.

Do not write the schema by hand. Annotate each value in `values.yaml` with an `@schema` block, a YAML comment holding JSON Schema keywords, and generate the schema with [helm-schema](https://github.com/dadav/helm-schema). The value's documentation comment follows the block and becomes the schema description:

```yaml
# @schema
# type: integer
# minimum: 1
# @schema
# replicaCount is the number of pods for the Deployment.
replicaCount: 2

# @schema
# type: array
# items:
#   type: string
#   pattern: ^[a-z]{3}$
# @schema
# tenants lists the three-letter tenant codes that get their own configuration.
tenants:
  - aia
  - cld
  - dcs

image:
  # @schema
  # type: string
  # minLength: 1
  # required: true
  # @schema
  # image.repository is the container image without tag.
  repository: registry.example.com/team/app
  # @schema
  # enum: [Always, IfNotPresent, Never]
  # @schema
  # image.pullPolicy is the Kubernetes image pull policy.
  pullPolicy: IfNotPresent

# @schema
# type: object
# additionalProperties:
#   type: string
# @schema
# podAnnotations are extra annotations for the pods.
podAnnotations: {}
```

- **Constrain, not only type:** add `pattern`, `enum`, `minimum`, `maximum`, `minLength`, and `required: true` wherever the template depends on a format or presence, as with the tenant codes above.
- **Unknown keys fail:** helm-schema sets `additionalProperties: false` on non-empty maps, so a misspelled key in an override fails validation. Allow extra keys explicitly, as for `podAnnotations`, only where users supply free-form maps.
- **Generate and commit together:** regenerate after every change to `values.yaml` or its annotations, and commit `values.yaml` and `values.schema.json` together; never edit the generated file.
- **Check in CI:** `--check` fails when the committed schema is missing or stale, without writing files.

```sh
helm-schema --chart-search-root mychart          # generate mychart/values.schema.json
helm-schema --chart-search-root mychart --check  # fail when the schema is missing or stale
helm template demo mychart --set 'tenants[0]=TOOLONG'  # must fail on the pattern
```

Install helm-schema as a binary or as the Helm plugin (`helm schema`), or run it as a [pre-commit hook](https://github.com/dadav/helm-schema#pre-commit-hook); build chart dependencies before generating so their values are included.

## Templates

- **Files:** use `.yaml` for templates that render YAML and `.tpl` for templates without output; use dashed names that include the kind, such as `api-deployment.yaml`; put one resource per file.
- **Named templates:** prefix every `define` with the chart name, such as `mychart.fullname`, because defined templates are global across the chart and its subcharts.
- **Formatting:** indent with two spaces, put spaces inside braces (`{{ .Values.foo }}`), and chomp whitespace with `{{-` and `-}}` so the output has no runs of blank lines.
- **Helpers:** call helpers with `include` and indent them with `nindent`, so they can be piped.
- **Required values:** fail early with `required "image.repository is required" .Values.image.repository`.
- **Comments:** use template comments `{{- /* */ -}}` to document templates; YAML comments appear in the output and still execute the template code inside them.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "mychart.fullname" . }}
  labels:
    {{- include "mychart.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "mychart.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "mychart.selectorLabels" . | nindent 8 }}
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
    spec:
      serviceAccountName: {{ include "mychart.serviceAccountName" . }}
      containers:
        - name: app
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.serverPort }}
```

The `checksum/config` annotation rolls the pods when the rendered ConfigMap changes.

## Labels and Annotations

Use labels for metadata that Kubernetes or operators query, and annotations for everything else; hooks are always annotations.

| Label | Value | Status |
|---|---|---|
| `app.kubernetes.io/name` | `{{ include "mychart.name" . }}` | Recommended |
| `app.kubernetes.io/instance` | `{{ .Release.Name }}` | Recommended |
| `app.kubernetes.io/managed-by` | `{{ .Release.Service }}` | Recommended |
| `helm.sh/chart` | `{{ .Chart.Name }}-{{ .Chart.Version \| replace "+" "_" }}` | Recommended |
| `app.kubernetes.io/version` | `{{ .Chart.AppVersion }}` | Optional |
| `app.kubernetes.io/component` | Role, such as `frontend` | Optional |
| `app.kubernetes.io/part-of` | Larger application | Optional |

Selectors use only `name` and `instance`, because selectors cannot change after creation and the other labels change between releases.

## Images and Pods

- Use a fixed tag or digest; never `latest`, `head`, `canary`, or other floating tags.
- Define the repository, tag, and pull policy in values so users can override them.
- Declare a `selector` in every pod template, matching the selector labels.

## RBAC and ServiceAccounts

Keep RBAC and ServiceAccount settings under separate keys:

```yaml
rbac:
  # rbac.create controls whether the chart creates RBAC resources.
  create: true

serviceAccount:
  # serviceAccount.create controls whether the chart creates a ServiceAccount.
  create: true
  # serviceAccount.name is the ServiceAccount to use; generated from the fullname when empty.
  name: ""
```

```yaml
{{- define "mychart.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{ default (include "mychart.fullname" .) .Values.serviceAccount.name }}
{{- else -}}
{{ default "default" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}
```

## Dependencies

- Use `https` repository URLs, or a repository alias with `@`.
- Use patch-level ranges such as `~1.2.3`, and `~1.2.3-0` when pre-releases must match.
- Add a `condition` such as `postgresql.enabled` to every optional dependency, and shared `tags` to dependencies that together form one optional feature.
- Run `helm dependency update` after changing dependencies and commit `Chart.lock`.

## CRDs

- Put CRDs in `crds/` when the chart owns them; Helm installs them before the templates but never upgrades or deletes them.
- Ship CRDs that need upgrades in a separate chart or manage them outside Helm.

## Secrets

- Never put secret values in `values.yaml` defaults.
- Reference an existing Secret through a value such as `existingSecret`, or integrate with the repository's secret mechanism.

## References

- [Chart best practices](https://helm.sh/docs/chart_best_practices/)
- [Values](https://helm.sh/docs/chart_best_practices/values/)
- [Templates](https://helm.sh/docs/chart_best_practices/templates/)
- [Labels and annotations](https://helm.sh/docs/chart_best_practices/labels/)
- [Dependencies](https://helm.sh/docs/chart_best_practices/dependencies/)
- [Pods and pod templates](https://helm.sh/docs/chart_best_practices/pods/)
- [Role-based access control](https://helm.sh/docs/chart_best_practices/rbac/)
- [Custom resource definitions](https://helm.sh/docs/chart_best_practices/custom_resource_definitions/)
- [Charts: schema files](https://helm.sh/docs/topics/charts/#schema-files)
- [helm-schema](https://github.com/dadav/helm-schema)
- [Chart template guide](https://helm.sh/docs/chart_template_guide/)

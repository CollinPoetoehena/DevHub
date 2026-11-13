# DevHub Containerization Package

`devhub-development-containerization` is an opt-in APM package for local development environments that build container images or deploy to Kubernetes. It adds Docker, Kubernetes, and Helm guidance, skills, and references and depends on [`development-core`](../development-core/README.md). Adopt shared repository standards separately through [`guidelines-core`](../guidelines-core/README.md).

The [APM guide](../README.md) owns the [language and framework design](../README.md#language-and-framework-guidance), the [package design](../README.md#package-design), and how to [maintain reused content](../README.md#maintaining-reused-content). The Docker instructions hold the DevHub Dockerfile defaults: RUN directives, base images, layer caching, and OpenShift-compatible runtime permissions.

## Table of Contents

- [Package contents](#package-contents)
- [Reuse registry](#reuse-registry)
- [Consumption](#consumption)

---

## Package contents

| File | Type | Purpose |
|---|---|---|
| [`docker.instructions.md`](.apm/instructions/docker.instructions.md) | Instruction (Dockerfiles, Compose files, `.dockerignore`) | DevHub Dockerfile defaults, image and Compose rules, and validation commands; points to the skill |
| [`kubernetes.instructions.md`](.apm/instructions/kubernetes.instructions.md) | Instruction (`k8s/`, `manifests/`, `deploy/`, Kustomize files) | Workload, security, and labeling rules and validation commands; points to the skills |
| [`helm.instructions.md`](.apm/instructions/helm.instructions.md) | Instruction (chart, values, and template files) | Chart, values, schema, template, and unit test rules and validation commands; points to the skills |
| [`docker`](.apm/skills/docker/SKILL.md) | Skill | Index and gotchas for Dockerfiles and Compose |
| [`docker/references/patterns.md`](.apm/skills/docker/references/patterns.md) | Skill reference | Compose stacks, multi-stage builds, networking, volumes, security, `.dockerignore`, and debugging |
| [`kubernetes`](.apm/skills/kubernetes/SKILL.md) | Skill | Index and gotchas for Kubernetes work |
| [`kubernetes/references/patterns.md`](.apm/skills/kubernetes/references/patterns.md) | Skill reference | Workload templates, probes, networking, configuration, resources, RBAC, autoscaling, Jobs, and kubectl debugging |
| [`kubernetes/references/manifests.md`](.apm/skills/kubernetes/references/manifests.md) | Skill reference | Labels, security context defaults, Pod Security Standards, rollouts, validation, and the manifest checklist |
| [`kubernetes/references/deployment.md`](.apm/skills/kubernetes/references/deployment.md) | Skill reference | Configuration and secrets, security, observability, deployment strategies, and troubleshooting |
| [`helm`](.apm/skills/helm/SKILL.md) | Skill | Index and gotchas for Helm charts |
| [`helm/references/patterns.md`](.apm/skills/helm/references/patterns.md) | Skill reference | Chart structure, `Chart.yaml`, values, `@schema` annotations with helm-schema, templates, labels, images, RBAC, dependencies, CRDs, and secrets |
| [`helm/references/testing.md`](.apm/skills/helm/references/testing.md) | Skill reference | Lint, schema check, render, required helm-unittest tests, chart-testing, and release tests |

---

## Reuse registry

Adapted parts are copied from the source at the synced commit and then standardized: the upstream frontmatter and title are replaced by a standard header with the source link and precedence rule, skill-activation sections and closing reminders are removed, and official documentation links are added at the end. The synced column lists the upstream commit and the date the part was copied from it; the local changes column lists only changes beyond that standardization. Update parts as described in [maintaining reused content](../README.md#maintaining-reused-content).

| Part | Source | Type | Synced | Local changes |
|---|---|---|---|---|
| `docker/references/patterns.md` | [ECC `docker-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/docker-patterns/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | Removed the hardened CLI installer harness section, which tests ECC's own installer |
| `kubernetes/references/patterns.md` | [ECC `kubernetes-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/kubernetes-patterns/SKILL.md) | Adapted | `b38be6a` (2026-11-06) | Removed the skill description and related ECC skills |
| `kubernetes/references/manifests.md` | [awesome-copilot `kubernetes-manifests.instructions.md`](https://github.com/github/awesome-copilot/blob/main/instructions/kubernetes-manifests.instructions.md) | Adapted | `797337f` (2026-11-06) | Removed the persona introduction; its `applyTo` directories informed the Kubernetes instruction |
| `kubernetes/references/deployment.md` | [awesome-copilot `kubernetes-deployment-best-practices.instructions.md`](https://github.com/github/awesome-copilot/blob/main/instructions/kubernetes-deployment-best-practices.instructions.md) | Adapted | `797337f` (2026-11-06) | Removed the persona introduction and conclusion |
| `helm/references/patterns.md` | [Helm chart best practices](https://helm.sh/docs/chart_best_practices/) and [helm-schema](https://github.com/dadav/helm-schema) | Authored | Not applicable | Condensed from the official guide; no suitable collection source exists. Values schema generated from `@schema` annotations with helm-schema |
| `helm/references/testing.md` | [Helm](https://helm.sh/docs/topics/chart_tests/), [helm-unittest](https://github.com/helm-unittest/helm-unittest), and [chart-testing](https://github.com/helm/chart-testing) documentation | Authored | Not applicable | Condensed from the official documentation |
| Docker instruction | DevHub Dockerfile instructions previously in `devhub-common` | Authored | Not applicable | Moved unchanged, with image, Compose, and validation rules added |
| Kubernetes and Helm instructions, `SKILL.md` indexes | DevHub | Authored | Not applicable | None |

---

## Consumption

The package depends on [`development-core`](../development-core/README.md) for shared local capabilities. Add the stack package to the consumer's `apm.yml`, then install and verify it using the host-specific procedure described in the [APM guide](../README.md#repository-setup):

```yaml
dependencies:
  apm:
    - CollinPoetoehena/DevHub/packages/apm/development-containerization
```

State the registries, cluster contexts that agents may use, and validation commands in the repository's `AGENTS.md`. Changes are recorded in the [changelog](CHANGELOG.md).

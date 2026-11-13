---
description: "Use when writing or reviewing Kubernetes manifests or Kustomize overlays: workload, security, and labeling conventions and validation commands alongside the common guidelines."
applyTo: "**/k8s/**/*.yaml,**/k8s/**/*.yml,**/manifests/**/*.yaml,**/manifests/**/*.yml,**/deploy/**/*.yaml,**/deploy/**/*.yml,**/kustomization.yaml,**/kustomization.yml"
---

# Kubernetes Guidelines

Use general best practices for Kubernetes and follow the common guidelines in `devhub-guidelines-core`.

Specifically for Kubernetes, in addition to general best practices:

Repository configuration, owning documentation, and `AGENTS.md` may refine or override these shared defaults. When applicable sources conflict, follow higher-priority policy and surface unresolved conflicts rather than assuming universal host precedence.

## Rules

- Set the recommended `app.kubernetes.io/*` labels, and select pods only with labels that never change, such as `name` and `instance`.
- Pin images to a fixed tag or digest; never use `latest` or other floating tags.
- Set CPU and memory requests and a memory limit for every container.
- Define readiness and liveness probes, and a startup probe for slow starts; liveness probes must not depend on external services.
- Meet the restricted Pod Security Standard: `runAsNonRoot: true`, `allowPrivilegeEscalation: false`, all capabilities dropped, a `RuntimeDefault` seccomp profile, and a read-only root file system where possible.
- Never commit secret values in manifests; reference Secrets managed by the repository's secret mechanism.
- Give workloads a dedicated ServiceAccount with least-privilege RBAC, and disable token automounting unless the workload calls the Kubernetes API.

## Validation

Validate without changing a cluster; use the repository's configured commands when they differ:

```sh
kubeconform -strict -summary <manifests>
kubectl kustomize <overlay> | kubeconform -strict -summary
kubectl apply --dry-run=client -f <manifest>
```

Run server-side dry runs or applies only against a cluster context the user approved.

Use the `kubernetes` skill for additional Kubernetes procedures; use the `helm` skill for Helm chart templates.

## References

- [Kubernetes documentation](https://kubernetes.io/docs/home/)
- [Recommended labels](https://kubernetes.io/docs/concepts/overview/working-with-objects/common-labels/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Configuration best practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [kubeconform](https://github.com/yannh/kubeconform)

Use relevant available skills for additional procedures and references.

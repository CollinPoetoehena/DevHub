---
description: "Use when writing or reviewing Kubernetes manifests or Kustomize overlays: mandatory workload, security, and labeling rules and validation commands on top of the common instructions."
applyTo: "**/k8s/**/*.yaml,**/k8s/**/*.yml,**/manifests/**/*.yaml,**/manifests/**/*.yml,**/deploy/**/*.yaml,**/deploy/**/*.yml,**/kustomization.yaml,**/kustomization.yml"
---

# Kubernetes Instructions

These rules add Kubernetes specifics to the [common instructions](https://github.com/CollinPoetoehena/DevHub/tree/main/packages/apm/common) of `devhub-common` (coding, security, documentation, and Git), which always apply. Where they differ, these rules refine the common ones; the repository's own configuration and `AGENTS.md` take precedence over both.

## Skills

- Apply the `kubernetes` skill before adding or changing workloads, services, configuration, RBAC, or autoscaling; it opens one reference per task.
- Apply the `helm` skill when the manifests are Helm chart templates.

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

## References

- [Kubernetes documentation](https://kubernetes.io/docs/home/)
- [Recommended labels](https://kubernetes.io/docs/concepts/overview/working-with-objects/common-labels/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Configuration best practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [kubeconform](https://github.com/yannh/kubeconform)

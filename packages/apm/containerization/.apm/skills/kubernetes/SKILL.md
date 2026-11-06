---
name: kubernetes
description: 'Kubernetes workload patterns and deployment practices: Deployments, StatefulSets, Jobs, probes, Services and Ingress, ConfigMaps and Secrets, resources, RBAC, autoscaling, disruption budgets, namespaces, manifest labels and security contexts, rollout strategies, observability, and kubectl debugging. Use when writing, reviewing, deploying, or debugging Kubernetes manifests and workloads.'
---

# Kubernetes

Index for Kubernetes work. Open only the reference the task needs; the Kubernetes and common instructions take precedence over the references.

## When to Use This Skill

- Writing or reviewing Deployments, StatefulSets, Jobs, or CronJobs
- Configuring probes, resources, autoscaling, or disruption budgets
- Setting up Services, Ingress, ConfigMaps, Secrets, RBAC, or namespaces
- Planning rollouts and rollbacks, or debugging failing pods

## Steps

1. **Write or change workloads.** Open [references/patterns.md](references/patterns.md) for production workload templates, probes, Services and Ingress, configuration, resources, RBAC, autoscaling, disruption budgets, namespaces, and Jobs.
2. **Check manifest conventions.** Open [references/manifests.md](references/manifests.md) for labels, security context defaults, Pod Security Standards, rollout strategies, validation, and the manifest checklist.
3. **Plan deployment and operations.** Open [references/deployment.md](references/deployment.md) for configuration and secrets management, security, observability, deployment strategies, and troubleshooting.
4. **Debug.** Use the kubectl cheatsheet in [references/patterns.md](references/patterns.md) and the troubleshooting section in [references/deployment.md](references/deployment.md).
5. **Validate.** Run the validation commands from the Kubernetes instructions and report each result.

## Gotchas

- **Immutable selectors:** a Deployment's `spec.selector` cannot change after creation; changing it requires a new object.
- **Liveness probes on dependencies:** a liveness probe that checks a database restarts every pod when the database fails; check only the process itself.
- **Limits have different effects:** exceeding a memory limit kills the container (`OOMKilled`), while a CPU limit throttles it.
- **Configuration changes do not restart pods:** pods keep old ConfigMap and Secret values in environment variables; roll the Deployment, for example with a checksum annotation.
- **Secrets are only encoded:** Secret data is base64-encoded, not encrypted; protect it with encryption at rest and RBAC, and keep values out of Git.

## Related Skills

- `docker`: building the images.
- `helm`: packaging manifests as charts.

## References

- [Kubernetes documentation](https://kubernetes.io/docs/home/)
- [Kubernetes API reference](https://kubernetes.io/docs/reference/kubernetes-api/)
- [kubectl reference](https://kubernetes.io/docs/reference/kubectl/)

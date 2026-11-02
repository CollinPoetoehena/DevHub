# Kubernetes Commands

See the [cheat sheet README](README.md) for scope, usage, placeholders, and safety.

Requires `kubectl`, a configured kubeconfig, and permission for the operation. Replace `demo`, `web`, `web-pod`, and `app=web` with the intended namespace, resource names, and label selector. Verify context before every change; examples using `-A` inspect all namespaces.

## Table of Contents

- [Context and discovery](#context-and-discovery)
  - [kubectl config](#kubectl-config)
  - [kubectl cluster-info](#kubectl-cluster-info)
  - [kubectl api-resources](#kubectl-api-resources)
  - [kubectl explain](#kubectl-explain)
  - [kubectl auth can-i](#kubectl-auth-can-i)
- [Inspection and troubleshooting](#inspection-and-troubleshooting)
  - [kubectl get](#kubectl-get)
  - [kubectl describe](#kubectl-describe)
  - [kubectl logs](#kubectl-logs)
  - [kubectl top](#kubectl-top)
  - [kubectl exec](#kubectl-exec)
  - [kubectl port-forward](#kubectl-port-forward)
- [Workload changes](#workload-changes)
  - [kubectl diff](#kubectl-diff)
  - [kubectl apply](#kubectl-apply)
  - [kubectl rollout](#kubectl-rollout)
  - [kubectl scale](#kubectl-scale)
  - [kubectl delete](#kubectl-delete)
- [Node maintenance](#node-maintenance)
  - [kubectl cordon](#kubectl-cordon)
  - [kubectl drain](#kubectl-drain)
  - [kubectl uncordon](#kubectl-uncordon)
- [MetalLB](#metallb)
  - [kubectl get: MetalLB resources](#kubectl-get-metallb-resources)

---

## Context and discovery

### kubectl config

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_config/).

```bash
kubectl config get-contexts                     # Available cluster/user/namespace contexts
kubectl config current-context                  # Currently selected context
kubectl config view --minify                     # Current context configuration; do not share credentials
kubectl config use-context my-cluster            # Changes local default context
kubectl config set-context --current --namespace=demo # Changes local default namespace
```

### kubectl cluster-info

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_cluster-info/).

```bash
kubectl cluster-info                            # Control-plane and cluster service addresses
```

### kubectl api-resources

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_api-resources/).

```bash
kubectl api-resources                           # Resource types supported by the cluster
kubectl api-resources --namespaced=true          # Namespace-scoped resource types
```

### kubectl explain

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_explain/).

```bash
kubectl explain deployment.spec                 # Schema documentation from the cluster
kubectl explain deployment.spec.template.spec   # Inspect a nested field
```

### kubectl auth can-i

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_auth/kubectl_auth_can-i/).

```bash
kubectl auth can-i get pods -n demo              # Check whether this identity can read pods
kubectl auth can-i --list -n demo                # List allowed actions in a namespace
```

---

## Inspection and troubleshooting

### kubectl get

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_get/) and [JSONPath support](https://kubernetes.io/docs/reference/kubectl/jsonpath/).

```bash
kubectl get nodes -o wide                        # Node status, versions, and addresses
kubectl get namespaces                          # Available namespaces
kubectl get pods -A -o wide                      # Pods across namespaces, with node assignment
kubectl get pods -n demo -l app=web -w            # Watch pods matching a label; Ctrl+C stops
kubectl get deployment web -n demo -o yaml       # Full deployment object
kubectl get services,ingresses -n demo           # Service and ingress resources
kubectl get endpointslices -n demo -l kubernetes.io/service-name=web # Service backends
kubectl get pvc -n demo                          # Persistent volume claims
kubectl get pv,storageclasses                    # Cluster-scoped storage resources
kubectl get events -n demo --sort-by=.metadata.creationTimestamp # Events by creation time
kubectl get pods -n demo -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\n"}{end}' # Name and phase
```

### kubectl describe

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_describe/).

```bash
kubectl describe pod web-pod -n demo             # Pod state, probes, scheduling, and events
kubectl describe node worker-1                   # Node conditions, capacity, and events
kubectl describe pvc data -n demo                # Claim binding and provisioning events
```

### kubectl logs

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_logs/).

```bash
kubectl logs web-pod -n demo -c web --tail=100    # Last 100 lines from one container
kubectl logs web-pod -n demo -c web -f            # Follow logs; Ctrl+C stops
kubectl logs web-pod -n demo -c web --previous    # Previous terminated container instance
kubectl logs -n demo -l app=web --all-containers=true --prefix --tail=50 # Label-selected pod logs
```

### kubectl top

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_top/). Requires the Metrics API, usually provided by Metrics Server.

```bash
kubectl top nodes                               # Recent node CPU and memory usage
kubectl top pods -n demo --containers            # Per-container CPU and memory usage
```

### kubectl exec

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_exec/).

**Changes state:** executes inside a running container with its permissions; the shell and tools must exist in the image.

```bash
kubectl exec -n demo web-pod -c web -- printenv PATH # Read one environment variable
kubectl exec -it -n demo web-pod -c web -- sh     # Open an interactive shell; exit to leave
```

### kubectl port-forward

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_port-forward/).

```bash
kubectl port-forward -n demo service/web 8080:80 # Forward localhost:8080 to service port 80
```

Keep the process running while using the tunnel; Ctrl+C stops it. The default listener is localhost; do not expose it on all interfaces casually.

---

## Workload changes

### kubectl diff

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_diff/).

```bash
kubectl diff -n demo -f deployment.yaml          # Preview manifest differences; exit 1 means differences
```

### kubectl apply

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_apply/).

**Changes state:** check the context, manifest namespace, and preview first. For GitOps-managed resources, update the owning source instead of making ad-hoc live changes.

```bash
kubectl apply -n demo --dry-run=server -f deployment.yaml # Validate through API admission without persisting
kubectl apply -n demo -f deployment.yaml         # Create or update resources from the manifest
```

### kubectl rollout

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/).

```bash
kubectl rollout status deployment/web -n demo --timeout=120s # Wait for rollout completion
kubectl rollout history deployment/web -n demo  # Inspect recorded revisions
# Disruptive: replaces pods; confirm availability and ownership first.
kubectl rollout restart deployment/web -n demo  # Trigger a rolling restart
kubectl rollout undo deployment/web -n demo     # Revert the pod template to the previous revision
```

### kubectl scale

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_scale/).

**Changes state:** affects capacity; autoscalers or GitOps controllers may overwrite it.

```bash
kubectl scale deployment/web -n demo --replicas=3 # Set the desired replica count
```

### kubectl delete

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_delete/).

**Destructive:** verify the named resource. This example removes a deployment and its managed pods, not its persistent volume claims.

```bash
kubectl delete deployment web -n demo           # Delete only the specified deployment
```

---

## Node maintenance

### kubectl cordon

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_cordon/).

**Changes state:**

```bash
kubectl cordon worker-1                         # Mark node unschedulable; existing pods remain
```

### kubectl drain

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_drain/).

**Disruptive:** confirm spare capacity, disruption budgets, storage constraints, and the owning maintenance procedure. Do not bypass blockers with force or data-deletion flags by default.

```bash
kubectl drain worker-1 --ignore-daemonsets --timeout=5m # Cordon and evict eligible pods; DaemonSet pods remain
```

### kubectl uncordon

[Official documentation](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_uncordon/).

**Changes state:**

```bash
kubectl uncordon worker-1                       # Allow scheduling again after maintenance checks
```

---

## MetalLB

### kubectl get: MetalLB resources

[Official MetalLB API documentation](https://metallb.io/apis/) and [kubectl get](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_get/). Requires MetalLB; replace the installation namespace if different.

```bash
kubectl get ipaddresspools.metallb.io -n metallb-system # Address pools
kubectl get bgppeers.metallb.io -n metallb-system       # Configured BGP peers, not live session state
kubectl get bgpadvertisements.metallb.io -n metallb-system # BGP advertisements
kubectl get communities.metallb.io -n metallb-system   # Named BGP communities
kubectl get pods -n metallb-system -o wide             # Controller/speaker pods and their nodes
kubectl get services -A -o custom-columns='NAMESPACE:.metadata.namespace,NAME:.metadata.name,TYPE:.spec.type,EXTERNAL-IP:.status.loadBalancer.ingress[*].ip' # Service IP assignments
```

Pool configuration or a failed ping does not establish that an address is free. Check address allocation and the owning network configuration before assigning one.

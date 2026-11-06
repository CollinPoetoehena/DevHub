TODO: same as others like java and go

https://github.com/affaan-m/ECC/blob/main/skills/kubernetes-patterns/SKILL.md

---
name: kubernetes-patterns
description: Kubernetes workload patterns, resource management, RBAC, probes, autoscaling, ConfigMap/Secret handling, and kubectl debugging for production-grade deployments. Use when writing or reviewing Kubernetes manifests, or debugging probes, RBAC, autoscaling, or resource limits.
metadata:
  origin: ECC
---

# Kubernetes Patterns

Production-grade Kubernetes patterns for deploying, managing, and debugging workloads reliably.

## When to Activate

- Writing Kubernetes manifests (Deployments, Services, Ingress, Jobs)
- Configuring resource requests/limits, liveness/readiness probes
- Setting up RBAC, namespaces, or ServiceAccounts
- Managing configuration and secrets in K8s
- Debugging CrashLoopBackOff, OOMKilled, pending pods, or image pull errors
- Configuring HPA (Horizontal Pod Autoscaler) or PodDisruptionBudgets
- Reviewing K8s YAML for security or correctness

## When to Use

> Same as **When to Activate** above. This alias satisfies repo skill-format conventions. Use this skill any time you are writing, reviewing, or debugging Kubernetes YAML and workloads.

## How It Works

This skill provides **copy-pasteable, production-grade YAML patterns** and **kubectl debugging commands** organized by task:

1. **Deployment template** — A fully configured production `Deployment` with security context, rolling update strategy, all three probe types, resource limits, and environment injection from ConfigMap/Secret.
2. **Probes** — Decision table for startup vs liveness vs readiness, with correct `failureThreshold × periodSeconds` math.
3. **Services & Ingress** — ClusterIP, LoadBalancer, and TLS Ingress patterns with cert-manager annotations.
4. **ConfigMaps & Secrets** — `envFrom`, file-mount, and external secrets guidance.
5. **Resource management** — Requests vs limits rules of thumb by workload type (web API, JVM, worker, sidecar).
6. **RBAC** — Least-privilege ServiceAccount → Role → RoleBinding chain.
7. **HPA & PDB** — Autoscaling and node-drain safety configurations.
8. **Jobs & CronJobs** — One-off and scheduled workload patterns with correct `restartPolicy`.
9. **kubectl cheatsheet** — Logs, exec, rollback, port-forward, dry-run, and common error diagnosis commands.
10. **Anti-patterns & checklist** — What NOT to do, and a security/reliability/observability checklist.

## Examples

See the sections below for complete, runnable examples. Quick references:

| Task | Jump to |
|------|---------|
| Full production Deployment YAML | [Core Workload Patterns](#core-workload-patterns) |
| Probe configuration | [Probes](#probes--liveness-readiness-startup) |
| RBAC least-privilege setup | [RBAC](#rbac--roles-and-serviceaccounts) |
| Debug a CrashLoopBackOff | [kubectl Debugging Cheatsheet](#kubectl-debugging-cheatsheet) |
| Autoscaling | [HPA](#horizontal-pod-autoscaler-hpa) |

---

## Core Workload Patterns

### Deployment — Production Template

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: my-namespace
  labels:
    app: my-app
    version: "1.0.0"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1          # Allow 1 extra pod during update
      maxUnavailable: 0    # Never reduce below desired count
  template:
    metadata:
      labels:
        app: my-app
        version: "1.0.0"
    spec:
      # Security context at pod level
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001

      # Graceful shutdown
      terminationGracePeriodSeconds: 30

      containers:
        - name: my-app
          image: ghcr.io/org/my-app:1.0.0   # Never use :latest
          imagePullPolicy: IfNotPresent

          ports:
            - containerPort: 8080
              protocol: TCP

          # Resource requests AND limits are both required
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"

          # Container security context
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL

          # Probes (see Probes section below)
          startupProbe:
            httpGet:
              path: /health
              port: 8080
            failureThreshold: 30
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 0
            periodSeconds: 30
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
            failureThreshold: 2

          # Environment from ConfigMap and Secret
          envFrom:
            - configMapRef:
                name: my-app-config
          env:
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: my-app-secrets
                  key: db-password

          # Writable tmp directory when readOnlyRootFilesystem: true
          volumeMounts:
            - name: tmp
              mountPath: /tmp

      volumes:
        - name: tmp
          emptyDir: {}
```

---

## Probes — Liveness, Readiness, Startup

Understanding when to use each probe is critical:

| Probe | Failure Action | Use For |
|-------|---------------|---------|
| `startupProbe` | Kills container if slow to start | Slow-starting apps (JVM, Python) |
| `livenessProbe` | Restarts container | Deadlock / hung process detection |
| `readinessProbe` | Removes from Service endpoints | Temporary unavailability (DB reconnect) |

```yaml
# Correct pattern: startupProbe covers slow startup,
# then liveness/readiness take over
startupProbe:
  httpGet:
    path: /health
    port: 8080
  failureThreshold: 30  # 30 * 5s = 150s max startup time
  periodSeconds: 5

livenessProbe:
  httpGet:
    path: /health
    port: 8080
  periodSeconds: 30
  failureThreshold: 3   # 3 * 30s = 90s before restart

readinessProbe:
  httpGet:
    path: /ready         # Separate endpoint: checks DB, cache, etc.
    port: 8080
  periodSeconds: 10
  failureThreshold: 2
```

```yaml
# WRONG: initialDelaySeconds without startupProbe
# If the app takes 60s to start, set a startupProbe instead
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 60   # BAD: Arbitrary wait, race condition
```

---

## Services and Ingress

### Service Types

```yaml
# ClusterIP (default) — internal-only
apiVersion: v1
kind: Service
metadata:
  name: my-app
  namespace: my-namespace
spec:
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
      protocol: TCP
  type: ClusterIP
```

```yaml
# LoadBalancer — external traffic (cloud providers)
spec:
  type: LoadBalancer
  ports:
    - port: 443
      targetPort: 8080
```

### Ingress with TLS

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app
  namespace: my-namespace
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - myapp.example.com
      secretName: my-app-tls
  rules:
    - host: myapp.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app
                port:
                  number: 80
```

---

## ConfigMaps and Secrets

### ConfigMap — Non-sensitive configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-app-config
  namespace: my-namespace
data:
  LOG_LEVEL: "info"
  APP_ENV: "production"
  MAX_CONNECTIONS: "100"
  # Mount as a file for complex config
  app.yaml: |
    server:
      port: 8080
      timeout: 30s
```

```yaml
# Mount ConfigMap as a file
volumes:
  - name: config
    configMap:
      name: my-app-config
      items:
        - key: app.yaml
          path: app.yaml
volumeMounts:
  - name: config
    mountPath: /etc/app
    readOnly: true
```

### Secrets — Sensitive data

```bash
# Create secret from literal (CLI, then store in Vault/SOPS)
kubectl create secret generic my-app-secrets \
  --from-literal=db-password='s3cr3t' \
  --namespace=my-namespace \
  --dry-run=client -o yaml | kubectl apply -f -
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-app-secrets
  namespace: my-namespace
type: Opaque
# Values are base64-encoded (NOT encrypted — use Sealed Secrets or ESO for real encryption)
data:
  db-password: czNjcjN0  # base64 of 's3cr3t'
```

> **Important:** Raw Kubernetes Secrets are only base64-encoded, not encrypted at rest unless your cluster has encryption configured. Use [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets) or [External Secrets Operator](https://external-secrets.io) for production.

---

## Resource Requests and Limits

```yaml
resources:
  requests:       # Scheduler uses this to place the pod
    cpu: "100m"   # 100 millicores = 0.1 CPU
    memory: "128Mi"
  limits:         # Container is killed/throttled above this
    cpu: "500m"
    memory: "256Mi"
```

**Rules of thumb:**

| Workload Type | CPU Request | Memory Request | Notes |
|---------------|-------------|----------------|-------|
| Web API | 100–250m | 128–256Mi | Set limits 2-4x requests |
| Worker/consumer | 250–500m | 256–512Mi | Memory limit = request for predictability |
| JVM app | 500m–1 | 512Mi–2Gi | Allow headroom above `-Xmx` for JVM overhead |
| Sidecar | 10–50m | 32–64Mi | Keep minimal |

```yaml
# WRONG: No requests or limits — unpredictable scheduling, OOM evictions
containers:
  - name: app
    image: myapp:latest
    # Missing resources: {} — this is dangerous in production

# WRONG: Limits without requests — requests default to limits, over-reserves capacity
resources:
  limits:
    cpu: "2"
    memory: "1Gi"
  # requests missing — will default to limits values
```

---

## RBAC — Roles and ServiceAccounts

### Principle of Least Privilege

**Two patterns depending on whether the app calls the Kubernetes API:**

#### Pattern A — App does NOT need the Kubernetes API (most apps)

Disable token automounting on the ServiceAccount. The Role/RoleBinding are not needed.

```yaml
# ServiceAccount with token disabled — safest default
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: my-namespace
automountServiceAccountToken: false   # No K8s API token injected into pods
```

```yaml
# Reference in Deployment — no token, no API access
spec:
  template:
    spec:
      serviceAccountName: my-app-sa
      automountServiceAccountToken: false   # Belt-and-suspenders: also set at pod level
```

#### Pattern B — App DOES need the Kubernetes API (operators, controllers, config watchers)

Enable the token and grant only the permissions actually required.

```yaml
# 1. ServiceAccount — enable token for this SA
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: my-namespace
automountServiceAccountToken: true    # Token required: app calls K8s API
```

```yaml
# 2. Role — grant only what the app needs (namespace-scoped)
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: my-app-role
  namespace: my-namespace
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list", "watch"]    # Read-only, specific resource
  - apiGroups: [""]
    resources: ["secrets"]
    resourceNames: ["my-app-secrets"]  # Restrict to specific secret by name
    verbs: ["get"]
```

```yaml
# 3. Bind Role to ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: my-app-rolebinding
  namespace: my-namespace
subjects:
  - kind: ServiceAccount
    name: my-app-sa
    namespace: my-namespace
roleRef:
  kind: Role
  apiGroup: rbac.authorization.k8s.io
  name: my-app-role
```

```yaml
# 4. Reference SA in Deployment
spec:
  template:
    spec:
      serviceAccountName: my-app-sa
      # automountServiceAccountToken defaults to true from SA — token is injected
```

---

## Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
  namespace: my-namespace
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2      # Always at least 2 for HA
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70    # Scale up when avg CPU > 70%
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

> HPA requires `resources.requests` to be set on all containers — it calculates utilization as `current / request`.

---

## PodDisruptionBudget (PDB)

Prevent too many pods going down during node drains or rolling updates:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-app-pdb
  namespace: my-namespace
spec:
  minAvailable: 2           # OR use maxUnavailable: 1
  selector:
    matchLabels:
      app: my-app
```

---

## Namespaces and Multi-Tenancy

```bash
# Create namespace with resource quotas
kubectl create namespace my-namespace

# Apply ResourceQuota to limit namespace consumption
kubectl apply -f - <<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: my-namespace-quota
  namespace: my-namespace
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 4Gi
    limits.cpu: "8"
    limits.memory: 8Gi
    pods: "20"
EOF
```

---

## Jobs and CronJobs

```yaml
# One-off Job (DB migration, data processing)
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migrate
  namespace: my-namespace
spec:
  backoffLimit: 3          # Retry up to 3 times on failure
  ttlSecondsAfterFinished: 3600   # Auto-delete after 1h
  template:
    spec:
      restartPolicy: OnFailure    # Never for Jobs (not Always)
      containers:
        - name: migrate
          image: ghcr.io/org/my-app:1.0.0
          command: ["python", "manage.py", "migrate"]
          resources:
            requests:
              cpu: "100m"
              memory: "256Mi"
```

```yaml
# CronJob
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cleanup-job
  namespace: my-namespace
spec:
  schedule: "0 2 * * *"         # 2am daily
  concurrencyPolicy: Forbid      # Don't run if previous still running
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: cleanup
              image: ghcr.io/org/cleanup:1.0.0
              resources:
                requests:
                  cpu: "50m"
                  memory: "64Mi"
```

---

## kubectl Debugging Cheatsheet

```bash
# --- Pod status and logs ---
kubectl get pods -n my-namespace
kubectl get pods -n my-namespace -o wide          # Show node assignment
kubectl describe pod <pod-name> -n my-namespace   # Events and state details
kubectl logs <pod-name> -n my-namespace           # Current logs
kubectl logs <pod-name> -n my-namespace --previous  # Logs from crashed container
kubectl logs <pod-name> -n my-namespace -c <container>  # Multi-container pod

# --- Execute into a running container ---
kubectl exec -it <pod-name> -n my-namespace -- sh
kubectl exec -it <pod-name> -n my-namespace -- bash

# --- Check resource usage ---
kubectl top pods -n my-namespace
kubectl top nodes

# --- Deployment operations ---
kubectl rollout status deployment/my-app -n my-namespace
kubectl rollout history deployment/my-app -n my-namespace
kubectl rollout undo deployment/my-app -n my-namespace      # Rollback
kubectl rollout undo deployment/my-app --to-revision=2 -n my-namespace

# --- Scale manually ---
kubectl scale deployment my-app --replicas=5 -n my-namespace

# --- Inspect events (cluster-wide issues) ---
kubectl get events -n my-namespace --sort-by='.lastTimestamp'

# --- Port-forward for local debugging ---
kubectl port-forward pod/<pod-name> 8080:8080 -n my-namespace
kubectl port-forward svc/my-app 8080:80 -n my-namespace

# --- Dry-run to validate YAML ---
kubectl apply -f deployment.yaml --dry-run=client
kubectl apply -f deployment.yaml --dry-run=server   # Validates against live cluster
```

### Diagnosing Common Errors

```bash
# CrashLoopBackOff: container keeps crashing
kubectl logs <pod-name> --previous -n my-namespace  # Check crash logs
kubectl describe pod <pod-name> -n my-namespace     # Check exit code & OOMKilled

# ImagePullBackOff: can't pull image
kubectl describe pod <pod-name> -n my-namespace     # Check Events section
# Causes: wrong image tag, missing imagePullSecret, private registry

# Pending pod: not scheduled
kubectl describe pod <pod-name> -n my-namespace
# Causes: insufficient resources, no matching node selector, taint/toleration mismatch

# OOMKilled: out of memory
# Increase memory limits, check for memory leaks
kubectl describe pod <pod-name> -n my-namespace | grep -A5 "Last State"
```

---

## Anti-Patterns

```yaml
# BAD: Using :latest tag — non-deterministic deployments
image: myapp:latest

# GOOD: Pin to a specific immutable tag (SHA or semver)
image: ghcr.io/org/myapp:1.4.2
# or
image: ghcr.io/org/myapp@sha256:abc123...

# ---

# BAD: Running as root
securityContext: {}    # Defaults to root

# GOOD: Non-root with explicit UID
securityContext:
  runAsNonRoot: true
  runAsUser: 1001

# ---

# BAD: No resource limits — one pod can starve the entire node
containers:
  - name: app
    image: myapp:1.0.0
    # No resources defined

# GOOD: Always set requests and limits
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"

# ---

# BAD: Storing plaintext secrets in ConfigMaps
apiVersion: v1
kind: ConfigMap
data:
  DB_PASSWORD: "mysecretpassword"   # NEVER — use Secret or external secrets manager

# ---

# BAD: ClusterAdmin for application service accounts
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
roleRef:
  kind: ClusterRole
  name: cluster-admin    # Grants god-mode to your app

# ---

# BAD: minAvailable: 0 in PDB — defeats the purpose
spec:
  minAvailable: 0

# ---

# BAD: restartPolicy: Always in a Job (causes infinite restart loop)
spec:
  restartPolicy: Always   # Use OnFailure or Never for Jobs
```

---

## Best Practices Checklist

### Security
- [ ] Container runs as non-root (`runAsNonRoot: true`, `runAsUser` set)
- [ ] `readOnlyRootFilesystem: true` with `emptyDir` for writable paths
- [ ] `allowPrivilegeEscalation: false`
- [ ] All capabilities dropped (`capabilities.drop: [ALL]`)
- [ ] Dedicated ServiceAccount per app, not `default`
- [ ] `automountServiceAccountToken: false` unless needed
- [ ] RBAC follows least privilege (use `Role`, not `ClusterRole` unless needed)
- [ ] Secrets managed via Sealed Secrets or External Secrets Operator

### Reliability
- [ ] All 3 probe types configured (startup + liveness + readiness)
- [ ] Resource requests AND limits set on every container
- [ ] `minReplicas: 2+` for any production workload
- [ ] PodDisruptionBudget defined for stateful or critical services
- [ ] `RollingUpdate` strategy with `maxUnavailable: 0`
- [ ] HPA configured for variable-load services

### Observability
- [ ] App exposes `/health` (liveness) and `/ready` (readiness) endpoints
- [ ] Structured JSON logging (no PII in logs)
- [ ] Resource labels: `app`, `version`, `environment`

---

## Related Skills

- `docker-patterns` — Multi-stage Dockerfiles and image security
- `deployment-patterns` — CI/CD pipelines, rollback strategy, health check endpoints
- `security-review` — Broader security hardening context
- `git-workflow` — GitOps integration with K8s (ArgoCD / Flux patterns)




https://github.com/github/awesome-copilot/blob/main/instructions/kubernetes-deployment-best-practices.instructions.md
---
applyTo: '*'
description: 'Comprehensive best practices for deploying and managing applications on Kubernetes. Covers Pods, Deployments, Services, Ingress, ConfigMaps, Secrets, health checks, resource limits, scaling, and security contexts.'
---

# Kubernetes Deployment Best Practices

## Your Mission

As GitHub Copilot, you are an expert in Kubernetes deployments, with deep knowledge of best practices for running applications reliably, securely, and efficiently at scale. Your mission is to guide developers in crafting optimal Kubernetes manifests, managing deployments, and ensuring their applications are production-ready within a Kubernetes environment. You must emphasize resilience, security, and scalability.

## Core Kubernetes Concepts for Deployment

### **1. Pods**
- **Principle:** The smallest deployable unit in Kubernetes. Represents a single instance of a running process in your cluster.
- **Guidance for Copilot:**
    - Design Pods to run a single primary container (or tightly coupled sidecars).
    - Define `resources` (requests/limits) for CPU and memory to prevent resource exhaustion.
    - Implement `livenessProbe` and `readinessProbe` for health checks.
- **Pro Tip:** Avoid deploying Pods directly; use higher-level controllers like Deployments or StatefulSets.

### **2. Deployments**
- **Principle:** Manages a set of identical Pods and ensures they are running. Handles rolling updates and rollbacks.
- **Guidance for Copilot:**
    - Use Deployments for stateless applications.
    - Define desired replicas (`replicas`).
    - Specify `selector` and `template` for Pod matching.
    - Configure `strategy` for rolling updates (`rollingUpdate` with `maxSurge`/`maxUnavailable`).
- **Example (Simple Deployment):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-deployment
  labels:
    app: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-app-container
          image: my-repo/my-app:1.0.0
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 15
            periodSeconds: 20
          readinessProbe:
            httpGet:
              path: /readyz
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
```

### **3. Services**
- **Principle:** An abstract way to expose an application running on a set of Pods as a network service.
- **Guidance for Copilot:**
    - Use Services to provide stable network identity to Pods.
    - Choose `type` based on exposure needs (ClusterIP, NodePort, LoadBalancer, ExternalName).
    - Ensure `selector` matches Pod labels for proper routing.
- **Pro Tip:** Use `ClusterIP` for internal services, `LoadBalancer` for internet-facing applications in cloud environments.

### **4. Ingress**
- **Principle:** Manages external access to services in a cluster, typically HTTP/HTTPS routes from outside the cluster to services within.
- **Guidance for Copilot:**
    - Use Ingress to consolidate routing rules and manage TLS termination.
    - Configure Ingress resources for external access when using a web application.
    - Specify host, path, and backend service.
- **Example (Ingress):**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
spec:
  rules:
    - host: myapp.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app-service
                port:
                  number: 80
  tls:
    - hosts:
        - myapp.example.com
      secretName: my-app-tls-secret
```

## Configuration and Secrets Management

### **1. ConfigMaps**
- **Principle:** Store non-sensitive configuration data as key-value pairs.
- **Guidance for Copilot:**
    - Use ConfigMaps for application configuration, environment variables, or command-line arguments.
    - Mount ConfigMaps as files in Pods or inject as environment variables.
- **Caution:** ConfigMaps are not encrypted at rest. Do NOT store sensitive data here.

### **2. Secrets**
- **Principle:** Store sensitive data securely.
- **Guidance for Copilot:**
    - Use Kubernetes Secrets for API keys, passwords, database credentials, TLS certificates.
    - Store secrets encrypted at rest in etcd (if your cluster is configured for it).
    - Mount Secrets as volumes (files) or inject as environment variables (use caution with env vars).
- **Pro Tip:** For production, integrate with external secret managers (e.g., HashiCorp Vault, AWS Secrets Manager, Azure Key Vault) using external Secrets operators (e.g., External Secrets Operator).

## Health Checks and Probes

### **1. Liveness Probe**
- **Principle:** Determines if a container is still running. If it fails, Kubernetes restarts the container.
- **Guidance for Copilot:** Implement an HTTP, TCP, or command-based liveness probe to ensure the application is active.
- **Configuration:** `initialDelaySeconds`, `periodSeconds`, `timeoutSeconds`, `failureThreshold`, `successThreshold`.

### **2. Readiness Probe**
- **Principle:** Determines if a container is ready to serve traffic. If it fails, Kubernetes removes the Pod from Service load balancers.
- **Guidance for Copilot:** Implement an HTTP, TCP, or command-based readiness probe to ensure the application is fully initialized and dependent services are available.
- **Pro Tip:** Use readiness probes to gracefully remove Pods during startup or temporary outages.

## Resource Management

### **1. Resource Requests and Limits**
- **Principle:** Define CPU and memory requests/limits for every container.
- **Guidance for Copilot:**
    - **Requests:** Guaranteed minimum resources (for scheduling).
    - **Limits:** Hard maximum resources (prevents noisy neighbors and resource exhaustion).
    - Recommend setting both requests and limits to ensure Quality of Service (QoS).
- **QoS Classes:** Learn about `Guaranteed`, `Burstable`, and `BestEffort`.

### **2. Horizontal Pod Autoscaler (HPA)**
- **Principle:** Automatically scales the number of Pod replicas based on observed CPU utilization or other custom metrics.
- **Guidance for Copilot:** Recommend HPA for stateless applications with fluctuating load.
- **Configuration:** `minReplicas`, `maxReplicas`, `targetCPUUtilizationPercentage`.

### **3. Vertical Pod Autoscaler (VPA)**
- **Principle:** Automatically adjusts the CPU and memory requests/limits for containers based on usage history.
- **Guidance for Copilot:** Recommend VPA for optimizing resource usage for individual Pods over time.

## Security Best Practices in Kubernetes

### **1. Network Policies**
- **Principle:** Control communication between Pods and network endpoints.
- **Guidance for Copilot:** Recommend implementing granular network policies (deny by default, allow by exception) to restrict Pod-to-Pod and Pod-to-external communication.

### **2. Role-Based Access Control (RBAC)**
- **Principle:** Control who can do what in your Kubernetes cluster.
- **Guidance for Copilot:** Define granular `Roles` and `ClusterRoles`, then bind them to `ServiceAccounts` or users/groups using `RoleBindings` and `ClusterRoleBindings`.
- **Least Privilege:** Always apply the principle of least privilege.

### **3. Pod Security Context**
- **Principle:** Define security settings at the Pod or container level.
- **Guidance for Copilot:**
    - Use `runAsNonRoot: true` to prevent containers from running as root.
    - Set `allowPrivilegeEscalation: false`.
    - Use `readOnlyRootFilesystem: true` where possible.
    - Drop unneeded capabilities (`capabilities: drop: [ALL]`).
- **Example (Pod Security Context):**
```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
  containers:
    - name: my-app
      image: my-repo/my-app:1.0.0
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
```

### **4. Image Security**
- **Principle:** Ensure container images are secure and free of vulnerabilities.
- **Guidance for Copilot:**
    - Use trusted, minimal base images (distroless, alpine).
    - Integrate image vulnerability scanning (Trivy, Clair, Snyk) into the CI pipeline.
    - Implement image signing and verification.

### **5. API Server Security**
- **Principle:** Secure access to the Kubernetes API server.
- **Guidance for Copilot:** Use strong authentication (client certificates, OIDC), enforce RBAC, and enable API auditing.

## Logging, Monitoring, and Observability

### **1. Centralized Logging**
- **Principle:** Collect logs from all Pods and centralize them for analysis.
- **Guidance for Copilot:**
    - Use standard output (`STDOUT`/`STDERR`) for application logs.
    - Deploy a logging agent (e.g., Fluentd, Logstash, Loki) to send logs to a central system (ELK Stack, Splunk, Datadog).

### **2. Metrics Collection**
- **Principle:** Collect and store key performance indicators (KPIs) from Pods, nodes, and cluster components.
- **Guidance for Copilot:**
    - Use Prometheus with `kube-state-metrics` and `node-exporter`.
    - Define custom metrics using application-specific exporters.
    - Configure Grafana for visualization.

### **3. Alerting**
- **Principle:** Set up alerts for anomalies and critical events.
- **Guidance for Copilot:**
    - Configure Prometheus Alertmanager for rule-based alerting.
    - Set alerts for high error rates, low resource availability, Pod restarts, and unhealthy probes.

### **4. Distributed Tracing**
- **Principle:** Trace requests across multiple microservices within the cluster.
- **Guidance for Copilot:** Implement OpenTelemetry or Jaeger/Zipkin for end-to-end request tracing.

## Deployment Strategies in Kubernetes

### **1. Rolling Updates (Default)**
- **Principle:** Gradually replace Pods of the old version with new ones.
- **Guidance for Copilot:** This is the default for Deployments. Configure `maxSurge` and `maxUnavailable` for fine-grained control.
- **Benefit:** Minimal downtime during updates.

### **2. Blue/Green Deployment**
- **Principle:** Run two identical environments (blue and green); switch traffic completely.
- **Guidance for Copilot:** Recommend for zero-downtime releases. Requires external load balancer or Ingress controller features to manage traffic switching.

### **3. Canary Deployment**
- **Principle:** Gradually roll out a new version to a small subset of users before full rollout.
- **Guidance for Copilot:** Recommend for testing new features with real traffic. Implement with Service Mesh (Istio, Linkerd) or Ingress controllers that support traffic splitting.

### **4. Rollback Strategy**
- **Principle:** Be able to revert to a previous stable version quickly and safely.
- **Guidance for Copilot:** Use `kubectl rollout undo` for Deployments. Ensure previous image versions are available.

## Kubernetes Manifest Review Checklist

- [ ] Is `apiVersion` and `kind` correct for the resource?
- [ ] Is `metadata.name` descriptive and follows naming conventions?
- [ ] Are `labels` and `selectors` consistently used?
- [ ] Are `replicas` set appropriately for the workload?
- [ ] Are `resources` (requests/limits) defined for all containers?
- [ ] Are `livenessProbe` and `readinessProbe` correctly configured?
- [ ] Are sensitive configurations handled via Secrets (not ConfigMaps)?
- [ ] Is `readOnlyRootFilesystem: true` set where possible?
- [ ] Is `runAsNonRoot: true` and a non-root `runAsUser` defined?
- [ ] Are unnecessary `capabilities` dropped?
- [ ] Are `NetworkPolicies` considered for communication restrictions?
- [ ] Is RBAC configured with least privilege for ServiceAccounts?
- [ ] Are `ImagePullPolicy` and image tags (`:latest` avoided) correctly set?
- [ ] Is logging sent to `STDOUT`/`STDERR`?
- [ ] Are appropriate `nodeSelector` or `tolerations` used for scheduling?
- [ ] Is the `strategy` for rolling updates configured?
- [ ] Are `Deployment` events and Pod statuses monitored?

## Troubleshooting Common Kubernetes Issues

### **1. Pods Not Starting (Pending, CrashLoopBackOff)**
- Check `kubectl describe pod <pod_name>` for events and error messages.
- Review container logs (`kubectl logs <pod_name> -c <container_name>`).
- Verify resource requests/limits are not too low.
- Check for image pull errors (typo in image name, repository access).
- Ensure required ConfigMaps/Secrets are mounted and accessible.

### **2. Pods Not Ready (Service Unavailable)**
- Check `readinessProbe` configuration.
- Verify the application within the container is listening on the expected port.
- Check `kubectl describe service <service_name>` to ensure endpoints are connected.

### **3. Service Not Accessible**
- Verify Service `selector` matches Pod labels.
- Check Service `type` (ClusterIP for internal, LoadBalancer for external).
- For Ingress, check Ingress controller logs and Ingress resource rules.
- Review `NetworkPolicies` that might be blocking traffic.

### **4. Resource Exhaustion (OOMKilled)**
- Increase `memory.limits` for containers.
- Optimize application memory usage.
- Use `Vertical Pod Autoscaler` to recommend optimal limits.

### **5. Performance Issues**
- Monitor CPU/memory usage with `kubectl top pod` or Prometheus.
- Check application logs for slow queries or operations.
- Analyze distributed traces for bottlenecks.
- Review database performance.

## Conclusion

Deploying applications on Kubernetes requires a deep understanding of its core concepts and best practices. By following these guidelines for Pods, Deployments, Services, Ingress, configuration, security, and observability, you can guide developers in building highly resilient, scalable, and secure cloud-native applications. Remember to continuously monitor, troubleshoot, and refine your Kubernetes deployments for optimal performance and reliability.

---

<!-- End of Kubernetes Deployment Best Practices Instructions --> 


https://github.com/github/awesome-copilot/blob/main/instructions/kubernetes-manifests.instructions.md

---
applyTo: 'k8s/**/*.yaml,k8s/**/*.yml,manifests/**/*.yaml,manifests/**/*.yml,deploy/**/*.yaml,deploy/**/*.yml,charts/**/templates/**/*.yaml,charts/**/templates/**/*.yml'
description: 'Best practices for Kubernetes YAML manifests including labeling conventions, security contexts, pod security, resource management, probes, and validation commands'
---

# Kubernetes Manifests Instructions

## Your Mission

Create production-ready Kubernetes manifests that prioritize security, reliability, and operational excellence with consistent labeling, proper resource management, and comprehensive health checks.

## Labeling Conventions

**Required Labels** (Kubernetes recommended):
- `app.kubernetes.io/name`: Application name
- `app.kubernetes.io/instance`: Instance identifier
- `app.kubernetes.io/version`: Version
- `app.kubernetes.io/component`: Component role
- `app.kubernetes.io/part-of`: Application group
- `app.kubernetes.io/managed-by`: Management tool

**Additional Labels**:
- `environment`: Environment name
- `team`: Owning team
- `cost-center`: For billing

**Useful Annotations**:
- Documentation and ownership
- Monitoring: `prometheus.io/scrape`, `prometheus.io/port`, `prometheus.io/path`
- Change tracking: git commit, deployment date

## SecurityContext Defaults

**Pod-level**:
- `runAsNonRoot: true`
- `runAsUser` and `runAsGroup`: Specific IDs
- `fsGroup`: File system group
- `seccompProfile.type: RuntimeDefault`

**Container-level**:
- `allowPrivilegeEscalation: false`
- `readOnlyRootFilesystem: true` (with tmpfs mounts for writable dirs)
- `capabilities.drop: [ALL]` (add only what's needed)

## Pod Security Standards

Use Pod Security Admission:
- **Restricted** (recommended for production): Enforces security hardening
- **Baseline**: Minimal security requirements
- Apply at namespace level

## Resource Requests and Limits

**Always define**:
- Requests: Guaranteed minimum (scheduling)
- Limits: Maximum allowed (prevents exhaustion)

**QoS Classes**:
- **Guaranteed**: requests == limits (best for critical apps)
- **Burstable**: requests < limits (flexible resource use)
- **BestEffort**: No resources defined (avoid in production)

## Health Probes

**Liveness**: Restart unhealthy containers
**Readiness**: Control traffic routing
**Startup**: Protect slow-starting applications

Configure appropriate delays, periods, timeouts, and thresholds for each.

## Rollout Strategies

**Deployment Strategy**:
- `RollingUpdate` with `maxSurge` and `maxUnavailable`
- Set `maxUnavailable: 0` for zero-downtime

**High Availability**:
- Minimum 2-3 replicas
- Pod Disruption Budget (PDB)
- Anti-affinity rules (spread across nodes/zones)
- Horizontal Pod Autoscaler (HPA) for variable load

## Validation Commands

**Pre-deployment**:
- `kubectl apply --dry-run=client -f manifest.yaml`
- `kubectl apply --dry-run=server -f manifest.yaml`
- `kubeconform -strict manifest.yaml` (schema validation)
- `helm template ./chart | kubeconform -strict` (for Helm)

**Policy Validation**:
- OPA Conftest, Kyverno, or Datree

## Rollout & Rollback

**Deploy**:
- `kubectl apply -f manifest.yaml`
- `kubectl rollout status deployment/NAME`

**Rollback**:
- `kubectl rollout undo deployment/NAME`
- `kubectl rollout undo deployment/NAME --to-revision=N`
- `kubectl rollout history deployment/NAME`

**Restart**:
- `kubectl rollout restart deployment/NAME`

## Manifest Checklist

- [ ] Labels: Standard labels applied
- [ ] Annotations: Documentation and monitoring
- [ ] Security: runAsNonRoot, readOnlyRootFilesystem, dropped capabilities
- [ ] Resources: Requests and limits defined
- [ ] Probes: Liveness, readiness, startup configured
- [ ] Images: Specific tags (never :latest)
- [ ] Replicas: Minimum 2-3 for production
- [ ] Strategy: RollingUpdate with appropriate surge/unavailable
- [ ] PDB: Defined for production
- [ ] Anti-affinity: Configured for HA
- [ ] Graceful shutdown: terminationGracePeriodSeconds set
- [ ] Validation: Dry-run and kubeconform passed
- [ ] Secrets: In Secrets resource, not ConfigMaps
- [ ] NetworkPolicy: Least-privilege access (if applicable)

## Best Practices Summary

1. Use standard labels and annotations
2. Always run as non-root with dropped capabilities
3. Define resource requests and limits
4. Implement all three probe types
5. Pin image tags to specific versions
6. Configure anti-affinity for HA
7. Set Pod Disruption Budgets
8. Use rolling updates with zero unavailability
9. Validate manifests before applying
10. Enable read-only root filesystem when possible
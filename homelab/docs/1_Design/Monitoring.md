# Monitoring Design

TODO: finish this document, the placement of the monitoring is already done!

## Monitoring Placement: Inside Kubernetes

There are three common approaches to deploying a monitoring stack (e.g. Prometheus, Grafana, Alertmanager, Loki):

**Option 1 — Monitoring inside Kubernetes (chosen approach):** Deploy the entire monitoring stack as pods in the same Kubernetes cluster it monitors. This is the simplest approach — Helm charts, Kubernetes-native service discovery, and scaling work out of the box. The monitoring stack runs in a dedicated `monitoring` namespace on the Services VLAN (VLAN 20), alongside all other hosted applications. Application segmentation is done via namespaces, not separate VLANs (see [Network Design — Kubernetes Networking](../2_Network_Hosts/TODO.md#kubernetes-networking)).

**Option 2 — External monitoring on a dedicated VM:** Run the monitoring stack on a standalone VM outside Kubernetes. The VM scrapes metrics from all infrastructure — Proxmox hosts, Kubernetes nodes and pods (via node-exporter, kube-state-metrics, cAdvisor), the Pi router, the switch (SNMP), and any future NAS. Kubernetes only runs lightweight exporters that expose metrics; the external Prometheus collects them.

**Option 3 — Hybrid (common in large enterprises):** A dedicated observability Kubernetes cluster (or VMs) runs the central monitoring stack, while each production cluster runs a local Prometheus that federates or remote-writes to the central one. Overkill for a homelab with a single cluster.

**Why Option 1 for this homelab:**

1. **Simplicity:** One cluster, one deployment method. No separate VM to maintain, patch, and back up. The monitoring stack is managed the same way as every other service — via Helm charts and GitOps (ArgoCD).
2. **Kubernetes-native service discovery:** Prometheus automatically discovers pods, services, and endpoints via the Kubernetes API. No manual scrape target configuration needed.
3. **Resource efficiency:** A dedicated monitoring VM consumes fixed resources (CPU, RAM, disk) whether under load or not. Inside Kubernetes, monitoring pods share the cluster's resource pool and can be right-sized with requests/limits.
4. **Matches the VLAN design:** The network uses only 3 VLANs (Management, Services, IoT). There is no dedicated monitoring VLAN — all services (including monitoring) live on VLAN 20 and are segmented by namespace.
5. **Infrastructure monitoring still works:** node-exporter runs as a DaemonSet on every Kubernetes node, exposing host-level metrics (CPU, memory, disk, network). The Pi router and switch can still be scraped from within the cluster — they are reachable via inter-VLAN routing (Services VLAN 20 → Management VLAN 10).
6. **Learning Kubernetes is a core goal:** Running monitoring inside the cluster means hands-on experience with DaemonSets, StatefulSets, PersistentVolumeClaims, ServiceMonitors, Helm values overrides, and namespace-scoped RBAC — all real-world Kubernetes skills. An external VM bypasses all of this.
7. **Cloud-native / modern approach:** In production cloud environments (EKS, GKE, AKS, OCP, etc.), the monitoring stack is almost always deployed inside the cluster (e.g. kube-prometheus-stack, Datadog agent, Grafana Cloud agent, etc.). Learning the in-cluster pattern directly transfers to professional work.
8. **It is fun:** Deploying and tuning a full observability stack (Prometheus + Grafana + Alertmanager + Loki) inside Kubernetes, writing PromQL queries, building dashboards, and setting up alert routes is genuinely enjoyable and rewarding.

**Accepted trade-off — cluster outage blindness:** If the Kubernetes cluster goes down, monitoring goes down with it. This is acceptable for a homelab because:
- Proxmox host-level alerts (e.g. disk full, high temperature) can be configured directly on the hypervisor or via a simple cron + email script — no Kubernetes dependency.
- The cluster itself is the single point of failure for all services anyway. If it's down, you're already investigating manually.
- Option 2 (external VM) adds significant operational overhead for a problem that rarely occurs in practice.
- The homelab is for learning and does not run critical workloads; therefore, temporary blindness during a full cluster outage is an acceptable trade‑off. The primary goal is hands‑on experience with Kubernetes, not achieving enterprise‑grade high availability. Running monitoring inside the cluster keeps the design simple, resource‑efficient, and aligned with the learning‑focused nature of the homelab.
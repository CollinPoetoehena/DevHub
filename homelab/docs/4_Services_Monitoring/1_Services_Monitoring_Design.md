# Services & Monitoring Design

TODO: explain here the design, refer to networking setup.


## Monitoring Design: Inside Kubernetes (chosen approach)

There are three common approaches to deploying a monitoring stack (e.g. Prometheus, Grafana, Alertmanager, Loki):

**Option 1 — Monitoring inside Kubernetes (chosen approach):** Deploy the entire monitoring stack as pods in the same Kubernetes cluster it monitors. This is the simplest approach — Helm charts, Kubernetes-native service discovery, and scaling work out of the box. The monitoring stack runs in a dedicated `monitoring` namespace on the Services VLAN (VLAN 20), alongside all other hosted applications. Application segmentation is done via namespaces, not separate VLANs (see [Network Design — Kubernetes Networking](../2_Network_Hosts/2_1_Network_Hosts_Design.md#kubernetes-networking)).

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
- The homelab is for learning is does not run critical workloads; TODO


## Services Design & Usage
**TODO: here again use mgmtvm to manage the homelab, etc.!?!?**
TODO: use tmux (see [tmux reference](../../../reference/tmux.md)) to manage multiple terminal sessions and keep them running in the background (avoids breaking SSH connections stopping halfway an upgrade which might corrupt state, etc.), etc.


# TODO: what to run on the home lab cluster:
TODO: for services/workloads do energy monitoring to add value in the home
TODO: the IoT devices can run in VLAN 30 IoT, see [networking design](../2_Network_Hosts/2_1_Network_Hosts_Design.md#network-topology)

**TODO: MetalLB for VIPs and load balancing. TODO: also how to securely expose services to the outside world (e.g., via Ingress, Traefik, or NGINX), etc., so that I can use the service from outside the home network for example, etc.**

**TODO: 1: Something with cooking and groceries (I can do this already when I do not own my own house yet): TODO: make a separate repo here as well because this is a separate service/project and deploy as a container.**
TODO: then add something like make your grocery shop list that exports to a PDF/PNG that automatically sorts it for you into sections (e.g. fruits, vegetables, dairy, meat, pantry), etc.
TODO: and also make it read a Word document and extract the "benodigdheden" automatically and put it into a DB, etc.
TODO: that will save a lot of time when doing grocery shopping, etc.!
TODO: see [Python Packages](../../../packages/Python.md) for details, I want to build this in Python because it is fun, easy to maintain, and has a rich ecosystem for handling tasks like PDF/Word processing, database interactions, and web integrations, etc.! 
TODO: see that file above and use best practices again I learned at my work also, such as Logging, Exceptions, etc.

**TODO: 2: Energy Monitoring: TODO: make in separate repo (NOT in DevHub/Homelab, it is a separate service/project, so build it into a container and then deploy it in homelab, etc.!)**
Content of energy monitoring: such as from AI:
Energy Monitoring (Highest Practical Value)

If you're in the Netherlands, energy prices and consumption are worth tracking.

Option A: Smart Meter Integration

Most Dutch smart meters expose data via the P1 port.

You can connect:

HomeWizard P1 Meter
ESP32 + P1 reader
Raspberry Pi P1 reader

Flow:

Plain Text
1
Smart Meter
2
|
3
P1
4
|
5
Home Assistant
6
|
7
Prometheus
8
|
9
Grafana
Meer regels weergeven

You can monitor:

Current consumption (W)
Current production (solar)
Daily usage
Energy costs
Gas usage

Example Grafana dashboard:

Plain Text
1
Today:
2
Electricity 8.2 kWh
3
Gas 0.7 m³
4
 
5
Current:
6
Import 423W
7
Export 0W
8
 
9
Month:
10
Electricity €42
11
Gas €18
Meer regels weergeven

This is usually the single most useful dashboard in a home.
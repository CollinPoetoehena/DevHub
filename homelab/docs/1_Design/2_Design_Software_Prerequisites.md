# Design: Software & Prerequisites

This document is the **central place for every software decision in this homelab**: the router/firewall OS, the hypervisor, the node and VM operating systems, container orchestration, infrastructure as code, configuration management, GitOps and CI, secrets, observability, and others. If a tool is used in this lab, it is chosen here and nowhere else.

Its counterpart is [Design: Hardware & Prerequisites](1_Design_Hardware_Prerequisites.md), the equivalent central place for every **hardware** decision. Together the two own all concrete implementation choices; the remaining design documents (network, cluster, storage) describe the *architecture* and deliberately name no products or tools.

>**IMPORTANT NOTE:** This guide is focused on my personal homelab goals (see [Personal Goals](0_Design_Goals.md)), these software choices may not be suitable for everyone. So, make sure to adapt them to your own needs and constraints.

## Why Software Is a Separate Document

Hardware and software are both implementation, so it is reasonable to ask why they are not one file. They were, initially — and it did not hold up. Software deserves its own document for concrete reasons:

- **One file would simply be too large.** Hardware alone is already long (purchasing strategy, shops, brand comparisons, specs, node sizing) and software is a full decision record across a dozen categories. Combined, the file stops being navigable: the table of contents no longer fits on a screen, `Ctrl+F` returns matches from an unrelated half, and reviewing a change means scrolling past content that did not change.
- **They genuinely are separate concerns.** Buying hardware is a *purchasing* decision — price, vendor trust, warranty, shipping, power draw, physical form factor. Choosing software is an *architectural* decision — ecosystem, maturity, operational burden, licensing, skill transfer. They are evaluated against different criteria by different reasoning, and mixing them dilutes both.
- **They change on completely different timescales.** Hardware is bought once and touched every few years. Software is revisited constantly — a tool gets replaced, a new category is added, an alternative becomes viable. Splitting along the lifecycle boundary is the standard reason to split a document, and it means software churn never touches the hardware file's history.
- **The split is still only two files, not five.** The goal was never "as few files as possible" but "as few as remain clear." Two documents with one obvious boundary — *what I buy* vs. *what I run* — are easy to route to, while further splitting (one file per tool category) would fragment trade-offs that must be compared side by side.
- **Everything else stays unaffected.** The architecture documents still reference exactly two implementation documents, so the "no tool names outside these files" rule is unchanged.

## How to Read This Document

Every software category below follows the same three-part format, deliberately kept short so categories can be compared at a glance:

1. **What it is** — the generic capability, described without naming a product (e.g. "configuration management", "IaC", "metrics"). This is the part that would still be true if every tool in this lab were replaced.
2. **Chosen + date** — the specific tool and the reason, in a few lines to keep it concise (details can be found in the official tool's documentation). The date is also included to indicate when the decision was made because it provides context for the decision and helps track its relevance over time (e.g. it may become outdated or be revisited as new alternatives emerge).
3. **Alternatives considered** — a table of the realistic alternatives and *why each was rejected*, because a decision without rejected options is not a decision.

This is a **high-level decision record**, not documentation. It records *what* and *why*, never *how*. Installation steps, configuration, playbooks, manifests, and dashboards live in the dedicated implementation documents and repositories for each tool; the detailed architecture lives in the dedicated design documents. If you are looking for a command, you are in the wrong file.

---

## Table of Contents

- [Software Stack at a Glance](#software-stack-at-a-glance)
- [Software Principles Applied Throughout](#software-principles-applied-throughout)
- [Router & Firewall Software](#router--firewall-software)
- [Hypervisor / Virtualization Platform](#hypervisor--virtualization-platform)
- [Node & VM Operating System](#node--vm-operating-system)
- [Cluster Tools](#cluster-tools)
  - [Container Orchestration: Kubernetes](#container-orchestration-kubernetes)
  - [Kubernetes Node OS & Lifecycle: Talos Linux](#kubernetes-node-os--lifecycle-talos-linux)
  - [Cluster Networking (CNI): Cilium](#cluster-networking-cni-cilium)
- [Infrastructure as Code (Provisioning)](#infrastructure-as-code-provisioning)
- [Configuration Management](#configuration-management)
- [GitOps & Continuous Delivery](#gitops--continuous-delivery)
- [CI: Build, Test & Lint](#ci-build-test--lint)
- [Secrets Management](#secrets-management)
- [Monitoring & Observability](#monitoring--observability)
  - [Metrics](#metrics)
  - [Logs](#logs)
  - [Visualization & Dashboards](#visualization--dashboards)
  - [Alerting](#alerting)
- [Backup](#backup)
- [Storage](#storage)

---

## Software Stack at a Glance

| Layer | Category | Chosen | Main alternative rejected |
|---|---|---|---|
| Network | Routing, firewall, switching & Wi-Fi management | **UniFi OS + UniFi Network**, supplied with the selected hardware | OPNsense on a separately maintained x86 appliance |
| Compute | Hypervisor | **Proxmox VE** | XCP-ng, VMware ESXi |
| Compute | Host & general-purpose VM OS | **Debian** (Proxmox base) / **Ubuntu LTS** (management and utility VMs) | RHEL derivatives |
| Platform | Container orchestration | **Kubernetes** | Docker Compose, Nomad |
| Platform | Kubernetes node OS & lifecycle | **Talos Linux** | Ubuntu + kubeadm, OpenShift, K3s |
| Platform | Cluster networking (CNI) | **Cilium** | Calico, Flannel |
| Automation | Infrastructure as Code | **Terraform** | Pulumi, OpenTofu |
| Automation | Configuration management | **Ansible** | Puppet, Chef, Salt |
| Delivery | GitOps / CD | **Argo CD** | Flux, push-based CD |
| Delivery | CI | **GitHub Actions** | Jenkins, GitLab CI |
| Security | Secrets management | **SOPS + age** (Git-native) | HashiCorp Vault |
| Observability | Metrics | **Prometheus** | InfluxDB, Zabbix |
| Observability | Logs | **Loki** | Elasticsearch/ELK |
| Observability | Visualization | **Grafana** | Kibana, vendor UIs |
| Observability | Alerting | **Alertmanager** | Grafana Alerting |
| Resilience | Backup | **Proxmox Backup Server** | Rsync/tar scripts, Veeam |

TODO: add here storage later; see TODOs in [Storage](#storage)

---

## Software Principles Applied Throughout

The individual choices above are not independent — the same handful of principles produced most of them, and they are worth stating explicitly because they are what to fall back on when a future decision is close:

- **Keep infrastructure boring.** For anything the rest of the lab depends on (router, hypervisor, backups), choose stability, predictability, and fast recovery over interesting. Spend the novelty budget on the layers where learning actually happens.
- **Declarative over imperative where it reduces work.** Terraform, Ansible, Kubernetes, and Argo CD remain useful for lab provisioning and workloads. The essential network is an intentional exception: a few documented GUI settings cost less to maintain than a custom automation layer.
- **Git records intent; sensitive state stays private.** Version-control design decisions, sanitized setup steps, and declarative lab configuration. For GUI-managed network devices, keep private backups and a documented recovery process instead of pretending Git contains the complete live configuration. Never commit unredacted exports or secrets; see the [security guide](../0_Security_and_Public_Repository.md).
- **Prefer the industry standard unless there is a concrete reason not to.** The point of this lab is transferable skill, so the tie-breaker between two technically comparable tools is which one is actually used at work.
- **Do not own solved problems.** Every hand-built component is a permanent maintenance liability. Build something yourself only while it is teaching you something; once it has, hand it to a platform that does it better (this is exactly what happened to the hand-built router).
- **Choose for the hardware you have.** Loki over Elasticsearch, SOPS over Vault, one 64 GB node over four 16 GB ones — resource efficiency is a first-class selection criterion when the whole lab is a few low-power machines.
- **Every choice must have a rejected alternative.** If nothing was rejected, nothing was actually decided — which is why each section above ends with a table rather than a recommendation.

---

## Router & Firewall Software

> **See for more details about the corresponding design (not software/tool specific): [3_Design_Network.md](./3_Design_Network.md).**

**What it is.** The software for the shared home-and-lab gateway, switch, and wireless access points: WAN connectivity, VLAN routing, DHCP/DNS forwarding, firewall rules, switch port profiles, and Wi-Fi networks. Household connectivity must remain independent of the hypervisor and cluster.

**Chosen (2026-10): [UniFi](https://ui.com/) software already supplied and maintained by Ubiquiti on the [selected network hardware](1_Design_Hardware_Prerequisites.md#part-1--networking-hardware).** The gateway runs UniFi OS and the UniFi Network application locally, managing the switch and AP firmware/configuration together. No separate controller VM, CloudKey, custom router OS, Ansible router role, or additional networking software is needed for now. "Cloud Gateway" does not mean forwarding household traffic through a hosted controller; local operation remains the foundation.

OPNsense was a major improvement over the previous hand-built Linux router managed with Ansible, but still required more configuration, integration, and maintenance than I want for the network the household depends on. UniFi saves **a lot of time** compared with that approach, and much more compared with maintaining nftables, DHCP, DNS, and IPv6 services individually. This is a fit-for-purpose decision, not a claim that OPNsense is unreliable or inferior. See [Why Not a Separately Maintained Firewall PC](1_Design_Hardware_Prerequisites.md#why-not-a-separately-maintained-firewall-pc) for the original Raspberry Pi/Ansible setup, the subsequent OPNsense direction, and why both were superseded.

**Configuration and recovery.** Accept a small set of manual GUI steps for networks, port profiles, SSIDs, firewall policy, and updates. Record their intent and verification in the setup documentation; keep configuration backups, account recovery details, and secrets outside public Git. Maintain firmware, review security advisories, schedule potentially disruptive updates, and test recovery. There is less automation development to maintain, not zero maintenance.

**Accepted trade-offs.** Vendor lock-in, less low-level control and plugin flexibility, dependence on vendor firmware/support, and less complete declarative configuration. Core local networking has no mandatory subscription, but optional paid services are separate. These costs are significantly outweighed here by integrated administration, simpler recovery, fewer components, and time saved.

**Learning remains possible.** As with choosing Talos for Kubernetes lifecycle management, using a platform does not prohibit learning its internals elsewhere. Run OPNsense, pfSense, or another router OS in an isolated VM network to study firewalling, routing, or VPNs without changing the household gateway. Do not bridge experimental DHCP or Router Advertisements into live VLANs. A router OS provides ample learning depth; returning to a manually assembled Ansible router stack is not necessary.

**Alternatives considered:**

| Alternative | Why rejected |
|---|---|
| **[OPNsense](https://opnsense.org/)** | Excellent integrated open-source firewall, and the previous direction. Still requires owning an appliance OS, its configuration, optional plugins, and separate switch/AP management. More operational work than this shared network needs; retain as an isolated learning option. See the [previous setup and retirement rationale](1_Design_Hardware_Prerequisites.md#why-not-a-separately-maintained-firewall-pc). |
| **[pfSense](https://www.pfsense.org/)** | Similar strengths and responsibilities to OPNsense. Switching between them does not solve the underlying desire to maintain fewer things. |
| **[OpenWrt](https://openwrt.org/)** | Flexible and lightweight, including on supported ARM hardware. Hardware support and configuration still need attention; not the selected integrated gateway/switch/AP experience. |
| **[VyOS](https://vyos.io/)** | Strong routing and configuration-as-code potential, but operating and automating a routing platform is not the goal for essential household connectivity. |
| **Plain Linux + nftables/dnsmasq + Ansible** | Previously useful for learning, but leaves routing, firewall, DHCP, DNS, updates, and recovery integration with me. The greatest maintenance/development burden; not returning to it. |
| **[TP-Link Omada](https://www.tp-link.com/en/omada/)** | Credible centrally managed alternative, often competitively priced. UniFi was selected for the desired hardware, cohesive local console, documentation, and community familiarity; Omada remains a reasonable alternative, not an inferior design. |
| **[MikroTik RouterOS](https://mikrotik.com/)** | Excellent capability per euro and deep routing control, but a steeper configuration/operational learning curve than wanted here. |
| **[ASUS](https://www.asus.com/) / [NETGEAR](https://www.netgear.com/) consumer firmware** | Convenient for simple home networks, but routed VLANs, per-SSID segmentation, and integrated managed switching vary by model. Not chosen for this explicitly segmented setup. |

> **TODO: future VPN / remote access.** Evaluate the gateway's supported VPN options, such as OpenVPN or WireGuard, only when remote access is needed. Confirm firmware support, ISP reachability/double NAT, authentication, and restricted access to the intended segments. No VPN is deployed merely because the hardware supports it; never publish endpoints, keys, or exports.

---

## Hypervisor / Virtualization Platform

> **See for more details about the corresponding design (not software/tool specific): [4_Design_Hypervisor.md](./4_Design_Hypervisor.md).**

**What it is.** The layer that turns physical machines into pools of virtual machines: CPU/memory/storage abstraction, VM lifecycle, snapshots, templates, live migration, and (optionally) clustering across hosts. It is the foundation every workload sits on.

**Chosen (2026-02): [Proxmox VE](https://www.proxmox.com/en/proxmox-ve).** Open-source, Debian-based, built on KVM and LXC. It is free with no feature-gated licence tier, gives a full web UI *and* a complete REST API and CLI (so it can be driven by automation tools like Terraform and Ansible), supports clustering, live migration, ZFS, snapshots, and VM templates out of the box, and runs on the exact class of [refurbished hardware](./1_Design_Hardware_Prerequisites.md#part-2--compute--workload-hardware) this lab uses. Because the base is Debian, normal Linux tooling and knowledge applies directly — nothing is hidden behind a proprietary appliance layer.

**Alternatives considered:**

| Alternative | Why rejected |
|---|---|
| **[VMware ESXi / vSphere](https://www.asus.com/)** | The enterprise standard, so there is real career value in it. Rejected because the free ESXi tier was discontinued and the licensing after the Broadcom acquisition is prohibitive for a homelab, hardware compatibility lists are restrictive for consumer/SMB hardware, and the automation story requires vCenter. |
| **[XCP-ng](https://xcp-ng.org/)** | Genuinely good open-source alternative (Xen-based, with Xen Orchestra). Rejected because the ecosystem, community size, and third-party tooling (Terraform providers, guides, Ansible collections) are noticeably smaller than Proxmox's, and the best management experience nudges towards a paid Xen Orchestra build. |
| **[Hyper-V](https://learn.microsoft.com/en-us/virtualization/hyper-v-on-windows/about/)** | Solid and free with Windows Server, but Windows-centric, weaker for Linux-first workloads, and a poor match for a Linux/Kubernetes learning lab. |
| **Plain KVM/libvirt on Debian** | Maximum control and minimum abstraction, and genuinely instructive. Rejected for the same reason as the hand-built router: it means owning clustering, backups, snapshots, and a management interface yourself — solved problems that would consume the time meant for the actual learning goals. |
| **Bare metal (no hypervisor)** | Simplest possible setup, but wastes most of the hardware's value: no snapshots, no rollback, no isolation, and no ability to rebuild a broken experiment in two minutes. Snapshot-and-rollback is the single most useful property a learning lab can have. |

---

## Node & VM Operating System

> **See for more details about the corresponding design (not software/tool specific): [5_Design_Hosts_Nodes.md](./5_Design_Hosts_Nodes.md).**

**What it is.** The base OS on the physical hosts and inside the VMs. Its job is to be predictable, well-supported, and boring — it is the substrate, not the interesting part.

**Chosen (2026-03; scope clarified 2026-10): [Debian](https://www.debian.org/) (stable) on the hosts, [Ubuntu LTS](https://ubuntu.com) in general-purpose VMs.** Debian comes as the Proxmox base, so the host OS is not really a separate choice — and it is exactly the right one: extremely stable, long support windows, minimal surprises. Ubuntu LTS is used for the management VM and other general-purpose Linux services because it is widely documented, has excellent cloud-image and `cloud-init` support, and a long support window. Kubernetes control-plane and worker VMs instead use [Talos Linux](#kubernetes-node-os--lifecycle-talos-linux); they do not need a general-purpose guest OS.

**Alternatives considered:**

| Alternative | Why rejected |
|---|---|
| **[RHEL](https://www.redhat.com/en/technologies/linux-platforms/enterprise-linux) / [Rocky](https://rockylinux.org/) / [AlmaLinux](https://almalinux.org/)** | Very relevant for enterprise work and worth learning eventually. Rejected as the default because Proxmox is Debian-based, so mixing families doubles the packaging and automation surface for no benefit. Easy to add later as a VM when RHEL-specific practice is the goal. |
| **[Alpine](https://alpinelinux.org/)** | Tiny and fast, great for containers. Rejected for VMs because musl instead of glibc causes subtle compatibility issues, and the smaller ecosystem costs more time than the saved RAM is worth. |
| **Rolling distros ([Arch](https://archlinux.org/), [Fedora](https://getfedora.org/))** | Latest packages, but frequent breaking changes. Infrastructure should be boring; a lab that breaks on its own is a lab you stop using. |

---

## Cluster Tools

> **See for more details about the corresponding design (not software/tool specific): [6_Design_Cluster.md](./6_Design_Cluster.md).**

These are three separate choices: **Kubernetes** is the orchestration platform, **Talos Linux** supplies the node OS and cluster lifecycle tooling, and **Cilium** supplies cluster networking. They work together, rather than replacing one another. See [Cluster Setup](../2_Setup/5_Setup_Cluster.md) for the implementation workflow.

### Container Orchestration: Kubernetes

**What it is.** The layer that schedules containers across nodes and keeps them running: declarative desired state, self-healing, service discovery, load balancing, rolling updates, storage and secret injection, and horizontal scaling. It is where "a bunch of containers" becomes "a platform".

**Chosen (2026-03): [Kubernetes (K8s)](https://kubernetes.io/).** It is the industry standard, which is the dominant argument for a lab whose explicit purpose is real-world DevOps skills: everything learned here transfers directly to work. Its declarative, API-driven model is exactly what makes GitOps possible, and the ecosystem (ingress controllers, CSI drivers, operators, Helm charts, Prometheus integration) means almost every problem already has a well-trodden solution. It runs on VMs on Proxmox, which keeps the cluster reproducible and lets nodes be rebuilt at will.

**Alternatives considered:**

| Alternative | Why rejected |
|---|---|
| **[Docker Compose](https://docs.docker.com/compose/) only** | Perfectly adequate for running a handful of services and far simpler. Rejected because it teaches almost nothing about orchestration: no scheduling, no self-healing, no multi-node behaviour, no declarative reconciliation — which is precisely the learning goal. |
| **[Docker Swarm](https://docs.docker.com/engine/swarm/)** | Much easier than Kubernetes and clusters natively. Rejected because it is effectively in maintenance mode with a shrinking ecosystem; the skills do not transfer. |
| **[HashiCorp Nomad](https://www.nomadproject.io/)** | Genuinely elegant, simpler operationally, and handles non-container workloads. Rejected purely on market reality — far fewer jobs, far fewer integrations, far less documentation. |
| **[Plain containers on the hypervisor (LXC)](https://linuxcontainers.org/)** | Fine for single services (and used opportunistically for utility workloads), but no orchestration layer at all. |

### Kubernetes Node OS & Lifecycle: Talos Linux

**What it is.** The operating system and tooling used to provision, configure, and upgrade Kubernetes nodes. Choosing Kubernetes does not mean choosing to assemble and maintain it on general-purpose Linux VMs.

**Chosen (2026-10): [Talos Linux](https://www.siderolabs.com/talos-linux).** A minimal, immutable, API-managed Linux OS built specifically for Kubernetes. It runs upstream Kubernetes on the Proxmox control-plane and worker VMs, managed through `talosctl` and declarative machine configuration rather than SSH, a shell, or a package manager. The [official documentation](https://docs.siderolabs.com/) is the implementation reference.

**Why this fits my homelab:**

- **Less maintenance, quicker setup, more fun.** I want a functioning, always-on Kubernetes cluster, not another general-purpose Linux fleet to maintain. With Ubuntu/kubeadm I would own package repositories, kernel and container-runtime updates, kubelet dependencies, OS hardening, SSH/users, service configuration, reboot coordination, and the Ansible roles that keep those layers aligned. Talos supplies a purpose-built OS/runtime stack and API-driven configuration and lifecycle operations, reducing moving parts and the custom automation I must write, debug, and keep compatible. Nodes can be rebuilt from a known image and configuration instead of repaired through accumulated manual edits. That makes setup and maintenance more repeatable and leaves more time for Kubernetes, monitoring, Proxmox, workloads, and expanding the homelab — the parts I enjoy. It does not remove responsibility for version compatibility, staged OS/Kubernetes upgrades, networking, access credentials, etcd/data backups, and recovery tests; it is not a managed service.
- **Immutable nodes reduce drift and attack surface.** A read-only OS and controlled image-based updates discourage ad-hoc node changes. Fewer components and no SSH server or interactive shell reduce the general-purpose administration and security surface. Declarative configuration makes nodes more consistent and rebuildable, but does not replace API access controls, network policies, patching, or recovery planning.
- **Linux learning does not require more VMs.** Learning Linux remains a goal, and the existing Ubuntu management VM already provides hands-on practice with users, packages, systemd services, permissions, SSH, networking, logs, and troubleshooting; see its role in [Hosts & Nodes Setup](../2_Setup/4_Setup_Hosts_Nodes.md). Those fundamentals transfer between Linux systems: repeating the same OS administration on several permanent Kubernetes VMs adds maintenance more than new learning. I can practice on the management VM and other Linux services while Talos keeps the cluster focused on Kubernetes. Use snapshots or disposable sandboxes for risky experiments rather than break the management access path. No extra always-on Linux VMs are needed just to satisfy this learning goal.
- **Manual Kubernetes installation can be a temporary experiment.** When I want to learn kubeadm and node setup in depth, I can use disposable homelab VMs or an Azure cloud sandbox, for example through Pluralsight if available, then tear it down. Learning that process does not require maintaining it as the 24/7 platform. This follows the [router decision](#router--firewall-software): learn the fundamentals, then use dedicated tooling rather than keep rebuilding solved functionality on bare Linux.
- **Enterprise-relevant concepts without the whole enterprise platform.** AKS and EKS abstract parts of cluster provisioning and lifecycle; OpenShift Container Platform (OCP) 4.x uses purpose-built Red Hat Enterprise Linux CoreOS (RHCOS) for control-plane nodes and commonly workers. These differ substantially, but share the idea of declarative, platform-managed infrastructure rather than manual node administration. Talos teaches that philosophy without reproducing OpenShift's operator ecosystem or transferring responsibility to a cloud provider. Neither OpenShift nor managed cloud Kubernetes is maintenance-free.
- **Git-friendly configuration and portable Kubernetes skills.** Non-secret machine configuration patches and version pins can be reviewed in Git and applied through automation, reducing manual changes. Argo CD manages Kubernetes workloads, not Talos itself; node configuration still needs an explicit apply workflow. Upstream Kubernetes APIs and standard manifests reduce dependence on platform-specific services, but Talos APIs, image extensions, storage, and Cilium-specific policies remain migration considerations. OpenShift is also Kubernetes-based; its additional APIs and integrations, rather than an incompatible Kubernetes core, create extra portability work.
- **Resource savings are a secondary benefit.** A minimal OS may save some RAM and disk compared with Ubuntu, but Kubernetes, container images, Cilium, and workloads dominate sizing. Savings are likely modest and must be measured, not assumed.

**Accepted trade-offs.** No normal shell, SSH, or arbitrary package installation; debugging uses Talos APIs and Kubernetes tooling, and special host dependencies may require supported system extensions. That reduced flexibility is fine because these VMs only need to run Kubernetes. Learning Talos is itself interesting and fun, and gives me another perspective on Kubernetes; AI can help explain it, but official version-matched documentation and validation remain essential. The benefits outweigh these limits. Talos reduces lifecycle work, not my responsibility for cluster reliability.

**Alternatives considered:**

| Alternative | Why rejected for the always-on cluster |
|---|---|
| **[Ubuntu LTS](https://ubuntu.com) + [kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/)** | Maximum Linux flexibility and useful installation practice, but I would own OS hardening, packages, SSH, configuration drift, and coordinated Kubernetes upgrades. Keep this for disposable learning experiments, not the permanent cluster. |
| **[Red Hat OpenShift (OCP)](https://www.redhat.com/en/technologies/cloud-computing/openshift)** | An integrated enterprise platform with operators and lifecycle management, but its resource and operational scope exceed what this lab needs. I want the concepts, not the full platform. |
| **[OKD](https://okd.io/)** | The community distribution of Kubernetes that powers OpenShift, without requiring an OCP subscription. Useful for OpenShift-style learning, but still a broader operator-managed application platform with its own resource, release, and support requirements. Free to obtain does not mean lighter or maintenance-free; its full platform scope is unnecessary here. |
| **[K3s](https://k3s.io/) / [k0s](https://k0sproject.io/)** | Valid lightweight Kubernetes distributions, worth revisiting under tighter resource limits. They simplify Kubernetes installation but do not by themselves remove general-purpose host OS maintenance as Talos does. |
| **[MicroK8s](https://microk8s.io/)** | Convenient snap-packaged Kubernetes with add-ons and clustering. Simplifies Kubernetes installation/lifecycle, but I still maintain the Linux host and snap/update policy. Talos better matches the dedicated immutable-node goal. |
| **[Kubespray](https://kubespray.io/)** | Ansible-based Kubernetes deployment and lifecycle automation on supported Linux distributions. Removes much manual setup, but still leaves host OS/package maintenance, inventory, playbooks, and compatibility to manage. It is a provisioning approach, not a node OS; useful when conventional Linux flexibility is required. |
| **[RKE2](https://docs.rke2.io/)** | A security-focused Kubernetes distribution with packaged components and lifecycle tooling. A credible option for hardened conventional Linux nodes, but it does not replace the underlying OS administration I want to minimize. |
| **[AKS](https://learn.microsoft.com/en-us/azure/aks/what-is-aks) / [EKS](https://aws.amazon.com/eks/)** | Useful for cloud learning and abstract control-plane operations, but add ongoing cloud cost and move the cluster away from the local Proxmox learning platform. Workload, access, networking, and some node responsibilities still remain. |

### Cluster Networking (CNI): Cilium

**What it is.** The Container Network Interface implementation connects pods across nodes and supplies the networking foundation for services and network-policy enforcement. It is separate from the node OS and the router/firewall.

**Chosen (2026-10): [Cilium](https://docs.cilium.io/en/stable/overview/intro/).** A strong fit for learning modern Kubernetes networking: eBPF-based networking, Kubernetes NetworkPolicy enforcement, and optional Hubble flow visibility for troubleshooting. Its support for advanced routing, service handling, and observability provides room to grow without enabling every feature immediately. It is not universally the best or simplest CNI; flexibility is valuable only when it serves a real requirement.

**Keep the initial setup small.** Follow the [official Talos/Cilium integration guide](https://docs.siderolabs.com/kubernetes-guides/cni/deploying-cilium), with compatible pinned versions, the default CNI disabled, and a basic networking configuration. Start with kube-proxy retained; kube-proxy replacement, Hubble, BGP, and advanced ingress/load-balancing features are separate, deliberate additions after basic connectivity and policies work. Cilium adds memory usage and an eBPF troubleshooting learning curve. Prefer standard Kubernetes NetworkPolicy where sufficient to preserve portability; Cilium-specific policies are a conscious dependency.

**Alternatives considered:**

| Alternative | Why rejected |
|---|---|
| **[Calico](https://docs.tigera.io/calico/latest/about/)** | Mature networking and policy enforcement, including an eBPF option. A valid alternative, but Cilium's integrated Hubble visibility and networking learning path fit my goals better. |
| **[Flannel](https://github.com/flannel-io/flannel)** | Simple connectivity and the Talos default, but it does not itself enforce Kubernetes NetworkPolicy. I want policy enforcement and a richer troubleshooting path without adding a separate policy engine. |

---

## Infrastructure as Code (Provisioning)

> **No separate design document for Infrastructure as Code required; this section covers it enough already. The goal and design are simple: Automatically provision and manage infrastructure to ensure reproducibility, consistency, and maintainability.**

**What it is.** Declaring *infrastructure that does not exist yet* — VMs, networks, disks, DNS records, cloud resources — in version-controlled files, and letting a tool reconcile reality with that declaration. It tracks state, computes a diff, shows a plan before applying, and makes infrastructure reproducible and reviewable instead of hand-clicked.

**Chosen (2026-03): [Terraform](https://www.terraform.io/).** The de-facto industry standard with by far the largest provider ecosystem, including a mature Proxmox provider. The `plan` → `apply` workflow with explicit state and a visible diff is exactly the safety property you want before touching infrastructure, the declarative HCL syntax is easy to review in a pull request, and the skills transfer directly to any cloud. In this lab it owns VM creation and lifecycle on Proxmox. General-purpose Linux guests are configured with Ansible; Kubernetes guests use Talos machine configuration and the [Sidero Labs Talos provider](https://registry.terraform.io/providers/siderolabs/talos/latest/docs). A separate Talos cluster module is planned; see [Cluster Setup](../2_Setup/5_Setup_Cluster.md#terraform-automation-boundary).

**Alternatives considered:**

| Alternative | Why rejected |
|---|---|
| **[OpenTofu](https://opentofu.io/)** | The open-source fork after Terraform's licence change — a drop-in replacement and a legitimate choice. Not chosen because Terraform remains what is overwhelmingly used in industry (and therefore what is worth practising), and the BUSL licence change has no practical impact on private homelab use. Trivial to switch to later if that changes. |
| **[Pulumi](https://www.pulumi.com/)** | Infrastructure in real programming languages, which is powerful. Rejected because general-purpose languages make it far too easy to write imperative, hard-to-review infrastructure code, and because the ecosystem and job-market presence are much smaller. |
| **[Ansible](https://www.ansible.com/) for provisioning too** | Ansible *can* create VMs, and using one tool is tempting. Rejected because Ansible has no real state model — it cannot reliably tell you what will change before it changes it, or clean up what it created. Provisioning wants state and a plan; configuration wants idempotent convergence. Keeping the two concerns in the right tools is the cleaner design. |
| **Cloud-specific tools (e.g. [CloudFormation](https://aws.amazon.com/cloudformation/), [ARM/Bicep](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/))** | Locked to a single cloud and irrelevant to on-prem hardware. |

---

## Configuration Management

> **No separate design document for Configuration Management required; this section covers it enough already. The goal and design are simple: Automatically drive machines to a desired state without (or with minimal) manual intervention to ensure reproducibility, consistency, and maintainability.**

**What it is.** Taking machines that already exist and driving them to a desired state: packages, users, services, files, kernel parameters, certificates. It is **idempotent** — running it repeatedly converges to the same result — which is what turns "I set this up once, somehow" into "this is how it is defined, and it can be rebuilt."

**Chosen (2026-02; network scope revised 2026-10): [Ansible](https://www.ansible.com/).** Agentless SSH-based configuration for supported hosts and general-purpose VMs, with readable YAML and reusable roles. It pairs with Terraform: Terraform creates the machine, Ansible configures it. It no longer configures the household gateway, switch, or APs; those use the documented UniFi GUI workflow and private backups, not an OPNsense export generated from Git.

**Talos boundary.** Ansible remains useful for Proxmox administration, the management VM, and other supported systems. Talos Kubernetes nodes are configured through their API, not SSH-based Linux roles or an Ansible kubeadm installation.

**Alternatives considered:**

| Alternative | Why rejected |
|---|---|
| **[Puppet](https://puppet.com/)** | Mature and strong at enforcing state continuously at scale. Rejected because it requires an agent (and usually a server), uses its own DSL, and is heavy for a handful of nodes. |
| **[Chef](https://www.chef.io/) ** | Same objection — agent-based, Ruby DSL, steep learning curve, and declining industry usage. |
| **[SaltStack](https://saltproject.io/)** | Fast and scalable with its event bus, but agent/master-based by default, a smaller community, and an uncertain roadmap. |
| **[Shell scripts](https://en.wikipedia.org/wiki/Shell_script)** | Zero dependencies and fine for a one-off. Rejected because they are not idempotent, not declarative, and rot immediately — exactly the problem configuration management exists to solve. |
| **Doing it inside the VM image (e.g. [Packer](https://www.packer.io/) / golden images)** | Complementary rather than competing, and worth adding later for faster VM builds. Rejected as the primary mechanism because rebuilding an image for every small change is a slow feedback loop. |

---

## GitOps & Continuous Delivery

> **See [Security and Public Repository](../0_Security_and_Public_Repository.md) for repository-wide rules on publishing and protecting secrets.**

**What it is.** Treating a Git repository as the single source of truth for what runs in the cluster, with an in-cluster agent continuously reconciling actual state against the repository. Deployments become commits; rollbacks become reverts; drift is detected and corrected automatically. Crucially it is **pull-based** — the cluster pulls from Git rather than CI pushing into the cluster, so no external system needs cluster credentials.

**Chosen (2026-03): [Argo CD](https://argo-cd.readthedocs.io/).** The most widely adopted GitOps controller, with an excellent UI that makes desired-vs-actual state and sync status immediately visible — which is genuinely valuable while learning, because it shows *why* something is out of sync rather than just failing. It handles Helm and Kustomize natively, supports app-of-apps patterns for structuring a whole cluster, and is the tool most likely to be encountered professionally.

**Alternatives considered:**

| Alternative | Why rejected |
|---|---|
| **[Flux CD](https://fluxcd.io/)** | Equally capable, more Kubernetes-native and more lightweight, and a perfectly valid choice. Rejected mainly on the UI: Flux is CLI-first, and Argo CD's visual diff and sync view is a real learning aid. Adoption is also somewhat broader for Argo CD. |
| **Push-based CD from CI** (CI runs `kubectl apply`) | Simpler to set up initially. Rejected because it requires handing cluster credentials to an external CI system, provides no drift detection, and makes the actual cluster state diverge silently from Git. |
| **[Helm](https://helm.sh/) alone, applied manually** | Templating without reconciliation — it deploys, but nothing keeps the cluster matching Git. Used *underneath* Argo CD rather than instead of it. |

---

## CI: Build, Test & Lint

> **See for more details about the corresponding design (not software/tool specific): TODO: add this later.**

**What it is.** The automation that runs on every commit and pull request: linting, validation, security scanning, building images, and running tests — catching mistakes before they reach the cluster. CI validates; CD (above) deploys.

**Chosen: [GitHub Actions](https://github.com/features/actions).** The repositories already live on GitHub, so there is nothing extra to host or maintain — which matters, because a self-hosted CI server is another piece of always-on infrastructure. Free for public repositories with a generous allowance for private ones, a huge marketplace of ready-made actions (`terraform validate`, `ansible-lint`, `yamllint`, `kubeconform`, container builds), and it is the CI system most commonly encountered today.

**Alternatives considered:**

| Alternative | Why rejected |
|---|---|
| **[Jenkins](https://www.jenkins.io/)** | Extremely flexible and still common in enterprises. Rejected because it must be hosted, maintained, updated, and secured — real ongoing work, and a plugin ecosystem that ages badly. |
| **[GitLab CI](https://docs.gitlab.com/ee/ci/)** | Excellent and arguably the nicest self-hosted experience. Rejected because it would mean migrating off GitHub or running a GitLab instance, which is significant infrastructure for a homelab. |
| **[Drone](https://www.drone.io/) / [Woodpecker](https://woodpecker-ci.org/) / [Gitea Actions](https://docs.gitea.io/en-us/actions/)** | Lightweight and self-hostable, good fits for a homelab. Rejected because self-hosting CI adds an always-on service with no learning benefit over the hosted equivalent. |
| **[Tekton](https://tekton.dev/) / [Argo Workflows](https://argoproj.github.io/argo-workflows/)** | Kubernetes-native CI, which is conceptually attractive. Rejected as too complex for the amount of CI this lab actually needs. |

---

## Secrets Management

> **See [Security and Public Repository](../0_Security_and_Public_Repository.md) for repository-wide rules on publishing and protecting secrets.**

**What it is.** Keeping credentials, keys, and tokens out of Git and out of plaintext, while still making them available to automation and workloads — with a clear story for rotation and for who can decrypt what.

**Chosen (2026-04): [SOPS](https://github.com/getsops/sops) with age.** Secrets are encrypted *in the repository itself*, so the GitOps model stays intact (everything is still in Git) without ever committing a plaintext credential. It integrates cleanly with Ansible and with Kubernetes manifests, has no server to run, and no additional always-on service to keep available — which matters, because a secrets store that is down blocks everything else.

**Alternatives considered:**

| Alternative | Why rejected |
|---|---|
| **[HashiCorp Vault](https://www.vaultproject.io/)** | The enterprise answer, with dynamic secrets, leasing, and proper audit — genuinely worth learning. Rejected for now because it is a stateful, always-on service with real operational complexity (unsealing, backup, HA) and becomes a hard dependency for the whole lab. A good candidate for a later, deliberate learning project. |
| **[Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) alone** | Only base64-encoded, not encrypted at rest by default, and cannot safely live in Git. Used as the delivery mechanism *inside* the cluster, not as the source of truth. |
| **[Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html)** | Works well for Ansible, but only for Ansible — it does not cover Kubernetes manifests or Terraform, so it would mean two secret systems. |
| **[External Secrets Operator](https://external-secrets.io/) + cloud [KMS](https://cloud.google.com/kms)** | Clean pattern, but requires a cloud dependency the lab deliberately does not have. |

---

## Monitoring & Observability

> **See for more details about the corresponding design (not software/tool specific): [7_Design_Monitoring.md](./7_Design_Monitoring.md).**

**What it is.** Knowing what the lab is doing and being told when it stops doing it. Observability is conventionally split into distinct signals, and the split matters because each has different storage, query, and retention characteristics — conflating them is how monitoring stacks become expensive and slow:

- **Metrics** — cheap numeric time series (CPU, memory, request rate, error rate). Good for trends, dashboards, and alert thresholds; bad at explaining *why*.
- **Logs** — expensive, high-cardinality text events. Good at explaining *why*; bad for trends.
- **Visualization** — turning both into dashboards a human can read at a glance.
- **Alerting** — deciding when a human needs to be interrupted, and routing/deduplicating/silencing those notifications.

(The fourth classic signal, **traces**, is deliberately out of scope for now — it only pays off with a real distributed application. Grafana Tempo is the natural addition if that changes.)

### Metrics

**Chosen (2026-05): [Prometheus](https://prometheus.io/).** The de-facto standard for cloud-native metrics: pull-based scraping, Kubernetes-aware service discovery, PromQL, and exporters such as node_exporter, Proxmox exporters, cAdvisor, and kube-state-metrics. Network devices use UniFi's built-in visibility for now; an external exporter is optional future integration, not another dependency of household networking.

| Alternative | Why rejected |
|---|---|
| **[InfluxDB / TICK](https://www.influxdata.com/)** | Good time-series database, but push-based, with a smaller Kubernetes ecosystem and a query language that has changed direction more than once. |
| **[Zabbix](https://www.zabbix.com/) / [Nagios](https://www.nagios.org/) / [Checkmk](https://checkmk.com/)** | Mature classic infrastructure monitoring with strong alerting. Rejected because they are host-centric and agent-based, and fit containerised, dynamically scheduled workloads poorly. |
| **[Netdata](https://www.netdata.cloud/)** | Superb out-of-the-box per-host visibility with near-zero setup. Rejected as the primary store because long-term retention and cross-host querying are weaker, and it does not integrate into the same ecosystem. |

### Logs

**Chosen (2026-05): [Loki](https://grafana.com/oss/loki/).** Designed deliberately as "Prometheus, but for logs": it indexes only labels rather than full log content, which makes it dramatically cheaper in storage and memory than a full-text search engine — a decisive property on homelab hardware. It uses the same label model as Prometheus, so a dashboard can pivot from a metric spike to the matching logs with identical selectors, and it is queried through the same Grafana UI.

| Alternative | Why rejected |
|---|---|
| **[Elasticsearch](https://www.elastic.co/elasticsearch/) / ELK (or [OpenSearch](https://opensearch.org/))** | More powerful full-text search and analytics. Rejected because it is heavy — a JVM, high RAM requirements, and real cluster operations — which is disproportionate for a homelab whose nodes are also running everything else. |
| **[Graylog](https://www.graylog.org/)** | Nice UI and alerting, but still Elasticsearch/OpenSearch underneath, so it inherits the same resource cost. |
| **Plain files + journald/rsyslog** | Zero cost and already there, but no central aggregation, no label-based querying, and no correlation with metrics. |

### Visualization & Dashboards

**Chosen (2026-05): [Grafana](https://grafana.com/).** The industry-standard visualization layer and, importantly, the *single pane of glass*: one UI queries Prometheus for metrics and Loki for logs side by side, so correlating "this spike" with "these log lines" happens in one place. Huge library of community dashboards (Proxmox, node_exporter, Kubernetes, OPNsense) means useful dashboards exist from day one, and dashboards are JSON and therefore version-controllable like everything else.

| Alternative | Why rejected |
|---|---|
| **[Kibana](https://www.elastic.co/kibana/)** | Tied to the Elasticsearch stack, which was already rejected for logs. |
| **[Prometheus' built-in UI](https://prometheus.io/docs/visualization/) ** | Fine for ad-hoc PromQL queries, but not a dashboarding tool. |
| **Vendor/per-tool UIs** (Proxmox summary graphs, UniFi Network) | Retained for local diagnostics, including network operation without lab monitoring. Not a replacement for cross-system lab dashboards. |

### Alerting

**Chosen (2026-05): [Prometheus Alertmanager](https://prometheus.io/docs/alerting/alertmanager/).** Alert *rules* live with the metrics in Prometheus (version-controlled alongside everything else), and Alertmanager handles the part that actually makes alerting usable: grouping, deduplication, inhibition, silencing, and routing to a notification channel. Without that layer, a single outage produces fifty notifications and you learn to ignore all of them.

| Alternative | Why rejected |
|---|---|
| **[Grafana Alerting](https://grafana.com/docs/grafana/latest/alerting/)** | Convenient because it is already in the dashboard UI, and genuinely good. Rejected as the primary mechanism to keep alert rules next to the metrics that define them, and because Alertmanager's routing/inhibition model is more capable. |
| **Per-tool alerting** (Proxmox email, UniFi notifications) | Useful independent fallback when lab monitoring is unavailable. Exact notification delivery depends on the service configured; not the primary correlated lab alerting mechanism. |

---

## Backup

> **See for more details about the corresponding design (not software/tool specific): TODO: add this later.**

**What it is.** The ability to get back to a known-good state after a failure, a bad change, or a mistake. A homelab that cannot be restored is a homelab you become afraid to experiment in — which defeats the purpose.

**Chosen (2026-05): [Proxmox Backup Server (PBS)](https://www.proxmox.com/en/proxmox-backup-server)** for incremental, deduplicated, compressed, verified VM/container backups, with sanitized configuration-as-code in Git as a second layer. Terraform, Ansible, and Kubernetes configuration can rebuild lab components from source; sensitive state, keys, and exports must remain private under the [security guide](../0_Security_and_Public_Repository.md). **UniFi configuration backups are separate from VM backups and are not committed to public Git.** Keep them accessible without the lab running, alongside a documented gateway restore/re-adoption process. Backups protect data and device state; version control protects publishable intent.

| Alternative | Why rejected |
|---|---|
| **[`vzdump`](https://pve.proxmox.com/pve-docs/vzdump.1.html) to a local/NFS share** | Built into Proxmox and simple, and a perfectly reasonable starting point. Rejected as the long-term answer because it produces full, undeduplicated archives — much larger, slower, and with no built-in verification. |
| **[Rsync](https://linux.die.net/man/1/rsync) / tar scripts** | Cheap and flexible, but no consistency guarantees for running VMs, no deduplication, no verification, and entirely homegrown. |
| **[Veeam / commercial backup](https://www.veeam.com/)** | Excellent products, but licensing cost and Windows-centric management make them a poor fit here. |
| **Snapshots only** | Snapshots are fast rollback, not backup — they live on the same disk and disappear with it. Used *alongside* backups, never instead. |

>**The 3-2-1 caveat:** PBS plus Git covers on-site recovery. A genuine off-site copy (a second location or encrypted cloud storage) is still required to survive theft, fire, or a failed disk taking the backup store with it. Treat that as part of the backup design, not an optional extra.

---

## Storage
 
> **See for more details about the corresponding design (not software/tool specific): TODO: add this later.**

TODO: add this later in the same format as the others above; brainstorm with AI how to do this, etc.
TODO: maybe Ceph?? And what to do with my Samsung 1TB SSD; I have them left over so may as well use them!

**TODO: I do need a storage setup, so use the Mini PCs and then 1 or 2 HDDs for backup storage! That is worth it and can maybe add more later, etc., and maybe RAID, etc., but somethung outside of the normal storage on the mini PC and old laptop for backup storage and a HDD because it is cold storage not harf storage, rtc. TODO: add thst in storage design anf add to hardware page also the additional storage, etc.**

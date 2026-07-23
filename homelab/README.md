# Home Lab

This is the central documentation for my personal home lab. It covers the goals, design, and step-by-step setup from buying hardware to a running cluster with Kubernetes, monitoring, and GitOps automation.

---

## Table of Contents

- [Personal Goal](#personal-goal)
  - [What this is NOT](#what-this-is-not)
- [Home Lab Design](#home-lab-design)
- [Installation & Setup](#installation--setup)

---

## Personal Goal

The goal of this home lab is simple: **learn the fundamentals of DevOps and Software Engineering, and have fun doing it — while building a cool and satisfying home lab to experiment with.** Topics include networking, Linux, Kubernetes, monitoring (Grafana, Prometheus), infrastructure automation, and more — because I genuinely enjoy experimenting with these things and want to advance my Engineering skills.

There's something genuinely cool and satisfying about having a real home lab cluster sitting on your desk: physical nodes, real networking, services you deployed yourself, dashboards showing live metrics from your own hardware. It's not just a learning environment — it's a playground to break things, try out new tools before using them at work, and experiment without any consequences. And it just looks and feels awesome.

In my work I use these techniques daily and will continue to do so: VMs, networking, Linux, containers, etc. Having hands-on experience with them makes my work easier and more enjoyable, and makes me a better Engineer overall. A home lab is the best way to get that unrestricted, persistent environment where you can break things, fix them, and learn without consequences.

### What this is NOT

This lab is purely for learning and fun — not production, not an obligation. Key boundaries:

- **Not 24/7 uptime required**: can turn it off when done for the day or keep it running depending on preference, no stress.
- **Not self-hosting everything**: still using cloud storage (e.g. OneDrive), streaming services (e.g. Netflix), and the ISP's modem/router. Setting up your own NAS with drives, a VPN, and a custom router costs a lot of money and effort, introduces security risks (e.g. a self-hosted VPN exposes your home network to the internet if misconfigured), and is the domain of Network/Storage/Infrastructure Engineers — which is not my goal at this time. The focus is on learning DevOps concepts, not on building a custom home network or storage solution.
- **Not advanced hardware tinkering**: the focus is on DevOps concepts (K8s, automation, observability), not on assembling servers or deep hardware engineering.
- **Repurpose old hardware**: rather than buying new, old laptops and refurbished enterprise-grade mini PCs are used — good for the environment, good for the wallet, and still perfectly capable for learning.

--- 

## Home Lab Design
The home lab is a hands-on learning environment for exploring DevOps, Kubernetes, networking, Linux, and infrastructure automation. The goal is learning and experimentation — not production. Everything is automated from the start, and all code and documentation lives in this repository.

The lab runs on a small cluster of personal hardware (e.g. mini PCs, old laptops, etc.) using Proxmox VE as the hypervisor, with VMs provisioned for a Kubernetes control plane, worker nodes, and management workloads such as monitoring and CI/CD.

Key components:
- **Proxmox VE**: Hypervisor for running VMs and LXC containers across physical nodes.
- **Kubernetes**: Container orchestration for learning real-world cluster management, CNI, scheduling, and high availability.
- **Ansible**: Configuration management and automation across nodes and VMs.
- **Terraform**: Infrastructure-as-Code for provisioning VMs and other resources in Proxmox.
- **Monitoring**: Prometheus and Grafana for observability and dashboards.
- **ArgoCD**: GitOps-based continuous delivery for Kubernetes workloads.

TODO: does this still apply at the end of my home lab setup? Update when I have my final home lab setup and architecture finalized and working!

---

## Installation & Setup

This section documents the step-by-step process for building this home lab from scratch — from defining goals and buying hardware to a fully running cluster. The **setup is based on my personal goals and hardware choices**, but **documented as generically as possible to be useful to others**. If your hardware or goals differ, adjust accordingly.

| Step | File | Description |
|------|------|-------------|
| 1 | [Goals & Hardware](docs/1_Goals_Hardware.md) | Define goals, choose hardware type, compare refurbished shops, and decide on your node setup. |
| 2 | [OS & Hypervisor](docs/2_OS_Hypervisor.md) | Install the OS or hypervisor (e.g. Proxmox VE, Ubuntu) on each node — bootable USB, BIOS config, and installation process. |
| 3 | [Cluster & Network](docs/3_Cluster_Network.md) | Link nodes into a cluster, configure networking — Gigabit switch, static IPs, VLANs, and join nodes via Proxmox cluster or k3s/kubeadm. |
| 4 | [Core Services & Monitoring](docs/4_Core_Services_Monitoring.md) | Deploy the core stack — container runtime, GitHub Runners, monitoring (Prometheus + Grafana), and logging, etc. |
| 5 | [Storage & Backups](docs/5_Storage_Backups.md) | Storage and backup strategy — why cloud-based backups fit this lab's goals, and when NAS/RAID makes sense. |
| 6 | [Experiment](docs/6_Experiment.md) | The ongoing phase — experiment, break things, and learn. |

TODO: update with latest documentation setup at the end.
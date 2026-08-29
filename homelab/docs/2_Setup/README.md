# Setup & Installation

> **See [Design](../1_Design/README.md) for the overall architecture and network topology. All setup steps are based on the design.**

TODO: here the setup and installation with the specific steps.

TODO: then the steps here as a guide, TODO: update with latest documents setup:
| Step | File | Description |
|------|------|-------------|
| 1 | [Design](docs//1_Design/README.md) | Design of the home lab, the personal goals, etc. — includes network topology, node setup, and overall architecture. |
| 2 | [OS & Hypervisor](docs/2_OS_Hypervisor.md) | Install the OS or hypervisor (e.g. Proxmox VE, Ubuntu) on each node — bootable USB, BIOS config, and installation process. |
| 3 | [Cluster & Network](docs/3_Cluster_Network.md) | Link nodes into a cluster, configure networking — Gigabit switch, static IPs, VLANs, and join nodes via Proxmox cluster or k3s/kubeadm. |
| 4 | [Storage & Backups](docs/5_Storage_Backups.md) | Storage and backup strategy — why cloud-based backups fit this lab's goals, and when NAS/RAID makes sense. |
| 5 | [Core Services & Monitoring](docs/4_Core_Services_Monitoring.md) | Deploy the core stack — container runtime, GitHub Runners, monitoring (Prometheus + Grafana), and logging, etc. |
| 6 | [Experiment](docs/6_Experiment.md) | The ongoing phase — experiment, break things, and learn. |
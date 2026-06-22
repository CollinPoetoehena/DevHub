# TODO

TODO: make this the starting point of HomeLab, below add Design section and then the steps for installing and using the HomeLab, etc.

## Personal Goal

The goal of this home lab is simple: **learn the fundamentals of DevOps and Software Engineering, and have fun doing it.** Topics include networking, Linux, Kubernetes, monitoring (Grafana, Prometheus), infrastructure automation, and more — because I genuinely enjoy experimenting with these things and want to advance my Engineering skills.

In my work I use these techniques daily and will continue to do so: VMs, networking, Linux, containers, etc. Having hands-on experience with them makes my work easier and more enjoyable, and makes me a better Engineer overall. A home lab is the best way to get that unrestricted, persistent environment where you can break things, fix them, and learn without consequences.

### What this is NOT

This lab is purely for learning and fun — not production, not an obligation. Key boundaries:

- **Not 24/7 uptime required**: can turn it off when done for the day or keep it running depending on preference, no stress.
- **Not self-hosting everything**: still using cloud storage (e.g. OneDrive), streaming services (e.g. Netflix), and the ISP's modem/router. Setting up your own NAS with drives, a VPN, and a custom router costs a lot of money and effort, introduces security risks (e.g. a self-hosted VPN exposes your home network to the internet if misconfigured), and is the domain of Network/Storage/Infrastructure Engineers — which is not my goal at this time. The focus is on learning DevOps concepts, not on building a custom home network or storage solution.
- **Not advanced hardware tinkering**: the focus is on DevOps concepts (K8s, automation, observability), not on assembling servers or deep hardware engineering.
- **Repurpose old hardware**: rather than buying new, old laptops and refurbished enterprise-grade mini PCs are used — good for the environment, good for the wallet, and still perfectly capable for learning.

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

# Installation & Setup of Personal Home Lab
TODO: here shortly explain the steps for installing and setting up the home lab, including the order of operations, prerequisites, and any other relevant information. Note that this is the personal home lab setup for myself based on the goals listed above, but it is documented here as generically as possible to be useful for others, if you have different goals, your setup may differ. The steps below are a general outline of the process, and may be adjusted based on your specific hardware, software, and learning objectives.
TODO: reference all files further for the setup.

# TODO: create dir for configuring with 2_... and then 1_Installing_OS, etc. inside that folder:



# TODO: here a separate file later for post installation:


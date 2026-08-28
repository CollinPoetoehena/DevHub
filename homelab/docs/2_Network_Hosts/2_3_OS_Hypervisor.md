# OS and Hypervisor Installation


TODO: split this up into /reference for the general things like bootable USB, Hypervisor and Ubuntu, etc.
TODO: then setup and installation for this file and the specific steps here for the hosts, run with Ansible again, etc.

# TODO: for Proxmox creating VMs:
TODO: use Ubuntu Server, TODO: add here why with AI.
TODO: nodes I want: mgmtvm, then 1 control plane for now and 2 workers. Later can expand when I have more hardware than only my laptop, etc.!
TODO: selecting the speccs (for now manual, but later do with automation!).
## TODO: explanation about specs and things, add this in /reference for explanation of what each part is, this is now from AI:
Proxmox CPU Options Explained
1. Cores
What it is:  
The number of virtual CPU cores inside the VM.

How it works:  
Proxmox maps these to threads on your physical CPU.

Example:  
If you set 2 cores, the VM sees a dual‑core CPU.

Recommendation:

Control plane: 2–4 cores

Worker node: 2 cores

2. Sockets
What it is:  
How many virtual CPU sockets the VM has.

How it works:  
This is mostly for compatibility with OSes that behave differently with multi‑socket CPUs.

Example:  
If you set:

Sockets: 1

Cores: 2

The VM sees 1 CPU with 2 cores.

If you set:

Sockets: 2

Cores: 1

The VM sees 2 CPUs with 1 core each.

Recommendation:  
Always use:

Sockets: 1  
Cores: X

Kubernetes nodes do not benefit from multi‑socket VMs.

3. vCPUs
What it is:  
The total number of virtual CPUs the VM sees.

Formula:

Code
vCPUs = sockets × cores
Example:  
Sockets: 1
Cores: 2
→ VM sees 2 vCPUs

Sockets: 2
Cores: 2
→ VM sees 4 vCPUs

Recommendation:  
You don’t set vCPUs directly — it’s derived automatically.

4. CPU Type
What it is:  
The virtual CPU model exposed to the VM.

Options:

host → exposes your real CPU features

kvm64 → generic, maximum compatibility

qemu64 → older, slower

Vendor-specific models (Skylake, Haswell, etc.)

Recommendation:  
Use:

CPU Type: host

Best performance for Kubernetes workloads.

5. CPU Units
What it is:  
A weighting system for CPU scheduling.

How it works:  
Higher number = VM gets more CPU time when the node is busy.

Default is 1024.

Example:  
If you set:

VM A: 1024

VM B: 512

VM A gets twice the CPU priority.

Recommendation:  
Leave default 1024 unless you want to deprioritize a VM.

6. CPU Limit
What it is:  
Hard cap on CPU usage.

Example:  
If you set CPU limit = 1.0, the VM can only use 1 physical core even if it has 4 vCPUs.

Recommendation:  
Do not set a limit for Kubernetes nodes.

7. CPU Weight
Same as CPU units — used for scheduling fairness.

Leave default.

8. NUMA
What it is:  
Non‑Uniform Memory Access — advanced CPU/memory topology.

Recommendation:  
Turn off unless you know you need it.

Kubernetes nodes do not benefit from NUMA in a homelab.

🎯 Recommended CPU Settings for Ubuntu Server K8s VM
Control Plane
Sockets: 1

Cores: 2–4

CPU Type: host

CPU Units: 1024

NUMA: off

CPU Limit: none

Worker Node
Sockets: 1

Cores: 2

CPU Type: host

CPU Units: 1024

NUMA: off

CPU Limit: none


# TODO: for setup:
TODO: started on Proxmox VE setup after booting it with a bootable USB.
TODO: refer to [Booting OS: Hypervisor Installation (Proxmox VE)](../../../reference/os_hardware/Booting_OS.md#hypervisor-installation-proxmox-ve)
TODO: add steps here to install Proxmox VE on the host and then after that just use the basic steps, maybe I need to manually add vmbr0.10 to add connectivity.
TODO: after adding in /etc/network/interfaces the correct ones such as vmbr0.10, etc., for the VLANs, it had connection, see [network interfaces template](../../ansible/roles/proxmox/templates/network-interfaces.j2).
**TODO: maybe add that with Ansible now via Ansible modules for the network interfaces and NOT as a template!!! This is hardcoded and ideally you want Ansible to automate this! TODO: then add in comments why the setup, such as vlan-aware, etc.**

TODO: then for image usage: Ubuntu Server.

## TODO: configure through connection with Proxmox VE host:
TODO: SSH works from the Pi router, I tested!
TODO: also add an automation account that can be used for automation things.
```bash
# SSH to Proxmox
ssh root@10.42.10.10

# Create user (if not exists)
pveum user add automation@pam

# Create API token
pveum user token add automation@pam automation --privsep=0

# Grant permissions
pveum acl modify / --user automation@pam --role Administrator
```

TODO: then with Terraform can automate the provisioning and management of VMs on the Proxmox VE host using the automation account and API token!

TODO: for automated VM setup, use Terraform with a cloud image (avoids having to manually configure the OS on each VM), can just use an existing cloud image from Ubuntu. See example: https://github.com/marcmassoteau-jpg/massoteau-homelab-devops/tree/main/terraform/proxmox-vms
TODO: add the Terraform module as a separate repo in DevHub!
**TODO: I think same design as azure with the separate things, such as terraform-proxmox-vms, terraform-proxmox-hardening, etc.**


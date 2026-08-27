# TODO: Fill this in when I start on the actual home lab and get to this point, etc.


TODO: refer here for number of nodes to [Goals & Hardware](../1_Goals_Hardware_LocalEnvSetup.md#how-many-nodes).
TODO: refer to [Hardware Setup](../1_Goals_Hardware_LocalEnvSetup.md#current-personal-setup). TODO: this will be 1 mini PC (main Proxmox node) and 1 old laptop (Proxmox backup server).

## Proxmox
TODO: create cluster with 2 nodes, can just be for now my laptop and later mini PC, etc.

Proxmox: Install and document in DevHub/homelab folder the setup with Proxmox. TODO: connectivity not working, check Proxmox documentation for the getting started to see if they say anything about the settings!
TODO: create Proxmox DevHub Terraform modules for things like VMs and maybe other things (TODO: think about what can be made, automate everything you do!).


## K8s
TODO: thoight with AI and I think for first setup Kubeadm with cp1 and cp2 and cp3 (all with 2 CPU and 2 GB RAM) and then 2 workers (both 4 CPU and 4 GB RAM) and the rest for the Proxmox host (14 GB RAM for the k8s cluster and then 2 GB left for Proxmox).
TODO; networking I think Cilium.
TODO: storage still brainstorm.
TODO: GitHub runner can be added later and use OUTBOUND connection so I do NOT expose internet to my home network!!



**TODO: I want to create VMs on Proxmox for the K8s cluster, explain here why VMs (extra layer, not on Bare Metal (BM)), such as more nodes available for the K8s cluster (segmentation, etc.), I want to learn VMs as well to get a deeper understanding, etc., TODO: explain with AI more and more reasons, etc.**
TODO: for the monitoring separate dedicated monitoring VMs because this should be separate of the main cluster (it also monitors the cluster!), etc.! See [explanation in network design](../2_Network/2_1_Network_Design.md#why-monitoring-lives-on-a-separate-vm-not-inside-kubernetes)
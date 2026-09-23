# Setup & Installation: Cluster

TODO: here after installing and setting up the VMs on the Hypervisor, you can proceed with setting up the Kubernetes cluster.

TODO: refer to design part for the cluster architecture and tools, etc.

## K8s
TODO: thoight with AI and I think for first setup Kubeadm with cp1 and cp2 and cp3 (all with 2 CPU and 2 GB RAM) and then 2 workers (both 4 CPU and 4 GB RAM) and the rest for the Proxmox host (14 GB RAM for the k8s cluster and then 2 GB left for Proxmox).
TODO; networking I think Cilium.
TODO: storage still brainstorm.
TODO: GitHub runner can be added later and use OUTBOUND connection so I do NOT expose internet to my home network!!

**TODO: I want to create VMs on Proxmox for the K8s cluster, explain here why VMs (extra layer, not on Bare Metal (BM)), such as more nodes available for the K8s cluster (segmentation, etc.), I want to learn VMs as well to get a deeper understanding, etc., TODO: explain with AI more and more reasons, etc.**
TODO: for the monitoring separate dedicated monitoring VMs because this should be separate of the main cluster (it also monitors the cluster!), etc.! See [explanation in network design](../2_Network_Hosts/TODO.md#why-monitoring-lives-on-a-separate-vm-not-inside-kubernetes)
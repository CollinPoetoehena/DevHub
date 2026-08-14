# TODO: Fill this in when I start on the actual home lab and get to this point, etc.


TODO: here creating the cluster of nodes 
TODO: network for cluster: Here or in Network.md part? I think add that in the Network.md earlier.

Link your nodes together so they behave as one system.

For Proxmox: create a cluster and join the other nodes

For Kubernetes: install k3s or kubeadm and join worker nodes

Verify node communication and cluster health
etc...

TODO: refer here for number of nodes to [Goals & Hardware](../1_Goals_Hardware_LocalEnvSetup.md#how-many-nodes).
TODO: refer to [Hardware Setup](../1_Goals_Hardware_LocalEnvSetup.md#current-personal-setup). TODO: this will be 1 mini PC (main Proxmox node) and 1 old laptop (Proxmox backup server).

**TODO: I want to create VMs on Proxmox for the K8s cluster, explain here why VMs (extra layer, not on Bare Metal (BM)), such as more nodes available for the K8s cluster (segmentation, etc.), I want to learn VMs as well to get a deeper understanding, etc., TODO: explain with AI more and more reasons, etc.**
**TODO: think about the actual setup, such as all VMs on a K8s cluster, or some VMs with monitoring like Prometheus, Grafana, mgmt VM, etc. TODO: I think 2 mgmt vms (one on one physical node, another on a different node as backup (and learns me to do everything with Ansible/IaC), then 1 or 2 "runner" VM for GitHub pipelines, etc., then monitoring VMs not I think since inside cluster is best (think with AI to do this as a separate VM or Grafana, Prometheus, etc., in K8s cluster, I think inside the cluster is best and easiest because K8s is the future and it is best to learn that now!!!, and I learn VMs already with the mgmt VM and the K8s VMs, etc.!?)), then just K8s VMs**
**TODO: update in 2_1_Network_Setup.md the network setup with the actual VMs!**.
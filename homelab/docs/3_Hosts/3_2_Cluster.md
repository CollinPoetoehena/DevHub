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
TODO: for the monitoring separate dedicated monitoring VMs because this should be separate of the main cluster (it also monitors the cluster!), etc.! See [explanation in network design](../2_Network/2_1_Network_Design.md#why-monitoring-lives-on-a-separate-vm-not-inside-kubernetes)
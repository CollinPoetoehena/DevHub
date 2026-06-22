# TODO: here creating the cluster of nodes and the network between them

Link your nodes together so they behave as one system.

For Proxmox: create a cluster and join the other nodes

For Kubernetes: install k3s or kubeadm and join worker nodes

Verify node communication and cluster health
etc...

A stable network is essential for clustering and node communication.


TODO: Use a Gigabit switch (5–8 ports is enough), Connect all nodes via Ethernet, Reserve static IPs in your router, etc.

TODO: also create VLANs for the different networks (management, workload, storage, etc.) and configure routing between them. This is because I also want to learn more about networking concepts, etc.

TODO: also use Ansible and Terraform here already.
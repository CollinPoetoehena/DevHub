# Setup & Installation: Hypervisor

TODO: here add setting up Proxmox

TODO: with Ansible configure proxmox after booting it with USB, etc.

# TODO: for setup:
TODO: started on Proxmox VE setup after booting it with a bootable USB.
TODO: refer to [Booting OS: Hypervisor Installation (Proxmox VE)](../../../reference/os_hardware/Booting_OS.md#hypervisor-installation-proxmox-ve)
TODO: add steps here to install Proxmox VE on the host and then after that just use the basic steps, maybe I need to manually add vmbr0.10 to add connectivity.
TODO: after adding in /etc/network/interfaces the correct ones such as vmbr0.10, etc., for the VLANs, it had connection, see [network interfaces template](../../ansible/roles/proxmox/templates/network-interfaces.j2).
**TODO: maybe add that with Ansible now via Ansible modules for the network interfaces and NOT as a template!!! This is hardcoded and ideally you want Ansible to automate this! TODO: then add in comments why the setup, such as vlan-aware, etc.**

TODO: then for image usage: Ubuntu Server.

## TODO: configure through connection with Proxmox VE host:
TODO: SSH works from the Pi router, I tested: `ssh root@10.42.10.10`, then just the password.

TODO: after that I can configure with Ansible the rest!

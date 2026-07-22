# OS and Hypervisor Installation

TODO: this below document is done and checked, only update some parts with some specific steps I do where necessary, etc. After that this part is done!

This document is split into three chapters:

1. [Create a bootable USB (general process)](#chapter-1-bootable-usb-general)
2. [Install a hypervisor (Proxmox VE)](#chapter-2-hypervisor-installation-proxmox-ve)
3. [Install a Linux OS for worker nodes (example: Ubuntu Server LTS)](#chapter-3-linux-os-installation-worker-node-example)

Use this as the baseline process for preparing homelab nodes.

## Chapter 1: Bootable USB (General)

A bootable USB is a USB drive prepared with an installer image (ISO) so a machine can start directly from it and run an OS or hypervisor installation.

### Prerequisites

Before you start:

- [ ] USB flash drive (8 GB minimum, 16 GB recommended)
- [ ] ISO image for the target installer (Proxmox VE or Linux distribution)
- [ ] USB writing tool (Rufus, balenaEtcher, or `dd`)
- [ ] Target hardware (laptop, desktop, mini PC, etc.)

### Create the Bootable USB

1. Download the correct ISO from the official project website.
2. Download and open your USB writing tool (I prefer [Rufus](https://rufus.ie/en/) but you can also use [balenaEtcher](https://www.balena.io/etcher/))
3. Insert the USB drive.
4. Select the USB device and ISO image in the USB writing tool.
5. Keep default settings unless the project documentation requires changes.
6. Click "Start" and wait for completion (click "OK" on any prompts). Note that all existing data on the USB will be erased!
7. Safely eject the USB drive.

### BIOS/UEFI Preparation
BIOS/UEFI is the motherboard firmware menu used before any OS loads. You use it to control boot order and low-level hardware boot settings.

The BIOS Configuration section explains how to access your hardware's firmware settings (BIOS/UEFI) to configure it for booting from USB. This is not an OS application, it's a low-level system interface that exists before any OS even loads.

To configure these settings:

1. Power off the target machine fully. Insert the USB drive (do not boot into any OS yet), otherwise you will not be able to set this as the first boot device in boot order.
2. Power on and repeatedly press BIOS/UEFI key (`F2`, `F12`, `Del`, `Esc`, depends on vendor). In previous attempts, it was usually `F2` for me, such as on an old Acer laptop.
3. Adjust settings:
   - Set USB as first boot device (or use one-time boot menu) in the boot order.
   - Disable Fast Boot.
   - Keep UEFI mode unless your hardware specifically requires Legacy/CSM.
   - If Linux installer complains about Intel RST/Optane, switch storage mode to AHCI. Note that on some machines the option may be hidden. For example, with an old Acer laptop, I had to press Ctrl+s to reveal the option under Main > SATA Mode, where I could select AHCI.
   - If Secure Boot causes boot issues, disable it temporarily.
4. Exit and save. Then reboot (`F10` on many systems from the BIOS/UEFI menu) or just power off and back on.

### Boot from USB

1. Make sure the USB drive is inserted.
2. Reboot.
3. Select USB from boot menu.
4. Start installer entry from the USB menu. Details for the installer process are in the next chapters (Proxmox VE or Linux OS).

### Optional: Restore USB to Normal Use

After installation, you can reformat the USB as a single FAT32 or exFAT partition.

1. Insert the USB drive back into your computer
2. Open File Explorer (Windows laptop or Linux does not really matter)
3. Select your USB drive on the left
4. Click the gear icon under the USB drive name and select Format
5. Choose Format Partition…
6. Select FAT32 (or exFAT if you want large file support) & Select overwrite existing data to get a clean USB drive
7. Click Format

If the USB has multiple partitions (common after using Rufus):
1. Click the minus (–) button to delete each partition
2. Then click the + button to create one new partition
3. Format it as FAT32

After that, the USB is completely normal again.

---

## Chapter 2: Hypervisor Installation (Proxmox VE)

Use this chapter for your virtualization host nodes.

A hypervisor is software that lets one physical machine run multiple virtual machines. Proxmox VE is the platform that manages those VMs, storage, and virtual networking. 

Proxmox VE is chosen because it is currently the main open-source hypervisor that is actively maintained, has a strong community, and is free to use.

### Proxmox VE Prerequisites

- [ ] Proxmox VE ISO downloaded from the official site
- [ ] At least one SSD/NVMe for host storage
- [ ] Planned static management IP, gateway, and DNS
- [ ] Planned hostname (example: `pve1.homelab.local`)

### Install Proxmox VE

1. Boot target machine from the Proxmox USB.
2. Select `Install Proxmox VE` in the boot menu.
3. Accept license and choose target disk.
4. Select filesystem (default `ext4` is fine to start; ZFS is optional if planned).
5. Configure locale, timezone, and keyboard.
6. Set a strong `root` password and admin email.
7. Configure management network:
   - Assign static IP/CIDR: pick an unused IP in your management subnet and enter it with prefix, for example `192.168.1.10/24` (`/24` = subnet mask `255.255.255.0`, typically range `192.168.1.1` to `192.168.1.254`). Reserve this IP in DHCP so it is never assigned to another device.
   - Set gateway: enter your router/firewall LAN IP on the same subnet (e.g. `192.168.1.1`). To determine it, check your router admin page, or on an already connected Linux machine run `ip r` and use the `default via ...` address.
   - Set DNS server: use a reachable resolver such as your router DNS, local DNS (e.g. Pi-hole/AdGuard), or public DNS (`1.1.1.1`, `8.8.8.8`). To determine your current DNS, check router DHCP/DNS settings, or on Linux run `resolvectl status` (or `cat /etc/resolv.conf`) on a working device in the same network.
    - Set FQDN hostname: use full name format `hostname.domain`, for example `pve1.homelab.local`; determine it by choosing (1) a short host name that is unique and role-based (`pve1`, `pve2`, `pve3`) and (2) a domain suffix from your DNS/router search domain (`homelab.local`, `lan`, or your own internal domain). Keep this value stable because certificates and cluster configuration depend on it; before installing, verify naming consistency by checking that your DNS (or router host overrides) will resolve the same name to the static IP you assigned.
8. Confirm summary and start installation. Wait until complete (may take 5–15 minutes depending on hardware).
9. Remove USB and reboot.

### First Login and Baseline Setup

1. Open browser to `https://<proxmox-ip>:8006`.
2. Log in as `root` with PAM realm.
3. Run updates from shell:

```bash
apt update
apt full-upgrade -y
```

4. Verify network bridge (`vmbr0`) is present and bound to primary NIC.
5. Set up storage/datastore layout according to your plan.

---

## Chapter 3: Linux OS Installation (Worker Node Example)

Use this chapter for non-hypervisor nodes (k3s/k8s workers, utility hosts, monitoring nodes, etc.).

A worker node is a regular Linux server that runs workloads or supporting services, rather than hosting virtual machines for other systems.

### Example Target

- Distribution: Ubuntu Server LTS
- Role: Worker node

### Install Linux Worker Node

1. Boot target machine from Linux USB.
2. Start installer (for Ubuntu: `Try or Install Ubuntu Server`).
3. Configure language, keyboard, and network.
4. Set static IP if this node should not rely on DHCP.
5. Partition disk:
   - Recommended for dedicated worker node: erase disk and install clean.
   - Manual option example:

```text
/boot/efi   512MB   FAT32   (UEFI systems)
/           30GB+   ext4    (root)
swap        2-8GB   swap    (or based on RAM/usage)
/var        remaining ext4  (optional split for workloads/logs)
```

6. Create admin user.
7. Enable OpenSSH during install.
8. Complete install, remove USB, and reboot.

### Post-Install Baseline (Linux Worker)

```bash
sudo apt update
sudo apt upgrade -y
sudo timedatectl set-timezone <your-timezone>
sudo hostnamectl set-hostname <node-name>
```

Recommended next checks:

- Verify SSH connectivity from management machine
- Verify static IP, gateway, and DNS
- Add node to inventory/config management (Ansible, etc.)

---

## Troubleshooting (Applies to Both)

### Boot and Installer Issues

- Problem: USB not detected or not booting.
  - Solution: recreate USB, check boot order, try different USB port, disable Fast Boot.

- Problem: Installer cannot detect internal disk.
  - Solution: switch BIOS storage mode from Intel RST/Optane to AHCI.

- Problem: System freezes during boot, such as "Your device ran into a problem and needs to restart. We'll restart for you." 
  - Solution: This often happens if Intel RST driver was removed from Storage Controllers but BIOS is still in RST/Optane mode. Boot into Windows Safe Mode to restore:
    1. Power off the laptop completely
    2. Remove the USB drive
    3. Turn on and immediately start tapping **F8** or **Shift+F8** repeatedly to enter Windwos Recovery/Automatic Repair Mode. This can be tricky on modern laptops due to fast boot times, so you may need to try a few times. In this experiment, it went to a mode where it did not have a network connection and prompted to press Enter to see other recovery options. Here I selected Quick Repair and enabled Hotspot on my mobile phone for network connection.
    4. If that doesn't work, go back into the BIOS/UEFI settings and set the SATA Mode to AHCI and boot with Ubuntu on USB:
       - Press power button
       - Enter BIOS/UEFI (see steps above for explanation)
       - Change SATA Mode to AHCI as explained in the earlier steps for BIOS/UEFI configuration
       - Save and Exit
       - Boot from the USB with Linux, such as Ubuntu, and continue the installation
       - Repeat this 3 times - Windows will boot into Recovery mode.

### Network Issues

- Problem: No network after install.
  - Solution: confirm NIC name, static config, gateway, DNS; test with `ip a` and `ping`.

### Performance Issues

- Problem: Node feels slow.
  - Solution: check thermal throttling, disk health, and running services (`htop`, `iostat`, `dmesg`).

---

## Resources

- [Proxmox VE Documentation](https://pve.proxmox.com/pve-docs/)
- [Proxmox VE Installation Guide](https://pve.proxmox.com/wiki/Installation)
- [Ubuntu Documentation](https://documentation.ubuntu.com/)
- [Ubuntu Server Install Tutorial](https://ubuntu.com/tutorials/install-ubuntu-server)

### Useful Commands Reference

```bash
# System information
uname -a                   # Kernel information
lsb_release -a             # Distribution information
df -h                      # Disk usage
free -h                    # Memory usage
lscpu                      # CPU information

# Package management (Debian/Ubuntu)
sudo apt update            # Update package list
sudo apt upgrade           # Upgrade packages
sudo apt install [package] # Install package
sudo apt remove [package]  # Remove package
sudo apt search [keyword]  # Search for package

# File operations
ls -lah                    # List files with details
cd [directory]             # Change directory
cp [source] [dest]         # Copy files
mv [source] [dest]         # Move/rename files
rm [file]                  # Remove file
mkdir [directory]          # Create directory

# Networking quick checks
ip a                     # Show network interfaces and assigned IP addresses
ip r                     # Show routing table (default gateway and routes)
ping -c 3 1.1.1.1        # Test basic outbound network connectivity (no DNS required)
ping -c 3 google.com     # Test connectivity plus DNS name resolution

# System management
sudo systemctl status [service]  # Check service status
sudo systemctl start [service]   # Start service
sudo systemctl enable [service]  # Enable service at boot
journalctl -xe                   # View system logs
```
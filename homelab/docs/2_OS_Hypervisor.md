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
   - Disable Secure Boot to allow for easier installation of unsigned bootloaders (e.g. Proxmox usually does not start with Secure Boot Enabled). You can always re-enable it later if you want. For this you usually first need to set a Supervisor Password in the BIOS/UEFI menu under the Security tab, then you can disable Secure Boot. Make sure to remember this password and keep it safe because you will need it to re-enable Secure Boot later. 
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
7. Configure management network (VERY IMPORTANT to configure this correctly, otherwise you may not have correct connectivity to the Proxmox web interface after install):
  - Assign static IP/CIDR: pick an unused IP in your management subnet and enter it with prefix, for example `192.168.1.10/24` (`/24` = subnet mask `255.255.255.0`, typically range `192.168.1.1` to `192.168.1.254`). Reserve this IP in DHCP so it is never assigned to another device.
  - Set gateway: enter your router/firewall LAN IP on the same subnet (e.g. `192.168.1.1`). To determine it, check your router admin page, or on an already connected Linux machine run `ip r` and use the `default via ...` address.
  - Set DNS server: use a reachable resolver such as your router DNS, local DNS (e.g. Pi-hole/AdGuard), or public DNS (`1.1.1.1`, `8.8.8.8`). To determine your current DNS, check router DHCP/DNS settings, or on Linux run `resolvectl status` (or `cat /etc/resolv.conf`) on a working device in the same network.
  - Set FQDN hostname: use full name format `hostname.domain`, for example `pve1.homelab.local`; determine it by choosing (1) a short host name that is unique and role-based (`pve1`, `pve2`, `pve3`) and (2) a domain suffix from your DNS/router search domain (`homelab.local`, `lan`, or your own internal domain). Keep this value stable because certificates and cluster configuration depend on it; before installing, verify naming consistency by checking that your DNS (or router host overrides) will resolve the same name to the static IP you assigned.

  Example: derive values from a working laptop in the same network before starting Proxmox install.
```sh
$ ip r
default via 192.168.144.1 dev eth0 proto kernel 
172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1 linkdown 
192.168.49.0/24 dev br-4c412f4ff897 proto kernel scope link src 192.168.49.1 linkdown 
192.168.144.0/20 dev eth0 proto kernel scope link src 192.168.151.174

$ resolvectl status
Global
         Protocols: -LLMNR -mDNS -DNSOverTLS DNSSEC=no/unsupported
  resolv.conf mode: foreign
Current DNS Server: 10.255.255.254
       DNS Servers: 10.255.255.254
        DNS Domain: home

Link 2 (eth0)
    Current Scopes: none
         Protocols: -DefaultRoute -LLMNR -mDNS -DNSOverTLS DNSSEC=no/unsupported

Link 3 (br-4c412f4ff897)
    Current Scopes: none
         Protocols: -DefaultRoute -LLMNR -mDNS -DNSOverTLS DNSSEC=no/unsupported

Link 4 (docker0)
```
  What to enter in Proxmox installer from this example:
  - Static IP/CIDR: `192.168.151.200/20` (same `/20` subnet as existing LAN, and `192.168.151.200` is an example unused host IP in that subnet).
  - Gateway: `192.168.144.1` (taken from `default via ...`; this is the route out of the local network).
  - DNS server: `192.168.144.1` (router DNS from `resolvectl`; add public DNS later as fallback if needed).
  - FQDN hostname: `pve1.homelab.local` (role-based host `pve1` + local domain `local` from DNS domain/search domain).
  
  Basic connectivity test: after install, from Proxmox console run:
```sh
ping -c 3 <gateway-ip>   # Test connectivity to gateway (LAN router)
ping -c 3 1.1.1.1        # Test basic outbound network connectivity (no DNS required)
ping -c 3 google.com     # Test connectivity plus DNS name resolution
```
  
  If you need to reconfigure, you can follow these steps in the running Proxmox console:
```sh
# 1) Log in on Proxmox local console as root, then back up current config
cp /etc/network/interfaces /etc/network/interfaces.bak

# 2) Identify physical NIC name (example: eno1, enp3s0)
ip -br link

# 3) Edit Proxmox network config
nano /etc/network/interfaces

# 4) Example config (replace eno1 and IPs for your LAN)
cat <<'EOF'
auto lo
iface lo inet loopback

iface eno1 inet manual

auto vmbr0
iface vmbr0 inet static
    address 192.168.151.200/20
    gateway 192.168.144.1
    bridge-ports eno1
    bridge-stp off
    bridge-fd 0
EOF

# NOTE: Make sure the 'address' line has no typos, extra characters, or spaces. 
# The format is exactly: 'address <IP>/<CIDR>'

# 5) Optionally update DNS server in /etc/resolv.conf (or use resolvconf if installed)
nano /etc/resolv.conf
# Example resolv.conf content:
search homelab.local
nameserver 192.168.144.1

# 6) Apply by rebooting (safest during initial setup)
reboot

# 7) After reboot, verify from Proxmox console
ip a
ip r
cat /etc/resolv.conf
```
  Use these values because they match the detected LAN route (`192.168.144.0/20`), use a valid host IP in that range, and keep gateway/DNS reachable from the same network.
8. Confirm summary and start installation. Wait until complete (may take 5–15 minutes depending on hardware).
9. Remove USB and reboot.

### First Login and Baseline Setup

1. Open browser to `https://<proxmox-ip>:8006`.
2. Log in as `root` user (shows `pve login:`) and enter the password you set during installation.
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
    3. Turn on and immediately start tapping **F8** or **Shift+F8** repeatedly to enter Windows Recovery/Automatic Repair Mode. This can be tricky on modern laptops due to fast boot times, so you may need to try a few times. In this experiment, it went to a mode where it did not have a network connection and prompted to press Enter to see other recovery options. Here I selected Quick Repair and enabled Hotspot on my mobile phone for network connection.
    4. If that doesn't work, go back into the BIOS/UEFI settings and set the SATA Mode to AHCI and boot with Ubuntu on USB:
       - Press power button
       - Enter BIOS/UEFI (see steps above for explanation)
       - Change SATA Mode to AHCI as explained in the earlier steps for BIOS/UEFI configuration
       - Save and Exit
       - Boot from the USB with Linux, such as Ubuntu, and continue the installation
       - Repeat this 3 times - Windows will boot into Recovery mode.

- Problem: After Proxmox installation, machine keeps rebooting and shows "Boot Option Restoration" (blue screen).
  - Solution: Firmware cannot find or trust the Proxmox EFI boot entry. In this case the problem was that I did not Disable Secure Boot, causing it to fail. Fix it in BIOS/UEFI:
    1. Power off fully, unplug USB devices, then enter BIOS/UEFI with the method described in [BIOS/UEFI Preparation](#biosuefi-preparation).
    2. Load BIOS defaults (`F9`), then set:
       - Boot mode: UEFI
       - Fast Boot: Disabled
       - Secure Boot: Disabled, as explained in [BIOS/UEFI Preparation](#biosuefi-preparation). With Secure Boot Enabled Proxmox will not boot because the bootloader is unsigned. You can re-enable Secure Boot later if you want, but for now it must be disabled to allow Proxmox to boot.
       - F12 Boot Menu: Enabled
    3. Move internal Proxmox boot entry to top of boot order.
    4. If no Proxmox entry exists, add one from EFI file browser:
       - `\\EFI\\proxmox\\grubx64.efi`
       - or `\\EFI\\debian\\grubx64.efi`
    5. Save (`F10`) and reboot.
    6. If loop continues, boot Proxmox USB in rescue mode and reinstall the EFI bootloader.

### Network Issues

- Problem: No network after install.
  - Solution: confirm NIC name, static config, gateway, DNS; diagnose with:

```bash
ip a
ip r
cat /etc/network/interfaces
systemctl status networking
```

    Common causes:
    - vmbr0 bridge is down: run `ifup vmbr0` to bring it up.
    - Physical NIC not bound: verify `bridge-ports eno1` (or your NIC name) exists in `/etc/network/interfaces`.
    - Gateway unreachable: verify ethernet cable connected, and `ip r` shows `default via <gateway IP, such as 192.168.144.1>`.

- Problem: `ip a` shows all interfaces down except the default route is correct, and the gateway is still unreachable.
  - Solution: the bridge or physical NIC is not actually up yet, even though the route is correct.
    1. Bring up the physical NIC first, for example: `ifup eno1`.
    2. Then bring up the bridge: `ifup vmbr0`.
    3. Verify both are up: `ip a` should show `UP` on the NIC and `vmbr0`.
    4. Test the gateway again: `ping -c 3 192.168.144.1`.
    5. If it still fails, restart networking: `systemctl restart networking`, then recheck `ip a` and `ip r`.

- Problem: After reconfiguring `/etc/network/interfaces`, `systemctl status networking` shows error like `does not appear to be an IPv4 or IPv6 address`.
  - Cause: typo in IP address (extra character, malformed CIDR, etc.).
  - Solution:
    1. Check the exact error message.
    2. Edit the file: `nano /etc/network/interfaces`
    3. Verify the `address` line is exactly: `address 192.168.151.200/20` (no extra characters like `X`).
    4. Save, exit, then restart: `systemctl restart networking`
    5. Verify bridge is up: `ip a` should show `vmbr0` with the correct IP.

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
cat /etc/resolv.conf     # Show DNS resolver configuration
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
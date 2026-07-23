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

### Install Proxmox VE & Configure Host Machine

1. Boot target machine from the Proxmox USB. Then select `Install Proxmox VE` in the boot menu.
2. Now you can configure the host machine by following the [Proxmox VE Installation Guide](https://pve.proxmox.com/wiki/Installation) and the [Proxmox VE Configuration Guide](https://pve.proxmox.com/pve-docs/chapter-sysadmin.html). Some tips and notes for myself regarding the installation and configuration are added below (e.g. Network tips).
3. Confirm summary and start installation. Wait until complete (may take 5–15 minutes depending on hardware).
4. Remove USB and reboot.

TODO: add in separate network config and now use a router in between from now on from my Raspberry Pi to avoid conflicts.
TODO: make it 2_Host_Network_Config as a folder and add a README.md, then 3_Cluster
TODO: add problems: Home network some devices cannot connect to internet. In this case, I had quite a couple devices that had this such as my phone, a TV, and a printer (connected wiht Ethernet). Likely because Proxmox VE on the main network did some things, TODO: let AI do what it might have done, causing IP conflicts likely which is why there were such problems for some devices, but not all. TODO: add additional troubleshooting here is logging into your ISPs modem, which I did in this case and saw some IP conflicts. Solutions: TODO: with AI in general you can reserve static IPs and internal bridge, etc., but that does not provide full safety, a better solution is a dedicated router for the homelab, which provides a full isolated network for the homelab where Proxmox and all other things in the dedicated homelab network cannot interfere (and with that break) the home network. This is the choice I made because it provides full safety to avoid breaking the home network, and because it is very fun to learn more about networking and create my own router, etc.
TODO: in the meantime when I set up this router, I shutdown the Proxmox VE host and add Linux on it in the meantime via the bootable USB with Ubuntu Desktop (see steps in the documentation in this repository for how to do that) to avoid Proxmox VE on that host continuing to interfering with the network each time I start the host while I was still able to use that machine (now with Ubuntu Desktop on it). Then when the router is ready, I can reinstall Proxmox VE on the host again.

TODO: router inloggen ook om IP Static toe te wijzen aan de home lab router! Dit doe je door in te loggen op je ISPs modem.
TODO: network doc updaten met eigen router maken, zoals een Raspberry Pi, etc. En dan met Ansible.

#### Network Configuration Notes
See [Proxmox VE Network Configuration](https://pve.proxmox.com/wiki/Network_Configuration) for details. The following contains notes for my home lab setup. See steps below, using subsections because of the longer instructions.
##### 1. Network Planning
Determine the network settings **before** installing Proxmox VE.
  - Make sure a network cable is connected from the Proxmox host to your LAN/router.
   - Collect gateway and DNS values from your **primary host OS network stack** (the real OS interface connected to LAN), not from a secondary/virtualized stack such as WSL on Windows, Docker bridge, VPN tunnel, or VM guest interface.
    - Why: secondary stacks often show virtual values that are not valid for bare-metal Proxmox management setup. This is the mistake I made the first time I tried, leading to a Proxmox host with no network connectivity because I used the virtual values from WSL instead of the real LAN gateway/DNS from the host OS.
    - Example of misleading virtualized values:
      - WSL often shows a NAT gateway like `172.x.x.1` in `/etc/resolv.conf` and `ip r`.
      - Docker bridges may show routes like `172.17.0.0/16`.
      - These are internal overlay/NAT networks, not your physical LAN gateway/DNS.
   - On the host connected to the same LAN, gather values with:
TODO: in network config kan ik dit gebruiken alsnog, ookal doe ik niet dit meer direct, zo kan ik bijvoorbeeld achterhalen van router IP.
```sh
# ====================================== Linux host: ======================================
ip r                # Shows default gateway (default via <gateway-ip> dev <interface>)
resolvectl status   # Shows DNS servers and search domain
# Example output (only showing relevant information, skipping the rest of the output):
$ ip r
default via <gateway-ip> dev <interface>
$ cat /etc/resolv.conf
nameserver <dns-server-ip>

# ====================================== Windows host: ======================================
ipconfig /all       # Shows all network information including gateway, DNS servers, etc.
# Example output (only showing relevant information, skipping the rest of the output):
$ ipconfig /all
IPv4 Address. . . . . . . . . . . : <host-ip>
Subnet Mask . . . . . . . . . . . : <subnet-mask>
Default Gateway . . . . . . . . . : <gateway-ipv6>
                                    <gateway-ipv4>
DHCP Server . . . . . . . . . . . : <dhcp-server-ip>
DNS Servers . . . . . . . . . . . : <dns-server-ipv6>
                                    <dns-server-ipv4>
```
   - Set installer values:
     - Static IP/CIDR: pick an unused IP in your management subnet, for example `192.168.1.10/24` (`/24` = subnet mask `255.255.255.0`, typically range `192.168.1.1` to `192.168.1.254`). Reserve it in DHCP so no other device gets it.
     - Gateway: use the LAN router/firewall IP from the above commands, shows in Linux as `default via <gateway-ip> dev <interface>` and in Windows as `Default Gateway` (example: `192.168.2.254`).
     - DNS server: use reachable DNS on the same LAN path (e.g. router DNS, Pi-hole/AdGuard, or other local resolver).
     - FQDN hostname: use stable format `<hostname>.<domain>`, such as `pve1.homelab.local`. Determine it by choosing (1) a short host name that is unique and role-based (`pve1`, `pve2`, `pve3`) and (2) a domain suffix from your DNS/router search domain (`homelab.local`, `lan`, or your own internal domain). Keep this value stable because certificates and cluster configuration depend on it; before installing, verify naming consistency by checking that your DNS (or router host overrides) will resolve the same name to the static IP you assigned.


Verify networking immediately after Proxmox installation.

```sh
# Check interface state and addresses
ip a

# Check routes (default gateway must exist)
ip r

# Check DNS resolver currently configured
cat /etc/resolv.conf

# Connectivity checks
ping -c 3 <gateway-ip>      # Test gateway reachability
ping -c 3 8.8.8.8           # Test basic outbound connectivity by pinging Google's DNS server (no DNS required)
ping -c 3 google.com        # Test connectivity plus DNS name resolution
```

   - What you should see:
     - Physical NIC (for example `eno1`/`enp3s0`/`nic0`) should be `UP`.
     - Physical NIC should show `LOWER_UP` when ethernet cable/link is active. For me `nic0` was the physical NIC, and `vmbr0` was the bridge.
     - Bridge `vmbr0` should have the static management IP.
     - `ip r` should include `default via <gateway-ip> dev vmbr0`.
     - `ping <gateway-ip>` should succeed; if `ping 1.1.1.1` works but `ping google.com` fails, this indicates a DNS issue.

3. If needed, apply network changes after Proxmox is installed (e.g. if you find out the static IP, gateway, or DNS was incorrect). This step is added here because the Proxmox installer sometimes does not allow you to set the correct values, or you may have misconfigured them. You can fix it after install by editing `/etc/network/interfaces` and `/etc/resolv.conf` directly. 
```sh
# 1) Log in on Proxmox local console as root and back up config
cp /etc/network/interfaces /etc/network/interfaces.bak

# 2) Identify NIC names
ip -br link

# 3) Edit network config
nano /etc/network/interfaces

# 4) Example (replace nic0 + IP values with your LAN values)
cat <<'EOF'
auto lo
iface lo inet loopback

iface nic0 inet manual

auto vmbr0
iface vmbr0 inet static
    address 192.168.2.200/24
    gateway 192.168.144.1
    bridge-ports nic0
    bridge-stp off
    bridge-fd 0
EOF

# NOTE: 'address' must be exactly: address <IP>/<CIDR>

# 5) Update DNS if required
nano /etc/resolv.conf
# Example:
search homelab.local
nameserver 192.168.144.1

# 6) Apply changes (reboot is safest during initial setup)
reboot

# 7) Re-verify after reboot: See verify networking immediately after Proxmox installation section above.
```

If interface states are still wrong after reboot (`DOWN` or missing `LOWER_UP`), check cable/port first, then verify the NIC name in `bridge-ports` exactly matches `ip -br link` output.

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
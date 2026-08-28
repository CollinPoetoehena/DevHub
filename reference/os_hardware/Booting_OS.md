# Booting OS 

This document provides an overview of the process involved in booting an operating system on a computer, including the role of the BIOS/UEFI, bootloader, and kernel initialization.

This document is split into 2 main parts: Creating a `boot device` (USB) and Booting from it. For the booting process, there are 2 main options you can choose: a hypervisor installation (e.g. Proxmox VE) or a standard OS installation (e.g. Ubuntu Server LTS)

---

## Table of Contents
1. [Create a bootable USB (general process)](#bootable-usb-general)
2. [Booting from USB (Hypervisor or OS)](#booting-from-usb-hypervisor-or-os)
    - [Install a hypervisor (Proxmox VE)](#hypervisor-installation-proxmox-ve)
    - [Install a Linux OS](#linux-os-installation)

---

# Bootable USB (General)

A bootable USB is a USB drive prepared with an installer image (ISO) so a machine can start directly from it and run an OS or hypervisor installation. This is also called `flashing` an OS onto a storage device (in this case a USB drive), making it a `boot device`.

## Prerequisites

Before you start:
- [ ] USB flash drive (8 GB minimum, 16 GB recommended)
- [ ] ISO image for the target installer (Proxmox VE or Linux distribution)
- [ ] USB writing tool (Rufus, balenaEtcher, or `dd`)
- [ ] Target hardware (laptop, desktop, mini PC, etc.)

## Create the Bootable USB
1. Download the correct ISO from the official project website.
2. Download and open your USB writing tool (I prefer [Rufus](https://rufus.ie/en/) but you can also use [balenaEtcher](https://www.balena.io/etcher/))
3. Insert the USB drive.
4. Select the USB device and ISO image in the USB writing tool.
5. Keep default settings unless the project documentation requires changes.
6. Click "Start" and wait for completion (click "OK" on any prompts). Note that all existing data on the USB will be erased!
7. Safely eject the USB drive.

## BIOS/UEFI Preparation
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

## Boot from USB General Steps
> **Note:** These are just general steps, the exact process may vary depending on your hardware and the specific OS or hypervisor you are installing. See for details the next chapter about [Booting from USB (Hypervisor or OS)](#booting-from-usb-hypervisor-or-os).

1. Make sure the USB drive is inserted.
2. Reboot.
3. Select USB from boot menu.
4. Start installer entry from the USB menu. Details for the installer process are in the next chapters (Proxmox VE or Linux OS).

## Optional: Restore USB to Normal Use

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

# Booting from USB (Hypervisor or OS)

This chapter covers the steps to boot from a USB drive and install either a hypervisor (Proxmox VE) or a Linux OS on your target machine.

## Hypervisor Installation (Proxmox VE)

A hypervisor is software that lets one physical machine run multiple virtual machines. Proxmox VE is the platform that manages those VMs, storage, and virtual networking. 

Proxmox VE is chosen because it is currently the main open-source hypervisor that is actively maintained, has a strong community, and is free to use.

### Proxmox VE Prerequisites

- [ ] Proxmox VE ISO downloaded from the [official site](https://www.proxmox.com/en/products/proxmox-virtual-environment/get-started) and written to a USB drive (see [Chapter 1: Bootable USB](#chapter-1-bootable-usb-general))
- [ ] At least one SSD/NVMe for host storage
- [ ] Planned static management IP, gateway, and DNS
- [ ] Planned hostname (example: `pve1.homelab.local`)

### Install Proxmox VE & Configure Host Machine

1. Boot target machine from the Proxmox USB. Then select `Install Proxmox VE` in the boot menu.
2. Now you can configure the host machine by following the [Proxmox VE Installation Guide](https://pve.proxmox.com/wiki/Installation) and the [Proxmox VE Configuration Guide](https://pve.proxmox.com/pve-docs/chapter-sysadmin.html). Some tips and notes for myself regarding the installation and configuration are added below (e.g. network tips).
3. Confirm summary and start installation. Wait until complete (may take 5–15 minutes depending on hardware).
4. Remove USB and reboot.

--- 

## Linux OS Installation

A regular OS node is a regular Linux server that runs workloads or supporting services, rather than hosting virtual machines for other systems. 

### Example Target

- Distribution: Ubuntu Server LTS
- Role: Worker node

### Install Linux Worker Node

1. Boot target machine from Linux USB, installed from [Chapter 1: Bootable USB](#chapter-1-bootable-usb-general).
2. Start installer (for Ubuntu: `Try or Install Ubuntu Server`). Follow the instructions from the specific distribution's installation guide.
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

### Post-Install Baseline

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

#### USB not detected or not booting

Recreate USB, check boot order, try different USB port, disable Fast Boot.

#### Installer cannot detect internal disk

Switch BIOS storage mode from Intel RST/Optane to AHCI.

#### System freezes during boot ("Your device ran into a problem and needs to restart")

This often happens if Intel RST driver was removed from Storage Controllers but BIOS is still in RST/Optane mode. Boot into Windows Safe Mode to restore:

1. Power off the laptop completely.
2. Remove the USB drive.
3. Turn on and immediately start tapping **F8** or **Shift+F8** repeatedly to enter Windows Recovery/Automatic Repair Mode. This can be tricky on modern laptops due to fast boot times, so you may need to try a few times. In this experiment, it went to a mode where it did not have a network connection and prompted to press Enter to see other recovery options. Here I selected Quick Repair and enabled Hotspot on my mobile phone for network connection.
4. If that doesn't work, go back into the BIOS/UEFI settings and set the SATA Mode to AHCI and boot with Ubuntu on USB:
   - Press power button.
   - Enter BIOS/UEFI (see steps above for explanation).
   - Change SATA Mode to AHCI as explained in the earlier steps for BIOS/UEFI configuration.
   - Save and Exit.
   - Boot from the USB with Linux, such as Ubuntu, and continue the installation.
   - Repeat this 3 times — Windows will boot into Recovery mode.

#### After Proxmox installation, machine keeps rebooting and shows "Boot Option Restoration" (blue screen)

Firmware cannot find or trust the Proxmox EFI boot entry. In this case the problem was that I did not Disable Secure Boot, causing it to fail. Fix it in BIOS/UEFI:

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

#### No network after install

Confirm NIC name, static config, gateway, and DNS; diagnose with:

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

#### `ip a` shows all interfaces down, default route is correct, but gateway is still unreachable

The bridge or physical NIC is not actually up yet, even though the route is correct.

1. Bring up the physical NIC first, for example: `ifup eno1`.
2. Then bring up the bridge: `ifup vmbr0`.
3. Verify both are up: `ip a` should show `UP` on the NIC and `vmbr0`.
4. Test the gateway again: `ping -c 3 192.168.144.1`.
5. If it still fails, restart networking: `systemctl restart networking`, then recheck `ip a` and `ip r`.

#### `systemctl status networking` shows "does not appear to be an IPv4 or IPv6 address" after reconfiguring `/etc/network/interfaces`

**Cause:** typo in IP address (extra character, malformed CIDR, etc.).

1. Check the exact error message.
2. Edit the file: `nano /etc/network/interfaces`
3. Verify the `address` line is exactly: `address 192.168.151.200/20` (no extra characters like `X`).
4. Save, exit, then restart: `systemctl restart networking`
5. Verify bridge is up: `ip a` should show `vmbr0` with the correct IP.

### Performance Issues

#### Node feels slow

Check thermal throttling, disk health, and running services (`htop`, `iostat`, `dmesg`).

---

## Resources

- [Proxmox VE Documentation](https://pve.proxmox.com/pve-docs/)
- [Proxmox VE Installation Guide](https://pve.proxmox.com/wiki/Installation)
- [Ubuntu Documentation](https://documentation.ubuntu.com/)
- [Ubuntu Server Install Tutorial](https://ubuntu.com/tutorials/install-ubuntu-server)

## Useful Commands Reference

Below are some useful commands, but also see other reference documentation for more details, such as [Networking Commands](../network/commands/README.md) and [Storage Commands](../Storage_Background_Commands.md).

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
# Troubleshooting

This document provides guidance for diagnosing and resolving common network issues, particularly those that arise when running a homelab environment.

## Some home network devices cannot connect to the internet

**Symptoms:** Multiple devices (e.g. phone, TV, printer over Ethernet) lose internet access, while others remain unaffected.

**Likely cause:** Proxmox VE running on the home network can cause IP conflicts. When Proxmox creates a Linux bridge (`vmbr0`) on the same subnet as your home LAN, it may respond to ARP requests or DHCP traffic in a way that conflicts with the ISP modem's DHCP assignments. This causes some devices to get duplicate IPs or lose their lease, which breaks connectivity for those devices but not necessarily all of them.

**Diagnosis:**
1. Log in to your ISP's modem/router admin page (typically at `192.168.2.1` or `192.168.1.1`).
2. Look for a connected devices or DHCP leases table.
3. Check for duplicate IP addresses or unexpected entries — this confirms an IP conflict.

**Solutions:**

Partial fix (not fully safe): Reserve static IPs in your ISP modem for all lab devices and configure a static address and internal bridge in Proxmox. This reduces the chance of conflict but does not eliminate it, since Proxmox bridge interfaces can still interfere with LAN traffic.

Recommended fix: Set up a dedicated router for the homelab (e.g. a Raspberry Pi or TP-Link ER605) placed between your ISP modem and all lab devices. This creates a fully isolated subnet for the lab so Proxmox and other lab services can never interfere with the home network.

```
ISP Modem (e.g. 192.168.2.0/24) → Lab Router (e.g. 192.168.10.0/24) → Lab Devices
```

**Interim workaround (while setting up the dedicated router):** Shut down the Proxmox VE host and temporarily install Ubuntu Desktop on it via bootable USB (see [OS and Hypervisor Installation](2_2_OS_Hypervisor.md) for steps). This prevents Proxmox from interfering with the home network on each boot, while still allowing you to use the machine. Once the dedicated router is ready, reinstall Proxmox VE on the host.
# Network Design

A stable network is the foundation of a reliable homelab. This document covers the design decisions: the setup options available, why a dedicated lab router behind the ISP modem is the right choice, the subnet design, and the target network topology.

> See the [Network Reference](../reference/network/README.md) for background knowledge on networking concepts, commands, and troubleshooting tips.

## Table of Contents

- [Network Setup Options](#network-setup-options)
- [Why a Dedicated Router Behind the ISP Modem](#why-a-dedicated-router-behind-the-isp-modem)
- [Hardware & Software](#hardware--software)
  - [Lab Router](#lab-router)
    - [Hardware](#hardware)
    - [Operating System](#operating-system-raspberry-pi-os-lite)
    - [Routing Software Stack](#routing-software-stack-dnsmasq--iptablesnftables)
  - [Managed Switch](#managed-switch)
  - [Ethernet Cables](#ethernet-cables)
- [Network Topology](#network-topology)

---

## Network Setup Options

### Option 1: Lab devices directly on the home network

Connect lab devices (Proxmox hosts, worker nodes) directly to the ISP modem or home switch.

```
ISP Modem → Home Switch → Lab Devices + Home Devices (same network)
```

**Why not:** Lab mistakes — DHCP conflicts, Proxmox bridge misconfiguration, routing loops — directly affect the home network. This is what caused home devices (phone, TV, printer) to lose internet access when Proxmox was first connected: its `vmbr0` bridge interfered with the home LAN's DHCP, creating IP conflicts that were visible in the ISP modem's admin page.

### Option 2: VLANs on the ISP modem

Segment the network using VLANs configured on the ISP modem itself.

**Why not:** Most ISP modems have very limited or no VLAN support. A misconfiguration can break the entire home network. Not practical.

### Option 3: Dedicated router behind the ISP modem (chosen approach)

Place a dedicated lab router between the ISP modem and all lab devices. The lab runs on its own subnet, fully isolated from the home network.

```
ISP Modem (192.168.2.0/24) → Lab Router → Lab Devices (10.42.0.0/20)
```

**Why `10.42.0.0/20` and not `10.0.0.0/20`?** The `10.0.0.0/x` range is extremely common — corporate VPNs, Docker defaults, Kubernetes pod CIDRs, and cloud VPCs all frequently use `10.0.x.x`. If any of these overlap with the lab subnet, routes conflict and traffic breaks. `10.42.0.0/20` is an uncommon slice of the `10.0.0.0/8` private range, so it is unlikely to collide with anything. The `42` is arbitrary — just picked to stay out of the way.

**Why `/20` and not `/24` or `/16`?** A `/24` gives only 254 usable addresses — that is enough for a flat network, but too small once you start carving out VLANs (each VLAN gets its own `/24` subnet within the parent range). A `/20` gives 4094 addresses and fits 16 × `/24` subnets comfortably — plenty of room for management, monitoring, Kubernetes, and future VLANs without ever running out. A `/16` (65k addresses) would also work but is far more than needed for a home lab.

---

## Why a Dedicated Router Behind the ISP Modem

**Full isolation (maintaining home network is not in my homelab's scope):** The lab runs on its own subnet with its own DHCP and firewall. Lab mistakes — DHCP conflicts, Proxmox bridge issues, Kubernetes networking — are contained within the lab network and never reach home devices. Avoid changing the ISP Modem's core configuration when others in the house depend on it for internet access. Changing the home network configuration can break connectivity for everyone, so it's best to leave it as-is and put your own router behind it for the lab. Furthermore, the ISP modem may have limited or no VLAN support, making it unsuitable for isolating your lab network. Finally, it is not in my homelab's scope to maintain the home network, so I want to keep it untouched and let the ISP modem handle the home network while I experiment freely in my lab network.

**Keeps the ISP modem intact:** Other people in the house depend on the ISP modem for WiFi and internet. Replacing it or changing its configuration would mean taking ownership of the entire home network. Keeping it untouched means home connectivity stays stable regardless of what happens in the lab. See [Goals](../1_Goals_Hardware_LocalEnvSetup.md#goals), in short: I am NOT planning to self-host everything and make the home network dependent on my lab!

**Learn networking:** Building and running your own router is a hands-on way to learn subnetting, routing, DHCP, firewall rules, and VLANs in a real environment.

**It is fun:** Designing and configuring your own network infrastructure is genuinely enjoyable.

**Classic mistakes that break home networks (avoid these):**

- Running a DHCP server on the same subnet as home devices
- Changing DNS settings on the ISP modem
- Connecting Proxmox or Kubernetes nodes directly to the home network
- Misconfiguring Proxmox bridges (can cause broadcast loops)
- Running firewall experiments on the home LAN

---

## Hardware & Software

### Background Knowledge: Raspberry Pi, Hardware & OS

> See [Raspberry Pi: Hardware & OS Background](../reference/raspberry_pi_hardware_os.md) for detailed background on the Raspberry Pi hardware, ARM vs x86 architecture, SD cards, the operating system and kernel, the boot process, flashing, network interfaces, GPIO, `raspi-config`, and headless operation.

### Lab Router

A Raspberry Pi is used as the dedicated lab router. It is cost-effective, educational, and provides full control over routing, DHCP, firewall rules, and future VLANs.

#### Hardware

- **Raspberry Pi 4 or later** — the compute unit running the router software.
- **SD card with Raspberry Pi OS Lite (64-bit) flashed** — primary storage. Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) — a free tool from the Raspberry Pi Foundation. Download and install it on your laptop, select the OS image and your SD card as the target, and click Write. It downloads the image, writes it, and verifies it. Then insert the SD card into the Pi and it boots from it automatically.
    - **No SD card reader on your laptop?** Most laptops do not have a built-in SD card reader (and even those that do often only accept full-size SD, not microSD). Use a USB SD card reader/adapter — a small dongle that accepts a microSD card and plugs into a USB port. I bought the "ISY ICR-120 USB 2.0-kaartlezer USB 2.0" for 6.99 EUR at MediaMarkt (ISY is MediaMarkt's store brand, it is a reputable and affordable brand). Plug it into your laptop, insert the microSD card, and it appears as a removable drive that Raspberry Pi Imager can write to.
- **USB-to-Ethernet adapter (`eth1`)** — adds the LAN interface. I bought the "TP-LINK UE306" for 12.99 EUR at MediaMarkt because "TP-LINK" is a reliable brand and affordable (do not buy the "TP-LINK UE300C" — it is USB-C, which the Pi 4 does not have). Plug into a USB-A port; Raspberry Pi OS includes the `r8152` driver by default, so it is detected automatically as `eth1`.
- **Access to the ISP modem admin page** — to reserve a static IP for the Pi's `eth0` by MAC address and check for IP conflicts. Typically at `192.168.2.1` or `192.168.1.1`.

#### Operating System: Raspberry Pi OS Lite

Raspberry Pi OS is the officially supported OS for the Pi, maintained by the Raspberry Pi Foundation. It is based on Debian, well-tested on Pi hardware, and includes Pi-specific optimisations and drivers out of the box (e.g. the `r8152` USB-Ethernet driver, GPU memory split, hardware interfaces). "Lite" means no desktop environment — just a minimal command-line system, which is exactly what you want for a headless appliance like a router. Ubuntu Server also works on the Pi, but it requires more manual configuration for Pi-specific hardware, has a larger footprint, and offers no real advantage for this use case. Stick with Raspberry Pi OS Lite.

**Why not pfSense or OpenWRT?** Both are purpose-built router/firewall OSes with polished web UIs and pre-configured networking stacks. However, the goal of this homelab ([see personal goals](../1_Goals_Hardware_LocalEnvSetup.md)) is to learn Linux networking by doing it yourself — configuring IP forwarding, DHCP, NAT, and firewall rules manually gives you a much deeper understanding than clicking through a GUI. You can always switch to OpenWRT or pfSense later once you understand what they are doing under the hood. Additionally, pfSense (FreeBSD-based) has limited ARM/Pi support, and OpenWRT replaces the entire OS — losing the familiar Debian/apt ecosystem and Pi-specific driver support that Raspberry Pi OS provides.

#### Routing Software Stack: dnsmasq + iptables/nftables

The router runs individual Linux tools handling each routing function:

- **dnsmasq** — provides DHCP and DNS forwarding. It is lightweight, simple to configure (a single config file), and does exactly what a homelab router needs: hand out IP leases, serve as the local DNS resolver, and forward external queries upstream. It is the standard choice for small networks and embedded routers (OpenWRT uses it under the hood too).
- **iptables/nftables** — handles NAT (masquerading) and firewall rules. These are built into the Linux kernel's netfilter framework — no extra software needed.
- **IP forwarding** (`net.ipv4.ip_forward=1`) — enables the Pi to route packets between `eth0` (WAN) and `eth1` (LAN). A single kernel parameter.

**Why not PowerDNS, BIND, or ISC DHCP?** These are production-grade tools designed for large-scale or complex DNS/DHCP deployments. PowerDNS is an authoritative DNS server with a database backend (MySQL/PostgreSQL) — it excels at hosting thousands of zones with API-driven record management and DNSSEC signing, but requires a database, a separate recursor process for forwarding, and significantly more configuration than dnsmasq. BIND is the oldest and most widely deployed DNS server on the internet — it supports authoritative hosting, recursive resolution, DNSSEC, split-horizon DNS, and complex zone delegation, but its configuration (`named.conf` + zone files) is notoriously verbose and error-prone for simple use cases. ISC DHCP (now end-of-life, succeeded by Kea) is a standalone DHCP server with support for failover, dynamic DNS updates, and complex pool configurations — but it only handles DHCP, so you still need a separate DNS forwarder. Kea, its successor, adds a REST API and database backends but is even more complex to set up.

For a homelab router that just needs to hand out leases on one subnet and forward DNS queries, all of these are overkill. dnsmasq handles both DHCP and DNS in a single lightweight process with a single config file — no databases, no zone files, no separate daemons. It starts in milliseconds, uses minimal memory, and is trivial to configure and debug. Finally, `dnsmasq` is widely used in embedded routers, OpenWRT, and small office/home office (SOHO) devices — it is battle-tested for exactly this use case.

---

### Managed Switch

**Managed switch** — expands LAN ports and enables VLANs. I bought the "NETGEAR GS305E" for 24.99 EUR at MediaMarkt because "NETGEAR" is a reputable brand and affordable (the "TP-LINK TL-SG105E" is a good alternative). See [User Manual](https://www.netgear.com/support/product/gs305e)

### Ethernet Cables

**Ethernet cables** (Cat6 or better for gigabit speeds):
- **Long Ethernet cable for WAN (ISP modem → lab router)** 1 cable (10 m (ensures it can reach the router, such as if it needs to go through the wall or a conduit to a different floor (e.g. your work room), etc.)). I bought the "ISY IPC-6100-1-GB Netwerkkabel 10 m Wit" at MediaMarkt for 18.99 EUR because "ISY" (MediaMarkt's own store brand) is a reputable brand and affordable.
- **Lab router → lab switch:** 1 cable (0.75 m). I bought the "ISY IPC-1012 CAT6A U/UTP Slim Netwerkkabel 0,75 m Wit" at MediaMarkt for 9.99 EUR (same reasoning for this brand as above).
- **Lab switch → lab devices:** 1 cable per device (same model as above).

---

## Network Topology

> See [Node Setup](../1_Goals_Hardware_LocalEnvSetup.md#node-setup) for the physical nodes in the homelab. The network topology diagram below shows how the nodes are connected to the lab router and switch, and how the lab network is isolated from the home network.

Full network topology (in .md diagram format to save space (no image file needed for this setup)):
```
Internet
    │
ISP Modem/Router
(192.168.2.0/24)
    │
    ├── Home devices
    │
    └── Raspberry Pi Router (Homelab Network: 10.42.0.0/20) `eth0` (WAN; connected to ISP Modem) → `eth1` (LAN; connected to switch)
            │
      Managed Switch (expands LAN ports; router only has one LAN port)
            │
            ├─ VLAN 1  Native (unused — no production traffic)
            │
            ├─ VLAN 10 Management      (10.42.10.0/24)
            │    ├─ 10.42.10.1   Router (Raspberry Pi — gateway for all VLANs)
            │    ├─ 10.42.10.2   Switch (NETGEAR GS305E — management interface)
            │    ├─ 10.42.10.10  PVE1 (physical machine: Proxmox VE host 1)
            │    └─ 10.42.10.11  PVE2 (physical machine: Proxmox VE host 2)
            │
            ├─ VLAN 20 Services        (10.42.20.0/24)
            │    ├─ 10.42.20.x   Kubernetes nodes, application VMs
            │    └─ ...          (Grafana, Prometheus, Home Assistant, ArgoCD, etc.)
            │
            └─ VLAN 30 IoT            (10.42.30.0/24)
                 ├─ 10.42.30.x   Smart plugs, sensors, Zigbee gateways
                 └─ ...          (all smart/IoT devices)
```

### Subnet & VLAN Design

| Subnet | VLAN | Purpose |
|--------|------|---------|
| — | 1 (native) | Unused — no production traffic, fallback recovery only |
| 10.42.10.0/24 | 10 | Management — router, switch, Proxmox host management IPs |
| 10.42.20.0/24 | 20 | Services — Kubernetes, application VMs, monitoring, databases |
| 10.42.30.0/24 | 30 | IoT — smart plugs, sensors, Zigbee gateways, energy meters |

### IoT Isolation

IoT devices are often the least secure devices in a home. By isolating them on VLAN 30:

```
IoT (VLAN 30) → Services (VLAN 20) = Allowed (sensors push data to Home Assistant)
IoT (VLAN 30) → Management (VLAN 10) = Blocked (a compromised smart bulb cannot probe Proxmox)
```

Firewall rules on the router enforce this — inter-VLAN traffic is denied by default, then specific flows are allowed explicitly.

**Why a dedicated Management VLAN (VLAN 10) instead of native VLAN (VLAN 1):**

1. **Closer to enterprise practice:** In production environments, the native VLAN is left unused or disabled entirely. All real traffic — including management — is explicitly tagged. Learning this pattern now means fewer surprises when working with enterprise infrastructure.
2. **Easier to expand later:** Adding new VLANs is uniform — every VLAN is tagged, every subnet has a matching VLAN ID (VLAN 10 → 10.42.10.0/24, VLAN 20 → 10.42.20.0/24, VLAN 30 → 10.42.30.0/24). No special case for "the one VLAN that happens to be untagged."
3. **Cleaner trunk configuration:** All production VLANs are tagged on trunk ports. The native VLAN exists only as a fallback: if VLAN tagging breaks entirely, you can still reach the switch management interface on VLAN 1 to fix the configuration (connect a laptop directly to a port, assign a static IP, access the switch web UI).
4. **Security:** Native VLAN hopping attacks (802.1Q double-tagging) exploit the fact that the native VLAN is untagged. By not carrying any production traffic on the native VLAN, this attack vector is eliminated.

TODO: document the recovery procedure — connect laptop directly to switch, assign static IP on the switch's VLAN 1 default, access switch web UI to fix VLAN config.

### Switch Port Assignments (NETGEAR GS305E — 5 ports)

| Port | Connected Device | VLAN Membership |
|------|-----------------|-----------------|
| 1 | Pi Router (eth1) | Untagged: 1 (native, unused) + Tagged: 10, 20, 30 (trunk port) |
| 2 | PVE1 (Proxmox host 1) | Untagged: 1 (native, unused) + Tagged: 10, 20, 30 |
| 3 | PVE2 (Proxmox host 2) | Untagged: 1 (native, unused) + Tagged: 10, 20, 30 |
| 4 | (spare) | Untagged: 1 (native) |
| 5 | (spare) | Untagged: 1 (native) |

#### How to read this table

> See [Network Devices — Tagged vs Untagged](../reference/network/Network_Devices.md#tagged-vs-untagged-8021q-vlan-tagging) for a full explanation of what tagged and untagged mean, how frames flow through the switch, and when to use each mode.

Each port can be a member of multiple VLANs simultaneously. The "VLAN Membership" column lists **all** VLANs that a port participates in, separated by `+`. The keyword before each VLAN entry tells the switch how to handle frames for that VLAN on that port:

- **Untagged: 1** — Frames for VLAN 1 are sent/received **without** a VLAN tag in the [Ethernet frame header](../reference/network/Network_Models_and_Packets.md#anatomy-of-a-frame-layer-2). In this design, the native VLAN carries no production traffic — it exists only as a fallback recovery path. If all VLAN tagging breaks, untagged frames still flow, allowing you to reach the switch management interface.

- **Tagged: 10, 20, 30** — Frames for VLANs 10, 20, and 30 are sent/received **with** an 802.1Q VLAN tag in the [Ethernet frame header](../reference/network/Network_Models_and_Packets.md#anatomy-of-a-frame-layer-2) (a 4-byte field that says "this frame belongs to VLAN X"). The device on the other end must understand VLAN tags and process them — the Pi router uses sub-interfaces (`eth1.10`, `eth1.20`, `eth1.30`) and Proxmox uses VLAN-aware bridges to separate tagged traffic into the correct virtual networks.

**The `+` does NOT mean "10, 20, and 30 are untagged from VLAN 1"** — it means the port carries four independent traffic streams: one untagged (VLAN 1, unused) and three tagged (VLAN 10, VLAN 20, VLAN 30). They coexist on the same physical cable but are completely separate at the logical level.

#### Per-port explanation

**Port 1 — Pi Router (eth1):**
The router is the gateway for all VLANs. Its physical `eth1` interface is on the native VLAN (unused — no IP assigned). Tagged traffic arrives on sub-interfaces `eth1.10` (VLAN 10, IP `10.42.10.1`), `eth1.20` (VLAN 20, IP `10.42.20.1`), and `eth1.30` (VLAN 30, IP `10.42.30.1`). The router forwards traffic between VLANs (inter-VLAN routing) and applies firewall rules. This is a "trunk port" — it carries all VLANs.

**Ports 2–3 — Proxmox hosts (PVE1, PVE2):**
Each Proxmox host has one physical NIC connected to the switch. Management traffic (SSH to the host, Proxmox web UI) flows tagged on VLAN 10 — the host's management IP (`10.42.10.10` or `.11`) is on a VLAN-aware bridge tagged to VLAN 10. VMs running on the host are placed into VLANs via Proxmox's VLAN-aware bridge (`vmbr0`): a service VM gets tagged into VLAN 20, an IoT gateway VM into VLAN 30. The switch delivers tagged frames for those VLANs to the port, and Proxmox's bridge routes them to the correct VM.

**Ports 4–5 — Spare:**
Simple access ports — only untagged VLAN 1. Any device plugged in lands on the native VLAN (no production access by default). To give a device access to a specific VLAN, reconfigure the port.

#### Why tagged for service VLANs instead of untagged (access ports)?

An alternative design would be to assign each port to a single VLAN as untagged (e.g. port 2 = untagged VLAN 10, port 3 = untagged VLAN 20). This is simpler per-port but has a critical limitation: **you only get 5 ports total**, and each device would be locked to a single VLAN. Since Proxmox hosts run VMs in multiple VLANs simultaneously (management + services + IoT on the same physical machine), the host's port MUST carry multiple VLANs — which requires tagging.

**Summary of the tagging logic:**
- **VLAN 1 (native): untagged** — carries no production traffic; exists as a fallback recovery path if VLAN tagging breaks.
- **VLAN 10 (management): tagged** — router, switch, Proxmox hosts; requires VLAN-aware sub-interface/bridge.
- **VLAN 20 (services): tagged** — Kubernetes, all hosted applications; requires VLAN-aware bridge/sub-interface.
- **VLAN 30 (IoT): tagged** — smart devices, sensors; isolated from management for security.

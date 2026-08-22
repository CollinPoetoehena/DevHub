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
            ├─ Native VLAN (untagged)  — Management (10.42.0.0/24)
            │    ├─ 10.42.0.1   Router (Raspberry Pi — gateway for all VLANs)
            │    ├─ 10.42.0.2   Switch (NETGEAR GS305E — management interface)
            │    ├─ 10.42.0.10  PVE1 (physical machine: Proxmox VE host 1)
            │    └─ 10.42.0.11  PVE2 (physical machine: Proxmox VE host 2)
            │
            ├─ VLAN 20 Monitoring      (10.42.20.0/24)
            │    ├─ 10.42.20.10  Monitoring VM1
            │    └─ ...          (other monitoring VMs, Prometheus, Grafana, alerting, etc.)
            │
            └─ VLAN 30 Workloads       (10.42.30.0/24)
                 ├─ 10.42.30.x   Kubernetes nodes, application VMs, databases, or any non-monitoring service
                 └─ ...          (other workload VMs, Kubernetes pods, etc.)
```

### Subnet & VLAN Design

| Subnet | VLAN | Purpose |
|--------|------|---------|
| 10.42.0.0/24 | Native (untagged, VLAN 1) | Management — router, switch, Proxmox host management IPs |
| 10.42.20.0/24 | 20 | Monitoring — Grafana, Prometheus, alerting VMs |
| 10.42.30.0/24 | 30 | Workloads — Kubernetes, application VMs, databases, and other services |

**Why management lives on the native (untagged) VLAN instead of a dedicated VLAN 10:**

1. **Always-reachable recovery path:** The router's physical `eth1` interface must have an IP on the native VLAN for the trunk to function. If the VLAN configuration on the switch ever breaks (bad config, firmware bug), tagged traffic stops flowing — but untagged (native) traffic still works. Keeping management on the native VLAN means you can always reach the router and switch to fix things, even when VLANs are misconfigured.
2. **Switch management defaults to VLAN 1:** The NETGEAR GS305E's management interface lives on the default/native VLAN (VLAN 1). While it *can* be moved to a tagged VLAN, doing so means a VLAN misconfiguration locks you out of the switch entirely — requiring a factory reset (hold the reset button for 10 seconds) to regain access.
3. **Less complexity for a homelab:** A dedicated management VLAN adds value in enterprise environments where hundreds of ports exist and you need to restrict which physical ports can reach management interfaces. In a 5-port switch where all ports are already trusted (physically in your home), it adds configuration without meaningful security gain.
4. **The router and switch already have their IPs on 10.42.0.x:** The router is `10.42.0.1` (its `eth1` static IP) and the switch is `10.42.0.2` (DHCP static lease). Moving them to a VLAN would require changing established addressing and SSH tunnel configurations.

### Switch Port Assignments (NETGEAR GS305E — 5 ports)

| Port | Connected Device | VLAN Membership |
|------|-----------------|-----------------|
| 1 | Pi Router (eth1) | Untagged: 1 (native) + Tagged: 20, 30 (trunk port) |
| 2 | PVE1 (Proxmox host 1) | Untagged: 1 (native) + Tagged: 20, 30 |
| 3 | PVE2 (Proxmox host 2) | Untagged: 1 (native) + Tagged: 20, 30 |
| 4 | (spare) | Untagged: 1 (native) |
| 5 | (spare) | Untagged: 1 (native) |

#### How to read this table

> See [Network Devices — Tagged vs Untagged](../reference/network/Network_Devices.md#tagged-vs-untagged-8021q-vlan-tagging) for a full explanation of what tagged and untagged mean, how frames flow through the switch, and when to use each mode.

Each port can be a member of multiple VLANs simultaneously. The "VLAN Membership" column lists **all** VLANs that a port participates in, separated by `+`. The keyword before each VLAN entry tells the switch how to handle frames for that VLAN on that port:

- **Untagged: 1** — Frames for VLAN 1 are sent/received **without** a VLAN tag in the Ethernet header. The device on the other end of the cable sees plain Ethernet frames with no VLAN information — it doesn't need to know VLANs exist. This is how the management interfaces work: the Pi's `eth1` has IP `10.42.0.1`, the Proxmox hosts have `10.42.0.10`/`.11` — all on plain, untagged Ethernet.

- **Tagged: 20, 30** — Frames for VLANs 20 and 30 are sent/received **with** an 802.1Q VLAN tag in the Ethernet header (a 4-byte field that says "this frame belongs to VLAN X"). The device on the other end must understand VLAN tags and process them — the Pi uses sub-interfaces (`eth1.20`, `eth1.30`) and Proxmox uses VLAN-aware bridges to separate tagged traffic into the correct virtual networks.

**The `+` does NOT mean "20 and 30 are untagged from VLAN 1"** — it means the port carries three independent traffic streams: one untagged (VLAN 1) and two tagged (VLAN 20, VLAN 30). They coexist on the same physical cable but are completely separate at the logical level.

#### Per-port explanation

**Port 1 — Pi Router (eth1):**
The router is the gateway for all VLANs. It receives untagged management traffic on `eth1` (VLAN 1, IP `10.42.0.1`) and tagged traffic on sub-interfaces `eth1.20` (VLAN 20, IP `10.42.20.1`) and `eth1.30` (VLAN 30, IP `10.42.30.1`). The router forwards traffic between VLANs (inter-VLAN routing) and applies firewall rules. This is a "trunk port" — it carries all VLANs.

**Ports 2–3 — Proxmox hosts (PVE1, PVE2):**
Each Proxmox host has one physical NIC connected to the switch. Management traffic (SSH to the host, Proxmox web UI) flows untagged on VLAN 1 — so the host's management IP (`10.42.0.10` or `.11`) works without any VLAN configuration on the base interface. VMs running on the host are placed into VLANs via Proxmox's VLAN-aware bridge (`vmbr0`): a monitoring VM gets tagged into VLAN 20, a workload VM into VLAN 30. The switch delivers tagged frames for those VLANs to the port, and Proxmox's bridge routes them to the correct VM.

**Ports 4–5 — Spare:**
Simple access ports — only untagged VLAN 1. Any device plugged in gets a management network IP via DHCP. No VLAN awareness required on the connected device.

#### Why tagged for workload VLANs instead of untagged (access ports)?

An alternative design would be to assign each port to a single VLAN as untagged (e.g. port 2 = untagged VLAN 20, port 3 = untagged VLAN 30). This is simpler per-port but has a critical limitation: **you only get 5 ports total**, and each device would be locked to a single VLAN. Since Proxmox hosts run VMs in multiple VLANs simultaneously (monitoring VMs + workload VMs on the same physical machine), the host's port MUST carry multiple VLANs — which requires tagging. The management VLAN stays untagged so you can always reach the host even if VLAN tagging breaks.

**Summary of the tagging logic:**
- **VLAN 1 (management): untagged** — ensures infrastructure is always reachable; no VLAN-aware config needed on base interfaces.
- **VLAN 20 (monitoring): tagged** — VMs in this VLAN are placed there by Proxmox/router; requires VLAN-aware bridge/sub-interface.
- **VLAN 30 (workloads): tagged** — same reasoning as VLAN 20.

# Network & Hosts Design

**TODO: this is now fully done and checked; only at the end of the homelab check one more time if this is still the final setup and update some things if needed; but the general things generally will remain as designed in this document!**

A stable network is the foundation of a reliable homelab. This document covers the design decisions: the setup options available, why a dedicated lab router behind the ISP modem is the right choice, the subnet design, and the target network topology. The lab network is **dual-stack (IPv4 + IPv6)**.

See the [Network Reference](../../../reference/network/README.md) for background knowledge on networking concepts, commands, and troubleshooting tips.

## Table of Contents
- [Network Setup Options](#network-setup-options)
  - [Option 1: Lab devices directly on the home network](#option-1-lab-devices-directly-on-the-home-network)
  - [Option 2: VLANs on the ISP modem](#option-2-vlans-on-the-isp-modem)
  - [Option 3: Dedicated router behind the ISP modem](#option-3-dedicated-router-behind-the-isp-modem)
  - [Chosen Option: Dedicated Router Behind the ISP Modem](#why-a-dedicated-router-behind-the-isp-modem)
- [Hardware & Software](#hardware--software)
  - [Background Knowledge: Raspberry Pi, Hardware & OS](#background-knowledge-raspberry-pi-hardware--os)
  - [Lab Router](#lab-router)
    - [Router Hardware](#router-hardware)
    - [Router OS: Raspberry Pi OS Lite](#router-os-raspberry-pi-os-lite)
    - [Routing Software Stack: dnsmasq + nftables](#routing-software-stack-dnsmasq--nftables)
  - [Managed Switch](#managed-switch)
  - [Ethernet Cables](#ethernet-cables)
- [Network Topology & Design](#network-topology--design)
  - [IPv6 Addressing (ULA + NAT66) on the Lab Network](#ipv6-addressing-ula--nat66-on-the-lab-network)
  - [Jumphost: Secure Access to Lab Network](#jumphost-secure-access-to-lab-network)
  - [Subnet & VLAN Design](#subnet--vlan-design)
    - [Why VLAN 1 (native) is not used — all traffic is explicitly VLAN-tagged](#why-vlan-1-native-is-not-used--all-traffic-is-explicitly-vlan-tagged)
    - [Why a dedicated Management VLAN (VLAN 10)](#why-a-dedicated-management-vlan-vlan-10)
    - [IoT Isolation](#iot-isolation)
    - [Switch Port Assignments](#switch-port-assignments)

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

### Option 3: Dedicated router behind the ISP modem

Place a dedicated lab router between the ISP modem and all lab devices. The lab runs on its own subnet, fully isolated from the home network, and is dual-stack (IPv4 + IPv6).

```
ISP Modem (192.168.2.0/24) → Lab Router → Lab Devices (10.42.0.0/20 + fd42::/48)
```

**Why `10.42.0.0/20` and not `10.0.0.0/20`?** The `10.0.0.0/x` range is extremely common — corporate VPNs, Docker defaults, Kubernetes pod CIDRs, and cloud VPCs all frequently use `10.0.x.x`. If any of these overlap with the lab subnet, routes conflict and traffic breaks. `10.42.0.0/20` is an uncommon slice of the `10.0.0.0/8` private range, so it is unlikely to collide with anything. The `42` is arbitrary — just picked to stay out of the way.

**Why `/20` and not `/24` or `/16`?** A `/24` gives only 254 usable addresses — that is enough for a flat network, but too small once you start carving out VLANs (each VLAN gets its own `/24` subnet within the parent range). A `/20` gives 4094 addresses and fits 16 × `/24` subnets comfortably — plenty of room for management, monitoring, Kubernetes, and future VLANs without ever running out. A `/16` (65k addresses) would also work but is far more than needed for a home lab.

**Why `fd42::/48` for IPv6 (ULA) and not a delegated prefix?** IPv6 normally needs no NAT at all — every device gets a globally routable address, but only if the upstream router (the ISP modem) delegates a usable prefix downstream (DHCPv6-PD). Consumer ISP modems usually either don't support this at all or only delegate a single `/64` — not enough for three VLANs, and it can change on every modem reboot, which would renumber the entire lab. Instead, the lab uses a Unique Local Address (ULA, `fd00::/8`) range: **`fd42::/48`**, split into one `/64` per VLAN (`fd42:10::/64`, `fd42:20::/64`, `fd42:30::/64`). This mirrors the IPv4 supernet in spirit (the "42" is the same arbitrary, memorable choice) — stable, private, and immune to ISP renumbering. Outbound IPv6 traffic is masqueraded (NAT66) to the router's WAN address until real prefix delegation is available; see [IPv6 Addressing (ULA + NAT66) on the Lab Network](#ipv6-addressing-ula--nat66-on-the-lab-network) below.

### Chosen Option: Dedicated Router Behind the ISP Modem

**Full isolation (maintaining home network is not in my homelab's scope):** The lab runs on its own subnet with its own DHCP and firewall. Lab mistakes — DHCP conflicts, Proxmox bridge issues, Kubernetes networking — are contained within the lab network and never reach home devices. Avoid changing the ISP Modem's core configuration when others in the house depend on it for internet access. Changing the home network configuration can break connectivity for everyone, so it's best to leave it as-is and put your own router behind it for the lab. Furthermore, the ISP modem may have limited or no VLAN support, making it unsuitable for isolating your lab network. Finally, it is not in my homelab's scope to maintain the home network, so I want to keep it untouched and let the ISP modem handle the home network while I experiment freely in my lab network.

**Keeps the ISP modem intact:** Other people in the house depend on the ISP modem for WiFi and internet. Replacing it or changing its configuration would mean taking ownership of the entire home network. Keeping it untouched means home connectivity stays stable regardless of what happens in the lab. See [Goals](../1_Design/0_Goals.md), in short: I am NOT planning to self-host everything and make the home network dependent on my lab!

**Learn networking:** Building and running your own router is a hands-on way to learn subnetting, routing, DHCP, firewall rules, VLANs, and dual-stack IPv6 (SLAAC, Router Advertisements, Neighbour Discovery) in a real environment — knowledge that only comes from actually running it, not from reading about it.

**It is fun:** Designing and configuring your own network infrastructure is genuinely enjoyable.

**Classic mistakes that break home networks (avoid these):**
- Running a DHCP server (or IPv6 Router Advertisements) on the same subnet as home devices
- Changing DNS settings on the ISP modem
- Connecting Proxmox or Kubernetes nodes directly to the home network
- Misconfiguring Proxmox bridges (can cause broadcast loops)
- Running firewall experiments on the home LAN

---

## Hardware & Software

### Background Knowledge: Raspberry Pi, Hardware & OS

See [Raspberry Pi](../../../reference/os_hardware/Raspberry_pi.md) for detailed background on the Raspberry Pi hardware, ARM vs x86 architecture, SD cards, the operating system and kernel, the boot process, flashing, network interfaces, GPIO, raspi-config, and headless operation.

### Lab Router

A Raspberry Pi is used as the dedicated lab router. It is cost-effective, educational, and provides full control over routing, DHCP, firewall rules, VLANs, and dual-stack IPv6.

#### Router Hardware

- **Raspberry Pi 4 or later** — the compute unit running the router software.
- **SD card with Raspberry Pi OS Lite (64-bit) flashed** — primary storage. Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) — a free tool from the Raspberry Pi Foundation. Download and install it on your laptop, select the OS image and your SD card as the target, and click Write. It downloads the image, writes it, and verifies it. Then insert the SD card into the Pi and it boots from it automatically.
    - **No SD card reader on your laptop?** Most laptops do not have a built-in SD card reader (and even those that do often only accept full-size SD, not microSD). Use a USB SD card reader/adapter — a small dongle that accepts a microSD card and plugs into a USB port. I bought the "ISY ICR-120 USB 2.0-kaartlezer USB 2.0" for 6.99 EUR at MediaMarkt (ISY is MediaMarkt's store brand, it is a reputable and affordable brand). Plug it into your laptop, insert the microSD card, and it appears as a removable drive that Raspberry Pi Imager can write to.
- **USB-to-Ethernet adapter (`eth1`)** — adds the LAN interface. I bought the "TP-LINK UE306" for 12.99 EUR at MediaMarkt because "TP-LINK" is a reliable brand and affordable (do not buy the "TP-LINK UE300C" — it is USB-C, which the Pi 4 does not have). Plug into a USB-A port; Raspberry Pi OS includes the `r8152` driver by default, so it is detected automatically as `eth1`.
- **Access to the ISP modem admin page** — to reserve a static IP for the Pi's `eth0` by MAC address and check for IP conflicts. Typically at `192.168.2.254`, `192.168.2.1` or `192.168.1.1`.

#### Router OS: Raspberry Pi OS Lite

Raspberry Pi OS is the officially supported OS for the Pi, maintained by the Raspberry Pi Foundation. It is based on Debian, well-tested on Pi hardware, and includes Pi-specific optimisations and drivers out of the box (e.g. the `r8152` USB-Ethernet driver, GPU memory split, hardware interfaces). "Lite" means no desktop environment — just a minimal command-line system, which is exactly what you want for a headless appliance like a router. Ubuntu Server also works on the Pi, but it requires more manual configuration for Pi-specific hardware, has a larger footprint, and offers no real advantage for this use case. Stick with Raspberry Pi OS Lite.

**Why not pfSense, OpenWRT or a similar dedicated router OS/appliance?** These are purpose-built router/firewall OSes with polished web UIs and pre-configured networking stacks. However, the goal of this homelab ([see personal goals](../1_Design/0_Goals.md)) is to learn Linux networking by doing it yourself — configuring IP forwarding, DHCP, NAT, and firewall rules manually gives you a much deeper understanding than clicking through a GUI. Furthermore, **documentation as code** is used with this setup because the configuration and setup steps are fully captured in version-controlled files (e.g. Ansible playbooks and variables, etc.) instead of configured through a web interface, making it easier to track changes, reproduce the environment, and share knowledge. Finally, this is much more flexible and educational for a homelab environment focused on learning and experimentation, also making it a lot more fun.

#### Routing Software Stack: dnsmasq + nftables

The router runs individual Linux tools handling each routing function:
- **dnsmasq** — provides DHCP, DNS forwarding, and (dual-stack) IPv6 Router Advertisements/SLAAC. It is lightweight, simple to configure (a single config file), and does exactly what a homelab router needs: hand out IPv4 leases, announce IPv6 prefixes so lab devices self-configure via SLAAC, serve as the local DNS resolver for both address families, and forward external queries upstream. There is no "DHCPv6 server" in the classic stateful sense here — IPv6 hosts derive their own address from the Router Advertisement, which is the modern, standards-preferred way to address a network and is what dnsmasq's `enable-ra` + `ra-names` options provide. It is the standard choice for small networks and embedded routers (OpenWRT uses it under the hood too).
- **nftables** — handles NAT (masquerading, including NAT66 for IPv6) and firewall rules. It is built into the Linux kernel's netfilter framework — no extra software needed. Using the `inet` table family means one ruleset covers both IPv4 and IPv6 at once, instead of maintaining iptables and ip6tables rules side by side that could drift apart.
- **IP forwarding** — enables the Pi to route packets between eth0 (WAN) and eth1 (LAN). This is now **two independent kernel parameters**: `net.ipv4.ip_forward=1` for IPv4 and `net.ipv6.conf.all.forwarding=1` for IPv6. Forgetting the second one is the single most common way a "dual-stack" router silently ends up only routing IPv4.

**Why nftables and not iptables or another alternative like firewalld or ufw?** nftables is the modern replacement for iptables, offering a more consistent and flexible syntax, better performance, and easier maintenance. iptables is still widely used and supported, but it is considered legacy, and its syntax can be cumbersome for complex rulesets — and, crucially, it needs a separate `ip6tables` rule set to cover IPv6, which is exactly the kind of duplication that causes an "IPv6-enabled" firewall to quietly stay IPv4-only. firewalld is a higher-level abstraction over iptables/nftables, providing dynamic rule management and a simpler interface, but it adds an extra layer of complexity and is less transparent for learning purposes. ufw is an even higher-level abstraction aimed at simplifying firewall management for end users, but it hides the underlying rules and is not suitable for learning or fine-grained control, and for a router (NAT, per-interface forwarding, inter-VLAN policy) it ends up generating the same raw iptables underneath anyway. For a homelab router where the goal is to understand and control the underlying firewall rules across both address families, nftables is the most suitable choice. Also, the configuration and maintenance of nftables is straightforward and fully transparent, making it ideal for educational purposes in a homelab environment. Finally, nftables is the modern, future-proof choice for Linux firewall management. See for all details the [router Ansible role](../../ansible/roles/router/README.md) (specifically the [firewall.yml task](../../ansible/roles/router/tasks/firewall.yml)).

**Why not PowerDNS, BIND, or ISC DHCP?** These are production-grade tools designed for large-scale or complex DNS/DHCP deployments. PowerDNS is an authoritative DNS server with a database backend (MySQL/PostgreSQL) — it excels at hosting thousands of zones with API-driven record management and DNSSEC signing, but requires a database, a separate recursor process for forwarding, and significantly more configuration than dnsmasq. BIND is the oldest and most widely deployed DNS server on the internet — it supports authoritative hosting, recursive resolution, DNSSEC, split-horizon DNS, and complex zone delegation, but its configuration (named.conf + zone files) is notoriously verbose and error-prone for simple use cases. ISC DHCP (now end-of-life, succeeded by Kea) is a standalone DHCP server with support for failover, dynamic DNS updates, and complex pool configurations — but it only handles DHCP (and its IPv6 support never gained the same traction as DHCPv4), so you still need a separate DNS forwarder and RA sender. Kea, its successor, adds a REST API and database backends but is even more complex to set up. For a homelab router that just needs to hand out leases on one subnet, announce IPv6 prefixes, and forward DNS queries, all of these are overkill. dnsmasq handles DHCP, DNS, and Router Advertisements in a single lightweight process with a single config file — no databases, no zone files, no separate daemons. It starts in milliseconds, uses minimal memory, and is trivial to configure and debug. Finally, dnsmasq is widely used in embedded routers, OpenWRT, and small office/home office (SOHO) devices — it is battle-tested for exactly this use case.

### Managed Switch

**Managed switch** — expands LAN ports and enables VLANs. I bought the "NETGEAR GS305E" for 24.99 EUR at MediaMarkt because "NETGEAR" is a reputable brand and affordable (the "TP-LINK TL-SG105E" is a good alternative). See [User Manual](https://www.netgear.com/support/product/gs305e). VLAN tagging happens at Layer 2 (Ethernet frames), so the same trunk/tagged configuration carries IPv4 and IPv6 traffic together without any switch-side change for dual-stack — the switch has no notion of IPv4 vs IPv6 at all, it only sees VLAN-tagged frames.

### Ethernet Cables

**Ethernet cables** (Cat6 or better for gigabit speeds):
- **Long Ethernet cable for WAN (ISP modem → lab router)** 1 cable (10 m (ensures it can reach the router, such as if it needs to go through the wall or a conduit to a different floor (e.g. your work room), etc.)). I bought the "ISY IPC-6100-1-GB Netwerkkabel 10 m Wit" at MediaMarkt for 18.99 EUR because "ISY" (MediaMarkt's own store brand) is a reputable brand and affordable. Alternatively, you can decide to add all of your infrastructure in the TODO
- **Long Ethernet cable for WAN (ISP modem → lab router)** 1 cable (10 m). A longer cable provides flexibility when the router is not located near the ISP modem, for example when your lab is set up in a dedicated work room, office, or another floor of the house. Keeping the router and other lab equipment in your work room is often preferable because it makes maintenance, troubleshooting, cable management, and physical access significantly easier. It also allows you to keep noise, blinking LEDs, and additional equipment close to where you actually use and manage them. The cable may need to pass through walls, conduits, or between floors, so 10 m is usually a safe choice. I bought the "ISY IPC-6100-1-GB Netwerkkabel 10 m Wit" at MediaMarkt for 18.99 EUR because "ISY" (MediaMarkt's own store brand) is a reputable and affordable brand.
  > **Alternative:** You may choose to install the router, switch, and other networking/homelab equipment in the meter cabinet ("meterkast") alongside the ISP modem. In that case, much shorter Ethernet cables will likely be sufficient. For typical consumer and homelab networking equipment, this is generally safe from a fire-safety perspective, provided the devices are used as intended, have adequate ventilation, and do not obstruct access to electrical installations. Avoid overcrowding the cabinet with heat-generating equipment, ensure proper airflow around all devices, and verify that the installation complies with any local electrical regulations or requirements.
- **Lab router → lab switch:** 1 cable (0.75 m). I bought the "ISY IPC-1012 CAT6A U/UTP Slim Netwerkkabel 0,75 m Wit" at MediaMarkt for 9.99 EUR (same reasoning for this brand as above).
- **Lab switch → lab devices:** 1 cable per device (same model as above).

---

## Network Topology & Design

See [Node Setup](../1_Design/1_Hardware_Prerequisites.md#node-setup) for the physical nodes in the homelab. The network topology diagram below shows how the nodes are connected to the lab router and switch, how the lab network is isolated from the home network, and the dual-stack (IPv4 + IPv6) addressing per VLAN.

**Full high-level network topology and design (in .md diagram format to save space — no image file needed for this setup (KISS: Keep It Simple, Stupid)):**
> **Scope note:** The network design described above focuses on the homelab environment, detailing VLAN segmentation, IP addressing, and the role of the lab router as a jumphost. It assumes a separate home network and does not cover ISP-specific configurations or external network considerations. Furthermore, low-level network configurations on the actual VLAN interfaces (e.g. the kubernetes network setup in the Services VLAN) of the router and switch are considered out of scope for this document and should be explained in the dedicated design document (e.g. [cluster network design]).
```
┌────────────────────────────────────────────────────────────┐
│                          Internet                          │
└────────────────────────────────────────────────────────────┘
                              ⇵
┌────────────────────────────────────────────────────────────┐
│           ISP Home Modem/Router (192.168.2.254)            │
│           Home devices (192.168.2.0/24)                    │
└────────────────────────────────────────────────────────────┘
                              ⇵
┌────────────────────────────────────────────────────────────┐
│   Lab Router (Homelab Network: 10.42.0.0/20 + fd42::/48)   │
│   eth0 (WAN; connected to ISP Modem)                       │
│   eth1.x (LAN (VLAN subinterface); connected to switch)    │
└────────────────────────────────────────────────────────────┘
                              ⇵
┌────────────────────────────────────────────────────────────┐
│            Managed Switch (expands LAN ports)              │
└────────────────────────────────────────────────────────────┘
  ├─ VLAN 1  Native (unused — no production traffic)
  │
  ├─ VLAN 10 Management      (10.42.10.0/24 + fd42:10::/64)
  │    ├─ 10.42.10.1  / fd42:10::1    Router (Raspberry Pi — gateway for all VLANs)
  │    ├─ 10.42.10.2                  Switch (NETGEAR GS305E — management interface)
  │    ├─ 10.42.10.10 / fd42:10::10   PVE1 (physical machine: Proxmox VE host 1 — old laptop)
  │    └─ 10.42.10.11 / fd42:10::11   PVE2 (physical machine: Proxmox VE host 2 — Mini PC (future; not yet deployed))
  │
  ├─ VLAN 20 Services        (10.42.20.0/24 + fd42:20::/64)
  │    ├─ 10.42.20.x / fd42:20::x     Kubernetes nodes, application VMs
  │    └─ ...                         (Grafana, Prometheus, Home Assistant, ArgoCD, etc.)
  │
  └─ VLAN 30 IoT            (10.42.30.0/24 + fd42:30::/64)
        ├─ 10.42.30.x / fd42:30::x     Smart plugs, sensors, Zigbee gateways
        └─ ...                         (all smart/IoT devices)
```

IPv6 addresses shown above are the router's own gateway addresses per VLAN (statically configured) and the ULA addresses lab devices derive for themselves via SLAAC. Individual lab devices do not need a static IPv6 address reserved — see [IPv6 Addressing](#ipv6-addressing-ula--nat66) for why static leases are IPv4-only by design in this lab.

**The sections below explain some of the design choices made for the lab network in more detail.**

### IPv6 Addressing (ULA + NAT66) on the Lab Network

**The lab is deliberately dual-stack rather than IPv4-only. This is a design choice, not an accident:**
- **Practice:** SLAAC, Router Advertisements, Neighbour Discovery, ULA vs GUA addressing, and IPv6 firewalling can only really be learned by running them — not by reading about them.
- **More possibilities:** dual-stack unlocks testing real dual-stack services, AAAA records, IPv6-only clients, and (later) dual-stack Kubernetes, instead of a permanently IPv4-only lab.
- **Better firewalling discipline:** IPv6 has no NAT to hide behind, so every inbound flow must be explicitly allowed on the router. This forces a proper default-deny firewall instead of relying on NAT as an accidental security boundary (see [IoT Isolation](#iot-isolation) and [Jumphost](#jumphost-secure-access-to-lab-network) below for where this matters concretely).

Addressing uses **ULA (fd42::/48)**, one `/64` per VLAN, instead of a prefix delegated by the ISP modem — see [Why fd42::/48](#option-3-dedicated-router-behind-the-isp-modem) above for the reasoning. Because ULA addresses are not globally routable, outbound IPv6 traffic is masqueraded to the router's WAN IPv6 address (**NAT66**), the same way IPv4 traffic is masqueraded to the WAN IPv4 address. NAT66 is not something to be proud of — in a "real" dual-stack network with a properly delegated prefix there would be no NAT for IPv6 at all — but it is the pragmatic choice for a homelab sitting behind a consumer ISP modem that does not delegate a usable prefix downstream. The moment prefix delegation becomes available, NAT66 can simply be switched off and the lab becomes properly routed dual-stack with no translation at all.

### Jumphost: Secure Access to Lab Network

A jumphost is a single, controlled entry point into a protected network, used to securely access management interfaces and internal systems.

The lab router (Raspberry Pi) is used as the jumphost for accessing all management interfaces inside the homelab. This is both intentional and beneficial for stability, security, and operational simplicity:
- **Central position in the network:** The lab router sits at the heart of VLAN 10 (Management) and has routed visibility into all VLANs (see [Network Topology](#network-topology)). This makes it the most reliable and consistent entry point into the homelab network.
- **Always reachable:** As the gateway (10.42.10.1 / fd42:10::1), the lab router remains accessible even if Proxmox, Kubernetes, or VLAN tagging break. It provides a stable fallback path during outages or misconfigurations.
- **Strong isolation guarantees:** Firewall rules already isolate management traffic. IoT devices cannot reach VLAN 10, and inter-VLAN traffic is denied by default — for both IPv4 and IPv6. This matters more for IPv6 specifically, since there is no NAT to accidentally provide that isolation as a side effect; the router's firewall rules are the *only* thing enforcing it.
- **Safe entry from the home network:** SSH access enters through the router's WAN interface, keeping the home network (e.g. 192.168.2.0/24) fully separated from the lab network (e.g. 10.42.0.0/20 + fd42::/48). No lab device is directly exposed to the home LAN or, once IPv6 routes to the internet, to the internet itself.
- **Centralized authentication & logging:** The router is the only device exposed to the home network, making it the ideal place to centralize SSH keys, access control, and audit logs — similar to enterprise bastion host patterns.
- **Minimal overhead:** The router is lightweight and hardened. Running a jumphost on it adds negligible load while significantly improving operational safety.
- **No extra hardware or services needed:** The homelab has limited physical machines and capacity; using the router as the jumphost avoids the need for a dedicated bastion VM or additional hardware, keeping the design simple and resource-efficient.
- **Enterprise-aligned design:** Using the router as the bastion mirrors how real networks operate: a single controlled gateway that provides secure access to management infrastructure.

### Subnet & VLAN Design

| Subnet (IPv4) | Subnet (IPv6, ULA) | VLAN | Purpose |
| --- | --- | --- | --- |
| — | — | 1 (native) | Unused — no production traffic, fallback recovery only |
| 10.42.10.0/24 | fd42:10::/64 | 10 | Management — router, switch, Proxmox host management IPs |
| 10.42.20.0/24 | fd42:20::/64 | 20 | Services — Kubernetes, application VMs, monitoring, databases |
| 10.42.30.0/24 | fd42:30::/64 | 30 | IoT — smart plugs, sensors, Zigbee gateways, energy meters |

#### Why VLAN 1 (native) is not used — all traffic is explicitly VLAN-tagged

The native VLAN (VLAN 1) carries no production traffic in this design. Every device — router, switch, Proxmox hosts, services, IoT — communicates exclusively on tagged VLANs (10, 20, 30). The Pi router's physical eth1 interface has no IP address in either address family; all traffic flows through VLAN sub-interfaces (eth1.10, eth1.20, eth1.30). VLAN 1 exists on the switch only because 802.1Q requires a native VLAN — it cannot be deleted, but it carries nothing.

Why this is the right approach:
- **Everything is explicit:** When all traffic is tagged, every frame on the wire declares which VLAN it belongs to. There is no ambiguity about where untagged traffic ends up. Debugging is simpler — a packet capture shows the VLAN tag immediately, and you never have to wonder "is this untagged frame on VLAN 1 or did something strip the tag?"
- **Closer to enterprise practice:** In production environments, the native VLAN is left unused or disabled entirely. All real traffic — including management — is explicitly tagged. Learning this pattern now means fewer surprises when working with enterprise infrastructure.
- **Security — prevents VLAN hopping:** Native VLAN hopping attacks (802.1Q double-tagging) exploit the fact that the native VLAN is untagged. An attacker on the native VLAN can craft a double-tagged frame: the switch strips the outer (native) tag and forwards the inner tag to a different VLAN. By not carrying any production traffic on the native VLAN, this attack vector is eliminated — there is nothing to hop from.
- **Easier to expand later:** Adding new VLANs is uniform — every VLAN is tagged, every subnet has a matching VLAN ID (VLAN 10 → 10.42.10.0/24 + fd42:10::/64, VLAN 20 → 10.42.20.0/24 + fd42:20::/64, VLAN 30 → 10.42.30.0/24 + fd42:30::/64). No special case for "the one VLAN that happens to be untagged."
- **Cleaner trunk configuration:** All production VLANs are tagged on trunk ports. No confusion about which VLAN carries untagged traffic on which port.
- **Fallback recovery still works:** Even though VLAN 1 is unused, it remains configured as untagged on all ports. If VLAN tagging breaks entirely (firmware bug, misconfiguration), untagged frames still flow on VLAN 1 — you can connect a laptop directly to the switch, assign a static IP, and access the switch web UI to fix the configuration.

#### Why a dedicated Management VLAN (VLAN 10)

Management traffic (SSH to hosts, Proxmox web UI, switch admin, router access) is on its own VLAN rather than being mixed in with services or IoT. This provides:
- **Isolation from workloads:** If a service on VLAN 20 misbehaves (broadcast storm, saturated bandwidth, compromised container), management access to the infrastructure remains unaffected — you can still SSH into hosts and access the Proxmox UI to diagnose and fix the problem.
- **Access control:** Firewall rules on the router restrict which VLANs can reach management interfaces, for both IPv4 and IPv6. IoT devices (VLAN 30) are blocked from reaching VLAN 10 entirely — a compromised smart bulb cannot probe Proxmox or SSH into the router, whether it tries over its DHCP-assigned IPv4 address or its SLAAC-derived IPv6 address. Only traffic that explicitly needs management access (e.g. your laptop via SSH tunnel) reaches VLAN 10.
- **Audit clarity:** All management traffic lives on a single, known subnet pair (10.42.10.0/24 + fd42:10::/64). Log analysis, packet captures, and firewall auditing are simpler when management is cleanly separated from application and IoT traffic.

#### IoT Isolation

IoT devices are often the least secure devices in a home. By isolating them on VLAN 30:

IoT (VLAN 30) → Services (VLAN 20) = Allowed (sensors push data to Home Assistant)
IoT (VLAN 30) → Management (VLAN 10) = Blocked (a compromised smart bulb cannot probe Proxmox)

Firewall rules on the router enforce this — inter-VLAN traffic is denied by default, then specific flows are allowed explicitly, for both IPv4 and IPv6. This matters more for IPv6 than it might first appear: IPv4 gets some accidental isolation "for free" from NAT (a device on VLAN 30 doesn't even have a routable address to reach VLAN 10 with), but IPv6 has no such safety net — every lab device gets a real, routable ULA address, so the IoT → Management block has to be an explicit firewall rule rather than an emergent property of address translation. See the [router Ansible role](../../ansible/roles/router/README.md) for exactly how these rules are generated per VLAN.

#### Switch Port Assignments

| Port | Connected Device | VLAN Membership |
| --- | --- | --- |
| 1 | Pi Router (eth1) | Untagged: 1 (native, unused) + Tagged: 10, 20, 30 (trunk port) |
| 2 | PVE1 (Proxmox host 1) | Untagged: 1 (native, unused) + Tagged: 10, 20, 30 |
| 3 | PVE2 (Proxmox host 2) | Untagged: 1 (native, unused) + Tagged: 10, 20, 30 |
| 4 | (spare) | Untagged: 1 (native) |
| 5 | (spare) | Untagged: 1 (native) |

**How to read this table:** See [Network Devices — Tagged vs Untagged](../../../reference/network/Network_Devices.md#tagged-vs-untagged-8021q-vlan-tagging) for a full explanation of what tagged and untagged mean, how frames flow through the switch, and when to use each mode. Each port can be a member of multiple VLANs simultaneously. The "VLAN Membership" column lists **all** VLANs that a port participates in, separated by +. The keyword before each VLAN entry tells the switch how to handle frames for that VLAN on that port:
- **Untagged: 1** — Frames for VLAN 1 are sent/received **without** a VLAN tag in the [Ethernet frame header](../../../reference/network/Network_Models_and_Packets.md#anatomy-of-a-frame-layer-2). In this design, the native VLAN carries no production traffic — it exists only as a fallback recovery path. If all VLAN tagging breaks, untagged frames still flow, allowing you to reach the switch management interface.
- **Tagged: 10, 20, 30** — Frames for VLANs 10, 20, and 30 are sent/received **with** an 802.1Q VLAN tag in the [Ethernet frame header](../../../reference/network/Network_Models_and_Packets.md#anatomy-of-a-frame-layer-2) (a 4-byte field that says "this frame belongs to VLAN X"). The device on the other end must understand VLAN tags and process them — the Pi router uses sub-interfaces (eth1.10, eth1.20, eth1.30) and Proxmox uses VLAN-aware bridges to separate tagged traffic into the correct virtual networks. Each tagged VLAN carries both IPv4 and IPv6 traffic together — VLAN tagging is a Layer 2 mechanism and has no notion of which Layer 3 protocol rides inside the frame.

**The + does NOT mean "10, 20, and 30 are untagged from VLAN 1"** — it means the port carries four independent traffic streams: one untagged (VLAN 1, unused) and three tagged (VLAN 10, VLAN 20, VLAN 30). They coexist on the same physical cable but are completely separate at the logical level.

**Per-port explanation**
- **Port 1 — Pi Router (eth1):** The router is the gateway for all VLANs. Its physical eth1 interface is on the native VLAN (unused — no IP assigned, in either address family). Tagged traffic arrives on sub-interfaces eth1.10 (VLAN 10, IP 10.42.10.1 + fd42:10::1), eth1.20 (VLAN 20, IP 10.42.20.1 + fd42:20::1), and eth1.30 (VLAN 30, IP 10.42.30.1 + fd42:30::1). The router forwards traffic between VLANs (inter-VLAN routing) and applies firewall rules. This is a "trunk port" — it carries all VLANs.
- **Ports 2–3 — Proxmox hosts (PVE1, PVE2):** Each Proxmox host has one physical NIC connected to the switch. Management traffic (SSH to the host, Proxmox web UI) flows tagged on VLAN 10 — the host's management IP (10.42.10.10 or .11, plus its SLAAC-derived fd42:10::/64 address) is on a VLAN-aware bridge tagged to VLAN 10. VMs running on the host are placed into VLANs via Proxmox's VLAN-aware bridge (vmbr0): a service VM gets tagged into VLAN 20, an IoT gateway VM into VLAN 30. The switch delivers tagged frames for those VLANs to the port, and Proxmox's bridge routes them to the correct VM. PVE1 is the Acer laptop being set up now; PVE2 is a planned future addition and not yet physically connected.
- **Ports 4–5 — Spare:** Simple access ports — only untagged VLAN 1. Any device plugged in lands on the native VLAN (no production access by default). To give a device access to a specific VLAN, reconfigure the port.

**Why tagged for service VLANs instead of untagged (access ports)?** An alternative design would be to assign each port to a single VLAN as untagged (e.g. port 2 = untagged VLAN 10, port 3 = untagged VLAN 20). This is simpler per-port but has a critical limitation: **you only get 5 ports total**, and each device would be locked to a single VLAN. Since Proxmox hosts run VMs in multiple VLANs simultaneously (management + services + IoT on the same physical machine), the host's port MUST carry multiple VLANs — which requires tagging. **Summary of the tagging logic:**
- **VLAN 1 (native): untagged** — carries no production traffic; exists as a fallback recovery path if VLAN tagging breaks.
- **VLAN 10 (management): tagged** — router, switch, Proxmox hosts; requires VLAN-aware sub-interface/bridge.
- **VLAN 20 (services): tagged** — Kubernetes, all hosted applications; requires VLAN-aware bridge/sub-interface.
- **VLAN 30 (IoT): tagged** — smart devices, sensors; isolated from management for security.
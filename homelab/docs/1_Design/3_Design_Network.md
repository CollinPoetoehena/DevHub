# Design: Network

> **Scope of this document: see [README.md/Documents Setup & Scope](README.md#documents-setup--scope); in short: design only — no specific hardware or software.**

A stable network is the foundation of a reliable homelab. This document covers the network **design decisions**: the setup options available, why a dedicated lab router behind the ISP modem is the right choice, the subnet and VLAN design, and the target network topology. The lab network is **dual-stack (IPv4 + IPv6)**.

See the [Network Reference](../../../reference/network/README.md) for background knowledge on networking concepts, commands, and troubleshooting tips.

> **Future option, not the current design:** see [TODO FUTURE: Shared Home and Lab Gateway](#todo-future-shared-home-and-lab-gateway) for the proposed integration, platform preference, and documents to revisit when I manage my own home network.

## Table of Contents
- [Network Setup Options](#network-setup-options)
  - [Option 1: Lab devices directly on the home network](#option-1-lab-devices-directly-on-the-home-network)
  - [Option 2: VLANs on the ISP modem](#option-2-vlans-on-the-isp-modem)
  - [Option 3: Dedicated router behind the ISP modem](#option-3-dedicated-router-behind-the-isp-modem)
  - [Chosen Option: Dedicated Router Behind the ISP Modem](#chosen-option-dedicated-router-behind-the-isp-modem)
- [Required Building Blocks (Design Level)](#required-building-blocks-design-level)
- [Network Topology & Design](#network-topology--design)
  - [IPv6 Addressing (ULA + NAT66) on the Lab Network](#ipv6-addressing-ula--nat66-on-the-lab-network)
  - [Jumphost: Secure Access to Lab Network](#jumphost-secure-access-to-lab-network)
- [Subnet & VLAN Design](#subnet--vlan-design)
  - [Switch Port Assignments](#switch-port-assignments)
- [TODO FUTURE: Shared Home and Lab Gateway](#todo-future-shared-home-and-lab-gateway)
  - [Why One Gateway Is Still Enough](#why-one-gateway-is-still-enough)
  - [Future Platform Preference and Comparison](#future-platform-preference-and-comparison)
  - [Configuration, Backups, and Public Documentation](#configuration-backups-and-public-documentation)
  - [TODO: Documents and Setup to Update Later](#todo-documents-and-setup-to-update-later)

---

## Network Setup Options

### Option 1: Lab devices directly on the home network

Connect lab devices (hypervisor hosts, worker nodes) directly to the ISP modem or home switch.

```
ISP Modem → Home Switch → Lab Devices + Home Devices (same network)
```

**Why not:** Lab mistakes — DHCP conflicts, virtual bridge misconfiguration, routing loops — directly affect the home network. This is what caused home devices (phone, TV, printer) to lose internet access when the first hypervisor host was connected: its virtual bridge interfered with the home LAN's DHCP, creating IP conflicts that were visible in the ISP modem's admin page.

### Option 2: VLANs on the ISP modem

Segment the network using VLANs configured on the ISP modem itself.

**Why not:** Most ISP modems have very limited or no VLAN support. A misconfiguration can break the entire home network. Not practical.

### Option 3: Dedicated router behind the ISP modem

Place a dedicated lab router between the ISP modem and all lab devices. The lab runs on its own subnet, fully isolated from the home network, and is dual-stack (IPv4 + IPv6).

```
ISP Modem (192.168.2.0/24) → Lab Router → Lab Devices (10.42.0.0/20 + fd42::/48)
```

**Why `10.42.0.0/20` and not `10.0.0.0/20`?** The `10.0.0.0/x` range is extremely common — corporate VPNs, container defaults, cluster pod CIDRs, and cloud VPCs all frequently use `10.0.x.x`. If any of these overlap with the lab subnet, routes conflict and traffic breaks. `10.42.0.0/20` is an uncommon slice of the `10.0.0.0/8` private range, so it is unlikely to collide with anything. The `42` is arbitrary — just picked to stay out of the way.

**Why `/20` and not `/24` or `/16`?** A `/24` gives only 254 usable addresses — that is enough for a flat network, but too small once you start carving out VLANs (each VLAN gets its own `/24` subnet within the parent range). A `/20` gives 4094 addresses and fits 16 × `/24` subnets comfortably — plenty of room for management, monitoring, cluster workloads, and future VLANs without ever running out. A `/16` (65k addresses) would also work but is far more than needed for a home lab.

**Why `fd42::/48` for IPv6 (ULA) and not a delegated prefix?** IPv6 normally needs no NAT at all — every device gets a globally routable address, but only if the upstream router (the ISP modem) delegates a usable prefix downstream (DHCPv6-PD). Consumer ISP modems usually either don't support this at all or only delegate a single `/64` — not enough for three VLANs, and it can change on every modem reboot, which would renumber the entire lab. Instead, the lab uses a Unique Local Address (ULA, `fd00::/8`) range: **`fd42::/48`**, split into one `/64` per VLAN (`fd42:10::/64`, `fd42:20::/64`, `fd42:30::/64`). This mirrors the IPv4 supernet in spirit (the "42" is the same arbitrary, memorable choice) — stable, private, and immune to ISP renumbering. Outbound IPv6 traffic is masqueraded (NAT66) to the router's WAN address until real prefix delegation is available; see [IPv6 Addressing (ULA + NAT66) on the Lab Network](#ipv6-addressing-ula--nat66-on-the-lab-network) below.

### Chosen Option: Dedicated Router Behind the ISP Modem

**Full isolation (maintaining the home network is not in my homelab's scope):** The lab runs on its own subnet with its own DHCP and firewall. Lab mistakes — DHCP conflicts, virtual bridge issues, cluster networking — are contained within the lab network and never reach home devices. Avoid changing the ISP Modem's core configuration when others in the house depend on it for internet access. Changing the home network configuration can break connectivity for everyone, so it's best to leave it as-is and put your own router behind it for the lab. Furthermore, the ISP modem may have limited or no VLAN support, making it unsuitable for isolating your lab network. Finally, it is not in my homelab's scope to maintain the home network, so I want to keep it untouched and let the ISP modem handle the home network while I experiment freely in my lab network.
- **Keeps the ISP modem intact:** Other people in the house depend on the ISP modem for WiFi and internet. Replacing it or changing its configuration would mean taking ownership of the entire home network. Keeping it untouched means home connectivity stays stable regardless of what happens in the lab. See [Goals](0_Goals.md), in short: I am NOT planning to self-host everything and make the home network dependent on my lab!
- **Learn networking:** Running your own dedicated router is a hands-on way to learn subnetting, routing, DHCP, firewall rules, VLANs, and dual-stack IPv6 (SLAAC, Router Advertisements, Neighbour Discovery) in a real environment — knowledge that only comes from actually running it, not from reading about it. This remains true on a purpose-built router platform: the concepts and the topology are identical, only the implementation details are handled by the platform instead of by hand.
- **It is stable and low-maintenance:** The lab router is infrastructure that everything else depends on. Keeping it boring, predictable, and quick to recover is worth more than squeezing the last bit of learning out of it.
- **The router must be physically separate from the hypervisor:** Running the router as a VM would put the router and the path used to fix the router in the same failure domain — if the virtualization host is down or being rebuilt, the entire lab *and* the way in are gone at the same time. A separate physical router keeps the network up independently of the compute platform.
- **It is fun:** Designing your own network infrastructure and segmentation is genuinely enjoyable.

**Classic mistakes that break home networks (avoid these):**
- Running a DHCP server (or IPv6 Router Advertisements) on the same subnet as home devices
- Changing DNS settings on the ISP modem
- Connecting hypervisor or cluster nodes directly to the home network
- Misconfiguring virtual bridges (can cause broadcast loops)
- Running firewall experiments on the home LAN

---

## Required Building Blocks (Design Level)

The design above implies three physical building blocks. **What they are is a design requirement; which products they are is not part of this document** — see [Design: Hardware & Prerequisites](1_Design_Hardware_Prerequisites.md) for the actual devices and prices, and [Design: Software & Prerequisites](3_Design_Software_Prerequisites.md) for the router/firewall platform that runs on them.

| Building block | What the design requires of it | Why |
|---|---|---|
| **Lab router / firewall** | A dedicated physical device with **at least two network interfaces** (WAN + LAN trunk), able to terminate tagged VLAN sub-interfaces, route between them, serve DHCP/DNS and IPv6 Router Advertisements, and enforce a dual-stack default-deny firewall. Must be separate from the virtualization platform. | It is the gateway for every VLAN, the enforcement point for all inter-VLAN policy, and the [jumphost](#jumphost-secure-access-to-lab-network). Two interfaces is the hard minimum for any router; more allow future segmentation. |
| **Managed switch** | 802.1Q VLAN tagging, enough ports for the router plus every host plus spares. | Without VLAN tagging there is no segmentation and the entire design collapses to a flat network. VLAN tagging is a Layer 2 mechanism, so the switch carries IPv4 and IPv6 together with no dual-stack-specific configuration. |
| **Ethernet cabling** | One long run for WAN (ISP modem → lab router), short patch cables for router → switch → hosts. Cat6 or better. | Lets the lab live where it is actually maintained (a work room) rather than next to the ISP modem, while keeping the local wiring tidy. |

**Configuration as code:** all router and switch configuration is defined in version-controlled files and applied through automation, never clicked into a web UI and forgotten. The repository is the source of truth; the device is the result. Which automation tooling is used is, again, in the [software document](3_Design_Software_Prerequisites.md).

---

## Network Topology & Design

See [Node Setup](1_Design_Hardware_Prerequisites.md#node-setup) for the physical nodes in the homelab. The topology below shows how the nodes connect to the lab router and switch, how the lab network is isolated from the home network, and the dual-stack (IPv4 + IPv6) addressing per VLAN.

**Full high-level network topology and design (in .md diagram format to save space — no image file needed for this setup (KISS: Keep It Simple, Stupid)):**
> **Scope note:** This topology covers the homelab environment only — VLAN segmentation, IP addressing, and the role of the lab router as a jumphost. It assumes a separate home network and does not cover ISP-specific configuration or external network considerations. Low-level network configuration *inside* a VLAN (e.g. the cluster's internal networking in the Services VLAN) is out of scope here and belongs in the dedicated design document for that component (e.g. \[cluster network design\]).
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
│   WAN interface (connected to ISP Modem)                   │
│   LAN interface (VLAN trunk; connected to switch)          │
└────────────────────────────────────────────────────────────┘
                              ⇵
┌────────────────────────────────────────────────────────────┐
│            Managed Switch (expands LAN ports)              │
└────────────────────────────────────────────────────────────┘
  ├─ VLAN 1  Native (unused — no production traffic)
  │
  ├─ VLAN 10 Management      (10.42.10.0/24 + fd42:10::/64)
  │    ├─ 10.42.10.1  / fd42:10::1    Lab router (gateway for all VLANs)
  │    ├─ 10.42.10.2                  Managed switch (management interface)
  │    ├─ 10.42.10.10 / fd42:10::10   Host 1 (physical machine: hypervisor host 1)
  │    └─ 10.42.10.11 / fd42:10::11   Host 2 (physical machine: hypervisor host 2)
  │
  ├─ VLAN 20 Services        (10.42.20.0/24 + fd42:20::/64)
  │    ├─ 10.42.20.x / fd42:20::x     Cluster nodes, application VMs
  │    └─ ...                         (monitoring, home automation, delivery tooling, etc.)
  │
  └─ VLAN 30 IoT            (10.42.30.0/24 + fd42:30::/64)
        ├─ 10.42.30.x / fd42:30::x     Smart plugs, sensors, Zigbee gateways
        └─ ...                         (all smart/IoT devices)
```

IPv6 addresses shown above are the router's own gateway addresses per VLAN (statically configured) and the ULA addresses lab devices derive for themselves via SLAAC. Individual lab devices do not need a static IPv6 address reserved — static leases are IPv4-only by design in this lab.

### IPv6 Addressing (ULA + NAT66) on the Lab Network

**The lab is deliberately dual-stack rather than IPv4-only. This is a design choice, not an accident:**
- **Practice:** SLAAC, Router Advertisements, Neighbour Discovery, ULA vs GUA addressing, and IPv6 firewalling can only really be learned by running them — not by reading about them.
- **More possibilities:** dual-stack unlocks testing real dual-stack services, AAAA records, IPv6-only clients, and (later) a dual-stack cluster, instead of a permanently IPv4-only lab.
- **Better firewalling discipline:** IPv6 has no NAT to hide behind, so every inbound flow must be explicitly allowed on the router. This forces a proper default-deny firewall instead of relying on NAT as an accidental security boundary.

Addressing uses **ULA (`fd42::/48`)**, one `/64` per VLAN, instead of a prefix delegated by the ISP modem — see [Option 3](#option-3-dedicated-router-behind-the-isp-modem) above for the reasoning. Because ULA addresses are not globally routable, outbound IPv6 traffic is masqueraded to the router's WAN IPv6 address (**NAT66**), the same way IPv4 traffic is masqueraded to the WAN IPv4 address. NAT66 is not something to be proud of — in a "real" dual-stack network with a properly delegated prefix there would be no NAT for IPv6 at all — but it is the pragmatic choice for a homelab sitting behind a consumer ISP modem that does not delegate a usable prefix downstream. The moment prefix delegation becomes available, NAT66 can simply be switched off and the lab becomes properly routed dual-stack with no translation at all.

### Jumphost: Secure Access to Lab Network

A jumphost is a single, controlled entry point into a protected network, used to securely access management interfaces and internal systems.

The lab router is used as the jumphost for accessing all management interfaces inside the homelab. This is both intentional and beneficial for stability, security, and operational simplicity:
- **Central position in the network:** The router sits at the heart of VLAN 10 (Management) and has routed visibility into all VLANs. This makes it the most reliable and consistent entry point into the homelab network.
- **Always reachable:** As the gateway (10.42.10.1 / fd42:10::1), the router remains accessible even if the hypervisor, the cluster, or VLAN tagging break. It provides a stable fallback path during outages or misconfigurations.
- **Strong isolation guarantees:** Firewall rules already isolate management traffic. IoT devices cannot reach VLAN 10, and inter-VLAN traffic is denied by default — for both IPv4 and IPv6. This matters more for IPv6 specifically, since there is no NAT to accidentally provide that isolation as a side effect; the router's firewall rules are the *only* thing enforcing it.
- **Safe entry from the home network:** SSH access enters through the router's WAN interface, keeping the home network (e.g. 192.168.2.0/24) fully separated from the lab network (e.g. 10.42.0.0/20 + fd42::/48). No lab device is directly exposed to the home LAN or, once IPv6 routes to the internet, to the internet itself.
- **Centralized authentication & logging:** The router is the only device exposed to the home network, making it the ideal place to centralize SSH keys, access control, and audit logs — similar to enterprise bastion host patterns.
- **Minimal overhead and no extra hardware:** The router is lightweight and hardened, and the lab has limited physical machines. Running the jumphost on it adds negligible load and avoids a dedicated bastion VM.
- **Enterprise-aligned design:** Using the router as the bastion mirrors how real networks operate: a single controlled gateway that provides secure access to management infrastructure.

---

## Subnet & VLAN Design

The lab is split into three tagged VLANs, each with a matching IPv4 `/24` and IPv6 `/64`, plus the unused native VLAN. **Inter-VLAN traffic is denied by default in both address families**, and only explicitly allowed flows are forwarded.

| Subnet (IPv4) | Subnet (IPv6, ULA) | VLAN | Purpose |
| --- | --- | --- | --- |
| — | — | 1 (native) | Unused — no production traffic, fallback recovery only |
| 10.42.10.0/24 | fd42:10::/64 | 10 | Management — router, switch, hypervisor host management IPs |
| 10.42.20.0/24 | fd42:20::/64 | 20 | Services — cluster nodes, application VMs, monitoring, databases |
| 10.42.30.0/24 | fd42:30::/64 | 30 | IoT — smart plugs, sensors, Zigbee gateways, energy meters |

**Why VLAN 1 (native) is not used — all traffic is explicitly tagged.** Every device communicates exclusively on tagged VLANs (10, 20, 30); the router's physical LAN interface has no IP address in either address family and only carries VLAN sub-interfaces. VLAN 1 exists only because 802.1Q requires a native VLAN — it cannot be deleted, but it carries nothing. This is the right approach because:
- **Everything is explicit:** every frame on the wire declares its VLAN, so a packet capture is unambiguous and there is never a question of where untagged traffic ended up.
- **Closer to enterprise practice:** production networks leave the native VLAN unused and tag all real traffic, including management.
- **Security — prevents VLAN hopping:** 802.1Q double-tagging attacks exploit the untagged native VLAN (the switch strips the outer tag and forwards the inner one to another VLAN). With no production traffic on the native VLAN, there is nothing to hop from.
- **Uniform and easy to expand:** every VLAN is tagged and every subnet matches its VLAN ID (VLAN 10 → 10.42.10.0/24 + fd42:10::/64, and so on) — no special case for "the one untagged VLAN", and no confusion on trunk ports.
- **Fallback recovery still works:** VLAN 1 remains untagged on all ports, so if VLAN tagging breaks entirely you can still plug a laptop into the switch, assign a static IP, and reach the switch UI to fix it.

**Why a dedicated Management VLAN (VLAN 10).** Management traffic (SSH to hosts, hypervisor web UI, switch admin, router access) is separated from services and IoT because:
- **Isolation from workloads:** if a service on VLAN 20 misbehaves (broadcast storm, saturated bandwidth, compromised container), management access is unaffected — you can still reach the hosts to diagnose and fix it.
- **Access control:** firewall policy restricts which VLANs may reach management interfaces, in both address families. IoT (VLAN 30) is blocked from VLAN 10 entirely, so a compromised smart bulb cannot probe the hypervisor or SSH into the router over either its IPv4 or its SLAAC-derived IPv6 address.
- **Audit clarity:** all management traffic lives on one known subnet pair, which makes log analysis, packet captures, and firewall auditing far simpler.

**IoT isolation.** IoT devices are often the least secure devices in a home, so VLAN 30 is constrained explicitly:

```
IoT (VLAN 30) → Services (VLAN 20)   = Allowed  (sensors push data to the home-automation service)
IoT (VLAN 30) → Management (VLAN 10) = Blocked  (a compromised smart bulb cannot probe the hypervisor)
```

Inter-VLAN traffic is denied by default and specific forwardings are allowed explicitly, for both IPv4 and IPv6. This matters more for IPv6 than it first appears: IPv4 gets some accidental isolation "for free" from NAT (a VLAN 30 device has no routable address to reach VLAN 10 with), but every lab device has a real, routable ULA address — so the IoT → Management block must be an explicit policy rather than an emergent property of address translation. Expressing this as per-VLAN zones and explicit inter-zone forwardings is both easier to review and harder to get subtly wrong than hand-maintained rule chains.

### Switch Port Assignments

| Port | Connected Device | VLAN Membership |
| --- | --- | --- |
| 1 | Lab router (LAN interface) | Untagged: 1 (native, unused) + Tagged: 10, 20, 30 (trunk port) |
| 2 | Host 1 (hypervisor host 1) | Untagged: 1 (native, unused) + Tagged: 10, 20, 30 |
| 3 | Host 2 (hypervisor host 2) | Untagged: 1 (native, unused) + Tagged: 10, 20, 30 |
| 4 | (spare) | Untagged: 1 (native) |
| 5 | (spare) | Untagged: 1 (native) |

**How to read this table:** See [Network Devices — Tagged vs Untagged](../../../reference/network/Network_Devices.md#tagged-vs-untagged-8021q-vlan-tagging) for a full explanation of what tagged and untagged mean and how frames flow through the switch. Each port can be a member of multiple VLANs simultaneously; the "VLAN Membership" column lists **all** VLANs a port participates in, separated by `+`, and the keyword before each entry tells the switch how to handle those frames:
- **Untagged: 1** — frames for VLAN 1 are sent/received **without** a VLAN tag in the [Ethernet frame header](../../../reference/network/Network_Models_and_Packets.md#anatomy-of-a-frame-layer-2). Carries no production traffic; exists only as a fallback recovery path.
- **Tagged: 10, 20, 30** — frames are sent/received **with** an 802.1Q VLAN tag (a 4-byte field saying "this frame belongs to VLAN X"). The device on the other end must understand tags: the router uses VLAN sub-interfaces, the hypervisor hosts use VLAN-aware bridges. Each tagged VLAN carries IPv4 and IPv6 together — tagging is Layer 2 and has no notion of which Layer 3 protocol rides inside.

**The `+` does NOT mean "10, 20, and 30 are untagged from VLAN 1"** — it means the port carries four independent traffic streams: one untagged (VLAN 1, unused) and three tagged. They coexist on one physical cable but are completely separate logically.

**Per-port explanation**
- **Port 1 — Lab router (LAN interface):** the router is the gateway for all VLANs. Its physical LAN interface sits on the native VLAN with no IP in either address family; tagged traffic arrives on VLAN sub-interfaces carrying 10.42.10.1 + fd42:10::1, 10.42.20.1 + fd42:20::1, and 10.42.30.1 + fd42:30::1. The router performs inter-VLAN routing and applies firewall policy. This is a trunk port — it carries all VLANs.
- **Ports 2–3 — Hypervisor hosts:** each host has one physical NIC to the switch. Host management traffic flows tagged on VLAN 10 (management IP 10.42.10.10 or .11, plus its SLAAC-derived fd42:10::/64 address) on a VLAN-aware bridge. VMs are placed into VLANs by the same bridge: a service VM tagged into VLAN 20, an IoT gateway VM into VLAN 30. Host 1 is the machine being set up now; Host 2 is a planned addition and not yet physically connected.
- **Ports 4–5 — Spare:** simple access ports, untagged VLAN 1 only. Anything plugged in lands on the native VLAN with no production access by default; reconfigure the port to grant VLAN access.

**Why tagged instead of untagged access ports?** An alternative would be one VLAN per port as untagged (port 2 = VLAN 10, port 3 = VLAN 20, etc.). That is simpler per port but has a fatal limitation here: **there are only 5 ports**, and each device would be locked to a single VLAN. The hypervisor hosts run VMs in multiple VLANs at once on the same physical machine, so their ports *must* carry multiple VLANs — which requires tagging.

**Summary of the tagging logic:**
- **VLAN 1 (native): untagged** — carries no production traffic; exists as a fallback recovery path if VLAN tagging breaks.
- **VLAN 10 (management): tagged** — router, switch, hypervisor hosts; requires a VLAN-aware sub-interface/bridge.
- **VLAN 20 (services): tagged** — cluster nodes and all hosted applications; requires a VLAN-aware bridge/sub-interface.
- **VLAN 30 (IoT): tagged** — smart devices and sensors; isolated from management for security.

---

## TODO FUTURE: Shared Home and Lab Gateway

**Future proposal only.** When I have my own home and control its network, consider one physical gateway behind the ISP modem for home and lab, with a suitably sized managed switch and VLAN-aware Wi-Fi. My preference for that future setup is a simple prebuilt platform rather than a separately maintained firewall PC. **The current dedicated lab router and OPNsense hardware/software choices remain unchanged until this proposal is deliberately revisited and validated.** Product names below are comparison examples, not new selections; final choices belong in the hardware/software prerequisites.

### Why One Gateway Is Still Enough

Sharing a router does not require sharing a flat network. Separate home, lab services, management, and IoT VLANs keep their Layer 2 broadcast domains and DHCP traffic apart. Default-deny inter-VLAN firewall rules in **both IPv4 and IPv6** allow only necessary flows: home clients can reach selected lab applications without reaching hypervisor management, and IoT can reach the home-automation endpoint without reaching other networks. VLAN tags alone and WAN NAT do not provide this isolation; switch configuration and firewall policy must be tested.

One gateway removes a device, a firmware lifecycle, duplicated DHCP/routing settings, and an extra downstream NAT boundary. It also makes controlled home/IoT integration easier. A second router is not needed solely for those logical boundaries, although it may still be useful for independent routing experiments or a stronger physical separation requirement.

**Accepted limits:** a router outage, bad update, compromise, or policy mistake can affect both household and lab. VLANs do not eliminate this shared failure/security boundary or prevent shared-link saturation. Keep the gateway physical and independent of lab VMs; household DHCP, DNS, and essential Wi-Fi functions must work when the lab is off. Preserve direct local recovery access, schedule maintenance, and keep disruptive experiments off the household gateway.

### Future Platform Preference and Comparison

| Approach | Benefits | Responsibilities and trade-offs |
|---|---|---|
| **Prebuilt platform, for example UniFi or TP-Link Omada** | Coherent device management, supported firmware, and potentially integrated gateway/switch/Wi-Fi administration. Best fits my future priority: straightforward operation of a network the household depends on. | Verify the exact model's routed VLANs, wired trunks, SSID mapping, firewall/IPv6 controls, throughput, local recovery, and account/controller dependencies. Some gateways need separate APs. Less open and portable; firmware updates and configuration still need care. |
| **Physical firewall appliance running OPNsense** | An open-source, purpose-built routing/firewall platform with more configuration, VPN, and plugin flexibility. Can serve home and lab through the same VLAN design. | I own hardware compatibility, installation/recovery, OS/plugin lifecycle, and coordination with separate Wi-Fi equipment. It is much simpler than building a router from plain Linux, but offers more control than I need for the proposed household role. Reusing an existing appliance may be sensible. |

**Why I would prefer prebuilt for that future network:** I would then manage both home and lab infrastructure, so dependable household connectivity matters more than learning every layer of the gateway. I want the easiest maintainability, a stable supported setup, and quick configuration/recovery, not another ongoing hardware/OS/plugin project. More control is not automatically more useful; it can add responsibilities without serving the actual requirements. A prebuilt product does not guarantee better reliability than OPNsense, so verify support, recovery, and real performance rather than assume the brand solves everything.

This follows a familiar enterprise principle: organizations often buy integrated networking platforms, for example Cisco routers/firewalls with vendor-supported software, instead of assembling generic PCs and their routing stack. Those products **still run an OS** and need patching, backups, and administration; the transferable idea is to use an integrated, supported platform for predictable operation, not to buy enterprise-grade equipment or claim there is no maintenance. I can keep learning networking through segmentation, policy, VPNs, and troubleshooting without maintaining the underlying gateway OS myself.

**Budget:** avoiding a second router can fund roughly the same **€250–€350 gateway/Wi-Fi planning budget** otherwise allocated to the lab appliance. Compare the whole cost, including APs, PoE, any controller, and recurring fees. An already-bought appliance is a sunk cost unless returned or resold; do not assume cash has been recovered or replace working equipment solely to consolidate. Check ISP handoff/bridge mode, prefix delegation, and whether the old NAT66 workaround is supported before choosing.

### Configuration, Backups, and Public Documentation

**Full router IaC is not a requirement for this future setup.** The earlier OPNsense automation goal need not dictate the replacement. For one stable household gateway, a small number of careful UI steps can be easier to maintain than custom automation that must track API changes, protect credentials, and preserve complex apply/rollback behavior. Manual configuration is acceptable when it is limited, documented, repeatable, and backed up; it does not mean untracked experimentation. Use supported automation later where scale or recurring changes justify it.

Keep a sanitized record of intended VLANs, access policies, and changes, and create protected configuration backups before and after significant changes and before updates. Encrypt backups, restrict access, retain copies outside the gateway, and test restore/local recovery. Check whether restoring also needs account access, matching firmware, or separately backed-up controller settings. A screenshot or public decision record is not a complete recovery artifact.

**Be even more careful because this repository is public and the gateway serves the household too.** Apply [Security and Public Repository](../0_Security_and_Public_Repository.md): publish principles and reserved examples, not the live home configuration. Keep raw gateway/controller exports, credentials, VPN keys, real public addresses/domains, device identifiers, and identifying household/client information outside Git. Private VLAN/subnet examples are not inherently secrets, but avoid publishing a detailed live household inventory or access map. Review screenshots, logs, and backups for sensitive values; public configuration-as-code is not a reason to expose actual network settings.

### TODO: Documents and Setup to Update Later

When this future proposal becomes an implementation decision, carry the reasoning above into the following documents **together**, rather than change the current choices now:

- **TODO — [Hardware Prerequisites](./1_Design_Hardware_Prerequisites.md#part-1--networking-hardware):** replace the active separate-firewall-appliance recommendation with the selected shared gateway, actual buying requirements, Wi-Fi/switch needs, total budget, and ease-of-maintenance rationale. Update [Current Personal Setup](./1_Design_Hardware_Prerequisites.md#current-personal-setup) only after purchase/migration is confirmed; preserve the old purchase as history if relevant.
- **TODO — [Software Prerequisites: Router & Firewall Software](./2_Design_Software_Prerequisites.md#router--firewall-software):** replace the current OPNsense selection with the chosen prebuilt platform and rejected alternatives. Include the household reliability priority, enterprise analogy, accepted vendor dependence, limited manual configuration, backups, and privacy rationale. Update the [stack summary](./2_Design_Software_Prerequisites.md#software-stack-at-a-glance) and [configuration-management boundary](./2_Design_Software_Prerequisites.md#configuration-management), rather than assume Linux/OPNsense roles apply to vendor firmware.
- **TODO — [Network Design](#network-setup-options):** revise the chosen topology, household ownership/scope, home/lab/IoT segmentation, firewall policy, management access, recovery, and IPv6 approach after validation. Do not assume the router can also be a general-purpose SSH jumphost; assess using the existing management VM. Recheck addressing and ISP compatibility before migrating.
- **TODO — [Network Setup](../2_Setup/2_Setup_Network.md):** replace legacy Pi/separate-router instructions with the selected vendor's setup, protected backup/restore, migration/rollback, and verification procedure. Confirm household internet works with the hypervisor, management VM, and cluster powered off, and test allowed/denied traffic in both address families.
- **TODO — [Hosts & Nodes Setup](../2_Setup/4_Setup_Hosts_Nodes.md) and [Monitoring Design](./7_Design_Monitoring.md):** adjust management access and supported router monitoring where needed. Update corresponding automation only after selecting supported APIs; keep required household services independent of lab-hosted tools.

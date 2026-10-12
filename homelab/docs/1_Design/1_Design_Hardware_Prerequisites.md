# Design: Hardware & Prerequisites

This document is the **central place for every hardware decision in this homelab**: which physical devices are bought, why, with what specs, and from where — networking hardware (router/firewall appliance, switch, cabling) and compute/workload hardware (nodes) alike. If a piece of physical equipment is part of this lab, it is decided here and nowhere else.

Its counterpart is [Design: Software & Prerequisites](2_Design_Software_Prerequisites.md), which is the equivalent central place for every **software** decision (network platform, hypervisor, cluster, automation, observability, backup). Together the two documents own all concrete implementation choices; the remaining design documents (network, cluster, storage) describe the *architecture* and deliberately name no products or tools.

>**IMPORTANT NOTE:** This guide is focused on my personal homelab goals (see [Personal Goals](0_Design_Goals.md)), the purchasing strategy and hardware choices may not be suitable for everyone. So, make sure to adapt it to your own needs and constraints.

## Why All Hardware Is in This One File

Hardware is one decision, made once, for one reason: **"what do I buy?"** Splitting that across several files would not make it smaller, only harder to answer.

- **One place to look for every physical device.** The router, the switch, the cables, and the nodes are bought against the same budget, from overlapping channels, under the same trade-offs (new vs. refurbished, official store vs. marketplace). Separating "networking hardware" from "compute hardware" would duplicate the purchasing reasoning in two places and let the two copies drift apart.
- **Every architecture document stays clean.** Because all brands, models, and prices are centralized here, the network and cluster design documents can describe topology, segmentation and policy without naming a single product — the classic separation between *architecture* and *implementation*.
- **Replacing a device is a one-file change.** Swap a node or the router and only this file changes; nothing else has to be hunted down and kept in sync.
- **Length is not the problem; structure is.** A long document with clear headings, tables and anchors is searchable (`Ctrl+F` finds everything), diffable in one review, and readable top to bottom. Split only when the parts have genuinely different audiences or lifecycles — which is exactly why *software* got its own document (see [the rationale there](2_Design_Software_Prerequisites.md)) and why hardware did not need further splitting.

## Table of Contents

- [Current Personal Setup](#current-personal-setup)
  - [Network](#network)
  - [Compute / Workload](#compute--workload)
- [Part 1 — Networking Hardware](#part-1--networking-hardware)
  - [General Home Network Design](#general-home-network-design)
  - [Network Platform: UniFi](#network-platform-unifi)
  - [ISP Modem](#isp-modem)
  - [Router / Firewall: Cloud Gateway Max](#router--firewall-cloud-gateway-max)
  - [Managed Switch](#managed-switch)
  - [Wi-Fi Access Points](#wi-fi-access-points)
  - [Ethernet Cables](#ethernet-cables)
  - [Purchasing, Cost, and Accepted Trade-offs](#purchasing-cost-and-accepted-trade-offs)
  - [Why Not a Separately Maintained Firewall PC](#why-not-a-separately-maintained-firewall-pc)
- [Part 2 — Compute / Workload Hardware](#part-2--compute--workload-hardware)
  - [Hardware Purchasing Strategy](#hardware-purchasing-strategy)
    - [New vs. Refurbished vs. Second-Hand](#new-vs-refurbished-vs-second-hand)
    - [Refurbished Shops in Europe](#refurbished-shops-in-europe)
    - [Why Not Amazon, AliExpress or eBay for Refurbished Compute](#why-not-amazon-aliexpress-or-ebay-for-refurbished-compute)
    - [Tip: Ask Your Employer](#tip-ask-your-employer)
    - [What to Check When Buying Refurbished](#what-to-check-when-buying-refurbished)
  - [Hardware Type Selection](#hardware-type-selection)
    - [Comparison: Main Compute Options](#comparison-main-compute-options)
    - [CPU Comparison: Families and Performance Tiers](#cpu-comparison-families-and-performance-tiers)
    - [Why Mini PCs](#why-mini-pcs)
    - [Why Enterprise-Grade (e.g. Dell, Lenovo, HP)](#why-enterprise-grade-eg-dell-lenovo-hp)
    - [Why NOT Raspberry Pi](#why-not-raspberry-pi)
  - [Node Setup](#node-setup)
    - [How Many Nodes](#how-many-nodes)
    - [Recommended Node Composition](#recommended-node-composition)
    - [Recommended Specs per Node](#recommended-specs-per-node)
    - [Start Small, Expand Later](#start-small-expand-later)
- [Software](#software)

---

## Current Personal Setup

My setup is split into **shared home-and-lab networking** (the things that move packets) and **compute/workload** (the things that run VMs and containers). The separate lab-router direction is superseded: one physical UniFi gateway, managed switch, and two wired APs serve both home and lab, isolated through VLANs and firewall policy. This also documents hardware the household needs independently of the lab. See [Network Design — One Shared Gateway with Segmentation](3_Design_Network.md#chosen-one-shared-gateway-with-segmentation) for that decision and [Network Setup](../2_Setup/2_Setup_Network.md) for implementation documentation; the historical setup procedure is marked superseded pending verified GUI steps.

### Network

| Role | Device | Key specs | Price | Source | Why chosen |
|------|--------|-----------|-------|--------|------------|
| ISP connection | ISP-provided modem / access termination | Provider-compatible; bridge/passthrough where available | Existing service equipment | ISP | Retain the provider's access equipment; model/mode to verify privately |
| Shared router / firewall | UniFi Cloud Gateway Max, no optional NVR storage | 5× 2.5GbE RJ45; local UniFi Network management; routed VLANs and firewall | €238 | [Ubiquiti Store Europe](https://eu.store.ui.com/eu/en), new | Integrated home-and-lab gateway; no separate router OS/controller VM |
| Managed PoE switch | UniFi Lite 8 PoE | 8× 1GbE; 4× PoE+; 52 W total PoE budget; VLAN support | €132 | [Ubiquiti Store Europe](https://eu.store.ui.com/eu/en), new | VLAN-aware wired access and power for both APs |
| Wi-Fi access points | 2× UniFi U6+ | Dual-band Wi-Fi 6; 2×2 per band (2.4GHz and 5GHz bands); 1GbE wired uplink; PoE; VLAN-mapped SSIDs | €238 total (€119 each) | [Ubiquiti Store Europe](https://eu.store.ui.com/eu/en), new | Two wired coverage points without a separate mesh ecosystem |
| WAN cable (ISP modem → router) | ISY IPC-6100-1-GB, Cat6, 10 m | Cat6, 10 m | €18.99 | MediaMarkt (new) | Long enough to run from the meter cabinet to the work room, through a wall or conduit if needed. |
| Router → switch and switch → hosts | ISY IPC-1012 CAT6A U/UTP Slim, 0.75 m | Cat6A, 0.75 m | €9.99 each | MediaMarkt (new) | Short patch cables keep the rack/shelf tidy; Cat6A is future-proof for 2.5GbE and beyond. |

> **Recorded purchase prices (2026-10), not current quotations:** gateway + switch + two APs total **€608**, excluding existing ISP equipment, cabling, and any delivery charges. All three UniFi product choices were bought from the official EU store. The switch and AP uplinks are gigabit: the gateway's 2.5GbE ports do not make the whole LAN multi-gigabit. See [Part 1](#part-1--networking-hardware) for alternatives and the [network design](3_Design_Network.md) for topology and policy.

### Compute / Workload

| Role | Device | CPU | RAM | Storage | Price | Source | Why chosen |
|------|--------|-----|-----|---------|-------|--------|------------|
| Compute node 1 | Dell OptiPlex 7050 Micro | Intel Core i5-7500T (3.2 GHz, TODO: cores and threads per core) | TODO: 32 or 64 GB | TODO: 512 GB or 1 TB SSD | €TODO: what did I buy them for eventually in 2026 | BackMarket (refurbished) | Enterprise-grade reliability, silent, low power (≈15W), VT-x/VT-d for virtualization, widely available refurbished at a good price (see [Why Enterprise-Grade](#why-enterprise-grade-eg-dell-lenovo-hp)). |
| Compute node 2 | Old personal Acer laptop (Acer Aspire A715-75G) | Intel Core i7-9750H (2.60 GHz, 6 cores, 2 threads per core) | 16 GB | 512 GB SSD | ≈€600 in 2020 | Personal (repurposed), bought on Coolblue | Already on hand — repurposed to add a second physical host to experiment with, without extra purchasing cost. |

>**What I think is the best value here (for my personal homelab, which is mostly used for learning and experimenting (see [Personal Goals](./0_Design_Goals.md))):** one refurbished enterprise mini PC with as much RAM as you can get (32 GB is enough) plus one machine you already own. That combination costs the least, uses the least power, and still covers ~95% of the learning value (see [How Many Nodes](#how-many-nodes)). Essential network equipment is bought **new** for straightforward support and warranty; workload hardware is worth buying **refurbished**.

---

## Part 1 — Networking Hardware

### General Home Network Design

Start with the ordinary home network, not a separate stack bought only for the lab. The modem terminates the ISP connection; the router provides the firewall and routing; the switch expands wired connectivity and carries VLANs; access points provide Wi-Fi. These responsibilities are separate even when a consumer all-in-one box combines them. See the [layered network topology](3_Design_Network.md#network-topology--design) for how these roles fit together.

```text
Internet
  |
ISP modem (bridge/passthrough preferred when supported)
  |
UniFi Cloud Gateway Max (one home-and-lab router/firewall + local console)
  |
UniFi Lite 8 PoE (managed VLAN switch, 1GbE uplink)
  +-- PoE + Ethernet --> U6+ AP 1 --> Home / IoT / Guest Wi-Fi
  +-- PoE + Ethernet --> U6+ AP 2 --> Home / IoT / Guest Wi-Fi
  +-- Ethernet -------> Wired household devices
  +-- VLAN trunks ----> Lab hosts and VMs

Shared equipment; separate Home, Lab, Management, IoT, and Guest VLANs.
No additional downstream lab router; lab compute may be switched off.
```

The gateway is **dedicated physical network hardware**, but it is not a separately maintained general-purpose firewall PC. It runs independently of Proxmox and Kubernetes. The [network design](3_Design_Network.md) owns segmentation, firewall policy, addressing, the layered topology, and the accepted shared failure domain.

The decisions below follow the software document's format: **what it is**, **chosen + date**, and **alternatives considered**. Prices are recorded purchases, not current quotations.

### Network Platform: UniFi

**What it is.** Integrated management for router/firewall, switches, and Wi-Fi APs: VLANs, port profiles, SSIDs, firmware, and troubleshooting in one place.

**Chosen (2026-10): [Ubiquiti UniFi](https://ui.com/).** Widely used in homelabs, prosumer networks, and small businesses, UniFi offers business-style features without the cost and complexity of many enterprise platforms. It is not exclusively a consumer brand or provably "the most popular" everywhere. Its appeal here is capability per euro, a broad range, extensive community guidance, and cohesive local administration.

The Cloud Gateway hosts UniFi Network, so no controller VM or CloudKey is required. Essential networking does not depend on lab compute. VLAN switching, per-SSID VLANs, and routed firewall policy support a lab while the integrated UI simplifies household operation. Core local networking has no mandatory subscription; optional services are separate.

**Alternatives considered:**

| Alternative | Why not chosen here |
|---|---|
| **[TP-Link Omada](https://www.tp-link.com/en/omada/)** | Strong value and integrated management; a serious alternative. Controller placement/features vary by model. UniFi's selected local console and hardware mix fit this purchase, not a universal quality ranking. |
| **[NETGEAR](https://www.netgear.com/) / Insight** | Good managed switches/business Wi-Fi; management/licensing varies by family. Not the selected single local gateway/switch/AP experience. |
| **[MikroTik](https://mikrotik.com/)** | Very capable per euro, but deeper configuration and a steeper learning curve than wanted for household infrastructure. |
| **[ASUS](https://www.asus.com/) / [AVM FRITZ!](https://fritz.com/)** | Convenient home all-in-one devices; routed VLANs, SSID isolation, and switch integration need model-specific checks. |
| **[Aruba Instant On](https://www.arubainstanton.com/)** | Credible small-business AP/switch option; check gateway offerings and cloud-management requirements. Not the selected local-console ecosystem. |
| Mixed vendors | Standards-based Ethernet/VLANs allow this and sometimes lower prices, but multiple tools and firmware lifecycles add work. |
| Firewall PC + independent switch/AP management | More OS/plugin freedom and more integration responsibility; see [why superseded](#why-not-a-separately-maintained-firewall-pc). |

### ISP Modem

**What it is.** Provider-compatible internet termination; depending on the service this may be a modem/router or optical termination.

**Chosen (2026-10): retain ISP-provided access equipment.** No new modem purchase is recorded. Prefer supported bridge/passthrough mode so the gateway owns WAN routing; verify ISP authentication and required TV/voice services first.

**Why a router behind it?** The ISP device prioritizes provider compatibility, not necessarily routed VLANs, detailed firewall policy, or segmented Wi-Fi. A separate gateway gives consistent control of these functions. It does **not** automatically improve speed/security: capacity, configuration, and the ISP service still matter. If the modem must route, document double NAT and its VPN/port-forwarding/IPv6 limitations instead of assuming bridge mode is available.

**Alternatives considered:**

| Alternative | Why not chosen here |
|---|---|
| ISP modem/router alone | Cheapest for a flat LAN, but segmentation/management may be limited. |
| Replacement modem | Needs provider support and a concrete benefit; adds compatibility responsibility. |
| Direct gateway connection to provider handoff | Possible where permitted, but provider requirements/technology must be verified; not assumed. |

### Router / Firewall: Cloud Gateway Max

**What it is.** Physical WAN firewall, inter-VLAN gateway, DHCP/DNS forwarding, and local network administration, independent of lab hosts.

**Chosen (2026-10): [UniFi Cloud Gateway Max](https://techspecs.ui.com/unifi/cloud-gateways/ucg-max), no optional NVR storage, €238.** Five 2.5GbE ports, routed VLANs, stateful firewalling, and a local console give a compact foundation without an OS installation or controller VM. There is **no built-in Wi-Fi or PoE output**; the switch and APs below are intentional components.

**Why Max over Ultra?** The Max offers 2.5GbE LAN and WAN for a future faster switch/direct device. Ultra remains excellent for gigabit: 2.5GbE WAN, four gigabit LAN ports. The premium buys headroom, not stronger VLAN isolation or immediate speed through this gigabit switch/AP setup. Routing/inspection capacity depends on firmware and enabled features; port speed is not guaranteed application throughput.

**Why no storage?** This means **no optional NVMe recording SSD**, not no internal OS storage. Routing, firewalling, and UniFi Network do not need an NVR drive. UniFi Protect camera recording would need suitable recording storage; I have no cameras now, so it has no current benefit. Revisit a compatible drive/tray or recorder only if needed; it is not storage for VMs or a NAS.

**Alternatives considered:**

| Alternative | Why not chosen here |
|---|---|
| **Cloud Gateway Ultra** | Cheaper and adequate for VLANs/firewall/gigabit; Max was selected for multi-gigabit LAN headroom, not because Ultra is poor. |
| **UniFi Express family** | Compact Wi-Fi/routing options vary by generation; this design separates gateway placement from two wired AP locations. |
| **UniFi UXG gateway-only models** | Need separately hosted management here; suitable when a controller already exists. |
| **Higher-tier Cloud Gateways / Dream Machine rack models** | Faster uplinks/capacity, rack integration, or camera capabilities exceed present needs and cost more. |
| **TP-Link Omada gateway** | Credible value; check VLAN/inspection/controller requirements per model. Best paired with an Omada stack. |
| **MikroTik router** | Strong routing/value with more configuration depth than wanted here. |
| **NETGEAR / ASUS / FRITZ! router** | Good home options; VLAN/firewall/AP-management varies by model, unlike this selected cohesive stack. |
| **Topton / CWWK / Qotom / Protectli PC** | Open router-OS flexibility, but OS/plugins/compatibility/integration ownership remain. |
| Router VM on lab hypervisor | Host outages take household routing and its recovery path down; only for isolated experiments. |

### Managed Switch

**What it is.** Layer 2 fan-out carrying VLAN trunks and access ports; the gateway does inter-VLAN routing.

**Chosen (2026-10): [UniFi Lite 8 PoE](https://techspecs.ui.com/unifi/switching/usw-lite-8-poe), €132.** Eight gigabit ports, four PoE+ ports, **52 W total PoE budget**, silent fanless cooling, and integrated port/VLAN management. It powers the APs without separate injectors.

Two U6+ APs have a published maximum consumption of 9 W each, comfortably within the budget. Check per-port and total power before adding devices; four PoE ports cannot necessarily all deliver their individual maximum simultaneously. The gateway uses no switch PoE.

| Management type | Capability | Fit |
|---|---|---|
| **Unmanaged** | Plug-and-play, no configurable VLAN membership/trunks/access ports. | Unsuitable as the main segmentation switch; passing tags is not enforcing boundaries. |
| **Smart / easy managed** | Usually basic VLANs/port controls via local UI; varies by model. | Can suffice after checking exact 802.1Q and management-isolation behavior. |
| **Managed** | VLANs/port profiles, monitoring, and typically more policy/loop controls. | Chosen for integrated management and PoE; Layer 3 enterprise routing is unnecessary. |

Require enough ports, 802.1Q, configurable access/trunk ports, restricted management, compatible PoE/budget, and appropriate uplinks. One gateway uplink, two APs, and two lab hosts leave three of eight ports for home devices/spares.

**Gigabit suits current light workloads**, but each link and the shared gateway uplink caps at 1Gbps. Concurrent/inter-VLAN flows can contend; the Max does not remove this bottleneck. Upgrade for an actual multi-gigabit NAS, faster internet, or port-count requirement, not simply because faster exists.

**Alternatives considered:**

| Alternative | Why not chosen here |
|---|---|
| **UniFi Flex Mini** | Cheaper managed connectivity, fewer ports, no downstream PoE. Injectors/expansion reduce savings. |
| **UniFi Lite 16 PoE** | More ports/power than needed initially. |
| **UniFi Flex 2.5G / other multi-gigabit switches** | Useful for faster hosts/NAS; check exact PoE/non-PoE variant and power source. No current speed requirement. |
| **UniFi Enterprise / Pro Max PoE** | More capacity/features, cost/size, and potentially power/noise; oversized now. |
| **NETGEAR GS305E / TP-Link TL-SG105E** | Cheap smart VLAN switches, including the former direction, but five ports/no AP PoE mean injectors and little expansion. Valid for smaller wired-only labs. |
| **TP-Link Omada managed PoE** | Competitive and capable; strongest with an Omada stack. Avoid mixed management for now. |
| **NETGEAR managed PoE / Aruba Instant On** | Credible alternatives; compare ports, budget, management/licensing per model. No compelling reason to split this stack. |
| Unmanaged switch | Cheapest, but cannot enforce the intended segmentation. |

### Wi-Fi Access Points

**What it is.** Wireless access bridged onto the appropriate VLAN, using wired backhaul rather than another router/NAT layer.

**Chosen (2026-10): 2× [UniFi U6+](https://techspecs.ui.com/unifi/wifi/u6-plus), €238 total (€119 each).** Dual-band Wi-Fi 6, 2×2 MIMO per band, gigabit Ethernet, PoE, and VLAN-mapped SSIDs. Home, IoT, and Guest wireless clients use the same segments as wired clients; AP administration stays restricted.

Two coverage points are preferable here to one AP transmitting through every wall. Placement, construction, interference, and clients determine actual coverage/roaming; test rather than guarantee it. Use wired backhaul, sensible channel/power settings, and WPA2/WPA3 as supported. Keep SSID count small to limit overhead.

There is no 6 GHz radio or multi-gigabit uplink. Wireless PHY rates are not application speeds; gigabit Ethernet remains a ceiling. Both APs use the chosen PoE switch, without separate injectors.

**Alternatives considered:**

| Alternative | Why not chosen here |
|---|---|
| **UniFi U6 Lite / older Wi-Fi 5 APs** | Potentially cheaper, including used; U6+ gives dual-band Wi-Fi 6 and new-device condition. Compare actual prices/availability. |
| **UniFi U6 Pro / U6 Enterprise** | More capacity/bands depending on model; extra cost without a demonstrated need. |
| **UniFi U7 family** | Wi-Fi 7/newer uplinks; features vary. Check clients, PoE, and switches; not needed for this gigabit access layer. |
| **UniFi wall / outdoor APs** | Appropriate for those installation needs, absent here. |
| **TP-Link Omada EAP** | Strong VLAN-capable Wi-Fi value, particularly in an Omada ecosystem. |
| **NETGEAR business / Aruba Instant On APs** | Credible segmentation; another management system adds little here. |
| **ASUS mesh / TP-Link Deco / NETGEAR Orbi** | Convenient coverage, but per-SSID VLAN/backhaul support varies. Another mesh/router ecosystem is unnecessary. |
| ISP Wi-Fi / single all-in-one router | Less cost, but placement/segmentation may not meet this plan. |
| Wireless mesh backhaul | Useful without cabling, but consumes airtime and adds interference/availability dependencies. |

### Ethernet Cables

**What it is.** WAN/LAN links and wired PoE backhaul.

**Chosen (2026-10): retain the [inventory's](#network) Cat6/Cat6A cables and add measured AP runs as needed.** The 10 m WAN and 0.75 m patch cables suit the work-room layout. AP cable purchases/lengths still need recording. Use standards-compliant copper cable suitable for installation/PoE, not copper-clad aluminium.

**Alternatives considered:**

| Alternative | Why not chosen here |
|---|---|
| Router/switch beside modem | Valid with accessible, ventilated placement; needs longer LAN/AP runs. |
| Cat5e | Suitable existing runs support gigabit; retain already owned Cat6/Cat6A without replacing good cable merely for its label. |
| Fibre | Useful longer/faster links, but cannot power APs and adds equipment. |
| Powerline / wireless | Convenient, but more variable performance/troubleshooting than Ethernet. |

### Purchasing, Cost, and Accepted Trade-offs

**All UniFi gear was bought new from [Ubiquiti Store Europe](https://eu.store.ui.com/eu/en).** At purchase time, Coolblue and MediaMarkt stocked a smaller subset and had less attractive prices for these choices. The official store supplied the desired models with direct product information. This is not a permanent cheapest-store claim; compare VAT, shipping, warranty/returns, and availability for later purchases.

**€608 is not cheap, but not an unusually expensive complete managed home-network foundation**: routing/firewall, PoE switching, and two APs. It saves **a lot of time** compared with OPNsense plus separate device management, and much more compared with maintaining a hand-built Linux/Ansible router. This is expected operational savings, not a measured hours-per-month guarantee.

The previously considered cheapest Topton N100 on AliExpress was about **€350 with 8 GB RAM and a 128 GB SSD** at the time, for a firewall PC alone. Household routing, switches, and APs still needed providing independently. The €238 gateway replaces that role, leaving €112 of that comparison budget toward switch/APs. The full package is not cheaper than the PC alone; it avoids duplicating essential home-and-lab infrastructure.

**Accepted trade-offs:** vendor lock-in, less OS/plugin flexibility, vendor firmware/support dependence, limited hardware upgrades, and GUI settings rather than complete IaC. Standards-based VLANs/Ethernet allow future mixed-vendor replacement, but migration costs effort. Gigabit access and a shared gateway failure domain are deliberate limits too. See the [shared-gateway boundaries](3_Design_Network.md#chosen-one-shared-gateway-with-segmentation) and [network maintenance and recovery approach](3_Design_Network.md#maintenance-recovery-and-safe-experiments).

The benefits significantly outweigh those costs for my [goals](0_Design_Goals.md): fewer components, simpler troubleshooting/recovery, consistent security policy, less duplicated hardware, and more learning time. Manual steps are acceptable when few, documented, privately backed up, and tested. Developing automation for every setting would reintroduce the maintenance this choice removes. See [Network Setup](../2_Setup/2_Setup_Network.md) for the implementation record and the [security guide](../0_Security_and_Public_Repository.md) for handling backups and publishable examples.

### Why Not a Separately Maintained Firewall PC

**First setup: a hand-built Linux router on a Raspberry Pi, configured with Ansible.** The Pi's built-in Ethernet port connected to the ISP modem/home LAN, and a USB-to-Ethernet adapter connected to the lab switch. The Pi was a separate downstream lab router, not the shared household gateway. Raspberry Pi OS supplied the general-purpose Linux base; custom Ansible roles assembled the router functionality: network interfaces and VLANs, kernel IP forwarding, dnsmasq for DHCP/DNS and IPv6 Router Advertisements, and nftables for firewalling and IPv4 NAT/IPv6 NAT66. It also served as an SSH jumphost into the lab. The [historical Network Setup](../2_Setup/2_Setup_Network.md) records that procedure, including [router configuration with Ansible](../2_Setup/2_Setup_Network.md#step-4-configure-the-pi-with-ansible).

**Why that was retired.** Ansible made the configuration repeatable, but did not turn the individually configured Linux services into a supported router platform. I still owned their integration, role development, package/kernel compatibility, dual-stack firewall correctness, troubleshooting, and recovery. The Pi also added adapter and SD-card dependencies. This was valuable for learning fundamentals, but maintaining the router implementation became more work than the learning justified. The problem was not Ansible itself; it was using custom automation to build and maintain functionality already supplied by purpose-built router software. Ansible remains useful for supported lab hosts and VMs; see its [current configuration-management scope](2_Design_Software_Prerequisites.md#configuration-management).

**Next direction: an x86 firewall appliance with OPNsense.** A Topton-style mini PC with native Ethernet ports and SSD storage addressed the Pi hardware compromises, while OPNsense integrated routing, firewalling, DHCP/DNS, and management rather than having me assemble those services. This was a substantial improvement over the hand-built Linux/Ansible setup. However, owning the firewall OS, configuring its features, and managing switches/APs alongside it still required more lifecycle work than wanted for essential networking. That direction is now superseded: a Topton or equivalent firewall PC and separately installed OPNsense/pfSense are no longer selected.

**Current choice: one integrated physical gateway for home and lab.** UniFi is still dedicated physical router/firewall hardware; the removed burden is the separately maintained general-purpose firewall platform and second lab-router stack. Shared switching and wired APs complete the household network, with VLANs and firewall policy providing logical separation. See [Network Setup Options](3_Design_Network.md#network-setup-options) and [One Shared Gateway with Segmentation](3_Design_Network.md#chosen-one-shared-gateway-with-segmentation) for the architectural comparison and reasoning.

OPNsense remains good for open extensibility, detailed control, and router-OS learning. That is not the priority for household infrastructure. UniFi still needs firmware updates/security care but reduces integration/development responsibility. See the [software decision](2_Design_Software_Prerequisites.md#router--firewall-software) for comparisons and the future VPN TODO.

**Learn separately:** run OPNsense or another router OS in an isolated lab VM for routing/firewall practice while the shared network stays stable if you want to learn the internals and operational aspects of a router OS/networking in more depth. No need to rebuild DHCP, DNS, firewalling, and routing manually with Ansible; a purpose-built router OS offers plenty to learn. Follow the [network's safe-experiment boundaries](3_Design_Network.md#maintenance-recovery-and-safe-experiments).

---

## Part 2 — Compute / Workload Hardware

This part covers the machines that actually run workloads: Proxmox hosts, VMs, and the Kubernetes cluster. The purchasing logic here is **the opposite of the router**: buy refurbished enterprise hardware, from dedicated refurbishers, not from marketplaces.

### Hardware Purchasing Strategy

#### New vs. Refurbished vs. Second-Hand

| Feature | Brand-New Retail | Professional Refurbished | Private Second-Hand |
|---|---|---|---|
| **Price** | Usually highest; budget mini PCs can overlap | Often substantially cheaper for the performance | Cheap, but high risk |
| **Quality Control** | 100% factory-tested | Tested on critical points | No guarantees |
| **Battery / Wear** | 100% capacity / brand-new | Minimum guarantees (e.g. 85%), otherwise replaced | Unknown (often worn out) |
| **Warranty** | Standard 2-year warranty | 1–2 years full refurbisher warranty | "Warranty until the front door" — basically none |
| **Sustainability** | Requires new materials & manufacturing | Very circular (prevents e-waste) | Circular, as long as the device works |

**Verdict:**
- **Brand-new** → Even inexpensive consumer mini PCs, such as Beelink models, can be tempting, but newness alone does not make them better value for this compute role. For a similar or lower price, a professionally refurbished enterprise mini PC often provides stronger CPU performance, more memory, better upgrade options, and business-grade virtualization features. Compare the exact CPU, RAM, storage, upgradeability, and warranty: a new consumer model can still make sense if it wins on those specifics, but this lab prioritises the performance and capability per euro of refurbished business hardware. Essential network equipment is the deliberate exception: new integrated devices with straightforward support and warranty serve the household as well as the lab (see [Networking Hardware](#part-1--networking-hardware)).
- **Professional refurbished** → Best balance. Enterprise-grade hardware (e.g. Lenovo, Dell, HP) at 40–80% less. These units come from companies replacing their fleets — the hardware is still high quality, power-efficient, and tested. This is the right choice for a home lab focused on learning real-world skills without breaking the bank. You pay more compared to private second-hand (e.g. via Amazon, eBay, Marktplaats, etc.), but the risk is significantly lower and the hardware will last longer and perform reliably. So, paying a bit extra compared to private second-hand is worth it for the peace of mind and reliability.
- **Private second-hand** (e.g. Marktplaats, eBay, Amazon, etc.) → Too risky. No proper testing, no guarantees. Avoid.

> **What is "refurbished"?** A previously used device that has been professionally inspected, cleaned, and extensively tested. Only when everything checks out technically is it offered as Refurbished. Not the same as second-hand.

#### Refurbished Shops in Europe

**Refurbed and Back Market are my two leading options**, with no fixed preference between them. Both offer refurbished business hardware through marketplace listings, so compare the actual device and seller terms rather than assuming one platform is always better.

| Factor | [Refurbed](https://www.refurbed.nl) | [Back Market](https://www.backmarket.nl) |
|---|---|---|
| **Marketplace and quality** | EU-wide marketplace with partner refurbishers and stated quality standards. | Large European marketplace with offers from different sellers; listing details and available stock can vary. |
| **Likely advantage** | A more consistent refurbishment framework may make it easier to compare offers. | More seller and listing variation can provide different configurations and prices to compare. |
| **What to check** | Confirm the listed CPU, RAM, storage, condition grade, warranty, and return terms for the specific offer. | Confirm the listed CPU, RAM, storage, condition grade, warranty, and return terms for the specific offer. |

Choose whichever has the better specific offer: the right CPU and upgradeable RAM, enough storage, a clearly described condition, suitable warranty and return terms, and a competitive delivered price. Marketplace policies and individual offers can change, so verify the terms on the listing before buying.

**Other shops considered but not selected:**

| Shop | Notes | Why not selected |
|---|---|---|
| **ReMarkt** | Dutch refurbisher with physical stores (ex-MediaMarkt). 12-month warranty, in-store testing, Dutch customer service. | Not chosen — limited mini PC selection, Dutch-local only. Refurbed EU is better. |
| **IT-Giant** | Dutch webshop for refurbished business hardware (servers, workstations, mini PCs). Lowest prices for business-grade gear, popular with home-lab builders. | Not chosen — Dutch-local only. Refurbed EU is better. |
| **ITSCO** | German specialist for refurbished business hardware, including enterprise mini PCs, with detailed specifications. | Not chosen — I am keeping the shortlist to Refurbed and Back Market, whose EU-wide marketplaces better fit my preference for straightforward shopping and buyer support. |
| **AfB Shop** | German social enterprise selling refurbished business IT, with its own refurbishment process and warranty support. | Not chosen — its reliable service is appealing, but I prefer the broader selection and simpler comparison across Refurbed and Back Market. |
| **LapStore** | German specialist with a broad selection of used business hardware. | Not chosen — fluctuating stock would mean more searching, while Refurbed and Back Market already meet my needs. |
| **MediaMarkt / Coolblue** | Mostly brand-new; not ideal for refurbished mini PCs. Useful for switches, cables and accessories (as used above). | Not relevant for compute. |

#### Why Not Amazon, AliExpress or eBay for Refurbished Compute

This differs from buying new network gear through the [official store](#purchasing-cost-and-accepted-trade-offs): **for new hardware you are buying a supported product, for refurbished hardware you are buying a process.** The marketplace model breaks down when the value of the product is the quality of the inspection that was done to it.

| Channel | Why not for refurbished compute |
|---|---|
| **AliExpress** | Effectively no refurbished enterprise market — these machines were sold to European companies and are retired in Europe. Anything listed as "used" is unverifiable, shipping a 1 kg mini PC from China makes no economic sense, and a return means shipping it back across the world. |
| **Amazon Renewed** | There *is* a warranty, but the grading is done by whichever third-party seller listed it, with no published refurbishment process. Prices are generally higher than dedicated refurbishers for a lower-quality guarantee. |
| **eBay / Marktplaats** | No testing, no grading standard, no warranty, seller risk. You cannot tell a 4-year-old fleet machine from a machine that was pulled because it was failing. |

By contrast, **Refurbed and BackMarket are built around the refurbishment process itself**: vetted partner refurbishers, a published grading system, a minimum 12-month warranty, a 30-day return window, and a marketplace that arbitrates when a unit does not match its grade. For a device that will run 24/7 for years, that process *is* the product. Both are also EU-based, so warranty and returns are covered by EU consumer law and do not involve international shipping.

#### Tip: Ask Your Employer

Companies replace hardware on a fixed cycle — often every 3–5 years, regardless of whether a device still works perfectly. Before spending money on a refurbished shop, it's worth simply asking your manager or IT department whether any old devices are being decommissioned. Many companies are happy to give them away for learning purposes to employees rather than deal with disposal. If not, that is also fine of course — you can always turn to refurbished shops or other sources.

> **Important:** Before using any company device for personal purposes, make sure you have explicit permission from your manager or IT department. Do not assume it is allowed — company hardware is company property until formally decommissioned and released.
>
> Once you have a device: **ensure all company data has been fully wiped and the device has been factory reset or re-imaged before use.** This protects both you and your employer. A full disk wipe (e.g. `shred`, `dd`, or a secure erase tool) or reinstalling the OS from scratch is the safest approach, your IT department can provide guidance on the best method to ensure data security and compliance.

#### What to Check When Buying Refurbished

- **Certification**: Look for *Keurmerk Refurbished* (NL) or an equivalent quality label.
- **Refurb process**: Check that the seller lists their full refurbishment process and read it carefully.
- **Battery health**: Aim for 80%+ capacity, or a replaced battery.
- **Warranty length**: Minimum 12 months recommended.
- **Return policy**: 14–30 days is standard for reputable sellers.
- **Condition grading**: "Like New" vs. "Very Good" can mean big price differences — read the grading definitions carefully.

### Hardware Type Selection

#### Comparison: Main Compute Options

| Category | CPU Power | RAM | Storage | Noise | Power Usage | Virtualization | Cost | Best Use Case |
|---|---|---|---|---|---|---|---|---|
| **Raspberry Pi** | Low | 1–8 GB | SD / USB SSD | Silent | Very low (5–10W) | Limited (ARM) | €50–€150 | Lightweight services, learning Linux |
| **Mini PC** | Medium to high | 8–64 GB | NVMe SSD (most common) | Silent / very quiet | Low (10–40W) | Excellent | €150–€600 | Proxmox, Docker, Kubernetes, CI/CD |
| **Laptop** | Medium | 8–32 GB | NVMe SSD | Quiet | Low–medium (10–60W) | Good | €200–€600 | Portable DevOps work, Docker, k3s |
| **Server / Workstation** | Very high | 32–256 GB | RAID SSD/HDD | Very loud (even at idle — ever been in a data centre? That constant hum comes from these machines) | Very high (100–300W) | Enterprise-grade | €300–€800 | Production workloads (overkill for home labs) |

> A great DevOps home lab focuses on **production-like architecture, not production-grade hardware**. You don't need enterprise servers (very harmful for your wallet and your ears) — but you do need reproducibility, automation, observability, and failure testing, etc.

#### CPU Comparison: Families and Performance Tiers

CPU names describe both a **product tier** (such as Core i5 or Ryzen 5) and a **power/performance class** (often indicated by a suffix such as `U`, `H`, or `T`). A tier name on its own does not guarantee a specific core count, performance, or power draw; those change across generations and device designs. Use this table to shortlist a class, then compare the exact CPU and computer.

| CPU family / tier | Typical processor power class | Relative performance and practical fit |
|---|---|---|
| **Intel Processor N-series** (e.g. N100, N150, N200, N305) | Roughly 6–15 W | Entry-level, efficiency-focused chips. Suitable for a low-cost, low-power host with light services and a modest VM workload. Core counts and performance differ within the family. |
| **Intel Core i3 / Core 3** | Commonly about 15–55 W for mobile models; 35 W or more for desktop models | Entry-level mainstream performance. Can suit a small hypervisor, but check core count and sustained performance before planning several active VMs. |
| **Intel Core i5 / Core 5** | Commonly about 15–55 W for mobile models; 35–65 W or more for desktop models | Mainstream mid-range. Often a good balance for multiple VMs and development workloads, especially when the exact model has enough cores and the system can cool it. |
| **Intel Core i7 / Core 7 and above** | Commonly about 15–55 W for mobile models; 35–65 W or more for desktop models | Higher-tier options with more performance in many generations, but the label alone does not ensure a faster or more efficient CPU than a newer lower-tier model. |
| **AMD Ryzen 3 / 5 / 7 and above** | Commonly about 15–54 W for mobile models; 35–65 W or more for desktop models | Comparable mainstream choices across entry, mid-range, and higher tiers. Check the generation, model suffix, core count, virtualization support, and system cooling. |
| **Older refurbished business CPUs** (Intel Core or AMD Ryzen) | Varies widely; often around 15–65 W by processor class | Can offer good value, but performance per core, efficiency, supported memory, and virtualization capabilities vary substantially by generation and exact model. |

These are **broad processor power classes**, not like-for-like guarantees or whole-computer electricity draw. For example, `U` commonly identifies an efficiency-focused mobile class, `H` a higher-performance mobile class, and `T` a lower-power desktop class; suffix meanings and available models vary by generation. Core i3/i5/i7 and Ryzen 3/5/7 indicate product tiers, not fixed power limits. Intel and AMD also use different power definitions, and boost power may be higher than the nominal figure.

A mini PC's actual wall power also includes the motherboard, memory, storage, network interfaces, power-supply losses, workload, and cooling limits. Treat processor ratings as a rough way to compare classes, not as idle or continuous consumption. For a buying decision, check independent measurements of the exact system at idle and under a representative sustained workload, or measure it with a plug-in power meter.

For a machine left on 24/7, each **10 W of average whole-system draw** uses about **87.6 kWh per year**. At an example electricity price of €0.30/kWh, that is about €26/year; 20 W is about €53/year and 40 W about €105/year. Use your own tariff and measured average draw for a realistic estimate.

**Which class to choose:**

- Choose an **Intel N-series** or similar low-power CPU when low electricity use and light workloads matter more than peak performance. Do not assume that a higher core count in an efficiency-focused chip makes it equivalent to a mainstream Core i5 or Ryzen 5.
- Choose a **Core i3/Ryzen 3-class** machine for modest workloads; a **Core i5/Ryzen 5-class** machine is often a balanced starting point for multiple VMs; consider **Core i7/Ryzen 7-class or higher** when workloads need more parallel CPU capacity. These are starting points, not guarantees—compare exact generations and models.
- Before buying, verify that the exact processor and system support the required virtualization features (such as Intel VT-x/VT-d or AMD-V/IOMMU), that firmware exposes them, and that the model supports the RAM capacity you need. For a hypervisor host, adequate RAM and SSD capacity can matter more than a small CPU-tier difference.

#### Why Mini PCs

- **Strong virtualization performance** — desktop-class CPUs (e.g. Intel i5/i7) handle Proxmox, Docker, and Kubernetes easily.
- **High RAM capacity** — up to 64 GB, which is good for running multiple VMs.
- **Silent operation** — can run 24/7 without fan noise (or minimal noise).
- **Low power usage** — typically 10–40W, far cheaper to run than servers.
- **Affordable** — €150–€400 per refurbished node for strong performance.
- **Compact size** — easy to stack for a small cluster.
- **Reliable business-grade hardware** — built for corporate environments, long lifespan (e.g. Dell, Lenovo, etc., see [Why Enterprise-Grade Hardware?](#why-enterprise-grade-eg-dell-lenovo-hp)).
- **Easy to upgrade** — RAM and NVMe SSD upgrades are simple.
- **Perfect for clustering** — ideal for a multi-node Proxmox or Kubernetes cluster.

#### Why Enterprise-Grade (e.g. Dell, Lenovo, HP)

- **Enterprise-grade reliability** — built for 5–10+ years of nonstop corporate use.
- **Real-world relevance** — the same class of hardware used in actual IT jobs; your lab mimics production.
- **Excellent virtualization support** — stable BIOS, VT-x/VT-d, predictable behaviour under Proxmox, KVM, Docker, and Kubernetes.
- **Long lifespan** — designed for long service cycles, fewer failures, consistent performance.
- **Efficient power usage** — typically 10–40W, far lower than servers or desktops.
- **Quiet operation** — engineered for office environments, silent even under load.
- **Compact form factor** — perfect for stacking multiple nodes without taking up space.
- **Massive refurbished availability** — companies generally replace fleets every 3–5 years regardless of condition, so you get high-quality hardware at low prices.
- **Consistent performance** — stable, predictable components, not the random mix found in consumer machines.
- **Better thermals** — designed to stay cool in dense office deployments.
- **Low failure rate** — higher-quality components than consumer PCs.

#### Why NOT Raspberry Pi

> **Scope note:** This section explains why Raspberry Pi is not preferred for compute nodes. It can still serve lightweight experiments, but is not the selected household gateway: the [integrated network platform](#network-platform-unifi) avoids owning a custom router stack.

Mini PCs give more value for money because they are **complete computers**: a proper x86 CPU, upgradeable RAM, fast NVMe SSD storage, active cooling, a stable power supply, and reliable networking all in one device. They're designed to run 24/7 under load and handle workloads more consistently.

Raspberry Pi boards are bare single-board computers — you still need to add a case, cooling, storage, and sometimes extra networking gear. They also use weaker ARM hardware and rely on microSD cards or add-on storage, which is slower and less reliable. Even though the Pi itself is cheaper, you end up with less performance, less reliability, and less convenience — and it costs more in total than expected once you add all the accessories.

More importantly, the Pi uses ARM/Pi OS instead of x86/Ubuntu or RHEL — which is what you find in real enterprise environments. Mini PCs give a more realistic learning experience that better matches production.

### Node Setup

#### How Many Nodes

**It depends on your situation — 1 node can be more than enough.** If your goal is learning Kubernetes, Docker, Ansible, and monitoring, a single well-specced mini PC handles all of that comfortably. If you are not even filling one node with workloads, buying more nodes just to "have a cluster" is not worth the purchase and energy cost. Add a second node only when you actually need more capacity — and anything beyond 1–2 nodes is only worth it if you intend to host a lot (a full home cloud replacing Netflix, OneDrive, etc.), which is not the goal of this lab (see [Goals](0_Design_Goals.md)).
- **Prioritise fewer, more powerful node(s).** The biggest factor in energy cost is the **number of physical machines**, not how much RAM is in each one. RAM uses very little power compared to the CPU, motherboard, SSDs, and PSU losses — so one node with 64 GB uses roughly the same power as one node with 16 GB, while four 16 GB nodes use roughly 4× the power of one 64 GB node. At ~20W per node and ~€0.30/kWh (NL, 2026):

  | Setup | Total RAM | Typical Power | Est. Yearly Cost |
  |-------|-----------|---------------|------------------|
  | 1 × 64 GB | 64 GB | ~20 W | ~€53 |
  | 2 × 32 GB | 64 GB | ~40 W | ~€105 |
  | 4 × 16 GB | 64 GB | ~80 W | ~€210 |

  Same total RAM, but cost roughly doubles with each doubling of nodes — plus extra purchases, cables, maintenance, and points of failure. In learning value, one well-specced node already covers ~85–90% of DevOps learning; a second adds clustering, migration and multi-node Kubernetes (~95%); three or more add HA, Ceph and quorum — useful, but increasingly niche for a home lab. To practise clustering without buying hardware, temporarily add a machine you already own, spin up 3 VMs on one host to simulate a multi-node cluster (you can still drop a VM to test failover and quorum loss), or practise in a test environment at work where large-scale setups already exist.
- **Balance capacity against availability.** One 64 GB node is cheaper and more power-efficient than two 32 GB nodes, but it is a single point of failure: if it goes down, all workloads stop. Two 32 GB nodes may be worth the extra cost if you want workloads to survive a hardware failure or planned maintenance, provided your platform, storage, and workloads support failover and the surviving node has enough capacity. Two nodes alone do not guarantee high availability; a two-member quorum needs both votes, so safe failover may require a third vote or witness (see [Quorum, in short](#quorum-in-short)). For a typical home lab, 4 × 16 GB nodes are usually unnecessary unless you specifically need the extra capacity or want to practise larger clusters.
- **Quorum, in short.** Quorum means a **majority of voting members agree** the cluster is healthy. That majority is required to elect a leader, commit configuration changes, and confirm writes. Without it the cluster stops making decisions and becomes unavailable — which is the point: it prevents **split-brain**, where two halves both think they are in charge and make conflicting changes.
- **Why odd numbers of voting members.** It is not that HA *requires* an odd total node count — what matters is an **odd number of voting members**, because majority is always `floor(n/2) + 1`:

  | Voting Nodes | Majority Needed | Failures Tolerated |
  |:---:|:---:|:---:|
  | 2 | 2 | 0 |
  | **3** | **2** | **1** |
  | 4 | 3 | 1 |
  | **5** | **3** | **2** |
  | 6 | 4 | 2 |
  | **7** | **4** | **3** |

  **3 and 4 nodes both tolerate only 1 failure** — the 4th node raises the total *and* the consensus bar, and the two cancel out. Only odd increments (3 → 5, 5 → 7) actually buy fault tolerance. With 2 voting nodes, majority = 2, so losing one takes the cluster down even though a machine is still running; with 3, the surviving 2 still form a majority.
- **Where quorum applies.** It applies to **consensus/voting members**, not to every node. In Proxmox, quorum spans all cluster nodes — with 3, losing 1 still leaves a majority and the cluster can fence the failed node. In Kubernetes it applies to the **etcd** cluster (the store for all cluster state) via the **Raft** consensus algorithm, not to worker nodes — typical setups are 1 control-plane node (not HA), 3 (HA, most common), or 5. The same principle holds for ZooKeeper, Consul, and databases with leader election.
- **Common misconception: "HA requires an odd number of nodes."** More accurately: **HA systems using majority-based consensus work most efficiently with an odd number of voting members.** Worker nodes never vote, so an even total (e.g. 3 control-plane + 20 workers) is perfectly fine.
- **When this actually matters.** In **production**, 3 voting members is the recommended minimum. In a **home lab** it is not a hard requirement — running 3 nodes to mimic production while not even filling one is not worth the cost. One well-specced node is a perfectly valid home lab.

#### Recommended Node Composition

- **1 refurbished enterprise-grade mini PC** — your main compute node, providing real-world hardware experience (e.g. Lenovo ThinkCentre Tiny, Dell OptiPlex Micro, HP EliteDesk Mini, etc.). A single well-specced node is enough for learning and running smaller workloads.
- **Optionally a 2nd mini PC or an old laptop you already have** — if you want more capacity or want to experiment with workload distribution. Only worth it if you're actually using the resources on the first node.

#### Recommended Specs per Node

| Component | Recommended | Notes |
|-----------|-------------|-------|
| **CPU** | Low-power Intel N-series for light workloads, or a suitable Core i3/Ryzen 3 class or higher for more VM and build headroom — verify virtualization support on the exact model | Choose using the [CPU family comparison](#cpu-comparison-families-and-performance-tiers), workload, and whole-system power measurements. |
| **RAM** | 32–64 GB | 32 GB is comfortable for running Proxmox with several VMs. 64 GB gives plenty of headroom and is often more power-efficient than running two separate 32 GB nodes (if you need 64 GB RAM total; if you only need 32 GB RAM then you do not need the 64 GB RAM of course) — one well-specced machine uses less energy than two underpowered ones (see [How Many Nodes](#how-many-nodes)). |
| **Storage** | NVMe SSD | Significantly faster than SATA SSD (3–7 GB/s vs ~550 MB/s) and far faster than HDD. Matters for VM boot times, live migration, snapshot I/O, and running multiple VMs in parallel. Most enterprise-grade mini PCs ship with an M.2 slot, making NVMe a natural fit — no cables, no adapters, compact form factor. |

See for how to check hardware specs [reference/os_hardware/Hardware_Specs.md](../../../reference/os_hardware/Hardware_Specs.md#how-to-check-your-hardware-specs).

**Storage sizing — intentional asymmetry:**

Not all nodes need the same storage size. A good approach is:
- **1× larger drive (e.g. 512 GB-1 TB)** on one node — acts as a "shock absorber": migration staging area, ISO storage, snapshots, and local VM disks when you need fast temporary storage, etc.
- **Smaller drives (e.g. 256 GB-512 GB)** on the other compute nodes — sufficient for the OS, Proxmox, and their resident VMs, etc.

This asymmetry is intentional: the larger node handles temporary bulk workloads so the compute nodes stay lean and focused.

#### Start Small, Expand Later

**Start with 1 mini PC or 1 old laptop** and expand later if needed. You can learn all the fundamentals — Kubernetes, Docker, Ansible, monitoring — on a single well-specced node. Only add a second node when you're actually running out of resources on the first one.

If you want to practice clustering or quorum without buying extra hardware, see [How Many Nodes](#how-many-nodes) above — in short you can temporarily add a 3rd node (e.g. an old laptop you already have), use at least 3 VMs to simulate a multi-node cluster, or practice through your work environment if you have access to a larger setup.

That's how I started: my old Acer laptop. Later I expanded to the full setup described in [Current Personal Setup](#current-personal-setup).

---

## Software

All software decisions — the network platform, hypervisor, node and VM operating systems, container orchestration, IaC, configuration management, GitOps/CI, secrets, observability, and backup — live in their own central document: **[Design: Software & Prerequisites](2_Design_Software_Prerequisites.md)**.

The two documents are deliberately symmetrical: this one is the single source of truth for *what hardware is bought*, that one is the single source of truth for *what software runs on it*. Dependencies are explicit in both: the gateway supplies the local network console, the switch powers the APs, and node RAM is sized for the hypervisor and cluster.

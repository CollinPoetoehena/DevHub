# Design: Network

> **Scope of this document: see [README.md/Documents Setup & Scope](README.md#documents-setup--scope); in short: design only — no specific hardware or software.** Concrete devices, prices, and platforms are recorded in [Hardware Prerequisites](1_Design_Hardware_Prerequisites.md#part-1--networking-hardware) and [Software Prerequisites](2_Design_Software_Prerequisites.md#router--firewall-software).

A stable network is the foundation of both household connectivity and a reliable homelab. The chosen design is **one shared physical network infrastructure, with one gateway behind the ISP modem and separate logical segments for home and lab**. There is no additional downstream lab router. Shared infrastructure does not mean a flat LAN: VLANs separate broadcast domains, and firewall policy controls traffic between them.

This is also documentation for the **home network itself**: it records the topology, boundaries, addressing intent, and recovery requirements so the setup is understandable, repeatable, and easier to maintain. It describes the target policy, not proof that every setting has already been applied. Actual configuration and verification belong in [Network Setup](../2_Setup/2_Setup_Network.md); private backups and real access details stay outside this public repository under the [security guide](../0_Security_and_Public_Repository.md).

> **Actual design, example values:** this document describes the chosen home-and-lab network setup, not a hypothetical alternative. Published VLAN IDs, subnets, IP addresses, and other configuration values are illustrative examples, not a record of live settings. The topology, segment roles, and policy intent describe the chosen design; keep the mapping to actual configured values in private operational records. Follow [Security and Public Repository](../0_Security_and_Public_Repository.md#information-that-is-usually-safe-to-document) when documenting those details: private ranges and VLAN IDs are not secrets by themselves, but examples must be clearly labeled and must not expose real access details or identifying information.

See the DevHub [Network Reference](https://github.com/CollinPoetoehena/DevHub/tree/main/reference/network) for networking concepts and troubleshooting, and [Personal Goals](0_Design_Goals.md) for the low-maintenance boundary between household infrastructure and disposable experiments.

## Table of Contents

- [Network Setup Options](#network-setup-options)
  - [Chosen: One Shared Gateway with Segmentation](#chosen-one-shared-gateway-with-segmentation)
- [Required Building Blocks (Design Level)](#required-building-blocks-design-level)
  - [Why Separate Gateway, Switch, and Access Points](#why-separate-gateway-switch-and-access-points)
- [Network Topology & Design](#network-topology--design)
  - [Core / Edge Layer](#core--edge-layer)
  - [Distribution and Access Layers](#distribution-and-access-layers)
  - [Why Wired Access Points Instead of a Mesh System](#why-wired-access-points-instead-of-a-mesh-system)
- [Subnet & VLAN Design](#subnet--vlan-design)
  - [IPv4 Addressing](#ipv4-addressing)
  - [IPv6 Design and Rollout](#ipv6-design-and-rollout)
  - [Switch Port Assignments](#switch-port-assignments)
- [Firewall and Access Policy](#firewall-and-access-policy)
  - [Management Access and Optional Jumphost](#management-access-and-optional-jumphost)
- [Maintenance, Recovery, and Safe Experiments](#maintenance-recovery-and-safe-experiments)
  - [Redundancy: Enterprise Requirements vs. Household Trade-offs](#redundancy-enterprise-requirements-vs-household-trade-offs)

---

## Network Setup Options

| Option | Advantages | Why chosen or rejected |
|---|---|---|
| **Flat home-and-lab LAN** | Few settings and no routed segmentation. | Rejected: lab DHCP mistakes, broadcasts, and compromised workloads share the household broadcast/security boundary. |
| **Segmentation on the ISP device only** | No additional gateway. | Model-dependent VLAN, firewall, Wi-Fi, and management capabilities; not the selected foundation. |
| **Separate home router plus downstream lab router** | A separate routing boundary; useful for deliberately independent experiments. | Previous direction, now rejected for normal operation: duplicated hardware, administration, updates, recovery, and possibly another NAT layer. The home network still needs maintaining anyway. |
| **One shared physical gateway, managed switching, and segmented Wi-Fi** | One routing/firewall policy and management lifecycle, with logical isolation for home and lab. | **Chosen:** best fit for simplicity, cost, minimal maintenance, and independent lab compute. |

### Chosen: One Shared Gateway with Segmentation

Maintaining a separate lab network does not make home-network maintenance disappear. The household already needs a router/firewall, switches, wireless coverage, security updates, and a recovery plan. Reuse that infrastructure and effort rather than buying and managing a second routing setup. One gateway avoids duplicating DHCP/DNS settings, firewall administration, backups, and firmware lifecycles; it also makes selected home-to-lab access easier to reason about.

**Segmentation is a home-network security requirement, not just a lab feature.** Even without a lab, guest clients, IoT devices, trusted household clients, and infrastructure management should have appropriate trust boundaries and least-privilege access; see the [segment roles](#subnet--vlan-design) and [firewall policy](#firewall-and-access-policy). Build that capability into the home network once, then add the lab as another restricted segment rather than leaving the home LAN flat and treating a second router as the only way to isolate experiments.

With separate home and lab routers, there are **two routing stacks to buy, build, secure, update, back up, troubleshoot, and recover**. The home router still needs its own segmentation and security care, while the lab router adds another configuration and maintenance lifecycle. This does not mean every cable, switch, or AP must be bought twice, but it does duplicate routing responsibilities and may require extra hardware and coordination between firewall rules. When the goal is simply to isolate lab traffic (which in this design it is!), the existing VLAN-capable gateway and managed network already provide that boundary; a second router adds no requirement that this design cannot meet.

VLANs contain Layer 2 broadcasts and DHCP within their segments when ports and bridges are configured correctly. The gateway routes between those segments and denies unneeded traffic. A home client can reach an explicitly allowed lab application without gaining access to host management; an IoT client can reach an approved endpoint without reaching every home device. VLAN tagging alone is not a firewall, and neither IPv4 NAT nor a separate subnet automatically enforces these policies.

**Security comes from correct configuration, not the number of routers.** A single, consistently administered gateway can provide strong least-privilege isolation and reduce configuration drift. It is not inherently safer than every two-router design. Shared infrastructure has a shared failure and security boundary: gateway failure, compromise, a bad firmware update, a mistaken rule, or link saturation can affect both home and lab. Segmentation does not provide physical independence or protect availability from all resource contention.

Keep the gateway **physical and separate from the virtualization platform**. Household DHCP, DNS forwarding, and Wi-Fi must work with every lab host switched off. The household depends on the network, not on a lab cluster, controller VM, or experimental service. Disruptive routing experiments belong in isolated virtual networks, not on this essential gateway.

---

## Required Building Blocks (Design Level)

| Building block | Requirements | Reason |
|---|---|---|
| **ISP modem / access termination** | Compatible with the provider's connection and any required voice/TV services; bridge or passthrough mode where supported. | Terminates the ISP service; avoids relying on it for the internal segmentation design. |
| **Shared router / firewall** | Physical WAN/LAN connectivity; routed VLAN interfaces; stateful firewalling; DHCP and DNS forwarding; IPv6 prefix delegation and firewall support if enabled; local management and recoverable backups. | One policy boundary for household and lab, independent of lab compute. |
| **Managed switch** | 802.1Q VLANs, configurable access/trunk ports, restricted management, sufficient ports/uplink capacity, and sufficient PoE for the APs. | Carries separated networks across shared cabling and powers wireless coverage. |
| **Wireless access points** | Wired backhaul, suitable coverage, multiple SSIDs mapped to VLANs, modern Wi-Fi security, restricted management, and compatible PoE. | Extends the same segmentation policy to wireless home, IoT, and guest clients. |
| **Cabling and power** | Suitable Ethernet runs, correctly rated PoE equipment, ventilation, accessible recovery cabling, and reliable power. | Physical installation quality is part of network reliability, not an afterthought. |

Concrete capacities and limitations belong in the [hardware decision record](1_Design_Hardware_Prerequisites.md#part-1--networking-hardware). Essential local services must not require a public cloud connection or the lab to remain operational.

### Why Separate Gateway, Switch, and Access Points

**One shared network does not mean one all-in-one box.** The chosen design separates routing/firewalling, wired switching, and wireless access into purpose-built components, while keeping their configuration and policy coordinated. This is modular hardware within one network, not the [duplicated home-and-lab routing stacks rejected above](#chosen-one-shared-gateway-with-segmentation).

- **Place each component where it works best:** the gateway can sit near the ISP handoff and the switch near wired connections, while APs go where they provide the best coverage. An all-in-one router's convenient cable location is not necessarily a good radio location; separate wired APs avoid that compromise.
- **Scale only what needs expanding:** add or reposition an AP for coverage, expand switch ports or PoE capacity for more devices, or upgrade the gateway for routing throughput. These requirements need not grow together, so one does not force replacement of the others.
- **Replace components independently:** a failed or outdated AP need not mean replacing a working gateway and switch. Troubleshooting and planned upgrades can focus on one role, although gateway or shared-switch outages still affect dependent devices; this is not redundancy.
- **Keep configuration responsibilities clear:** firewall and routing policy live at the gateway, wired VLAN membership at the switch, and SSID-to-VLAN mapping at the APs; see the [layered topology](#network-topology--design). With coordinated management, this makes changes easier to reason about and gives explicit control over ports, coverage, and segment boundaries without adding another router.

For someone comfortable with networking and the [VLAN and port model](#switch-port-assignments), this is the better fit for control, growth, and maintainability in this setup. It is **not automatically easier to configure or more secure**: trunks, SSIDs, firewall rules, and management access still need to agree across devices. The trade-off is more equipment, cabling, power connections, and initial cost than a compact all-in-one.

An all-in-one gateway/switch/AP can be a good choice for a small home with suitable placement and sufficient ports, coverage, and segmentation support. Some also accept external switches and APs, so they are not inherently unexpandable. Here, separate coverage points and independent hardware lifecycles justify the modular setup; see the [gateway hardware alternatives](1_Design_Hardware_Prerequisites.md#router--firewall-cloud-gateway-max) for the concrete comparison.

---

## Network Topology & Design

The layers below describe responsibilities, **not a requirement to buy a separate core and distribution switch**. At home scale one managed switch can combine distribution and access. Lab-internal cluster networking belongs in the [cluster design](6_Design_Cluster.md), not in the household routing policy.

```text
Internet
   |
CORE / EDGE LAYER
   ISP modem / access termination
   (bridge/passthrough preferred where supported)
   |
   One physical home-and-lab gateway
   WAN firewall | VLAN routing | DHCP | DNS forwarding
   Local management, independent of lab compute
   |
   LAN VLAN trunk
   |
DISTRIBUTION LAYER
   Managed switch (also wired access at this scale)
   VLAN membership | restricted trunks | PoE | port profiles
   |
   +----------------------+--------------------------+
   |                      |                          |
ACCESS LAYER
   Wired access ports     PoE AP 1 + PoE AP 2        Lab host trunks
   Home / IoT clients     Wired backhaul             Only needed VLANs
                          Home / IoT / Guest SSIDs   VLAN-aware bridges
   |                      |                          |
LOGICAL SEGMENTS (shared equipment, separate broadcast domains)
   Management: gateway, switch, APs, host management
   Home:       trusted household clients
   Lab:        VMs, cluster nodes, experimental services
   IoT:        constrained devices
   Guest:      internet-only visitors

Inter-segment traffic always crosses the gateway's firewall.
Traffic within one VLAN does not necessarily cross that firewall.
```

### Core / Edge Layer

A router behind the ISP modem gives deliberate control over firewalling, VLANs, DHCP/DNS, and upgrades rather than relying on a provider device's limited LAN functions. A modem and router have different roles; the additional router does not automatically increase speed or security. Performance is bounded by the ISP service, gateway processing, cabling, switch uplinks, and client capabilities.

Prefer bridge/passthrough mode when the ISP supports it and required services still work. The shared gateway then owns routing and the WAN boundary. If the ISP device must remain a router, the shared gateway can sit downstream with **double NAT for IPv4**. Document that limitation: inbound VPNs, port forwarding, gaming, and IPv6 prefix delegation may need extra work or may be constrained by ISP carrier-grade NAT. Do not assume a modem's "DMZ" setting removes NAT.

Home and lab clients belong behind the shared gateway, not partly on the modem's Wi-Fi/LAN and partly behind the gateway. Disable redundant ISP Wi-Fi/DHCP only as appropriate to the selected modem mode and after validating provider services. Never make an unplanned household-wide change just to start a lab.

### Distribution and Access Layers

The switch carries the gateway trunk and connects APs, wired household clients, and hypervisor hosts. Access ports present one VLAN untagged to ordinary devices. Trunks carry only the VLANs required by an AP or host; a lab host does not need the home or guest VLAN simply because the switch carries them.

Map wireless SSIDs to the same logical segments as wired devices. Use wired AP backhaul rather than making wireless mesh a default dependency; place APs for coverage and validate roaming/channel use in the actual building. AP management belongs to the management segment, not to the guest or IoT SSID.

### Why Wired Access Points Instead of a Mesh System

**The requirement is reliable, segmented Wi-Fi coverage, not mesh itself.** Multiple wired APs can provide coverage and client roaming under the same SSIDs without a wireless mesh uplink. Roaming still depends on client behavior, placement, and radio settings; neither mesh branding nor multiple APs guarantees seamless handover.

- **Wired backhaul is more predictable:** each AP reaches the switch over Ethernet instead of relying on a radio link through walls or interference. Wireless backhaul consumes airtime and can contend with clients, especially when they share a radio/channel; dedicated backhaul radios reduce that contention but do not remove the wireless dependency.
- **Segmentation must extend to Wi-Fi:** coverage alone is not enough. APs must map Home, IoT, and Guest SSIDs to the [chosen VLANs](#subnet--vlan-design), keep management restricted, and leave routing to the shared gateway. A mesh system's guest network does not by itself prove support for that policy.
- **Avoid a second routing or management stack:** another system in router mode could add NAT and its own DHCP/firewall configuration. Bridge/AP mode can avoid this, but its VLAN capabilities must still be verified. The selected design needs access points, not another gateway.

Mesh is useful when Ethernet runs are impractical. Some mesh systems also support wired backhaul and suitable VLAN controls; those are not inherently unsuitable, but offer no needed advantage here over wired APs. The accepted trade-off is installing Ethernet and PoE to the coverage points in exchange for predictable uplinks and one consistent segmentation policy. See [Wi-Fi Access Points](1_Design_Hardware_Prerequisites.md#wi-fi-access-points) for the actual equipment and product alternatives.

---

## Subnet & VLAN Design

The table below documents the **chosen segmentation of this setup using example values only**. Management, Lab, IoT, Home, and Guest are the intended segment roles; VLAN IDs such as `10` and `40`, subnets such as `10.42.10.0/24`, and gateway addresses shown later are illustrative, not confirmed live values. Keep the actual VLAN/subnet mapping and client inventory privately, following [Security and Public Repository](../0_Security_and_Public_Repository.md#information-that-is-usually-safe-to-document). VLANs can be created as needed, but do not connect lab, IoT, or guest devices to a trusted flat LAN as a shortcut.

| Segment | Example VLAN | Example IPv4 subnet | Purpose |
|---|---|---|---|
| Management | 10 | 10.42.10.0/24 | Gateway, switch, APs, hypervisor management, approved administrators |
| Lab services | 20 | 10.42.20.0/24 | Cluster nodes, VMs, applications, experimental workloads |
| IoT | 30 | 10.42.30.0/24 | Smart devices and constrained clients |
| Home | 40 | 10.42.40.0/24 | Trusted household wired and wireless clients |
| Guest | 50 | 10.42.50.0/24 | Visitor internet access; no internal access |

### IPv4 Addressing

Use one distinct subnet per VLAN; `/24` is ample for each segment at this scale. Reserve infrastructure addresses and use DHCP for ordinary clients. For example, the gateway in management could use `10.42.10.1`, with privately documented reservations for infrastructure devices.

The earlier `10.42.0.0/20` aggregate **does not contain** `10.42.20.0/24` or the later segments above. This design lists the actual per-VLAN example subnets instead of claiming they fit that aggregate. Check overlap with ISP LAN addressing, VPN routes, container networks, and pod/service CIDRs before using them. The number `42` is memorable, not collision-proof; some cluster networking defaults also use `10.42.x.x`.

### IPv6 Design and Rollout

Dual-stack is useful for learning, but it must not introduce untested household connectivity or bypass IPv4 firewall policy. **Enable production IPv6 only after verifying ISP/gateway support and equivalent IPv6 isolation.** Until then, an IPv4 baseline is acceptable; record IPv6 as pending rather than claiming working dual-stack.

- Prefer an ISP-delegated prefix with enough space for one `/64` per enabled VLAN. Check whether the upstream device delegates it to the shared gateway and how renumbering behaves.
- Global IPv6 addresses do not mean unsolicited inbound access is allowed: enforce stateful WAN and inter-VLAN policy explicitly. NAT is not the security boundary in either address family.
- ULA can provide local-only addressing, but does not itself provide internet access. If used, generate a proper locally assigned `/48` prefix and derive one `/64` per VLAN from it; keep published examples in `2001:db8::/32`, never publish real global prefixes.
- Do not carry the previous ULA + NAT66 assumption into this setup. Verify supported capabilities before considering translation; lack of usable delegation is not a reason to maintain a custom router stack.
- Test DHCP, DNS, Router Advertisements, and permitted/denied flows in both families. Block unintended IPv6 routing/advertisements where IPv6 is not deliberately enabled.

### Switch Port Assignments

This is a role-based example; final port numbering and native-management settings belong in the verified setup record.

| Connected role | Untagged / native network | Tagged VLANs | Intent |
|---|---|---|---|
| Gateway LAN uplink | Explicitly selected native network, or none where supported | All required routed segments | Trunk between gateway and switch; settings agree at both ends |
| AP uplink, each | Management if used untagged for AP adoption/management | Home, IoT, Guest | Power plus VLAN-tagged SSIDs; no Lab segment unless needed |
| Hypervisor uplink, each | Management if used untagged, otherwise none where supported | Lab; additional experimental segments only when justified | Host administration plus VLAN-aware VM connectivity |
| Ordinary home client | Home | None | Access port; client need not understand tags |
| Wired IoT client | IoT | None | Constrained access port |
| Spare / recovery port | Explicitly assigned only for controlled recovery | None | Disable unused ports; keep a documented local recovery method |

**Tagged** means an 802.1Q tag identifies the VLAN on that link; **untagged** means the port's configured VLAN classifies the frame. Native VLANs must match across a link. Management may be tagged or untagged depending on supported adoption/recovery behavior; neither "VLAN 1 must exist everywhere" nor "an unused VLAN always gives recovery access" is a design guarantee. Test recovery before restricting management.

For explanation, see the DevHub [Tagged vs Untagged reference](https://github.com/CollinPoetoehena/DevHub/blob/main/reference/network/Network_Devices.md#tagged-vs-untagged-8021q-vlan-tagging). Limit VLAN membership and configuration access; trunking every VLAN to every device defeats least privilege.

---

## Firewall and Access Policy

Default-deny **new inter-VLAN connections**, then allow only specific source/destination/service combinations. Permit return traffic for approved stateful connections. Apply equivalent policy for IPv4 and IPv6, including traffic to the gateway's own services, not just forwarded traffic.

| Source | Destination | Policy intent |
|---|---|---|
| Approved administrator | Management interfaces | Allow only required management services; ordinary Home clients are not administrators by default |
| Home | Selected lab application | Allow only explicitly selected endpoints/ports; deny broad Lab and Management access |
| Lab | Home / Management | Deny new connections except documented necessities |
| IoT | Home / Lab / Management | Deny by default; allow only a specific service endpoint if genuinely needed |
| Guest | Internal segments / device administration | Deny; permit only required gateway DHCP/DNS and internet access |
| Each segment | Gateway DHCP/DNS | Allow only its required infrastructure services |
| Internal clients | Internet | Permit according to segment needs; no unsolicited WAN access to internal services |

NAT is not inter-VLAN isolation. Hosts in the same VLAN can communicate without traversing the routed firewall; use host firewalls or supported client isolation where needed. Guest client isolation is separate from blocking guests from other VLANs. Service discovery across VLANs is not automatically enabled: allow narrowly scoped discovery only when needed, instead of broadly opening IoT-to-Home traffic.

### Management Access and Optional Jumphost

Use approved administrative clients with narrowly scoped access to gateway, switch, AP, and hypervisor management. Restrict administrative accounts, protect credentials, and keep WAN management disabled. Maintain a direct local recovery path that does not require a running lab VM or cloud login.

The gateway is **not an application server or SSH jumphost**. If an SSH bastion is useful for lab access, place it in a dedicated lab/management VM with explicit firewall permissions. Its failure may interrupt lab administration but must not interrupt household connectivity or the local gateway recovery path. Remote VPN access is a future decision; its implementation choice belongs in [Software Prerequisites](2_Design_Software_Prerequisites.md#router--firewall-software).

---

## Maintenance, Recovery, and Safe Experiments

**Minimal maintenance is the goal, not zero responsibility.** Sharing infrastructure for everything in the home network (including lab network) reduces hardware cost and administrative work, while household routing still needs updates, security review, and backups. Keep its configuration small and predictable.

- Document GUI settings and intent: VLANs/subnets, SSID mapping, port profiles, allowed flows, and recovery steps. A concise checklist plus private configuration backups is repeatable even when the network is not fully IaC-managed.
- Store exports, credentials, recovery codes, and identifying endpoints privately; sanitize public documentation under the [security guide](../0_Security_and_Public_Repository.md).
- Schedule disruptive changes, review firmware release notes, back up before changes, and know how to recover locally from a mistaken management/VLAN setting.
- Verify allowed **and denied** paths from each segment, wireless and wired mapping, guest isolation, and IPv6 behavior where enabled. Confirm home internet, DHCP, DNS, and Wi-Fi still work with all lab compute powered off.
- Keep router-OS, DHCP, firewall, and bridging experiments inside isolated virtual networks. Do not bridge experimental DHCP servers or IPv6 advertisements onto live household segments.
- Expect shared bandwidth and shared failure domains. If a future requirement demands physical independence, revisit separate hardware deliberately rather than assuming VLANs supply it.

These records make the home network easier to understand and rebuild, while keeping the lab a learning environment rather than the household's critical service platform.

### Redundancy: Enterprise Requirements vs. Household Trade-offs

**Enterprises need redundancy where outages would breach availability commitments or cause unacceptable business impact.** The aim is to keep services running through component failure or planned maintenance, rather than waiting for replacement equipment. The required level follows the service's availability target; not every enterprise network needs every high-availability feature.

| Layer | Typical enterprise redundancy | What it protects against |
|---|---|---|
| Internet access | Multiple ISP connections with independent access equipment and, where possible, diverse physical paths | Failure of one provider, modem, or access circuit |
| Gateway / firewall | A supported high-availability pair with health checks, configuration synchronization, and state synchronization where supported | Gateway failure or maintenance, with tested failover |
| Switching and links | Redundant switches and uplinks, with supported loop prevention or multi-chassis link aggregation and dual-connected critical hosts | Switch, port, or cable failure without creating network loops |
| Wireless access | Overlapping AP coverage and resilient management where required | Loss of an AP while retaining sufficient coverage and capacity |
| Power | UPS protection and, where justified, separate power feeds and redundant supplies | Short power interruptions or failure of one power path |

Redundancy is **more than buying two boxes**: failover must be supported, configured, monitored, and tested, and the surviving path must carry the required load. Shared power, cabling, upstream equipment, or configuration mistakes can still defeat both paths. Backups help restore configuration but do not keep traffic flowing during an outage.

**This household deliberately accepts downtime instead of paying for enterprise-style availability.** A failed gateway or shared switch can interrupt the network until a replacement arrives and its configuration is restored. That is inconvenient, but not catastrophic for this simple household: there are no enterprise uptime commitments or business-critical services that justify duplicate gateways, switches, independent internet subscriptions, and their additional maintenance. Ideally, redundancy would reduce interruptions; for the [personal goals](0_Design_Goals.md), its cost and operational complexity outweigh that benefit. The two APs serve coverage needs, not a guaranteed redundant Wi-Fi design.

For essential internet access during an outage, use a **mobile hotspot or a travel router with a supported mobile uplink** temporarily, subject to signal, data allowance, and device compatibility. This can keep selected household clients online; it does not restore the lab, wired LAN, normal VLAN policy, or all local services. Keep it a limited fallback, not an unplanned bridge that bypasses the [segmentation and firewall policy](#firewall-and-access-policy).

The **ISP modem and single ISP connection remain single points of failure** even if the internal gateway and switch were duplicated. Removing that dependency requires genuinely independent upstream connectivity; two internal routers alone do not provide end-to-end redundancy. The chosen approach is therefore [documented recovery and private backups](#maintenance-recovery-and-safe-experiments), replacement of the failed component, and temporary mobile access when needed. Revisit redundancy if prolonged outages become unacceptable or the household's requirements change.

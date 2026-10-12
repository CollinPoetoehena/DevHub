# Design: Network

> **Scope of this document: see [README.md/Documents Setup & Scope](README.md#documents-setup--scope); in short: design only — no specific hardware or software.** Concrete devices, prices, and platforms are recorded in [Hardware Prerequisites](1_Design_Hardware_Prerequisites.md#part-1--networking-hardware) and [Software Prerequisites](2_Design_Software_Prerequisites.md#router--firewall-software).

A stable network is the foundation of both household connectivity and a reliable homelab. The chosen design is **one shared physical network infrastructure, with one gateway behind the ISP modem and separate logical segments for home and lab**. There is no additional downstream lab router. Shared infrastructure does not mean a flat LAN: VLANs separate broadcast domains, and firewall policy controls traffic between them.

This is also documentation for the **home network itself**: it records the topology, boundaries, addressing intent, and recovery requirements so the setup is understandable, repeatable, and easier to maintain. It describes the target policy, not proof that every setting has already been applied. Actual configuration and verification belong in [Network Setup](../2_Setup/2_Setup_Network.md); private backups and real access details stay outside this public repository under the [security guide](../0_Security_and_Public_Repository.md).

> **Actual design, example values:** this document describes the chosen home-and-lab network setup, not a hypothetical alternative. Published VLAN IDs, subnets, IP addresses, and other configuration values are illustrative examples, not a record of live settings. The topology, segment roles, and policy intent describe the chosen design; keep the mapping to actual configured values in private operational records. Follow [Security and Public Repository](../0_Security_and_Public_Repository.md#information-that-is-usually-safe-to-document) when documenting those details: private ranges and VLAN IDs are not secrets by themselves, but examples must be clearly labeled and must not expose real access details or identifying information.

See the [Network Reference](../../../reference/network/README.md) for networking concepts and troubleshooting, and [Personal Goals](0_Design_Goals.md) for the low-maintenance boundary between household infrastructure and disposable experiments.

## Table of Contents

- [Network Setup Options](#network-setup-options)
  - [Chosen: One Shared Gateway with Segmentation](#chosen-one-shared-gateway-with-segmentation)
- [Required Building Blocks (Design Level)](#required-building-blocks-design-level)
- [Network Topology & Design](#network-topology--design)
  - [Core / Edge Layer](#core--edge-layer)
  - [Distribution and Access Layers](#distribution-and-access-layers)
- [Subnet & VLAN Design](#subnet--vlan-design)
  - [IPv4 Addressing](#ipv4-addressing)
  - [IPv6 Design and Rollout](#ipv6-design-and-rollout)
  - [Switch Port Assignments](#switch-port-assignments)
- [Firewall and Access Policy](#firewall-and-access-policy)
  - [Management Access and Optional Jumphost](#management-access-and-optional-jumphost)
- [Maintenance, Recovery, and Safe Experiments](#maintenance-recovery-and-safe-experiments)

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

For explanation, see [Tagged vs Untagged](../../../reference/network/Network_Devices.md#tagged-vs-untagged-8021q-vlan-tagging). Limit VLAN membership and configuration access; trunking every VLAN to every device defeats least privilege.

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

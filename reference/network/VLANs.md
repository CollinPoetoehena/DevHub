# VLANs and Tagged Ethernet

A **Virtual LAN (VLAN)** separates Layer 2 broadcast domains on shared switching infrastructure. Endpoints in the same VLAN can communicate directly when forwarding and endpoint policy allow it; communication between VLANs normally requires Layer 3 routing. VLAN membership is not a substitute for firewall policy, and shared switches still share hardware, power and administrative failure domains.

Use [Network Design](./Network_Design.md#segmentation-and-access) to decide which trust boundaries are needed. This page explains the Ethernet mechanism; [Network Modes](./Network_Modes.md) explains guest/container attachment and overlays.

---

## Table of Contents

- [Why Use VLANs](#why-use-vlans)
- [IDs, Subnets and Membership](#ids-subnets-and-membership)
- [Tagged and Untagged Links](#tagged-and-untagged-links)
- [How a Frame Travels](#how-a-frame-travels)
- [Routing and Policy](#routing-and-policy)
- [VLANs Versus Overlays](#vlans-versus-overlays)
- [Verification and Maintenance](#verification-and-maintenance)
- [Official References](#official-references)

---

## Why Use VLANs

| Approach | Benefits | Drawbacks / responsibilities | Typical use |
|---|---|---|---|
| One shared VLAN | Simple addressing and switching; fewer membership settings | Broad peer reachability and a shared broadcast domain. Maintain endpoint protection and do not assume a gateway sees local traffic | Endpoints with compatible trust and connectivity needs |
| Multiple VLANs on shared infrastructure | Separate broadcast domains without a physical switch per role; explicit inter-VLAN routing/policy points | Requires VLAN-aware paths and correct membership. Maintain port maps, allowed trunks, routing, DHCP/RA ownership and policy; configuration mistakes can breach boundaries or remove management access | Different trust roles sharing switches, APs or hypervisors |
| Separate physical networks | Can separate cabling, bandwidth or selected hardware failure domains | More equipment, power and operations; gateways or multi-homed hosts can still reconnect them. Maintain each network and verify remaining shared dependencies | A physical boundary is justified rather than only logical separation |

---

## IDs, Subnets and Membership

- **VLAN ID (VID):** the 12-bit identifier in an 802.1Q tag. Ordinary configurable IDs are 1-4094; 0 is used for priority-tagged frames and 4095 is reserved. A product may reserve additional IDs.
- **Subnet:** a Layer 3 address range, not a VLAN. One subnet per VLAN per IP family is a common design, not a requirement imposed by Ethernet. A VLAN ID does not need to match an IP-address octet.
- **PVID (Port VLAN ID):** the VLAN used to classify incoming untagged or priority-tagged frames when that traffic is accepted. Ingress admission and membership controls are separate settings.
- **Tagged/untagged egress membership:** whether frames for a VLAN leave a particular port with or without a VLAN tag. Do not infer ingress classification solely from an egress checkbox.
- **Native VLAN:** commonly the VLAN carried untagged on a trunk. Some platforms can tag it or reject untagged traffic entirely; defaults and terminology vary.

VLAN 1 is a common factory default, not a universal native VLAN or a special security boundary. IDs are meaningful within the connected switching domain: configuring the same number on disconnected switches does not connect them.

---

## Tagged and Untagged Links

An 802.1Q tag adds four bytes to an [Ethernet frame](./Network_Models_and_Packets.md#anatomy-of-a-frame-layer-2), including the VLAN ID and priority information. It is neither an IP header nor encryption.

| Link role | On-wire behavior | Responsibility |
|---|---|---|
| Access port | Conventionally one endpoint VLAN carried untagged; the switch classifies incoming traffic into that VLAN | Configure ingress admission, PVID and egress membership together; reject unintended tagged membership |
| Trunk | Carries selected tagged VLANs and, optionally, an explicitly agreed untagged/native VLAN | Both ends must agree on allowed VLANs and untagged handling; permit only required networks |
| VLAN-aware endpoint | Router subinterfaces, AP mappings or hypervisor switching interpret tags | Preserve the intended mapping end-to-end and expose only required memberships to clients/guests |

Access and trunk describe common configurations, not two different cable types. Some products use hybrid/general-port terminology. Ordinary endpoints need not understand tags when their switch port supplies untagged access.

```text
Endpoint A -- untagged -- access port [VLAN A]
                                  |
                               switch 1
                                  |
                       trunk: tagged VLAN A + VLAN B
                                  |
                               switch 2
                                  +-- access port [VLAN A] -- untagged -- Endpoint B
                                  +-- access port [VLAN B] -- untagged -- Endpoint C
```

The letters are synthetic roles, not literal configurable IDs. A and B can share a Layer 2 domain across the trunk; C is in another domain. The diagram does not grant routed access between them.

---

## How a Frame Travels

1. **Ingress admission:** the switch checks whether the arriving traffic is acceptable. An untagged frame is assigned to the ingress PVID; a tagged frame identifies its VLAN, subject to membership/filtering.
2. **Learning and forwarding:** the switch learns the source MAC in that VLAN's forwarding context and looks up the destination there. Broadcasts and unknown destinations may be flooded only to eligible ports in that domain.
3. **Egress membership:** eligible output ports transmit the frame tagged or untagged according to their VLAN configuration.

With a **native/PVID mismatch**, one end's untagged traffic can be classified into a different VLAN at the other end. The link may appear healthy while isolation or reachability is wrong. There is no universally safer rule that management must be untagged: choose its membership explicitly and retain a recovery path.

---

## Routing and Policy

```text
VLAN A -- router interface A -- routing + firewall -- router interface B -- VLAN B

Same-VLAN peer traffic: endpoint -- switch/bridge -- endpoint
                                  (may bypass the routed firewall)
```

Routing can happen on a gateway, Layer 3 switch or virtual router. Locate policy where the traffic actually passes; a perimeter firewall cannot inspect a path that bypasses it. Protect traffic to the routing device's administration separately from traffic through it.

Different subnets placed on one unsegmented Ethernet network do not provide VLAN isolation. Conversely, placing endpoints in separate VLANs does not guarantee safe inter-VLAN policy. DHCP, IPv6 Router Advertisements, DNS and any relays must have deliberate ownership; a VLAN change alone does not configure those services.

---

## VLANs Versus Overlays

A VLAN tag classifies frames on VLAN-aware Ethernet links. An overlay such as VXLAN encapsulates workload traffic between tunnel endpoints over an IP underlay. They can be combined: the underlay may use VLANs, and an endpoint may map a local VLAN into an overlay segment.

A VXLAN network identifier (VNI) has 24 bits, unlike the VLAN ID's 12 bits. A VNI is not an extended VLAN tag that ordinary Ethernet switches automatically understand, and its number need not match a local VLAN ID. See [Overlay and Underlay Networks](./Network_Modes.md#overlay-and-underlay-networks) for packet flow, benefits, costs and verification.

---

## Verification and Maintenance

- Record ingress PVID/admission, tagged/untagged egress, permitted trunk VLANs and the management path at both ends of each link.
- Verify VLAN filtering on software bridges; a VLAN-aware design on paper does not enable filtering on a host.
- Test authorized same-VLAN connectivity and intended inter-VLAN denials using known-working services, in every enabled IP family. A failed ping alone is not proof of isolation.
- Check DHCP/RA sources and address assignment after moving a port, guest or SSID. Do not let an experimental network service inherit household membership.
- Inspect forwarding tables, VLAN membership and packet captures with the [host-networking tools](./commands/host_networking.md). NIC offloads can change how tags appear in a host capture; corroborate with device configuration and an appropriate capture point.
- Preserve a console or known-good wired recovery path before changing management membership. Back up settings and recheck after firmware, cabling, AP or hypervisor changes.

---

## Official References

- [IEEE 802.1 Working Group](https://1.ieee802.org/) is the standards entry point for IEEE 802.1Q bridges and bridged networks.
- [Linux Ethernet bridging](https://docs.kernel.org/networking/bridge.html) documents VLAN filtering and bridge controls.
- Use the exact switch, AP and hypervisor's official documentation for port terminology, defaults, reserved IDs and supported tagging behavior.

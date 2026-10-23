# Network Reference

This reference covers general networking theory, architecture and a deliberately useful command toolkit, following DevHub's [scope and tool-specificity design](../README.md#scope-and-tool-specificity). Network fundamentals are easier to understand and verify when paired with practical diagnostics. Tools such as `ip`, `ss`, `dig`, `tcpdump`, `tshark`, Wireshark and `iperf3` are included because they are used frequently to inspect real interfaces, name resolution, packet flows and performance—not to document every possible networking product or vendor configuration. The command guides emphasize portable diagnostic techniques and explain tool-specific syntax where it makes those fundamentals actionable.

The [network design reference](./Network_Design.md) explains reusable principles such as layered responsibilities, segmentation, trust zones, and permitted traffic flows. For an example applying these principles to household and lab needs, see the [public homelab network chapter](https://github.com/CollinPoetoehena/devhub-homelab/blob/main/docs/02-architecture/network.md). DevHub owns the general explanation; the homelab guide owns its home-scale examples and trade-offs rather than duplicating the theory. Use the relevant vendor's official documentation for current product-specific behavior and configuration. See the [repository relationship](https://github.com/CollinPoetoehena/devhub-homelab/blob/main/README.md#how-devhub-and-the-homelab-repositories-fit-together) for the full division of responsibilities.

---

## Table of Contents

- [Concepts](#concepts)
- [Commands](#commands)

---

## Concepts

- [Network Design](./Network_Design.md) — General architecture, layered responsibilities, segmentation and access, addressing decisions, trust-zone models including Upper/Lower Red, traffic flows, and policy verification.
- [Network Modes and Virtual Connectivity](./Network_Modes.md) — VM/container attachment modes, overlay versus underlay, VXLAN packet flow, MTU overhead and native-routing trade-offs, with text diagrams and verification guidance.
- [VLANs and Tagged Ethernet](./VLANs.md) — Broadcast domains, VLAN IDs versus subnets/VNIs, PVID/native membership, access/trunk links, frame forwarding, routing policy and verification.
- [Network Models & Packets](Network_Models_and_Packets.md) — OSI model (7 layers), TCP/IP model (4 layers), encapsulation, and detailed anatomy of frames, packets, and segments with examples of how data flows from application to wire.
- [Network Devices & Interfaces](Network_Devices.md) — ISP modem/gateway, routers, switches and network interfaces, with links to the dedicated VLAN guide. Covers what each device does, how NAT and IPv6 work at the modem level, double NAT, routing tables, and firewalls.
- [Subnets & IP Addresses](Subnets_and_IP_Addresses.md) — Subnets, CIDR notation, IPv4 (private ranges, address exhaustion), NAT in detail (types, connection tracking, step-by-step packet flow), IPv6 (format, address types, SLAAC, DHCPv6, privacy extensions, dual-stack), and how all of this applies to the homelab.
- [DHCP & DNS](DHCP_and_DNS.md) — How DHCP assigns network configuration (DORA handshake, leases, reservations, conflicts) and how DNS resolves hostnames (resolution chain, record types, forwarding, local DNS).

---

## Commands

- [Network Commands](commands/README.md) — All networking commands with detailed output explanations, organized by topic, such as host networking, DNS, etc.

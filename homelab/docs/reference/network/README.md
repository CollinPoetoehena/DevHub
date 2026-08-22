# Network Reference

Background knowledge and command reference for networking. These documents explain the concepts and commands used throughout the homelab documentation, avoiding repetition in setup and operational docs.

## Concepts

- [Network Models & Packets](Network_Models_and_Packets.md) — OSI model (7 layers), TCP/IP model (4 layers), encapsulation, and detailed anatomy of frames, packets, and segments with examples of how data flows from application to wire.
- [Network Devices & Interfaces](Network_Devices.md) — ISP modem/gateway, routers, switches, VLANs (tagged vs untagged), and network interfaces. Covers what each device does, how NAT and IPv6 work at the modem level, double NAT, routing tables, and firewalls.
- [Subnets & IP Addresses](Subnets_and_IP_Addresses.md) — Subnets, CIDR notation, IPv4 (private ranges, address exhaustion), NAT in detail (types, connection tracking, step-by-step packet flow), IPv6 (format, address types, SLAAC, DHCPv6, privacy extensions, dual-stack), and how all of this applies to the homelab.
- [DHCP & DNS](DHCP_and_DNS.md) — How DHCP assigns network configuration (DORA handshake, leases, reservations, conflicts) and how DNS resolves hostnames (resolution chain, record types, forwarding, local DNS).

## Commands

- [Network Commands](Network_Commands.md) — All networking commands with detailed output explanations: `nmcli`, `ip a`, `ip r`, `ping`, `ip neigh`/`arp`, `ss`, `dig`/`nslookup`, DHCP client commands, and `tcpdump`.

## Other References

- [dnsmasq](dnsmasq.md) — Configuration and commands for the dnsmasq DHCP/DNS server running on the lab router.
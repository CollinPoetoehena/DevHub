# Network Devices & Interfaces

Background information on the physical and virtual network components: ISP modem/gateway, routers, switches, and network interfaces.

---

## Table of Contents

- [ISP Modem / Gateway](#isp-modem--gateway)
- [Router](#router)
- [Switch](#switch)
- [VLAN (Virtual LAN)](#vlan-virtual-lan)
- [Network Interface](#network-interface)

---

### ISP Modem / Gateway

Modem is short for *modulator-demodulator*. It converts digital signals from your devices into analog signals for transmission over telephone or cable lines, and vice versa. The device provided by your ISP (e.g. a KPN Experia Box) that connects your home to the internet. It is the bridge between your private home network and the public internet: one side faces the ISP (WAN — your public IP address, assigned by the ISP), the other side faces your home devices (LAN — private addresses such as `192.168.2.x`).

**What it does:**

- **NAT (Network Address Translation) — IPv4:** Your ISP gives you one public IPv4 address, but many devices in your home need internet access simultaneously. NAT lets the modem/router track outgoing connections and rewrite packet headers so all home devices share that single public IP. Incoming replies are translated back to the correct internal device. From the internet's perspective, all traffic from your home appears to come from one address. See [IP Addresses — IPv4 and IPv6](Subnets_and_IP_Addresses.md#ip-addresses--ipv4-and-ipv6) for a detailed explanation of how NAT works, its types, and its limitations.
- **IPv6 — no NAT needed:** With IPv6, the ISP assigns your modem a *prefix* (a block of addresses, e.g. a `/56` or `/48`) instead of a single address. The modem delegates sub-prefixes to the LAN side, and every device generates its own globally unique, internet-routable IPv6 address via SLAAC (Stateless Address Autoconfiguration) or DHCPv6. There is no address translation — each device's IPv6 address is the real address used end-to-end. **Security is provided by the modem's firewall, not by NAT:** the modem's stateful firewall still blocks unsolicited inbound IPv6 traffic by default, the same way it does for IPv4. The difference is that your devices' IPv6 addresses are *real public addresses* — if the firewall were turned off, they would be directly reachable from anywhere on the internet. See [IP Addresses — IPv4 and IPv6](Subnets_and_IP_Addresses.md#ip-addresses--ipv4-and-ipv6) for the full IPv6 explanation.
- **DHCP server:** Automatically assigns IPv4 addresses, subnet masks, default gateway, and DNS server addresses to devices that join the home network. (For IPv6, address assignment is typically handled by SLAAC via Router Advertisements, though DHCPv6 may also be used.)
- **DNS forwarding:** Passes DNS queries from home devices to the ISP's DNS servers (or a configured upstream resolver).
- **Firewall:** Blocks unsolicited inbound traffic from the internet by default — only traffic that was initiated from inside is allowed back in. This applies to both IPv4 and IPv6. For IPv4, NAT provides an additional (accidental) layer of protection because private IPs are not routable. For IPv6, the firewall is the *only* protection — there is no NAT hiding devices. This makes the firewall critically important for IPv6.
- **WiFi access point** (on combined units): Provides wireless connectivity for home devices.
- **Admin interface:** Accessible via a browser at its LAN IP (typically `192.168.2.1` or `192.168.1.1`). Used to view connected devices, DHCP leases, port forwarding rules, and static IP reservations.

**Double NAT (IPv4 only):** If you place a second router (e.g. a Raspberry Pi) behind the ISP modem, you create a *double NAT* situation — the ISP modem NATs to the Pi's WAN IP, and the Pi NATs again to lab devices. This is fine for outbound internet access but complicates inbound connections (e.g. accessing lab services from outside). For the homelab, double NAT is an acceptable trade-off for full isolation. Note that double NAT is an IPv4 concept — with IPv6 there is no NAT at all, so the Pi router would simply route IPv6 traffic (if IPv6 forwarding is enabled) and rely on firewall rules for security.

### Router

A router connects two or more networks and directs traffic between them. It has:

- A **WAN port** — faces the internet or an upstream network
- One or more **LAN ports** — face your local devices
- Its own **DHCP server** — assigns IPs to devices on the LAN side
- **NAT** — allows LAN devices to share the single WAN IP for internet access
- **Firewall rules** — control what traffic is allowed to pass between networks

A router creates a new, separate subnet. LAN devices get private IPs from the router's DHCP server; the router's WAN port gets an IP from the upstream network (via DHCP or static). Traffic between the LAN and WAN is routed (and NATed) by the router.

**Routing table:** The router maintains a routing table that maps destination networks to an outgoing interface or next-hop gateway. When a packet arrives, the router selects the most specific matching route and forwards the packet. The default route (`0.0.0.0/0`) catches all traffic that does not match a more specific entry and sends it upstream toward the internet.

**Firewall:** Routers use stateful firewall rules to decide which traffic is allowed. Typical default behaviour: all outbound traffic is allowed, all unsolicited inbound traffic from the WAN is blocked, and established/related return traffic is automatically permitted.

**Why this matters for the homelab:** Placing a dedicated router between the ISP modem and all lab devices creates a separate subnet. Lab mistakes — DHCP conflicts, Proxmox bridge misconfiguration, Kubernetes networking experiments — are contained within the lab subnet and never affect home devices.

### Switch

A switch connects multiple devices within the same network. It does not create a new network, does not run DHCP, provides no firewall, and does no routing. Think of it as a power strip for Ethernet: it gives you more ports, but everything plugged in is on the same network.

| Device | Creates new network | DHCP | Firewall | Isolation |
|--------|---------------------|------|----------|-----------|
| Switch | No                  | No   | No       | No        |
| Router | Yes                 | Yes  | Yes      | Yes       |

### VLAN (Virtual LAN)

A VLAN is a way to split one physical switch into multiple isolated logical networks. Devices in the same VLAN can communicate directly (layer 2); devices in different VLANs cannot reach each other without going through a router (layer 3). VLANs are defined by the IEEE 802.1Q standard.

**Why use VLANs:**
- **Isolation:** Separate traffic types (management, monitoring, workloads) so a misconfiguration or compromise in one VLAN doesn't affect the others.
- **Security:** The router between VLANs can enforce firewall rules — e.g. workload VMs cannot reach management interfaces.
- **Efficiency:** You don't need a separate physical switch for each network — one managed switch handles all VLANs on the same hardware.

**Key concepts:**
- **VLAN ID:** A number (1–4094) that identifies the VLAN. VLAN 1 is the default/native VLAN on most switches.
- **PVID (Port VLAN ID):** The VLAN assigned to untagged frames arriving on a port. Typically set to 1 (default).
- **Native VLAN:** The VLAN carried untagged on a trunk port. Usually VLAN 1.
- **Trunk port:** A port that carries multiple VLANs (combination of tagged and untagged traffic).
- **Access port:** A port that carries only one VLAN (all traffic untagged).

#### Tagged vs Untagged (802.1Q VLAN Tagging)

A single physical Ethernet cable can carry traffic for multiple VLANs. The switch needs to know how to handle frames for each VLAN on each port — that's where "tagged" and "untagged" come in:

- **Untagged (access):** The switch strips/adds the VLAN tag transparently. The device on the other end sees plain Ethernet frames — it has no idea VLANs exist. Used for devices that don't support VLANs or for the "default" network on a port. Each port can be untagged for **only one** VLAN (its PVID).

- **Tagged (trunk):** The switch preserves the 802.1Q VLAN tag in the Ethernet frame header (a 4-byte field containing the VLAN ID). The device on the other end **must** understand VLAN tags and use them to separate traffic into the correct virtual network (e.g. via sub-interfaces on Linux, or VLAN-aware bridges in Proxmox). A port can be tagged for **multiple** VLANs simultaneously.

**How a frame travels through the switch:**
1. A frame arrives on a port. If it has no VLAN tag, the switch assigns it to the port's PVID (e.g. VLAN 1).
2. The switch looks up the destination MAC in its forwarding table and determines which port(s) to send the frame out on.
3. On the egress port: if that VLAN is configured as **untagged**, the switch strips the tag before sending. If **tagged**, it keeps the tag in the frame.

**Analogy:** Think of a tagged port as a multi-lane highway with lane markers (each lane is a VLAN). An untagged port is a single-lane road with no markers — traffic just flows without any labelling.

**When to use tagged vs untagged:**
- Use **untagged** for devices that don't understand VLANs (printers, laptops, simple servers) or for the management/default network that should always be reachable even if VLAN config breaks.
- Use **tagged** when a device needs to participate in multiple VLANs simultaneously (e.g. a router with sub-interfaces, or a hypervisor running VMs in different VLANs).

### Network Interface

A network interface is the point of connection between a device and a network. Each interface is a distinct channel through which the device sends and receives network traffic.

- **Physical interface** — a real hardware port: a built-in Ethernet port (e.g. `eth0` on the router), a USB-to-Ethernet adapter (e.g. `eth1`), or a WiFi card (`wlan0`). Each has a unique MAC address burned into the hardware.
- **Virtual interface** — a software-only interface created by the OS: `lo` (loopback, always `127.0.0.1`, never leaves the machine), bridge interfaces (e.g. Proxmox's `vmbr0`), VLAN sub-interfaces (e.g. `eth1.10`), and tunnel interfaces.

Each interface has:
- A **name** assigned by the OS (`eth0`, `eth1`, `lo`, `wlan0`, …)
- A **MAC address** (OSI model layer 2, unique hardware identifier) — used for delivery within a local network
- An optional **IP address** (OSI model layer 3) — assigned statically or via DHCP; required for routing

A device can have many interfaces, each connecting it to a different network. A router exploits this: it has one interface facing the upstream network (WAN) and at least one facing the local network (LAN), and routes packets between them.

# Network Background & Commands
This document provides background information and commands with detailed explanation for networking. This provides a reference for networking concepts and commands that are commonly used in networking and avoid repetition of information in other documents (e.g. installation steps).

---

## Table of Contents

- [Background: Networking Concepts](#background-networking-concepts)
  - [ISP Modem / Gateway](#isp-modem--gateway)
  - [Router](#router)
  - [Switch](#switch)
  - [Network Interface](#network-interface)
  - [Subnet](#subnet)
  - [DHCP](#dhcp)
  - [DNS](#dns)
- [Commands: Networking](#commands-networking)
  - [nmcli connection show](#nmcli-connection-show)
  - [ip a](#ip-a-or-ip-addr-or-ip-address)
  - [ip r](#ip-r)
  - [ping](#ping)
  - [ip neigh / arp — ARP Neighbour Table](#ip-neigh--arp--arp-neighbour-table)
  - [ss — Socket Statistics](#ss--socket-statistics)
  - [dig / nslookup — DNS Lookup](#dig--nslookup--dns-lookup)
  - [DHCP Client Commands](#dhcp-client-commands)
  - [tcpdump — Packet Capture](#tcpdump--packet-capture)

---

## Background: Networking Concepts

### ISP Modem / Gateway

The device provided by your ISP (e.g. a KPN Experia Box) that connects your home to the internet. It is the bridge between your private home network and the public internet: one side faces the ISP (WAN — your public IP address, assigned by the ISP), the other side faces your home devices (LAN — private addresses such as `192.168.2.x`).

**What it does:**

- **NAT (Network Address Translation):** Your ISP gives you one public IP address, but many devices in your home need internet access simultaneously. NAT lets the modem/router track outgoing connections and rewrite packet headers so all home devices share that single public IP. Incoming replies are translated back to the correct internal device. From the internet's perspective, all traffic from your home appears to come from one address.
- **DHCP server:** Automatically assigns IP addresses, subnet masks, default gateway, and DNS server addresses to devices that join the home network.
- **DNS forwarding:** Passes DNS queries from home devices to the ISP's DNS servers (or a configured upstream resolver).
- **Firewall:** Blocks unsolicited inbound traffic from the internet by default — only traffic that was initiated from inside is allowed back in.
- **WiFi access point** (on combined units): Provides wireless connectivity for home devices.
- **Admin interface:** Accessible via a browser at its LAN IP (typically `192.168.2.1` or `192.168.1.1`). Used to view connected devices, DHCP leases, port forwarding rules, and static IP reservations.

**Double NAT:** If you place a second router (e.g. a Raspberry Pi) behind the ISP modem, you create a *double NAT* situation — the ISP modem NATs to the Pi's WAN IP, and the Pi NATs again to lab devices. This is fine for outbound internet access but complicates inbound connections (e.g. accessing lab services from outside). For the homelab, double NAT is an acceptable trade-off for full isolation.

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

### Network Interface

A network interface is the point of connection between a device and a network. Each interface is a distinct channel through which the device sends and receives network traffic.

- **Physical interface** — a real hardware port: a built-in Ethernet port (e.g. `eth0` on the Pi), a USB-to-Ethernet adapter (e.g. `eth1`), or a WiFi card (`wlan0`). Each has a unique MAC address burned into the hardware.
- **Virtual interface** — a software-only interface created by the OS: `lo` (loopback, always `127.0.0.1`, never leaves the machine), bridge interfaces (e.g. Proxmox's `vmbr0`), VLAN sub-interfaces (e.g. `eth1.10`), and tunnel interfaces.

Each interface has:
- A **name** assigned by the OS (`eth0`, `eth1`, `lo`, `wlan0`, …)
- A **MAC address** (OSI model layer 2, unique hardware identifier) — used for delivery within a local network
- An optional **IP address** (OSI model layer 3) — assigned statically or via DHCP; required for routing

A device can have many interfaces, each connecting it to a different network. A router exploits this: it has one interface facing the upstream network (WAN) and at least one facing the local network (LAN), and routes packets between them.

### Subnet

A subnet is a range of IP addresses that form one logical network. For example, `192.168.10.0/24` covers addresses `192.168.10.1` to `192.168.10.254`. Devices on different subnets cannot communicate directly — they need a router in between. This separation is what provides network isolation.

- **Subnet mask:** A 32-bit number that defines which part of an IP address is the *network* portion and which part is the *host* portion. Written either in dotted-decimal (e.g. `255.255.255.0`) or CIDR prefix notation (e.g. `/24`). The network portion is the same for all devices in the subnet; the host portion is what makes each device's address unique within that subnet. In binary, the mask is a block of `1`s (network bits) followed by `0`s (host bits):
    ```
    255.255.255.0    =  11111111.11111111.11111111.00000000  (/24 — 24 network bits,  8 host bits)
    255.255.0.0      =  11111111.11111111.00000000.00000000  (/16 — 16 network bits, 16 host bits)
    255.255.240.0    =  11111111.11111111.11110000.00000000  (/20 — 20 network bits, 12 host bits)
    255.255.252.0    =  11111111.11111111.11111100.00000000  (/22 — 22 network bits, 10 host bits)
    255.255.255.192  =  11111111.11111111.11111111.11000000  (/26 — 26 network bits,  6 host bits)
    ```
    Note how the boundary can fall anywhere inside an octet (e.g. `/22` splits the third octet: `11111100` — 6 bits network, 2 bits host; `/26` splits the fourth octet: `11000000` — 2 bits network, 6 bits host). This is what makes CIDR "classless" — there is no requirement for the boundary to fall on an octet boundary.
- **CIDR notation (Classless Inter-Domain Routing):** A compact way of writing an IP address together with its subnet mask as a single string: `<network-address>/<prefix-length>`. The prefix length (the number after the `/`) is simply the count of `1` bits in the subnet mask. CIDR replaced the old class-based system (Class A/B/C) and allows subnets of any size.
- **How to read CIDR — key numbers:**
    | CIDR  | Subnet Mask       | Usable Hosts | Host Range (example)                    | Notes                                              |
    |-------|-------------------|--------------|-----------------------------------------|----------------------------------------------------|
    | `/8`  | `255.0.0.0`       | 16,777,214   | `10.0.0.1` – `10.255.255.254`           | Very large; private `10.x.x.x` space               |
    | `/16` | `255.255.0.0`     | 65,534       | `192.168.0.1` – `192.168.255.254`       | Large; private `192.168.x.x` space                 |
    | `/20` | `255.255.240.0`   | 4,094        | `10.42.0.1` – `10.42.15.254`            | Used for this homelab lab network                  |
    | `/22` | `255.255.252.0`   | 1,022        | `10.42.8.1` – `10.42.11.254`            | Spans 4 "class C" blocks; used for medium LANs     |
    | `/24` | `255.255.255.0`   | 254          | `192.168.2.1` – `192.168.2.254`         | Most common home/office subnet                     |
    | `/26` | `255.255.255.192` | 62           | `10.42.10.1` – `10.42.10.62`            | Quarter of a /24; used to carve up a single block  |
    | `/30` | `255.255.255.252` | 2            | `10.0.0.1` – `10.0.0.2`                 | Point-to-point links (e.g. router–router)          |
    | `/32` | `255.255.255.255` | 0 (1 host)   | just that one IP                        | Single host route                                  |

    Formula: usable hosts = $2^{(32 - \text{prefix})} - 2$ (subtract 2: one for the network address, one for the broadcast address).
- **Network address and broadcast address:** For any subnet, the first address is the *network address* (identifies the subnet itself, not assignable to a host) and the last address is the *broadcast address* (sends to all hosts in the subnet, not assignable). Everything in between is usable.
    ```
    Subnet:    10.42.0.0/20
    Network:   10.42.0.0       ← first address, not assignable
    Hosts:     10.42.0.1  –  10.42.15.254   ← 4,094 usable addresses
    Broadcast: 10.42.15.255    ← last address, not assignable

    Subnet:    10.42.8.0/22
    Network:   10.42.8.0       ← first address, not assignable
    Hosts:     10.42.8.1  –  10.42.11.254   ← 1,022 usable addresses (spans .8, .9, .10, .11 in the third octet)
    Broadcast: 10.42.11.255    ← last address, not assignable

    Subnet:    10.42.10.0/26
    Network:   10.42.10.0      ← first address, not assignable
    Hosts:     10.42.10.1  –  10.42.10.62   ← 62 usable addresses (only the first quarter of the .10 block)
    Broadcast: 10.42.10.63     ← last address, not assignable
    ```
- **Worked examples:**
    - `192.168.2.59/24` → network `192.168.2.0`, hosts `.1`–`.254`, broadcast `.255`. The Pi's `eth0` address on the home network.
    - `10.42.0.1/20` → network `10.42.0.0`, hosts `10.42.0.1`–`10.42.15.254`, broadcast `10.42.15.255`. The Pi's `eth1` address; the entire lab network fits inside this `/20`.
    - `127.0.0.1/8` → the loopback subnet; all of `127.x.x.x` is local to the machine.
    - `10.42.8.50/22` → network `10.42.8.0`, hosts `10.42.8.1`–`10.42.11.254`, broadcast `10.42.11.255`. A `/22` spans four consecutive `/24` blocks (`.8`, `.9`, `.10`, `.11`). A host at `.50` in the third octet is well within the range — the boundary is at `.11.255`, not at `.8.255`.
    - `10.42.10.33/26` → network `10.42.10.0`, hosts `10.42.10.1`–`10.42.10.62`, broadcast `10.42.10.63`. This is the first `/26` carved out of `10.42.10.0/24`. The second `/26` would be `10.42.10.64/26` (hosts `.65`–`.126`), the third `.128/26`, the fourth `.192/26` — four equal quarters of the same `/24`.

> **Note:** You do not need to calculate all of this by hand. Know the basics (what CIDR means, how to read a subnet mask, roughly how many hosts a prefix gives you), but for anything more precise use an online subnet calculator: [calculator.net](https://www.calculator.net/ip-subnet-calculator.html), [subnet-calculator.com](https://www.subnet-calculator.com/), or [subnet-calculator.nl](https://subnet-calculator.nl/).

### DHCP

Dynamic Host Configuration Protocol — the protocol that automatically assigns network configuration to devices when they join a network. Without DHCP, every device would need a manually configured static IP.

**What DHCP assigns to each device:**

- **IP address** — a unique address for the device on this subnet
- **Subnet mask** — defines the size of the network (e.g. `255.255.255.0` / `/24`)
- **Default gateway** — the router's IP; the device sends traffic here when the destination is outside the local subnet
- **DNS server(s)** — where the device sends DNS queries to resolve hostnames
- **Lease time** — how long the assignment is valid before the device must renew

**How it works (DORA):**

1. **Discover** — the device broadcasts on the network: *"Is there a DHCP server? I need an IP address."*
2. **Offer** — the DHCP server replies with an available IP and configuration.
3. **Request** — the device formally requests the offered address.
4. **Acknowledge** — the server confirms the assignment and records the lease.

**DHCP reservation (static DHCP):** You can bind a specific IP to a device's MAC address in the DHCP server. The device still uses DHCP (no manual configuration on the device), but always receives the same IP. Useful for servers, routers, and any device that others need to reach at a predictable address.

**Lease time:** DHCP leases are temporary. When a lease expires the device must renew; if the server is unreachable it loses its IP. For servers and infrastructure, use DHCP reservations or configure static IPs directly on the device.

**DHCP conflicts:** If two DHCP servers run on the same subnet, devices may receive duplicate addresses, causing connectivity failures. This is a common mistake when connecting a Proxmox host or second router directly to the home network — its bridged interface can start responding to DHCP requests alongside the ISP modem.

> This homelab uses [dnsmasq](dnsmasq.md) as the DHCP server on the lab router. See the dnsmasq reference for configuration, lease management, and debugging commands.

### DNS

Domain Name System — the protocol that translates human-readable hostnames (e.g. `google.com`) into IP addresses (e.g. `142.250.185.110`). Without DNS you would need to know and type the IP address of every service you want to reach.

**How resolution works:**

When you type `google.com` in a browser, your OS sends a DNS query to its configured DNS server. Resolution happens in stages:

1. **Local cache** — the OS checks if it has recently resolved this name. If so, it uses the cached result immediately (no network query needed).
2. **Recursive resolver** — if not cached, the query goes to the DNS server configured for the network (set by DHCP, or manually — e.g. `8.8.8.8` for Google DNS, `1.1.1.1` for Cloudflare). This resolver handles the full lookup on your behalf and caches results.
3. **Nameserver chain** — if the recursive resolver has no cached answer, it walks down the DNS hierarchy:
   - a. **Root nameservers (.)** — one of 13 root nameserver clusters (operated by IANA/ICANN and various organisations). They do not know the final answer; they respond with a referral: *"ask the `.com` TLD nameservers."*
   - b. **TLD nameservers (.com)** — operated by Verisign for `.com`. They also respond with a referral: *"ask `ns1.google.com`"* (Google's own authoritative nameservers).
   - c. **Authoritative nameserver (ns1.google.com)** — holds the actual DNS records for `google.com` and returns the `A` record: `google.com → 142.250.185.110`.
4. **Response** — the resolver caches the answer (for the TTL duration) and returns the IP to your OS. Your OS caches it too, then passes it to the browser.

```
Browser/App
    │
    ▼
OS local cache ──► (hit) ──► done
    │ (miss)
    ▼
Recursive resolver (e.g. 8.8.8.8)
    │ cache miss → walks nameserver chain:
    │   a. Root (.)          → referral: "ask .com TLD"
    │   b. TLD (.com)        → referral: "ask ns1.google.com"
    │   c. Authoritative     → answer: google.com → 142.250.185.110
    ▼
Recursive resolver caches result, returns IP
    │
    ▼
OS caches result, passes IP to browser
```

In practice the recursive resolver almost always has `.com` and many popular domains cached already, so step 3 is skipped entirely. The full nameserver chain walk only happens for domains the resolver has never seen before.

**Key concepts:**

- **DNS server (resolver):** The server your device queries. Provided by DHCP (the DHCP server tells devices which DNS server to use) or configured manually. On Linux, see `/etc/resolv.conf` for the configured nameserver(s).
- **DNS forwarding:** A local DNS server (e.g. `dnsmasq` on the lab router) that receives queries from local devices and forwards them upstream to a public resolver. Useful when you want to add local hostname resolution on top of regular internet DNS.
- **Local DNS:** A DNS server that resolves names for hosts within a private network (e.g. `pi.lab` → `10.42.0.1`). Public resolvers have no knowledge of private hostnames; a local resolver handles them.
- **TTL (Time To Live):** How long a DNS response may be cached before it must be re-queried. Set by the domain owner. Short TTL = more DNS queries but faster propagation of IP changes; long TTL = fewer queries but slower propagation.
- **Common record types:** `A` = hostname → IPv4; `AAAA` = hostname → IPv6; `CNAME` = hostname alias → another hostname; `PTR` = IP → hostname (reverse DNS); `MX` = mail server for a domain.

**DNS in the homelab:** The lab router runs [dnsmasq](dnsmasq.md), which acts as both the DHCP server and a local DNS forwarder. It forwards external queries upstream (to the ISP modem or a public resolver) and can resolve local hostnames for lab devices by reading its own DHCP lease database. See the dnsmasq reference for configuration and DNS/DHCP commands.

---

## Commands: Networking

General networking commands with output format explanations. Used for connectivity checks, debugging, and inspecting network configuration.

---

### `nmcli connection show`

Lists all network connections managed by NetworkManager.

**Output columns:**

| Column | Description |
|--------|-------------|
| `NAME` | Human-readable connection profile name (set when the connection was created) |
| `UUID` | Unique identifier for the connection profile (used internally by NetworkManager) |
| `TYPE` | Connection type: `ethernet`, `wifi`, `loopback`, etc. |
| `DEVICE` | Network interface the connection is currently active on; blank means the profile exists but is not connected |

```
nmcli connection show
```

Example output:
```
NAME                UUID                                  TYPE      DEVICE
Wired connection 1  f4de99e2-ffb3-3c23-9bce-7003ba21786a  ethernet  eth0
lo                  57b46a79-d752-41c4-bac9-0cd0e0a5591c  loopback  lo
```

- `Wired connection 1` is the auto-created profile for the first Ethernet interface, active on `eth0`.
- `lo` is the loopback profile, always present and always active.
- If a connection has no `DEVICE` value, the profile exists but is not currently active.
- TODO: the eth1 line needs to be added here later as example for the lab router

---

### `ip a` (or `ip addr` or `ip address`)

Shows all network interfaces and their IP addresses.

**Output format for each interface block:**
```
<index>: <name>: <flags> mtu <mtu>
    link/<type> <mac-address> brd <broadcast-mac>
    inet <ipv4-address>/<prefix> brd <broadcast-ip> scope <scope>
       valid_lft <lft> preferred_lft <lft>
    inet6 <ipv6-address>/<prefix> scope <scope>
```

**Key fields:**

| Field | Description |
|-------|-------------|
| `<index>` | Sequential number assigned by the kernel (1, 2, 3, …) |
| `<name>` | Interface name: `lo` = loopback, `eth0` = first Ethernet, `eth1` = second, `wlan0` = WiFi. The loopback (`lo`) is a virtual interface the OS uses to communicate with itself (localhost) — packets sent here never leave the machine. Always present at `127.0.0.1` (=localhost). Not a real network card. |
| `<flags>` | State flags in angle brackets: `UP` = interface enabled; `LOWER_UP` = physical link present (cable connected); `NO-CARRIER` = no physical link (cable unplugged); `BROADCAST` = supports broadcast; `MULTICAST` = supports multicast; `LOOPBACK` = loopback interface |
| `mtu` | Maximum Transmission Unit — largest packet size in bytes (1500 = standard Ethernet) |
| `link/` | Layer 2 info — MAC address and broadcast MAC (`ff:ff:ff:ff:ff:ff` = all hosts on the LAN) |
| `inet` | IPv4 address with CIDR prefix (e.g. `/24` = `255.255.255.0`) |
| `brd` | Broadcast address for the subnet |
| `scope` | Reachability: `global` = routable; `host` = local to this machine only; `link` = same physical link only |
| `valid_lft` | How long the address is valid: `forever` = static; a number in seconds = DHCP lease remaining time |
| `preferred_lft` | How long the address is preferred for new connections (may expire before `valid_lft` on DHCP renewal) |
| `inet6` | IPv6 address — `fe80::` prefix means link-local (not routable; used for neighbour discovery on the same link) |

```
ip a
```

Example output (Pi router with two Ethernet interfaces):
```
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host noprefixroute
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 88:a2:9e:98:97:1e brd ff:ff:ff:ff:ff:ff
    inet 192.168.2.59/24 brd 192.168.2.255 scope global dynamic noprefixroute eth0
       valid_lft 86165sec preferred_lft 86165sec
    inet6 fe80::1d9f:d306:dbe6:f1db/64 scope link noprefixroute
       valid_lft forever preferred_lft forever
3: eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether aa:bb:cc:dd:ee:ff brd ff:ff:ff:ff:ff:ff
    inet 10.42.0.1/20 brd 10.42.15.255 scope global eth1
       valid_lft forever preferred_lft forever
    inet6 fe80::a8bb:ccff:fedd:eeff/64 scope link noprefixroute
       valid_lft forever preferred_lft forever
4: wlan0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc pfifo_fast state DOWN group default qlen 1000
    link/ether 88:a2:9e:98:97:1f brd ff:ff:ff:ff:ff:ff
```

- `eth0` (WAN): `UP` + `LOWER_UP` — cable connected. Got `192.168.2.59/24` from the ISP modem's DHCP server; `valid_lft 86165sec` shows the lease expires in ~24h (not static).
- `eth1` (LAN): `UP` + `LOWER_UP` — cable connected. Has static `10.42.0.1/20`; `valid_lft forever` confirms it is not DHCP.
- `wlan0`: `NO-CARRIER` — no WiFi signal; `state DOWN` — not active; no `inet` line = no IP assigned.
- TODO: the eth1 line was pasted by copilot, check what the actual output is later and update above

---

### `ip r`

Shows the routing table — how the kernel decides which interface and gateway to use for each destination.

**Output format per route:**
```
<destination> [via <gateway>] dev <interface> proto <source> [scope <scope>] src <src-ip> metric <metric>
```

**Key fields:**

| Field | Description |
|-------|-------------|
| `<destination>` | Target network, or `default` (= `0.0.0.0/0`) which matches all traffic not covered by a more specific route |
| `via <gateway>` | Next-hop IP to send packets to; only present when the destination is not directly connected |
| `dev <iface>` | Network interface to send the packet out of. `dev` because Linux uses the dev keyword to refer to a *device* (any kernel‑managed hardware or virtual component represented under /dev (e.g., disks, terminals, network interfaces, etc.)). |
| `proto` | Who installed this route: `kernel` = auto-created when an IP was assigned to an interface; `dhcp` = received from DHCP server; `static` = manually configured |
| `scope link` | Destination is directly reachable on the link — no gateway needed (same subnet) |
| `src` | Preferred source IP to use when sending packets on this route |
| `metric` | Route priority — lower number wins when multiple routes match the same destination |

```
ip r
```

Example output (Pi router):
```
default via 192.168.2.254 dev eth0 proto dhcp src 192.168.2.59 metric 100
192.168.2.0/24 dev eth0 proto kernel scope link src 192.168.2.59 metric 100
10.42.0.0/20 dev eth1 proto kernel scope link src 10.42.0.1 metric 100
```

- `default via 192.168.2.254 dev eth0` — all internet-bound traffic goes to the ISP modem first, then onward.
- `192.168.2.0/24 dev eth0 scope link` — home network hosts are directly reachable via `eth0`; no gateway needed.
- `10.42.0.0/20 dev eth1 scope link` — lab network hosts are directly reachable via `eth1`; no gateway needed.
- TODO: the last line was pasted by copilot, check what the actual output is later and update above

---

### `ping`

Tests reachability and measures round-trip time to a host by sending ICMP echo requests. `-c <n>` limits the number of packets sent (without it, ping runs until interrupted).

```
ping -c 3 <host>
```

---

### `ip neigh` / `arp` — ARP Neighbour Table

Shows the ARP (Address Resolution Protocol) table — the mapping of IP addresses to MAC addresses for devices on the same link. ARP is how the kernel finds the MAC address of a device it needs to send a packet to directly (i.e. on the same subnet). It sends an ARP broadcast ("who has `<ip>`?"), caches the reply here, and uses the MAC for delivery.

There are two families of commands that show this same table: the modern `ip neigh` (from iproute2) and the legacy `arp` (from net-tools). Both read the same kernel ARP cache — they just format and enrich the output differently.

> **The ARP table is not always up-to-date.** It only contains entries for devices the kernel has recently communicated with. A device that is online but has not been contacted will not appear. Entries also expire — `STALE` entries are re-probed on next use, and old entries eventually disappear. If you expect to see a device but it is missing, `ping` it first to trigger an ARP exchange, then check again:
>
> ```
> poetoec@lab-router:~ $ ip neigh
> 192.168.2.5 dev eth0 lladdr 80:e4:ba:58:58:c2 REACHABLE
> ```
>
> No entry for `10.42.0.168` yet — the Pi has not talked to it. After pinging:
>
> ```
> poetoec@lab-router:~ $ ping -c 3 10.42.0.168
> PING 10.42.0.168 (10.42.0.168) 56(84) bytes of data.
> 64 bytes from 10.42.0.168: icmp_seq=1 ttl=64 time=4.67 ms
> 64 bytes from 10.42.0.168: icmp_seq=2 ttl=64 time=2.50 ms
> 64 bytes from 10.42.0.168: icmp_seq=3 ttl=64 time=2.52 ms
>
> poetoec@lab-router:~ $ ip neigh
> 192.168.2.254 dev eth0 lladdr b0:5b:99:28:74:80 REACHABLE
> 192.168.2.5 dev eth0 lladdr 80:e4:ba:58:58:c2 REACHABLE
> 10.42.0.168 dev eth1 lladdr 28:94:01:8a:ec:28 REACHABLE
> ```
>
> Now `10.42.0.168` appears on `eth1` because the ping triggered an ARP resolution.

#### IPs only: `ip neigh` and `arp -n`

These show the ARP table with raw IP addresses (no hostname resolution).

**`ip neigh`** — the modern command; includes the ARP state (`REACHABLE`, `STALE`, `DELAY`, `FAILED`, `PERMANENT`):

```
<ip-address> dev <interface> lladdr <mac-address> <state>
```

| Field | Description |
|-------|-------------|
| `<ip-address>` | Neighbour's IP address |
| `dev` | Interface the neighbour was seen on |
| `lladdr` | Link Layer address = MAC address of that device |
| `<state>` | `REACHABLE` = recently confirmed; `STALE` = not confirmed recently, will re-probe on next use; `DELAY` = waiting to confirm after a packet was sent; `FAILED` = ARP probe sent but no reply — device unreachable or gone; `PERMANENT` = statically configured, never expires |

```
poetoec@lab-router:~ $ ip neigh
192.168.2.254 dev eth0 lladdr b0:5b:99:28:74:80 DELAY
192.168.2.5 dev eth0 lladdr 80:e4:ba:58:58:c2 REACHABLE
```

**`arp -n`** — the legacy equivalent; `-n` suppresses hostname resolution. Shows flags instead of states (`C` = complete/MAC resolved, `M` = permanent/static, `P` = published), such as:

```
poetoec@lab-router:~ $ arp -n
Address         HWtype  HWaddress           Flags Iface
192.168.2.254   ether   b0:5b:99:28:74:80   C     eth0
192.168.2.5     ether   80:e4:ba:58:58:c2   C     eth0
```

- `192.168.2.254` on `eth0` — the ISP modem; `DELAY` in `ip neigh` means the kernel sent a packet and is waiting for an ARP confirmation (transitions to `REACHABLE` on reply, or `FAILED` if no reply comes).
- `192.168.2.5` on `eth0` — a device on the home network; `REACHABLE` means its MAC was recently confirmed via ARP.
- If a device shows `FAILED`, the Pi sent an ARP request but got no reply — the device is off, not connected, or there is a cabling/VLAN issue.

#### With hostnames: `arp -a` and `ip neigh` + reverse DNS

To identify *which* device is behind each IP, you need hostname resolution. `arp -a` does this automatically; `ip neigh` does not, but you can pipe it through a reverse DNS lookup.

**`arp -a`** — resolves IPs to hostnames via reverse DNS or `/etc/hosts` out of the box, such as:

```
poetoec@lab-router:~ $ arp -a
mijnmodem.kpn (192.168.2.254) at b0:5b:99:28:74:80 [ether] on eth0
<laptop name>.home (192.168.2.5) at 80:e4:ba:58:58:c2 [ether] on eth0
```

- `mijnmodem.kpn` — the ISP modem's hostname (advertised via the ISP modem's DNS).
- `<laptop name>.home` — the laptop's hostname on the home network.

**`ip neigh` with manual reverse DNS** — `ip neigh` has no built-in hostname resolution, but you can add it by piping each IP through `getent hosts` (which queries DNS and `/etc/hosts`):

```bash
ip neigh | while read ip rest; do
  name=$(getent hosts "$ip" | awk '{print $2}')
  echo "${name:-(unknown)} $ip $rest"
done
```

Use `arp -a` when you want to quickly identify who's who on the network; use `ip neigh` (with or without the pipe) when you need the ARP state information for debugging.

---

### `ss` — Socket Statistics

Shows active network sockets (connections and listening ports). Replaces the legacy `netstat` command. Use it to check which services are listening on which ports, verify a daemon started correctly, or debug port conflicts.

**Common flags:**

| Flag | Description |
|------|-------------|
| `-t` | Show TCP sockets only |
| `-u` | Show UDP sockets only |
| `-l` | Show only listening sockets (servers waiting for connections) |
| `-n` | Numeric output — show port numbers instead of service names (e.g. `53` instead of `domain`) |
| `-p` | Show the process using each socket (requires `sudo` for processes owned by other users) |
| `-4` / `-6` | Show only IPv4 / IPv6 sockets |

**Typical combinations:**

| Command | Purpose |
|---------|---------|
| `ss -tulpn` | All TCP and UDP listening sockets with process info and numeric ports — the most common "what's listening?" check |
| `ss -tn` | All established TCP connections (no listeners) |
| `ss -ulpn` | Only UDP listening sockets (useful for checking DHCP port 67, DNS port 53) |

**Output format:**

```
Netid  State   Recv-Q  Send-Q  Local Address:Port  Peer Address:Port  Process
```

**Key fields:**

| Field | Description |
|-------|-------------|
| `Netid` | Socket type: `tcp` = TCP, `udp` = UDP, `u_str` = Unix stream socket |
| `State` | `LISTEN` = waiting for incoming connections; `ESTAB` = active connection; `TIME-WAIT` = connection closing; `UNCONN` = unconnected (normal for UDP listeners) |
| `Recv-Q` | Bytes queued to be read by the application (non-zero on a listener = connections waiting to be accepted) |
| `Send-Q` | Bytes queued to be sent (non-zero on a listener = the backlog size / max pending connections) |
| `Local Address:Port` | IP and port this socket is bound to; `0.0.0.0` = all IPv4 interfaces; `*` = all interfaces (any protocol); a specific IP means it only accepts traffic on that address |
| `Peer Address:Port` | Remote side of the connection; `0.0.0.0:*` for listeners (no peer yet) |
| `Process` | Process name and PID using the socket (only shown with `-p` and sufficient privileges) |

```
sudo ss -tulpn
```

Example output (Pi router running dnsmasq and SSH):
```
Netid  State   Recv-Q  Send-Q  Local Address:Port  Peer Address:Port  Process
udp    UNCONN  0       0       10.42.0.1:53        0.0.0.0:*          users:(("dnsmasq",pid=512,fd=4))
udp    UNCONN  0       0       0.0.0.0:67          0.0.0.0:*          users:(("dnsmasq",pid=512,fd=3))
tcp    LISTEN  0       32      10.42.0.1:53        0.0.0.0:*          users:(("dnsmasq",pid=512,fd=5))
tcp    LISTEN  0       128     0.0.0.0:22          0.0.0.0:*          users:(("sshd",pid=450,fd=3))
```

- `10.42.0.1:53` (TCP + UDP) — dnsmasq serving DNS on the LAN interface only (not on `0.0.0.0`, so it is not listening on the WAN side).
- `0.0.0.0:67` (UDP) — dnsmasq serving DHCP on all interfaces (port 67 is the DHCP server port; filtering is done by the `interface=` directive in dnsmasq config, not by bind address).
- `0.0.0.0:22` (TCP) — SSH daemon listening on all interfaces.

**Debugging port conflicts:** If a service fails to start with "Address already in use", use `ss -tulpn | grep :<port>` to find which process already holds that port. For example, when dnsmasq fails because something else occupies port 53:

```
sudo ss -tulpn | grep :53
tcp  LISTEN  0  4096  127.0.0.53%lo:53  0.0.0.0:*  users:(("systemd-resolve",pid=320,fd=17))
```

This shows `systemd-resolved` is listening on `127.0.0.53:53` — it must be stopped or dnsmasq must be configured to not bind to loopback (`except-interface=lo`).

---

### `dig` / `nslookup` — DNS Lookup

Queries DNS servers to resolve hostnames to IP addresses (or vice versa). Use these to debug DNS resolution issues — verify that a hostname resolves correctly, check which DNS server is answering, and inspect the full DNS response.

There are two commands: `dig` (the modern, detailed tool) and `nslookup` (simpler, available on most systems including Windows). Both query DNS; `dig` gives more control and detail.

#### `dig`

`dig` (Domain Information Groper) queries a DNS server and shows the full response, including the answer, the server that responded, and the query time.

**Basic usage:**

```bash
dig <hostname>                  # query the default DNS server for an A record
dig <hostname> @<server>        # query a specific DNS server
dig -x <ip>                     # reverse DNS lookup (IP → hostname)
dig <hostname> AAAA             # query for IPv6 address
dig <hostname> MX               # query for mail server records
dig <hostname> NS               # query for nameservers
dig <hostname> SOA              # query for Start of Authority (zone info)
dig <hostname> TXT              # query for TXT records (SPF, verification, etc.)
dig <hostname> ANY              # request all available record types
dig <hostname> +short           # compact output — just the answer
dig <hostname> +noall +answer   # suppress everything except the answer section
dig <hostname> +trace           # trace the full resolution path from root to answer
```

**Example — full query:**

```
poetoec@lab-router:~ $ dig google.com

; <<>> DiG 9.18.28 <<>> google.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 12345
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; QUESTION SECTION:
;google.com.                    IN      A

;; ANSWER SECTION:
google.com.             300     IN      A       142.250.185.110

;; Query time: 12 msec
;; SERVER: 192.168.2.254#53(192.168.2.254) (UDP)
;; WHEN: Thu Aug 14 12:00:00 CEST 2026
;; MSG SIZE  rcvd: 55
```

**Header flags:**

The line `flags: qr rd ra` contains single-letter flags describing the query and response:

| Flag | Name | Description |
|------|------|-------------|
| `qr` | Query Response | This is a response (not a query). |
| `rd` | Recursion Desired | The client asked the server to resolve recursively (follow the chain of nameservers on its behalf). |
| `ra` | Recursion Available | The server supports recursion. |
| `aa` | Authoritative Answer | The responding server is the authoritative nameserver for this domain (not a cache). Absent here because the ISP modem's resolver is a cache, not the authority for `google.com`. |
| `tc` | Truncated | Response was too large for UDP and was truncated — the client should retry over TCP. |
| `ad` | Authenticated Data | DNSSEC validation passed — the response is cryptographically verified. |
| `cd` | Checking Disabled | The client asked the server to skip DNSSEC validation. |

The `status` field shows the result: `NOERROR` = success, `NXDOMAIN` = domain does not exist, `SERVFAIL` = server error (e.g. upstream unreachable or DNSSEC failure), `REFUSED` = server refused the query.

The counters (`QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1`) show how many records are in each section of the response.

**Answer format:**

Each line in the ANSWER section has five columns:

```
google.com.             300     IN      A       142.250.185.110
<name>                  <TTL>   <class> <type>  <data>
```

| Column | Description |
|--------|-------------|
| `<name>` | The domain name this record belongs to. The trailing `.` is the DNS root — all fully qualified domain names end with it. |
| `<TTL>` | Time To Live in seconds — how long this answer may be cached. `300` = 5 minutes. After this, the resolver must re-query. |
| `<class>` | Almost always `IN` (Internet). Other classes exist (`CH`, `HS`) but are rarely used. |
| `<type>` | Record type — see table below. |
| `<data>` | The record value — an IP address, hostname, or other data depending on the type. |

**Common record types in detail:**

| Type | Description | Example Data |
|------|-------------|--------------|
| `A` | IPv4 address | `142.250.185.110` |
| `AAAA` | IPv6 address | `2a00:1450:400e:811::200e` |
| `CNAME` | Alias — points to another hostname (the "canonical name"). The resolver follows the chain until it reaches an A/AAAA record. | `www.google.com. → www.google.com.cdn.example.net.` |
| `MX` | Mail exchanger — where to deliver email for this domain. Includes a priority (lower = preferred). | `10 smtp.google.com.` |
| `NS` | Nameserver — the authoritative DNS servers for this domain. | `ns1.google.com.` |
| `TXT` | Arbitrary text — used for SPF (email anti-spoofing), domain verification, DKIM, etc. | `"v=spf1 include:_spf.google.com ~all"` |
| `SOA` | Start of Authority — zone metadata: primary nameserver, admin email, serial number, refresh/retry/expire timers. | `ns1.google.com. dns-admin.google.com. 2024010100 900 900 1800 60` |
| `PTR` | Pointer — reverse DNS, maps an IP back to a hostname. Used with `dig -x`. | `mijnmodem.kpn.` |
| `SRV` | Service locator — specifies host and port for a service (e.g. SIP, LDAP, Kubernetes API). | `0 5 5060 sip.example.com.` |

**Key sections:**

| Section | Description |
|---------|-------------|
| `QUESTION` | What was asked — the hostname and record type. |
| `ANSWER` | The response records matching the question. |
| `AUTHORITY` | The authoritative nameservers for the domain (usually present when the answer comes from a referral). |
| `ADDITIONAL` | Extra records provided to avoid follow-up queries (e.g. A records for the nameservers listed in AUTHORITY). |
| `SERVER` | Which DNS server answered (here: the ISP modem at `192.168.2.254`). |
| `Query time` | How long the lookup took — useful for comparing resolvers. |

**Example — short output:**

```
poetoec@lab-router:~ $ dig google.com +short
142.250.185.110
```

**Example — clean answer only:**

```bash
dig google.com +noall +answer
```

Suppresses the header, question, authority, and additional sections — shows only the answer lines. Useful for scripting or when you want a clean but not *too* short output (unlike `+short`, this still shows TTL and record type).

**Example — query a specific DNS server:**

```bash
dig google.com @8.8.8.8          # ask Google's public DNS directly
dig google.com @10.42.0.1        # ask the lab router's DNS
```

Useful for verifying whether the lab's local DNS server resolves differently from a public one. For example, if `dig lab-node1.lab @10.42.0.1` returns an answer but `dig lab-node1.lab @8.8.8.8` returns `NXDOMAIN`, your local DNS is working correctly — public resolvers have no knowledge of private hostnames.

**Example — reverse DNS:**

```bash
dig -x 192.168.2.254 +short      # find the hostname for an IP
```

This sends a PTR query for `254.2.168.192.in-addr.arpa` — the special reversed-IP format used for reverse DNS.

**Example — trace full resolution path:**

```bash
dig google.com +trace
```

Shows every step of the resolution: root nameservers → `.com` TLD nameservers → `google.com` authoritative nameservers → final answer. Useful for debugging where in the chain a lookup breaks — if the trace stops at a certain level, that is where the problem is.

**Example — querying different record types:**

```bash
dig google.com MX +short          # mail servers
dig google.com NS +short          # authoritative nameservers
dig google.com TXT +short         # TXT records (SPF, verification)
dig google.com SOA +short         # zone authority info
```

**Useful flag combinations:**

| Command | Purpose |
|---------|---------|
| `dig <host> +short` | Quick answer only. |
| `dig <host> +noall +answer` | Answer with TTL and record type, no clutter. |
| `dig <host> +trace` | Trace full resolution chain from root. |
| `dig <host> @<server>` | Test a specific resolver. |
| `dig <host> +stats` | Show query time and server (default on, useful if disabled). |
| `dig -x <ip>` | Reverse DNS lookup. |

#### `nslookup`

`nslookup` is a simpler DNS lookup tool. Less detailed than `dig`, but available on virtually every OS (Linux, macOS, Windows).

**Basic usage:**

```bash
nslookup <hostname>              # query the default DNS server
nslookup <hostname> <server>     # query a specific DNS server
nslookup <ip>                    # reverse DNS lookup
```

**Example:**

```
poetoec@lab-router:~ $ nslookup google.com
Server:         192.168.2.254
Address:        192.168.2.254#53

Non-authoritative answer:
Name:   google.com
Address: 142.250.185.110
```

- `Server` / `Address` — the DNS server that was queried.
- `Non-authoritative answer` — the response came from a cache (the recursive resolver), not directly from Google's authoritative nameserver. This is normal.

**Example — query a specific server:**

```
poetoec@lab-router:~ $ nslookup google.com 8.8.8.8
Server:         8.8.8.8
Address:        8.8.8.8#53

Non-authoritative answer:
Name:   google.com
Address: 142.250.185.110
```

#### When to use which

| Tool | Best for |
|------|----------|
| `dig +short` | Quick "does this hostname resolve?" check. |
| `dig` (full) | Debugging DNS — see TTL, response status, which server answered, query time. |
| `dig @<server>` | Testing whether a specific DNS server (e.g. the lab router) resolves correctly. |
| `nslookup` | Quick lookups on any OS, especially Windows where `dig` is not installed by default. |

---

### DHCP Client Commands

Commands for inspecting and managing DHCP leases from the **client** side (the device requesting an IP). For server-side DHCP management (lease files, reservations, debugging), see the [dnsmasq reference](dnsmasq.md#commands-dhcp).

#### `dhclient` — Request or Release a DHCP Lease

`dhclient` is the ISC DHCP client. It sends DHCP DISCOVER/REQUEST messages to obtain a lease, or releases an existing one.

```bash
sudo dhclient eth0                     # request a new lease on eth0
sudo dhclient -r eth0                  # release the current lease
sudo dhclient -v eth0                  # verbose — shows the full DORA exchange
```

**Verbose output example:**

```
poetoec@proxmox-node1:~ $ sudo dhclient -v eth0
Internet Systems Consortium DHCP Client 4.4.3
Listening on LPF/eth0/28:94:01:8a:ec:28
Sending on   LPF/eth0/28:94:01:8a:ec:28
DHCPDISCOVER on eth0 to 255.255.255.255 port 67 interval 3
DHCPOFFER of 10.42.0.168 from 10.42.0.1
DHCPREQUEST for 10.42.0.168 on eth0 to 255.255.255.255 port 67
DHCPACK of 10.42.0.168 from 10.42.0.1
bound to 10.42.0.168 -- renewal in 40000 seconds.
```

This shows the full DORA handshake: DISCOVER → OFFER → REQUEST → ACK. The server (`10.42.0.1`, the lab router) assigned `10.42.0.168`.

#### NetworkManager — Release and Renew

On systems using NetworkManager (most modern desktop/server Linux), use `nmcli` instead of `dhclient`:

```bash
# Bounce the connection (release + renew in one step):
sudo nmcli connection down "Wired connection 1" && sudo nmcli connection up "Wired connection 1"

# Or by device name:
sudo nmcli device disconnect eth0 && sudo nmcli device connect eth0
```

#### View Current DHCP Lease Details

On the client, the active lease is stored in a file:

```bash
# dhclient lease file (location varies by distribution):
cat /var/lib/dhcp/dhclient.eth0.leases

# Or check the current IP and lease time via ip:
ip -4 addr show eth0
```

The `valid_lft` value in `ip addr` output shows the remaining lease time in seconds (`forever` = static, not DHCP).

#### Inspect DHCP Traffic

Use [`tcpdump`](#tcpdump--packet-capture) to capture live DHCP traffic and see exactly what the client sends and what the server responds:

```bash
sudo tcpdump -i eth0 -n port 67 or port 68
```

See the [tcpdump section](#tcpdump--packet-capture) for full details, flags, and output format.

#### Quick DHCP Debugging Checklist

| Check | Command |
|-------|---------|
| Does the client have an IP? | `ip -4 addr show eth0` |
| What is the default gateway? | `ip route \| grep default` |
| What DNS server was assigned? | `cat /etc/resolv.conf` or `resolvectl status` |
| Is the DHCP server reachable? | `ping <dhcp-server-ip>` |
| Is port 67 open on the server? | `ss -ulpn \| grep :67` (on the server) |
| What does the DHCP exchange look like? | `sudo tcpdump -i eth0 -n port 67 or port 68` |
| Force a fresh lease | `sudo dhclient -r eth0 && sudo dhclient -v eth0` |

---

### `tcpdump` — Packet Capture

Captures and displays network packets in real time. The most fundamental network debugging tool — it shows you exactly what is going on the wire. Requires `sudo` because it puts the network interface into promiscuous mode.

**Basic usage:**

```bash
sudo tcpdump -i <interface>                         # capture all traffic on an interface
sudo tcpdump -i eth0 -n                              # -n = numeric (no DNS resolution, faster)
sudo tcpdump -i eth0 -n -c 10                        # capture only 10 packets then stop
sudo tcpdump -i eth0 -n port 53                      # capture only DNS traffic (port 53)
sudo tcpdump -i eth0 -n port 67 or port 68           # capture only DHCP traffic
sudo tcpdump -i eth0 -n host 10.42.0.168             # capture traffic to/from a specific host
sudo tcpdump -i eth0 -n icmp                         # capture only ICMP (ping) traffic
sudo tcpdump -i eth0 -n tcp port 22                  # capture only SSH traffic
sudo tcpdump -i eth0 -n -w capture.pcap              # write raw packets to file (for Wireshark)
sudo tcpdump -i eth0 -n -r capture.pcap              # read packets from a file
```

**Common flags:**

| Flag | Description |
|------|-------------|
| `-i <iface>` | Interface to capture on. Use `-i any` to capture on all interfaces. |
| `-n` | Numeric output — don't resolve IPs to hostnames or ports to service names. Much faster. |
| `-nn` | Numeric output for both IPs and ports (same as `-n` on most systems). |
| `-c <count>` | Stop after capturing `<count>` packets. |
| `-v` / `-vv` / `-vvv` | Increase verbosity — show more protocol details (TTL, ID, flags, checksums, etc.). |
| `-w <file>` | Write raw packets to a `.pcap` file instead of printing to terminal. Can be opened in Wireshark. |
| `-r <file>` | Read and display packets from a previously captured `.pcap` file. |
| `-A` | Print packet payload in ASCII (useful for HTTP, DNS text, etc.). |
| `-X` | Print packet payload in both hex and ASCII. |
| `-e` | Show link-layer (Ethernet) headers — includes MAC addresses. |
| `-q` | Quiet — shorter output, less protocol detail. |

**Filter expressions:**

tcpdump uses BPF (Berkeley Packet Filter) expressions to select which packets to capture:

| Filter | Description |
|--------|-------------|
| `host <ip>` | Traffic to or from a specific IP. |
| `src <ip>` | Traffic from a specific source IP. |
| `dst <ip>` | Traffic to a specific destination IP. |
| `port <n>` | Traffic on a specific port (TCP or UDP). |
| `tcp port <n>` | TCP traffic on a specific port. |
| `udp port <n>` | UDP traffic on a specific port. |
| `icmp` | ICMP traffic only (ping, traceroute). |
| `arp` | ARP traffic only. |
| `net <cidr>` | Traffic to or from a subnet (e.g. `net 10.42.0.0/20`). |
| `not port 22` | Exclude SSH traffic (useful when capturing over SSH to avoid flooding). |
| Combine with `and`, `or`, `not` | `host 10.42.0.1 and port 53` = DNS traffic to/from the lab router. |

**Output format:**

Each line shows one packet:

```
<timestamp> <protocol> <src> > <dst>: <details>
```

Example — DHCP traffic:
```
12:00:01.123456 IP 0.0.0.0.68 > 255.255.255.255.67: BOOTP/DHCP, Request from 28:94:01:8a:ec:28, length 300
12:00:01.124789 IP 10.42.0.1.67 > 10.42.0.168.68: BOOTP/DHCP, Reply, length 300
```

- First line: client (`0.0.0.0`, no IP yet) broadcasts a DHCP request on port 68 → 67.
- Second line: server (`10.42.0.1`) replies with an offer/ack to the client on port 67 → 68.

Example — DNS query:
```
12:00:02.456789 IP 10.42.0.168.43210 > 10.42.0.1.53: 12345+ A? google.com. (28)
12:00:02.458123 IP 10.42.0.1.53 > 10.42.0.168.43210: 12345 1/0/0 A 142.250.185.110 (44)
```

- First line: client queries the lab router's DNS for `google.com` (A record).
- Second line: server responds with `142.250.185.110`.

**Useful recipes:**

| Purpose | Command |
|---------|---------|
| Debug DHCP | `sudo tcpdump -i eth0 -n port 67 or port 68` |
| Debug DNS | `sudo tcpdump -i eth0 -n port 53` |
| Debug ARP | `sudo tcpdump -i eth0 -n arp` |
| All traffic to/from a host | `sudo tcpdump -i eth0 -n host 10.42.0.168` |
| Capture for Wireshark | `sudo tcpdump -i eth0 -n -w /tmp/capture.pcap` |
| Capture over SSH (exclude SSH itself) | `sudo tcpdump -i eth0 -n not port 22` |
| Verbose DHCP with MACs | `sudo tcpdump -i eth0 -n -e -v port 67 or port 68` |

> **Tip:** When capturing over SSH, always add `not port 22` to your filter — otherwise tcpdump captures its own SSH traffic, which generates more traffic, which generates more captures, flooding the output.

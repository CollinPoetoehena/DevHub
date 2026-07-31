# Network Background & Commands
TODO: this document provides background information and commands with detailed explanation for networking. This provides a reference for networking concepts and commands that are commonly used in networking and avoid repetition of information in other documents.

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

**DNS in the homelab:** The lab router runs `dnsmasq`, which acts as both the DHCP server and a local DNS forwarder. It forwards external queries upstream (to the ISP modem or a public resolver) and can resolve local hostnames for lab devices by reading its own DHCP lease database.

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

### `ip a`

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

### `ip neigh`

Shows the neighbour (ARP) table — the mapping of IP addresses to MAC addresses for devices on the same link.

ARP (Address Resolution Protocol) is how the kernel finds the MAC address of a device it needs to send a packet to directly (i.e. on the same subnet). It sends an ARP broadcast ("who has `<ip>`?"), caches the reply here, and uses the MAC for delivery.

**Output format per entry:**
```
<ip-address> dev <interface> lladdr <mac-address> <state>
```

**Key fields:**

| Field | Description |
|-------|-------------|
| `<ip-address>` | Neighbour's IP address |
| `dev` | Interface the neighbour was seen on |
| `lladdr` | Link Layer address = MAC address of that device |
| `<state>` | `REACHABLE` = recently confirmed; `STALE` = not confirmed recently, will re-probe on next use; `DELAY` = waiting to confirm after a packet was sent; `FAILED` = ARP probe sent but no reply — device unreachable or gone; `PERMANENT` = statically configured, never expires |

```
ip neigh
```

Example output:
```
192.168.2.254 dev eth0 lladdr a4:91:b1:xx:xx:xx REACHABLE
10.42.0.100 dev eth1 lladdr b8:27:eb:xx:xx:xx REACHABLE
```

- `192.168.2.254` on `eth0` — the ISP modem; `REACHABLE` means its MAC was recently resolved via ARP.
- `10.42.0.100` on `eth1` — a lab device that received its IP from the DHCP server and is currently reachable.
- If a device shows `FAILED`, the Pi sent an ARP request but got no reply — the device is off, not connected, or there is a cabling/VLAN issue.

---

### `arp -n`

Shows the same ARP table as `ip neigh` but in the older `arp(8)` format. `-n` suppresses hostname resolution (faster and unambiguous).

**Output format:**
```
<ip-address>   <hw-type>   <mac-address>   <flags>   <interface>
```

Flags: `C` = complete (MAC resolved successfully), `M` = permanent/static, `P` = published.

```
arp -n
```

Example output:
```
Address         HWtype  HWaddress           Flags Iface
192.168.2.254   ether   a4:91:b1:xx:xx:xx   C     eth0
10.42.0.100     ether   b8:27:eb:xx:xx:xx   C     eth1
```

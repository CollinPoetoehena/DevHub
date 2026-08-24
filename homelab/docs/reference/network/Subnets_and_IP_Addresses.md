# Subnets & IP Addresses

Background information on subnets, CIDR notation, IPv4, IPv6, and NAT.

---

## Table of Contents

- [IP Addresses — IPv4 and IPv6](#ip-addresses--ipv4-and-ipv6)
  - [IPv4](#ipv4)
  - [NAT — Network Address Translation (IPv4)](#nat--network-address-translation-ipv4)
  - [IPv6](#ipv6)
    - [IPv6 address types](#ipv6-address-types)
    - [IPv6 does not need NAT — and why that matters](#ipv6-does-not-need-nat--and-why-that-matters)
    - [How IPv6 address assignment works](#how-ipv6-address-assignment-works)
- [Subnets](#subnets)

---

## IP Addresses — IPv4 and IPv6

An IP address is a numeric label assigned to every device on a network. It serves two purposes: **identification** (which device is this?) and **location** (where is it on the network, and how do I route packets to it?). There are two versions of IP in use today: IPv4 (the original, still dominant) and IPv6 (the successor, designed to solve IPv4's limitations).

### IPv4

IPv4 is the fourth version of the Internet Protocol and the foundation of most modern networking. It’s still widely used today, especially in legacy systems and many home and enterprise networks.

**Format:** A 32-bit number, written as four decimal octets separated by dots ("dotted-decimal notation"). Each octet is 8 bits → ranges from 0 to 255.

```
192.168.2.59

In binary:
11000000.10101000.00000010.00111011
```

32 bits means $2^{32}$ = 4,294,967,296 total possible addresses (~4.3 billion). That sounds like a lot, but it is far fewer than the number of devices on the internet today. This shortage is the central problem that NAT solves and that IPv6 was designed to eliminate.

**IPv4 address exhaustion:** IANA (the global IP address authority) allocated the last blocks of IPv4 addresses in 2011. Regional registries (RIPE for Europe, ARIN for North America, etc.) exhausted their pools in subsequent years. Today, new IPv4 addresses are only available through transfers (buying from others) or reclamation. This is why:
- Most home and business networks use private addresses + NAT (one public IP shared by all devices).
- ISPs increasingly use **CGNAT** (Carrier-Grade NAT) — putting multiple customers behind a single public IPv4 address, adding yet another NAT layer.
- IPv6 was developed as the long-term solution.

**Private address ranges (RFC 1918):** Three blocks of IPv4 addresses are reserved for private networks — they are not routable on the public internet. Any device can use them internally, and routers/firewalls will never forward them to the internet. If a packet with a private source IP reaches the internet, it is dropped.

| Range | CIDR | Usable Addresses | Typical Use |
|-------|------|------------------|-------------|
| `10.0.0.0` – `10.255.255.255` | `10.0.0.0/8` | 16,777,214 | Large enterprise networks, cloud VPCs, homelabs |
| `172.16.0.0` – `172.31.255.255` | `172.16.0.0/12` | 1,048,574 | Medium networks, Docker default bridges |
| `192.168.0.0` – `192.168.255.255` | `192.168.0.0/16` | 65,534 | Home networks, small offices |

For example, a homelab uses `10.42.0.0/20` (from the `10.0.0.0/8` block). The home network uses `192.168.2.0/24` (from the `192.168.0.0/16` block). Both are private ranges — they only work within their respective local networks.

**Other special IPv4 ranges:**

| Range | Purpose |
|-------|---------|
| `127.0.0.0/8` | Loopback — `127.0.0.1` is "localhost", traffic never leaves the machine |
| `169.254.0.0/16` | Link-local — auto-assigned when DHCP fails (APIPA); not routable |
| `0.0.0.0` | "Any" / "unspecified" — used in routing tables and socket binds, not a real destination |
| `255.255.255.255` | Limited broadcast — reaches all hosts on the local network segment |
| `100.64.0.0/10` | Carrier-grade NAT (CGNAT) — used by ISPs for another layer of NAT before the customer's modem |

### NAT — Network Address Translation (IPv4)

NAT is the mechanism that allows many devices sharing private IP addresses to access the internet through a single public IP address. It is the reason IPv4 still works despite address exhaustion — without NAT, every device would need its own public IP.

**How NAT works — step by step:**

```
                       Public Internet
                              │
           ┌──────────────────┴─────────────────┐
           │          ISP Modem/Router          │
           │ Public IP: 203.0.113.5 (example)   │
           │        LAN IP: 192.168.2.1         │
           └──────────────────┬─────────────────┘
                              │ NAT here
              ┌───────────────┼───────────────┐
              │               │               │
        192.168.2.59     192.168.2.5    192.168.2.10
         (Pi router)      (Laptop)        (Phone)
```

1. **Outbound packet** — your laptop (`192.168.2.5`) sends a request to `142.250.185.110` (Google):
    ```
    Source: 192.168.2.5:43210  →  Destination: 142.250.185.110:443
    ```

2. **NAT translation** — the router replaces the private source IP and port with its own public IP and a unique port, and records the mapping in its **NAT table** (also called the connection tracking table):
    ```
    Source: 203.0.113.5:50001  →  Destination: 142.250.185.110:443
    NAT table entry: 203.0.113.5:50001 ↔ 192.168.2.5:43210
    ```

3. **Google responds** — the reply comes back to the router's public IP and mapped port:
    ```
    Source: 142.250.185.110:443  →  Destination: 203.0.113.5:50001
    ```

4. **Reverse translation** — the router looks up port `50001` in its NAT table, finds it maps to `192.168.2.5:43210`, rewrites the destination, and forwards the packet to the laptop:
    ```
    Source: 142.250.185.110:443  →  Destination: 192.168.2.5:43210
    ```

The laptop never sees the public IP — it only knows its private address. Google never sees the private IP — it only knows the router's public address. The router silently translates between the two worlds.

**Types of NAT:**

| Type | Also Known As | Description |
|------|---------------|-------------|
| **SNAT** (Source NAT) | Masquerading | Rewrites the *source* IP on outbound packets. This is what home routers do — all LAN devices appear to use the router's public IP. Called "masquerading" in Linux (`iptables -t nat -A POSTROUTING -j MASQUERADE`) because the private IPs are "masquerading" behind the public one. |
| **DNAT** (Destination NAT) | Port forwarding | Rewrites the *destination* IP on inbound packets. Used to expose an internal service to the internet — e.g. forwarding port `8080` on the public IP to `192.168.2.59:80` on the Pi. Configured in the modem's admin page as "port forwarding". |
| **PAT** (Port Address Translation) | NAT overload | A form of SNAT where multiple internal connections are distinguished by assigning different source *ports* on the public IP. This is what almost all home NAT does — one public IP, thousands of simultaneous connections, each mapped to a unique port. |
| **1:1 NAT** | Static NAT | Maps one public IP to one private IP, bidirectionally. Uncommon in home networks; used in data centres where each server needs its own public IP. |

**NAT table (connection tracking):** The router maintains a table of active translations. On Linux, this is managed by `conntrack` (part of netfilter/iptables):

```bash
# View active NAT/connection tracking entries on the Pi router:
sudo conntrack -L
# Or check the count:
sudo conntrack -C
# Each entry tracks: protocol, source IP:port, destination IP:port, translated IP:port, state, timeout
```

**Why NAT is both a solution and a problem:**

| Advantage | Disadvantage |
|-----------|--------------|
| Conserves IPv4 addresses — millions of devices share one public IP | Breaks the end-to-end principle — devices behind NAT cannot be directly reached from the internet |
| Provides implicit security — unsolicited inbound traffic is dropped because there is no NAT mapping for it | Complicates protocols that embed IP addresses in payloads (SIP, FTP active mode, some games) — requires ALGs (Application Layer Gateways) to rewrite them |
| Simple to set up — every home router does it automatically | Makes peer-to-peer communication harder — two NATed devices cannot easily connect directly (requires STUN/TURN/ICE hole-punching techniques) |
| | Double/triple NAT (ISP CGNAT + modem NAT + lab router NAT) multiplies these problems |

### IPv6

IPv6 is the successor to IPv4, designed primarily to solve address exhaustion. It uses 128-bit addresses, providing $2^{128}$ ≈ 340 undecillion (3.4 × 10³⁸) addresses — enough to assign a unique public IP to every device on every network on Earth, many times over. This is such an enormous space that NAT is no longer needed.

**Format:** Eight groups of four hexadecimal digits, separated by colons:

```
2001:0db8:85a3:0000:0000:8a2e:0370:7334
```

**Abbreviation rules (RFC 5952):** IPv6 addresses are long, so there are rules to shorten them:

1. **Leading zeros** within each group can be dropped:
    ```
    2001:0db8:85a3:0000:0000:8a2e:0370:7334
    → 2001:db8:85a3:0:0:8a2e:370:7334
    ```

2. **One consecutive run** of all-zero groups can be replaced with `::` (only once per address):
    ```
    2001:db8:85a3:0:0:8a2e:370:7334
    → 2001:db8:85a3::8a2e:370:7334
    ```

3. **Full compression examples:**
    ```
    Full:        2001:0db8:0000:0000:0000:0000:0000:0001
    Shortened:   2001:db8::1

    Loopback:    0000:0000:0000:0000:0000:0000:0000:0001
    Shortened:   ::1

    Unspecified: 0000:0000:0000:0000:0000:0000:0000:0000
    Shortened:   ::
    ```

**IPv6 address structure:** Unlike IPv4 where the network/host split is defined by the subnet mask, IPv6 addresses have a standardised structure:

```
|← ────── 64 bits ────── →|← ────── 64 bits ────── →|
|     Network Prefix      |      Interface ID      |
|   (assigned by ISP/     |   (derived from MAC    |
|    router/RA)           |    via EUI-64 or       |
|                         |    randomly generated) |

Example:  2001:db8:1234:5678 : abcd:ef01:2345:6789
          ──── prefix ─────    ── interface ID ───
```

The first 64 bits identify the network (the "prefix"), the last 64 bits identify the device on that network (the "interface identifier"). ISPs typically assign a `/48` or `/56` prefix to customers, who then subnet it into `/64` networks — each `/64` supports $2^{64}$ ≈ 18.4 quintillion devices.

#### IPv6 address types:

| Type | Prefix | Scope | Example | Description |
|------|--------|-------|---------|-------------|
| **Global Unicast (GUA)** | `2000::/3` (starts with `2` or `3`) | Internet-routable | `2a02:a44a:8185:1::1` | The IPv6 equivalent of a public IPv4 address. Globally unique and directly reachable from anywhere on the internet. Every device gets one (or more). |
| **Link-Local** | `fe80::/10` | Single link only | `fe80::1d9f:d306:dbe6:f1db` | Auto-configured on every interface. Not routable — only valid on the local network segment. Used for neighbour discovery, router advertisements, and local communication. Always present, even without a router or DHCP. |
| **Unique Local (ULA)** | `fd00::/8` | Private networks | `fd12:3456:789a::1` | The IPv6 equivalent of RFC 1918 private addresses. Not routable on the internet. Useful for internal-only services that should never be reached from outside. |
| **Loopback** | `::1/128` | Host only | `::1` | Same as `127.0.0.1` in IPv4 — the machine talking to itself. |
| **Multicast** | `ff00::/8` | Varies | `ff02::1` (all nodes) | Replaces IPv4 broadcast. `ff02::1` = all nodes on the link; `ff02::2` = all routers on the link. |

> **Note:** There is no broadcast in IPv6. IPv4 uses broadcast (`255.255.255.255` or subnet broadcast like `192.168.2.255`) to reach all devices on a network. IPv6 replaces this entirely with multicast — targeted group communication that is more efficient and does not disturb devices that are not interested.

#### IPv6 does not need NAT — and why that matters:

This is the most important conceptual difference between IPv4 and IPv6:

| | IPv4 | IPv6 |
|-|------|------|
| **Address space** | 4.3 billion total (not enough) | 340 undecillion (effectively unlimited) |
| **NAT required?** | Yes — private addresses + NAT to share one public IP | No — every device gets its own globally unique public address |
| **Device reachability** | Hidden behind NAT; not directly reachable from internet | Directly reachable from internet (firewall is what provides security, not NAT) |
| **Security model** | NAT provides "accidental" security by hiding devices | Firewall provides intentional security; devices are visible but protected by rules |
| **End-to-end connectivity** | Broken by NAT — two devices behind different NATs cannot easily connect directly | Restored — any device can connect to any other device (if firewalls allow it) |
| **Port forwarding** | Required to expose services behind NAT | Not needed — services are directly reachable (firewall opens/closes ports) |

With IPv6, your ISP assigns your home network a prefix (e.g. `/56`), and every device on your network gets its own globally routable address. Your laptop, phone, Pi, Proxmox hosts — they all have public IPv6 addresses that are, in principle, directly reachable from anywhere on the internet. **Security is provided by the firewall, not by NAT.** The ISP modem's firewall (and the Pi router's firewall, in the lab) blocks unsolicited inbound IPv6 traffic by default — the same stateful firewall rules that exist for IPv4, just without the NAT translation step.

```
IPv4 (with NAT):
    Internet ← NAT → Private IP (192.168.2.5)
    Internet only sees: 203.0.113.5 (the router's public IP)
    Laptop is hidden; needs port forwarding to be reached

IPv6 (no NAT):
    Internet ←── Firewall ──→ Public IP (2a02:a44a:8185:1::5)
    Internet can see the laptop's real address
    Firewall blocks unsolicited inbound; allows outbound + replies
    No translation needed — the address is the same end-to-end
```

#### How IPv6 address assignment works:

IPv6 devices get their addresses differently from IPv4. There are two main mechanisms:

1. **SLAAC (Stateless Address Autoconfiguration):**
   - The router sends **Router Advertisements (RA)** via ICMPv6, announcing the network prefix (e.g. `2a02:a44a:8185:1::/64`), the default gateway, and other parameters.
   - Each device generates its own interface ID (the last 64 bits) either from its MAC address (EUI-64) or randomly (privacy extensions — see below), and combines it with the prefix to form a complete address.
   - "Stateless" means the router does not track which addresses have been assigned — each device picks its own.
   - This is the most common method on home and small networks. No DHCP server needed for address assignment.

2. **DHCPv6 (Stateful):**
   - Works similarly to DHCPv4 — a server assigns specific addresses and tracks leases.
   - Can provide additional configuration that SLAAC cannot: DNS server addresses (though RA can also do this via RDNSS), NTP servers, domain search lists.
   - Used more in enterprise environments where administrators need full control over address assignment.
   - Can run alongside SLAAC — the RA tells devices whether to use DHCPv6 for addresses, for extra configuration, or both.

**IPv6 privacy extensions (RFC 8981):**

With SLAAC using EUI-64, the interface ID is derived from the device's MAC address — which is a fixed hardware identifier. This means your device's IPv6 address is stable and traceable across networks: wherever you connect, the last 64 bits are the same, and they reveal your hardware identity. Privacy extensions solve this by generating a **random, temporary interface ID** that changes periodically (typically every 24 hours). Most modern operating systems enable privacy extensions by default.

```
Without privacy extensions (EUI-64):
    MAC:  88:a2:9e:98:97:1e
    IPv6: 2a02:a44a:8185:1:8aa2:9eff:fe98:971e   ← MAC embedded, stable, trackable

With privacy extensions:
    IPv6: 2a02:a44a:8185:1:a1b2:c3d4:e5f6:7890   ← random, changes periodically
```

```bash
# Check IPv6 privacy extensions on Linux:
sysctl net.ipv6.conf.eth0.use_tempaddr
# 0 = disabled; 2 = enabled (prefer temporary addresses); 1 = enabled but prefer stable

# Check current IPv6 addresses (look for "temporary" or "mngtmpaddr"):
ip -6 addr show eth0
# You may see multiple IPv6 addresses: a stable one (EUI-64 or stable-privacy) and
# one or more temporary ones (privacy extensions).
```

**IPv6 on Linux — key commands:**

```bash
# Show IPv6 addresses for all interfaces:
ip -6 addr show

# Show only global (internet-routable) IPv6 addresses:
ip -6 addr show scope global

# Show the IPv6 routing table:
ip -6 route show

# Show the IPv6 default gateway:
ip -6 route show default

# Ping an IPv6 address:
ping6 2001:db8::1
# Or on modern systems:
ping -6 2001:db8::1

# Ping a link-local address (must specify the interface with %):
ping6 fe80::1%eth0

# Check IPv6 neighbour table (equivalent of ARP for IPv6, uses NDP):
ip -6 neigh show

# DNS lookup for IPv6 (AAAA record):
dig google.com AAAA +short

# Test IPv6 connectivity to the internet:
ping6 2001:4860:4860::8888    # Google's public IPv6 DNS server
curl -6 ifconfig.me            # WARNING: shows your public IPv6 — do not put this in docs!
```

> **Note:** IPv6 uses NDP (Neighbour Discovery Protocol) instead of ARP. NDP runs over ICMPv6 and handles address resolution (who has this IPv6?), router discovery (where is the gateway?), and duplicate address detection. The `ip -6 neigh` command shows the NDP neighbour table, which is the IPv6 equivalent of the ARP table shown by `ip neigh`.

**Dual-stack:** Most networks today run IPv4 and IPv6 simultaneously — this is called "dual-stack". Each interface has both an IPv4 address and one or more IPv6 addresses. The OS decides which protocol to use for each connection (preferring IPv6 when available, per RFC 6724 "Happy Eyeballs"). The homelab currently uses IPv4 only for internal addressing (`10.42.0.0/20`), but the ISP modem likely provides IPv6 connectivity to the internet, which lab devices may use for outbound traffic via the Pi router (if IPv6 forwarding is enabled).

---

## Subnets

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
    | `/20` | `255.255.240.0`   | 4,094        | `10.42.0.1` – `10.42.15.254`            | Used for a homelab lab network for example         |
    | `/22` | `255.255.252.0`   | 1,022        | `10.42.8.1` – `10.42.11.254`            | Spans 4 "class C" blocks; used for medium LANs     |
    | `/24` | `255.255.255.0`   | 254          | `192.168.2.1` – `192.168.2.254`         | Most common home/office subnet                     |
    | `/26` | `255.255.255.192` | 62           | `10.42.10.1` – `10.42.10.62`            | Quarter of a /24; used to carve up a single block  |
    | `/30` | `255.255.255.252` | 2            | `10.0.0.1` – `10.0.0.2`                 | Point-to-point links (e.g. router–router)          |
    | `/32` | `255.255.255.255` | 0 (1 host)   | just that one IP                        | Single host route                                  |

    Formula: usable hosts = $2^{(32 - \text{prefix})} - 2$ (subtract 2: one for the network address, one for the broadcast address).

- **Network address and broadcast address:** For any subnet, the first address is the *network address* (identifies the subnet itself, not assignable to a host) and the last address is the *broadcast address* (sends to all hosts in the subnet, not assignable). Everything in between is usable.

    > **Note:** This applies to IPv4 only. IPv6 has no broadcast address — it uses multicast instead. In IPv6, the first address of a subnet (e.g. `2a02:a44a:8185:1::/64`) is the "subnet-router anycast address" (used to reach any router on that subnet), and all other addresses in the range are usable. There is no "last address reserved for broadcast" concept.
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

- **IPv6 subnets — separate table:** IPv6 subnets work differently from IPv4 in a few important ways. IPv6 addresses are 128 bits (not 32), there are no subnet masks in dotted-decimal form (only prefix lengths), and the standard subnet size for a LAN is always `/64` — regardless of how many devices are on it. IPv6 also has no broadcast address, so the formula is different: usable addresses = $2^{(128 - \text{prefix})}$ (no subtraction needed). ISPs assign prefixes to customers (typically `/48` or `/56`), who then carve them into `/64` networks. The prefix hierarchy looks like this:

    | CIDR   | Addresses | Typical Use | Notes |
    |--------|-----------|-------------|-------|
    | `/32`  | $2^{96}$ = 79,228,162,514,264,337,593,543,950,336 (≈ 79.2 × 10²⁷) | ISP allocation from regional registry (RIR) | A single ISP receives this block and assigns sub-prefixes to customers |
    | `/48`  | $2^{80}$ = 1,208,925,819,614,629,174,706,176 (≈ 1.2 × 10²⁴) | Site allocation — assigned to a large customer or organisation | Can be subnetted into 65,536 × `/64` networks |
    | `/56`  | $2^{72}$ = 4,722,366,482,869,645,213,696 (≈ 4.7 × 10²¹) | Residential customer allocation — assigned by ISP to a home connection | Can be subnetted into 256 × `/64` networks — plenty for a homelab |
    | `/64`  | $2^{64}$ = 18,446,744,073,709,551,616 (≈ 18.4 quintillion) | Single LAN subnet — the standard size for every IPv6 network segment | SLAAC requires exactly `/64`; this is the universal LAN prefix length. Never use anything smaller for a LAN. |
    | `/128` | 1 | Single host route — one specific address | Equivalent to IPv4's `/32`; used in routing tables for individual hosts, loopback (`::1/128`) |

    **Why `/64` is always the LAN size:** In IPv4, you choose a subnet size based on how many hosts you need (`/24` for 254, `/20` for 4094, etc.). In IPv6, the LAN size is always `/64` — not because you need $2^{64}$ addresses, but because SLAAC (the standard auto-configuration mechanism) requires it. SLAAC assumes the last 64 bits are the interface identifier and the first 64 bits are the network prefix. If you use a different prefix length (e.g. `/48` or `/96` on a LAN), SLAAC breaks and devices cannot auto-configure. DHCPv6 can technically work with other prefix lengths, but `/64` is the universal convention and deviating from it causes compatibility problems.

    **How IPv6 prefix delegation works (ISP → customer → LANs):**
    ```
    ISP has:        2a02:a44a::/32                   ← ISP's allocation from RIPE
    Assigns to you: 2a02:a44a:8185::/56              ← your home's prefix (256 /64s available)
    Your LANs:
      Home LAN:     2a02:a44a:8185:0001::/64         ← subnet 1
      Lab LAN:      2a02:a44a:8185:0002::/64         ← subnet 2
      IoT VLAN:     2a02:a44a:8185:0003::/64         ← subnet 3
      ...up to:     2a02:a44a:8185:00ff::/64         ← subnet 256
    ```

    **Worked examples (IPv6):**
    - `2a02:a44a:8185:1::1/64` → network `2a02:a44a:8185:1::/64`, hosts `2a02:a44a:8185:1::1` – `2a02:a44a:8185:1:ffff:ffff:ffff:ffff`. This is a global unicast address on a `/64` LAN — the standard configuration.
    - `fe80::1d9f:d306:dbe6:f1db/10` → link-local address. The `/10` prefix means all addresses starting with `fe80` through `febf` are link-local. These are auto-configured on every interface and never routed beyond the local link.
    - `fd12:3456:789a::1/48` → ULA (Unique Local Address) site prefix. Hosts `fd12:3456:789a::1` – `fd12:3456:789a:ffff:ffff:ffff:ffff:ffff`. Used for private internal communication, not routable on the internet. Can be subnetted into 65,536 × `/64` LANs.
    - `::1/128` → the loopback address (IPv6 equivalent of `127.0.0.1`). A `/128` is a single address — the machine talking to itself.

> **Note:** You do not need to calculate all of this by hand. Know the basics (what CIDR means, how to read a subnet mask, roughly how many hosts a prefix gives you), but for anything more precise use an online subnet calculator: [calculator.net](https://www.calculator.net/ip-subnet-calculator.html), [subnet-calculator.com](https://www.subnet-calculator.com/), or [subnet-calculator.nl](https://subnet-calculator.nl/).
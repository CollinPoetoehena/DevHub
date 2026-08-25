# Network Commands

General networking commands with output format explanations. Used for connectivity checks, debugging, and inspecting network configuration.

---

## Table of Contents

- [nmcli connection show](#nmcli-connection-show)
- [ip a](#ip-a-or-ip-addr-or-ip-address)
- [ip r](#ip-r)
- [ping](#ping)
- [traceroute / tracepath — Trace Packet Path](#traceroute--tracepath--trace-packet-path)
- [ip neigh / arp — ARP Neighbour Table](#ip-neigh--arp--arp-neighbour-table)
- [ss — Socket Statistics](#ss--socket-statistics)
- [dig / nslookup — DNS Lookup](#dig--nslookup--dns-lookup)
- [DHCP Client Commands](#dhcp-client-commands)
- [Packet Capture — tcpdump & tshark](#packet-capture--tcpdump--tshark)

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

Example output (router with two Ethernet interfaces):
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

Example output (router):
```
default via 192.168.2.254 dev eth0 proto dhcp src 192.168.2.59 metric 100
192.168.2.0/24 dev eth0 proto kernel scope link src 192.168.2.59 metric 100
10.42.0.0/20 dev eth1 proto kernel scope link src 10.42.0.1 metric 100
```

- `default via 192.168.2.254 dev eth0` — all internet-bound traffic goes to the ISP modem first, then onward.
- `192.168.2.0/24 dev eth0 scope link` — home network hosts are directly reachable via `eth0`; no gateway needed.
- `10.42.0.0/20 dev eth1 scope link` — lab network hosts are directly reachable via `eth1`; no gateway needed.

---

### `ping`

Tests reachability and measures round-trip time to a host by sending ICMP echo requests. `-c <n>` limits the number of packets sent (without it, ping runs until interrupted).

```
ping -c 3 <host>
```

---

### `traceroute` / `tracepath` — Trace Packet Path

Shows the route packets take from your machine to a destination, listing every intermediate hop (router) along the way. Each hop decrements the packet's TTL (Time To Live) by 1; when TTL reaches 0 the router discards the packet and sends back an ICMP "Time Exceeded" message — this is how traceroute discovers each hop.

Use it to find where packets are being dropped, which path traffic takes through the network, or where latency is introduced.

There are two commands: `traceroute` (classic, feature-rich, may need installation) and `tracepath` (simpler, always available on modern Linux, no root required).

#### `traceroute`

**Basic usage:**

```bash
traceroute <host>                      # trace using UDP probes (default on Linux)
traceroute -I <host>                   # use ICMP echo (like ping) instead of UDP
traceroute -T <host>                   # use TCP SYN probes (useful when ICMP is blocked)
traceroute -n <host>                   # numeric output — don't resolve hostnames
traceroute -m <max_ttl> <host>         # set max hops (default: 30)
traceroute -w <seconds> <host>         # timeout per probe (default: 5s)
traceroute -q <n> <host>               # number of probes per hop (default: 3)
traceroute -p <port> <host>            # set destination port (for UDP/TCP probes)
```

**Common flags:**

| Flag | Description |
|------|-------------|
| `-I` | Use ICMP echo requests instead of UDP. Requires root. More likely to get responses from all hops since many routers respond to ICMP. |
| `-T` | Use TCP SYN probes. Useful for tracing to hosts behind firewalls that block UDP/ICMP but allow TCP on common ports (e.g. `-T -p 443`). Requires root. |
| `-n` | Don't resolve IP addresses to hostnames — faster output. |
| `-m <hops>` | Maximum number of hops (TTL) before giving up. Default is 30. |
| `-q <n>` | Number of probe packets per hop. Default is 3 (hence three time values per line). |
| `-w <sec>` | Seconds to wait for a response before printing `*`. Default is 5. |
| `-f <ttl>` | Start at this TTL instead of 1 (skip the first N-1 hops). |
| `-p <port>` | Destination port for UDP or TCP probes. |

**Output format:**

Each line represents one hop (router) along the path:

```
<hop>  <hostname> (<ip>)  <rtt1> ms  <rtt2> ms  <rtt3> ms
```

| Field | Description |
|-------|-------------|
| `<hop>` | Hop number (TTL value that reached this router). |
| `<hostname>` | Reverse DNS name of the router (or just the IP if `-n` is used or reverse DNS fails). |
| `<ip>` | IP address of the router interface that sent the ICMP reply. |
| `<rtt>` | Round-trip time for each probe packet. Three values by default (one per probe). |
| `*` | No response received within the timeout — the router either dropped the probe, is configured not to reply, or is behind a firewall. |
| `!H` | Host unreachable. |
| `!N` | Network unreachable. |
| `!X` | Communication administratively prohibited (firewall). |
| `!P` | Protocol unreachable. |

**Example — trace to an external host:**

```
poetoec@lab-router:~ $ traceroute -n 8.8.8.8
traceroute to 8.8.8.8 (8.8.8.8), 30 hops max, 60 byte packets
 1  192.168.2.254  1.234 ms  1.112 ms  1.098 ms
 2  10.0.0.1  8.456 ms  8.321 ms  8.298 ms
 3  172.16.50.1  12.789 ms  12.654 ms  12.601 ms
 4  * * *
 5  108.170.241.1  14.123 ms  14.067 ms  13.998 ms
 6  8.8.8.8  13.456 ms  13.321 ms  13.289 ms
```

- Hop 1: `192.168.2.254` — the ISP modem (first gateway from `ip r`).
- Hop 2–3: ISP internal routers.
- Hop 4: `* * *` — a router that does not respond to probes (common — many ISP/backbone routers disable ICMP replies). This does not mean the path is broken; it just means that router is silent.
- Hop 5–6: Google's network; final hop is the destination `8.8.8.8`.

**Example — trace within the lab network:**

```
poetoec@proxmox-node1:~ $ traceroute -n 192.168.2.5
traceroute to 192.168.2.5 (192.168.2.5), 30 hops max, 60 byte packets
 1  10.42.0.1  2.456 ms  2.321 ms  2.298 ms
 2  192.168.2.5  3.789 ms  3.654 ms  3.601 ms
```

- Hop 1: `10.42.0.1` — the lab router (default gateway for the lab subnet).
- Hop 2: `192.168.2.5` — the destination on the home network, reached via the router.

**Interpreting problems:**

| Symptom | Meaning |
|---------|---------|
| All hops respond, latency increases gradually | Normal — each hop adds some delay. |
| `* * *` for one hop, then continues | That router silently forwards but does not reply to TTL-exceeded — not a problem. |
| `* * *` for all remaining hops | Traffic is being dropped at or after the last responding hop — check firewall rules or routing. |
| Sudden large latency jump at one hop | That link is congested or geographically distant. |
| `!H` or `!N` at a hop | The router at that hop has no route to the destination — routing misconfiguration. |
| Loop (same IPs repeating) | Routing loop — two routers are bouncing packets between each other. |

#### `tracepath`

`tracepath` is a simpler alternative that comes pre-installed on most Linux distributions. It does not require root, uses UDP probes, and also discovers the Path MTU (maximum packet size that can traverse the entire path without fragmentation).

```bash
tracepath <host>                       # trace with automatic PMTU discovery
tracepath -n <host>                    # numeric output
tracepath -b <host>                    # show both hostname and IP
tracepath -m <max_hops> <host>         # set max hops (default: 30)
```

**Example:**

```
poetoec@lab-router:~ $ tracepath -n 8.8.8.8
 1?: [LOCALHOST]                        pmtu 1500
 1:  192.168.2.254                        1.234ms
 1:  192.168.2.254                        1.112ms
 2:  10.0.0.1                             8.456ms asymm  3
 3:  172.16.50.1                          12.789ms reached
     Resume: pmtu 1500 hops 3 back 3
```

- `pmtu 1500` — Path MTU is 1500 bytes (standard Ethernet, no fragmentation needed).
- `asymm 3` — asymmetric routing: the return path has a different hop count (3) than the forward path at this point. Not necessarily a problem, but worth noting.
- `reached` — destination was reached.

#### When to use which

| Tool | Best for |
|------|----------|
| `traceroute -n` | Quick path check with numeric output. |
| `traceroute -I` | When UDP probes get no response but ICMP might work. |
| `traceroute -T -p 443` | Tracing through firewalls that only allow TCP on well-known ports. |
| `tracepath` | No-root quick trace with Path MTU discovery. |

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
> No entry for `10.42.0.168` yet — the router has not talked to it. After pinging:
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
- If a device shows `FAILED`, the router sent an ARP request but got no reply — the device is off, not connected, or there is a cabling/VLAN issue.

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

**What is a socket?** A socket is one endpoint of a network connection — the combination of an **IP address** and a **port number** (e.g. `10.42.0.1:53`). When a program wants to communicate over the network, it creates a socket and either *listens* on it (server: "I'm accepting connections on this IP:port") or *connects* to a remote socket (client: "I want to talk to that IP:port"). Every network connection has two sockets — one on each end. A listening socket (e.g. `0.0.0.0:22` for SSH) is a server waiting for incoming connections; an established socket (e.g. `10.42.0.1:22 ↔ 192.168.2.5:43210`) is an active connection between two endpoints. The OS tracks all sockets in a table — `ss` reads and displays that table.

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

Example output (router running dnsmasq and SSH):
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

Commands for inspecting and managing DHCP leases from the **client** side (the device requesting an IP, such as a VM). For server-side DHCP management (lease files, reservations, debugging, etc.), see the [dnsmasq reference](dnsmasq.md#commands-dhcp).

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

### Packet Capture — `tcpdump` & `tshark`

Tools for capturing and inspecting network packets in real time. Essential for debugging DHCP, DNS, firewall, and routing issues — they show you exactly what is going on the wire.

| Tool | What it is | Best for |
|------|-----------|----------|
| `tcpdump` | Lightweight CLI packet capture tool, available on virtually every Linux system. | Quick captures, minimal environments, writing `.pcap` files. |
| `tshark` | CLI version of Wireshark — uses the same dissectors and display filters. | Deep protocol inspection, decoding complex protocols, reading `.pcap` files with rich detail. |

Both require `sudo` because they put the network interface into promiscuous mode.

#### `tcpdump`

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

#### `tshark`

[`tshark`](https://tshark.dev/) is the command-line interface to Wireshark. It uses the same protocol dissectors, so it can decode and display protocol fields that tcpdump cannot (e.g. DHCP option names, DNS record details, HTTP headers, TLS handshake parameters). Install with `sudo apt install tshark`.

**Basic usage:**

```bash
sudo tshark -i <interface>                           # capture all traffic on an interface
sudo tshark -i eth0 -f "port 53"                     # capture filter (BPF syntax, same as tcpdump)
sudo tshark -i eth0 -Y "dns"                         # display filter (Wireshark syntax, applied after capture)
sudo tshark -i eth0 -c 10                            # capture only 10 packets then stop
sudo tshark -i eth0 -w /tmp/capture.pcap             # write to file (same .pcap format as tcpdump)
sudo tshark -r /tmp/capture.pcap                     # read and display a capture file
sudo tshark -r /tmp/capture.pcap -Y "dhcp"           # read file, show only DHCP packets
```

**Capture filters vs display filters:**

| Type | Flag | Syntax | When applied | Example |
|------|------|--------|-------------|--------|
| Capture filter | `-f` | BPF (same as tcpdump) | During capture — packets not matching are discarded | `-f "port 67 or port 68"` |
| Display filter | `-Y` | Wireshark display filter | After capture — all packets are captured, only matching ones are shown | `-Y "dhcp.option.type == 53"` |

Capture filters are faster (kernel-level filtering), but display filters are more powerful (can filter on decoded protocol fields). Use capture filters to limit volume, display filters to drill down.

**Common flags:**

| Flag | Description |
|------|-------------|
| `-i <iface>` | Interface to capture on. `-i any` for all interfaces. |
| `-f "<filter>"` | Capture filter (BPF syntax). |
| `-Y "<filter>"` | Display filter (Wireshark syntax). |
| `-c <count>` | Stop after `<count>` packets. |
| `-n` | Don't resolve IP addresses to hostnames. |
| `-V` | Verbose — show full protocol tree for each packet (very detailed). |
| `-T fields -e <field>` | Output specific fields only (useful for scripting). |
| `-w <file>` | Write raw packets to `.pcap` file. |
| `-r <file>` | Read from a `.pcap` file. |
| `-q` | Quiet — suppress per-packet output (useful with `-z` statistics). |
| `-z <stat>` | Show statistics (e.g. `-z io,stat,1` for per-second I/O stats). |

**Example — decode DHCP traffic with option names:**

```bash
sudo tshark -i eth1 -f "port 67 or port 68" -V
```

Unlike tcpdump which shows raw `BOOTP/DHCP`, tshark decodes every DHCP option by name:
```
Dynamic Host Configuration Protocol (Discover)
    Message type: Boot Request (1)
    Client MAC address: 28:94:01:8a:ec:28
    Option: (53) DHCP Message Type (Discover)
    Option: (61) Client identifier
    Option: (50) Requested IP Address (10.42.0.168)
    Option: (12) Host Name: proxmox-node1
```

**Example — extract specific fields (scripting-friendly):**

```bash
# Show source IP, destination IP, and DNS query name for all DNS traffic:
sudo tshark -i eth0 -f "port 53" -T fields -e ip.src -e ip.dst -e dns.qry.name
```

Output:
```
10.42.0.168	10.42.0.1	google.com
10.42.0.1	10.42.0.168	google.com
```

**Example — read a tcpdump capture with richer decoding:**

```bash
# Capture with tcpdump (lightweight, always available):
sudo tcpdump -i eth0 -n -w /tmp/debug.pcap

# Analyze with tshark (rich protocol decoding):
tshark -r /tmp/debug.pcap -Y "dns.flags.rcode != 0"   # show only failed DNS queries
tshark -r /tmp/debug.pcap -Y "dhcp.option.dhcp == 5"   # show only DHCP ACKs
```

This is a common workflow: capture with tcpdump on a minimal system (always installed), then analyze with tshark or Wireshark on a machine with the tools installed.

**Useful display filters:**

| Filter | Description |
|--------|-------------|
| `dns` | All DNS traffic |
| `dhcp` | All DHCP traffic |
| `arp` | All ARP traffic |
| `icmp` | All ICMP (ping) traffic |
| `tcp.port == 22` | SSH traffic |
| `ip.addr == 10.42.0.1` | Traffic to/from a specific IP |
| `dns.qry.name contains "google"` | DNS queries containing "google" |
| `dhcp.option.dhcp == 1` | DHCP Discover messages only |
| `dhcp.option.dhcp == 5` | DHCP ACK messages only |
| `dns.flags.rcode != 0` | Failed DNS queries (NXDOMAIN, SERVFAIL, etc.) |
| `http.request` | HTTP requests only |
| `tcp.flags.syn == 1 && tcp.flags.ack == 0` | TCP SYN packets (new connection attempts) |

**Useful recipes:**

| Purpose | Command |
|---------|---------|
| Debug DHCP with full decode | `sudo tshark -i eth1 -f "port 67 or port 68" -V` |
| Debug DNS queries | `sudo tshark -i eth0 -Y "dns.flags.response == 0"` |
| Show only failed DNS | `sudo tshark -i eth0 -Y "dns.flags.rcode != 0"` |
| List all DHCP leases being handed out | `sudo tshark -i eth1 -Y "dhcp.option.dhcp == 5" -T fields -e dhcp.ip.your -e dhcp.hw.mac_addr` |
| Per-second packet rate | `sudo tshark -i eth0 -q -z io,stat,1` |
| Analyze a pcap from tcpdump | `tshark -r capture.pcap -Y "<filter>"` |

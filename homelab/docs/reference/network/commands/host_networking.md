# Host Networking

Commands for inspecting a host's network configuration (interfaces, addresses, routes, neighbours, listening ports) and testing connectivity to other hosts. These are the day-to-day commands for answering "what's my network state?", "can I reach that host?", and "what's listening on this machine?".

---

## Table of Contents

- [nmcli connection show](#nmcli-connection-show)
- [ip a](#ip-a-or-ip-addr-or-ip-address)
- [ip r](#ip-r)
- [ip neigh / arp — ARP Neighbour Table](#ip-neigh--arp--arp-neighbour-table)
- [ping](#ping)
- [traceroute / tracepath — Trace Packet Path](#traceroute--tracepath--trace-packet-path)
- [nc — Netcat](#nc--netcat)
- [ss — Socket Statistics](#ss--socket-statistics)

---

## `nmcli connection show`

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

## `ip a` (or `ip addr` or `ip address`)

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

## `ip r`

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

## `ip neigh` / `arp` — ARP Neighbour Table

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

### IPs only: `ip neigh` and `arp -n`

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

### With hostnames: `arp -a` and `ip neigh` + reverse DNS

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

## `ping`

Tests reachability and measures round-trip time to a host by sending ICMP echo requests. Sends an ICMP Echo Request packet; if the host is reachable and not blocking ICMP, it replies with an ICMP Echo Reply. `-c <n>` limits the number of packets sent (without it, ping runs until interrupted with Ctrl+C).

**Basic usage:**

```bash
ping -c 3 <host>                       # send 3 packets then stop
ping -c 3 -W 2 <host>                  # 2-second timeout per packet (useful for slow links)
ping -i 0.2 <host>                     # send packets every 0.2s instead of default 1s
ping -s 1472 -M do <host>              # test MTU — send 1472-byte payload (1500 with headers), don't fragment
ping -I eth1 <host>                    # force ping out of a specific interface
ping -n <host>                         # numeric output — don't resolve hostnames
ping6 <host>                           # IPv6 ping (or `ping -6 <host>` on most modern systems)
```

> **IPv4 vs IPv6:** On most modern Linux systems, `ping` auto-detects the address family — `ping <ipv6-addr>` just works. On older systems, use `ping6` or `ping -6` explicitly for IPv6 targets. All flags below work the same for both.

**Common flags:**

| Flag | Description |
|------|-------------|
| `-c <count>` | Stop after sending `<count>` packets. Without this, ping runs forever. |
| `-W <seconds>` | Timeout waiting for each reply (default varies by OS, usually ~1-10s). |
| `-i <interval>` | Seconds between packets (default: 1). Values below 0.2 require root. |
| `-s <size>` | Payload size in bytes (default: 56, resulting in 64-byte ICMP packet with 8-byte header). |
| `-M do` | Set Don't Fragment bit — useful for MTU path discovery. |
| `-I <iface>` | Bind to a specific interface (useful on multi-homed hosts like the lab router). |
| `-n` | Numeric output — don't reverse-DNS the reply IP. |
| `-q` | Quiet — only show summary at the end. |
| `-f` | Flood ping — send packets as fast as possible (requires root). Use with `-c` to avoid overload. |

**Output format:**

```
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=118 time=5.23 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=118 time=5.11 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=118 time=5.08 ms

--- 8.8.8.8 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 5.080/5.140/5.230/0.064 ms
```

**Key fields:**

| Field | Description |
|-------|-------------|
| `64 bytes` | Reply size (56-byte payload + 8-byte ICMP header) |
| `icmp_seq` | Sequence number — sequential; gaps mean dropped packets |
| `ttl` | Time To Live remaining in the reply — starts at the remote host's initial TTL (usually 64 or 128) and decrements per hop; useful for estimating hop count (`64 - ttl` or `128 - ttl`) |
| `time` | Round-trip time in milliseconds |
| `packet loss` | Percentage of packets that got no reply — 0% is ideal |
| `rtt min/avg/max/mdev` | Latency statistics — `mdev` is the standard deviation (jitter) |

**Interpreting results:**

| Result | Meaning |
|--------|---------|
| Replies with low consistent `time` | Host reachable, network healthy. |
| High `time` values | Network congestion or geographically distant host. |
| Intermittent replies (some `icmp_seq` missing) | Packet loss — congestion, flaky link, or rate limiting. |
| `Destination Host Unreachable` | A router on the path has no route to the destination. |
| `Destination Net Unreachable` | No route to the destination network. |
| `Request timeout` / no output | Host is down, ICMP is firewalled, or no route exists. |
| `time` values with high `mdev` (jitter) | Unstable link — buffering, WiFi interference, or congestion. |

---

## `traceroute` / `tracepath` — Trace Packet Path

Shows the route packets take from your machine to a destination, listing every intermediate hop (router) along the way. Each hop decrements the packet's TTL (Time To Live) by 1; when TTL reaches 0 the router discards the packet and sends back an ICMP "Time Exceeded" message — this is how traceroute discovers each hop.

Use it to find where packets are being dropped, which path traffic takes through the network, or where latency is introduced.

There are two commands: `traceroute` (classic, feature-rich, may need installation) and `tracepath` (simpler, always available on modern Linux, no root required).

### `traceroute`

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

- Hop 1: `10.42.0.1` — the router (default gateway for the lab subnet for the homelab for example).
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

### `tracepath`

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

### When to use which

| Tool | Best for |
|------|----------|
| `traceroute -n` | Quick path check with numeric output. |
| `traceroute -I` | When UDP probes get no response but ICMP might work. |
| `traceroute -T -p 443` | Tracing through firewalls that only allow TCP on well-known ports. |
| `tracepath` | No-root quick trace with Path MTU discovery. |

---

## `nc` — Netcat

`nc` (netcat) is a versatile networking utility for reading and writing data across TCP and UDP connections. Often called the "Swiss army knife" of networking — use it to test whether a port is open, send/receive data over a connection, or set up a simple listener. Available as `nc`, `ncat` (from Nmap), or `netcat` depending on the distribution.

**Basic usage:**

```bash
nc -zv <host> <port>                                 # test if a single TCP port is open
nc -zv -w 2 <host> <port>                            # test with 2-second timeout
nc -u -zv <host> <port>                              # test a UDP port
nc -zv <host> 8000-9000                              # scan a port range (OpenBSD netcat only, ncat does not support this)
nc -6 -zv <ipv6-host> <port>                         # test an IPv6 host

# test multiple ports (ncat only accepts one port at a time), such as common protocols (HTTP (80), HTTPS (443), DNS (53), SSH (22)):
PORTS="80 443 53 22"; for p in $PORTS; do nc -zv -w 2 <host> "$p"; done
```

**Common flags:**

| Flag | Description |
|------|-------------|
| `-z` | Zero-I/O mode — just test the connection, don't send data. Used for port scanning/probing. |
| `-v` | Verbose — print whether the connection succeeded or failed. Without this, `nc` is silent on success. |
| `-w <seconds>` | Timeout — give up after `<seconds>` if no connection is established. Essential for probing hosts that silently drop traffic. |
| `-u` | Use UDP instead of TCP. |
| `-6` | Force IPv6. Required by some implementations when connecting to IPv6 addresses. |
| `-l` | Listen mode — act as a server, waiting for incoming connections on the specified port. |
| `-p <port>` | Specify the source port (when connecting) or the listen port (some implementations). |
| `-k` | Keep listening — accept multiple connections (with `-l`). Without this, the listener exits after the first connection closes. |
| `-n` | Numeric only — don't resolve hostnames via DNS. |

**Output format (port probing with `-zv`):**

```
Connection to 10.42.0.1 22 port [tcp/ssh] succeeded!
Connection to 10.42.0.1 80 port [tcp/http] refused!
nc: connect to 10.42.0.1 port 443 (tcp) timed out: Operation now in progress
```

**Interpreting results:**

| Result | Meaning |
|--------|----------|
| `succeeded` | Port is open — a service is listening and accepted the TCP handshake. |
| `refused` (or `Connection refused`) | Host is reachable but nothing is listening on that port — the OS sent a TCP RST. |
| `timed out` | No response — the host is down, the port is firewalled (silently dropped), or there is no route. |
| `Network is unreachable` | No route to the destination. |

> **`refused` vs `timed out`:** "Connection refused" actually confirms the host is alive and reachable — it just means no service is running on that port. "Timed out" is more ambiguous — could be a firewall, a down host, or a routing issue.

**Examples — common use cases:**

```bash
# Test if SSH is reachable on a host
nc -zv -w 2 10.42.0.168 22

# Test if a web server is running
nc -zv -w 2 10.42.0.168 80 443

# Test if BGP port is open on a router
nc -zv -w 2 10.42.0.1 179

# Test if DNS is reachable on UDP
nc -u -zv -w 2 10.42.0.1 53

# Simple connectivity test between two machines:
# On the listener (machine A):
nc -l 12345
# On the sender (machine B):
echo "hello" | nc <machine-A-ip> 12345

# Transfer a file (quick and dirty, no encryption):
# Receiver:
nc -l 12345 > received_file.txt
# Sender:
nc <receiver-ip> 12345 < file_to_send.txt
```

**Useful recipes:**

| Purpose | Command |
|---------|----------|
| Test a single port | `nc -zv -w 2 <host> <port>` |
| Test multiple ports | `PORTS="80 443 22"; for p in $PORTS; do nc -zv -w 2 <host> "$p"; done` |
| Test UDP port | `nc -u -zv -w 2 <host> 53` |
| Test IPv6 port | `nc -6 -zv -w 2 <ipv6-host> <port>` |
| Quick listener for testing | `nc -l <port>` |
| Persistent listener | `nc -lk <port>` |
| Check if a host is alive (any port) | `PORTS="22 80 443"; for p in $PORTS; do nc -zv -w 2 <host> "$p"; done` |

> **Note:** There are multiple `nc` implementations (`OpenBSD netcat`, `GNU netcat`, `ncat` from Nmap) with slightly different flag support. If a flag does not work, check `nc -h` or `man nc` for your version. On RHEL/CentOS, `ncat` (from the `nmap-ncat` package) is the default.

---

## `ss` — Socket Statistics

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
|---------|----------|
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

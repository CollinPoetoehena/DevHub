# Packet Capture — tcpdump & tshark

Tools for capturing and inspecting network packets in real time. Essential for debugging DHCP, DNS, firewall, and routing issues — they show you exactly what is going on the wire.

| Tool | What it is | Best for |
|------|-----------|----------|
| `tcpdump` | Lightweight CLI packet capture tool, available on virtually every Linux system. | Quick captures, minimal environments, writing `.pcap` files. |
| `tshark` | CLI version of Wireshark — uses the same dissectors and display filters. | Deep protocol inspection, decoding complex protocols, reading `.pcap` files with rich detail. |

Both require `sudo` because they put the network interface into promiscuous mode.

> **WARNING:** `tcpdump` (and `tshark`) can be very resource-intensive. On a busy network, capturing unfiltered traffic can generate enormous volumes of data, potentially overloading the system's CPU, memory, or disk — which in extreme cases can lead to crashes or unresponsive servers. **Always** apply capture filters (e.g. `port 53`, `host 10.42.0.1`) and use `-c <count>` to limit the number of captured packets. Never run an unfiltered, unlimited capture on a production system.

---

## Table of Contents

- [tcpdump](#tcpdump)
- [tshark](#tshark)

---

## `tcpdump`

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

---

## `tshark`

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

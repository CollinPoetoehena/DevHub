# Packet Capture & Analysis — tcpdump, tshark & Wireshark

Tools for capturing, inspecting, and analyzing network packets. Essential for debugging DHCP, DNS, firewall, and routing issues — they show you exactly what is going on the wire.

| Tool | What it is | Best for |
|------|-----------|----------|
| `tcpdump` | Lightweight CLI capture tool, available on virtually every Linux system. | Quick captures, minimal environments, writing `.pcap` files on headless servers. |
| `tshark` | CLI version of Wireshark — same dissectors and display filters. | Deep protocol inspection from the terminal, scripting, reading `.pcap` files with rich detail. |
| Wireshark | Full GUI packet analyzer with colour-coded protocols, stream reassembly, and graphical flow diagrams. | Interactive deep-dive analysis, following TCP streams, visualizing traffic patterns. |

**Common workflow:** Capture with `tcpdump` on a remote/minimal system → transfer the `.pcap` file → analyze with `tshark` or Wireshark on a workstation.

Both `tcpdump` and `tshark` require `sudo` because they put the network interface into promiscuous mode.

> **WARNING:** `tcpdump` (and `tshark`) can be very resource-intensive. On a busy network, capturing unfiltered traffic can generate enormous volumes of data, potentially overloading the system's CPU, memory, or disk — which in extreme cases can lead to crashes or unresponsive servers. **Always** apply capture filters (e.g. `port 53`, `host 10.42.0.1`) and use `-c <count>` to limit the number of captured packets. Never run an unfiltered, unlimited capture on a production system.

---

## Table of Contents

- [tcpdump](#tcpdump)
  - [Basic usage](#basic-usage)
  - [Common flags](#common-flags)
  - [Filter expressions](#filter-expressions)
  - [Output format](#output-format)
  - [Useful recipes](#useful-recipes)
- [tshark](#tshark)
  - [Basic usage](#basic-usage-1)
  - [Capture filters vs display filters](#capture-filters-vs-display-filters)
  - [Common flags](#common-flags-1)
  - [Useful display filters](#useful-display-filters)
  - [Useful recipes](#useful-recipes-1)
- [Wireshark](#wireshark)
  - [Installation](#installation)
  - [Key GUI panels](#key-gui-panels)
  - [Essential Wireshark features](#essential-wireshark-features)
  - [Common Wireshark analysis workflow](#common-wireshark-analysis-workflow)

---

## `tcpdump`

[`tcpdump`](https://www.tcpdump.org/) is the standard command-line packet capture tool on Unix/Linux. It captures packets at the kernel level using BPF (Berkeley Packet Filter) and prints a decoded summary of each packet to the terminal, or writes raw packet data to `.pcap` files for later analysis. Available by default on virtually every Linux distribution — making it the go-to tool for quick captures on servers and embedded devices where installing anything else is impractical.

### Basic usage:

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

### Common flags

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
| `-s <snaplen>` | Capture `<snaplen>` bytes per packet (default: 262144). Use `-s 0` for full packets, `-s 96` for headers only (saves disk on large captures). |
| `-G <seconds>` | Rotate capture file every `<seconds>` seconds (use with `-w` and `%` time format in filename). |
| `-C <filesize>` | Rotate capture file every `<filesize>` MB. |
| `-Z <user>` | Drop privileges to `<user>` after starting capture (security best practice for long-running captures). |

### Filter expressions

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
| `portrange 8000-9000` | Traffic on any port in the range. |
| `len > 1000` | Packets larger than 1000 bytes. |
| `ether host <mac>` | Traffic to/from a specific MAC address. |
| Combine with `and`, `or`, `not` | `host 10.42.0.1 and port 53` = DNS traffic to/from the router (e.g. the lab router). |
| Parentheses for grouping | `(port 67 or port 68) and host 10.42.0.1` |

### Output format

Each line shows one packet:

```
<timestamp> <protocol> <src> > <dst>: <flags> <details>
```

**TCP flag characters:**

| Flag | Description |
|------|-------------|
| `S` | SYN — connection initiation |
| `S.` | SYN-ACK — connection accepted |
| `.` | ACK — acknowledgement |
| `P.` | PSH-ACK — data push |
| `F.` | FIN-ACK — connection close |
| `R` | RST — connection reset (forceful close or rejection) |

Example — TCP handshake:
```
12:00:01.100000 IP 10.42.0.168.43210 > 10.42.0.1.22: Flags [S], seq 123456, win 65535, length 0
12:00:01.100500 IP 10.42.0.1.22 > 10.42.0.168.43210: Flags [S.], seq 789012, ack 123457, win 65535, length 0
12:00:01.101000 IP 10.42.0.168.43210 > 10.42.0.1.22: Flags [.], ack 789013, win 65535, length 0
```

- Line 1: Client sends SYN (connection request) to SSH port 22.
- Line 2: Server replies SYN-ACK (accepts the connection).
- Line 3: Client sends ACK (handshake complete — connection established).

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

- First line: client queries the router's DNS (e.g. the lab router for the homelab) for `google.com` (A record). `+` means recursion desired.
- Second line: server responds with `142.250.185.110`. `1/0/0` = 1 answer, 0 authority, 0 additional records.

### Useful recipes

| Purpose | Command |
|---------|---------|
| Debug DHCP | `sudo tcpdump -i eth0 -n -c 20 port 67 or port 68` |
| Debug DNS | `sudo tcpdump -i eth0 -n -c 50 port 53` |
| Debug ARP | `sudo tcpdump -i eth0 -n -c 20 arp` |
| All traffic to/from a host | `sudo tcpdump -i eth0 -n -c 100 host 10.42.0.168` |
| Capture for Wireshark | `sudo tcpdump -i eth0 -n -w /tmp/capture.pcap -c 1000` |
| Capture over SSH (exclude SSH itself) | `sudo tcpdump -i eth0 -n not port 22 -c 200` |
| Verbose DHCP with MACs | `sudo tcpdump -i eth0 -n -e -v -c 20 port 67 or port 68` |
| Rotating capture (new file every 60s) | `sudo tcpdump -i eth0 -n -w /tmp/cap_%Y%m%d_%H%M%S.pcap -G 60` |
| TCP SYN only (new connections) | `sudo tcpdump -i eth0 -n 'tcp[tcpflags] & tcp-syn != 0'` |
| HTTP requests (unencrypted) | `sudo tcpdump -i eth0 -n -A port 80 \| grep -E '^(GET\|POST\|PUT\|DELETE)'` |

> **Tip:** When capturing over SSH, always add `not port 22` to your filter — otherwise tcpdump captures its own SSH traffic, which generates more traffic, which generates more captures, flooding the output.

---

## `tshark`

[`tshark`](https://tshark.dev/) is the command-line interface to Wireshark. It uses the same protocol dissectors, so it can decode and display protocol fields that tcpdump cannot (e.g. DHCP option names, DNS record details, HTTP headers, TLS handshake parameters). Install with `sudo apt install tshark`.

### Basic usage

```bash
sudo tshark -i <interface>                           # capture all traffic on an interface
sudo tshark -i eth0 -f "port 53"                     # capture filter (BPF syntax, same as tcpdump)
sudo tshark -i eth0 -Y "dns"                         # display filter (Wireshark syntax, applied after capture)
sudo tshark -i eth0 -c 10                            # capture only 10 packets then stop
sudo tshark -i eth0 -w /tmp/capture.pcap             # write to file (same .pcap format as tcpdump)
sudo tshark -r /tmp/capture.pcap                     # read and display a capture file
sudo tshark -r /tmp/capture.pcap -Y "dhcp"           # read file, show only DHCP packets
```

### Capture filters vs display filters

| Type | Flag | Syntax | When applied | Example |
|------|------|--------|-------------|--------|
| Capture filter | `-f` | BPF (same as tcpdump) | During capture — packets not matching are discarded | `-f "port 67 or port 68"` |
| Display filter | `-Y` | Wireshark display filter | After capture — all packets are captured, only matching ones are shown | `-Y "dhcp.option.type == 53"` |

Capture filters are faster (kernel-level filtering), but display filters are more powerful (can filter on decoded protocol fields). Use capture filters to limit volume, display filters to drill down.

### Common flags

| Flag | Description |
|------|-------------|
| `-i <iface>` | Interface to capture on. `-i any` for all interfaces. |
| `-f "<filter>"` | Capture filter (BPF syntax). |
| `-Y "<filter>"` | Display filter (Wireshark syntax). |
| `-c <count>` | Stop after `<count>` packets. |
| `-n` | Don't resolve IP addresses to hostnames. |
| `-V` | Verbose — show full protocol tree for each packet (very detailed). |
| `-T fields -e <field>` | Output specific fields only (useful for scripting). |
| `-T json` | Output as JSON (useful for programmatic processing). |
| `-w <file>` | Write raw packets to `.pcap` file. |
| `-r <file>` | Read from a `.pcap` file. |
| `-q` | Quiet — suppress per-packet output (useful with `-z` statistics). |
| `-z <stat>` | Show statistics (e.g. `-z io,stat,1` for per-second I/O stats). |
| `-2` | Two-pass analysis — enables display filters that depend on future packets (e.g. response time). |

**Example — decode DHCP traffic with option names:**

```bash
sudo tshark -i eth1 -f "port 67 or port 68" -V -c 4
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
sudo tshark -i eth0 -f "port 53" -T fields -e ip.src -e ip.dst -e dns.qry.name -c 20
```

Output:
```
10.42.0.168	10.42.0.1	google.com
10.42.0.1	10.42.0.168	google.com
```

**Example — conversation statistics (who is talking to whom):**

```bash
tshark -r capture.pcap -q -z conv,ip         # IP conversation summary
tshark -r capture.pcap -q -z conv,tcp        # TCP conversation summary
tshark -r capture.pcap -q -z endpoints,ip    # endpoint traffic summary
```

Output:
```
================================================================================
IPv4 Conversations
Filter:<No Filter>
                                               |       <-      | |       ->      | |     Total     |
                                               | Frames  Bytes | | Frames  Bytes | | Frames  Bytes |
10.42.0.168          <-> 10.42.0.1                  45   5400       52   48200       97   53600
10.42.0.168          <-> 8.8.8.8                    12    840       12   1200        24    2040
```

**Example — protocol hierarchy (traffic composition):**

```bash
tshark -r capture.pcap -q -z io,phs           # protocol hierarchy statistics
```

Shows the percentage breakdown of traffic by protocol — useful for understanding what is generating traffic on a busy network.

**Example — DNS response time analysis:**

```bash
tshark -r capture.pcap -Y "dns.time" -T fields -e dns.qry.name -e dns.time -2
```

Shows how long each DNS query took to resolve — useful for identifying slow upstream resolvers.

**Example — read a tcpdump capture with richer decoding:**

```bash
# Capture with tcpdump (lightweight, always available):
sudo tcpdump -i eth0 -n -w /tmp/debug.pcap -c 500

# Analyze with tshark (rich protocol decoding):
tshark -r /tmp/debug.pcap -Y "dns.flags.rcode != 0"   # show only failed DNS queries
tshark -r /tmp/debug.pcap -Y "dhcp.option.dhcp == 5"   # show only DHCP ACKs
tshark -r /tmp/debug.pcap -Y "tcp.analysis.retransmission"  # show retransmissions (network issues)
tshark -r /tmp/debug.pcap -Y "tcp.analysis.zero_window"     # show zero-window events (receiver overloaded)
```

This is a common workflow: capture with tcpdump on a minimal system (always installed), then analyze with tshark or Wireshark on a machine with the tools installed.

### Useful display filters

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
| `tcp.analysis.retransmission` | TCP retransmissions (indicates packet loss) |
| `tcp.analysis.duplicate_ack` | Duplicate ACKs (indicates out-of-order delivery) |
| `tcp.analysis.zero_window` | Zero-window events (receiver buffer full) |
| `frame.time_delta > 1` | Packets with more than 1 second gap from previous (find stalls) |
| `tls.handshake.type == 1` | TLS Client Hello (new TLS connections) |

### Useful recipes

| Purpose | Command |
|---------|---------|
| Debug DHCP with full decode | `sudo tshark -i eth1 -f "port 67 or port 68" -V -c 8` |
| Debug DNS queries | `sudo tshark -i eth0 -Y "dns.flags.response == 0" -c 20` |
| Show only failed DNS | `sudo tshark -i eth0 -Y "dns.flags.rcode != 0" -c 20` |
| List all DHCP leases being handed out | `sudo tshark -i eth1 -Y "dhcp.option.dhcp == 5" -T fields -e dhcp.ip.your -e dhcp.hw.mac_addr -c 20` |
| Per-second packet rate | `tshark -r capture.pcap -q -z io,stat,1` |
| Top talkers | `tshark -r capture.pcap -q -z endpoints,ip` |
| TCP retransmission analysis | `tshark -r capture.pcap -q -z io,stat,1,tcp.analysis.retransmission` |
| Follow a TCP stream | `tshark -r capture.pcap -z follow,tcp,ascii,0` |
| Export as JSON for scripting | `tshark -r capture.pcap -T json -Y "dns" > dns_traffic.json` |
| Analyze a pcap from tcpdump | `tshark -r capture.pcap -Y "<filter>"` |

---

## Wireshark

[Wireshark](https://www.wireshark.org/) is the full graphical packet analyzer. It reads the same `.pcap`/`.pcapng` files as tcpdump and tshark, but provides an interactive GUI with colour-coded protocols, click-to-expand packet dissection, stream reassembly, and flow visualizations.

### When to use Wireshark over tshark

| Use Wireshark when… | Use tshark when… |
|---------------------|------------------|
| You need to visually browse and explore a capture | You need a quick filter/count from the terminal |
| Following TCP/UDP streams interactively | Extracting specific fields for a script |
| Analyzing TLS handshakes or certificate chains | Running on a headless server |
| Building complex filters interactively (autocomplete) | Generating statistics in batch |
| Showing captures to others (screenshots, presentations) | Processing many pcap files in a pipeline |

### Installation

```bash
sudo apt install wireshark           # Debian/Ubuntu
sudo dnf install wireshark           # Fedora/RHEL
brew install --cask wireshark        # macOS
```

During installation on Debian/Ubuntu, it asks whether non-root users should be able to capture packets. Select "Yes" — this adds the `wireshark` group. Then add your user: `sudo usermod -aG wireshark $USER` (re-login required).

### Opening a capture file

```bash
wireshark /tmp/capture.pcap          # open from terminal
wireshark -r /tmp/capture.pcap -Y "dns"  # open with a display filter pre-applied
```

Or: File → Open in the GUI.

### Key GUI panels

| Panel | Description |
|-------|-------------|
| **Packet List** (top) | One row per packet — shows timestamp, source, destination, protocol, length, and info summary. Click a row to inspect it. |
| **Packet Details** (middle) | Expandable tree showing every protocol layer and field for the selected packet. Click fields to see their raw bytes highlighted below. |
| **Packet Bytes** (bottom) | Raw hex/ASCII dump of the selected packet. Highlights correspond to the selected field in the details panel. |
| **Display Filter bar** (top) | Type display filters (same syntax as `tshark -Y`). Green = valid filter, red = syntax error. Autocomplete with Tab. |

### Essential Wireshark features

### Display filter bar

Same syntax as tshark's `-Y` flag. Type a filter and press Enter to apply:

```
dns.flags.rcode != 0
tcp.port == 443 && ip.addr == 10.42.0.1
frame.time_delta > 0.5
```

Right-click any field in the Packet Details panel → "Apply as Filter" to build filters visually without typing.

### Follow Stream

Right-click a packet → Follow → TCP Stream (or UDP/TLS Stream). Opens a window showing the full conversation between client and server, colour-coded by direction:
- Red = client → server
- Blue = server → client

Essential for debugging HTTP, SMTP, or any text-based protocol — you see the full request/response exchange as readable text.

### Conversation and Endpoint Statistics

- Statistics → Conversations: shows all IP/TCP/UDP conversations with packet counts, bytes, and duration.
- Statistics → Endpoints: shows all hosts with traffic volume — useful for finding top talkers.
- Statistics → Protocol Hierarchy: shows traffic breakdown by protocol percentage.

### I/O Graphs

Statistics → I/O Graphs: shows packets/bytes per time interval. Add multiple lines with different filters to compare traffic types (e.g. DNS vs HTTP vs retransmissions) over time.

### Expert Information

Analyze → Expert Information: Wireshark's built-in analysis engine flags anomalies:
- **Errors** (red): malformed packets, bad checksums.
- **Warnings** (yellow): TCP retransmissions, out-of-order segments, zero-window events.
- **Notes** (cyan): duplicate ACKs, TCP window updates.
- **Chats** (blue): normal protocol events (connection setup/teardown).

This is the fastest way to spot network problems in a large capture — jump directly to the warnings/errors.

### Time reference and delta columns

- Right-click a packet → "Set/Unset Time Reference" to make it time zero — all subsequent timestamps show relative to this packet.
- Add a column: Edit → Preferences → Columns → add `Delta time displayed` to see the gap between consecutive displayed packets (useful for finding stalls).

### Colouring rules

Packets are colour-coded by protocol and condition (e.g. red = bad TCP, green = HTTP, light blue = DNS). Customize via View → Coloring Rules.

### Common Wireshark analysis workflow

1. Open the `.pcap` file.
2. Check Expert Information (Analyze → Expert Info) for immediate warnings/errors.
3. Apply a display filter to focus on the relevant protocol or hosts.
4. Right-click → Follow Stream for any conversation you want to inspect in detail.
5. Check Statistics → Conversations to see who is talking to whom and how much.
6. Use I/O Graphs to correlate issues with time (e.g. retransmissions spike at 14:32).

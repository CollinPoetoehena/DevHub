# Network Models & Packets

How data travels across a network — from application to wire and back. This document explains the layered models (OSI and TCP/IP), what happens at each layer, and how data is structured (frames, packets, segments) with concrete examples.

---

## Table of Contents

- [Why Layered Models](#why-layered-models)
- [The OSI Model (7 Layers)](#the-osi-model-7-layers)
  - [Layer 1 — Physical](#layer-1--physical)
  - [Layer 2 — Data Link](#layer-2--data-link)
  - [Layer 3 — Network](#layer-3--network)
  - [Layer 4 — Transport](#layer-4--transport)
  - [Layers 5–7 — Session, Presentation, Application](#layers-57--session-presentation-application)
- [The TCP/IP Model (4 Layers)](#the-tcpip-model-4-layers)
- [OSI vs TCP/IP Comparison](#osi-vs-tcpip-comparison)
- [Data Units at Each Layer](#data-units-at-each-layer)
  - [Encapsulation and De-encapsulation](#encapsulation-and-de-encapsulation)
  - [Anatomy of a Frame (Layer 2)](#anatomy-of-a-frame-layer-2)
  - [Anatomy of a Packet (Layer 3)](#anatomy-of-a-packet-layer-3)
    - [IPv4 Packet](#ipv4-packet)
    - [IPv6 Packet](#ipv6-packet)
  - [Anatomy of a Segment/Datagram (Layer 4)](#anatomy-of-a-segmentdatagram-layer-4)
    - [TCP Segment](#tcp-segment)
    - [UDP Datagram](#udp-datagram)
  - [Full Example: HTTP Request Through the Layers](#full-example-http-request-through-the-layers)
- [Understanding Local and Remote Network Communication](#understanding-local-and-remote-network-communication)
  - [Example 1: Same Subnet, Same Switch](#example-1-same-subnet-same-switch)
  - [Example 2: Same Subnet, Multiple Switches](#example-2-same-subnet-multiple-switches)
  - [Example 3: Different Subnet](#example-3-different-subnet)
  - [Example 4: Different Network (Internet Access)](#example-4-different-network-internet-access)
  - [Why People Say "Layer 2 Is Local" and "Layer 3 Is Remote"](#why-people-say-layer-2-is-local-and-layer-3-is-remote)
- [Where Homelab Devices Operate](#where-homelab-devices-operate)

---

## Why Layered Models

Networking is complex — dozens of protocols, hardware types, and software components must work together. Layered models break this complexity into discrete, independent layers where each layer has a single responsibility and communicates with the layers directly above and below it.

Benefits:
- **Separation of concerns:** You can change one layer (e.g. switch from WiFi to Ethernet) without affecting the layers above (TCP, HTTP still work the same).
- **Interoperability:** Vendors can build products for a specific layer (switches for layer 2, routers for layer 3) and they all work together.
- **Troubleshooting:** When something breaks, you can isolate which layer is failing (is it a cable issue? IP routing? DNS? Application bug?).

---

## The OSI Model (7 Layers)

The OSI (Open Systems Interconnection) model is a conceptual framework with 7 layers. It was defined by the ISO in 1984 and is the standard reference for discussing "which layer" something operates at, even though real implementations don't follow it strictly.

| Layer | Name | Purpose | Protocols/Examples | Data Unit |
|-------|------|---------|-------------------|-----------|
| 7 | Application | User-facing services and APIs | HTTP, HTTPS, DNS, SSH, SMTP, FTP | Data |
| 6 | Presentation | Data format translation, encryption, compression | TLS/SSL, JPEG, ASCII, UTF-8 | Data |
| 5 | Session | Manage connections (open, maintain, close) | NetBIOS, RPC, SOCKS | Data |
| 4 | Transport | End-to-end delivery, reliability, flow control | TCP, UDP | Segment (TCP) / Datagram (UDP) |
| 3 | Network | Logical addressing and routing between networks | IP (IPv4, IPv6), ICMP, ARP* | Packet |
| 2 | Data Link | Physical addressing and hop-to-hop delivery | Ethernet (802.3), WiFi (802.11), 802.1Q (VLANs) | Frame |
| 1 | Physical | Bits on the wire (electrical/optical/radio signals) | Ethernet cables, fibre optic, WiFi radio, RJ45 | Bits |

*ARP is sometimes placed at layer 2/3 boundary — it maps layer 3 addresses (IP) to layer 2 addresses (MAC).

**Mnemonic (top to bottom):** **A**ll **P**eople **S**eem **T**o **N**eed **D**ata **P**rocessing.

**Mnemonic (bottom to top):** **P**lease **D**o **N**ot **T**hrow **S**ausage **P**izza **A**way.

### Layer 1 — Physical

The physical medium that carries bits: copper cables (Ethernet Cat5e/Cat6), fibre optic, WiFi radio waves. This layer defines voltages, frequencies, pin layouts, and connector types (RJ45, SFP+). It has no concept of addresses, packets, or meaning — just raw bit streams (1s and 0s).

**Failures at this layer:** broken cable, loose connector, interference, wrong cable type, port LED off.

### Layer 2 — Data Link

Responsible for delivering frames between devices on the **same** local network (same broadcast domain). In practice, the *same local network (same broadcast domain)* means devices that can communicate directly using MAC addresses without needing a router.  Uses **MAC addresses** (48-bit hardware addresses like `28:94:01:8a:ec:28`) to identify source and destination on the local segment.

See for more details about what *local network* and *remote/different networks* mean in section: [Understanding Local and Remote Network Communication](#understanding-local-and-remote-network-communication).

This is where **switches operate**. A switch reads the destination MAC in each frame, looks it up in its MAC address table, and forwards the frame out the correct port. Switches never look at IP addresses — they only understand MAC addresses.

**VLANs (802.1Q)** operate at this layer — the VLAN tag is inserted into the Ethernet frame header between the source MAC and the EtherType field.

**Failures at this layer:** MAC address conflicts, switch loop (broadcast storm), VLAN misconfiguration, wrong port assignment.

### Layer 3 — Network

Responsible for delivering packets between devices on **different** networks. Uses **IP addresses** (logical addresses like `10.42.0.1`) to identify source and destination across network boundaries.

See for more details about what *local network* and *remote/different networks* mean in section: [Understanding Local and Remote Network Communication](#understanding-local-and-remote-network-communication).

This is where **routers operate**. A router reads the destination IP in each packet, consults its routing table, and forwards the packet out the correct interface toward the next hop. Routers decrement the TTL (Time To Live) and re-encapsulate the packet in a new layer 2 frame for each hop.

**Failures at this layer:** wrong IP address, missing route, firewall blocking, TTL expired (too many hops).

### Layer 4 — Transport

Provides end-to-end communication between processes on different machines. Uses **port numbers** (0–65535) to identify which application on the machine should receive the data.

- **TCP (Transmission Control Protocol):** Reliable, ordered delivery. Establishes a connection (3-way handshake: SYN → SYN-ACK → ACK), tracks sequence numbers, retransmits lost data, provides flow control. Used by HTTP, SSH, SMTP.
- **UDP (User Datagram Protocol):** Unreliable, unordered, no connection. Just sends datagrams — fast but no guarantees. Used by DNS queries, DHCP, video streaming, gaming.

**TCP vs UDP — when to use which:**

| | TCP | UDP |
|-|-----|-----|
| Connection | Yes (3-way handshake) | No (just send) |
| Reliability | Guaranteed delivery, retransmission | Best-effort, no retransmission |
| Ordering | Maintains order via sequence numbers | No ordering guarantees |
| Overhead | 20+ byte header, connection state | 8 byte header, stateless |
| Speed | Slower (reliability has a cost) | Faster (no setup, no waiting) |
| Use cases | HTTP, SSH, SMTP, file transfers | DNS queries, DHCP, video streaming, gaming, VoIP |

**Failures at this layer:** port blocked by firewall, connection refused (no process listening), TCP timeout/reset.

### Layers 5–7 — Session, Presentation, Application

In practice these three layers are often collapsed into one "application layer" in real implementations. They cover:
- **Session (5):** Managing the lifecycle of a communication session (rarely implemented as a distinct layer).
- **Presentation (6):** Data formatting — character encoding (UTF-8), encryption (TLS), compression (gzip).
- **Application (7):** The actual protocol the user/application speaks: HTTP (web), SSH (remote shell), DNS (name resolution), SMTP (email).

---

## The TCP/IP Model (4 Layers)

The TCP/IP model (also called the Internet model or DoD model) is the practical model that the internet actually uses. It predates the OSI model and has 4 layers. It's simpler because it doesn't try to separate session/presentation/application — those are all "application layer" in TCP/IP.

| Layer | Name | OSI Equivalent | Purpose | Protocols |
|-------|------|----------------|---------|-----------|
| 4 | Application | OSI 5–7 | Application protocols | HTTP, DNS, SSH, SMTP, DHCP |
| 3 | Transport | OSI 4 | End-to-end delivery | TCP, UDP |
| 2 | Internet | OSI 3 | Routing between networks | IP, ICMP, ARP |
| 1 | Network Access (Link) | OSI 1–2 | Local delivery over physical media | Ethernet, WiFi, PPP |

---

## OSI vs TCP/IP Comparison

```
OSI Model              TCP/IP Model
─────────────────      ──────────────────
7  Application  ─┐
6  Presentation  ├──→  4  Application
5  Session      ─┘
4  Transport    ────→  3  Transport
3  Network      ────→  2  Internet
2  Data Link    ─┐
1  Physical     ─┴──→  1  Network Access
```

**Which to use:** The OSI model is better for discussing concepts and troubleshooting ("is this a layer 2 or layer 3 problem?"). The TCP/IP model is better for describing how the internet actually works. Both are used throughout networking documentation — they're complementary, not competing.

---

## Data Units at Each Layer

As data moves down through the layers, each layer wraps (encapsulates) the data from the layer above with its own header. Each layer has its own name for the data unit:

| Layer | Data Unit Name | Contains |
|-------|---------------|----------|
| Application (7) | Data / Message | The actual payload (e.g. an HTTP request body) |
| Transport (4) | Segment (TCP) / Datagram (UDP) | Transport header + application data |
| Network (3) | Packet | IP header + segment |
| Data Link (2) | Frame | Ethernet header + packet + trailer (FCS) |
| Physical (1) | Bits | Raw electrical/optical/radio signals |

### Encapsulation and De-encapsulation

**Encapsulation (sending):** Each layer adds its own header around the data from the layer above, like putting a letter in an envelope, then putting that envelope in a bigger envelope:

```
Application data:       "GET / HTTP/1.1\r\nHost: google.com\r\n\r\n"
                                    │
                                    ▼ Transport layer adds TCP header
TCP Segment:            [TCP Header (src port, dst port, seq#, flags)] [Application Data]
                                    │
                                    ▼ Network layer adds IP header
IP Packet:              [IP Header (src IP, dst IP, TTL, protocol)] [TCP Segment]
                                    │
                                    ▼ Data Link layer adds Ethernet header + trailer
Ethernet Frame:         [Eth Header (dst MAC, src MAC, EtherType)] [IP Packet] [FCS]
                                    │
                                    ▼ Physical layer
Bits on the wire:       101010001110010101...
```

**De-encapsulation (receiving):** The reverse process. Each layer strips its header, reads the relevant information, and passes the payload up to the next layer.

### Anatomy of a Frame (Layer 2)

An Ethernet frame is the unit of data on a local network. It's what switches forward between ports.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Ethernet II Frame                            │
├──────────┬──────────┬───────────┬──────────────────────┬────────────┤
│ Dst MAC  │ Src MAC  │ EtherType │      Payload         │    FCS     │
│ 6 bytes  │ 6 bytes  │ 2 bytes   │   46–1500 bytes      │  4 bytes   │
└──────────┴──────────┴───────────┴──────────────────────┴────────────┘
```

| Field | Size | Description |
|-------|------|-------------|
| Destination MAC | 6 bytes | MAC address of the target device (or `ff:ff:ff:ff:ff:ff` for broadcast) |
| Source MAC | 6 bytes | MAC address of the sending device |
| EtherType | 2 bytes | Identifies the layer 3 protocol: `0x0800` = IPv4, `0x86DD` = IPv6, `0x8100` = 802.1Q VLAN tag |
| Payload | 46–1500 bytes | The IP packet (or other layer 3 data) |
| FCS (Frame Check Sequence) | 4 bytes | CRC-32 checksum to detect transmission errors |

**With 802.1Q VLAN tag (tagged frame):**

```
┌──────────┬──────────┬──────────────────┬───────────┬─────────────────────┬─────┐
│ Dst MAC  │ Src MAC  │ 802.1Q Tag       │ EtherType │      Payload        │ FCS │
│ 6 bytes  │ 6 bytes  │ 4 bytes          │ 2 bytes   │   46–1500 bytes     │ 4 B │
└──────────┴──────────┴──────────────────┴───────────┴─────────────────────┴─────┘
                       │                  │
                       ├─ TPID: 0x8100    │
                       ├─ Priority: 3 bits│
                       ├─ DEI: 1 bit      │
                       └─ VLAN ID: 12 bits│ ← This is the VLAN number (1–4094)
```

The VLAN tag is inserted between the source MAC and the original EtherType. This is what makes a frame "tagged" — the 12-bit VLAN ID field tells the switch which VLAN the frame belongs to.

**Example (hex dump of a tagged frame header):**
```
Dst MAC:    28:94:01:8a:ec:28
Src MAC:    dc:a6:32:xx:xx:xx
802.1Q:     81 00 00 14          ← TPID=0x8100, VLAN ID=20 (0x0014)
EtherType:  08 00                ← IPv4
Payload:    45 00 00 3c ...      ← IP packet starts here
```

### Anatomy of a Packet (Layer 3)

An IP packet is the unit of data routed between networks. It's what routers forward based on the destination IP address.

#### IPv4 Packet

[IPv4 Packet Structure](https://en.wikipedia.org/wiki/IPv4#Packet_structure):
```
┌────────┬───────┬───────────────┬───────────────┬───────────────┬───────────────┐
│ OFFSET │ Octet │ 0             │ 1             │ 2             │ 3             │
├────────┼───────┼─┬─┬─┬─┬─┬─┬─┬─┼─┬─┬─┬─┬─┬─┬─┬─┼─┬─┬─┬─┬─┬─┬─┬─┼─┬─┬─┬─┬─┬─┬─┬─┤
│ Octet  │ Bit   │0│1│2│3│4│5│6│7│8│9│0│1│2│3│4│5│6│7│8│9│0│1│2│3│4│5│6│7│8│9│0│1│
├────────┼───────┼─┴─┴─┴─┼─┴─┴─┴─┼─┴─┴─┴─┴─┴─┼─┴─┼─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┤
│ 0      │ 0     │Version│  IHL  │      DSCP │ECN│        Total Length           │
├────────┼───────┼───────┴───────┴───────────┴───┼─────┬─────────────────────────┤
│ 4      │ 32    │           Identification      │Flags│    Fragment Offset      │
├────────┼───────┼───────────────┬───────────────┼─────┴─────────────────────────┤
│ 8      │ 64    │      TTL      │      Protocol │      Header Checksum          │
├────────┼───────┼───────────────┴───────────────┴───────────────────────────────┤
│ 12     │ 96    │                         Source IP Address                     │
├────────┼───────┼───────────────────────────────────────────────────────────────┤
│ 16     │ 128   │                      Destination IP Address                   │
├────────┼───────┼───────────────────────────────────────────────────────────────┤
│ 20–59  │ 160   │                                                               │
│        │ -     │                      Options (if IHL > 5)                     │
│        │ 479   │           (0 - 320 bits, padded to multiples of 32 bits)      │
│        │       │                                                               │
├────────┴───────┼═══════════════════════════════════════════════════════════════╡
│ variable       │        Data (variable length — layer 4 segment/datagram)      │
└────────────────┴───────────────────────────────────────────────────────────────┘
```

**How to read the diagrams:** Each diagram is a single box with three parts: the **bit-position ruler** (top 2 rows), the **header fields**, and the **data** (payload), separated by a `═══` divider.
- **The ruler (top 2 rows):** The first row (`OFFSET / Octet`) labels the four octets (0, 1, 2, 3) that make up each 32-bit row. The second row (`Octet / Bit`) shows individual bit positions within those octets, numbered 0–9 repeating for each octet (the first `0` is bit 0, the second `0` after octet 1 is bit 10, the third is bit 20, the fourth is bit 30 — see the Offset column to know which row you're in). Each bit has its own cell (`│0│1│2│...│`) so you can count exactly where a field starts and ends.
- **Why 0–9 instead of 0–31:** Each octet contains 10 bit positions (0 through 9), and the numbering repeats for each of the 4 octets. This keeps the diagram compact — full two-digit numbers (10, 11, ..., 31) would require wider cells and break the alignment with the header fields below. Since each octet is clearly labeled (0, 1, 2, 3) in the row above, you can always calculate the absolute bit position: octet number × 10 + bit digit. For example, bit `3` under octet `2` = bit 23. The `│` separators between each digit make it easy to count without ambiguity.
- **The Offset column:** The left two columns show the cumulative position of each row — `OFFSET` is the octet offset from the start of the header, and `Octet` is the bit offset. For example, row `4 / 32` means "starting at octet 4 (= bit 32)". Each row adds 4 octets (32 bits).
- **How to read a field's position:** Find the field in the header section. Its left edge aligns with a bit in the ruler above — that's its start position. Count the bit cells it spans to get its size. For example, `Version` spans 4 bit cells (bits 0–3), `Total Length` spans 16 bit cells (bits 16–31 = 2 octets).
- **The `═══` divider:** Separates the header from the data. Everything above is the protocol header (structured, fixed-format fields). Everything below is the data payload (variable length, carries the next layer's content).
- **The `│` separators:** Every bit in the ruler row has its own cell (`│0│1│2│...│`), and every field in the header rows is enclosed in `│` borders. This makes it easy to count exactly how many bits a field spans — just count the cells between its left `│` and right `│`. It also makes field boundaries unambiguous, even when two fields sit side by side in the same row (like `Version│IHL` or `Flags│Fragment Offset`).
- **Why "octet" instead of "byte":** An [octet](https://en.wikipedia.org/wiki/Octet_(computing)) is a unit of exactly 8 bits. Networking standards use "octet" because "byte" historically meant different sizes on different systems. In practice on modern systems, 1 octet = 1 byte = 8 bits.
- **Structure vs values:** The diagrams show the *structure* (field layout), not actual values. When a real packet is sent, each bit position is filled with the actual value for that field.
- **Why bit-level diagrams are used:** These RFC-style diagrams are the standard in protocol documentation because they provide a precise, implementation-independent representation. Any device from any vendor can interpret packets correctly by reading the defined bit ranges.

| Field | Size | Description |
|-------|------|-------------|
| Version | 4 bits | `4` for IPv4, `6` for IPv6 |
| IHL (Internet Header Length) | 4 bits | Header length in 32-bit words (usually 5 = 20 bytes) |
| DSCP (Differentiated Services Code Point) | 6 bits | Used for QoS — marks traffic priority class |
| ECN (Explicit Congestion Notification) | 2 bits | Allows routers to signal congestion without dropping packets |
| Total Length | 16 bits (2 bytes) | Total size of the IP packet (header + payload) in bytes |
| Identification | 16 bits (2 bytes) | Unique ID for reassembling fragmented packets |
| Flags | 3 bits | Fragmentation control: DF (Don't Fragment), MF (More Fragments) |
| Fragment Offset | 13 bits | Position of this fragment within the original packet |
| TTL (Time To Live) | 8 bits (1 byte) | Decremented by each router; packet is dropped when it reaches 0 (prevents infinite loops) |
| Protocol | 8 bits (1 byte) | Layer 4 protocol: `6` = TCP, `17` = UDP, `1` = ICMP |
| Header Checksum | 16 bits (2 bytes) | Error-detection checksum over the header only (recalculated at each hop) |
| Source IP | 32 bits (4 bytes) | IP address of the sender (e.g. `10.42.0.10`) |
| Destination IP | 32 bits (4 bytes) | IP address of the target (e.g. `8.8.8.8`) |
| Options | 0–320 bits (0–40 bytes) | Optional fields (e.g. record route, timestamp). Present when IHL > 5. Padded to 32-bit boundary. |
| Data | Variable | The layer 4 segment/datagram being carried (TCP segment, UDP datagram, ICMP message, etc.). Size = Total Length − (IHL × 4). |

**Example:**
```
Version: 4, IHL: 5 (20 bytes), Total Length: 60
TTL: 64, Protocol: 6 (TCP)
Source IP:      10.42.0.10
Destination IP: 8.8.8.8
Data:           [TCP segment: src port 54321, dst port 80, seq 1, "GET / HTTP/1.1..."]
```

#### IPv6 Packet

[IPv6 Packet Structure](https://en.wikipedia.org/wiki/IPv6_packet#Fixed_header):
```
┌────────┬───────┬───────────────┬───────────────┬───────────────┬───────────────┐
│ OFFSET │ Octet │ 0             │ 1             │ 2             │ 3             │
├────────┼───────┼─┬─┬─┬─┬─┬─┬─┬─┼─┬─┬─┬─┬─┬─┬─┬─┼─┬─┬─┬─┬─┬─┬─┬─┼─┬─┬─┬─┬─┬─┬─┬─┤
│ Octet  │ Bit   │0│1│2│3│4│5│6│7│8│9│0│1│2│3│4│5│6│7│8│9│0│1│2│3│4│5│6│7│8│9│0│1│
├────────┼───────┼─┴─┴─┴─┼─┴─┴─┴─┴─┴─┴─┴─┼─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┤
│ 0      │ 0     │Version│ Traffic Class │              Flow Label               │
├────────┼───────┼───────┴───────────────┴───────┬───────────────┬───────────────┤
│ 4      │ 32    │       Payload Length          │  Next Header  │   Hop Limit   │
├────────┼───────┼───────────────────────────────┴───────────────┴───────────────┤
│ 8–23   │ 64    │                                                               │
│        │ -     │                       Source Address                          │
│        │ 191   │                        (128 bits)                             │
│        │       │                                                               │
├────────┼───────┼───────────────────────────────────────────────────────────────┤
│ 24–39  │ 192   │                                                               │
│        │ -     │                    Destination Address                        │
│        │ 319   │                        (128 bits)                             │
│        │       │                                                               │
├────────┴───────┼═══════════════════════════════════════════════════════════════╡
│ variable       │           Data (variable length — layer 4 segment/datagram)   │
└────────────────┴───────────────────────────────────────────────────────────────┘
```

> **Note:** The bit positions in the diagram above are read the same way as in the IPv4 diagram — see the explanation in [Anatomy of a Packet (Layer 3) > "How to read the diagrams"](#anatomy-of-a-packet-layer-3).

The IPv6 header is simpler than IPv4 — it is always exactly 40 bytes (no variable-length options, no IHL field, no header checksum). Optional functionality is handled through **extension headers** that are chained after the fixed header.

| Field | Size | Description |
|-------|------|-------------|
| Version | 4 bits | Always `6` for IPv6 |
| Traffic Class | 8 bits | Equivalent to IPv4's DSCP + ECN — used for QoS (priority/class of traffic) |
| Flow Label | 20 bits | Identifies a flow of packets that should receive the same treatment (e.g. same path through routers). Set to `0` if not used. |
| Payload Length | 16 bits | Length of the payload in bytes (everything after this 40-byte header, including extension headers) |
| Next Header | 8 bits | Identifies the type of the next header — either a layer 4 protocol (`6` = TCP, `17` = UDP, `58` = ICMPv6) or an extension header type (`0` = Hop-by-Hop, `43` = Routing, `44` = Fragment, etc.) |
| Hop Limit | 8 bits | Same function as IPv4's TTL — decremented by each router, packet dropped at 0 |
| Source Address | 128 bits (16 bytes) | IPv6 address of the sender (e.g. `2a02:a44a:8185:1::10`) |
| Destination Address | 128 bits (16 bytes) | IPv6 address of the target (e.g. `2001:4860:4860::8888`) |
| Data | Variable | The layer 4 segment/datagram being carried (TCP segment, UDP datagram, ICMPv6 message, etc.). Size = Payload Length (minus any extension headers). |

**Key differences from IPv4:**

| | IPv4 | IPv6 |
|-|------|------|
| Header size | Variable (20–60 bytes) | Fixed (40 bytes) |
| Address size | 32 bits (4 bytes) | 128 bits (16 bytes) |
| Checksum | Header checksum field (recalculated at every hop) | No checksum — removed to improve router performance; layer 4 (TCP/UDP) checksums handle integrity |
| Fragmentation | Done by any router along the path | Done only by the source (routers never fragment; they send "Packet Too Big" ICMPv6 if needed) |
| Options | Variable-length Options field in the header | Extension headers chained after the fixed header |
| Broadcast | Yes (`255.255.255.255`, subnet broadcast) | No — replaced entirely by multicast |

**Example:**
```
Version: 6, Traffic Class: 0, Flow Label: 0
Payload Length: 40, Next Header: 6 (TCP), Hop Limit: 64
Source:      2a02:a44a:8185:1::10
Destination: 2001:4860:4860::8888
Data:        [TCP segment: src port 54321, dst port 443, seq 1, TLS ClientHello...]
```

### Anatomy of a Segment/Datagram (Layer 4)

Layer 4 has two main protocols: TCP (reliable, connection-oriented) and UDP (unreliable, connectionless). Each has its own header format.

#### TCP Segment

A TCP segment is the unit of data for reliable end-to-end delivery between processes.

[TCP Segment Structure](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#TCP_segment_structure):
```
┌────────┬───────┬───────────────┬───────────────┬───────────────┬───────────────┐
│ OFFSET │ Octet │ 0             │ 1             │ 2             │ 3             │
├────────┼───────┼─┬─┬─┬─┬─┬─┬─┬─┼─┬─┬─┬─┬─┬─┬─┬─┼─┬─┬─┬─┬─┬─┬─┬─┼─┬─┬─┬─┬─┬─┬─┬─┤
│ Octet  │ Bit   │0│1│2│3│4│5│6│7│8│9│0│1│2│3│4│5│6│7│8│9│0│1│2│3│4│5│6│7│8│9│0│1│
├────────┼───────┼─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┼─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┤
│ 0      │ 0     │          Source Port          │        Destination Port       │
├────────┼───────┼───────────────────────────────┴───────────────────────────────┤
│ 4      │ 32    │                       Sequence Number                         │
├────────┼───────┼───────────────────────────────────────────────────────────────┤
│ 8      │ 64    │                    Acknowledgment Number                      │
│        │       │                (meaningful when ACK bit set)                  │
├────────┼───────┼───────┬───────┬─┬─┬─┬─┬─┬─┬─┬─┬───────────────────────────────┤
│ 12     │ 96    │ Data  │Reser- │C│E│U│A│P│R│S│F│           Window              │
│        │       │ Offset│ved    │W│C│R│C│S│S│Y│I│                               │
│        │       │       │       │R│E│G│K│H│T│N│N│                               │
├────────┼───────┼───────┴───────┴─┴─┴─┴─┴─┴─┴─┴─┼───────────────────────────────┤
│ 16     │ 128   │          Checksum             │        Urgent Pointer         │
│        │       │                               │ (meaningful when URG bit set) │
├────────┼───────┼───────────────────────────────┴───────────────────────────────┤
│ 20–59  │ 160   │                                                               │
│        │ -     │                  Options (if Data Offset > 5)                 │
│        │ 479   │ (0 - 320 bits, padded with zeroes to a multiple of 32 bits)   │
│        │       │                                                               │
├────────┴───────┼═══════════════════════════════════════════════════════════════╡
│ variable       │           Data (variable length — application data)           │
└────────────────┴───────────────────────────────────────────────────────────────┘
```

> **Note:** The bit positions in the diagram above are read the same way as in the IPv4 diagram — see the explanation in [Anatomy of a Packet (Layer 3) > "How to read the diagrams"](#anatomy-of-a-packet-layer-3).

> **Why individual flag bits?** Unlike most header fields that span multiple bits and represent a numeric value (e.g. a 16-bit port number), each TCP flag is a single bit that is independently either set (`1`) or unset (`0`). That is why the diagram and table list them separately — each flag has its own meaning and can be toggled independently of the others. A single segment can have multiple flags set at the same time (e.g. PSH+ACK, SYN+ACK).

| Field | Size | Description |
|-------|------|-------------|
| Source Port | 16 bits (2 bytes) | Port on the sending machine (e.g. `54321` — ephemeral/random) |
| Destination Port | 16 bits (2 bytes) | Port on the receiving machine (e.g. `80` for HTTP, `22` for SSH) |
| Sequence Number | 32 bits (4 bytes) | Byte position in the stream (used for ordering and retransmission) |
| Acknowledgment Number | 32 bits (4 bytes) | Next byte the sender expects to receive (confirms receipt of data) |
| Data Offset | 4 bits | TCP header length in 32-bit words (usually 5 = 20 bytes without options) |
| Reserved | 3 bits | Reserved for future use — must be set to zero |
| Flag: CWR | 1 bit | Congestion Window Reduced — sender reduced its transmit rate after receiving ECE |
| Flag: ECE | 1 bit | ECN-Echo — signals congestion was detected (during handshake: ECN capability) |
| Flag: URG | 1 bit | Urgent — Urgent Pointer field is valid; data should be prioritised |
| Flag: ACK | 1 bit | Acknowledgment — Acknowledgment Number field is valid (set on all segments after the initial SYN) |
| Flag: PSH | 1 bit | Push — deliver data to the application immediately, don't buffer |
| Flag: RST | 1 bit | Reset — abort the connection (error or rejection) |
| Flag: SYN | 1 bit | Synchronize — start a new connection (used in 3-way handshake) |
| Flag: FIN | 1 bit | Finish — sender has finished sending data (graceful close) |
| Window | 16 bits (2 bytes) | How much data (window size) the receiver can accept (flow control) |
| Checksum | 16 bits (2 bytes) | Error-detection checksum over header + payload |
| Urgent Pointer | 16 bits (2 bytes) | Points to urgent data in the stream (only valid when URG flag is set) |
| Options | 0–320 bits (0–40 bytes) | Optional fields (e.g. MSS, window scaling, timestamps). Present when Data Offset > 5. Padded with zeroes to a multiple of 32 bits, since Data Offset counts words of 4 octets. |
| Data | Variable | The application data being sent (e.g. HTTP request, SSH command, file bytes). Size = IP Total Length − IP header − TCP header. |

**Example:**
```
Source Port: 54321, Destination Port: 80
Sequence: 1, Acknowledgment: 1, Flags: PSH+ACK
Window Size: 65535, Checksum: 0xA3F2
Data: "GET / HTTP/1.1\r\nHost: google.com\r\n\r\n" (37 bytes)
```

**TCP 3-way handshake (connection establishment):**
```
Client                          Server
  │                               │
  │──── SYN (seq=100) ───────────→│ "I want to connect"
  │                               │
  │←─── SYN-ACK (seq=300,ack=101)─│ "OK, I acknowledge your SYN"
  │                               │
  │──── ACK (seq=101,ack=301) ───→│ "Got it, connection established"
  │                               │
```

#### UDP Datagram

A UDP datagram is the unit of data for fast, connectionless delivery. No handshake, no retransmission, no ordering guarantees — just send and hope it arrives.

[UDP Datagram Structure](https://en.wikipedia.org/wiki/User_Datagram_Protocol#UDP_datagram_structure):
```
┌────────┬───────┬───────────────┬───────────────┬───────────────┬───────────────┐
│ OFFSET │ Octet │ 0             │ 1             │ 2             │ 3             │
├────────┼───────┼─┬─┬─┬─┬─┬─┬─┬─┼─┬─┬─┬─┬─┬─┬─┬─┼─┬─┬─┬─┬─┬─┬─┬─┼─┬─┬─┬─┬─┬─┬─┬─┤
│ Octet  │ Bit   │0│1│2│3│4│5│6│7│8│9│0│1│2│3│4│5│6│7│8│9│0│1│2│3│4│5│6│7│8│9│0│1│
├────────┼───────┼─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┼─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┤
│ 0      │ 0     │          Source Port          │       Destination Port        │
├────────┼───────┼───────────────────────────────┼───────────────────────────────┤
│ 4      │ 32    │            Length             │           Checksum            │
├────────┴───────┼═══════════════════════════════┴═══════════════════════════════╡
│ variable       │           Data (variable length — application data)           │
└────────────────┴───────────────────────────────────────────────────────────────┘
```

> **Note:** The bit positions in the diagram above are read the same way as in the IPv4 diagram — see the explanation in [Anatomy of a Packet (Layer 3) > "How to read the diagrams"](#anatomy-of-a-packet-layer-3).

The UDP header is only **8 bytes** — far simpler than TCP's 20+ bytes. There is no sequence number, no acknowledgment, no flow control, and no connection state.

| Field | Size | Description |
|-------|------|-------------|
| Source Port | 16 bits (2 bytes) | Port on the sending machine (optional — can be `0` if no reply is expected) |
| Destination Port | 16 bits (2 bytes) | Port on the receiving machine (e.g. `53` for DNS, `67`/`68` for DHCP) |
| Length | 16 bits (2 bytes) | Total size of the UDP datagram (header + payload) in bytes. Minimum is 8 (header only). |
| Checksum | 16 bits (2 bytes) | Error-detection checksum over header + payload (optional in IPv4, mandatory in IPv6) |
| Data | Variable | The application data being sent (e.g. DNS query, DHCP message, video frame). Size = Length − 8 bytes. |

**Example:**
```
Source Port: 54321, Destination Port: 53
Length: 45, Checksum: 0xB7E1
Data: [DNS query: A record for "google.com"] (37 bytes)
```

**TCP vs UDP Comparison:** See [Layer 4 — Transport — TCP vs UDP](#layer-4--transport) for a detailed comparison of the two protocols.

### Full Example: HTTP Request Through the Layers

A device at `10.42.0.10` (on the lab network) opens `http://google.com` in a browser. Here's what happens at each layer:

#### 1. Application Layer (HTTP)

The browser constructs an HTTP request:
```
GET / HTTP/1.1
Host: google.com
```

#### 2. Transport Layer (TCP)

TCP wraps the HTTP data in a segment:
```
Source Port: 54321 (random ephemeral port)
Destination Port: 80 (HTTP)
Sequence: 1, Flags: PSH+ACK
Payload: "GET / HTTP/1.1\r\nHost: google.com\r\n\r\n"
```

#### 3. Network Layer (IP)

IP wraps the TCP segment in a packet. DNS has already resolved `google.com` → `142.250.179.110`:
```
Source IP: 10.42.0.10
Destination IP: 142.250.179.110
TTL: 64, Protocol: TCP (6)
Payload: [TCP segment from above]
```

#### 4. Data Link Layer (Ethernet)

The device's IP stack checks: "Is `142.250.179.110` on my local subnet (`10.42.0.0/20`)?" — No. So it sends the frame to its **default gateway** (`10.42.0.1` = the Pi router). It looks up the router's MAC via ARP:
```
Destination MAC: dc:a6:32:xx:xx:xx  (Pi router's MAC)
Source MAC: aa:bb:cc:dd:ee:ff       (this device's MAC)
EtherType: 0x0800 (IPv4)
Payload: [IP packet from above]
FCS: [calculated checksum]
```

#### 5. Physical Layer

The frame is converted to electrical signals on the Ethernet cable and sent to the switch on port 2.

#### 6. At the Switch (Layer 2)

The switch receives the frame, reads the destination MAC (`dc:a6:32:xx:xx:xx`), looks it up in its MAC table → port 1 (the router). It forwards the frame out port 1. The switch never looks at the IP address or TCP port — it only cares about MAC addresses.

#### 7. At the Router (Layer 3)

The router receives the frame, strips the Ethernet header, and reads the IP packet. Destination is `142.250.179.110` — not local. It consults its routing table: default route → `eth0` → ISP modem at `192.168.2.254`.

The router:
1. Decrements TTL (64 → 63)
2. Applies NAT: rewrites source IP from `10.42.0.10` → `192.168.2.59` (router's WAN IP) and tracks the mapping
3. Builds a new Ethernet frame with the ISP modem's MAC as destination
4. Sends it out `eth0`

The process continues through the ISP modem (another NAT), across the internet (many routers/hops), until it reaches Google's server. The reply follows the reverse path, with NAT tables at each stage rewriting the destination back to the original device.

---

## Understanding Local and Remote Network Communication

> **Note:** This section builds on the explanation of layers and data units above, which provide the background needed to understand the distinction between "local" and "remote" network communication.

People often learn that:

- **Layer 2 is for the local network**
- **Layer 3 is for different networks**

While this is broadly true, it can be misleading because **both Layer 2 and Layer 3 are involved in almost all IP communication**, even when devices are in the same subnet.

The key differences are:

- **Layer 1** decides how bits travel across the physical medium (cable, fibre, WiFi).
- **Layer 2** decides how frames are delivered within a **Layer 2 domain (broadcast domain)** using MAC addresses.
- **Layer 3** decides whether a destination is **local** or **remote**, and how packets are routed using IP addresses.

**Broadcast domain:** A group of devices that receive the same Layer 2 broadcast traffic (such as ARP requests). Devices in the same VLAN are typically in the same broadcast domain. Routers separate broadcast domains and do not forward Layer 2 broadcasts.

**Local** means the destination IP is **within the host's own subnet**.

For example:

```
Source:      192.168.1.10/24
Destination: 192.168.1.20/24
Both belong to: 192.168.1.0/24
```

The destination is local and can be reached directly through Layer 2 (MAC address).

**Remote** means the destination IP is **outside the local subnet**.

For example:

```
Source:      192.168.1.10/24
Destination: 192.168.2.30/24
These belong to different networks:
  192.168.1.0/24
  192.168.2.0/24
```

A **router must perform Layer 3 forwarding**.

### Example 1: Same Subnet, Same Switch

**Suppose:**

- PC-A: `192.168.1.10/24`, MAC: `AA:AA:AA:AA:AA:AA`
- PC-B: `192.168.1.20/24`, MAC: `BB:BB:BB:BB:BB:BB`

**When PC-A wants to send data to PC-B:**

1. PC-A determines that `192.168.1.20` is in its own subnet (`192.168.1.0/24`).
2. PC-A uses ARP to learn PC-B's MAC address.
3. PC-A creates:
   - An IP packet:
     - Source IP: `192.168.1.10`
     - Destination IP: `192.168.1.20`
   - An Ethernet frame:
     - Source MAC: `AA:AA:AA:AA:AA:AA`
     - Destination MAC: `BB:BB:BB:BB:BB:BB`
4. The switch looks up the destination MAC and forwards the frame directly to PC-B.

Here **Layer 2 forwarding occurs entirely within a single switch**. Layer 3 is still present because the packet contains IP addresses, but **no routing is required** because the **destination is local**.

### Example 2: Same Subnet, Multiple Switches

**Suppose:**

- PC-A: `192.168.1.10/24`, MAC: `AA:AA:AA:AA:AA:AA`
- PC-B: `192.168.1.20/24`, MAC: `BB:BB:BB:BB:BB:BB`
- Topology: `PC-A ---- Switch-1 ---- Switch-2 ---- PC-B`
- Both hosts are still in `192.168.1.0/24` and the same VLAN.

**When PC-A wants to send data to PC-B:**

1. PC-A determines that the destination is local.
2. PC-A learns PC-B's MAC address via ARP.
3. PC-A sends a frame addressed to PC-B's MAC address.
4. Switch-1 forwards the frame to Switch-2 using its MAC table.
5. Switch-2 forwards the frame to PC-B.

Here Layer 2 **forwarding occurs across multiple switches**, but still **within the same Layer 2 domain**. **No router is involved** because the **destination is local**.

### Example 3: Different Subnet

**Suppose:**

- PC-A: `192.168.1.10/24`
- PC-C: `192.168.2.30/24`
- Gateway: `192.168.1.1`

**PC-A wants to reach PC-C (`192.168.2.30`):**

1. PC-A calculates that `192.168.2.30` is not in its own subnet (`192.168.1.0/24`).
2. Therefore the destination is not local.
3. PC-A sends the frame to the default gateway.
4. The Ethernet frame contains the router's MAC address as the destination.
5. The IP packet still contains:
   - Source IP: `192.168.1.10`
   - Destination IP: `192.168.2.30`
6. The router examines the destination IP and forwards the packet to the correct network. In this case, the destination network (`192.168.2.0/24`) is **directly connected to the router**, so the traffic stays within the local organization/home LAN and **does not require Internet access**.

Here **Layer 3 routing is required** because the **destination is not local**. Although both devices may belong to the same organization or physical network infrastructure, they are in **different IP subnets** (`192.168.1.0/24` and `192.168.2.0/24`), **so a router must forward the traffic between them**. However, the traffic can still remain entirely within the same LAN or organizational network and does not need Internet access. **Routing simply moves packets between different local subnets**.

### Example 4: Different Network (Internet Access)

**Suppose:**

- PC-A: `192.168.1.10/24`
- DNS Server: `8.8.8.8`
- Gateway: `192.168.1.1`

**PC-A wants to reach `8.8.8.8`:**

1. PC-A calculates that `8.8.8.8` is not in the same subnet (`192.168.1.0/24`).
2. Therefore it sends the frame to the default gateway (`192.168.1.1`).
3. The Ethernet frame contains:
   - Destination MAC = router's MAC
4. The IP packet still contains:
   - Source IP = `192.168.1.10`
   - Destination IP = `8.8.8.8`
5. The router receives it, examines the Layer 3 destination IP, and forwards it to the next hop toward the internet.
6. Multiple routers repeat this process, each using its routing table to determine the next hop.
7. Eventually the packet reaches the network that owns `8.8.8.8`, and the server sends a response back to PC-A (`192.168.1.10`).

Here **Layer 3 routing is required** across **multiple networks and multiple routers** before the destination is reached.

### Why People Say "Layer 2 Is Local" and "Layer 3 Is Remote"

Because:

- **Layer 2 forwarding** only works within a single Layer 2 domain (broadcast domain).
- **Layer 3 routing** becomes necessary whenever a destination is outside the local subnet.

**A useful rule is:** A host always asks: "Is the destination IP in my subnet?"

- **Yes** → destination is local → use ARP and Layer 2 forwarding.
- **No** → destination is remote → send traffic to a router for Layer 3 forwarding.

This unifies both concepts nicely because "local" from a Layer 3 perspective usually corresponds to "reachable through the current Layer 2 domain without routing."

---

## Where Homelab Devices Operate

| Device | Primary OSI Layer | What it looks at |
|--------|-------------------|-----------------|
| Ethernet cable | 1 (Physical) | Electrical signals |
| Switch (NETGEAR GS305E) | 2 (Data Link) | MAC addresses, VLAN tags |
| Router (Pi) | 3 (Network) | IP addresses, routing table |
| Firewall (iptables on Pi) | 3–4 (Network + Transport) | IP addresses, ports, connection state |
| dnsmasq (DHCP/DNS) | 7 (Application) | DHCP messages, DNS queries |
| SSH tunnel | 4–7 (Transport + Application) | TCP connections, encrypted payload |

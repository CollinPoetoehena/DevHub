# Network Models & Packets

How data travels across a network — from application to wire and back. This document explains the layered models (OSI and TCP/IP), what happens at each layer, and how data is structured (frames, packets, segments) with concrete examples.

---

## Table of Contents

- [Why Layered Models](#why-layered-models)
- [The OSI Model (7 Layers)](#the-osi-model-7-layers)
- [The TCP/IP Model (4 Layers)](#the-tcpip-model-4-layers)
- [OSI vs TCP/IP Comparison](#osi-vs-tcpip-comparison)
- [Data Units at Each Layer](#data-units-at-each-layer)
- [Encapsulation and De-encapsulation](#encapsulation-and-de-encapsulation)
- [Anatomy of a Frame (Layer 2)](#anatomy-of-a-frame-layer-2)
- [Anatomy of a Packet (Layer 3)](#anatomy-of-a-packet-layer-3)
- [Anatomy of a Segment (Layer 4)](#anatomy-of-a-segment-layer-4)
- [Full Example: HTTP Request Through the Layers](#full-example-http-request-through-the-layers)
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

Responsible for delivering frames between devices on the **same** local network (same broadcast domain). Uses **MAC addresses** (48-bit hardware addresses like `28:94:01:8a:ec:28`) to identify source and destination on the local segment.

This is where switches operate. A switch reads the destination MAC in each frame, looks it up in its MAC address table, and forwards the frame out the correct port. Switches never look at IP addresses — they only understand MAC addresses.

**VLANs (802.1Q)** operate at this layer — the VLAN tag is inserted into the Ethernet frame header between the source MAC and the EtherType field.

**Failures at this layer:** MAC address conflicts, switch loop (broadcast storm), VLAN misconfiguration, wrong port assignment.

### Layer 3 — Network

Responsible for delivering packets between devices on **different** networks. Uses **IP addresses** (logical addresses like `10.42.0.1`) to identify source and destination across network boundaries.

This is where routers operate. A router reads the destination IP in each packet, consults its routing table, and forwards the packet out the correct interface toward the next hop. Routers decrement the TTL (Time To Live) and re-encapsulate the packet in a new layer 2 frame for each hop.

**Failures at this layer:** wrong IP address, missing route, firewall blocking, TTL expired (too many hops).

### Layer 4 — Transport

Provides end-to-end communication between processes on different machines. Uses **port numbers** (0–65535) to identify which application on the machine should receive the data.

- **TCP (Transmission Control Protocol):** Reliable, ordered delivery. Establishes a connection (3-way handshake: SYN → SYN-ACK → ACK), tracks sequence numbers, retransmits lost data, provides flow control. Used by HTTP, SSH, SMTP.
- **UDP (User Datagram Protocol):** Unreliable, unordered, no connection. Just sends datagrams — fast but no guarantees. Used by DNS queries, DHCP, video streaming, gaming.

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

---

## Encapsulation and De-encapsulation

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

---

## Anatomy of a Frame (Layer 2)

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

---

## Anatomy of a Packet (Layer 3)

An IP packet is the unit of data routed between networks. It's what routers forward based on the destination IP address.

**IPv4 Header:**

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
│Version│  IHL  │    DSCP   │ECN│         Total Length          │
├───────┴───────┼───────────┴───┼───────────────────────────────┤
│   Identification              │Flags│     Fragment Offset     │
├───────────────┼───────────────┼───────────────────────────────┤
│      TTL      │   Protocol    │       Header Checksum         │
├───────────────┴───────────────┴───────────────────────────────┤
│                       Source IP Address                       │
├───────────────────────────────────────────────────────────────┤
│                    Destination IP Address                     │
├───────────────────────────────────────────────────────────────┤
│                    Options (if IHL > 5)                       │
└───────────────────────────────────────────────────────────────┘
```

| Field | Size | Description |
|-------|------|-------------|
| Version | 4 bits | `4` for IPv4, `6` for IPv6 |
| IHL (Internet Header Length) | 4 bits | Header length in 32-bit words (usually 5 = 20 bytes) |
| TTL (Time To Live) | 1 byte | Decremented by each router; packet is dropped when it reaches 0 (prevents infinite loops) |
| Protocol | 1 byte | Layer 4 protocol: `6` = TCP, `17` = UDP, `1` = ICMP |
| Source IP | 4 bytes | IP address of the sender (e.g. `10.42.0.10`) |
| Destination IP | 4 bytes | IP address of the target (e.g. `8.8.8.8`) |

**Example:**
```
Version: 4, IHL: 5 (20 bytes), Total Length: 60
TTL: 64, Protocol: 6 (TCP)
Source IP:      10.42.0.10
Destination IP: 8.8.8.8
```

---

## Anatomy of a Segment (Layer 4)

A TCP segment is the unit of data for reliable end-to-end delivery between processes.

**TCP Header:**

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
│          Source Port          │        Destination Port       │
├───────────────────────────────┼───────────────────────────────┤
│                       Sequence Number                         │
├───────────────────────────────────────────────────────────────┤
│                    Acknowledgment Number                      │
├───────┼───────┼─┼─┼─┼─┼─┼─┼───┼───────────────────────────────┤
│Offset │Reserv │U│A│P│R│S│F│   │           Window Size         │
├───────┴───────┴─┴─┴─┴─┴─┴─┴───┼───────────────────────────────┤
│          Checksum             │        Urgent Pointer         │
└───────────────────────────────┴───────────────────────────────┘
```

| Field | Description |
|-------|-------------|
| Source Port | Port on the sending machine (e.g. `54321` — ephemeral/random) |
| Destination Port | Port on the receiving machine (e.g. `80` for HTTP, `22` for SSH) |
| Sequence Number | Byte position in the stream (used for ordering and retransmission) |
| Flags | SYN (start connection), ACK (acknowledge), FIN (close), RST (reset), PSH (push) |
| Window Size | How much data the receiver can accept (flow control) |

**TCP 3-way handshake (connection establishment):**
```
Client                          Server
  │                                │
  │──── SYN (seq=100) ───────────→│   "I want to connect"
  │                                │
  │←─── SYN-ACK (seq=300,ack=101)─│   "OK, I acknowledge your SYN"
  │                                │
  │──── ACK (seq=101,ack=301) ───→│   "Got it, connection established"
  │                                │
```

---

## Full Example: HTTP Request Through the Layers

A device at `10.42.0.10` (on the lab network) opens `http://google.com` in a browser. Here's what happens at each layer:

### 1. Application Layer (HTTP)

The browser constructs an HTTP request:
```
GET / HTTP/1.1
Host: google.com
```

### 2. Transport Layer (TCP)

TCP wraps the HTTP data in a segment:
```
Source Port: 54321 (random ephemeral port)
Destination Port: 80 (HTTP)
Sequence: 1, Flags: PSH+ACK
Payload: "GET / HTTP/1.1\r\nHost: google.com\r\n\r\n"
```

### 3. Network Layer (IP)

IP wraps the TCP segment in a packet. DNS has already resolved `google.com` → `142.250.179.110`:
```
Source IP: 10.42.0.10
Destination IP: 142.250.179.110
TTL: 64, Protocol: TCP (6)
Payload: [TCP segment from above]
```

### 4. Data Link Layer (Ethernet)

The device's IP stack checks: "Is `142.250.179.110` on my local subnet (`10.42.0.0/20`)?" — No. So it sends the frame to its **default gateway** (`10.42.0.1` = the Pi router). It looks up the router's MAC via ARP:
```
Destination MAC: dc:a6:32:xx:xx:xx  (Pi router's MAC)
Source MAC: aa:bb:cc:dd:ee:ff       (this device's MAC)
EtherType: 0x0800 (IPv4)
Payload: [IP packet from above]
FCS: [calculated checksum]
```

### 5. Physical Layer

The frame is converted to electrical signals on the Ethernet cable and sent to the switch on port 2.

### 6. At the Switch (Layer 2)

The switch receives the frame, reads the destination MAC (`dc:a6:32:xx:xx:xx`), looks it up in its MAC table → port 1 (the router). It forwards the frame out port 1. The switch never looks at the IP address or TCP port — it only cares about MAC addresses.

### 7. At the Pi Router (Layer 3)

The router receives the frame, strips the Ethernet header, and reads the IP packet. Destination is `142.250.179.110` — not local. It consults its routing table: default route → `eth0` → ISP modem at `192.168.2.254`.

The router:
1. Decrements TTL (64 → 63)
2. Applies NAT: rewrites source IP from `10.42.0.10` → `192.168.2.59` (router's WAN IP) and tracks the mapping
3. Builds a new Ethernet frame with the ISP modem's MAC as destination
4. Sends it out `eth0`

The process continues through the ISP modem (another NAT), across the internet (many routers/hops), until it reaches Google's server. The reply follows the reverse path, with NAT tables at each stage rewriting the destination back to the original device.

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

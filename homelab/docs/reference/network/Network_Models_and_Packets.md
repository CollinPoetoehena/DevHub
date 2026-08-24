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
  - [Anatomy of a Segment (Layer 4)](#anatomy-of-a-segment-layer-4)
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

### Anatomy of a Segment (Layer 4)

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
  │                               │
  │──── SYN (seq=100) ───────────→│ "I want to connect"
  │                               │
  │←─── SYN-ACK (seq=300,ack=101)─│ "OK, I acknowledge your SYN"
  │                               │
  │──── ACK (seq=101,ack=301) ───→│ "Got it, connection established"
  │                               │
```

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

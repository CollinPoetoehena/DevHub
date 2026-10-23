# Network Modes and Virtual Connectivity

A network mode describes how a guest, container or device connects to other networks. Choose it by the traffic path and trust boundary needed, not by a familiar label: **bridge**, **host-only** and **host networking** do not mean the same thing.

This page explains reusable concepts and trade-offs. For home-scale choices and recovery considerations, see the public [homelab network chapter](https://github.com/CollinPoetoehena/devhub-homelab/blob/main/docs/02-architecture/network.md#vm-and-container-network-attachment). Product labels and defaults vary; the [official references](#official-references) own exact configuration and platform limitations.

---

## Table of Contents

- [First Identify Which Layer](#first-identify-which-layer)
- [Virtual Machine Attachment Modes](#virtual-machine-attachment-modes)
  - [Bridged Attachment](#bridged-attachment)
  - [NAT and Routed Attachment](#nat-and-routed-attachment)
  - [Host-Only, Internal and Disconnected](#host-only-internal-and-disconnected)
- [Container Network Modes](#container-network-modes)
  - [Bridge Versus Host Networking](#bridge-versus-host-networking)
  - [Direct LAN Attachment and Overlays](#direct-lan-attachment-and-overlays)
- [Overlay and Underlay Networks](#overlay-and-underlay-networks)
  - [Following a VXLAN Packet](#following-a-vxlan-packet)
  - [Encapsulation Versus Native Routing](#encapsulation-versus-native-routing)
  - [MTU, Policy and Troubleshooting](#mtu-policy-and-troubleshooting)
- [Choosing and Verifying a Mode](#choosing-and-verifying-a-mode)
- [Official References](#official-references)

---

## First Identify Which Layer

These are related mechanisms, not interchangeable settings:

| Term | Meaning | What it does not establish |
|---|---|---|
| ISP gateway bridge mode | Passes the provider connection toward a downstream router instead of supplying the usual gateway routing/NAT functions | Compatibility with provider authentication, TV/voice or IPv6 delegation; vendor "passthrough" may behave differently |
| Router mode | Routes between subnets, commonly with firewall, DHCP and IPv4 NAT services | That NAT is required for routing, or that the configured firewall policy is appropriate |
| Access-point / bridge mode on Wi-Fi equipment | Connects wireless clients to an existing wired network rather than creating another routed network | Guest isolation, VLAN mapping or identical behavior across vendors; verify which routing/DHCP services are disabled |
| VM bridged attachment | Connects a guest's virtual NIC to a software switch, optionally with a physical uplink | Routing, NAT, encryption or isolation from other endpoints on that segment |
| Container bridge driver | Connects separate container network namespaces through a software bridge; a runtime can add routing, NAT and port publishing | Direct attachment to the physical LAN; Docker's usual bridge network is an internal subnet, not an uplinked VM bridge |
| VLAN / access / trunk membership | Determines which Layer 2 segment an interface or bridge port carries | Another NAT mode or an access policy between every pair of endpoints |
| Bond / link aggregation | Combines physical links for supported redundancy or capacity goals | A new trust boundary or guaranteed multiplication of a single connection's throughput |

A bridge is a Layer 2 switch in software. A router forwards between Layer 3 networks. NAT translates addresses, while a firewall permits or denies traffic. These functions can coexist on one host but should be designed separately. See [network devices](./Network_Devices.md), [VLANs and tagged Ethernet](./VLANs.md), [addressing and NAT](./Subnets_and_IP_Addresses.md), and [network design](./Network_Design.md).

All diagrams below are synthetic traffic-path sketches, not configurations or evidence of working isolation. Lines show attachment or a possible path, not permission for unrestricted traffic.

---

## Virtual Machine Attachment Modes

| Mode | How it works | Benefits | Drawbacks / responsibilities | Typical use |
|---|---|---|---|---|
| Bridged to an uplink | Guest NIC joins a virtual switch connected to a physical NIC or selected VLAN | Guest has its own address on the selected LAN; ordinary clients can reach it subject to policy; useful protocol visibility | Guest becomes a peer on that segment, including possible DHCP/RA broadcasts. Wi-Fi bridging and upstream multiple-MAC restrictions vary. Maintain VLAN membership, guest/host filtering and address ownership | Servers or cluster nodes intended to participate in a real network |
| Per-VM NAT | Hypervisor translates a guest's outbound traffic through the host; exact implementation varies | Convenient outbound access with little upstream configuration | Unsolicited inbound access usually needs forwarding; outbound traffic may still reach sensitive LAN services. In VirtualBox's plain NAT mode, separate VMs do not share a guest network by default. Maintain forwards and check platform limitations | A standalone development VM needing downloads, not direct LAN presence |
| Shared NAT network | Multiple guests share a private virtual subnet with NAT egress | Guests communicate with each other and obtain outbound access without upstream routes | Shared peers can reach one another; inbound publishing and another NAT layer add diagnosis work. Maintain subnet allocation, DHCP/DNS, forwards and egress rules | A small multi-VM application or test cluster with outbound dependencies |
| Routed subnet without NAT | Guests use a separate subnet; the host or a router forwards it without changing addresses | Clear source addresses and controlled inbound/outbound routing without another translation layer | Upstream return routes, IP forwarding and firewall policy must agree; providers may restrict routed addresses. Maintain routes and rules across reboots and subnet changes | Routing exercises or managed networks with control over upstream routes |
| Host-only | Private virtual network connects selected guests and a host-side interface, normally without an external uplink | Host can administer guests while the test segment stays off the physical LAN | The host is reachable and therefore part of the trust boundary. Host forwarding or a second guest NIC can create an external path. Maintain host filtering and check for accidental forwarding | Development/test services requiring access from the workstation |
| Internal / isolated switch | Guests share a virtual switch with no physical uplink and no host-side IP interface | Guest-to-guest exercises without ordinary host or LAN connectivity | No outside updates or administration over that segment; a router VM or another NIC can reintroduce access. Maintain membership and any internal DHCP/DNS. Hypervisor terminology varies | Contained routing, DHCP or protocol experiments |
| Disconnected / no NIC | Virtual cable disconnected, or network adapter absent | Simple way to test link loss or run a network-independent workload | No network administration or downloads; disabling one NIC leaves any other NICs active. Maintain console/file-transfer access | Offline processing and failure tests |

### Bridged Attachment

```text
                         +-- host-side IP (if configured)
                         |
Guest A NIC --+-- virtual bridge -- physical NIC -- switch / selected LAN
Guest B NIC --+
```

With an uplink, guests usually get addresses from that LAN's DHCP server or from its address plan. The bridge itself does not need an IP to switch frames; a host-side IP is a separate management choice. A VLAN-aware bridge can carry multiple segments, but a guest should receive only the memberships it requires.

Two guests on the same bridge/segment may exchange traffic locally without traversing the physical gateway. Do not assume that gateway firewall rules inspect it. Bridging a second physical NIC or guest interface into the wrong segment can also join networks that were meant to stay separate.

### NAT and Routed Attachment

```text
NAT:
Guest A --+
Guest B --+-- private switch -- router + source NAT -- upstream LAN
                                  ^
LAN client -- selected forwarded port (only if configured and allowed)

Routed, no NAT:
Guest subnet -- forwarding router + firewall -- upstream LAN
                         ^
             upstream needs a return route to the guest subnet
```

Outbound NAT commonly makes the upstream see the translator's address rather than the guest's. A port forward creates a selected inbound path; it is not necessary for replies to an established outbound connection. Return routing and firewall permissions are still required without NAT.

**NAT is not a containment policy.** Guests may initiate connections to upstream private networks unless filtering prevents it. Additional translation can complicate inbound access, VPNs and diagnostics. Treat IPv6 routing, Router Advertisements and filtering explicitly rather than assuming an IPv4 NAT setting controls IPv6 too.

### Host-Only, Internal and Disconnected

```text
Host-only:
Host interface -- private switch -- Guest A
                         +-------- Guest B
                         X no physical uplink by default

Internal / isolated:
Guest A -- private switch -- Guest B
                 X no host IP interface or physical uplink

Disconnected:
Guest NIC -- X virtual cable disconnected
```

Here `X` marks an absent path, not a firewall rule. "Host-only" is not container "host networking": the former normally uses a private guest network; the latter shares the host's network namespace.

An isolated network is not a sandbox against hypervisor compromise, shared-folder access or deliberate host reconfiguration. A dual-homed guest, host forwarding or a newly attached uplink changes the boundary. Inspect all adapters, not just the mode of the first one.

---

## Container Network Modes

The examples here use Docker Engine terminology on Linux. Desktop, rootless runtimes and other container platforms can use different paths and restrictions; do not infer their behavior from a Linux-host diagram.

| Mode | How it works | Benefits | Drawbacks / responsibilities | Typical use |
|---|---|---|---|---|
| User-defined bridge | Containers have separate network namespaces on a host-local bridge; Docker normally supplies DNS, outbound masquerading and explicit port publishing | Simple application grouping, container-name resolution and selected host-port entry points | Peers on the same network can normally reach each other's listening ports. Publication can expose services on more host addresses than intended; maintain subnet allocation, bindings and runtime firewall interactions | Ordinary single-host application stacks |
| Host | Container shares the host network namespace rather than receiving a separate container IP | Avoids that extra bridge/NAT path; convenient when host-level networking is explicitly required | Reduced network isolation, access to host-local services and port conflicts; published-port mappings do not apply. Maintain host firewall and listener bindings; verify platform support | A workload with a demonstrated need for host networking, not a default performance shortcut |
| None | Only loopback is created in the container network namespace | No ordinary external container networking | No remote dependencies; shared files and other privileges are unaffected. Maintain offline inputs and verify no extra interfaces are introduced | Network-independent jobs |
| Macvlan | Containers attach through a parent interface with individual MAC and IP addresses | Direct presence on the selected LAN without host-port mapping; supports applications needing LAN identities | Upstream must support multiple MACs; Linux host-to-container communication is restricted by default. Maintain unique address allocation, parent/VLAN choice and a deliberate host-access design | A specific LAN-presence or legacy-protocol requirement |
| IPvlan | Containers use individual IPs but share the parent interface's MAC; L2 and L3 variants differ | Reduces upstream MAC usage; integrates container addresses with an underlay | Host communication is restricted by default; L3 requires appropriate routing and does not carry ordinary broadcast/multicast like L2. Maintain routes, addressing and policy for the selected variant | Controlled networks needing direct addressing with fewer MACs |
| Overlay | Encapsulates traffic between hosts so workloads share a logical network across them | Multi-host connectivity without exposing every workload as a LAN peer | Underlay reachability, MTU, control plane and policy still need management; an overlay is not inherently encrypted. Docker's driver requires Swarm membership even for standalone containers. Maintain tunnel paths, cluster membership and encryption settings | Multi-host applications using a platform that supplies and manages the overlay |

Docker also creates a default network named `bridge`. Its behavior differs from user-defined bridges, including container-name DNS resolution. Prefer explicit application networks rather than attaching unrelated stacks to that shared default; consult the [bridge driver documentation](https://docs.docker.com/engine/network/drivers/bridge/).

### Bridge Versus Host Networking

```text
Docker bridge (usual Linux NAT path):
Container A --+
Container B --+-- internal bridge -- host routing/NAT -- host NIC -- LAN
LAN client -------- host published port --------> selected container port

Host networking (Linux):
Container process -- host network namespace -- host NIC -- LAN
Host process ------+   shared IPs, routes and listening-port space
```

A container can listen on a port without that port being published to the LAN. Conversely, publishing a port does not make it private: check which host addresses it binds to and the actual firewall path. Docker may manage forwarding rules itself; a host firewall's input policy alone is not proof that a published container port is blocked.

### Direct LAN Attachment and Overlays

```text
Direct LAN attachment:
Container A (IP A) --+-- parent NIC -- selected LAN
Container B (IP B) --+
  macvlan: distinct MAC per container
  ipvlan L2: parent MAC shared across container IPs
```

Macvlan/ipvlan are not automatic security upgrades: direct LAN presence changes exposure, and traffic does not necessarily follow the ordinary bridge/NAT firewall path. For multi-host transport, see [Overlay and Underlay Networks](#overlay-and-underlay-networks) below. Kubernetes networking may use an overlay or native routing; it is not the same setting as selecting Docker's overlay driver.

Sharing another container's network namespace is another attachment pattern, not a new bridge or physical segment: the processes share interfaces, localhost and port space. Likewise, NIC passthrough and SR-IOV change device ownership rather than supplying a firewall policy; consult the hypervisor's hardware/isolation requirements before choosing them.

---

## Overlay and Underlay Networks

The **underlay** supplies connectivity between transport endpoints: links, switches, routers, addressing, routes, firewalls and the available path MTU. The **overlay** supplies a logical network on top, commonly by wrapping workload traffic in another packet between tunnel endpoints. An overlay can span hosts that are not on the same Ethernet segment.

These terms are relative layers, not synonyms for "physical" and "virtual." An underlay can include hypervisor switches or a cloud virtual network, and a VPN can carry another overlay. The important question is which network must work before the next layer can carry traffic.

| Aspect | Underlay | Overlay |
|---|---|---|
| Endpoint identity | Transport/node or tunnel-endpoint addresses | Workload addresses and logical segment identifiers |
| Forwarding | Delivers the outer packet to the remote endpoint | Delivers the inner traffic to its logical destination after decapsulation |
| What ordinary transit devices see | Outer headers and tunnel traffic; not necessarily inner workload identity | Overlay-aware endpoints can inspect inner traffic and segment membership |
| Operational dependency | Reachability, return routes, link capacity, MTU and permitted tunnel protocols | Endpoint mappings, segment membership, workload routes/policy and a functioning underlay |

An overlay does not repair broken underlay routing, add physical capacity or create an independent failure domain. Multiple overlays sharing one uplink still compete for that uplink.

### Following a VXLAN Packet

VXLAN is one example: it carries an inner Ethernet frame inside UDP/IP between **VXLAN Tunnel Endpoints (VTEPs)**. The VXLAN header contains a **24-bit VNI** identifying a logical segment. The VTEPs may be implemented in host software or network equipment.

```text
Logical overlay segment:
Workload A ---- local bridge/VTEP A ................ VTEP B/local bridge ---- Workload B
                         |                             |
                         +--- routed IP underlay ------+
                              switches / routers

On an underlay link (simplified, not to scale):
[outer Ethernet][outer IP: VTEP A -> VTEP B][UDP][VXLAN: VNI][inner Ethernet frame]
                                                           |
                                              workload IP + transport + data
```

1. Workload A sends a frame onto its local logical network.
2. VTEP A identifies the segment and remote destination, then encapsulates the frame for VTEP B.
3. Transit routers forward using the **outer destination IP**. They need a path to VTEP B, not necessarily a route to Workload B.
4. VTEP B decapsulates and forwards within the appropriate logical segment, subject to local membership and policy.

The underlay Ethernet header can change at routed hops; the carried frame is payload until decapsulation. Same-host workload traffic may be switched locally without entering a tunnel.

Endpoint discovery and forwarding information still need an owner. Implementations can use static entries, learning/flooding, multicast or a control plane such as EVPN; these are not interchangeable defaults. **VXLAN is a data-plane encapsulation; EVPN is a control-plane approach**, not a second name for the tunnel. Consult the chosen platform rather than manually combining incompatible mechanisms.

A VNI is not a VLAN ID, and neither is an IP subnet. A platform can map a local VLAN to a VNI without matching their numbers; ordinary underlay switches need not carry every workload VLAN. See [VLANs versus overlays](./VLANs.md#vlans-versus-overlays).

### Encapsulation Versus Native Routing

| Approach | Benefits | Drawbacks / responsibilities | When it fits |
|---|---|---|---|
| Local VLANs and ordinary routing | Familiar Ethernet membership and explicit subnet routing; no tunnel overhead | VLAN membership must span required Layer 2 paths; routed boundaries need policy. Maintain trunks, routes and failure-domain awareness | Local networks whose segmentation and scale fit ordinary switching/routing |
| Encapsulated overlay, such as VXLAN | Decouples logical segments from underlay VLAN layout; carries workload networks across routed transport without teaching each transit router every workload route | Additional headers, endpoint state and another diagnostic layer; stretching Layer 2 can also spread broadcasts and failures. Maintain tunnel reachability, MTU, mappings and policy | Multi-host or multi-tenant networks where logical placement should not follow physical attachment |
| Native workload routing | Forwards workload IP traffic without this tunnel encapsulation; simpler packet visibility and no tunnel-specific MTU cost | Connected networks need suitable routes and return paths, possibly distributed by BGP; source-address checks and provider constraints must permit it. Maintain route distribution and filtering | A platform and underlay designed to carry workload prefixes directly |

Not every logical workload network requires a tunnel. Kubernetes CNI implementations may offer encapsulation, native routing or combinations; a Service virtual IP is not automatically a VLAN or tunnel segment. Conversely, a VPN can be an overlay without being a VXLAN Layer 2 network.

### MTU, Policy and Troubleshooting

Encapsulation consumes packet budget. **For plain VXLAN over outer IPv4, carrying a 1500-byte inner IP packet requires an underlay IP MTU of at least 1550 bytes**: 1500 inner IP + 14 inner Ethernet + 8 VXLAN + 8 UDP + 20 outer IPv4. With an outer IPv6 header instead, the corresponding baseline is 1570 bytes. These figures exclude extra inner VLAN tags, IP options/extensions, encryption and additional tunnels; do not apply them universally.

With a 1500-byte underlay IP MTU, the corresponding plain outer-IPv4 example typically needs an inner IP MTU no greater than 1450. Outer Ethernet framing is outside the underlay *IP* MTU, but the physical links must still support the resulting frame size. Configure the platform's supported MTU behavior consistently across the path; jumbo frames on one host do not fix a smaller intermediate link.

Small packets may work while larger transfers stall. Check path MTU discovery and required ICMP error delivery, not just ping reachability; do not rely on fragmentation or TCP MSS adjustment as a universal fix for UDP and other traffic.

Keep **transport policy** and **workload policy** separate. Permitting a tunnel between approved endpoints does not permit every inner application flow. An underlay firewall may see only endpoint-to-endpoint packets, while workload policy belongs at overlay-aware enforcement points. VXLAN is not encryption or endpoint authentication; restrict tunnel access to trusted participants and choose separate protection where needed.

Troubleshoot in dependency order:

1. Verify underlay addresses, routes, return paths and endpoint reachability independently of workload access.
2. Check the actual tunnel protocol/ports and endpoint configuration. VXLAN's assigned UDP destination port is 4789, but implementations can use a different configured value.
3. Check VNI membership, forwarding/endpoint mappings and workload addressing at both ends.
4. Compare captures before encapsulation, on the transport path and after decapsulation. Use the [packet-analysis toolkit](./commands/packet_capture_analysis.md); host offloads can change what captures appear to contain.
5. Test larger payloads and real application flows in both directions and every enabled IP family; validate intended denials separately from connectivity.
6. Recheck after node replacement, route/plugin changes or adding another tunnel layer. Keep the underlay management/recovery path usable when the overlay is down.

---

## Choosing and Verifying a Mode

1. **Define reachability first:** guest-to-guest, host-to-guest, LAN-to-service, outbound dependencies and forbidden destinations.
2. **Choose the narrowest attachment that meets it:** disconnected for offline work, internal for guest-only exercises, host-only for host access, NAT for convenient egress, bridged/routed for deliberate network participation.
3. **Plan ownership:** who supplies addresses, DHCP, DNS, routes and policy? Check overlap with LANs, VPNs and other virtual networks.
4. **Trace both directions:** identify the forward and return paths, any NAT/port publication, and where permitted and denied traffic is enforced.
5. **Verify rather than infer:** test an authorized application connection and the same denied connection from another role; inspect listeners, routes, bridge/VLAN membership and packet captures as needed.
6. **Check every adapter and IP family:** a second NIC or IPv6 path can defeat an IPv4-only assumption. Recheck after reboot, runtime updates or changing a mode.
7. **Keep recovery independent:** changing a host bridge can disconnect the session used to repair it. Retain console access and a known-good rollback path.

Use the [network command toolkit](./commands/README.md) for diagnostics and the [network design verification guidance](./Network_Design.md#verification-and-maintenance) for policy checks. Successful internet access alone proves neither correct segmentation nor safe publishing.

---

## Official References

- [RFC 7348: VXLAN](https://www.rfc-editor.org/rfc/rfc7348.html) describes encapsulation, VNI, underlay MTU considerations and security limits; [Linux VXLAN documentation](https://docs.kernel.org/networking/vxlan.html) explains the Linux implementation and endpoint forwarding.
- [VirtualBox virtual networking](https://www.virtualbox.org/manual/ch06.html) explains per-VM NAT, NAT Network, bridged, internal, host-only and disconnected modes; these names are not universal hypervisor APIs.
- [Proxmox VE network configuration](https://pve.proxmox.com/wiki/Network_Configuration) describes Linux bridges, routed and masquerading/NAT designs, VLANs and bonds.
- [Docker network drivers](https://docs.docker.com/engine/network/drivers/) provides the driver overview; see [bridge](https://docs.docker.com/engine/network/drivers/bridge/), [host](https://docs.docker.com/engine/network/drivers/host/), [none](https://docs.docker.com/engine/network/drivers/none/), [macvlan](https://docs.docker.com/engine/network/drivers/macvlan/), [ipvlan](https://docs.docker.com/engine/network/drivers/ipvlan/) and [overlay](https://docs.docker.com/engine/network/drivers/overlay/) for requirements and limitations.

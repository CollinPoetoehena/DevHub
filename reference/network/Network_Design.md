# Network Design

General network architecture and security-design principles: define responsibilities, trust boundaries, permitted flows, and recovery paths before selecting equipment or configuring services. These principles apply across physical, virtual, and cloud environments; the implementation depends on the requirements and available enforcement mechanisms.

For their application at home scale, see the public [homelab network guide](https://github.com/CollinPoetoehena/devhub-homelab/blob/main/docs/2_HLD/Network/README.md). It owns household/lab isolation examples, router arrangements, equipment choices, placement, and recovery trade-offs rather than repeating this general reference. The [repository relationship](https://github.com/CollinPoetoehena/devhub-homelab/blob/main/README.md#how-devhub-and-the-homelab-repositories-fit-together) explains the division between reusable principles, public examples, and private implementation records.

---

## Table of Contents

- [Layered Design](#layered-design)
- [Segmentation and Access](#segmentation-and-access)
  - [Trust Roles and Minimum Access](#trust-roles-and-minimum-access)
  - [Routing, Gateway Services and Local Traffic](#routing-gateway-services-and-local-traffic)
  - [Addressing and VLAN Membership](#addressing-and-vlan-membership)
- [Trust Zones and Traffic Flow](#trust-zones-and-traffic-flow)
- [Verification and Maintenance](#verification-and-maintenance)

---

## Layered Design

Use **edge, core, distribution and access** as responsibilities, not a requirement to buy a separate enterprise switch for each layer.

- **Edge:** upstream/provider connectivity, external routing, and perimeter policy.
- **Core:** backbone connectivity between major network parts.
- **Distribution:** aggregates access links and places routing/policy where designed.
- **Access:** classifies endpoint connections into intended networks.

The layers make **ownership and traffic paths** visible. Draw where clients enter, where trunks aggregate, where routing happens, and which device or service enforces policy. Several responsibilities can be collapsed into shared infrastructure when capacity, failure impact, and operations allow it. Logical layers do not create independent failure domains.

If a Layer 3 switch routes traffic, a perimeter firewall does not automatically inspect it. The same consideration applies to virtual switches, workload overlays, and cloud routing: enforcement must be placed on the actual traffic path. Start with responsibilities and dependencies, then select the components that implement them rather than copying an enterprise three-tier diagram with unused boxes.

---

## Segmentation and Access

Choose segments according to trust, asset sensitivity, required services, and the consequences of compromise. Separate administration, ordinary clients, application workloads, untrusted devices, visitors, or exposed services when they need different policies. A functional name alone does not establish the appropriate trust boundary.

VLANs separate Layer 2 domains, not availability or all communication. Same-VLAN traffic may never cross a gateway. Protect router services separately from forwarded traffic; namespaces, NAT, and SSID names are not firewall isolation. Use the [device and VLAN reference](./Network_Devices.md#vlan-virtual-lan) for the underlying mechanisms.

Use non-overlapping address ranges and explicit access/trunk membership. Match native/tagged settings along links and limit trunks to required segments. Include connected sites, VPNs, and container/pod/service networks in overlap checks. Plan IPv6 prefix allocation and equivalent policy/control traffic before enabling it; an explicitly documented IPv4-only baseline can be appropriate while that is unresolved.

### Trust Roles and Minimum Access

List each role's assets, dependencies, and allowed initiators before writing rules. An administrator may need a management service without needing access to every workload; an application may need one database API without needing general access to the data network.

Prefer an explicit allowed-flow matrix over dozens of undocumented exceptions. Record source role or identity, destination service, protocol/port, purpose, enforcement point, and owner. Default-deny unnecessary new cross-boundary traffic while preserving approved replies and required infrastructure services. Review egress as well as ingress: a compromised exposed service should not inherit unrestricted internal or Internet access.

A DMZ is a controlled network segment, **not** a consumer-router "DMZ host" feature that forwards broad unsolicited WAN traffic to one machine. Publish only required services, not router/hypervisor administration. Restrict DMZ-initiated access to other segments and review outbound dependencies. Segmentation does not replace application patching, authentication, host isolation, or backups.

### Routing, Gateway Services and Local Traffic

Treat traffic **through** a firewall separately from traffic **to** the gateway. An inter-segment block may not stop a client reaching the router console; DHCP/DNS permissions should not grant unrestricted management. Same-segment flows may bypass the routed firewall entirely, requiring host firewalls, device controls, or supported client isolation.

Service discovery such as mDNS is a deliberate cross-boundary feature. Allow it narrowly only when needed, and distinguish discovering a device from permission to connect to it. NAT hides or translates addresses; it does not replace an access policy. Host bridges and multi-homed systems must not accidentally join otherwise separated trust networks.

### Addressing and VLAN Membership

Use an address plan that does not overlap connected networks, remote-access sites, or workload-platform ranges. Size each subnet for its role; the VLAN ID does not have to match an address octet. Reserve infrastructure addresses and keep static allocations outside dynamic pools or represented by appropriate reservations. See [subnets and addressing](./Subnets_and_IP_Addresses.md) for the underlying theory.

Access ports usually carry one untagged client segment. Trunks carry only the tagged networks required by a switch, AP, or hypervisor, with an explicitly agreed native/untagged behavior. A native mismatch or unrestricted host trunk can defeat an otherwise good design. Management over tags versus untagged access is a platform/port-design decision, not a universal rule.

IPv6 requires a plan for allocated/delegated prefixes, addressing, DNS, router advertisements, and policy. Multiple addresses and global reachability do not imply that all inbound traffic should be allowed. Preserve essential ICMPv6/control traffic and verify both allowed and denied paths; disabling all ICMP is not a safe substitute for understanding it.

---

## Trust Zones and Traffic Flow

> Trust boundaries deserve detailed design: a convenient traffic path can also become an unintended route to sensitive data or privileged management.

A useful way to reason about a network is to group systems into **zones by trust and purpose**, then define which connections may cross each boundary. A zone is a policy boundary, not simply a label for a device type or a guarantee that every system inside it is safe. The colors below are mnemonic labels for this generic example only; they are not a standard, a prescribed number of networks, or a representation of any real network. "External" is relative to the specific protected environment, not to who owns the originating network: a remote employee, customer, partner, or another organization-owned network can still be external when traffic crosses into a separate security domain. Ownership does not prove that a device or connection is uncompromised.

| Illustrative zone | Role and typical systems | Typical reachability and traffic path | Policy intent |
|---|---|---|---|
| **Black — external / untrusted** | Networks, systems, and users outside the defined protected environment. This can include the public Internet, remote users, customer or partner networks, and separately administered networks owned by the same organization. | May initiate connections only to explicitly published services or separately approved access gateways. It is not an internal zone simply because its operator is familiar or has the same organizational owner. | Treat incoming traffic as untrusted; monitor and inspect it at appropriate boundaries. Where the threat and service justify it, upstream filtering or traffic-scrubbing services may help absorb attacks before they reach the service edge; their availability and behavior depend on the provider and design. |
| **Upper Red — external-facing DMZ** | The outer part of a Red/DMZ boundary. Typical systems include public-facing reverse proxies, web application firewalls, load balancers, TLS termination points, and other edge services. | Receives the deliberately published connections from Black and terminates, validates, or filters them. It may pass only specifically allowed application flows toward Lower Red, or toward a narrowly scoped application endpoint if the design has no Lower Red tier. | Expose only the required service interfaces. Do not treat traffic as trusted just because it reached this tier; constrain both inbound and onward connections, protect the components themselves, and avoid routes to Green or Blue management interfaces. |
| **Lower Red — internal-facing DMZ** | An optional inner part of the Red/DMZ boundary, placed between the external-facing edge and internal application services. It can host or connect to components that relay already-filtered service traffic inward. | Accepts only specified traffic from Upper Red and forwards only approved service flows toward Orange. It may also support narrowly defined internal service access, but must not become a general bridge between external and internal networks. | Enforce a separate policy boundary from Upper Red. Where a system has interfaces in both Red tiers, carefully restrict and inspect forwarding; do not bridge the interfaces or assume that filtering at Upper Red makes all onward traffic safe. |
| **Orange — application** | Application-tier systems that implement service or business logic, such as application and API servers, middleware, backend services, and data stores whose classification permits this tier. | Receives only the service calls required from an approved Red edge or other explicitly authorized client. It may initiate narrowly scoped requests to Green for data needed by the application; responses should return to the authorized requester. It has no direct Black-facing service path in this model. | Keep application services behind the service edge. Allow only required protocols, destinations, and identities; do not use Orange as an unrestricted transit path between Red and Green or between unrelated applications. |
| **Green — protected data** | Systems holding sensitive, confidential, personal, or otherwise higher-classification data, commonly databases or protected storage services. | Accepts only the specific data operations required from authorized Orange services and separately approved Blue management paths. External clients and Red edge systems do not connect directly to Green in this model. | Minimize reachable systems and permitted operations. Apply data-layer authentication and authorization as well as network controls; an allowed application connection does not mean that the application should have unrestricted access to every record or operation. |
| **Blue — privileged management** | A logical management-connectivity zone for approved administrators, secured access systems, and management tooling used to operate systems across the other zones. It is not an ordinary end-user network. | Administrators enter through a separately secured and authorized access path; management tools then reach only the specific management interfaces and targets they are responsible for. The required route can differ by system and may use controlled stepping-stone access rather than direct administrator connectivity. | Treat management as privileged, not inherently safe. Require appropriate identity assurance and authorization, protect administrator endpoints and tooling, log sensitive actions, and limit each path to necessary targets and operations. |

The table describes **common roles and candidate paths, not automatic reachability**. A zone being mentioned as a possible source does not mean every system in it may connect to every system in another zone. Define who may initiate each connection, the destination service and protocol, the enforcement point, and the expected response path. Apply a least-privilege policy to traffic in both directions; stateful return traffic for an approved connection is different from allowing the destination to start an unrelated new connection.

Red can be implemented as one DMZ segment or split into **Upper Red** and **Lower Red**. When split, Upper Red faces Black and hosts the externally reachable edge; Lower Red is the internal-facing tier that relays only explicitly filtered traffic toward Orange. The split can make the boundary and review of permitted flows clearer, but requires additional interfaces, rules, monitoring, and maintenance. It is useful only when the risk model and operational capacity justify those costs. Separate segments or other controls must enforce the boundary: the tier names alone do not provide isolation. Any system connected to more than one zone needs special scrutiny because a compromised or misconfigured multi-homed host can become a path around the intended controls.

Traffic from Black should be monitored and inspected at suitable points because it crosses a trust boundary. Depending on the exposure and threat model, protection may include rate limiting, application-layer filtering, or upstream DDoS mitigation; these are design choices, not properties guaranteed by a zone label. Filtering should not be confused with reachability: security controls can observe or reject a flow without granting it access to the next zone. Normal routing and any mitigation path, including its capacity and operational ownership, should be understood and tested where applicable.

```text
 BLACK: external to the protected environment
 Internet, remote users, customer/partner or other separately managed networks
                           |
             published service / approved access only
                           v
 UPPER RED: external-facing DMZ edge
 proxy / WAF / load balancer -> terminate, inspect, filter
                           |
       only explicitly permitted service traffic
                           v
 LOWER RED: internal-facing DMZ tier (optional)
       relay only the authorized application flow
                           |
             only required application calls
                           v
 ORANGE: application / service logic
                           |
        specifically authorized data operations
                           v
 GREEN: protected data

 BLUE: privileged management (separate logical access plane)
 approved administrator -> secured access path -> authorized target
                     -> specific management interface / operation

 No direct Black-to-Green path in this model. Deny unneeded new
 inter-zone connections; document and test every exception.
```

This is a representative request path, not a complete topology or universal rule set. When Lower Red is used, an external request is terminated or filtered in Upper Red, then only an approved service flow is relayed through Lower Red to Orange. In a simpler design without Lower Red, permit only the required edge-to-application flow; do not interpret that as permission for all Red systems to reach all Orange systems. Orange can query Green only for the specific data and operations needed by the service. Green replies to those authorized requests; that response path does not grant Green broad access to Orange. No direct Black-to-Green connection is part of this model.

Blue is shown separately because administrative access is not an ordinary application path. A secured administrator or management tool may need carefully controlled interfaces in several zones, but should reach only approved targets and operations. Do not expose management interfaces through the public service edge. The secure access method, identity checks, approval requirements, and logging depend on the environment and must be designed explicitly.

Segmentation limits which paths are available and can reduce lateral movement, but it does not make compromise harmless. An exposed edge service can still be vulnerable; an attacker who compromises an application may be able to use that application's permitted Green access; and an allowed management path can still be abused. Use network controls alongside host and application isolation, strong identity and authorization, least privilege, monitoring, patching, and recoverable backups. Do not assume that placing a database in Green makes its data safe if the application in Orange can retrieve it without appropriate authorization.

The policy must be enforced at a point that actually sees the traffic. Same-segment traffic, Layer 3 switching, host bridges, and platform overlay networks may bypass a perimeter firewall. Choose enforcement points for each path, account for both IPv4 and IPv6, preserve necessary stateful replies and infrastructure services, and verify allowed **and denied** flows from representative systems. A VLAN, a firewall zone name, or a diagram alone does not enforce access policy.

Use the model as a starting point for a network design: identify the assets and trust assumptions in each zone, map required service and management flows, choose the enforcement point, and state what must remain unreachable. Keep privileged management and recovery paths usable during outages or changes. Document each exception with its owner and purpose, then test that it works as intended and that neighboring, unapproved paths remain blocked. The [segmentation and access guidance above](#segmentation-and-access) covers trust roles, routing, and VLAN considerations.

---

## Verification and Maintenance

Check dependencies, routing, permitted services, intended denials, and local management separately. Establish that a target service works from an authorized source before testing that the same service is blocked from an unauthorized source; a failed ping alone is not evidence of isolation.

Record source role, destination service, IP family, expected outcome, and observed result. Include same-segment and management traffic rather than testing only perimeter forwarding. Recheck after changes to rules, routes, port membership, wireless mappings, or platform networking.

Keep an allowed-flow record with owners and review dates, remove temporary exceptions, and retain protected configuration backups and a known-good rollback path. Test management and recovery when their ordinary dependencies are unavailable. A diagram, downloaded backup, or successful configuration apply is not proof that the design is secure or recoverable.

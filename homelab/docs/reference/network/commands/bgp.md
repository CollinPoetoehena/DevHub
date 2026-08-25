# BGP — Border Gateway Protocol

Commands for managing and inspecting BGP sessions across different environments: standalone Linux routers using BIRD, and Kubernetes/OpenShift clusters using MetalLB. Use these to check BGP peer status, inspect advertised/received routes, verify load balancer IP advertisement, and debug routing issues.

---

## Table of Contents

- [BIRD — Linux Router BGP](#bird--linux-router-bgp)
  - [birdc — BIRD Client CLI](#birdc--bird-client-cli)
  - [Show Protocols — BGP Session Status](#show-protocols--bgp-session-status)
  - [Show Routes — BGP Route Table](#show-routes--bgp-route-table)
  - [Route Management](#route-management)
  - [Configuration](#configuration)
  - [Debugging BGP Issues (BIRD)](#debugging-bgp-issues-bird)
- [Kubernetes / OpenShift — MetalLB BGP](#kubernetes--openshift--metallb-bgp)
  - [MetalLB Resources](#metallb-resources)
  - [IP Management — Checking Used & Available IPs](#ip-management--checking-used--available-ips)
  - [Service & Endpoint Inspection](#service--endpoint-inspection)
  - [MetalLB Speaker Logs](#metallb-speaker-logs)
  - [Debugging BGP Issues (K8s/OCP)](#debugging-bgp-issues-k8socp)

---

# BIRD — Linux Router BGP

Commands for managing BGP sessions using [BIRD](https://bird.network.cz/), a lightweight routing daemon commonly used on Linux routers.

---

## `birdc` — BIRD Client CLI

`birdc` is the interactive CLI client for BIRD. It connects to the running BIRD daemon and lets you inspect protocols, routes, and configuration. Requires root or membership in the `bird` group.

```bash
sudo birdc                             # enter interactive mode
sudo birdc show status                 # one-shot command (no interactive shell)
```

In interactive mode, type `?` or `help` for available commands. All commands below can be run either interactively or as one-shot (`sudo birdc <command>`).

---

## Show Protocols — BGP Session Status

```bash
birdc show protocols                   # summary of all protocols (BGP, static, direct, etc.)
birdc show protocols all               # detailed info for all protocols
birdc show protocols all <name>        # detailed info for a specific BGP peer
```

**Summary output format:**

```
Name       Proto      Table    State  Since         Info
bgp_peer1  BGP        ---      up     2026-08-25    Established
bgp_peer2  BGP        ---      start  2026-08-25    Active        Socket: Connection refused
static1    Static     ---      up     2026-08-25
direct1    Direct     ---      up     2026-08-25
```

**Key fields:**

| Field | Description |
|-------|-------------|
| `Name` | Protocol instance name (defined in `bird.conf`) |
| `Proto` | Protocol type: `BGP`, `Static`, `Direct`, `Kernel`, `OSPF`, etc. |
| `Table` | Routing table this protocol feeds into (usually `master4` or `master6`) |
| `State` | `up` = running normally; `start` = trying to connect; `down` = disabled |
| `Info` | BGP-specific state — see table below |

**BGP session states (`Info` column):**

| State | Description |
|-------|-------------|
| `Established` | BGP session is up and exchanging routes — normal operation. |
| `Active` | BIRD is trying to connect to the peer but has not succeeded yet. Check the peer's IP, port, and firewall rules. |
| `Connect` | TCP connection in progress. |
| `OpenSent` | TCP connected, BGP OPEN message sent, waiting for peer's OPEN. |
| `OpenConfirm` | Both sides exchanged OPEN messages, waiting for KEEPALIVE. |
| `Idle` | Session is down — either administratively disabled or waiting for a retry after a failure. |

**Detailed output (`show protocols all <name>`)** adds:

- `BGP state`: same as Info above
- `Neighbor address`: peer IP
- `Neighbor AS`: peer's AS number
- `Local AS`: your AS number
- `Routes`: imported/exported/preferred route counts
- `Hold timer`: negotiated keepalive/hold timers
- `Last error`: reason for the last session failure (e.g. `Connection refused`, `Hold timer expired`)

---

## Show Routes — BGP Route Table

```bash
birdc show route                       # all routes in the main routing table
birdc show route for <prefix>          # best route for a specific destination
birdc show route where net ~ 10.42.0.0/16   # routes matching a prefix range
birdc show route protocol <name>       # routes learned from a specific protocol/peer
birdc show route export <name>         # routes being exported to a specific peer
birdc show route all                   # all routes with full attributes (AS path, communities, etc.)
birdc show route for <prefix> all      # full attributes for a specific route
```

**Output format:**

```
10.42.0.0/20       unicast [bgp_peer1 2026-08-25] * (100) [AS65001i]
        via 10.42.0.1 on eth1
```

**Key fields:**

| Field | Description |
|-------|-------------|
| `10.42.0.0/20` | Destination prefix |
| `unicast` | Route type |
| `[bgp_peer1 ...]` | Protocol that installed this route and when |
| `*` | This is the currently selected (best) route |
| `(100)` | Route preference (higher = more preferred in BIRD) |
| `[AS65001i]` | BGP origin — `i` = IGP, `e` = EGP, `?` = incomplete |
| `via 10.42.0.1 on eth1` | Next hop and outgoing interface |

**With `all` flag**, additional BGP attributes are shown:

| Attribute | Description |
|-----------|-------------|
| `BGP.as_path` | Sequence of AS numbers the route has traversed |
| `BGP.next_hop` | BGP next hop IP (may differ from the gateway in the route) |
| `BGP.local_pref` | Local preference (higher = more preferred; default 100) |
| `BGP.community` | BGP communities attached to the route |
| `BGP.origin` | Origin type: `IGP`, `EGP`, or `Incomplete` |

---

## Route Management

```bash
birdc reload <name>                    # soft-reload: re-apply filters without dropping the session
birdc reload in <name>                 # re-apply import filters only
birdc reload out <name>                # re-apply export filters only
birdc restart <name>                   # hard restart: tear down and re-establish the BGP session
birdc disable <name>                   # administratively shut down a BGP session
birdc enable <name>                    # bring a disabled BGP session back up
birdc down                             # shut down BIRD entirely
```

> **`reload` vs `restart`:** `reload` re-evaluates filters on already-received routes without tearing down the TCP session — fast and non-disruptive. `restart` tears down the BGP session and re-establishes it from scratch — use when the peer needs a full reset. Always prefer `reload` unless you specifically need a session reset.

---

## Configuration

BIRD's configuration file is typically at `/etc/bird/bird.conf` (or `/etc/bird.conf`).

```bash
birdc configure                        # reload configuration without restarting BIRD
birdc configure check                  # syntax-check the config without applying it
birdc show config                      # dump the running configuration
```

**Minimal BGP peer configuration example:**

```
protocol bgp bgp_peer1 {
    local as 65000;
    neighbor 10.42.0.2 as 65001;
    ipv4 {
        import all;
        export where net ~ [ 10.42.0.0/20+ ];
    };
}
```

| Directive | Description |
|-----------|-------------|
| `local as` | Your AS number |
| `neighbor <ip> as <asn>` | Peer's IP address and AS number |
| `import all` | Accept all routes from this peer (apply filters here to restrict) |
| `export where ...` | Only advertise routes matching the filter to this peer |

After editing the config, apply with `birdc configure`. Check for syntax errors first with `birdc configure check`.

---

## Debugging BGP Issues (BIRD)

| Symptom | Check | Command |
|---------|-------|---------|
| Peer stuck in `Active` | TCP connectivity to peer | `ping <peer_ip>` and `ss -tn \| grep :179` |
| Peer stuck in `Active` | Firewall blocking BGP port 179 | `sudo tcpdump -i eth0 -n tcp port 179` |
| Session drops frequently | Hold timer expiring | `birdc show protocols all <name>` — check `Last error` |
| No routes received | Import filter too restrictive | `birdc show route protocol <name>` |
| Routes not advertised | Export filter too restrictive | `birdc show route export <name>` |
| Wrong route selected | Check preferences and AS path | `birdc show route for <prefix> all` |
| Config syntax error | Validate before applying | `birdc configure check` |

---

# Kubernetes / OpenShift — MetalLB BGP

Commands for inspecting BGP-based load balancer IP advertisement in Kubernetes and OpenShift clusters using [MetalLB](https://metallb.universe.tf/). MetalLB runs as a set of speaker pods that establish BGP sessions with your network router to advertise `LoadBalancer` service IPs.

> **`oc` vs `kubectl`:** All commands below use `oc` (OpenShift CLI). Replace with `kubectl` on plain Kubernetes — the commands are identical for MetalLB resources.

---

## MetalLB Resources

These are the custom resources that define how MetalLB allocates and advertises IPs via BGP.

### IPAddressPool — Available IP Ranges

```bash
oc get ipaddresspools -A                              # list all IP address pools
oc get ipaddresspools -n metallb-system               # list pools in the MetalLB namespace
oc get ipaddresspool <name> -n metallb-system -o yaml  # full pool definition
```

Example output:
```
NAMESPACE        NAME              AUTO ASSIGN   AVOID BUGGY IPS   ADDRESSES
metallb-system   lab-pool          true          false              ["10.42.1.0/24"]
```

| Field | Description |
|-------|-------------|
| `NAME` | Pool name referenced by BGPAdvertisement |
| `AUTO ASSIGN` | `true` = automatically assign IPs from this pool to new `LoadBalancer` services |
| `ADDRESSES` | IP ranges available for allocation (CIDR or range format) |

### BGPAdvertisement — What Gets Advertised

```bash
oc get bgpadvertisements -A                                   # list all BGP advertisements
oc get bgpadvertisement <name> -n metallb-system -o yaml      # full advertisement definition
```

Shows which IP pools are advertised to which BGP peers, with optional community and aggregation settings.

### BGPPeer — Router Peering Configuration

```bash
oc get bgppeers -A                                    # list all BGP peer definitions
oc get bgppeer <name> -n metallb-system -o yaml       # full peer definition
```

Example output:
```
NAMESPACE        NAME          ADDRESS       ASN     BFD PROFILE   EBGP MULTI HOP   HOLD TIME   KEEPALIVE TIME
metallb-system   lab-router    10.42.0.1     65000                 false
```

| Field | Description |
|-------|-------------|
| `ADDRESS` | Router IP that MetalLB speakers peer with |
| `ASN` | Router's AS number |
| `EBGP MULTI HOP` | Whether the peer is more than one hop away |
| `HOLD TIME` / `KEEPALIVE TIME` | BGP timer settings for this peer |

### Community — BGP Communities

```bash
oc get communities -A                                 # list BGP community definitions
oc get community <name> -n metallb-system -o yaml     # full community definition
```

---

## IP Management — Checking Used & Available IPs

Commands for checking which MetalLB IPs are currently assigned, which are free, and which service is using a specific IP. Essential when provisioning new `LoadBalancer` services or troubleshooting IP conflicts.

### Check assigned IPs

List all IP address pools to see what is available:

```bash
oc -n metallb-system get ipaddresspool
```

Show pools that have assigned addresses (i.e. IPs currently in use):

```bash
# IPv4
oc -n metallb-system get ipaddresspool -o jsonpath='{range .items[?(@.status.assignedIPv4==1)]}{.metadata.name}{"\t"}{.spec.addresses[0]}{"\n"}{end}'

# IPv6
oc -n metallb-system get ipaddresspool -o jsonpath='{range .items[?(@.status.assignedIPv6==1)]}{.metadata.name}{"\t"}{.spec.addresses[0]}{"\n"}{end}'
```

### Find which service owns an IP

Given a set of IPs, find the corresponding `LoadBalancer` services across all namespaces:

```bash
TARGET_IP_REGEX="10.42.1.10|10.42.1.11|10.42.1.12"
for ns in $(oc projects -q); do
  oc get svc -n "$ns" \
    --field-selector spec.type=LoadBalancer \
    -o jsonpath="{range .items[*]}{'\n'}$ns{'\t'}{.metadata.name}{'\t'}{.status.loadBalancer.ingress[*].ip}{end}" \
    2>/dev/null
done | grep -E "$TARGET_IP_REGEX"
```

This iterates all projects/namespaces and prints `<namespace> <service-name> <external-ip>` for matching IPs. Works for both IPv4 and IPv6 addresses — adjust `TARGET_IP_REGEX` accordingly.

### Check available (free) IPs

Show pools that still have available (unassigned) addresses:

```bash
# IPv4
oc -n metallb-system get ipaddresspool -o jsonpath='{range .items[?(@.status.availableIPv4==1)]}{.metadata.name}{"\t"}{.spec.addresses[0]}{"\n"}{end}'

# IPv6
oc -n metallb-system get ipaddresspool -o jsonpath='{range .items[?(@.status.availableIPv6==1)]}{.metadata.name}{"\t"}{.spec.addresses[0]}{"\n"}{end}'
```

### Verify an IP is truly unused

Before assigning a "free" IP, verify that nothing is already using it. Start with a ping:

```bash
ping -c 3 -W 2 <candidate-ip>                        # IPv4
ping6 -c 3 -W 2 <candidate-ip>                       # IPv6 (or `ping -6` on some systems)
```

- **Replies received** — something is using this IP, do not assign it.
- **No reply** — likely free, but the host could be blocking ICMP. For a more thorough check, probe common service ports with [`nc`](host_networking.md#nc--netcat):

See the [`ping` reference](host_networking.md#ping) for full flag details and output interpretation.

```bash
nc -zv -w 2 <candidate-ip> 80 443 53 22              # test common protocols like HTTP (port 80), HTTPS (port 443), DNS (port 53), SSH (port 22)
nc -6 -zv -w 2 <candidate-ipv6> 80 443 53 22         # same for IPv6
```

- **"Connection refused"** — a host is there but not running that service (IP is in use).
- **"Connection timed out"** on all ports + no ping reply — IP is most likely free.

See the [`nc` reference](host_networking.md#nc--netcat) for full flag details and output interpretation.

> **Note:** Neither ping nor port scanning guarantees an IP is unused — a firewall could be silently dropping all traffic. If your environment has an IPAM (IP Address Management) system or CMDB, always cross-check there as well.

---

## Service & Endpoint Inspection

Commands to verify that services have received a `LoadBalancer` IP and traffic is reaching the correct pods.

```bash
oc get svc                                            # list services — check EXTERNAL-IP column
oc get svc -A                                         # all namespaces
oc get svc <name> -o wide                             # show selector and additional details
oc get svc <name> -o yaml                             # full service spec including loadBalancerIP
```

**Key columns for BGP debugging:**

| Column | Description |
|--------|-------------|
| `TYPE` | Must be `LoadBalancer` for MetalLB to assign an IP |
| `CLUSTER-IP` | Internal cluster IP (always assigned) |
| `EXTERNAL-IP` | IP assigned by MetalLB from an IPAddressPool — `<pending>` means no IP was assigned yet |
| `PORT(S)` | Service ports and their node port mappings |

```bash
oc get endpoints <name>                               # pod IPs backing the service
oc get endpointslices -l kubernetes.io/service-name=<name>  # newer endpoint slice API
```

If `EXTERNAL-IP` is `<pending>`, MetalLB could not assign an IP — check that an IPAddressPool exists with available addresses and that the service's annotation/selector matches a BGPAdvertisement.

### Node & Speaker Status

```bash
oc get nodes -o wide                                  # node IPs and status — speakers run on these
oc get pods -n metallb-system                         # MetalLB controller and speaker pods
oc get pods -n metallb-system -l component=speaker    # speaker pods only
oc get pods -n metallb-system -o wide                 # include node assignment
```

Each speaker pod runs on a node and establishes BGP sessions with the configured peers. If a speaker pod is not `Running`, that node cannot advertise routes.

---

## MetalLB Speaker Logs

The speaker pods contain BGP session logs — check these when sessions are not establishing or routes are not being advertised.

```bash
oc logs -n metallb-system -l component=speaker                      # all speaker logs
oc logs -n metallb-system -l component=speaker --tail=50            # last 50 lines
oc logs -n metallb-system <speaker-pod-name>                        # specific speaker
oc logs -n metallb-system -l component=speaker | grep -i bgp        # BGP-related messages
oc logs -n metallb-system -l component=speaker | grep -i "session"  # session state changes
```

**Common log messages:**

| Message | Meaning |
|---------|---------|
| `"sessionUp"` | BGP session established with peer |
| `"sessionDown"` | BGP session dropped — check peer reachability and firewall |
| `"announcing"` with IP | MetalLB is advertising a service IP to the peer |
| `"connection refused"` | Peer's BGP daemon is not listening on port 179 |
| `"hold timer expired"` | Peer stopped responding — network issue or peer overloaded |

---

## Debugging BGP Issues (K8s/OCP)

| Symptom | Check | Command |
|---------|-------|---------|
| `EXTERNAL-IP` is `<pending>` | IPAddressPool exists and has free IPs | `oc get ipaddresspools -A` |
| `EXTERNAL-IP` is `<pending>` | BGPAdvertisement references the correct pool | `oc get bgpadvertisements -A -o yaml` |
| Service IP not reachable | Speaker pods are running | `oc get pods -n metallb-system -l component=speaker` |
| Service IP not reachable | BGP sessions are established | `oc logs -n metallb-system -l component=speaker \| grep session` |
| Service IP not reachable | Router sees the route | `birdc show route for <service-ip>` (on the router) |
| BGP session not establishing | Peer config matches router config | `oc get bgppeers -A` and `birdc show protocols all` |
| BGP session not establishing | Port 179 is reachable between nodes and router | `sudo tcpdump -i eth0 -n tcp port 179` |
| Traffic reaches service but no response | Endpoints exist and pods are healthy | `oc get endpoints <name>` and `oc get pods` |
| Only some nodes advertise | Speaker pod missing on a node | `oc get pods -n metallb-system -o wide` |

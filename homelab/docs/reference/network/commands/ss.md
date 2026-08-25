# ss — Socket Statistics

Shows active network sockets (connections and listening ports). Replaces the legacy `netstat` command. Use it to check which services are listening on which ports, verify a daemon started correctly, or debug port conflicts.

---

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

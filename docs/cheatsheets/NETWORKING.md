# Networking Commands

See the [cheat sheet README](README.md) for scope, usage, placeholders, and safety.

## Table of Contents

- [Host networking](#host-networking)
  - [ip](#ip)
  - [nmcli](#nmcli)
  - [ss](#ss)
- [Connectivity](#connectivity)
  - [ping](#ping)
  - [traceroute](#traceroute)
  - [tracepath](#tracepath)
  - [nc](#nc)
  - [nmap](#nmap)
- [DNS and DHCP](#dns-and-dhcp)
  - [dig](#dig)
  - [nslookup](#nslookup)
  - [resolvectl](#resolvectl)
  - [dhclient](#dhclient)
- [Packet capture](#packet-capture)
  - [tcpdump](#tcpdump)
- [Performance](#performance)
  - [iperf3](#iperf3)
- [BGP](#bgp)
  - [birdc](#birdc)

---

## Host networking

### ip

[Manuals: address](https://man7.org/linux/man-pages/man8/ip-address.8.html), [link](https://man7.org/linux/man-pages/man8/ip-link.8.html), [route](https://man7.org/linux/man-pages/man8/ip-route.8.html), [neighbour](https://man7.org/linux/man-pages/man8/ip-neighbour.8.html).

```bash
ip -br address                       # Compact interface and address overview
ip -4 address show dev eth0           # IPv4 addresses and lifetimes
ip -6 address show dev eth0           # IPv6 addresses and lifetimes
ip -s link show dev eth0              # Link state, traffic counters, and errors
ip route show                        # IPv4 routing table
ip -6 route show                      # IPv6 routing table
ip route get 192.0.2.10               # Route and source address selected for a destination
ip neigh show                        # Cached IPv4/IPv6 neighbours; not a host inventory
```

### nmcli

[Official manual](https://networkmanager.dev/docs/api/latest/nmcli.html). Requires NetworkManager.

```bash
nmcli connection show                # Saved connection profiles
nmcli connection show --active       # Active profiles
nmcli device status                  # Device state
nmcli device show eth0               # Addresses, routes, DNS, and DHCP details
```

**Disruptive:** reconnecting can interrupt remote access. Use local or out-of-band access.

```bash
sudo nmcli connection down "Wired connection 1"   # Deactivate the verified profile
sudo nmcli connection up "Wired connection 1"     # Activate it again; may request DHCP
```

### ss

[Manual](https://man7.org/linux/man-pages/man8/ss.8.html).

```bash
sudo ss -tulpn                       # TCP/UDP listeners, numeric ports, and processes
ss -tn state established             # Established TCP connections
sudo ss -lunp 'sport = :53'           # UDP DNS listeners
sudo ss -ltnp 'sport = :53'           # TCP DNS listeners
```

---

## Connectivity

### ping

[Official manual](https://github.com/iputils/iputils/blob/master/doc/ping.xml).

```bash
ping -c 3 -W 2 192.0.2.10             # Three ICMP probes, two-second reply timeout
ping -6 -c 3 2001:db8::10             # IPv6 probes
ping -I eth0 -c 3 192.0.2.10          # Probe through a specific interface
ping -4 -c 3 -s 1472 -M do 192.0.2.10 # Test a 1500-byte IPv4 path without fragmentation
```

No reply does not prove a host is down or an address is unused; ICMP may be blocked.

### traceroute

[Official documentation](https://traceroute.sourceforge.net/).

```bash
traceroute -n 192.0.2.10              # Trace hops without reverse DNS lookups
sudo traceroute -I 192.0.2.10         # Use ICMP probes
sudo traceroute -T -p 443 192.0.2.10  # Use TCP probes to port 443
```

### tracepath

[Official manual](https://github.com/iputils/iputils/blob/master/doc/tracepath.xml).

```bash
tracepath -n 192.0.2.10               # Trace path and discover path MTU without root
```

### nc

[Official OpenBSD manual](https://man.openbsd.org/nc). Linux netcat variants differ; check local help.

```bash
nc -zv -w 2 192.0.2.10 443            # Test a TCP connection with a timeout
nc -6 -zv -w 2 2001:db8::10 443       # Test an IPv6 TCP connection
```

A TCP connection is not an application health check. UDP netcat success does not reliably establish that a service is reachable.

### nmap

[Official manual](https://nmap.org/book/man.html). Scan only authorized targets.

```bash
nmap -sn 192.0.2.0/24                 # Discover responding hosts without a port scan
nmap -p 22,53,80,443 192.0.2.10        # Scan selected TCP ports
nmap -sV -p 443 192.0.2.10            # Probe the service version on a selected port
sudo nmap -sU -p 53,123 192.0.2.10    # Scan selected UDP ports; results may be open|filtered
```

---

## DNS and DHCP

### dig

[Official BIND manual](https://bind9.readthedocs.io/en/latest/manpages.html#dig-dns-lookup-utility).

```bash
dig example.com A                    # Query the configured resolver for IPv4 records
dig @192.0.2.53 example.com A         # Query a specific resolver
dig example.com AAAA +short          # Compact IPv6 answers
dig example.com MX                   # Mail exchanger records
dig example.com NS                   # Nameserver records
dig example.com SOA                  # Zone authority record
dig example.com TXT                  # Text records
dig -x 192.0.2.10                    # Reverse DNS lookup
dig example.com A +noall +answer     # Answer section only
dig example.com A +time=2 +tries=1   # Bound query timeout and attempts
dig @192.0.2.53 example.com A +tcp    # Query DNS over TCP
dig example.com +trace               # Follow delegations; not the configured resolver's path
```

### nslookup

[Official BIND manual](https://bind9.readthedocs.io/en/latest/manpages.html#nslookup-query-internet-name-servers-interactively).

```bash
nslookup example.com                 # Query the configured resolver
nslookup example.com 192.0.2.53       # Query a specific resolver
nslookup 192.0.2.10                   # Reverse DNS lookup
```

### resolvectl

[Official manual](https://www.freedesktop.org/software/systemd/man/latest/resolvectl.html). Requires systemd-resolved.

```bash
resolvectl status                    # Per-link DNS servers and resolver settings
resolvectl query example.com         # Resolve through systemd-resolved
```

### dhclient

[Official ISC manual](https://kb.isc.org/docs/isc-dhcp-44-manual-pages-dhclient). ISC DHCP is end-of-life; these examples are for existing installations.

**Disruptive:** only use on an interface managed by dhclient, not alongside another DHCP client. Releasing a lease can disconnect remote access.

```bash
sudo dhclient -v eth0                # Request a lease with verbose exchange details
sudo dhclient -r eth0                # Release the lease and stop that client
```

---

## Packet capture

### tcpdump

[Official manual](https://www.tcpdump.org/manpages/tcpdump.1.html) and [filter syntax](https://www.tcpdump.org/manpages/pcap-filter.7.html). Captures can expose sensitive traffic.

```bash
sudo tcpdump -ni eth0 -c 40 'port 53'                         # DNS traffic
sudo tcpdump -ni eth0 -c 40 'udp and (port 67 or port 68)'    # DHCPv4 traffic
sudo tcpdump -ni eth0 -c 40 'udp and (port 546 or port 547)'  # DHCPv6 traffic
sudo tcpdump -ni eth0 -c 40 'tcp port 179'                   # BGP traffic
sudo tcpdump -ni eth0 -c 100 -w capture.pcap 'host 192.0.2.10' # Save selected packets
tcpdump -nn -r capture.pcap                                  # Read a saved capture
```

---

## Performance

### iperf3

[Official documentation](https://software.es.net/iperf/invoking.html). Requires iperf3 at both ends and firewall access to the server (default port 5201). Tests generate load; stop the server with Ctrl+C afterward.

```bash
iperf3 -s                            # Server: listen for test clients
iperf3 -c 192.0.2.10 -t 10            # Client: TCP throughput for ten seconds
iperf3 -c 192.0.2.10 -R               # Reverse direction: server sends to client
iperf3 -c 192.0.2.10 -P 4             # Four parallel TCP streams
iperf3 -c 192.0.2.10 -u -b 100M       # UDP at 100 Mbit/s; inspect loss and jitter
iperf3 -c 192.0.2.10 --bidir           # Send in both directions simultaneously
```

---

## BGP

### birdc

[Official BIRD documentation](https://bird.nic.cz/doc/bird-3.1.0.html). Requires a running BIRD daemon and permission to access its control socket.

```bash
sudo birdc show status                        # Daemon status
sudo birdc show protocols                     # Protocol/session summary
sudo birdc show protocols all peer1           # Detailed state for a configured peer
sudo birdc show route                         # Routes in BIRD's default table
sudo birdc show route for 192.0.2.10 all       # Matching route and attributes
sudo birdc show route protocol peer1          # Routes learned from a peer
sudo birdc show route export peer1            # Routes exported to a peer
sudo birdc configure check                    # Check configuration without applying it
```

**Changes state:** configuration reloads can affect routing or restart sessions.

```bash
sudo birdc configure                          # Apply configuration
sudo birdc reload out peer1                   # Re-export routes through current filters
```

For MetalLB resource inspection, see the [Kubernetes commands](KUBERNETES.md#metallb).

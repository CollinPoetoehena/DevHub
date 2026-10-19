# DHCP and DNS Server Diagnostics

This page covers portable ways to diagnose DNS and DHCP services without assuming a particular server product. DNS and DHCP server configuration, lease databases, service names, and logs differ by implementation; use that product's official documentation for setup and detailed administration. This guide focuses on observing behavior from clients, hosts, and packet captures.

For the underlying concepts, see [DHCP and DNS](../DHCP_and_DNS.md). For client-specific lease commands, see [DHCP Client Commands](dhcp_client.md); for querying DNS records, see [DNS Lookup Commands](dns.md).

---

## Table of Contents

- [Diagnostic sequence](#diagnostic-sequence)
- [Check DNS service behavior](#check-dns-service-behavior)
- [Check DHCP service behavior](#check-dhcp-service-behavior)
- [Inspect listeners and service health](#inspect-listeners-and-service-health)
- [Capture DNS and DHCP traffic](#capture-dns-and-dhcp-traffic)
- [References](#references)

---

## Diagnostic sequence

Start at the client that experiences the problem, and work outward:

1. Confirm the client has a valid interface, address, route, and configured resolver.
2. Query the configured DNS resolver directly, then compare with another known resolver if appropriate.
3. For DHCP, renew or inspect the client's lease and check whether it received an address, gateway, and DNS server.
4. Check that the server process is healthy and listening on the expected interfaces and ports.
5. Capture a short, filtered packet trace on the client, server, or relevant network boundary to see whether requests and replies pass.
6. Check the selected server's logs and configuration using its official documentation.

The point where a request disappears or a response changes direction helps narrow the fault to the client, network path, server, or upstream resolver. A successful lookup from the server itself does not prove that clients can reach it or that firewall rules permit replies.

---

## Check DNS service behavior

Use [`dig`](dns.md#dig) to ask a specific resolver and compare its response with the operating system's configured resolver:

```bash
dig example.com A @<resolver-ip>
dig example.com A +time=2 +tries=1
dig -x <ip-address> @<resolver-ip>
```

Check the response status (`NOERROR`, `NXDOMAIN`, `SERVFAIL`, or `REFUSED`), answer section, responding server, and query time. If one resolver answers and another does not, compare its forwarding, recursion, DNSSEC, and local-zone behavior in that server's documentation. Do not assume that a public resolver knows private hostnames.

DNS commonly uses UDP port 53, and also TCP port 53 (including for larger responses and some operations). A listener on the server alone is not proof that packets are allowed through local or network firewalls.

---

## Check DHCP service behavior

DHCP clients normally use UDP source port 68 and server port 67 for IPv4. When a client has no usable lease, inspect its DHCP client logs and packet exchange; a server cannot answer a broadcast that does not reach it or a relay.

For DHCPv4, the expected exchange is often described as DORA: Discover, Offer, Request, Acknowledge. A trace can show whether the client broadcasts a Discover, whether any server or relay replies with an Offer, and whether the exchange completes. DHCPv6 uses different messages and ports; consult the protocol documentation and packet dissector for details.

```bash
sudo tcpdump -ni <interface> -c 40 'udp and (port 67 or port 68)'
```

Use [DHCP client commands](dhcp_client.md) to inspect or renew a lease. Server-side lease inspection, reservations, address pools, relay configuration, and logs are implementation-specific: check the selected DHCP server's official documentation rather than assuming a common file path or command.

---

## Inspect listeners and service health

On Linux, `ss` can show whether a process has sockets open on the expected ports:

```bash
sudo ss -lunp | grep -E ':(53|67|547)\b'
sudo ss -ltnp | grep -E ':53\b'
```

Port 53 can be served over UDP and TCP. The IPv4 DHCP server commonly listens on UDP 67; DHCPv6 commonly uses UDP 547 on the server. Actual sockets, addresses, and process names vary by implementation. A wildcard bind address may be intentional, so verify interface restrictions and firewall policy rather than inferring exposure from the bind address alone.

On a system using systemd, `systemctl status <service>` and `journalctl -u <service>` can help inspect a service and its logs. The unit name and log location depend on the distribution and implementation; use the platform's standard service tools and the product's documentation.

---

## Capture DNS and DHCP traffic

Short, filtered packet captures help establish whether requests reach a server and whether replies return. See [Packet Capture & Analysis](packet_capture_analysis.md) for more `tcpdump`, `tshark`, and Wireshark techniques.

```bash
sudo tcpdump -ni <interface> -c 40 'port 53'
sudo tcpdump -ni <interface> -c 40 'udp and (port 67 or port 68)'
```

For an existing capture, `tshark -r <capture.pcap> -Y 'dns'` filters DNS packets; DHCPv4 display-filter field names can depend on the Wireshark version, so check its official [display-filter reference](https://www.wireshark.org/docs/dfref/). Captures can contain internal addresses, hostnames, and other sensitive metadata: limit scope and retention, and treat capture files accordingly.

---

## References

- [RFC 1034: Domain Names — Concepts and Facilities](https://www.rfc-editor.org/rfc/rfc1034)
- [RFC 1035: Domain Names — Implementation and Specification](https://www.rfc-editor.org/rfc/rfc1035)
- [RFC 2131: Dynamic Host Configuration Protocol (DHCPv4)](https://www.rfc-editor.org/rfc/rfc2131)
- [RFC 8415: Dynamic Host Configuration Protocol for IPv6 (DHCPv6)](https://www.rfc-editor.org/rfc/rfc8415)

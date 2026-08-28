# DHCP & DNS

Background information on DHCP (Dynamic Host Configuration Protocol) and DNS (Domain Name System).

---

## Table of Contents

- [DHCP](#dhcp)
- [DNS](#dns)

---

### DHCP

Dynamic Host Configuration Protocol — the protocol that automatically assigns network configuration to devices when they join a network. Without DHCP, every device would need a manually configured static IP.

**What DHCP assigns to each device:**

- **IP address** — a unique address for the device on this subnet
- **Subnet mask** — defines the size of the network (e.g. `255.255.255.0` / `/24`)
- **Default gateway** — the router's IP; the device sends traffic here when the destination is outside the local subnet
- **DNS server(s)** — where the device sends DNS queries to resolve hostnames
- **Lease time** — how long the assignment is valid before the device must renew

**How it works (DORA):**

1. **Discover** — the device broadcasts on the network: *"Is there a DHCP server? I need an IP address."*
2. **Offer** — the DHCP server replies with an available IP and configuration.
3. **Request** — the device formally requests the offered address.
4. **Acknowledge** — the server confirms the assignment and records the lease.

**DHCP reservation (static DHCP):** You can bind a specific IP to a device's MAC address in the DHCP server. The device still uses DHCP (no manual configuration on the device), but always receives the same IP. Useful for servers, routers, and any device that others need to reach at a predictable address.

**Lease time:** DHCP leases are temporary. When a lease expires the device must renew; if the server is unreachable it loses its IP. For servers and infrastructure, use DHCP reservations or configure static IPs directly on the device.

**DHCP conflicts:** If two DHCP servers run on the same subnet, devices may receive duplicate addresses, causing connectivity failures. This is a common mistake when connecting a Proxmox host or second router directly to the home network — its bridged interface can start responding to DHCP requests alongside the ISP modem.

> This homelab uses [dnsmasq](dnsmasq.md) as the DHCP server on the lab router. See the dnsmasq reference for configuration, lease management, and debugging commands.

### DNS

Domain Name System — the protocol that translates human-readable hostnames (e.g. `google.com`) into IP addresses (e.g. `142.250.185.110`). Without DNS you would need to know and type the IP address of every service you want to reach.

**How resolution works:**

When you type `google.com` in a browser, your OS sends a DNS query to its configured DNS server. Resolution happens in stages:

1. **Local cache** — the OS checks if it has recently resolved this name. If so, it uses the cached result immediately (no network query needed).
2. **Recursive resolver** — if not cached, the query goes to the DNS server configured for the network (set by DHCP, or manually — e.g. `8.8.8.8` for Google DNS, `1.1.1.1` for Cloudflare). This resolver handles the full lookup on your behalf and caches results.
3. **Nameserver chain** — if the recursive resolver has no cached answer, it walks down the DNS hierarchy:
   - a. **Root nameservers (.)** — one of 13 root nameserver clusters (operated by IANA/ICANN and various organisations). They do not know the final answer; they respond with a referral: *"ask the `.com` TLD nameservers."*
   - b. **TLD nameservers (.com)** — operated by Verisign for `.com`. They also respond with a referral: *"ask `ns1.google.com`"* (Google's own authoritative nameservers).
   - c. **Authoritative nameserver (ns1.google.com)** — holds the actual DNS records for `google.com` and returns the `A` record: `google.com → 142.250.185.110`.
4. **Response** — the resolver caches the answer (for the TTL duration) and returns the IP to your OS. Your OS caches it too, then passes it to the browser.

```
Browser/App
    │
    ▼
OS local cache ──► (hit) ──► done
    │ (miss)
    ▼
Recursive resolver (e.g. 8.8.8.8)
    │ cache miss → walks nameserver chain:
    │   a. Root (.)          → referral: "ask .com TLD"
    │   b. TLD (.com)        → referral: "ask ns1.google.com"
    │   c. Authoritative     → answer: google.com → 142.250.185.110
    ▼
Recursive resolver caches result, returns IP
    │
    ▼
OS caches result, passes IP to browser
```

In practice the recursive resolver almost always has `.com` and many popular domains cached already, so step 3 is skipped entirely. The full nameserver chain walk only happens for domains the resolver has never seen before.

**Key concepts:**

- **DNS server (resolver):** The server your device queries. Provided by DHCP (the DHCP server tells devices which DNS server to use) or configured manually. On Linux, see `/etc/resolv.conf` for the configured nameserver(s).
- **DNS forwarding:** A local DNS server (e.g. `dnsmasq` on the lab router) that receives queries from local devices and forwards them upstream to a public resolver. Useful when you want to add local hostname resolution on top of regular internet DNS.
- **Local DNS:** A DNS server that resolves names for hosts within a private network (e.g. `pi.lab` → `10.42.10.1`). Public resolvers have no knowledge of private hostnames; a local resolver handles them.
- **TTL (Time To Live):** How long a DNS response may be cached before it must be re-queried. Set by the domain owner. Short TTL = more DNS queries but faster propagation of IP changes; long TTL = fewer queries but slower propagation.
- **Common record types:** `A` = hostname → IPv4; `AAAA` = hostname → IPv6; `CNAME` = hostname alias → another hostname; `PTR` = IP → hostname (reverse DNS); `MX` = mail server for a domain.
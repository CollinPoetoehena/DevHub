# dnsmasq

`dnsmasq` is a lightweight DNS forwarder and DHCP server designed for small networks. It is the tool used in the [Homelab](../../homelab/README.md) to provide DNS forwarding and DHCP services on the lab router (e.g. a Raspberry Pi).

- **Official site:** [https://dnsmasq.org/doc.html](https://dnsmasq.org/doc.html) and [https://docs.opnsense.org/manual/dnsmasq.html](https://docs.opnsense.org/manual/dnsmasq.html)
- **Man page:** `man dnsmasq` (on the host where it is installed)

> **Note:** `dnsmasq` does not have a CLI for interactive use. It is configured via a config file and run as a background service. Use `systemctl` to manage the service and `journalctl` to view logs. This document provides a reference for other commands for DNS and DHCP as well.

---

## Table of Contents

- [What dnsmasq Does](#what-dnsmasq-does)
- [Configuration](#configuration)
- [Commands: Service Management](#commands-service-management)
- [Commands: DNS](#commands-dns)
- [Commands: DHCP](#commands-dhcp)
- [Debugging](#debugging)

---

## What dnsmasq Does

dnsmasq combines two services in one lightweight daemon:

- **DNS forwarder** — receives DNS queries from lab devices and forwards them upstream to a public resolver (e.g. the ISP modem, `8.8.8.8`, `1.1.1.1`). It also caches responses to speed up repeated lookups and can resolve local hostnames for devices on the lab network by reading its own DHCP lease database.
- **DHCP server** — assigns IP addresses, subnet masks, default gateway, and DNS server addresses to devices that join the lab network. Supports static reservations (bind a specific IP to a MAC address).

For background on DNS and DHCP concepts, see [DHCP & DNS](DHCP_and_DNS.md).

---

## Configuration

dnsmasq is configured via a single file (or a directory of files). The main config file is typically:

```bash
/etc/dnsmasq.conf           # main config
/etc/dnsmasq.d/             # drop-in directory (files here are included automatically)
```

**Key configuration directives:**

| Directive | Description | Example |
|-----------|-------------|---------|
| `interface=` | Listen on this interface only (restrict DHCP/DNS to the LAN side). | `interface=eth1` |
| `except-interface=` | Do not listen on this interface. | `except-interface=eth0` |
| `bind-interfaces` | Bind only to the interfaces specified by `interface=`. Prevents dnsmasq from listening on wildcard. | `bind-interfaces` |
| `domain=` | Local domain name appended to DHCP hostnames. | `domain=lab` |
| `local=` | Resolve this domain locally (do not forward upstream). | `local=/lab/` |
| `server=` | Upstream DNS server to forward queries to. | `server=8.8.8.8` |
| `dhcp-range=` | DHCP address pool: start IP, end IP, subnet mask, lease time. | `dhcp-range=10.42.0.100,10.42.0.200,255.255.240.0,24h` |
| `dhcp-host=` | Static DHCP reservation: MAC address, IP, hostname. | `dhcp-host=aa:bb:cc:dd:ee:ff,10.42.0.10,node1` |
| `dhcp-option=` | Set DHCP options: gateway, DNS server, etc. | `dhcp-option=3,10.42.0.1` (gateway) |
| `expand-hosts` | Add the `domain=` suffix to hostnames from `/etc/hosts` and DHCP leases. | `expand-hosts` |
| `no-resolv` | Do not read `/etc/resolv.conf` for upstream servers (use `server=` directives only). | `no-resolv` |
| `log-queries` | Log every DNS query to syslog (useful for debugging, noisy in production). | `log-queries` |
| `log-dhcp` | Log DHCP transactions to syslog. | `log-dhcp` |
| `cache-size=` | Number of DNS cache entries (default 150). | `cache-size=1000` |

**Common DHCP options (`dhcp-option=`):**

| Option | Description | Example |
|--------|-------------|---------|
| `3` | Default gateway | `dhcp-option=3,10.42.10.1` |
| `6` | DNS server(s) | `dhcp-option=6,10.42.10.1` |
| `15` | Domain name | `dhcp-option=15,lab` |
| `28` | Broadcast address | `dhcp-option=28,10.42.15.255` |

**Validate config before restarting:**

```bash
sudo dnsmasq --test
```

Returns `dnsmasq: syntax check OK.` if the config is valid, or shows the error and line number if not.

---

## Commands: Service Management

```bash
sudo systemctl status dnsmasq         # check if running and see recent logs
sudo systemctl start dnsmasq          # start the service
sudo systemctl stop dnsmasq           # stop the service
sudo systemctl restart dnsmasq        # restart (reload config)
sudo systemctl enable dnsmasq         # start on boot
sudo systemctl disable dnsmasq        # do not start on boot
```

**Reload config without full restart** (re-reads `/etc/hosts`, DHCP leases, and some config changes):

```bash
sudo kill -HUP $(pidof dnsmasq)
```

Note: not all config changes take effect with `SIGHUP` — a full `systemctl restart` is needed for changes to `interface=`, `dhcp-range=`, `bind-interfaces`, and most other directives.

---

## Commands: DNS


### Check which interface dnsmasq is serving DNS on

```bash
sudo ss -tulpn | grep dnsmasq
```

See [ss](Network_Commands.md#ss--socket-statistics) for details about the `ss` command.

### Query the local DNS server

> See [Check which interface dnsmasq is serving DNS on](#check-which-interface-dnsmasq-is-serving-dns-on) above to verify the correct interface and IP address to use below (e.g. `10.42.10.1`).

Use `dig` or `nslookup` to test that dnsmasq is resolving correctly (see [dig / nslookup](Network_Commands.md#dig--nslookup--dns-lookup) for full details):

```bash
dig google.com @10.42.10.1              # external query via dnsmasq
dig node1.lab @10.42.10.1               # local hostname via dnsmasq
dig google.com @10.42.10.1 +short       # quick check
```

### View DNS cache statistics

dnsmasq logs cache hit/miss statistics when it receives a `SIGUSR1` signal:

```bash
sudo kill -USR1 $(pidof dnsmasq)
journalctl -u dnsmasq --no-pager --since "1 minute ago" | grep -i "cache"
```

Output shows cache size, insertions, evictions, and hit rates.

### Clear DNS cache

dnsmasq has no built-in cache flush command. The simplest way is to restart the service:

```bash
sudo systemctl restart dnsmasq
```

### Check which upstream servers dnsmasq is using

```bash
sudo kill -USR1 $(pidof dnsmasq)
journalctl -u dnsmasq --no-pager --since "1 minute ago" | grep -i "server"
```

Shows which upstream DNS servers are configured and their query counts.

### Test local hostname resolution

If `expand-hosts` and `domain=lab` are configured, devices with DHCP leases or `/etc/hosts` entries should resolve:

```bash
dig node1.lab @10.42.10.1 +short
dig -x 10.42.10.10 @10.42.10.1 +short   # reverse lookup
```

---

## Commands: DHCP

`dnsmasq` manages DHCP from the server-side. Use `dhclient` to manage DHCP from the client-side (e.g. a VM), see [dhclient](Network_Commands.md#dhclient--dhcp-client) for full details.

### View active DHCP leases

dnsmasq stores active leases in a file (default `/var/lib/misc/dnsmasq.leases` or `/var/lib/dnsmasq/dnsmasq.leases` depending on the distribution):

```bash
cat /var/lib/misc/dnsmasq.leases
```

**Lease file format:**

```
<expiry-timestamp> <mac-address> <ip-address> <hostname> <client-id>
```

| Field | Description |
|-------|-------------|
| `<expiry-timestamp>` | Unix timestamp when the lease expires. `0` = static/infinite. |
| `<mac-address>` | Client's MAC address. |
| `<ip-address>` | IP address assigned to the client. |
| `<hostname>` | Hostname the client reported (or `*` if none). |
| `<client-id>` | DHCP client identifier (or `*` if none). |

Example:
```
1723680000 28:94:01:8a:ec:28 10.42.10.168 proxmox-node1 *
1723680000 aa:bb:cc:dd:ee:ff 10.42.10.169 proxmox-node2 *
```

### View DHCP lease log

```bash
journalctl -u dnsmasq --no-pager | grep -i "dhcp"
```

Shows DHCP DISCOVER, OFFER, REQUEST, and ACK messages — useful for debugging why a device did or did not get an address.

### Check DHCP reservations (static leases)

```bash
grep "dhcp-host" /etc/dnsmasq.conf /etc/dnsmasq.d/* 2>/dev/null
```

Shows all static MAC-to-IP bindings configured in dnsmasq.

### Release and renew a DHCP lease (from a client)

On the client device (not the dnsmasq server), release and request a new lease:

```bash
sudo dhclient -r eth0                 # release current lease
sudo dhclient eth0                    # request a new lease
```

Or with NetworkManager:

```bash
sudo nmcli connection down "Wired connection 1" && sudo nmcli connection up "Wired connection 1"
```

### Check which interface dnsmasq is serving DHCP on

```bash
sudo ss -ulpn | grep :67
```

Port 67 is the DHCP server port. The output shows which process holds it and on which address (see [ss](Network_Commands.md#ss--socket-statistics) for details).

---

## Debugging

### Check if dnsmasq is running

```bash
systemctl status dnsmasq
pidof dnsmasq
```

### Enable verbose logging

Add to config and restart:

```
log-queries
log-dhcp
```

Then watch logs in real time:

```bash
journalctl -u dnsmasq -f
```

### Common issues

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| `Address already in use` on port 53 | `systemd-resolved` is running | `sudo systemctl stop systemd-resolved && sudo systemctl disable systemd-resolved` |
| `Address already in use` on port 67 | Another DHCP server is running | Check with `ss -ulpn \| grep :67` and stop the conflicting service |
| DHCP clients get no IP | dnsmasq not listening on the right interface | Check `interface=` in config and verify with `ss -ulpn \| grep :67` |
| Local hostnames don't resolve | Missing `expand-hosts`, `domain=`, or `local=` | Add all three to config and restart |
| Upstream DNS fails | Wrong `server=` or `no-resolv` without `server=` | Check upstream with `dig google.com @<upstream-ip>` and fix `server=` directive |

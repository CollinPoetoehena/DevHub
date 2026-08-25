# DHCP Client Commands

Commands for inspecting and managing DHCP leases from the **client** side (the device requesting an IP, such as a VM). For server-side DHCP management (lease files, reservations, debugging, etc.), see the [dnsmasq reference](../dnsmasq.md#commands-dhcp).

---

## Table of Contents

- [dhclient — Request or Release a DHCP Lease](#dhclient--request-or-release-a-dhcp-lease)
- [NetworkManager — Release and Renew](#networkmanager--release-and-renew)
- [View Current DHCP Lease Details](#view-current-dhcp-lease-details)
- [Inspect DHCP Traffic](#inspect-dhcp-traffic)
- [Quick DHCP Debugging Checklist](#quick-dhcp-debugging-checklist)

---

## `dhclient` — Request or Release a DHCP Lease

`dhclient` is the ISC DHCP client. It sends DHCP DISCOVER/REQUEST messages to obtain a lease, or releases an existing one.

```bash
sudo dhclient eth0                     # request a new lease on eth0
sudo dhclient -r eth0                  # release the current lease
sudo dhclient -v eth0                  # verbose — shows the full DORA exchange
```

**Verbose output example:**

```
poetoec@proxmox-node1:~ $ sudo dhclient -v eth0
Internet Systems Consortium DHCP Client 4.4.3
Listening on LPF/eth0/28:94:01:8a:ec:28
Sending on   LPF/eth0/28:94:01:8a:ec:28
DHCPDISCOVER on eth0 to 255.255.255.255 port 67 interval 3
DHCPOFFER of 10.42.0.168 from 10.42.0.1
DHCPREQUEST for 10.42.0.168 on eth0 to 255.255.255.255 port 67
DHCPACK of 10.42.0.168 from 10.42.0.1
bound to 10.42.0.168 -- renewal in 40000 seconds.
```

This shows the full DORA handshake: DISCOVER → OFFER → REQUEST → ACK. The server (`10.42.0.1`, the lab router) assigned `10.42.0.168`.

---

## NetworkManager — Release and Renew

On systems using NetworkManager (most modern desktop/server Linux), use `nmcli` instead of `dhclient`:

```bash
# Bounce the connection (release + renew in one step):
sudo nmcli connection down "Wired connection 1" && sudo nmcli connection up "Wired connection 1"

# Or by device name:
sudo nmcli device disconnect eth0 && sudo nmcli device connect eth0
```

---

## View Current DHCP Lease Details

On the client, the active lease is stored in a file:

```bash
# dhclient lease file (location varies by distribution):
cat /var/lib/dhcp/dhclient.eth0.leases

# Or check the current IP and lease time via ip:
ip -4 addr show eth0
```

The `valid_lft` value in `ip addr` output shows the remaining lease time in seconds (`forever` = static, not DHCP).

---

## Inspect DHCP Traffic

Use [`tcpdump`](packet_capture.md#tcpdump) to capture live DHCP traffic and see exactly what the client sends and what the server responds:

```bash
sudo tcpdump -i eth0 -n port 67 or port 68
```

See the [tcpdump section](packet_capture.md#tcpdump) for full details, flags, and output format.

---

## Quick DHCP Debugging Checklist

| Check | Command |
|-------|---------|
| Does the client have an IP? | `ip -4 addr show eth0` |
| What is the default gateway? | `ip route \| grep default` |
| What DNS server was assigned? | `cat /etc/resolv.conf` or `resolvectl status` |
| Is the DHCP server reachable? | `ping <dhcp-server-ip>` |
| Is port 67 open on the server? | `ss -ulpn \| grep :67` (on the server) |
| What does the DHCP exchange look like? | `sudo tcpdump -i eth0 -n port 67 or port 68` |
| Force a fresh lease | `sudo dhclient -r eth0 && sudo dhclient -v eth0` |

# Router Role

Configures a Raspberry Pi as a dedicated lab router providing network isolation, DHCP, DNS, NAT, and firewall rules for the homelab.

## What This Role Does

| Task File | Purpose |
|-----------|---------|
| `networking.yml` | Static IP on LAN interface (`eth1`), enable IPv4 forwarding |
| `dhcp_dns.yml` | Install and configure `dnsmasq` for DHCP + DNS on the lab network |
| `firewall.yml` | NAT (masquerading), forwarding rules, lab→home blocking, INPUT protection |

## Network Topology

```
ISP Modem (192.168.2.0/24)
    │
    └── eth0 (WAN) ─── Raspberry Pi Router ─── eth1 (LAN) → Lab Switch
                         10.42.0.1/20                        │
                                                             ├── Lab devices
                                                             └── (get DHCP from Pi)
```

## Requirements

- Raspberry Pi 4 (or later) with Raspberry Pi OS Lite (64-bit)
- Two Ethernet interfaces: built-in (`eth0`) + USB adapter (`eth1`)
- SSH enabled and `ansibleremote` user created (via the users bootstrap play)
- `eth0` connected to ISP modem, `eth1` connected to lab switch

## Key Variables (defaults/main.yml)

| Variable | Default | Description |
|----------|---------|-------------|
| `router_wan_interface` | `eth0` | WAN interface (ISP modem side) |
| `router_lan_interface` | `eth1` | LAN interface (lab switch side) |
| `router_lan_ip` | `10.42.0.1` | Gateway IP for the lab network |
| `router_lan_cidr` | `20` | Subnet mask (4094 usable IPs) |
| `router_home_subnet` | `192.168.2.0/24` | Home network to block from lab |
| `router_dhcp_range_start` | `10.42.0.100` | DHCP pool start |
| `router_dhcp_range_end` | `10.42.0.200` | DHCP pool end |
| `router_dhcp_lease_time` | `24h` | DHCP lease duration |
| `router_static_leases` | `[]` | Static MAC→IP reservations |
| `router_block_lab_to_home` | `true` | Firewall: block lab→home traffic |

## Usage

```bash
# Run only the router role:
ansible-playbook site.yml --tags router

# Run a specific part:
ansible-playbook site.yml --tags firewall
ansible-playbook site.yml --tags dhcp
ansible-playbook site.yml --tags networking
```

## Tags

- `router` — all router tasks
- `networking` — static IP and IP forwarding
- `dhcp`, `dns`, `dnsmasq` — DHCP/DNS configuration
- `firewall`, `nat` — iptables rules
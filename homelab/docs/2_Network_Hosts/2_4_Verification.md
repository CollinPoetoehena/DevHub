# Verification

TODO: here network verification.

See [Network Commands](../reference/network/Network_Commands.md) for detailed explanations of each command and its output used below. The following commands are used for verification, specifying only the expected outputs, the commands themselves are explained in the document above.

> **Note:** The [router playbook/verify.yml](../../ansible/roles/router/tasks/verify.yml) already performs these connectivity checks automatically. The checks below are just basic manual verification steps for reference, see the playbook for the full automated verification and detailed checks for more comprehensive testing.

## Pi router Connectivity

From the Pi:

```bash
nmcli connection show   # lab-wan (eth0), lab-lan (eth1), vlan-management (eth1.10), vlan-services (eth1.20), vlan-iot (eth1.30), lo
ip a                    # eth0: 192.168.2.x/24 (DHCP from ISP modem); eth1: no IPv4; eth1.10: 10.42.10.1/24; eth1.20: 10.42.20.1/24; eth1.30: 10.42.30.1/24
ip r                    # default via 192.168.2.254 dev eth0; 10.42.10.0/24 dev eth1.10; 10.42.20.0/24 dev eth1.20; 10.42.30.0/24 dev eth1.30
ping -c 3 192.168.2.1   # Test ISP modem reachability
ping -c 3 8.8.8.8       # Test internet from Pi
ip neigh                # 192.168.2.254 on eth0 REACHABLE; lab devices on eth1.10/eth1.20/eth1.30 REACHABLE
arp -n                  # Same information as ip neigh, in older format
```

## Lab Device Connectivity

From a lab device (e.g. Proxmox host on VLAN 10):

```bash
ip a                    # Should show an IP in 10.42.10.x (management VLAN)
ip r                    # Should show: default via 10.42.10.1
ping -c 3 10.42.10.1    # Test gateway (Pi) reachability
ping -c 3 8.8.8.8       # Test internet connectivity
ping -c 3 google.com    # Test DNS resolution
```

## VLAN Setup & Tagging

**Use parent interface for capturing VLAN tags:** When you capture on the parent interface, you’re seeing the raw Ethernet frames before Linux processes them. That’s why the VLAN tag is still present there. Once the frame reaches the VLAN sub‑interface (like eth1.10), the kernel has already stripped the 802.1Q header and delivered a clean, de‑tagged packet, so tcpdump can’t show the tag anymore.
```bash
# On the router run:
sudo tcpdump -i eth1 -n -e
# Optionally add -vvv for more output

# On a Proxmox host run:
ping 10.42.10.1 # Test management VLAN reachability (VLAN 10)
ping 10.42.20.1 # Test services VLAN reachability (VLAN 20)
ping 10.42.30.1 # Test IoT VLAN reachability (VLAN 30)
```
This should show in the tcpdump output on the router, with VLAN tags visible for each of the pings from the Proxmox host. For example:
```
poetoec@lab-router:~ $ sudo tcpdump -i eth1 -n -e 
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on eth1, link-type EN10MB (Ethernet), snapshot length 262144 bytes
19:48:52.661201 08:97:98:9e:8a:9e > 9c:69:d3:94:66:27, ethertype 802.1Q (0x8100), length 102: vlan 10, p 0, ethertype IPv4 (0x0800), 10.42.10.10 > 10.42.10.1: ICMP echo request, id 53939, seq 1, length 64
19:48:52.661353 9c:69:d3:94:66:27 > 08:97:98:9e:8a:9e, ethertype 802.1Q (0x8100), length 102: vlan 10, p 0, ethertype IPv4 (0x0800), 10.42.10.1 > 10.42.10.10: ICMP echo reply, id 53939, seq 1, length 64
19:48:53.663179 08:97:98:9e:8a:9e > 9c:69:d3:94:66:27, ethertype 802.1Q (0x8100), length 102: vlan 10, p 0, ethertype IPv4 (0x0800), 10.42.10.10 > 10.42.10.1: ICMP echo request, id 53939, seq 2, length 64
19:48:53.663267 9c:69:d3:94:66:27 > 08:97:98:9e:8a:9e, ethertype 802.1Q (0x8100), length 102: vlan 10, p 0, ethertype IPv4 (0x0800), 10.42.10.1 > 10.42.10.10: ICMP echo reply, id 53939, seq 2, length 64
```
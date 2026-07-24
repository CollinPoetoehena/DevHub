# Network Setup

A stable network is the foundation of a reliable homelab. This document covers the background on networking concepts, the setup options available, why a dedicated lab router behind the ISP modem is the right choice, and the specific steps to set it up using a Raspberry Pi as the lab router.

---

## Background: Networking Concepts

### ISP Modem / Gateway

The device provided by your ISP (e.g. a KPN Experia Box) that connects your home to the internet. It acts as the gateway for the home network and runs DHCP to assign IPs to home devices. Usually also contains router functionality, WiFi, and firewall rules. It is the main router for the home network.

### Router

A router connects two or more networks and directs traffic between them. It has:

- A WAN port (facing the internet or an upstream network)
- One or more LAN ports (facing your devices)
- Its own DHCP server to assign IPs on the LAN side
- Firewall rules to control what traffic can pass

A router creates a new, separate network. This is what makes it useful for isolation.

### Switch

A switch connects multiple devices within the same network. It does not create a new network, does not run DHCP, provides no firewall, and does no routing. Think of it as a power strip for Ethernet: it gives you more ports, but everything plugged in is on the same network.

| Device | Creates new network | DHCP | Firewall | Isolation |
|--------|---------------------|------|----------|-----------|
| Switch | No                  | No   | No       | No        |
| Router | Yes                 | Yes  | Yes      | Yes       |

### Subnet

A subnet is a range of IP addresses that form one logical network. For example, `192.168.10.0/24` covers addresses `192.168.10.1` to `192.168.10.254`. Devices on different subnets cannot communicate directly — they need a router in between. This separation is what provides network isolation.

### DHCP

The protocol that automatically assigns IP addresses to devices when they join a network. If two DHCP servers run on the same subnet, they hand out conflicting IPs, causing connectivity failures for affected devices.

---

## Network Setup Options

### Option 1: Lab devices directly on the home network

Connect lab devices (Proxmox hosts, worker nodes) directly to the ISP modem or home switch.

```
ISP Modem → Home Switch → Lab Devices + Home Devices (same network)
```

**Why not:** Lab mistakes — DHCP conflicts, Proxmox bridge misconfiguration, routing loops — directly affect the home network. This is what caused home devices (phone, TV, printer) to lose internet access when Proxmox was first connected: its `vmbr0` bridge interfered with the home LAN's DHCP, creating IP conflicts that were visible in the ISP modem's admin page.

### Option 2: VLANs on the ISP modem

Segment the network using VLANs configured on the ISP modem itself.

**Why not:** Most ISP modems have very limited or no VLAN support. A misconfiguration can break the entire home network. Not practical.

### Option 3: Dedicated router behind the ISP modem (chosen approach)

Place a dedicated lab router between the ISP modem and all lab devices. The lab runs on its own subnet, fully isolated from the home network.

```
ISP Modem (192.168.2.0/24) → Lab Router → Lab Devices (10.42.0.0/20)
```

---

## Why a Dedicated Router Behind the ISP Modem

**Full isolation (maintaining home network is not in my homelab's scope):** The lab runs on its own subnet with its own DHCP and firewall. Lab mistakes — DHCP conflicts, Proxmox bridge issues, Kubernetes networking — are contained within the lab network and never reach home devices. Avoid changing the ISP Modem's core configuration when others in the house depend on it for internet access. Changing the home network configuration can break connectivity for everyone, so it’s best to leave it as-is and put your own router behind it for the lab. Furthermore, the ISP modem may have limited or no VLAN support, making it unsuitable for isolating your lab network. Finally, it is not in my homelab's scope to maintain the home network, so I want to keep it untouched and let the ISP modem handle the home network while I experiment freely in my lab network.

**Keeps the ISP modem intact:** Other people in the house depend on the ISP modem for WiFi and internet. Replacing it or changing its configuration would mean taking ownership of the entire home network. Keeping it untouched means home connectivity stays stable regardless of what happens in the lab.

**Learn networking:** Building and running your own router is a hands-on way to learn subnetting, routing, DHCP, firewall rules, and VLANs in a real environment.

**It is fun:** Designing and configuring your own network infrastructure is genuinely enjoyable.

**Classic mistakes that break home networks (avoid these):**

- Running a DHCP server on the same subnet as home devices
- Changing DNS settings on the ISP modem
- Connecting Proxmox or Kubernetes nodes directly to the home network
- Misconfiguring Proxmox bridges (can cause broadcast loops)
- Running firewall experiments on the home LAN

---

## Setup: Lab Router on a Raspberry Pi

A Raspberry Pi is used as the dedicated lab router. It is cost-effective, educational, and provides full control over routing, DHCP, firewall rules, and future VLANs.

```
Internet
    │
ISP Modem/Router
(192.168.1.0/24)
    │
    ├── Home devices
    │
    └── Raspberry Pi Router (Homelab Network: 10.42.0.0/20)
            │
      Managed Switch (simply expands the number of available LAN ports (router typically does not have enough ports for all physical lab devices below))
            ├─ VLAN 10 Management    (10.42.10.0/24)
            │    ├─ 10.42.10.10  PVE1 (phycial machine: Proxmox VE host 1)
            │    ├─ 10.42.10.11  PVE2 (physical machine: Proxmox VE host 2)
            │    ├─ 10.42.10.12  PVE3 (physical machine: Proxmox VE host 3)
            │    ├─ 10.42.10.20  Router (physical machine: Raspberry Pi Router)
            │    └─ 10.42.10.30  Switch (physical machine: Managed Switch)
            ├─ VLAN 20 Monitoring    (10.42.20.0/24)
            │    ├─ 10.42.20.10  Monitoring VM1 (runs on PVE1, such as Prometheus, Grafana, etc.)
            │    ├─ 10.42.20.11  Monitoring VM2 (same as above, runs on PVE2)
            │    └─ 10.42.20.12  Monitoring VM3 (same as above, runs on PVE3)
            └─ VLAN 30 Kubernetes    (10.42.30.0/24)
                 ├─ 10.42.30.10  k8s-control-plane-1 (VM; runs on PVE1, part of Kubernetes cluster)
                 ├─ 10.42.30.11  k8s-control-plane-2 (VM; runs on PVE2, part of Kubernetes cluster)
                 ├─ 10.42.30.12  k8s-worker-1 (VM; runs on PVE1, part of Kubernetes cluster)
                 ├─ 10.42.30.13  k8s-worker-2 (VM; runs on PVE2, part of Kubernetes cluster)
                 └─ 10.42.30.14  k8s-worker-3 (VM; runs on PVE3, part of Kubernetes cluster)
```

### Prerequisites (including background knowledge for the setup)
#### Compute: Raspberry Pi 4 or later
The compute unit — the actual computer that runs the router software. It runs the Linux OS, IP forwarding, DHCP server, NAT, firewall rules, etc. that make it function as a router. A Raspberry Pi is a small, low-cost single-board computer. It runs a full Linux OS, has USB ports, HDMI, GPIO pins, and built-in Ethernet. It uses an ARM architecture (64-bit ARMv8 on the Pi 4), which differs from the x86-64 architecture used by most desktop and server hardware — keep this in mind when installing software or compiling binaries. It draws very little power (typically 3–7W) and is well-suited for running as a dedicated appliance such as a router, DNS server, or monitoring node. The Pi 4 and later models are capable enough to handle routing, DHCP, NAT, and firewalling for a small homelab. It is generally cheaper than a mini PC or dedicated router appliance for small applications like a router, and it is a great learning tool for Linux networking.
#### Storage: SD Card with Raspberry Pi OS Lite (64-bit)
An SD card (Secure Digital card) is a small, removable flash storage card. The Raspberry Pi has no built-in storage (no hard drive or SSD); the SD card is its primary storage device — it holds the operating system, all configuration files, and any data the Pi writes. The Pi boots directly from it. Raspberry Pi OS Lite is a minimal, headless (no desktop environment) version of the OS based on Debian, optimised for server and appliance use cases. "64-bit" refers to the ARM64 (AArch64) instruction set, which allows the OS to use more than 4 GB of RAM and run 64-bit software. You flash the OS image onto the SD card using [Raspberry Pi Imager](https://www.raspberrypi.com/software/) from a desktop or laptop, then insert the card into the Pi — it boots from it automatically. Most laptops do not have a built-in SD card reader (and even those that do often only accept full-size SD, not microSD). In that case, use a USB SD card reader/adapter (a small dongle that accepts a microSD card and plugs into a USB port (I bought the "ISY ICR-120 USB 2.0-kaartlezer USB 2.0" for 6.99 EUR at MediaMarkt because "ISY" is a reputable brand and cheap (it is MediaMarkt's store brand))). Plug it into your laptop, insert the microSD card, and it appears as a removable drive that Raspberry Pi Imager can write to.
#### Network Interfaces (two required)
A router needs two separate network interfaces: one facing the upstream network (WAN) and one facing the lab devices (LAN). The Pi's built-in Ethernet port serves as the WAN side; a USB-to-Ethernet adapter adds the LAN side.
```text
ISP Modem LAN port → Pi eth0 (WAN side)
Pi eth1 (LAN side) → Lab switch or directly to lab devices
```
The Pi's `eth0` receives an IP from the ISP modem (e.g. `192.168.2.x`). The Pi's `eth1` is the gateway for the lab network (e.g. `10.42.0.1`).
- **built-in Ethernet (`eth0`):** Connects to the ISP modem (WAN side)
- **USB-to-Ethernet adapter (`eth1`):** Connects to the lab switch to provide the LAN side (I bought the "TP-LINK UE300C" for 12.99 EUR at MediaMarkt because "TP-LINK" is a reputable brand and it is cheap; perfect for my homelab use case). Plug it into a USB 3.0 port on the Pi. Raspberry Pi OS includes the `r8152` driver by default, so it is detected automatically and appears as `eth1` — no manual driver installation needed. Verify with `ip link` after booting.
#### Managed Switch
Expands the number of available LAN ports (the Pi's `eth1` is a single port, so without a switch you can only connect one device directly). A managed switch additionally allows you to create VLANs, monitor traffic, and configure port settings via a web interface — an unmanaged switch only gives you more ports with no configuration options. I bought the "NETGEAR GS305E" for 24.99 EUR at MediaMarkt (the "TP-LINK TL-SG105E" is a good alternative).
#### Ethernet Cables
Used to connect the Pi to the ISP modem, the Pi to the lab switch, and each lab device to the switch. Preferably Cat6 or better for gigabit speeds.
- **ISP modem → lab router:** 1 cable (3 m; slightly longer than the other cables to accommodate placement). I bought the "ISY IPC-6030-1-GB Netwerkkabel 3 m Wit" at MediaMarkt for 12.99 EUR because "ISY" is a reputable brand and cheap (other slightly cheaper brands like "LINDY 47176 Netwerkkabel 3 m Zwart" are also possible, but in this case I chose the cable above since it is slightly more reliable and of higher quality). Avoid very cheap cables that may not support gigabit speeds or may have poor shielding, which can cause connectivity issues and unstable connections.
- **Lab router → lab switch:** 1 cable (0.75 m). I bought the "ISY IPC-1012 CAT6A U/UTP Slim Netwerkkabel 0,75 m Wit" at MediaMarkt for 9.99 EUR (same reasoning as above).
- **Lab switch → lab devices:** 1 cable per device (same model as above).
#### Access to the ISP Modem Admin Page
Used to reserve a static IP for the Pi's WAN interface (`eth0`) by MAC address, and to check for IP conflicts.

### Step 1: Reserve a Static IP for the Pi on the ISP Modem

Log in to the ISP modem admin page (typically `192.168.2.1`) and reserve a static DHCP lease for the Pi's WAN interface using its MAC address (`eth0`). This ensures the Pi always receives the same upstream IP.

### Step 2: Configure the Pi as a Router
#### Step 2.1: Assemble and Set up the Pi
1. Assemble the Raspberry Pi: fit it in a case, and connect any accessories. See the [official product page](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/), [getting started guide](https://www.raspberrypi.com/documentation/computers/getting-started.html). Possible accessories (including link to set them up/configure them):
    - [case](https://www.raspberrypi.com/products/raspberry-pi-4-case/)
    - [power supply](https://www.raspberrypi.com/products/power-supply/)
    - [Raspberry Pi SD Card](https://www.raspberrypi.com/products/sd-cards/)
    - [case fan (including heat sink)](https://www.raspberrypi.com/products/raspberry-pi-4-case-fan/) (this link shows how you can set up the fan and assemble it in the case)
    - USB-to-Ethernet adapter: Plug it into a USB 3.0 port on the Pi. Raspberry Pi OS includes the `r8152` driver by default, so it is detected automatically and appears as a second network interface (e.g. `eth1`) — no manual driver installation needed. Verify with `ip link` after booting.
2. Flash Raspberry Pi OS Lite (64-bit) to the SD card using Raspberry Pi Imager.
3. Insert the SD card, connect `eth0` to the ISP modem LAN port and `eth1` to the lab switch (or directly to a lab device).
4. Boot the Pi and SSH into it.
TODO: from this onwards it can be left to Ansible
5. Set a static IP on `eth1` (LAN side).
6. Enable IP forwarding.
7. Install and configure `dnsmasq` to serve DHCP on the lab network.
8. Configure NAT with `iptables` so lab devices can reach the internet through `eth0`.
9. Verify connectivity from a lab device and from the Pi itself.

TODO: I want to do this via Ansible, use Ansible to configure all of this and add code in this repo!
TODO: for now use the Pi OS with Ansible and make it in a role called `router` that configures the Pi as a router with DHCP, NAT, and firewall rules, etc. 
TODO: add detailed comments everywhere in the Ansible code what everything does, why it is needed, etc., so I can understand it well and always go back to it later and easily read it, etc.
TODO: add a NOTE here later can use for example OpenWRT or pfSense on the Pi, but for now I configure it myself entirely because I want to learn Linux networking and understand it, you learn a lot more by doing everything yourself without a ready-made solution like OpenWRT or pfSense. I can always later on do it that way anyway.
#### Step 2.2: Configure the Pi as a Router
TODO: here use Ansible, below can all move to Ansible and here only the run for the Ansible playbook.
**TODO: VERY IMPORTANT:** Also add firewalling with the lab router to block access to the home network from the lab network, an extra safety measure to prevent lab devices from accidentally reaching the home network. This is important because if a lab device is compromised, it should not be able to access the home network. Add firewall rules to block traffic from the lab subnet reaching the home network in the router configuration (TODO: add in Ansible variables files the home network subnet).
**2a. Set a static IP on the LAN interface (`eth1`):**

Edit `/etc/dhcpcd.conf`:

```
interface eth1
static ip_address=10.42.0.1/20
```

**2b. Enable IP forwarding:**

```bash
echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

**2c. Install and configure `dnsmasq` for DHCP on the lab network:**

```bash
sudo apt install dnsmasq
```

Edit `/etc/dnsmasq.conf`:

```
interface=eth1
dhcp-range=10.42.0.100,10.42.0.200,255.255.240.0,24h
```

Apply and enable:

```bash
sudo systemctl restart dnsmasq
sudo systemctl enable dnsmasq
```

**2d. Configure NAT so lab devices can reach the internet:**

```bash
sudo apt install iptables iptables-persistent

sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT
sudo iptables -A FORWARD -i eth0 -o eth1 -m state --state RELATED,ESTABLISHED -j ACCEPT

sudo netfilter-persistent save
```

### Step 3: Connect Lab Devices

Connect all lab devices to the Pi's LAN side (`eth1`) through a switch attached to `eth1`. Devices will receive IPs in `10.42.0.0/20` from the Pi's DHCP server and route internet traffic through the Pi Router.

### Step 4: Verify

From a lab device:

```bash
ip a                        # Should show 10.42.0.x
ip r                        # Should show default via 10.42.0.1
ping -c 3 10.42.0.1         # Test gateway (Pi) reachability
ping -c 3 8.8.8.8           # Test internet connectivity
ping -c 3 google.com        # Test DNS resolution
```

From the Pi:

```bash
ip a                        # eth0: ISP-assigned IP, eth1: 10.42.0.1
ping -c 3 192.168.2.1       # Test ISP modem reachability
ping -c 3 8.8.8.8           # Test internet from Pi
```

---

## Setup: TODO: other network setup
TODO: here add things like VLANs on the managed switch, and any other networking setup that may be required outside of the lab router, etc.

---

## Troubleshooting

### Some home network devices cannot connect to the internet

**Symptoms:** Multiple devices (e.g. phone, TV, printer over Ethernet) lose internet access, while others remain unaffected.

**Likely cause:** Proxmox VE running on the home network can cause IP conflicts. When Proxmox creates a Linux bridge (`vmbr0`) on the same subnet as your home LAN, it may respond to ARP requests or DHCP traffic in a way that conflicts with the ISP modem's DHCP assignments. This causes some devices to get duplicate IPs or lose their lease, which breaks connectivity for those devices but not necessarily all of them.

**Diagnosis:**
1. Log in to your ISP's modem/router admin page (typically at `192.168.2.1` or `192.168.1.1`).
2. Look for a connected devices or DHCP leases table.
3. Check for duplicate IP addresses or unexpected entries — this confirms an IP conflict.

**Solutions:**

Partial fix (not fully safe): Reserve static IPs in your ISP modem for all lab devices and configure a static address and internal bridge in Proxmox. This reduces the chance of conflict but does not eliminate it, since Proxmox bridge interfaces can still interfere with LAN traffic.

Recommended fix: Set up a dedicated router for the homelab (e.g. a Raspberry Pi or TP-Link ER605) placed between your ISP modem and all lab devices. This creates a fully isolated subnet for the lab so Proxmox and other lab services can never interfere with the home network.

```
ISP Modem (e.g. 192.168.2.0/24) → Lab Router (e.g. 192.168.10.0/24) → Lab Devices
```

**Interim workaround (while setting up the dedicated router):** Shut down the Proxmox VE host and temporarily install Ubuntu Desktop on it via bootable USB (see [OS and Hypervisor Installation](2_2_OS_Hypervisor.md) for steps). This prevents Proxmox from interfering with the home network on each boot, while still allowing you to use the machine. Once the dedicated router is ready, reinstall Proxmox VE on the host.
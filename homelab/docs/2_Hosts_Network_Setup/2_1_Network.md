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

- **Subnet mask:** A 32-bit number that defines which part of an IP address is the *network* portion and which part is the *host* portion. Written either in dotted-decimal (e.g. `255.255.255.0`) or CIDR prefix notation (e.g. `/24`). The network portion is the same for all devices in the subnet; the host portion is what makes each device's address unique within that subnet. In binary, the mask is a block of `1`s (network bits) followed by `0`s (host bits):
    ```
    255.255.255.0    =  11111111.11111111.11111111.00000000  (/24 — 24 network bits,  8 host bits)
    255.255.0.0      =  11111111.11111111.00000000.00000000  (/16 — 16 network bits, 16 host bits)
    255.255.240.0    =  11111111.11111111.11110000.00000000  (/20 — 20 network bits, 12 host bits)
    255.255.252.0    =  11111111.11111111.11111100.00000000  (/22 — 22 network bits, 10 host bits)
    255.255.255.192  =  11111111.11111111.11111111.11000000  (/26 — 26 network bits,  6 host bits)
    ```
    Note how the boundary can fall anywhere inside an octet (e.g. `/22` splits the third octet: `11111100` — 6 bits network, 2 bits host; `/26` splits the fourth octet: `11000000` — 2 bits network, 6 bits host). This is what makes CIDR "classless" — there is no requirement for the boundary to fall on an octet boundary.
- **CIDR notation (Classless Inter-Domain Routing):** A compact way of writing an IP address together with its subnet mask as a single string: `<network-address>/<prefix-length>`. The prefix length (the number after the `/`) is simply the count of `1` bits in the subnet mask. CIDR replaced the old class-based system (Class A/B/C) and allows subnets of any size.
- **How to read CIDR — key numbers:**
    | CIDR  | Subnet Mask       | Usable Hosts | Host Range (example)                    | Notes                                              |
    |-------|-------------------|--------------|-----------------------------------------|----------------------------------------------------|
    | `/8`  | `255.0.0.0`       | 16,777,214   | `10.0.0.1` – `10.255.255.254`           | Very large; private `10.x.x.x` space               |
    | `/16` | `255.255.0.0`     | 65,534       | `192.168.0.1` – `192.168.255.254`       | Large; private `192.168.x.x` space                 |
    | `/20` | `255.255.240.0`   | 4,094        | `10.42.0.1` – `10.42.15.254`            | Used for this homelab lab network                  |
    | `/22` | `255.255.252.0`   | 1,022        | `10.42.8.1` – `10.42.11.254`            | Spans 4 "class C" blocks; used for medium LANs     |
    | `/24` | `255.255.255.0`   | 254          | `192.168.2.1` – `192.168.2.254`         | Most common home/office subnet                     |
    | `/26` | `255.255.255.192` | 62           | `10.42.10.1` – `10.42.10.62`            | Quarter of a /24; used to carve up a single block  |
    | `/30` | `255.255.255.252` | 2            | `10.0.0.1` – `10.0.0.2`                 | Point-to-point links (e.g. router–router)          |
    | `/32` | `255.255.255.255` | 0 (1 host)   | just that one IP                        | Single host route                                  |

    Formula: usable hosts = $2^{(32 - \text{prefix})} - 2$ (subtract 2: one for the network address, one for the broadcast address).
- **Network address and broadcast address:** For any subnet, the first address is the *network address* (identifies the subnet itself, not assignable to a host) and the last address is the *broadcast address* (sends to all hosts in the subnet, not assignable). Everything in between is usable.
    ```
    Subnet:    10.42.0.0/20
    Network:   10.42.0.0       ← first address, not assignable
    Hosts:     10.42.0.1  –  10.42.15.254   ← 4,094 usable addresses
    Broadcast: 10.42.15.255    ← last address, not assignable

    Subnet:    10.42.8.0/22
    Network:   10.42.8.0       ← first address, not assignable
    Hosts:     10.42.8.1  –  10.42.11.254   ← 1,022 usable addresses (spans .8, .9, .10, .11 in the third octet)
    Broadcast: 10.42.11.255    ← last address, not assignable

    Subnet:    10.42.10.0/26
    Network:   10.42.10.0      ← first address, not assignable
    Hosts:     10.42.10.1  –  10.42.10.62   ← 62 usable addresses (only the first quarter of the .10 block)
    Broadcast: 10.42.10.63     ← last address, not assignable
    ```
- **Worked examples:**
    - `192.168.2.59/24` → network `192.168.2.0`, hosts `.1`–`.254`, broadcast `.255`. The Pi's `eth0` address on the home network.
    - `10.42.0.1/20` → network `10.42.0.0`, hosts `10.42.0.1`–`10.42.15.254`, broadcast `10.42.15.255`. The Pi's `eth1` address; the entire lab network fits inside this `/20`.
    - `127.0.0.1/8` → the loopback subnet; all of `127.x.x.x` is local to the machine.
    - `10.42.8.50/22` → network `10.42.8.0`, hosts `10.42.8.1`–`10.42.11.254`, broadcast `10.42.11.255`. A `/22` spans four consecutive `/24` blocks (`.8`, `.9`, `.10`, `.11`). A host at `.50` in the third octet is well within the range — the boundary is at `.11.255`, not at `.8.255`.
    - `10.42.10.33/26` → network `10.42.10.0`, hosts `10.42.10.1`–`10.42.10.62`, broadcast `10.42.10.63`. This is the first `/26` carved out of `10.42.10.0/24`. The second `/26` would be `10.42.10.64/26` (hosts `.65`–`.126`), the third `.128/26`, the fourth `.192/26` — four equal quarters of the same `/24`.

> **Note:** You do not need to calculate all of this by hand. Know the basics (what CIDR means, how to read a subnet mask, roughly how many hosts a prefix gives you), but for anything more precise use an online subnet calculator: [calculator.net](https://www.calculator.net/ip-subnet-calculator.html), [subnet-calculator.com](https://www.subnet-calculator.com/), or [subnet-calculator.nl](https://subnet-calculator.nl/).

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

Full network setup (in .md diagram format to save space (no image file needed for this setup)):
```
Internet
    │
ISP Modem/Router
(192.168.2.0/24)
    │
    ├── Home devices
    │
    └── Raspberry Pi Router (Homelab Network: 10.42.0.0/20) `eth0` (WAN; connected to ISP Modem) → `eth1` (LAN; connected to switch)
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
- **What is an SD card?** A small, removable flash storage card (Secure Digital). The Raspberry Pi has no built-in storage (no hard drive or SSD) — the SD card is its primary storage device. It holds the operating system, all configuration files, and any data the Pi writes. The Pi boots directly from it.
- **What is an OS?** The operating system (OS) is the software that manages the hardware and provides a foundation for running programs. Without an OS, the Pi is just bare hardware. For a router, the OS runs the kernel that handles networking, the DHCP server, the firewall, etc.
- **Why Raspberry Pi OS Lite (and not Ubuntu Server or others)?** Raspberry Pi OS is the officially supported OS for the Pi, maintained by the Raspberry Pi Foundation. It is based on Debian, well-tested on Pi hardware, and includes Pi-specific optimisations and drivers out of the box (e.g. the `r8152` USB-Ethernet driver, GPU memory split, hardware interfaces). "Lite" means no desktop environment — just a minimal command-line system, which is exactly what you want for a headless appliance like a router. Ubuntu Server also works on the Pi, but it requires more manual configuration for Pi-specific hardware, has a larger footprint, and offers no real advantage for this use case. Stick with Raspberry Pi OS Lite.
- **What does "64-bit" mean?** It refers to the ARM64 (AArch64) instruction set. The Pi 4's CPU supports 64-bit, which allows the OS to use more than 4 GB of RAM and run 64-bit software. Use the 64-bit version.
- **How to flash the OS onto the SD card?** Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) — a free tool from the Raspberry Pi Foundation. Download and install it on your laptop, select the OS image and your SD card as the target, and click Write. It downloads the image, writes it, and verifies it. Then insert the SD card into the Pi and it boots from it automatically.
- **What if your laptop has no SD card reader?** Most laptops do not have a built-in SD card reader (and even those that do often only accept full-size SD, not microSD). Use a USB SD card reader/adapter — a small dongle that accepts a microSD card and plugs into a USB port. I bought the "ISY ICR-120 USB 2.0-kaartlezer USB 2.0" for 6.99 EUR at MediaMarkt (ISY is MediaMarkt's store brand). Plug it into your laptop, insert the microSD card, and it appears as a removable drive that Raspberry Pi Imager can write to.
> **Note — OS alternatives:** You could run OpenWRT or pfSense on the Pi instead. Both are purpose-built router/firewall OSes with polished web UIs and pre-configured networking stacks. However, the goal of my homelab ([see personal goal](../1_Goals_Hardware.md)) is to learn Linux networking by doing it yourself — configuring IP forwarding, DHCP, NAT, and firewall rules manually gives you a much deeper understanding than clicking through a GUI. You can always switch to OpenWRT or pfSense later once you understand what they are doing under the hood.
#### Network Interfaces (two required)
A router needs two separate network interfaces: one facing the upstream network (WAN) and one facing the lab devices (LAN). The Pi's built-in Ethernet port serves as the WAN side; a USB-to-Ethernet adapter adds the LAN side.
```text
ISP Modem LAN port → Pi eth0 (WAN side)
Pi eth1 (LAN side) → Lab switch or directly to lab devices
```
The Pi's `eth0` receives an IP from the ISP modem (e.g. `192.168.2.x`). The Pi's `eth1` is the gateway for the lab network (e.g. `10.42.0.1`).
- **built-in Ethernet (`eth0`):** Connects to the ISP modem (WAN side).
    - **How to get from the ISP modem to another floor in the house?** Use a long Ethernet cable (e.g. 10 m) to reach the Pi from the modem. If you need to go through walls or floors, consider using a flat Ethernet cable or running it through a conduit.
    - **Avoid WiFi for the WAN side:** The Pi does have a WiFi interface (`wlan0`), which could be used for the WAN side instead of `eth0`. However, WiFi is less stable than wired Ethernet, and I want to avoid potential connectivity issues in my lab. For example, in an earlier version I tested with WiFi, which resulted in an unstable and very slow connection where you could basically do almost nothing (I could not even connect to the Pi via SSH, while all other devices (e.g. my laptop) had perfectly fine WiFi connections). Therefore, I use the built-in Ethernet port for the WAN side and a USB-to-Ethernet adapter for the LAN side, and do not recommend using WiFi for the WAN side.
- **USB-to-Ethernet adapter (`eth1`):** Connects to the lab switch to provide the LAN side (I bought the "TP-LINK UE306" for 12.99 EUR at MediaMarkt because "TP-LINK" is a reputable brand and it is cheap; perfect for my homelab use case (do not buy the "TP-LINK UE300C" because it has is USB-C, which the Raspberry Pi model 4 does not have!)). Plug it into a USB-A port on the Pi. Raspberry Pi OS includes the `r8152` driver by default, so it is detected automatically and appears as `eth1` — no manual driver installation needed. Verify with `ip link` after booting.
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
1. Assemble the Raspberry Pi: fit it in a case, and connect any accessories. See the [official product page](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/), [getting started guide](https://www.raspberrypi.com/documentation/computers/getting-started.html). See the steps below for how to configure the Pi and setup SSH, etc. Possible accessories (including link to set them up/configure them):
    - [case](https://www.raspberrypi.com/products/raspberry-pi-4-case/)
    - [power supply](https://www.raspberrypi.com/products/power-supply/)
    - [Raspberry Pi SD Card](https://www.raspberrypi.com/products/sd-cards/)
    - [case fan (including heat sink)](https://www.raspberrypi.com/products/raspberry-pi-4-case-fan/) (this link shows how you can set up the fan and assemble it in the case).
    - USB-to-Ethernet adapter: Plug it into a USB 3.0 port on the Pi. Verify with `ip link` after booting.
2. Insert the SD card (already containing flashed OS, [see prerequisites](#prerequisites-including-background-knowledge-for-the-setup)), connect `eth0` to the ISP modem LAN port and `eth1` to the lab switch.
3. Boot the Pi and perform the first setup. For the first boot, connect a monitor (HDMI), keyboard, and mouse (USB) to complete the initial setup. In the next step we enable SSH — after that, all subsequent access is via SSH and the Pi runs headless (no monitor, keyboard, or mouse needed). 
4. Enable SSH manually via terminal (required before you can access it from another device!): SSH (Secure Shell) lets you remotely control the Pi from your laptop over the network — no monitor or keyboard needed. Once enabled, all subsequent management is done via SSH.
```bash
# ========================== Ensure the Pi is up-to-date: ==========================
sudo apt update && sudo apt full-upgrade -y
sudo reboot

# ========================== Enable SSH: ==========================
# Check if SSH is already enabled:
sudo systemctl status ssh
# If you see "Active: active (running)", SSH is already enabled.

# If not, enable and start it:
sudo systemctl enable ssh
sudo systemctl start ssh
sudo systemctl status ssh   # Verify: should show "Active: active (running)"

# Confirm SSH is listening on port 22 (sudo ensures the process list is complete):
sudo ss -tulnp | grep ssh
# Should show: LISTEN 0 128 0.0.0.0:22

# ========================== Find the Pi's IP address and hostname: ==========================
# Find the Pi's IP address from the Pi itself:
hostname -I
# Example output: 192.168.2.123
# Or from the network interfaces on the Pi itself (assuming eth0 is the interface connected to the home network):
ip addr show eth0 | grep 'inet '
# Example output: inet 192.168.2.123/24 brd 192.168.2.255 scope global dynamic noprefixroute eth0
# Or from another device on the same network (e.g., your laptop)
arp -a
# NOTE: This outputs all devices on the same subnet that your laptop can see. Look for the Pi's MAC address (printed on the Pi board) to find its IP address.

# Or use the hostname command to get the Pi's hostname:
hostname
# Example output: raspberrypi

# ========================== Connect from another device (e.g. your laptop): ==========================
# Optionally check if the Pi is reachable from your laptop:
ping <pi-ip>
# If not reachable, make sure the Pi is connected to the ISP modem and that your laptop is on the same network (e.g., connected to the same WiFi or LAN (e.g. if the ISP modem has IP 192.168.2.1, your laptop and the Pi should have an IP in the same subnet: 192.168.2.x)).

# Connect from your laptop:
ssh <username>@<pi-ip>
# Example: ssh pi@192.168.2.123
# Use the username you set during Raspberry Pi OS setup (default is "pi").
# On first connect you'll be asked to confirm the host fingerprint — type "yes".

# Alternatively, connect by hostname (no need to look up the IP):
ssh <username>@raspberrypi.local
# NOTE: This only works from the primary OS on your laptop (e.g., Windows, macOS, Linux) if it supports mDNS/Bonjour. If it doesn't work, use the IP address instead. For example, this does not work from WSL because WSL doesn't automatically participate in your local network's mDNS/Bonjour (Multicast DNS, Apple's Bonjour service for resolving names like raspberrypi.local without a DNS server) name resolution, so a hostname like raspberrypi.local often cannot be resolved inside WSL even though it may work from Windows itself.
```
TODO: SSH not yet working, laptop cannot see Pi, brainstorm with AI and fix
From this step onwards you can use another device to SSH into the Pi.
6. Configuring the case fan to run quietly and only when a certain temperature is reached is recommended to avoid it running the loud fan all the time. See the [Raspberry Pi 4 Case Fan product page](https://www.raspberrypi.com/products/raspberry-pi-4-case-fan/) for instructions on how to set this up. Follow these steps:
```bash
# Open the Pi configuration tool:
sudo raspi-config
# Under "Performance Options" → "Fan", you can set the fan to turn on at a specific temperature (e.g., 60°C) and adjust the fan speed. This will help keep the Pi cool while minimizing noise.
# After configuring, reboot the Pi to apply changes:
sudo reboot

# Some useful commands:
echo "$(($(cat /sys/class/thermal/thermal_zone0/temp)/1000))°C" # Check the current CPU temperature in Celsius.
vcgencmd measure_temp # Check the current CPU temperature using the vcgencmd command (alternative method to above).
```
7. TODO: Config with Ansible: TODO: from this point you need to configure the rest with Ansible.
    - Set a static IP on `eth1` (LAN side).
    - Enable IP forwarding.
    - Install and configure `dnsmasq` to serve DHCP on the lab network.
    - Configure NAT with `iptables` so lab devices can reach the internet through `eth0`.
    - Verify connectivity from a lab device and from the Pi itself.
8. If you want to shut the Raspberry Pi down, use the following command to safely power it off:
```bash
sudo shutdown -h now
# Then after a few seconds when the lights on the Pi stop blinking, you can safely unplug the power supply.

# Power on again by plugging the power supply back in. The Pi will boot automatically.
```


TODO: I want to do this via Ansible, use Ansible to configure all of this and add code in this repo!
TODO: for now use the Pi OS with Ansible and make it in a role called `router` that configures the Pi as a router with DHCP, NAT, and firewall rules, etc. 
TODO: add detailed comments everywhere in the Ansible code what everything does, why it is needed, etc., so I can understand it well and always go back to it later and easily read it, etc.

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
#### Pi Connectivity
From the Pi:
> **NOTE:** The commands contain extensive comments explaining the output and what to look for. This is important for understanding the network setup and troubleshooting!
```bash
# ========================== General connectivity checks ==========================
# -------- nmcli connection show: list all network connections managed by NetworkManager --------
# General format of each row:
#   NAME                UUID                                  TYPE      DEVICE
#
#   NAME   : human-readable connection profile name (can be anything; set when the connection was created)
#   UUID   : unique identifier for the connection profile (used internally by NetworkManager)
#   TYPE   : connection type (ethernet, wifi, loopback, bridge, etc.)
#   DEVICE : the network interface this connection is currently active on (blank = not connected)
#
# What to look for: eth0 and eth1 should both appear with a DEVICE assigned,
# confirming NetworkManager has active connections on both interfaces.
nmcli connection show
# Example output and explanation:
NAME                UUID                                  TYPE      DEVICE
# "Wired connection 1" = auto-created profile for the first Ethernet interface.
# TYPE=ethernet, DEVICE=eth0 → active on the WAN interface (connected to ISP modem).
Wired connection 1  f4de99e2-ffb3-3c23-9bce-7003ba21786a  ethernet  eth0
# "lo" = the loopback connection profile. TYPE=loopback, DEVICE=lo → always present, always active.
lo                  57b46a79-d752-41c4-bac9-0cd0e0a5591c  loopback  lo
# If a connection has no DEVICE shown, it means the profile exists but is not currently active.
# TODO: the eth1 line needs to be added here later 

# -------- ip a: show all network interfaces and their IP addresses --------
# General format of each interface block:
#   <index>: <name>: <flags> mtu <mtu> ...
#       link/<type> <mac-address> brd <broadcast-mac>
#       inet <ipv4-address>/<prefix> brd <broadcast-ip> scope <scope> ...
#       inet6 <ipv6-address>/<prefix> scope <scope> ...
#
#   <index>     : sequential number assigned by the kernel (1, 2, 3, ...)
#   <name>      : interface name (lo = loopback, eth0 = first Ethernet, eth1 = second, wlan0 = WiFi)
#                   lo (loopback) : a virtual interface the OS uses to communicate with itself — packets sent here never leave the machine. Always present, always 127.0.0.1 (localhost). Not a real network card.
#   <flags>     : comma-separated state flags in angle brackets:
#                   UP           = interface is administratively enabled
#                   LOWER_UP     = physical link is up (cable connected / signal present)
#                   NO-CARRIER   = no physical link (cable unplugged)
#                   BROADCAST    = supports broadcast (normal for Ethernet)
#                   MULTICAST    = supports multicast
#                   LOOPBACK     = loopback interface (lo only)
#   mtu         : Maximum Transmission Unit — largest packet size in bytes (1500 = standard Ethernet)
#   link/       : Layer 2 info — MAC address and broadcast MAC (ff:ff:ff:ff:ff:ff = send to everyone on the LAN)
#   inet        : IPv4 address with CIDR prefix length (e.g. /24 = 255.255.255.0)
#   brd         : IPv4 broadcast address for the subnet
#   scope       : where the address is reachable: "global" = routable on a network, "host" = local only, "link" = same link only
#   valid_lft   : how long the address lease is valid ("forever" = static/permanent, seconds = DHCP lease remaining time)
#   preferred_lft: how long the address is preferred for new connections (can expire before valid_lft for DHCP graceful renewal)
#   inet6       : IPv6 address — "fe80::" addresses are link-local (not routable, used for neighbour discovery on the same link)
ip a
# Example output and explanation:
poetoec@raspberrypi:~ $ ip a
# Interface 1: lo (loopback) — see above explanation comment for what this interface is.
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo        # 127.0.0.1 = localhost; /8 means the entire 127.x.x.x range is local
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host noprefixroute # IPv6 loopback address (equivalent of 127.0.0.1)
       valid_lft forever preferred_lft forever
# Interface 2: eth0 (WAN — built-in Ethernet, connected to ISP modem)
# UP + LOWER_UP = enabled and cable is physically connected.
# Got IP 192.168.2.59 from the ISP modem's DHCP server (home network subnet 192.168.2.0/24).
# valid_lft 86165sec = DHCP lease expires in ~24h; preferred_lft 86165sec = same.
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 88:a2:9e:98:97:1e brd ff:ff:ff:ff:ff:ff  # Pi's MAC address on eth0
    inet 192.168.2.59/24 brd 192.168.2.255 scope global dynamic noprefixroute eth0
       valid_lft 86165sec preferred_lft 86165sec          # DHCP lease — not static
    inet6 fe80::1d9f:d306:dbe6:f1db/64 scope link noprefixroute  # link-local IPv6, auto-generated from MAC
       valid_lft forever preferred_lft forever
# Interface 3: eth1 (LAN — USB-to-Ethernet adapter, connected to lab switch)
# UP + LOWER_UP = enabled and cable is physically connected.
# Has static IP 10.42.0.1/20 — this is the gateway address for the entire lab network.
# valid_lft forever = static address (not from DHCP).
# brd 10.42.15.255 = broadcast address for 10.42.0.0/20 (covers 10.42.0.0–10.42.15.255).
3: eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether aa:bb:cc:dd:ee:ff brd ff:ff:ff:ff:ff:ff  # USB adapter's MAC address
    inet 10.42.0.1/20 brd 10.42.15.255 scope global eth1
       valid_lft forever preferred_lft forever            # Static — no DHCP lease
    inet6 fe80::a8bb:ccff:fedd:eeff/64 scope link noprefixroute
       valid_lft forever preferred_lft forever
# Interface 4: wlan0 (built-in WiFi — not used, no cable/signal)
# NO-CARRIER = no WiFi signal associated. state DOWN = not active.
# No inet line = no IP address assigned (not connected to any network).
4: wlan0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc pfifo_fast state DOWN group default qlen 1000
    link/ether 88:a2:9e:98:97:1f brd ff:ff:ff:ff:ff:ff
# TODO: the eth1 line was pasted by copilot, check what the actual output is later and update above

# -------- ip r: show the routing table (how the Pi decides where to send packets) --------
# General format of each route:
#   <destination> via <gateway> dev <interface> proto <source> [scope <scope>] src <preferred-src> metric <metric>
#
#   <destination> : the target network or "default" (= 0.0.0.0/0, matches everything not matched by a more specific route)
#   via <gateway> : next-hop IP to forward packets to (only present when the destination is not directly connected)
#   dev <iface>   : which network interface to send out of
#   proto         : who installed this route:
#                     kernel = auto-created by the kernel when you assign an IP to an interface
#                     dhcp   = created by the DHCP client (received from DHCP server)
#                     static = manually configured
#   scope link    : destination is directly reachable on the link (no gateway needed; same subnet)
#   src           : preferred source IP to use when sending packets on this route
#   metric        : route priority — lower number wins if multiple routes match the same destination
ip r
# Example output and explanation:
poetoec@raspberrypi:~ $ ip r
# Route 1: default route (for all traffic not matched by a more specific route)
# "default" = 0.0.0.0/0 — catch-all. Any packet going to the internet or an unknown destination hits this.
# "via 192.168.2.254" = send to the ISP modem (gateway) first; it will forward it onward.
# "dev eth0" = send it out the WAN interface.
# "proto dhcp" = this route was learned from the DHCP server (ISP modem told us to use 192.168.2.254 as gateway).
# "src 192.168.2.59" = use this IP as the source address when sending packets via this route.
# "metric 100" = priority (lower wins; if there were another default route with metric 50, that would be preferred).
default via 192.168.2.254 dev eth0 proto dhcp src 192.168.2.59 metric 100
# Route 2: home network subnet (directly connected via eth0)
# "192.168.2.0/24" = packets destined for anything in 192.168.2.x go directly out eth0 — no gateway needed.
# "proto kernel" = the kernel created this route automatically when eth0 got its IP (192.168.2.59).
# "scope link" = the destination is on the same physical link (no routing needed, just ARP + send).
# "src 192.168.2.59" = use this as the source IP for packets sent to the home network.
# No "via" = no gateway; send directly (the host is on the same subnet).
192.168.2.0/24 dev eth0 proto kernel scope link src 192.168.2.59 metric 100
# Route 3: lab network subnet (directly connected via eth1)
# "10.42.0.0/20" = packets for any lab device (10.42.0.x–10.42.15.x) go out eth1 — no gateway needed.
# "proto kernel" = auto-created when eth1 was assigned 10.42.0.1/20.
# "scope link" = directly reachable on eth1.
# "src 10.42.0.1" = use the Pi's LAN IP as the source when sending packets to lab devices.
10.42.0.0/20 dev eth1 proto kernel scope link src 10.42.0.1 metric 100
# TODO: the last line was pasted by copilot, check what the actual output is later and update above

# -------- Check Connectivity --------
ping -c 3 192.168.2.1       # Test ISP modem reachability
ping -c 3 8.8.8.8           # Test internet from Pi

# ========================== More advanced checks ==========================

# -------- ip neigh: show the neighbour/ARP table (Layer 2 — who is on the same link) --------
# ARP (Address Resolution Protocol) maps IP addresses to MAC addresses on the same subnet.
# When the Pi wants to send a packet to an IP on the same link, it first needs the MAC address.
# It sends an ARP request ("who has 192.168.2.254?"), the target replies with its MAC, and the Pi caches it here.
#
# General format of each entry:
#   <ip-address> dev <interface> lladdr <mac-address> <state>
#
#   <ip-address> : the neighbour's IP address
#   dev          : which interface the neighbour was seen on
#   lladdr       : Link Layer address = MAC address of that device
#   <state>      : freshness of the ARP entry:
#                    REACHABLE = recently confirmed reachable (within the reachability timeout, typically ~30s)
#                    STALE     = entry exists but hasn't been confirmed recently; will be re-probed on next use
#                    DELAY     = waiting to confirm reachability after a packet was sent
#                    FAILED    = ARP probe sent but no reply received — device is unreachable or gone
#                    PERMANENT = statically configured, never expires

ip neigh
# Example output and explanation:
# The ISP modem (192.168.2.254) is reachable on eth0 — its MAC address was resolved via ARP.
# REACHABLE = recently confirmed; the Pi successfully received an ARP reply from this device.
192.168.2.254 dev eth0 lladdr a4:91:b1:xx:xx:xx REACHABLE
# A lab device (10.42.0.100) received an IP from the Pi's DHCP server and is reachable on eth1.
10.42.0.100 dev eth1 lladdr b8:27:eb:xx:xx:xx REACHABLE
# If you see FAILED instead of REACHABLE, the Pi sent an ARP request but got no reply —
# the device is either off, not connected, or there is a cabling/VLAN issue.

# -------- arp -n: show the ARP table (older tool, similar to ip neigh) --------
# arp -n shows the same IP-to-MAC mappings but in the older arp(8) format.
# "-n" = numeric output (do not resolve IPs to hostnames, faster and unambiguous).
#
# General format of each entry:
#   <ip-address>   <hw-type>   <mac-address>   <flags>   <interface>
#
#   <ip-address>  : neighbour's IP
#   <hw-type>     : hardware type (ether = Ethernet)
#   <mac-address> : neighbour's MAC address
#   <flags>       : C = complete (MAC resolved), M = permanent/static, P = published
#   <interface>   : which interface the neighbour is reachable on

arp -n
# Example output and explanation:
Address         HWtype  HWaddress           Flags Iface
# ISP modem reachable on WAN interface (eth0). Flags=C means ARP is complete (MAC resolved successfully).
192.168.2.254   ether   a4:91:b1:xx:xx:xx   C     eth0
# Lab device reachable on LAN interface (eth1). Got its IP from the Pi's dnsmasq DHCP server.
10.42.0.100     ether   b8:27:eb:xx:xx:xx   C     eth1
```
#### Lab Device Connectivity
From a lab device:
> **Note:** See the extensive comments in the Pi connectivity section above for explanations of the commands and their output.
```bash
ip a                        # Should show 10.42.0.x
ip r                        # Should show default via 10.42.0.1
ping -c 3 10.42.0.1         # Test gateway (Pi) reachability
ping -c 3 8.8.8.8           # Test internet connectivity
ping -c 3 google.com        # Test DNS resolution
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
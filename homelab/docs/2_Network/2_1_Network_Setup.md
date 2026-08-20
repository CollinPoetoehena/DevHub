# Network Setup

A stable network is the foundation of a reliable homelab. This document covers the setup options available, why a dedicated lab router behind the ISP modem is the right choice, and the specific steps to set it up using a Raspberry Pi as the lab router.

> See [Network Background & Commands](./2_1_Network_Background_Commands.md) for background knowledge on networking concepts, commands, and troubleshooting tips.

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

**Why `10.42.0.0/20` and not `10.0.0.0/20`?** The `10.0.0.0/x` range is extremely common — corporate VPNs, Docker defaults, Kubernetes pod CIDRs, and cloud VPCs all frequently use `10.0.x.x`. If any of these overlap with the lab subnet, routes conflict and traffic breaks. `10.42.0.0/20` is an uncommon slice of the `10.0.0.0/8` private range, so it is unlikely to collide with anything. The `42` is arbitrary — just picked to stay out of the way.

**Why `/20` and not `/24` or `/16`?** A `/24` gives only 254 usable addresses — that is enough for a flat network, but too small once you start carving out VLANs (each VLAN gets its own `/24` subnet within the parent range). A `/20` gives 4094 addresses and fits 16 × `/24` subnets comfortably — plenty of room for management, monitoring, Kubernetes, and future VLANs without ever running out. A `/16` (65k addresses) would also work but is far more than needed for a home lab.

---

## Why a Dedicated Router Behind the ISP Modem

**Full isolation (maintaining home network is not in my homelab's scope):** The lab runs on its own subnet with its own DHCP and firewall. Lab mistakes — DHCP conflicts, Proxmox bridge issues, Kubernetes networking — are contained within the lab network and never reach home devices. Avoid changing the ISP Modem's core configuration when others in the house depend on it for internet access. Changing the home network configuration can break connectivity for everyone, so it’s best to leave it as-is and put your own router behind it for the lab. Furthermore, the ISP modem may have limited or no VLAN support, making it unsuitable for isolating your lab network. Finally, it is not in my homelab's scope to maintain the home network, so I want to keep it untouched and let the ISP modem handle the home network while I experiment freely in my lab network.

**Keeps the ISP modem intact:** Other people in the house depend on the ISP modem for WiFi and internet. Replacing it or changing its configuration would mean taking ownership of the entire home network. Keeping it untouched means home connectivity stays stable regardless of what happens in the lab. See [Goals](../1_Goals_Hardware_LocalEnvSetup.md#goals), in short: I am NOT planning to self-host everything and make the home network dependent on my lab!

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

### Background Knowledge: Raspberry Pi, Hardware & OS

> See [Raspberry Pi: Hardware & OS Background](../reference/raspberry_pi_hardware_os.md) for detailed background on the Raspberry Pi hardware, ARM vs x86 architecture, SD cards, the operating system and kernel, the boot process, flashing, network interfaces, GPIO, `raspi-config`, and headless operation.

### Prerequisites

- **Raspberry Pi 4 or later** — the compute unit running the router software.
- **SD card with Raspberry Pi OS Lite (64-bit) flashed** — primary storage. Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) — a free tool from the Raspberry Pi Foundation. Download and install it on your laptop, select the OS image and your SD card as the target, and click Write. It downloads the image, writes it, and verifies it. Then insert the SD card into the Pi and it boots from it automatically.
    - **No SD card reader on your laptop?** Most laptops do not have a built-in SD card reader (and even those that do often only accept full-size SD, not microSD). Use a USB SD card reader/adapter — a small dongle that accepts a microSD card and plugs into a USB port. I bought the "ISY ICR-120 USB 2.0-kaartlezer USB 2.0" for 6.99 EUR at MediaMarkt (ISY is MediaMarkt's store brand, it is a reputable and affordable brand). Plug it into your laptop, insert the microSD card, and it appears as a removable drive that Raspberry Pi Imager can write to.
    - **Why Raspberry Pi OS Lite (and not Ubuntu Server or others)?** Raspberry Pi OS is the officially supported OS for the Pi, maintained by the Raspberry Pi Foundation. It is based on Debian, well-tested on Pi hardware, and includes Pi-specific optimisations and drivers out of the box (e.g. the `r8152` USB-Ethernet driver, GPU memory split, hardware interfaces). "Lite" means no desktop environment — just a minimal command-line system, which is exactly what you want for a headless appliance like a router. Ubuntu Server also works on the Pi, but it requires more manual configuration for Pi-specific hardware, has a larger footprint, and offers no real advantage for this use case. Stick with Raspberry Pi OS Lite.
    - > **Note — OS alternatives:** You could run OpenWRT or pfSense on the Pi instead. Both are purpose-built router/firewall OSes with polished web UIs and pre-configured networking stacks. However, the goal of my homelab ([see personal goal](../1_Goals_Hardware_LocalEnvSetup.md)) is to learn Linux networking by doing it yourself — configuring IP forwarding, DHCP, NAT, and firewall rules manually gives you a much deeper understanding than clicking through a GUI. You can always switch to OpenWRT or pfSense later once you understand what they are doing under the hood.
- **USB-to-Ethernet adapter (`eth1`)** — adds the LAN interface. I bought the "TP-LINK UE306" for 12.99 EUR at MediaMarkt because "TP-LINK" is a reliable brand and affordable (do not buy the "TP-LINK UE300C" — it is USB-C, which the Pi 4 does not have). Plug into a USB-A port; Raspberry Pi OS includes the `r8152` driver by default, so it is detected automatically as `eth1`.
- **Managed switch** — expands LAN ports and enables VLANs. I bought the "NETGEAR GS305E" for 24.99 EUR at MediaMarkt because "NETGEAR" is a reputable brand and affordable (the "TP-LINK TL-SG105E" is a good alternative). See [User Manual](https://www.netgear.com/support/product/gs305e)
- **Ethernet cables** (Cat6 or better for gigabit speeds):
    - **Long Ethernet cable for WAN (ISP modem → lab router)** 1 cable (10 m (ensures it can reach the router, such as if it needs to go through the wall or a conduit to a different floor (e.g. your work room), etc.)). I bought the "ISY IPC-6100-1-GB Netwerkkabel 10 m Wit" at MediaMarkt for 18.99 EUR because "ISY" (MediaMarkt's own store brand) is a reputable brand and affordable.
    - **Lab router → lab switch:** 1 cable (0.75 m). I bought the "ISY IPC-1012 CAT6A U/UTP Slim Netwerkkabel 0,75 m Wit" at MediaMarkt for 9.99 EUR (same reasoning for this brand as above).
    - **Lab switch → lab devices:** 1 cable per device (same model as above).
- **Access to the ISP modem admin page** — to reserve a static IP for the Pi's `eth0` by MAC address and check for IP conflicts. Typically at `192.168.2.1` or `192.168.1.1`.

### Full Setup Steps

> **Important security note:** The IPs named here are all local network addresses, they are not reachable from the internet. Make sure to avoid listing any public IPs in the documentation (e.g. `curl ifconfig.me` returns your public IP) because this is sensitive information that can be used to attack your network. Only use local IPs (e.g., `192.168.x.x`, `10.x.x.x`, `172.16.x.x`) in documentation!
>
> **Extra caution with IPv6:** Unlike IPv4 (where devices use private addresses like `192.168.x.x` behind NAT and are not directly reachable from the internet), IPv6 gives every device a **globally unique, internet-routable public address**. This means IPv6 addresses are *far more sensitive* than IPv4 private addresses — leaking an IPv6 address in documentation, a screenshot, or a log file exposes the real, directly reachable address of that device. An attacker with your device's IPv6 address can attempt to connect to it directly (if your firewall allows it or is misconfigured). Commands like `ip -6 addr show scope global`, `curl -6 ifconfig.me`, or even `ip a` (which shows `inet6` lines with global-scope addresses) can reveal public IPv6 addresses — never include their output in documentation or public repositories. Furthermore, if privacy extensions are not enabled, the IPv6 address embeds the device's MAC address (via EUI-64), which is a permanent hardware identifier that can be used to track the device across networks. See [Network Background & Commands — IP Addresses](../reference/Network_Background_Commands.md#ip-addresses--ipv4-and-ipv6) for full details on how IPv6 addressing works and why NAT does not protect IPv6 devices.

#### Step 1: Reserve a Static IP for the Pi on the ISP Modem

Log in to the ISP modem admin page (typically `192.168.2.1`) and reserve a static DHCP lease for the Pi's WAN interface using its MAC address (`eth0`). This ensures the Pi always receives the same upstream IP.

#### Step 2: Configure the Pi as a Router

##### 1. Assemble the Raspberry Pi

Fit it in a case, and connect any accessories. See the [official product page](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/), [getting started guide](https://www.raspberrypi.com/documentation/computers/getting-started.html). See the steps below for how to configure the Pi and setup SSH, etc. Possible accessories (including link to set them up/configure them):
- [case](https://www.raspberrypi.com/products/raspberry-pi-4-case/)
- [power supply](https://www.raspberrypi.com/products/power-supply/)
- [Raspberry Pi SD Card](https://www.raspberrypi.com/products/sd-cards/)
- [case fan (including heat sink)](https://www.raspberrypi.com/products/raspberry-pi-4-case-fan/) (this link shows how you can set up the fan and assemble it in the case).
- USB-to-Ethernet adapter: Plug it into a USB 3.0 port on the Pi. Verify with `ip link` after booting.

##### 2. Insert the SD card and connect cables

Insert the SD card (already containing flashed OS, [see prerequisites](#prerequisites-including-background-knowledge-for-the-setup)), connect `eth0` to the ISP modem LAN port and `eth1` to the lab switch.

##### 3. First boot and initial configuration

Boot the Pi and perform the first setup configuration. For the first boot, connect a monitor (HDMI), keyboard, and mouse (USB) to complete the initial setup. In the next step we enable SSH — after that, all subsequent access is via SSH and the Pi runs headless (no monitor, keyboard, or mouse needed). Some important first startup settings in the Raspberry Pi OS configuration tool (`raspi-config`):

```bash
# Ensure the Pi is up-to-date:
sudo apt update && sudo apt full-upgrade -y
sudo apt install vim # My favorite text editor, but you can use nano or any other editor you prefer.
sudo reboot

# Open the Raspberry Pi OS configuration tool:
sudo raspi-config
# The following settings are recommended to configure on first boot:
#
# -- Localisation Options ----------------------------------------------------
# → "Locale"
#   Select your locale (e.g., "en_GB.UTF-8 UTF-8" for British English, or
#   "en_US.UTF-8 UTF-8" for American English). This controls the language,
#   character encoding, and formatting (dates, numbers, currency) system-wide.
#   Without the correct locale set, some tools emit "locale" warnings/errors.
#   I chose "en_US.UTF-8 UTF-8" because American is the default locale for so many tools and applications.
#
# → "Timezone"
#   Set your timezone (e.g., "Europe/Amsterdam"). This ensures system clocks,
#   log timestamps, and cron jobs use the correct local time. Raspberry Pi OS
#   Lite defaults to "Europe/London" (UTC in winter, BST in summer).
#
# → "Keyboard"  (navigate to "Layout")
#   Select the correct keyboard layout (e.g., "Generic 105-key PC (intl.)"
#   for a standard international keyboard) → Other → English (US) → Default options for the rest. 
#   Without this, special characters map to wrong keys — for example, \ types as # on a UK layout.
#
# → "WLAN Country"
#   Set your country (e.g., "NL" for the Netherlands). This is required for
#   the built-in WiFi to comply with local radio regulations (allowed channels
#   and power levels). Even if you are not using WiFi, setting this avoids a
#   warning in raspi-config and ensures the radio is not left unconfigured.
#
# -- System Options -----------------------------------------------------------
# → "Hostname"
#   Change the hostname from the default "raspberrypi" to something meaningful
#   (e.g., "lab-router"). The hostname identifies the device on the network
#   and appears in SSH prompts and log messages.
#
# -- Performance Options ------------------------------------------------------
# → "Fan"
#   Set the fan to turn on only at a specific temperature (e.g., 60°C) rather
#   than running at full speed all the time. See the
#   https://www.raspberrypi.com/products/raspberry-pi-4-case-fan/ for
#   assembly and configuration instructions.
#   Without this, the fan runs continuously at full speed — noticeably loud.
#
# After making all changes, select "Finish" and reboot to apply them:
sudo reboot
# Verify the locale is set correctly:
localectl status
# Check the current CPU temperature to confirm thermal monitoring works:
echo "$(($(cat /sys/class/thermal/thermal_zone0/temp)/1000))°C"
vcgencmd measure_temp  # Alternative method
```

##### 4. Enable SSH

Enable SSH manually via terminal (required before you can access it from another device!). SSH (Secure Shell) lets you remotely control the Pi from your laptop over the network — no monitor or keyboard needed. Once enabled, all subsequent management is done via SSH.

```bash
# ========================== Enable SSH: ==========================
# Check if SSH is already enabled:
sudo systemctl status ssh
# If you see "Active: active (running)", SSH is already enabled.

# If not, enable and start it:
sudo systemctl enable ssh
sudo systemctl start ssh
sudo systemctl status ssh   # Verify: should show "Active: active (running)"

# Confirm SSH is listening on port 22 (sudo ensures the process list is complete):
sudo ss -tulpn | grep ssh
# Should show: LISTEN 0 128 0.0.0.0:22

# ========================== Find the Pi's IP address and hostname: ==========================
# Find the Pi's IP address from the Pi itself:
hostname -I
# Example output: 192.168.2.123
# Or from the network interfaces on the Pi itself (assuming eth0 is the interface connected to the home network):
ip a show eth0 | grep 'inet '
# Example output: inet 192.168.2.123/24 brd 192.168.2.255 scope global dynamic noprefixroute eth0
# Or from another device on the same network (e.g., your laptop) one of these commands
ip neigh # New version
arp -a # Old version
# NOTE: This outputs all devices on the same subnet that your laptop can see. Look for the Pi's MAC address (printed on the Pi board) to find its IP address.

# Or use the hostname command to get the Pi's hostname:
hostname
# Example output: lab-router (if changed; default is raspberrypi)

# ========================== Connect from another device (e.g. your laptop): ==========================
# Optionally check if the Pi is reachable from your laptop:
ping <pi-ip>
ping <pi-hostname>.local
# If not reachable, make sure the Pi is connected to the ISP modem and that your laptop is on the same network (e.g., connected to the same WiFi or LAN (e.g. if the ISP modem has IP 192.168.2.1, your laptop and the Pi should have an IP in the same subnet: 192.168.2.x)).

# Connect from your laptop:
ssh <username>@<pi-ip>
# Example: ssh pi@192.168.2.123
# Use the username you set during Raspberry Pi OS setup (default is "pi").
# On first connect you'll be asked to confirm the host fingerprint — type "yes".
# NOTE: This should work from WSL as well, even with a VPN (unless you have a full VPN), check reachability via ping with IP (hostname usually does not work from WSL!)!

# Alternatively, connect by hostname (no need to look up the IP):
ssh <username>@lab-router.local
```

**TODO: This is done for now as a manual step, integarte this in Ansible later to automate this and provide a public key and only add the step of generating the key and saving it from below, etc.!**

##### 5. Set up SSH key-based authentication and disable password login

Password login is convenient initially but is weaker than key-based auth — a key cannot be brute-forced over the network. Once a key is in place, disable passwords so only key holders can log in.

> **Prerequisite:** You must have already generated your SSH key pair (`~/.ssh/id_homelab`). See [Local Environment Setup — Step 1](../0_Local_Environment_Setup.md#step-1-generate-an-ssh-key-pair) if you haven't done this yet.

```bash
# ========================== Copy your public key to the Pi ==========================
# ssh-copy-id is the simplest method — it appends your public key to ~/.ssh/authorized_keys on the Pi:
ssh-copy-id -i ~/.ssh/id_homelab.pub <username>@<pi-ip>
# Example: ssh-copy-id pi@192.168.2.123
# You will be prompted for the Pi user's password one last time.

# If ssh-copy-id is not available (e.g. on Windows without Git Bash), do it manually:
cat ~/.ssh/id_homelab.pub | ssh <username>@<pi-ip> "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"

# ========================== Verify key login works BEFORE disabling passwords ==========================
# Open a NEW terminal and test key login (do NOT close the current session yet!):
ssh <username>@<pi-ip> -i ~/.ssh/id_homelab
# If you log in without being asked for a password (or only asked for your key passphrase), key auth works.
# Only proceed to disable passwords once this succeeds.

# ========================== On the Pi: disable password authentication ==========================
# Edit the SSH daemon configuration:
sudo su # Need to become root to edit the config file
vim /etc/ssh/sshd_config

# Find and set (or add) these lines (excluding the explanations!):
#   PasswordAuthentication no
#     → Disables password-based login entirely. Only SSH keys can authenticate.
#       Without this, attackers can still brute-force passwords over the network.
#   ChallengeResponseAuthentication no
#     → Disables challenge-response mechanisms (e.g. one-time passwords, keyboard-interactive prompts).
#       If left enabled, PAM or other modules can still prompt for a password even when
#       PasswordAuthentication is off, bypassing your key-only policy.
#   UsePAM yes
#     → Keep PAM enabled (this is the Debian default). Do NOT set this to "no".
#       On Debian-based systems (including Raspberry Pi OS), OpenSSH 10.x rejects
#       pubkey login for accounts without a password (locked accounts like ansibleremote)
#       when PAM is disabled. With UsePAM yes + PasswordAuthentication no, PAM does NOT
#       allow password login — it only handles account validation and session setup,
#       which correctly permits key-based auth for locked service accounts.
# Save and exit (Esc, :wq, Enter in vim).

# Apply the new config by restarting SSH:
sudo systemctl restart ssh

# ========================== Verify from your laptop ==========================
# From a new terminal, confirm key login still works:
ssh <username>@<pi-ip> -i ~/.ssh/id_homelab
# Should log in using your key without prompting for a password.

# Confirm password login is rejected (optional — use a different user or try explicitly):
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no <username>@<pi-ip>
# Should print: "Permission denied (publickey)." — password login is disabled.
```

From this step onwards you can use another device to SSH into the Pi.

##### 6. Ensure eth1 has carrier (cable connected to an active device)

Ensure `eth1` has a cable connected to an active device (the switch in this case!) before running the router playbook. NetworkManager only assigns the static IP (`10.42.0.1/20`) to `eth1` when the interface has **carrier** (link detected). Without carrier, the IP is never assigned, dnsmasq cannot bind to it, and the router does not function.

**Why carrier is required:** Ethernet link detection is a physical-layer handshake — both ends of the cable must be connected to active Ethernet ports that exchange electrical link pulses (auto-negotiation). If the other end is disconnected, unpowered, or missing, the Pi's Ethernet PHY reports `NO-CARRIER` and NetworkManager treats the interface as inactive (no IP assignment).

**In the real setup this is not a problem:** The Pi's `eth1` connects to the managed switch. A switch port is always electrically active — it provides carrier immediately, even if no other devices are plugged into the switch yet. So once the Pi is cabled to the switch, `eth1` gets carrier → NM assigns the IP → dnsmasq binds → everything works, regardless of whether any lab devices are connected.

**During testing with a direct laptop connection:** If you connect `eth1` directly to a laptop (no switch), the laptop's Ethernet port must be active (powered on, interface up) for carrier to be detected. A powered-off laptop or disconnected cable means no carrier → no IP → no DHCP/DNS.

```bash
# Verify carrier status on the Pi:
cat /sys/class/net/eth1/carrier
# 1 = cable connected to active device (carrier detected)
# 0 or "No such file" = no carrier (cable missing or other end inactive)

# Or check via ip command:
ip link show eth1
# Look for: state UP + LOWER_UP = carrier present
#           state DOWN or NO-CARRIER = no active link

# Once carrier is detected, verify NM assigned the IP:
ip -4 addr show eth1
# Should show: inet 10.42.0.1/20
```

##### 7. Configure the Pi with Ansible

```bash
# Go to the Ansible directory and activate Python venv (see 0_Local_Environment_Setup.md for details!):
cd homelab/ansible
source venv/bin/activate

# Load the SSH key into the agent so Ansible can use it without prompting for the passphrase.
# Without this, Ansible fails with "Permission denied (publickey)" because it cannot
# interactively prompt for the key's passphrase like a manual ssh command can.
eval $(ssh-agent) && ssh-add ~/.ssh/id_homelab
# Enter your passphrase once — it stays cached for this shell session.

# ========================== Bootstrap the ansibleremote user ==========================
# Run the users play to create the ansibleremote service account on the Pi.
# --diff: show file changes made on the remote host
# -u <username>: connect as the initial OS user (the one you created during Pi setup)
# -K: prompt for the sudo password (needed because <username> requires a password for sudo)
ansible-playbook site.yml -i hosts -l lab-router --tags users --diff -u <username> -K
# Check users with a few of the commands provided by the users role: see ./roles/devhub.users/tasks/main.yml
# Furthermore, you can check logs on the Pi if you have authentication problems:
sudo journalctl | grep -i "sshd" | tail -30

# After the initial setup (ansibleremote added), you need to run without -K on the router (ansibleremote has passwordless sudo):
ansible-playbook site.yml -i hosts -l lab-router --tags users --diff -u ansibleremote

# ========================== Verify connectivity with ansibleremote ==========================
# Test that Ansible can reach the Pi using the newly created ansibleremote user:
ansible all -i hosts -m ping -l lab-router -u ansibleremote

# ========================== Configure the Pi as a router ==========================
# First do a dry run (-C) to preview changes without applying them:
# --diff: shows the exact file content changes (like a git diff)
# -C (--check): dry run — shows what WOULD change without actually changing anything
ansible-playbook site.yml -i hosts -l lab-router --tags router --diff -C

# If the dry run looks good, apply the changes (remove -C):
ansible-playbook site.yml -i hosts -l lab-router --tags router --diff

# ========================== Verify router configuration ==========================
# Check the router configuration on the Pi (uses tag "verify" from the roles/router), run with -vvv to check the actual results and commands that ran on the Pi:
ansible-playbook site.yml -i hosts -l lab-router --tags verify -vvv

# ---------- Some helpful manual verification steps: ----------
# Check that the DHCP server is running
systemctl status dnsmasq.service
# List all listening ports and their associated processes (should show dnsmasq listening)
# t = TCP; u = UDP; l = listening sockets only; p = show process; n = numeric addresses/ports (don't resolve names)
sudo ss -tulpn
journalctl -xeu dnsmasq.service # TODO: what does htis do and also the options!

# If there are problems and you need to re-apply the router playbook, you may need to stop the process manually on the Pi:
sudo kill 992
sudo systemctl restart dnsmasq
```

##### 8. Configure the Managed Switch

The switch's web UI is on the lab network (`10.42.0.168`), which is not directly reachable from your home laptop (`192.168.2.x`). Use **SSH port forwarding** (SSH tunnel) through the Pi to access it.

**Why SSH port forwarding:** The whole point of the dedicated router is to keep the lab and home networks separated. Adding a route from your home laptop to `10.42.0.0/20` would punch a hole through that isolation. SSH port forwarding keeps the networks fully separated — your home laptop connects to the Pi (which is reachable on the home network at `192.168.2.59`), and the Pi forwards the traffic to the switch on the lab side. The tunnel is temporary (exists only while the SSH session is open) and requires no firewall or routing changes on either network.

```
Traffic flow:

Home Laptop browser → localhost:8080
    │
    │  SSH tunnel (encrypted, over home network)
    ▼
Pi (192.168.2.59) — decrypts and forwards →
    │
    │  (over lab network)
    ▼
Switch web UI (10.42.0.168:80)
```

**Alternatives (and why SSH forwarding is preferred):**
- **Add a route on the home laptop** (`sudo ip route add 10.42.0.0/20 via 192.168.2.59`): works, but breaks the network isolation that the dedicated router is designed to provide. Home devices should not have routes into the lab network.
- **Connect the laptop directly to the switch**: works for initial setup, but requires physically moving the Ethernet cable and getting a lab IP via DHCP, losing access to the home network.

```bash
# ========================== Find the switch's IP address ==========================
# SSH into the Pi and check the ARP/neighbour table to find the switch:
ip neigh
# Should show something like: 10.42.0.168 dev eth1 lladdr 28:94:01:8a:ec:28 STALE
# Or use:
arp -a
# Could show: ? (10.42.0.168) at 28:94:01:8a:ec:28 [ether] on eth1

# ========================== Access the switch web UI via SSH tunnel ==========================
# From your home laptop, open an SSH tunnel that forwards local port 8080
# to the switch's web UI (port 80) through the Pi:
#   -L 8080:10.42.0.168:80  = "listen on localhost:8080 on my laptop, and
#      forward connections through the Pi to 10.42.0.168:80"
ssh -L 8080:10.42.0.168:80 <username>@192.168.2.59 -i ~/.ssh/id_homelab

# While the SSH session is open, open a browser on your home laptop and go to:
#   http://localhost:8080
# You should see the NETGEAR switch management interface.
# When you close the SSH session, the tunnel closes and the port is released.

# NOTE: This same technique works for any web UI on the lab network. For example,
# to access the Proxmox web UI (port 8006) later:
#   ssh -L 8006:10.42.10.10:8006 <username>@192.168.2.59 -i ~/.ssh/id_homelab
#   Then browse to: https://localhost:8006
```

##### 9. Shutting down the Pi

If you want to shut the Raspberry Pi down, use the following command to safely power it off:

```bash
sudo shutdown -h now
# Then after a few seconds when the lights on the Pi stop blinking, you can safely unplug the power supply.

# Power on again by plugging the power supply back in. The Pi will boot automatically.
```

#### Step 3: Connect Lab Devices

Connect all lab devices to the Pi's LAN side (`eth1`) through a switch attached to `eth1`. Devices will receive IPs in `10.42.0.0/20` from the Pi's DHCP server and route internet traffic through the Pi Router.

#### Step 4: Verify

See [Network Background & Commands — Network Verification](2_1_Network_Background_Commands.md#commands-network-verification) for detailed explanations of each command and its output used below. The following commands are used for verification, specifying only the expected outputs, the commands themselves are explained in the document above.

#### Pi Connectivity

From the Pi:

```bash
nmcli connection show   # eth0, eth1, and lo should each show a DEVICE assigned
ip a                    # eth0: 192.168.2.x/24 (DHCP from ISP modem); eth1: 10.42.0.1/20 (static)
ip r                    # default via 192.168.2.254 dev eth0; 10.42.0.0/20 dev eth1
ping -c 3 192.168.2.1   # Test ISP modem reachability
ping -c 3 8.8.8.8       # Test internet from Pi
ip neigh                # 192.168.2.254 on eth0 REACHABLE; lab devices on eth1 REACHABLE
arp -n                  # Same information as ip neigh, in older format
```

#### Lab Device Connectivity

From a lab device:

```bash
ip a                    # Should show an IP in 10.42.0.x
ip r                    # Should show: default via 10.42.0.1
ping -c 3 10.42.0.1     # Test gateway (Pi) reachability
ping -c 3 8.8.8.8       # Test internet connectivity
ping -c 3 google.com    # Test DNS resolution
```

---

## Setup: TODO: other network setup
TODO: here add things like VLANs on the managed switch, and any other networking setup that may be required outside of the lab router, etc.

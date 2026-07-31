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

### Background Knowledge: Raspberry Pi, Hardware & OS

> See [Raspberry Pi: Hardware & OS Background](../reference/raspberry_pi_hardware_os.md) for detailed background on the Raspberry Pi hardware, ARM vs x86 architecture, SD cards, the operating system and kernel, the boot process, flashing, network interfaces, GPIO, `raspi-config`, and headless operation.

### Prerequisites

- **Raspberry Pi 4 or later** — the compute unit running the router software.
- **SD card with Raspberry Pi OS Lite (64-bit) flashed** — primary storage. Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) — a free tool from the Raspberry Pi Foundation. Download and install it on your laptop, select the OS image and your SD card as the target, and click Write. It downloads the image, writes it, and verifies it. Then insert the SD card into the Pi and it boots from it automatically.
    - **No SD card reader on your laptop?** Most laptops do not have a built-in SD card reader (and even those that do often only accept full-size SD, not microSD). Use a USB SD card reader/adapter — a small dongle that accepts a microSD card and plugs into a USB port. I bought the "ISY ICR-120 USB 2.0-kaartlezer USB 2.0" for 6.99 EUR at MediaMarkt (ISY is MediaMarkt's store brand, it is a reputable and affordable brand). Plug it into your laptop, insert the microSD card, and it appears as a removable drive that Raspberry Pi Imager can write to.
    - **Why Raspberry Pi OS Lite (and not Ubuntu Server or others)?** Raspberry Pi OS is the officially supported OS for the Pi, maintained by the Raspberry Pi Foundation. It is based on Debian, well-tested on Pi hardware, and includes Pi-specific optimisations and drivers out of the box (e.g. the `r8152` USB-Ethernet driver, GPU memory split, hardware interfaces). "Lite" means no desktop environment — just a minimal command-line system, which is exactly what you want for a headless appliance like a router. Ubuntu Server also works on the Pi, but it requires more manual configuration for Pi-specific hardware, has a larger footprint, and offers no real advantage for this use case. Stick with Raspberry Pi OS Lite.
    - > **Note — OS alternatives:** You could run OpenWRT or pfSense on the Pi instead. Both are purpose-built router/firewall OSes with polished web UIs and pre-configured networking stacks. However, the goal of my homelab ([see personal goal](../1_Goals_Hardware.md)) is to learn Linux networking by doing it yourself — configuring IP forwarding, DHCP, NAT, and firewall rules manually gives you a much deeper understanding than clicking through a GUI. You can always switch to OpenWRT or pfSense later once you understand what they are doing under the hood.
- **USB-to-Ethernet adapter (`eth1`)** — adds the LAN interface. I bought the "TP-LINK UE306" for 12.99 EUR at MediaMarkt because "TP-LINK" is a reliable brand and affordable (do not buy the "TP-LINK UE300C" — it is USB-C, which the Pi 4 does not have). Plug into a USB-A port; Raspberry Pi OS includes the `r8152` driver by default, so it is detected automatically as `eth1`.
- **Managed switch** — expands LAN ports and enables VLANs. I bought the "NETGEAR GS305E" for 24.99 EUR at MediaMarkt because "NETGEAR" is a reputable brand and affordable (the "TP-LINK TL-SG105E" is a good alternative).
- **Ethernet cables** (Cat6 or better for gigabit speeds):
    - **Long Ethernet cable for WAN (ISP modem → lab router)** 1 cable (10 m (ensures it can reach the router, such as if it needs to go through the wall or a conduit to a different floor (e.g. your work room), etc.)). I bought the "ISY IPC-6100-1-GB Netwerkkabel 10 m Wit" at MediaMarkt for 18.99 EUR because "ISY" (MediaMarkt's own store brand) is a reputable brand and affordable.
    - **Lab router → lab switch:** 1 cable (0.75 m). I bought the "ISY IPC-1012 CAT6A U/UTP Slim Netwerkkabel 0,75 m Wit" at MediaMarkt for 9.99 EUR (same reasoning for this brand as above).
    - **Lab switch → lab devices:** 1 cable per device (same model as above).
- **Access to the ISP modem admin page** — to reserve a static IP for the Pi's `eth0` by MAC address and check for IP conflicts. Typically at `192.168.2.1` or `192.168.1.1`.

### Full Setup Steps
#### Step 1: Reserve a Static IP for the Pi on the ISP Modem

Log in to the ISP modem admin page (typically `192.168.2.1`) and reserve a static DHCP lease for the Pi's WAN interface using its MAC address (`eth0`). This ensures the Pi always receives the same upstream IP.

#### Step 2: Configure the Pi as a Router
1. Assemble the Raspberry Pi: fit it in a case, and connect any accessories. See the [official product page](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/), [getting started guide](https://www.raspberrypi.com/documentation/computers/getting-started.html). See the steps below for how to configure the Pi and setup SSH, etc. Possible accessories (including link to set them up/configure them):
    - [case](https://www.raspberrypi.com/products/raspberry-pi-4-case/)
    - [power supply](https://www.raspberrypi.com/products/power-supply/)
    - [Raspberry Pi SD Card](https://www.raspberrypi.com/products/sd-cards/)
    - [case fan (including heat sink)](https://www.raspberrypi.com/products/raspberry-pi-4-case-fan/) (this link shows how you can set up the fan and assemble it in the case).
    - USB-to-Ethernet adapter: Plug it into a USB 3.0 port on the Pi. Verify with `ip link` after booting.
2. Insert the SD card (already containing flashed OS, [see prerequisites](#prerequisites-including-background-knowledge-for-the-setup)), connect `eth0` to the ISP modem LAN port and `eth1` to the lab switch.
3. Boot the Pi and perform the first setup configuration. For the first boot, connect a monitor (HDMI), keyboard, and mouse (USB) to complete the initial setup. In the next step we enable SSH — after that, all subsequent access is via SSH and the Pi runs headless (no monitor, keyboard, or mouse needed). Some important first startup settings in the Raspberry Pi OS configuration tool (`raspi-config`):
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
4. Enable SSH manually via terminal (required before you can access it from another device!): SSH (Secure Shell) lets you remotely control the Pi from your laptop over the network — no monitor or keyboard needed. Once enabled, all subsequent management is done via SSH.
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
5. Set up SSH key-based authentication and disable password login for security purposes (even though it is your homelab, you should still make it secure!). Password login is convenient initially but is weaker than key-based auth — a key cannot be brute-forced over the network. Once a key is in place, disable passwords so only key holders can log in.
```bash
# ========================== On your LAPTOP: generate an SSH key pair ==========================
# Generate a new Ed25519 key (modern, compact, fast; recommended over RSA):
ssh-keygen -t ed25519 -C "your-email@example.com"
# Save with appropriate name (e.g., ~/.ssh/id_homelab, NOTE: you cannot fill in "~", so use type out your full home path, such as /home/pi).
# Enter a passphrase (strongly recommended — protects the key if your laptop is stolen).
# This creates two files:
#   ~/.ssh/id_homelab       — private key (never share this)
#   ~/.ssh/id_homelab.pub   — public key  (safe to share; goes on the Pi)
# Make sure to save these files and the passphrase securely (e.g., in a password manager like KeePassXC). If you lose the private key, you cannot log in to the Pi.

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
#   UsePAM no
#     → Disables PAM (Pluggable Authentication Modules) for SSH sessions.
#       PAM can re-enable password prompts or other auth methods behind the scenes.
#       Setting this to "no" ensures SSH relies solely on its own key-based auth,
#       with no PAM module overriding your configuration.
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
6. TODO: Config with Ansible: 
```bash
# ========================== Run Ansible playbook to configure the Pi as a router ==========================
cd homelab/ansible
# Test connectivity from your local laptop:
ansible all -i hosts -m ping -l lab-router -u <username>
# Run the playbook to configure the Pi as a router:
TODO: check and diff first
TODO: for below command what to add, such as the flags I use at my work as well, etc.
TODO: add explanation for what each flag does
ansible-playbook site.yml -i hosts -l lab-router --diff -u <username> -C
```
7. If you want to shut the Raspberry Pi down, use the following command to safely power it off:
```bash
sudo shutdown -h now
# Then after a few seconds when the lights on the Pi stop blinking, you can safely unplug the power supply.

# Power on again by plugging the power supply back in. The Pi will boot automatically.
```


TODO: I want to do this via Ansible, use Ansible to configure all of this and add code in this repo!
TODO: for now use the Pi OS with Ansible and make it in a role called `router` that configures the Pi as a router with DHCP, NAT, and firewall rules, etc. 
TODO: add detailed comments everywhere in the Ansible code what everything does, why it is needed, etc., so I can understand it well and always go back to it later and easily read it, etc.

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

TODO: Block lab → home:
```bash
sudo iptables -A FORWARD -i eth1 -o eth0 -m state --state NEW -j ACCEPT
sudo iptables -A FORWARD -i eth0 -o eth1 -j DROP
```
This allows lab → internet but blocks home → lab.

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

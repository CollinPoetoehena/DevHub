# Setup & Installation: Network

This document covers the specific steps to set up the homelab network using the setup explained in [Network Design](TODO.md).

> **Prerequisites:** See [Network Design — Hardware & Software](TODO.md#hardware--software) for all required hardware (Pi, SD card, USB-Ethernet adapter, switch, cables) and software choices before starting.
>
> See [Network Design](TODO.md) for the network architecture, design decisions, and target topology.
> See the [Network Reference](../../../reference/network/README.md) for background knowledge on networking concepts, commands, and troubleshooting tips.
> **If you need to shutdown the Pi, such as when you are not using it anymore, etc., use:** `sudo shutdown -h now` — wait for the lights to stop blinking, then unplug the power supply. Power on again by plugging it back in.

## Table of Contents

- [Step 1: Reserve a Static IP for the Pi on the ISP Modem](#step-1-reserve-a-static-ip-for-the-pi-on-the-isp-modem)
- [Step 2: Assemble and Boot the Pi & Prepare the Pi for Headless Operation](#step-2-assemble-and-boot-the-pi--prepare-the-pi-for-headless-operation)
- [Step 3: Security & Hardening](#step-3-security--hardening)
- [Step 4: Configure the Pi with Ansible](#step-4-configure-the-pi-with-ansible)
- [Step 5: Configure Switch & Ensure eth1 of the Router Has Carrier](#step-5-configure-switch--ensure-eth1-of-the-router-has-carrier)

> **Important security note:** The IPs named here are all local network addresses, they are not reachable from the internet. Make sure to avoid listing any public IPs in the documentation (e.g. `curl ifconfig.me` returns your public IP) because this is sensitive information that can be used to attack your network. Only use local IPs (e.g., `192.168.x.x`, `10.x.x.x`, `172.16.x.x`) in documentation!
>
> **Extra caution with IPv6:** Unlike IPv4 (where devices use private addresses like `192.168.x.x` behind NAT and are not directly reachable from the internet), IPv6 gives every device a **globally unique, internet-routable public address**. This means IPv6 addresses are *far more sensitive* than IPv4 private addresses — leaking an IPv6 address in documentation, a screenshot, or a log file exposes the real, directly reachable address of that device. An attacker with your device's IPv6 address can attempt to connect to it directly (if your firewall allows it or is misconfigured). Commands like `ip -6 addr show scope global`, `curl -6 ifconfig.me`, or even `ip a` (which shows `inet6` lines with global-scope addresses) can reveal public IPv6 addresses — never include their output in documentation or public repositories. Furthermore, if privacy extensions are not enabled, the IPv6 address embeds the device's MAC address (via EUI-64), which is a permanent hardware identifier that can be used to track the device across networks. See [Subnets & IP Addresses — IPv6](../../../reference/network/Subnets_and_IP_Addresses.md#ipv6) for full details on how IPv6 addressing works and why NAT does not protect IPv6 devices.

---

## Step 1: Reserve a Static IP for the Pi on the ISP Modem

Log in to the ISP modem admin page (typically `192.168.2.1`) and reserve a static DHCP lease for the Pi's WAN interface using its MAC address (`eth0`). This ensures the Pi always receives the same upstream IP.

---

## Step 2: Assemble and Boot the Pi & Prepare the Pi for Headless Operation

> **Goal: Prepare the Pi for headless operation, this is the only manual setup required:** These are the only manual steps for the Pi, these are all the steps you need to perform before it can run headless. This ensures that once the initial setup is complete, you can manage and operate the Pi entirely via SSH without needing direct physical access.

### Step 2.1: Fit the Pi in a Case and Connect Accessories
1. Fit the Pi in a case and connect any accessories. See the [official product page](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/), [getting started guide](https://www.raspberrypi.com/documentation/computers/getting-started.html). Possible accessories (including link to set them up/configure them):
- [case](https://www.raspberrypi.com/products/raspberry-pi-4-case/)
- [power supply](https://www.raspberrypi.com/products/power-supply/)
- [Raspberry Pi SD Card](https://www.raspberrypi.com/products/sd-cards/)
- [case fan (including heat sink)](https://www.raspberrypi.com/products/raspberry-pi-4-case-fan/) (this link shows how you can set up the fan and assemble it in the case).
- USB-to-Ethernet adapter: Plug it into a USB 3.0 port on the Pi. Verify with `ip link` after booting.
2. Insert the SD card (already containing flashed OS, see [prerequisites](TODO.md#hardware--software)), connect `eth0` to the ISP modem LAN port and `eth1` to the lab switch. Power on the Pi.

### Step 2.2: Prepare the Pi for Headless Operation
1. Boot the Pi and perform the first setup configuration. For the first boot, connect a monitor (HDMI), keyboard, and mouse (USB) to complete the initial setup. Furthermore, we enable SSH — after that, all subsequent access is via SSH and the Pi runs headless (no monitor, keyboard, or mouse needed). Some important first startup settings in the Raspberry Pi OS configuration tool (`raspi-config`):
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
2. Enable SSH: Enable SSH manually via terminal (required before you can access it from another device!). SSH (Secure Shell) lets you remotely control the Pi from your laptop over the network — no monitor or keyboard needed. Once enabled, all subsequent management is done via SSH.

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

## Step 3: Security & Hardening

TODO: this is now about SSH manually, but this should be automated via Ansible in a role. 
TODO: I already have a role for configuring a jumphost, so use that since it already contains the SSH hardening part, etc.: https://github.com/CollinPoetoehena/devhub-ansible-role-jumphost
TODO: check the role and make changes where needed!

TODO: this below can be removed, this will be in the jumphost role!
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

---

## Step 4: Configure the Pi with Ansible

```bash
# Go to the Ansible directory and activate Python venv (see 0_Local_Environment_Setup.md for details!):
cd homelab; source venv/bin/activate; cd ansible

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

# Show connections:
nmcli connection show
# Should show: lab-wan (eth0), lab-lan (eth1), vlan-management (eth1.10), vlan-services (eth1.20), vlan-iot (eth1.30)
ip -4 addr show eth1.10  # Should show: inet 10.42.10.1/24
ip -4 addr show eth1.20  # Should show: inet 10.42.20.1/24
ip -4 addr show eth1.30  # Should show: inet 10.42.30.1/24
```

TODO: refer here to the next step where also the firewall is set up, etc., which are the other steps for security, etc.

---

## Step 5: Configure Switch & Ensure eth1 of the Router Has Carrier

In this step we will configure the switch and ensure that the `eth1` interface of the router has carrier (i.e., is physically connected and active).

### Step 5.1: Configure the Managed Switch (via Laptop)
**Why not just give `eth1` an IP on VLAN 1 and configure the switch through the Pi?** An alternative would be to assign an IP to the Pi's physical `eth1` interface (on the native VLAN 1), connect the unconfigured switch, and configure it from there — the switch defaults to VLAN 1 for management, so it would be reachable. However, this is rejected because VLAN 1 is deliberately unused in this design: all production traffic must be explicitly VLAN-tagged. Adding an IP to `eth1` — even temporarily — breaks that principle and introduces the exact ambiguity the design avoids. See [Network Design — Why VLAN 1 is not used](TODO.md#why-vlan-1-native-is-not-used--all-traffic-is-explicitly-vlan-tagged) for the full rationale. Configuring the switch via a direct laptop connection is simpler and keeps the router configuration clean.

Additionally, because all production traffic is explicitly VLAN-tagged in this design, the switch must have VLANs 10, 20, and 30 created and its management moved to VLAN 10 before it can participate in the lab network. Without this, the switch only speaks on the native VLAN (VLAN 1), which carries no production traffic.

Unfortunately, the NETGEAR GS305E web UI is not scriptable (no CLI or API), so this must be done manually. This is fine since these are only a few steps and buying a switch with automation capabilities would be overkill and generally costs significantly more money.

The switch ships with DHCP enabled on VLAN 1 — **but it only receives a DHCP address if it is connected to a router or DHCP server via Ethernet**. However, a laptop connected over Wi‑Fi does *not* provide DHCP to the switch. Therefore, in a direct laptop‑to‑switch setup, the switch falls back to its default IP (typically **192.168.0.239** on NETGEAR Plus switches, check the switch’s manual for confirmation). The below approach works **without a router** and on **any laptop**, because you can temporarily assign your laptop’s Ethernet interface a static IP in the same subnet as the switch’s fallback IP. This creates a small, isolated two‑device network that allows you to reach the management UI and change the IP configuration of the switch:
#### Step 5.1.1: Direct Laptop-to-Switch Connection
1. Connect an Ethernet cable directly from your laptop to any port on the switch.
2. Assign a static IP to your laptop’s Ethernet interface in the same subnet as the switch’s fallback IP (e.g., `192.168.0.x`), see the switch’s manual for its static IP. To assign the static IP on your laptop:
    - **Windows:**
        1. Open Settings → Network & Internet → Ethernet → Click your Ethernet adapter → Scroll to IP assignment → Edit → Choose Manual → Enable IPv4
        2. Enter:
            - IP: 192.168.0.10
            - Subnet mask: 255.255.255.0
            - Gateway: (leave blank)
        3. Save
        4. Disable Wi‑Fi (important)
    - **Linux:**
        1. Open a terminal
        2. Assign a static IP to your Ethernet interface (replace `eth0` with your interface name if different) and bring the interface up: `sudo ip addr flush dev eth0; sudo ip addr add 192.168.0.10/24 dev eth0; sudo ip link set eth0 up`
        3. Disable Wi‑Fi (important)
3. Verify that your laptop can ping the switch’s IP (e.g., `ping 192.168.0.239`).
4. Open a web browser and navigate to the switch’s IP (e.g., `http://192.168.0.239`) to access the management UI.
5. Follow the next steps below, such as configuring the switch, etc. Any errors related to internet connectivity can be ignored at this stage, as the switch is not yet connected to the network.
#### Step 5.1.2: Configure the Switch
Perform all configuration in one session. See [Network Design — Subnet & VLAN Design](TODO.md#subnet--vlan-design) for the design rationale and [Switch Port Assignments](TODO.md#switch-port-assignments-netgear-gs305e--5-ports) for the port-to-VLAN mapping. **In the NETGEAR web UI:**
1. **Log in** — Default credentials: no username, password is `password` (unless specified otherwise by your switch, check the switch's manual)
2. **Change password** — Navigate to **System → Maintenance → Change Password** (or the switch may force you on first login). Set a strong, unique password and store it in your password manager
3. **Set switch name** — Navigate to **System → Maintenance → Switch Information** and set the Switch Name to `lab-switch`
4. **Create VLANs** — Navigate to **VLAN → 802.1Q (not Port-based!) → Advanced → VLAN Configuration**. Add VLAN 10 (name: `Management`), VLAN 20 (name: `Services`), VLAN 30 (name: `IoT`)
5. **Set VLAN membership** — For VLAN 10, VLAN 20, and VLAN 30, go to **VLAN Membership** and set:
    - Port 1 (router): **T** (tagged)
    - Port 2 (PVE1): **T** (tagged)
    - Port 3 (PVE2): **T** (tagged)
    - Ports 4–5: leave as not a member
6. **Verify VLAN 1** — All ports should remain **U** (untagged) for VLAN 1 (native VLAN — unused for production traffic, serves only as a fallback recovery path)
7. **Set PVID** — Set the **PVID** (Port VLAN ID) for all ports to 1 (typically the default — untagged frames arriving on any port are assigned to VLAN 1)
8. **Set Management VLAN (VERY IMPORTANT)** — Navigate to **System → Management → Management VLAN**, select VLAN 10. This moves the switch's management interface to the management VLAN. The switch will be assigned a static IP later based on its MAC address by the Pi router after [Step 4: Configure the Pi with Ansible](#step-4-configure-the-pi-with-ansible). If the switch is not in the Management VLAN, the router cannot assign it an IP, and you may lose access to the switch. That is why this step is critical.
    - **Alternative (the switch I bought (GS305E) did not have the above option)** — Some switches do not have the option to change the management interface VLAN. In that case, you need to manually update the switch's IP address to be within the management VLAN subnet: Navigate to **System → Maintenance → Switch Information → Disable DHCP** and set the IP address to an address within the management VLAN subnet (e.g., `10.42.10.2`), the corresponding subnet mask (e.g., `255.255.255.0`) and the gateway to the Pi router's IP (e.g. `10.42.10.1`).
        - **This behavior is perfectly fine on the GS305E** — The GS305E always uses **VLAN 1** internally for its management CPU, and this cannot be changed. This does *not* break the homelab design because VLAN 1 is intentionally left unused for production traffic and serves only as a fallback recovery path. The Pi router can still route traffic between VLAN 10 and VLAN 1, allowing the switch to have an IP inside the management subnet (`10.42.10.0/24`) even though its internal management plane lives on VLAN 1. This results in a clean and secure setup that matches enterprise practice for low‑end smart switches and integrates cleanly with the homelab network topology:
            - VLAN 10 remains the **true management VLAN** for all homelab devices (router, Proxmox, services).
            - VLAN 1 remains the **native fallback VLAN**, isolated and unused except for the switch’s management CPU.
            - No production device uses VLAN 1, so the switch’s management plane is isolated by design.
            - If VLAN tagging ever breaks, VLAN 1 still provides guaranteed access to the switch for recovery.
7. **Apply** — Click **Apply** to save
8. Once the switch is configured fully with all the steps explained in the other sections, revert your laptop’s Ethernet interface back to DHCP so your Wi‑Fi and normal networking continue to work as before:
    - **Windows:** Settings → Network & Internet → Ethernet → IP assignment → Edit → Automatic (DHCP). Then re-enable Wi‑Fi.
    - **Linux:** `sudo ip addr flush dev eth0; sudo dhclient eth0`

> **If you need to reconfigure later:** See [Step 7.4 — Recovery](#step-74-recovery--if-locked-out-of-the-switch) for how to regain access.

### Step 5.2: Connect Switch to Pi's LAN Interface to ensure carrier is detected
**Why connect the switch after the initial configuration?** The router's Ansible playbook creates VLAN sub-interfaces (`eth1.10`, `eth1.20`, `eth1.30`) and configures dnsmasq to serve DHCP per VLAN. For these to work, the switch must already have VLANs configured and be passing tagged frames. If you connect an unconfigured switch to the configured Pi router, the VLAN sub-interfaces come up but have no corresponding VLANs on the switch — tagged frames are dropped, dnsmasq cannot reach clients, and you cannot access the switch's web UI via the Pi (because the switch's management interface is on a VLAN the unconfigured switch does not understand). Configuring the switch first via a direct laptop connection avoids this chicken-and-egg problem entirely.

Connect the switch to the Pi's `eth1` (LAN) interface (you can disconnect it from your laptop, which was only necessary for the initial switch configuration). This provides carrier on `eth1`, which NetworkManager needs to bring up the VLAN sub-interfaces.

**Why carrier is required:** Ethernet link detection is a physical-layer handshake — both ends of the cable must be connected to active Ethernet ports that exchange electrical link pulses (auto-negotiation). If the other end is disconnected, unpowered, or missing, the Pi's Ethernet PHY reports `NO-CARRIER` and NetworkManager treats the interface as inactive (no IP assignment on sub-interfaces).

A switch port is always electrically active — it provides carrier immediately, even if no other devices are plugged into the switch yet. So once the Pi is cabled to the switch, `eth1` gets carrier → the router can use the VLAN sub-interfaces → dnsmasq binds → everything works.

```bash
# Verify carrier status on the Pi:
cat /sys/class/net/eth1/carrier
# 1 = cable connected to active device (carrier detected)
# 0 or "No such file" = no carrier (cable missing or other end inactive)

# Or check via ip command:
ip link show eth1
# Look for: state UP + LOWER_UP = carrier present
#           state DOWN or NO-CARRIER = no active link
```

### Step 5.3: Access Switch Management via SSH Tunnel & Perform Final Switch Configurations
Now that the router is configured and running, the final steps for the switch can be performed.
#### Step 5.3.1: **Verify the switch is reachable:**

```bash
# From the Pi, verify the static lease is in the dnsmasq config:
grep "lab-switch" /etc/dnsmasq.conf
# Should show: dhcp-host=<MAC address>,10.42.10.2,lab-switch

# If the switch hasn't picked up its IP yet, reboot it:
# Unplug the switch's power cable, wait ~5 seconds, plug it back in.
# On boot it sends a DHCP DISCOVER and gets the reserved IP.

# Verify from the Pi:
ping -c 3 10.42.10.2
```
#### Step 5.3.2: Access the switch web UI via SSH tunnel
The switch's web UI is on the lab management network (`10.42.10.2`, VLAN 10), which is not directly reachable from your home laptop. Use **SSH port forwarding** through the Pi to access it.

```
Traffic flow:

Home Laptop browser → localhost:8080
    │
    │  SSH tunnel (encrypted, over home network)
    ▼
Pi (192.168.2.59) — decrypts and forwards →
    │
    │  (over lab management VLAN 10)
    ▼
Switch web UI (10.42.10.2:80)
```

**Why SSH port forwarding:** The whole point of the dedicated router is to keep the lab and home networks separated. Adding a route from your home laptop to `10.42.0.0/20` would punch a hole through that isolation. SSH port forwarding keeps the networks fully separated — your home laptop connects to the Pi (which is reachable on the home network at your Pi's IP, such as `192.168.2.59`), and the Pi forwards the traffic to the switch on the lab side. The tunnel is temporary (exists only while the SSH session is open) and requires no firewall or routing changes on either network.

```bash
# From your home laptop, open an SSH tunnel:
#   -L 8080:10.42.10.2:80  = "listen on localhost:8080 on my laptop, and
#      forward connections through the Pi to 10.42.10.2:80"
ssh -L 8080:10.42.10.2:80 <username>@<Pi_IP> -i ~/.ssh/id_homelab

# Then open a browser: http://localhost:8080
# You should see the NETGEAR switch management interface.
# When you close the SSH session, the tunnel closes and the port is released.

# This same technique works for any web UI on the lab network. For example,
# to access the Proxmox web UI (port 8006) later:
#   ssh -L 8006:10.42.10.10:8006 <username>@<Pi_IP> -i ~/.ssh/id_homelab
#   Then browse to: https://localhost:8006
```
Use this access to verify the switch configuration, update settings, or download a backup of the configuration.
#### Step 5.3.3: Enable DHCP on the switch
In the switch's management interface, make sure the DHCP client is enabled so it can obtain the reserved IP (`10.42.10.2`) from the router's dnsmasq server.
Now that the router is configured and the switch is connected to the Pi, the switch should have received its static IP (`10.42.10.2`) on the management VLAN (VLAN 10) via DHCP from dnsmasq. The static lease is defined in [`group_vars/router/main.yml`](../../ansible/group_vars/router/main.yml) (the `router_static_leases` variable).
#### Step 5.3.4: Backup the switch configuration
Before disconnecting from the switch, back up its configuration:
1. Navigate to **System → Maintenance → Save Configuration → Save**
2. Save the configuration file in [homelab/files](../../files) with the name `lab-switch.cfg` for version control and future reference
3. If you ever need to restore the switch, upload this file via **System → Maintenance → Restore Configuration**
### Step 5.4: Recovery — if locked out of the switch
If you lose access to the switch (e.g. management VLAN misconfigured, SSH tunnel not working, switch not getting DHCP), you can always reconfigure it directly from your laptop:
1. **Factory reset the switch** — hold the reset button on the switch for 10 seconds. This restores the switch to factory defaults (management on VLAN 1, password `password`)
2. **Follow [Step 5.1](#step-51-direct-laptop-to-switch-connection)** to connect your laptop and find the switch's IP and reconfigure it (password, name, VLANs, management VLAN). 
3. Optionally, restore the configuration by the [backup file saved earlier](#step-533-backup-the-switch-configuration) (e.g., `lab-switch.cfg`) via **System → Maintenance → Restore Configuration**.

---
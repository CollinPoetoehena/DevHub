# Network Setup

This document covers the specific steps to set up the homelab network using the setup explained in [Network Design](2_1_Network_Design.md).

> **Prerequisites:** See [Network Design — Hardware & Software](2_1_Network_Design.md#hardware--software) for all required hardware (Pi, SD card, USB-Ethernet adapter, switch, cables) and software choices before starting.
>
> See [Network Design](2_1_Network_Design.md) for the network architecture, design decisions, and target topology.
> See the [Network Reference](../reference/network/README.md) for background knowledge on networking concepts, commands, and troubleshooting tips.
> **If you need to shutdown the Pi, such as when you are not using it anymore, etc., use:** `sudo shutdown -h now` — wait for the lights to stop blinking, then unplug the power supply. Power on again by plugging it back in.

## Table of Contents

- [Step 1: Reserve a Static IP for the Pi on the ISP Modem](#step-1-reserve-a-static-ip-for-the-pi-on-the-isp-modem)
- [Step 2: Assemble and Boot the Pi](#step-2-assemble-and-boot-the-pi)
- [Step 3: First Boot and Initial Configuration](#step-3-first-boot-and-initial-configuration)
- [Step 4: Enable SSH](#step-4-enable-ssh)
- [Step 5: Set Up SSH Key-Based Authentication](#step-5-set-up-ssh-key-based-authentication)
- [Step 6: Ensure eth1 Has Carrier](#step-6-ensure-eth1-has-carrier)
- [Step 7: Configure the Pi with Ansible](#step-7-configure-the-pi-with-ansible)
- [Step 8: Configure the Managed Switch](#step-8-configure-the-managed-switch)
- [Step 9: Connect Lab Devices](#step-9-connect-lab-devices)
- [Step 10: Verify](#step-10-verify)

> **Important security note:** The IPs named here are all local network addresses, they are not reachable from the internet. Make sure to avoid listing any public IPs in the documentation (e.g. `curl ifconfig.me` returns your public IP) because this is sensitive information that can be used to attack your network. Only use local IPs (e.g., `192.168.x.x`, `10.x.x.x`, `172.16.x.x`) in documentation!
>
> **Extra caution with IPv6:** Unlike IPv4 (where devices use private addresses like `192.168.x.x` behind NAT and are not directly reachable from the internet), IPv6 gives every device a **globally unique, internet-routable public address**. This means IPv6 addresses are *far more sensitive* than IPv4 private addresses — leaking an IPv6 address in documentation, a screenshot, or a log file exposes the real, directly reachable address of that device. An attacker with your device's IPv6 address can attempt to connect to it directly (if your firewall allows it or is misconfigured). Commands like `ip -6 addr show scope global`, `curl -6 ifconfig.me`, or even `ip a` (which shows `inet6` lines with global-scope addresses) can reveal public IPv6 addresses — never include their output in documentation or public repositories. Furthermore, if privacy extensions are not enabled, the IPv6 address embeds the device's MAC address (via EUI-64), which is a permanent hardware identifier that can be used to track the device across networks. See [Subnets & IP Addresses — IPv6](../reference/network/Subnets_and_IP_Addresses.md#ipv6) for full details on how IPv6 addressing works and why NAT does not protect IPv6 devices.

---

## Step 1: Reserve a Static IP for the Pi on the ISP Modem

Log in to the ISP modem admin page (typically `192.168.2.1`) and reserve a static DHCP lease for the Pi's WAN interface using its MAC address (`eth0`). This ensures the Pi always receives the same upstream IP.

---

## Step 2: Assemble and Boot the Pi

Fit the Pi in a case and connect any accessories. See the [official product page](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/), [getting started guide](https://www.raspberrypi.com/documentation/computers/getting-started.html). Possible accessories (including link to set them up/configure them):
- [case](https://www.raspberrypi.com/products/raspberry-pi-4-case/)
- [power supply](https://www.raspberrypi.com/products/power-supply/)
- [Raspberry Pi SD Card](https://www.raspberrypi.com/products/sd-cards/)
- [case fan (including heat sink)](https://www.raspberrypi.com/products/raspberry-pi-4-case-fan/) (this link shows how you can set up the fan and assemble it in the case).
- USB-to-Ethernet adapter: Plug it into a USB 3.0 port on the Pi. Verify with `ip link` after booting.

Insert the SD card (already containing flashed OS, see [prerequisites](2_1_Network_Design.md#hardware--software)), connect `eth0` to the ISP modem LAN port and `eth1` to the lab switch. Power on the Pi.

---

## Step 3: First Boot and Initial Configuration

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

---

## Step 4: Enable SSH

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

---

## Step 5: Set Up SSH Key-Based Authentication

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

## Step 6: Ensure eth1 Has Carrier

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

---

## Step 7: Configure the Pi with Ansible

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
```

---

## Step 8: Configure the Managed Switch
### Step 8.1: Assign a static IP to the switch
The switch should have a fixed IP so SSH tunnels, documentation, and firewall rules don't break when leases change. This is done via a DHCP static lease (reservation) in dnsmasq on the Pi — the switch still uses DHCP, but dnsmasq always hands out the same IP for its MAC address.

The static lease is defined in [`group_vars/router/main.yml`](../../ansible/group_vars/router/main.yml) (the `router_static_leases` variable) and deployed by the router playbook. The switch's MAC address is printed on the device itself.

```bash
# Re-run the router playbook to deploy the updated dnsmasq config with the static lease: See Step 7 above for details on running the playbook.

# Then on the Pi, verify the lease file shows the reservation:
grep "lab-switch" /etc/dnsmasq.conf
# Should show: dhcp-host=<MAC address>,10.42.0.2,lab-switch

# Force the switch to pick up its new IP:
# - reboot the switch: Unplug the switch's power cable, wait ~5 seconds, plug it back in. On boot it will send a new DHCP DISCOVER and get the reserved IP.
# - Or wait for the DHCP lease to expire and renew automatically.
# After that, verify from the Pi:
ping -c 3 10.42.0.2
```

### Step 8.2: Access the switch's web UI via SSH tunnel
Access the switch's web UI via SSH tunnel: The switch's web UI is on the lab network (`10.42.0.2`), which is not directly reachable from your home laptop because it is in the home network (e.g. `192.168.2.x`). Use **SSH port forwarding** (SSH tunnel) through the Pi to access it.
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
Switch web UI (10.42.0.2:80)
```
- **Why SSH port forwarding:** The whole point of the dedicated router is to keep the lab and home networks separated. Adding a route from your home laptop to `10.42.0.0/20` would punch a hole through that isolation. SSH port forwarding keeps the networks fully separated — your home laptop connects to the Pi (which is reachable on the home network at `192.168.2.59`), and the Pi forwards the traffic to the switch on the lab side. The tunnel is temporary (exists only while the SSH session is open) and requires no firewall or routing changes on either network.
- **Alternatives (and why SSH forwarding is preferred):**
    - **Add a route on the home laptop** (`sudo ip route add 10.42.0.0/20 via 192.168.2.59`): works, but breaks the network isolation that the dedicated router is designed to provide. Home devices should not have routes into the lab network.
    - **Connect the laptop directly to the switch**: works for initial setup, but requires physically moving the Ethernet cable and getting a lab IP via DHCP, losing access to the home network.

Follow these steps to set up the SSH tunnel and access the switch's web UI:
```bash 
# From your home laptop, open an SSH tunnel that forwards local port 8080
# to the switch's web UI (port 80) through the Pi:
#   -L 8080:10.42.0.2:80  = "listen on localhost:8080 on my laptop, and
#      forward connections through the Pi to 10.42.0.2:80"
ssh -L 8080:10.42.0.2:80 <username>@192.168.2.59 -i ~/.ssh/id_homelab

# While the SSH session is open, open a browser on your home laptop and go to:
#   http://localhost:8080
# You should see the NETGEAR switch management interface.
# When you close the SSH session, the tunnel closes and the port is released.

# NOTE: This same technique works for any web UI on the lab network. For example,
# to access the Proxmox web UI (port 8006) later:
#   ssh -L 8006:10.42.10.10:8006 <username>@192.168.2.59 -i ~/.ssh/id_homelab
#   Then browse to: https://localhost:8006
```

### Step 8.3: Change the default admin password
The NETGEAR GS305E ships with a well-known default password (`password`). Change it immediately to prevent unauthorized access from any device on the lab network.

1. Log in to the switch web UI (via the SSH tunnel from [Step 8.2](#step-82-access-the-switchs-web-ui-via-ssh-tunnel)): `http://localhost:8080`
2. Default credentials: no username, password is `password`
3. Navigate to **Maintenance → Change Password** (or the switch may force you to change it on first login)
4. Set a strong, unique password and store it in your password manager
### Step 8.4: Configure VLANs on the switch
VLANs segment the lab network into isolated broadcast domains — devices in different VLANs cannot communicate without going through the router (which can apply firewall rules). See [Network Design — Subnet & VLAN Design](2_1_Network_Design.md#subnet--vlan-design) for the full rationale (why management stays on the native VLAN) and [Switch Port Assignments](2_1_Network_Design.md#switch-port-assignments-netgear-gs305e--5-ports) for the port-to-VLAN mapping.

**Steps in the NETGEAR web UI:**

1. Navigate to **VLAN → 802.1Q (not Port-based!) → Advanced → VLAN Configuration**
2. Add VLAN 20 (name: `Monitoring`), VLAN 30 (name: `Workloads`)
3. For VLAN 20 and VLAN 30, go to **VLAN Membership** and set (see [Switch Port Assignments](2_1_Network_Design.md#switch-port-assignments-netgear-gs305e--5-ports) for what tagged/untagged means and why each VLAN uses that mode):
   - Port 1 (router): **T** (tagged)
   - Port 2 (PVE1): **T** (tagged)
   - Port 3 (PVE2): **T** (tagged)
   - Ports 4–5: leave as not a member
4. Verify VLAN 1 (default) membership — all ports should remain **U** (untagged) for VLAN 1 (this is the native/management VLAN that carries untagged traffic)
5. Set the **PVID** (Port VLAN ID) for all ports to 1 (this is typically the default — it means untagged frames arriving on any port are assigned to VLAN 1)
6. Click **Apply** to save the configuration

> **Note:** The NETGEAR GS305E saves configuration immediately when you click Apply — there is no separate "save to startup" step. However, verify after a power cycle that VLANs persist.

### Step 8.5: Configure VLAN sub-interfaces on the Pi router
After the switch is configured with VLANs, the Pi router needs VLAN sub-interfaces on `eth1` to route traffic between VLANs and serve DHCP/DNS per VLAN. Management traffic stays on the physical `eth1` interface (native/untagged) — only workload VLANs need sub-interfaces.

> **TODO:** This requires updates to the router Ansible role — adding VLAN sub-interfaces (`eth1.20`, `eth1.30`) via NetworkManager, per-VLAN DHCP ranges in dnsmasq, and inter-VLAN firewall rules. Implement this once the Proxmox hosts are ready to connect.

TODO: left off here, implement VLAN sub-interfaces in the router role and document the Ansible steps.

---

## Step 9: Connect Lab Devices

Connect all lab devices to the Pi's LAN side (`eth1`) through a switch attached to `eth1`. Devices will receive IPs in `10.42.0.0/20` from the Pi's DHCP server and route internet traffic through the Pi Router.

---

## Step 10: Verify

See [Network Commands](../reference/network/Network_Commands.md) for detailed explanations of each command and its output used below. The following commands are used for verification, specifying only the expected outputs, the commands themselves are explained in the document above.

### Pi Connectivity

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

### Lab Device Connectivity

From a lab device:

```bash
ip a                    # Should show an IP in 10.42.0.x
ip r                    # Should show: default via 10.42.0.1
ping -c 3 10.42.0.1     # Test gateway (Pi) reachability
ping -c 3 8.8.8.8       # Test internet connectivity
ping -c 3 google.com    # Test DNS resolution
```
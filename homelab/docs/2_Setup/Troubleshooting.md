# Troubleshooting

This document provides guidance for diagnosing and resolving common issues during setup, such as network issues.

---

## Some home network devices cannot connect to the internet

- **Symptoms:** Multiple devices (phone, TV, printer) lose internet while others work fine.
- **Cause:** Proxmox `vmbr0` bridge on the home LAN conflicts with the ISP modem's DHCP — causes duplicate IPs.
- **Diagnosis:** Check ISP modem admin page (`192.168.2.1`) → DHCP leases → look for duplicate IPs.
- **Fix:** Set up a dedicated lab router (Raspberry Pi) between the ISP modem and lab devices to isolate the lab subnet. See [Network Setup](./2_1_Network_Setup.md).
- **Interim workaround:** Shut down the Proxmox host until the lab router is ready.

---

## SSH key authentication fails for ansibleremote after user bootstrap

- **Symptoms:** After running the users bootstrap playbook, `ssh ansibleremote@<pi-ip>` fails:
    ```
    ansibleremote@192.168.2.59: Permission denied (publickey).
    ```
  But Ansible `ping` may still work (due to SSH connection multiplexing from the same session).

- **Diagnosis:** SSH into the Pi with a user that still works (e.g. the initial OS user) and check sshd logs:
    ```bash
    ssh <initial-user>@<pi-ip>
    sudo journalctl | grep -i "sshd" | tail -30
    ```
  If you see this line, the account is locked:
    ```
    sshd-session[1551]: User ansibleremote not allowed because account is locked
    ```

- **Cause:** The `ansibleremote` user was created without a password (correct for key-only auth), but `UsePAM no` in `/etc/ssh/sshd_config` makes OpenSSH 10.x reject pubkey login for locked accounts. Without PAM, sshd checks the password field in `/etc/shadow` directly — a `!` or `*` means locked, and the connection is refused before the key is even checked.

- **Fix:** Set `UsePAM yes` in sshd_config (the Debian default):
    ```bash
    sudo sed -i 's/^UsePAM no/UsePAM yes/' /etc/ssh/sshd_config
    sudo systemctl restart ssh
    ```
  With `UsePAM yes` + `PasswordAuthentication no`, PAM handles account validation and correctly allows key-based auth for locked accounts — password login remains disabled. See [step 5 in Network Setup](./2_1_Network_Setup.md) for the full sshd_config recommendations.

---

## Lab device has an IP but cannot reach the internet

- **Symptoms:** A device connected to the lab network (via the Pi router's `eth1`) receives a DHCP address (e.g. `10.42.0.160`) and can ping the Pi's LAN IP (e.g. `10.42.10.1`), but `ping 8.8.8.8` and `ping google.com` both fail. The Pi itself can reach the internet fine.

- **Diagnosis:** Check IPv4 forwarding on the Pi:
    ```bash
    cat /proc/sys/net/ipv4/ip_forward
    ```
  If it returns `0`, the kernel is not forwarding packets between interfaces — traffic from lab devices stops at the Pi and is never sent out to the internet via `eth0`.

- **Cause:** IPv4 forwarding is disabled. This can happen if:
  - The Ansible `sysctl` task wrote to `/etc/sysctl.conf` but a file in `/etc/sysctl.d/` overrides it with `0` (files in `/etc/sysctl.d/` are loaded after `/etc/sysctl.conf` and take priority).
  - The setting was never applied at runtime (only written to disk, requiring a reboot).

- **Fix:** Enable forwarding immediately and persist it:
    ```bash
    sudo sysctl -w net.ipv4.ip_forward=1        # Apply now
    cat /proc/sys/net/ipv4/ip_forward            # Verify: should show 1
    ```
  To persist across reboots, write to a high-priority sysctl file:
    ```bash
    echo 'net.ipv4.ip_forward = 1' | sudo tee /etc/sysctl.d/99-router-ip-forward.conf
    sudo sysctl -p /etc/sysctl.d/99-router-ip-forward.conf
    ```
  Then re-test from the lab device — `ping 8.8.8.8` and `ping google.com` should both work.
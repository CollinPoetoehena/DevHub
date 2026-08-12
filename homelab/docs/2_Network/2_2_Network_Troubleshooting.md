# Troubleshooting

This document provides guidance for diagnosing and resolving common network issues, particularly those that arise when running a homelab environment.

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
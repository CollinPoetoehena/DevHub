# Operating System (OS)

The software that manages the hardware and provides a foundation for running programs. Without an OS, the hardware (e.g. a Raspberry Pi) is just bare hardware with no way to interact with it. For a router, the OS runs the kernel that handles networking, the DHCP server, the firewall, etc.

## Kernel

The kernel is the core of the OS — it is the first software that runs after the bootloader and it remains running for the entire lifetime of the system. It manages:

- **Hardware abstraction:** Provides drivers so user-space programs can use hardware (network cards, USB devices, storage) through a uniform interface without knowing the hardware details.
- **Process management:** Schedules and isolates running programs (processes), allocating CPU time and memory to each.
- **Networking stack:** Implements TCP/IP, routing tables, packet filtering (iptables/nftables), and network interfaces. When you configure IP forwarding or NAT, you are configuring the kernel's networking subsystem.
- **Filesystem:** Manages reading and writing data to storage devices.

On the Pi, the kernel is Linux (specifically the Raspberry Pi Foundation's fork with Pi-specific patches and drivers). You can check the running kernel version:

```bash
uname -r
# Example output: 6.6.51+rpt-rpi-v8
```

---

## User Space vs Kernel Space

Programs run in one of two privilege levels:

- **Kernel space:** The kernel and its modules run with full hardware access. A bug here can crash the entire system.
- **User space:** Applications (your shell, dnsmasq, iptables commands, SSH server) run with restricted access. They interact with hardware only through system calls to the kernel. This isolation prevents a buggy application from taking down the whole system.

When you run `iptables -A FORWARD ...`, the `iptables` user-space tool sends instructions to the kernel's `netfilter` subsystem, which then enforces the rules at kernel level on every packet.

---

## What Does "64-bit" Mean?

It refers to the CPU's architecture instruction set — the width of the CPU's registers and memory addresses. Practically:

- **Memory:** A 32-bit OS can address at most 4 GB of RAM. A 64-bit OS can address vastly more (theoretically 16 exabytes, practically limited by the hardware). For example, the Raspberry Pi 4 comes in 2 GB, 4 GB, and 8 GB variants — the 4 GB and 8 GB models benefit from a 64-bit OS.
- **Software:** 64-bit binaries can use wider registers for arithmetic, which can improve performance for certain workloads. Increasingly, software is built and tested primarily for 64-bit, and some packages may drop 32-bit support.
- **Recommendation:** Always use the 64-bit version for your host.

---

## Init System (systemd)

Most modern Linux distributions (including Raspberry Pi OS) use **systemd** as the init system — the first process started by the kernel (PID 1). It manages:

- **Service lifecycle:** Starting, stopping, restarting, and monitoring services (e.g. `sshd`, `dnsmasq`, `iptables-persistent`).
- **Boot order:** Ensuring services start in the correct order (e.g. networking before DHCP server).
- **Logging:** Collecting logs from all services via `journald` (viewable with `journalctl`).

Common commands:

```bash
sudo systemctl status <service>     # Check if a service is running
sudo systemctl start <service>      # Start a service
sudo systemctl stop <service>       # Stop a service
sudo systemctl enable <service>     # Start automatically on boot
sudo systemctl disable <service>    # Do not start on boot
sudo systemctl restart <service>    # Stop and start again
sudo journalctl -u <service>        # View logs for a specific service
```

---
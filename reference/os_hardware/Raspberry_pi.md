# Raspberry Pi

Background reference for Raspberry Pi hardware concepts, operating system fundamentals, storage, boot process, and networking interfaces. This document is referenced from the [Homelab Network Design ](../homelab/docs/2_Network_Hosts/TODO.md) and other homelab documentation.

---

## What is a Raspberry Pi?

A small, low-cost single-board computer (SBC) that runs a full Linux OS. Unlike a traditional desktop or server — which has separate components (motherboard, CPU, RAM, storage, GPU, NIC) — the Pi integrates all of these onto a single printed circuit board (PCB) roughly the size of a credit card. It has USB ports, HDMI, GPIO pins, and built-in Ethernet.

### ARM vs x86 Architecture

The Pi uses an ARM architecture (64-bit ARMv8 / Cortex-A72 on the Pi 4), which differs from the x86-64 (also called AMD64) architecture used by most desktop PCs, laptops, and servers. This distinction matters in practice:

- **Software compatibility:** Pre-compiled binaries built for x86-64 will not run on ARM. When downloading software, look for `arm64` or `aarch64` builds. Package managers (`apt`) handle this automatically, but manual downloads (e.g. from GitHub releases) require selecting the correct architecture.
- **Docker images:** Many Docker images are published only for `amd64`. When running containers on the Pi, verify the image supports `arm64` or `linux/arm64`. Multi-arch images handle this transparently; single-arch images will fail with `exec format error`.
- **Compiling from source:** If a package does not offer ARM binaries, you can compile it on the Pi. Compilation is slower on the Pi's CPU compared to a desktop, but it produces a native ARM binary.
- **Performance profile:** ARM CPUs are designed for power efficiency rather than raw single-thread performance. The Pi 4's quad-core Cortex-A72 at 1.5 GHz is more than adequate for routing, DNS, DHCP, and light services, but it is not suitable for heavy compute workloads.

You can check the architecture of your running system:

```bash
uname -m
# Expected output on Pi 4 with 64-bit OS: aarch64

dpkg --print-architecture
# Expected output: arm64
```

### Power Consumption

The Pi draws very little power — typically 3–7 W under normal load (compared to 50–150 W for a small x86 server). This makes it well-suited for running 24/7 as a dedicated appliance such as a router, DNS server, or monitoring node, without a noticeable impact on your electricity bill.

### Why Use a Pi as a Router

- **Cost-effective:** The Pi 4 (around €50–70) plus a USB-to-Ethernet adapter (€10–15) is significantly cheaper than a dedicated router appliance or mini PC for small applications like a homelab router.
- **Educational:** Building and running your own router is a hands-on way to learn Linux networking, IP forwarding, DHCP, NAT, and firewalling — skills that directly transfer to professional infrastructure work.
- **Sufficient performance:** The Pi 4 and later models can comfortably handle routing, DHCP, NAT, DNS, and firewalling for a small homelab (dozens of devices, up to gigabit throughput on the Ethernet port).
- **Full control:** Running a general-purpose Linux OS (rather than a locked-down router firmware) gives you complete control over every aspect of the system — you can install any package, write custom scripts, and integrate with Ansible or other automation tools.

---

## SD Card

A small, removable flash storage card (Secure Digital). The Raspberry Pi has no built-in storage (no hard drive or SSD) — the SD card is its primary storage device. It holds the operating system, all configuration files, and any data the Pi writes. The Pi boots directly from it.

### SD Card Types and Sizes

- **microSD vs SD:** The Pi uses a microSD card slot. Full-size SD cards do not fit. Most microSD cards come with a full-size SD adapter for use in laptops, but the Pi itself takes only microSD.
- **Capacity:** 16 GB is the minimum for Raspberry Pi OS Lite. 32 GB is recommended — it provides ample room for the OS, packages, logs, and temporary files. Larger cards (64 GB+) are fine but unnecessary for a router.
- **Speed class:** Look for cards rated A1 or A2 (Application Performance Class) and U1/U3 (UHS Speed Class). These ensure acceptable random I/O performance, which matters more than sequential speed for an OS drive. Cheap, unbranded cards often have poor random read/write performance, leading to a sluggish system.

### SD Card Reliability

Flash memory has a limited number of write cycles. An SD card running as an OS drive receives constant writes (logs, temp files, journals). To extend card life:

- Minimise unnecessary logging (reduce log verbosity, use `logrotate`).
- Consider mounting `/tmp` and `/var/log` as `tmpfs` (in-memory filesystem) if the Pi has sufficient RAM.
- Use a quality brand (Raspberry Pi, SanDisk, Samsung, Kingston) — cheap cards fail more quickly and more often.
- Keep a backup of the SD card image so you can re-flash quickly if the card fails.

### SD Card Reader

Most laptops do not have a built-in SD card reader (and even those that do often only accept full-size SD, not microSD). Use a USB SD card reader/adapter — a small dongle that accepts a microSD card and plugs into a USB port. Once connected, the card appears as a removable drive that tools like Raspberry Pi Imager can write to.

---

## Flashing the OS onto the SD Card

"Flashing" means writing a disk image byte-for-byte onto storage media. The term comes from the underlying technology: SD cards use **flash memory** (non-volatile storage that retains data without power, using floating-gate transistors that trap electrical charge).

### Disk Images

A disk image (`.img` file) is a complete binary snapshot of an entire storage device — every byte, partition table, bootloader, and file — packaged into a single file. Writing it to the SD card produces a fully bootable system (a **boot device**); the Pi can boot directly from it without any installation wizard or setup steps.

The image typically contains:

- **Partition table:** Defines the layout of the card (usually two partitions: a small FAT32 boot partition and a larger ext4 root partition).
- **Bootloader:** The firmware that the Pi's SoC loads first, which then loads the kernel.
- **Root filesystem:** The full OS with all directories (`/bin`, `/etc`, `/usr`, `/home`, etc.) and pre-installed packages.

### Raspberry Pi Imager

[Raspberry Pi Imager](https://www.raspberrypi.com/software/) is a free tool from the Raspberry Pi Foundation. It runs on Windows, macOS, and Linux. The workflow:

1. Download and install Raspberry Pi Imager on your laptop.
2. Insert the microSD card (via a USB reader if needed).
3. Select the Pi model, the OS (Raspberry Pi OS Lite 64-bit), and the target SD card.
4. **Configure settings before writing** (click the gear icon or "Edit Settings"): set hostname, username/password, locale, and optionally enable SSH and configure WiFi. These settings are baked into the image so the Pi boots with them pre-configured — no need for a monitor on first boot if SSH is enabled here.
5. Click Write. The tool downloads the image, writes it to the card, and verifies the write.
6. Eject the card, insert it into the Pi, and power on.

### Verifying the Write

After flashing, Raspberry Pi Imager automatically verifies the write by reading back the data and comparing checksums. If verification fails, try a different SD card — the current one may be defective or counterfeit (fake cards are common and report larger capacities than they actually have).

---

## Boot Process

Understanding the Pi's boot sequence helps diagnose startup problems:

1. **SoC firmware (first stage):** The Pi's Broadcom SoC has a small bootloader burned into ROM. On power-on, it loads `bootcode.bin` from the SD card's boot partition.
2. **`bootcode.bin` (second stage):** Initialises the SDRAM and loads `start4.elf`.
3. **`start4.elf` (GPU firmware):** Reads `config.txt` (hardware configuration: memory split, overclocking, display settings) and `cmdline.txt` (kernel command-line parameters), then loads the Linux kernel into memory.
4. **Linux kernel:** Takes over from the GPU firmware. Initialises drivers, mounts the root filesystem (the ext4 partition), and starts the init system (`systemd`).
5. **systemd:** Starts all configured services in the correct order. Once networking and SSH are up, the Pi is ready for remote access.

If the Pi does not boot:

- **No green LED activity:** The SoC cannot read the SD card. Re-flash or try a different card.
- **Green LED blinks in a pattern:** The bootloader found the card but cannot load the kernel. Check that the image was written correctly.
- **Kernel panic (visible on HDMI):** The kernel started but failed to mount the root filesystem or encountered a critical error. Check the SD card integrity.

---

## Network Interfaces

> See [Network Devices & Interfaces — Network Interface](./network/Network_Devices.md#network-interface) for background on what a network interface is.

A router needs two separate network interfaces: one facing the upstream network (WAN) and one facing the lab devices (LAN). The Pi's built-in Ethernet port serves as the WAN side; a USB-to-Ethernet adapter adds the LAN side.

```text
ISP Modem LAN port → Pi eth0 (WAN side)
Pi eth1 (LAN side) → Lab switch or directly to lab devices
```

The Pi's `eth0` receives an IP from the ISP modem (e.g. `192.168.2.x`). The Pi's `eth1` is the gateway for the lab network (e.g. `10.42.10.1`).

### Built-in Ethernet (`eth0`)

The Pi 4 has a true Gigabit Ethernet port (the Pi 3 was limited to 100 Mbps because its Ethernet shared the USB 2.0 bus). It connects directly to the Broadcom SoC via a dedicated bus, providing full 1 Gbps throughput. This is used as the WAN interface — the uplink to the ISP modem.

### USB-to-Ethernet Adapter (`eth1`)

Since the Pi has only one built-in Ethernet port, a USB-to-Ethernet adapter provides the second interface for the LAN side. Key considerations:

- **USB 3.0 port:** Plug the adapter into one of the Pi's USB 3.0 ports (the blue ones) for maximum throughput. USB 2.0 ports cap out at ~300 Mbps in practice.
- **Chipset compatibility:** Common chipsets (`RTL8153`, `RTL8152`, `AX88179`) are supported out of the box by Raspberry Pi OS. The `r8152` kernel module handles Realtek-based adapters. Verify detection after plugging in:

```bash
# Check if the adapter is detected as a USB device:
lsusb
# Look for an entry like: Realtek Semiconductor Corp. RTL8153 Gigabit Ethernet Adapter

# Check if it appears as a network interface:
ip link
# Should show eth1 (or enx<mac> depending on naming policy)

# Check which kernel module (driver) is loaded for it:
ethtool -i eth1
# Should show: driver: r8152  (or ax88179_178a for AX88179 chipsets)
```

- **Naming:** By default, Raspberry Pi OS names the built-in port `eth0` and the USB adapter `eth1`. If you plug in multiple adapters or change USB ports, the naming may shift. For stable naming, you can create a udev rule based on MAC address, but for a single-adapter setup this is unnecessary.

### WiFi Interface (`wlan0`)

The Pi has a built-in WiFi interface (`wlan0`). While it could theoretically be used for the WAN side instead of `eth0`, this is **not recommended**:

- **Stability:** WiFi is inherently less stable than wired Ethernet — signal strength varies, interference from other devices and networks causes packet loss, and the connection can drop during high-traffic periods.
- **Throughput:** The Pi 4's WiFi is 802.11ac (WiFi 5) with a theoretical max of ~150 Mbps on a single stream — far below the 1 Gbps wired Ethernet provides.
- **Real-world experience:** In an earlier version I tested with WiFi as the WAN interface, which resulted in an unstable and very slow connection where you could basically do almost nothing (I could not even connect to the Pi via SSH, while all other devices like my laptop had perfectly fine WiFi connections). This was likely due to the Pi's internal WiFi antenna being weaker than laptop antennas, combined with the additional overhead of routing traffic through the same radio.

**Conclusion:** Use the built-in Ethernet port for the WAN side and a USB-to-Ethernet adapter for the LAN side. Do not use WiFi for the WAN side.

---

## GPIO (General-Purpose Input/Output)

The Pi has a 40-pin GPIO header — a row of small metal pins on the board that can be programmed to send or receive electrical signals. While not used for the router setup, it is worth knowing about:

- **What it is for:** Connecting sensors, LEDs, motors, relays, displays, and other electronic components directly to the Pi. Each pin can be configured as a digital input (read a signal) or output (send a signal).
- **Voltage:** GPIO pins operate at 3.3 V logic. Connecting 5 V signals directly to GPIO pins can permanently damage the Pi. Use a level shifter if interfacing with 5 V devices.
- **Homelab relevance:** You could connect a temperature sensor to monitor the Pi's environment, wire up status LEDs, or add a hardware power button. These are optional projects and not needed for the router.

---

## Raspberry Pi Configuration Tool (`raspi-config`)

Raspberry Pi OS includes `raspi-config`, an interactive terminal-based configuration tool for common system settings. Run it with:

```bash
sudo raspi-config
```

It provides menus for:

- **System Options:** Hostname, boot behaviour (console or desktop), auto-login, network at boot.
- **Interface Options:** Enable/disable SSH, SPI, I2C, serial, camera, VNC, and other hardware interfaces.
- **Performance Options:** Overclock settings, GPU memory split, fan control.
- **Localisation Options:** Locale, timezone, keyboard layout, WLAN country.
- **Advanced Options:** Expand filesystem (to use the full SD card), network interface names, boot order.

Settings changed through `raspi-config` are written to system configuration files (`/boot/firmware/config.txt`, `/etc/locale.gen`, `/etc/timezone`, etc.) and take effect after a reboot.

---

## Headless Operation

"Headless" means running the Pi without a monitor, keyboard, or mouse attached. After the initial setup (where you may need a display to configure SSH and network settings), all subsequent interaction is via SSH over the network. This is the normal operating mode for a server or appliance like a router.

**Advantages of headless operation:**
- No need to keep a monitor and keyboard plugged in — saves space, power, and cables.
- The Pi can be placed anywhere with Ethernet access (e.g. next to the ISP modem in a different room).
- All administration is done remotely via SSH, which is faster and more convenient for command-line work.

**Prerequisite:** SSH must be enabled and working before going headless. Always verify you can SSH in from another device before disconnecting the monitor.

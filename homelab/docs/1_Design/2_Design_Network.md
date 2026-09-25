# Network & Hosts Design

**TODO: this is now fully done and checked; only at the end of the homelab check one more time if this is still the final setup and update some things if needed; but the general things generally will remain as designed in this document!**

A stable network is the foundation of a reliable homelab. This document covers the design decisions: the setup options available, why a dedicated lab router behind the ISP modem is the right choice, the subnet design, and the target network topology. The lab network is **dual-stack (IPv4 + IPv6)**.

See the [Network Reference](../../../reference/network/README.md) for background knowledge on networking concepts, commands, and troubleshooting tips.

## Table of Contents
- [Network Setup Options](#network-setup-options)
  - [Option 1: Lab devices directly on the home network](#option-1-lab-devices-directly-on-the-home-network)
  - [Option 2: VLANs on the ISP modem](#option-2-vlans-on-the-isp-modem)
  - [Option 3: Dedicated router behind the ISP modem](#option-3-dedicated-router-behind-the-isp-modem)
  - [Chosen Option: Dedicated Router Behind the ISP Modem](#chosen-option-dedicated-router-behind-the-isp-modem)
- [Hardware & Software](#hardware--software)
  - [Background Knowledge: Raspberry Pi, Hardware & OS](#background-knowledge-raspberry-pi-hardware--os)
  - [Lab Router](#lab-router)
    - [Router Hardware](#router-hardware)
    - [Router OS: OpenWrt](#router-os-openwrt)
    - [Historical Note: Why Not a Custom Raspberry Pi OS + Ansible Router Anymore](#historical-note-why-not-a-custom-raspberry-pi-os--ansible-router-anymore)
    - [Routing Software Stack: OpenWrt (UCI + dnsmasq/odhcpd + firewall4/nftables)](#routing-software-stack-openwrt-uci--dnsmasqodhcpd--firewall4nftables)
    - [Automation & Documentation as Code on OpenWrt](#automation--documentation-as-code-on-openwrt)
  - [Managed Switch](#managed-switch)
  - [Ethernet Cables](#ethernet-cables)
- [Network Topology & Design](#network-topology--design)
  - [IPv6 Addressing (ULA + NAT66) on the Lab Network](#ipv6-addressing-ula--nat66-on-the-lab-network)
  - [Jumphost: Secure Access to Lab Network](#jumphost-secure-access-to-lab-network)
  - [Subnet & VLAN Design](#subnet--vlan-design)
    - [Why VLAN 1 (native) is not used — all traffic is explicitly VLAN-tagged](#why-vlan-1-native-is-not-used--all-traffic-is-explicitly-vlan-tagged)
    - [Why a dedicated Management VLAN (VLAN 10)](#why-a-dedicated-management-vlan-vlan-10)
    - [IoT Isolation](#iot-isolation)
    - [Switch Port Assignments](#switch-port-assignments)

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

### Option 3: Dedicated router behind the ISP modem

Place a dedicated lab router between the ISP modem and all lab devices. The lab runs on its own subnet, fully isolated from the home network, and is dual-stack (IPv4 + IPv6).

```
ISP Modem (192.168.2.0/24) → Lab Router → Lab Devices (10.42.0.0/20 + fd42::/48)
```

**Why `10.42.0.0/20` and not `10.0.0.0/20`?** The `10.0.0.0/x` range is extremely common — corporate VPNs, Docker defaults, Kubernetes pod CIDRs, and cloud VPCs all frequently use `10.0.x.x`. If any of these overlap with the lab subnet, routes conflict and traffic breaks. `10.42.0.0/20` is an uncommon slice of the `10.0.0.0/8` private range, so it is unlikely to collide with anything. The `42` is arbitrary — just picked to stay out of the way.

**Why `/20` and not `/24` or `/16`?** A `/24` gives only 254 usable addresses — that is enough for a flat network, but too small once you start carving out VLANs (each VLAN gets its own `/24` subnet within the parent range). A `/20` gives 4094 addresses and fits 16 × `/24` subnets comfortably — plenty of room for management, monitoring, Kubernetes, and future VLANs without ever running out. A `/16` (65k addresses) would also work but is far more than needed for a home lab.

**Why `fd42::/48` for IPv6 (ULA) and not a delegated prefix?** IPv6 normally needs no NAT at all — every device gets a globally routable address, but only if the upstream router (the ISP modem) delegates a usable prefix downstream (DHCPv6-PD). Consumer ISP modems usually either don't support this at all or only delegate a single `/64` — not enough for three VLANs, and it can change on every modem reboot, which would renumber the entire lab. Instead, the lab uses a Unique Local Address (ULA, `fd00::/8`) range: **`fd42::/48`**, split into one `/64` per VLAN (`fd42:10::/64`, `fd42:20::/64`, `fd42:30::/64`). This mirrors the IPv4 supernet in spirit (the "42" is the same arbitrary, memorable choice) — stable, private, and immune to ISP renumbering. Outbound IPv6 traffic is masqueraded (NAT66) to the router's WAN address until real prefix delegation is available; see [IPv6 Addressing (ULA + NAT66) on the Lab Network](#ipv6-addressing-ula--nat66-on-the-lab-network) below.

### Chosen Option: Dedicated Router Behind the ISP Modem

**Full isolation (maintaining home network is not in my homelab's scope):** The lab runs on its own subnet with its own DHCP and firewall. Lab mistakes — DHCP conflicts, Proxmox bridge issues, Kubernetes networking — are contained within the lab network and never reach home devices. Avoid changing the ISP Modem's core configuration when others in the house depend on it for internet access. Changing the home network configuration can break connectivity for everyone, so it's best to leave it as-is and put your own router behind it for the lab. Furthermore, the ISP modem may have limited or no VLAN support, making it unsuitable for isolating your lab network. Finally, it is not in my homelab's scope to maintain the home network, so I want to keep it untouched and let the ISP modem handle the home network while I experiment freely in my lab network.
- **Keeps the ISP modem intact:** Other people in the house depend on the ISP modem for WiFi and internet. Replacing it or changing its configuration would mean taking ownership of the entire home network. Keeping it untouched means home connectivity stays stable regardless of what happens in the lab. See [Goals](../1_Design/0_Goals.md), in short: I am NOT planning to self-host everything and make the home network dependent on my lab!
- **Learn networking:** Running your own dedicated router is a hands-on way to learn subnetting, routing, DHCP, firewall rules, VLANs, and dual-stack IPv6 (SLAAC, Router Advertisements, Neighbour Discovery) in a real environment — knowledge that only comes from actually running it, not from reading about it. Note that this remains true on a dedicated router OS: the concepts and the topology are identical, only the implementation details are handled by the platform instead of by hand (see [Historical Note](#historical-note-why-not-a-custom-raspberry-pi-os--ansible-router-anymore)).
- **It is stable and low-maintenance:** The lab router is infrastructure that everything else depends on. Keeping it boring, predictable, and quick to recover is worth more than squeezing the last bit of learning out of it.
- **It is fun:** Designing your own network infrastructure and segmentation is genuinely enjoyable.

**Classic mistakes that break home networks (avoid these):**
- Running a DHCP server (or IPv6 Router Advertisements) on the same subnet as home devices
- Changing DNS settings on the ISP modem
- Connecting Proxmox or Kubernetes nodes directly to the home network
- Misconfiguring Proxmox bridges (can cause broadcast loops)
- Running firewall experiments on the home LAN

---

## Hardware & Software

### Background Knowledge: Raspberry Pi, Hardware & OS

See [Raspberry Pi](../../../reference/os_hardware/Raspberry_pi.md) for detailed background on the Raspberry Pi hardware, ARM vs x86 architecture, SD cards, the operating system and kernel, the boot process, flashing, network interfaces, GPIO, raspi-config, and headless operation.

### Lab Router

A Raspberry Pi is used as the dedicated lab router, running **OpenWrt**. It is cost-effective, silent, low-power, and provides full control over routing, DHCP, firewall rules, VLANs, and dual-stack IPv6 — but with a maintained, purpose-built networking stack instead of a hand-assembled one.

#### Router Hardware
- **Raspberry Pi 4 or later** — the compute unit running the router software. OpenWrt provides official images for the Pi 4 (bcm27xx/bcm2711 target), so the same hardware carries over unchanged from the previous setup.
- **SD card with the OpenWrt image flashed** — primary storage. Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) or any image writer (e.g. balenaEtcher, dd): download the OpenWrt `squashfs-factory.img.gz` for the Pi target from [downloads.openwrt.org](https://downloads.openwrt.org/), select your SD card as the target, and write it. Then insert the SD card into the Pi and it boots from it automatically. Note that OpenWrt is flashed as a complete firmware image — there is no OS installer and no `apt` base system underneath; the image *is* the router.
  - **No SD card reader on your laptop?** Most laptops do not have a built-in SD card reader (and even those that do often only accept full-size SD, not microSD). Use a USB SD card reader/adapter — a small dongle that accepts a microSD card and plugs into a USB port. I bought the "ISY ICR-120 USB 2.0-kaartlezer USB 2.0" for 6.99 EUR at MediaMarkt (ISY is MediaMarkt's store brand, it is a reputable and affordable brand). Plug it into your laptop, insert the microSD card, and it appears as a removable drive that the imager can write to.
- **USB-to-Ethernet adapter (eth1)** — adds the LAN interface. I bought the "TP-LINK UE306" for 12.99 EUR at MediaMarkt because "TP-LINK" is a reliable brand and affordable (do not buy the "TP-LINK UE300C" — it is USB-C, which the Pi 4 does not have). Plug into a USB-A port. Unlike Raspberry Pi OS, OpenWrt ships a minimal image, so the driver package for the adapter (`kmod-usb-net-rtl8152` for the UE306) must be installed explicitly with `opkg`/`apk` or, better, baked into a custom image — see [Automation & Documentation as Code on OpenWrt](#automation--documentation-as-code-on-openwrt). Once installed, it is detected as eth1 exactly as before.
- **Access to the ISP modem admin page** — to reserve a static IP for the Pi's `eth0` by MAC address and check for IP conflicts. Typically at `192.168.2.254`, `192.168.2.1` or `192.168.1.1`.

#### Router OS: OpenWrt

OpenWrt is a purpose-built Linux distribution for routers and network appliances. It is the OS the lab router now runs, replacing the previous Raspberry Pi OS Lite installation that was configured by hand through custom Ansible roles.
- **Why OpenWrt:** it ships a complete, coherent, well-tested networking stack out of the box — interfaces, VLANs, DHCP, DNS, Router Advertisements, NAT/NAT66, and a default-deny firewall — all driven by one unified configuration system (UCI). Everything the previous setup had to assemble, wire together, and keep consistent by hand is already integrated, tested by a large community on exactly this use case, and upgraded as a single unit. Upgrades are a `sysupgrade` that preserves the configuration, and a full recovery is "flash the image, restore the config backup" — minutes instead of an evening. It also brings capabilities that would otherwise be real projects on their own: WireGuard, DNS-over-TLS, adblocking, traffic shaping/SQM, per-interface statistics, and a web UI (LuCI) for the moments when you do not want to read a config file.
- **Why not stay on Raspberry Pi OS Lite with dnsmasq + nftables?** Because the learning goal that justified it has been met — see the [Historical Note](#historical-note-why-not-a-custom-raspberry-pi-os--ansible-router-anymore) directly below.
- **Why not pfSense/OPNsense?** They are excellent, mature router/firewall platforms, but they are FreeBSD-based with effectively no ARM/Raspberry Pi support, so running them would mean buying and powering an x86 box purely to be a router. OpenWrt runs well on the hardware already in the lab, uses a few watts, is silent, and has no fans or spinning disks to fail.
- **Why not run the router as a VM on Proxmox?** Because then the router and its management path share a single failure domain: if the Proxmox host is down, being reinstalled, or has a broken bridge, the entire lab — and the path used to fix it — is gone at the same time. A separate physical router keeps the network up independently of the virtualization platform, which is exactly the property you want from infrastructure.

#### Historical Note: Why Not a Custom Raspberry Pi OS + Ansible Router Anymore

The original design of this lab used Raspberry Pi OS Lite with a hand-built routing stack via the [custom router role](https://github.com/CollinPoetoehena/devhub-ansible-router-custom) I developed — dnsmasq for DHCP/DNS/SLAAC, nftables for NAT/NAT66 and a dual-stack default-deny firewall, VLAN sub-interfaces (e.g. eth1.10/.20/.30) managed through NetworkManager, and IP forwarding enabled through two separate sysctls — all deployed and maintained through a custom Ansible `router` role. That choice was deliberate and, at the time, correct: the explicit goal was to learn Linux networking by doing it, and writing every forwarding rule, every masquerade rule, every lease reservation, and every Router Advertisement (RA) option by hand teaches far more than selecting checkboxes in a GUI. It also produced fully version-controlled documentation as code, which is exactly how the topology, the addressing plan, and the firewall policy in this document came to be understood well enough to write down at all.

What changed is not the design but the objective. Building the custom router was a learning project; the router itself is infrastructure. Once the learning was done, everything that remained was maintenance: keeping the Debian base updated, tracking dnsmasq and nftables package changes, re-verifying the ruleset after every kernel or NetworkManager update, chasing IPv6 quirks where forwarding silently stayed IPv4-only because one sysctl was missed, debugging why a VLAN sub-interface did not come up after a reboot or a carrier loss, and re-testing the entire dual-stack path after each change. Diagnosing those problems is genuinely time-consuming, and it is time spent on a problem that has already been solved — by a dedicated router OS like OpenWrt or pfSense — rather than on the parts of the homelab that are still teaching something new. On top of that, recovery was slow: an SD card failure meant reinstalling the OS, re-bootstrapping the Ansible user, and re-running the playbooks before the lab had a network again.

The trade-off is therefore accepted consciously. Some depth is given up: the platform now decides how the ruleset is rendered and how the interfaces are brought up, and a layer of abstraction sits between the intent and the kernel. In exchange the router becomes *boring* (not boring to work with but boring in the sense of stability/reliability) — stable, upgradeable in one command, restorable from a config backup in minutes, and supported by a community that runs this exact stack on hundreds of thousands of devices. The time that used to go into maintaining and troubleshooting the router now goes into other things like Proxmox, Kubernetes, storage, observability, GitOps, and backup — the areas of the homelab where there is still something to learn. And running a dedicated router still is highly valuable for learning networking concepts, etc. The old role is kept archived for reference (see [custom router role](https://github.com/CollinPoetoehena/devhub-ansible-router-custom)): the concepts it taught (subnetting, routing, NAT, stateful firewalling, SLAAC, VLAN tagging) are precisely what makes the dedicated router OS like OpenWrt or pfSense configuration in this document readable rather than magic.

#### Routing Software Stack: OpenWrt (UCI + dnsmasq/odhcpd + firewall4/nftables)

OpenWrt does not replace the building blocks from the previous design with the custom router (see [Historical Note: Why Not a Custom Raspberry Pi OS + Ansible Router Anymore](#historical-note-why-not-a-custom-raspberry-pi-os--ansible-router-anymore)) — it integrates them and manages them centrally through **UCI** (Unified Configuration Interface), a single configuration system whose files live in `/etc/config/` (`network`, `dhcp`, `firewall`, `system`, `wireless`). Every component below is configured through UCI rather than through its own native config file, which is what makes the whole stack consistent and, importantly, scriptable:
- **netifd + UCI `network`** — manages the WAN interface (eth0, DHCP client towards the ISP modem), the LAN trunk (eth1), and the three tagged VLAN interfaces (eth1.10, eth1.20, eth1.30) carrying the per-VLAN IPv4 gateway addresses and the fd42:xx::1 ULA gateway addresses. IPv4 and IPv6 forwarding are handled by the platform as part of bringing interfaces and zones up — there is no pair of loose sysctls to forget, which removes one of the most common ways a "dual-stack" router silently ends up routing IPv4 only.
- **dnsmasq** — still provides DHCPv4 leases (including the static reservations, e.g. the switch at 10.42.10.2) and DNS forwarding/caching for both address families, including local hostname resolution for lab devices. It is the same daemon as before, just configured through `/etc/config/dhcp` instead of a hand-written `dnsmasq.conf`.
- **odhcpd** — handles IPv6 Router Advertisements/SLAAC (and optional stateless DHCPv6) per VLAN, so lab devices derive their own fd42:10::/64, fd42:20::/64, and fd42:30::/64 addresses. On OpenWrt this is a dedicated daemon rather than an option flag on dnsmasq, which makes per-interface RA behaviour explicit and easier to reason about.
- **firewall4 (nftables)** — generates the nftables ruleset from the zone/rule/forwarding model in `/etc/config/firewall`. The underlying engine is the same nftables that the previous setup wrote by hand, so `nft list ruleset` still shows a familiar `inet` table; the difference is that policy is expressed as zones (wan, mgmt, services, iot) and explicit inter-zone forwardings rather than as individual chains and rules maintained manually. Masquerading for IPv4 and NAT66 for the fd42::/48 ULA range are zone options, and the default for every unspecified flow is drop — which is exactly the default-deny posture the [IoT Isolation](#iot-isolation) and [Management VLAN](#why-a-dedicated-management-vlan-vlan-10) sections depend on.
- **Dropbear (SSH)** — provides the SSH access used for the [jumphost](#jumphost-secure-access-to-lab-network) role and for automation, key-only, with password authentication disabled.
- **LuCI (optional web UI)** — a read-mostly convenience. It is useful for inspecting live state (leases, routes, firewall counters, interface statistics) and for recovery, but configuration changes are still made through version-controlled UCI so the Git repository remains the source of truth.

#### Automation & Documentation as Code on OpenWrt

Moving to a dedicated router OS does **not** mean giving up infrastructure as code (IaC) and automation. UCI is fully scriptable (`uci set`, `uci commit`, `uci show`), so the same Ansible workflow used for the rest of the homelab still applies: variables (VLAN IDs, subnets, static leases, firewall rules, WireGuard peers) live in Git, templates render the `/etc/config/*` files, and a playbook pushes them to the router and reloads the affected services. What disappears is not the automation but the obligation to implement the routing stack itself.

Concretely, the split that works well here is: **OpenWrt owns the platform, Git and Ansible own the configuration.** Automate the things that actually change — VLAN definitions, DHCP reservations, firewall rules, DNS overrides, WireGuard peers, and configuration backup/restore. Do not over-engineer the things that never change, such as hostname, NTP servers, or LED behaviour; those are set once and captured in the config backup. For maximum reproducibility the OpenWrt Image Builder can be used to produce a custom image that already contains the required packages (the `kmod-usb-net-rtl8152` driver for the USB-Ethernet adapter, WireGuard, monitoring agents) and the baseline UCI configuration, so a rebuild from a dead SD card is "flash image, push config, done".

This preserves the property the original design valued most — the configuration and the reasoning behind it are captured in version-controlled files rather than clicked into a web interface — while removing the maintenance burden of owning the routing stack itself. See the archived [custom router Ansible role]((https://github.com/CollinPoetoehena/devhub-ansible-router-custom)) for how this was done previously on Raspberry Pi OS, and the current OpenWrt role for how the same intent is expressed through UCI today.

### Managed Switch

**Managed switch** — expands LAN ports and enables VLANs. I bought the "NETGEAR GS305E" for 24.99 EUR at MediaMarkt because "NETGEAR" is a reputable brand and affordable (the "TP-LINK TL-SG105E" is a good alternative). See [User Manual](https://www.netgear.com/support/product/gs305e). VLAN tagging happens at Layer 2 (Ethernet frames), so the same trunk/tagged configuration carries IPv4 and IPv6 traffic together without any switch-side change for dual-stack — the switch has no notion of IPv4 vs IPv6 at all, it only sees VLAN-tagged frames. The switch configuration is unaffected by the move to OpenWrt: it trunks the same tagged VLANs (10, 20, 30) to the router regardless of which OS terminates them.

### Ethernet Cables

**Ethernet cables** (Cat6 or better for gigabit speeds):
- **Long Ethernet cable for WAN (ISP modem → lab router)** 1 cable (10 m (ensures it can reach the router, such as if it needs to go through the wall or a conduit to a different floor (e.g. your work room), etc.)). I bought the "ISY IPC-6100-1-GB Netwerkkabel 10 m Wit" at MediaMarkt for 18.99 EUR because "ISY" (MediaMarkt's own store brand) is a reputable brand and affordable. Alternatively, you can decide to add all of your infrastructure in the TODO
- **Long Ethernet cable for WAN (ISP modem → lab router)** 1 cable (10 m). A longer cable provides flexibility when the router is not located near the ISP modem, for example when your lab is set up in a dedicated work room, office, or another floor of the house. Keeping the router and other lab equipment in your work room is often preferable because it makes maintenance, troubleshooting, cable management, and physical access significantly easier. It also allows you to keep noise, blinking LEDs, and additional equipment close to where you actually use and manage them. The cable may need to pass through walls, conduits, or between floors, so 10 m is usually a safe choice. I bought the "ISY IPC-6100-1-GB Netwerkkabel 10 m Wit" at MediaMarkt for 18.99 EUR because "ISY" (MediaMarkt's own store brand) is a reputable and affordable brand.
  > **Alternative:** You may choose to install the router, switch, and other networking/homelab equipment in the meter cabinet ("meterkast") alongside the ISP modem. In that case, much shorter Ethernet cables will likely be sufficient. For typical consumer and homelab networking equipment, this is generally safe from a fire-safety perspective, provided the devices are used as intended, have adequate ventilation, and do not obstruct access to electrical installations. Avoid overcrowding the cabinet with heat-generating equipment, ensure proper airflow around all devices, and verify that the installation complies with any local electrical regulations or requirements.
- **Lab router → lab switch:** 1 cable (0.75 m). I bought the "ISY IPC-1012 CAT6A U/UTP Slim Netwerkkabel 0,75 m Wit" at MediaMarkt for 9.99 EUR (same reasoning for this brand as above).
- **Lab switch → lab devices:** 1 cable per device (same model as above).

---

## Network Topology & Design

See [Node Setup](../1_Design/1_Hardware_Prerequisites.md#node-setup) for the physical nodes in the homelab. The network topology diagram below shows how the nodes are connected to the lab router and switch, how the lab network is isolated from the home network, and the dual-stack (IPv4 + IPv6) addressing per VLAN. The topology and addressing are unchanged by the move to OpenWrt — only the implementation on the router changed, not the design.

**Full high-level network topology and design (in .md diagram format to save space — no image file needed for this setup (KISS: Keep It Simple, Stupid)):**
> **Scope note:** The network design described above focuses on the homelab environment, detailing VLAN segmentation, IP addressing, and the role of the lab router as a jumphost. It assumes a separate home network and does not cover ISP-specific configurations or external network considerations. Furthermore, low-level network configurations on the actual VLAN interfaces (e.g. the kubernetes network setup in the Services VLAN) of the router and switch are considered out of scope for this document and should be explained in the dedicated design document (e.g. [cluster network design]).
```
┌────────────────────────────────────────────────────────────┐
│                          Internet                          │
└────────────────────────────────────────────────────────────┘
                              ⇵
┌────────────────────────────────────────────────────────────┐
│           ISP Home Modem/Router (192.168.2.254)            │
│           Home devices (192.168.2.0/24)                    │
└────────────────────────────────────────────────────────────┘
                              ⇵
┌────────────────────────────────────────────────────────────┐
│   Lab Router (Homelab Network: 10.42.0.0/20 + fd42::/48)   │
│   eth0 (WAN; connected to ISP Modem)                       │
│   eth1.x (LAN (VLAN subinterface); connected to switch)    │
└────────────────────────────────────────────────────────────┘
                              ⇵
┌────────────────────────────────────────────────────────────┐
│            Managed Switch (expands LAN ports)              │
└────────────────────────────────────────────────────────────┘
  ├─ VLAN 1  Native (unused — no production traffic)
  │
  ├─ VLAN 10 Management      (10.42.10.0/24 + fd42:10::/64)
  │    ├─ 10.42.10.1  / fd42:10::1    Router (Raspberry Pi — gateway for all VLANs)
  │    ├─ 10.42.10.2                  Switch (NETGEAR GS305E — management interface)
  │    ├─ 10.42.10.10 / fd42:10::10   PVE1 (physical machine: Proxmox VE host 1 — old laptop)
  │    └─ 10.42.10.11 / fd42:10::11   PVE2 (physical machine: Proxmox VE host 2 — Mini PC (future; not yet deployed))
  │
  ├─ VLAN 20 Services        (10.42.20.0/24 + fd42:20::/64)
  │    ├─ 10.42.20.x / fd42:20::x     Kubernetes nodes, application VMs
  │    └─ ...                         (Grafana, Prometheus, Home Assistant, ArgoCD, etc.)
  │
  └─ VLAN 30 IoT            (10.42.30.0/24 + fd42:30::/64)
        ├─ 10.42.30.x / fd42:30::x     Smart plugs, sensors, Zigbee gateways
        └─ ...                         (all smart/IoT devices)
```

IPv6 addresses shown above are the router's own gateway addresses per VLAN (statically configured) and the ULA addresses lab devices derive for themselves via SLAAC. Individual lab devices do not need a static IPv6 address reserved — see [IPv6 Addressing](#ipv6-addressing-ula--nat66) for why static leases are IPv4-only by design in this lab.

**The sections below explain some of the design choices made for the lab network in more detail.**

### IPv6 Addressing (ULA + NAT66) on the Lab Network

**The lab is deliberately dual-stack rather than IPv4-only. This is a design choice, not an accident:**
- **Practice:** SLAAC, Router Advertisements, Neighbour Discovery, ULA vs GUA addressing, and IPv6 firewalling can only really be learned by running them — not by reading about them.
- **More possibilities:** dual-stack unlocks testing real dual-stack services, AAAA records, IPv6-only clients, and (later) dual-stack Kubernetes, instead of a permanently IPv4-only lab.
- **Better firewalling discipline:** IPv6 has no NAT to hide behind, so every inbound flow must be explicitly allowed on the router. This forces a proper default-deny firewall instead of relying on NAT as an accidental security boundary (see [IoT Isolation](#iot-isolation) and [Jumphost](#jumphost-secure-access-to-lab-network) below for where this matters concretely).

Addressing uses **ULA (fd42::/48)**, one `/64` per VLAN, instead of a prefix delegated by the ISP modem — see [Why fd42::/48](#option-3-dedicated-router-behind-the-isp-modem) above for the reasoning. Because ULA addresses are not globally routable, outbound IPv6 traffic is masqueraded to the router's WAN IPv6 address (**NAT66**), the same way IPv4 traffic is masqueraded to the WAN IPv4 address. NAT66 is not something to be proud of — in a "real" dual-stack network with a properly delegated prefix there would be no NAT for IPv6 at all — but it is the pragmatic choice for a homelab sitting behind a consumer ISP modem that does not delegate a usable prefix downstream. The moment prefix delegation becomes available, NAT66 can simply be switched off and the lab becomes properly routed dual-stack with no translation at all.

### Jumphost: Secure Access to Lab Network

A jumphost is a single, controlled entry point into a protected network, used to securely access management interfaces and internal systems.

The lab router (Raspberry Pi) is used as the jumphost for accessing all management interfaces inside the homelab. This is both intentional and beneficial for stability, security, and operational simplicity:
- **Central position in the network:** The lab router sits at the heart of VLAN 10 (Management) and has routed visibility into all VLANs (see [Network Topology & Design](#network-topology--design)). This makes it the most reliable and consistent entry point into the homelab network.
- **Always reachable:** As the gateway (10.42.10.1 / fd42:10::1), the lab router remains accessible even if Proxmox, Kubernetes, or VLAN tagging break. It provides a stable fallback path during outages or misconfigurations.
- **Strong isolation guarantees:** Firewall rules already isolate management traffic. IoT devices cannot reach VLAN 10, and inter-VLAN traffic is denied by default — for both IPv4 and IPv6. This matters more for IPv6 specifically, since there is no NAT to accidentally provide that isolation as a side effect; the router's firewall rules are the *only* thing enforcing it.
- **Safe entry from the home network:** SSH access enters through the router's WAN interface, keeping the home network (e.g. 192.168.2.0/24) fully separated from the lab network (e.g. 10.42.0.0/20 + fd42::/48). No lab device is directly exposed to the home LAN or, once IPv6 routes to the internet, to the internet itself.
- **Centralized authentication & logging:** The router is the only device exposed to the home network, making it the ideal place to centralize SSH keys, access control, and audit logs — similar to enterprise bastion host patterns.
- **Minimal overhead:** The router is lightweight and hardened. Running a jumphost on it adds negligible load while significantly improving operational safety.
- **No extra hardware or services needed:** The homelab has limited physical machines and capacity; using the router as the jumphost avoids the need for a dedicated bastion VM or additional hardware, keeping the design simple and resource-efficient.
- **Enterprise-aligned design:** Using the router as the bastion mirrors how real networks operate: a single controlled gateway that provides secure access to management infrastructure.

### Subnet & VLAN Design

| Subnet (IPv4) | Subnet (IPv6, ULA) | VLAN | Purpose |
| --- | --- | --- | --- |
| — | — | 1 (native) | Unused — no production traffic, fallback recovery only |
| 10.42.10.0/24 | fd42:10::/64 | 10 | Management — router, switch, Proxmox host management IPs |
| 10.42.20.0/24 | fd42:20::/64 | 20 | Services — Kubernetes, application VMs, monitoring, databases |
| 10.42.30.0/24 | fd42:30::/64 | 30 | IoT — smart plugs, sensors, Zigbee gateways, energy meters |

#### Why VLAN 1 (native) is not used — all traffic is explicitly VLAN-tagged

The native VLAN (VLAN 1) carries no production traffic in this design. Every device — router, switch, Proxmox hosts, services, IoT — communicates exclusively on tagged VLANs (10, 20, 30). The Pi router's physical eth1 interface has no IP address in either address family; all traffic flows through VLAN sub-interfaces (eth1.10, eth1.20, eth1.30). VLAN 1 exists on the switch only because 802.1Q requires a native VLAN — it cannot be deleted, but it carries nothing.

Why this is the right approach:
- **Everything is explicit:** When all traffic is tagged, every frame on the wire declares which VLAN it belongs to. There is no ambiguity about where untagged traffic ends up. Debugging is simpler — a packet capture shows the VLAN tag immediately, and you never have to wonder "is this untagged frame on VLAN 1 or did something strip the tag?"
- **Closer to enterprise practice:** In production environments, the native VLAN is left unused or disabled entirely. All real traffic — including management — is explicitly tagged. Learning this pattern now means fewer surprises when working with enterprise infrastructure.
- **Security — prevents VLAN hopping:** Native VLAN hopping attacks (802.1Q double-tagging) exploit the fact that the native VLAN is untagged. An attacker on the native VLAN can craft a double-tagged frame: the switch strips the outer (native) tag and forwards the inner tag to a different VLAN. By not carrying any production traffic on the native VLAN, this attack vector is eliminated — there is nothing to hop from.
- **Easier to expand later:** Adding new VLANs is uniform — every VLAN is tagged, every subnet has a matching VLAN ID (VLAN 10 → 10.42.10.0/24 + fd42:10::/64, VLAN 20 → 10.42.20.0/24 + fd42:20::/64, VLAN 30 → 10.42.30.0/24 + fd42:30::/64). No special case for "the one VLAN that happens to be untagged."
- **Cleaner trunk configuration:** All production VLANs are tagged on trunk ports. No confusion about which VLAN carries untagged traffic on which port.
- **Fallback recovery still works:** Even though VLAN 1 is unused, it remains configured as untagged on all ports. If VLAN tagging breaks entirely (firmware bug, misconfiguration), untagged frames still flow on VLAN 1 — you can connect a laptop directly to the switch, assign a static IP, and access the switch web UI to fix the configuration.

#### Why a dedicated Management VLAN (VLAN 10)

Management traffic (SSH to hosts, Proxmox web UI, switch admin, router access) is on its own VLAN rather than being mixed in with services or IoT. This provides:
- **Isolation from workloads:** If a service on VLAN 20 misbehaves (broadcast storm, saturated bandwidth, compromised container), management access to the infrastructure remains unaffected — you can still SSH into hosts and access the Proxmox UI to diagnose and fix the problem.
- **Access control:** Firewall zones and forwardings on the router restrict which VLANs can reach management interfaces, for both IPv4 and IPv6. IoT devices (VLAN 30) are blocked from reaching VLAN 10 entirely — a compromised smart bulb cannot probe Proxmox or SSH into the router, whether it tries over its DHCP-assigned IPv4 address or its SLAAC-derived IPv6 address. Only traffic that explicitly needs management access (e.g. your laptop via SSH tunnel) reaches VLAN 10.
- **Audit clarity:** All management traffic lives on a single, known subnet pair (10.42.10.0/24 + fd42:10::/64). Log analysis, packet captures, and firewall auditing are simpler when management is cleanly separated from application and IoT traffic.

#### IoT Isolation

IoT devices are often the least secure devices in a home. By isolating them on VLAN 30:
IoT (VLAN 30) → Services (VLAN 20) = Allowed (sensors push data to Home Assistant)
IoT (VLAN 30) → Management (VLAN 10) = Blocked (a compromised smart bulb cannot probe Proxmox)
Firewall zones on the router enforce this — inter-VLAN traffic is denied by default, then specific forwardings are allowed explicitly, for both IPv4 and IPv6. This matters more for IPv6 than it might first appear: IPv4 gets some accidental isolation "for free" from NAT (a device on VLAN 30 doesn't even have a routable address to reach VLAN 10 with), but IPv6 has no such safety net — every lab device gets a real, routable ULA address, so the IoT → Management block has to be an explicit policy rather than an emergent property of address translation. On OpenWrt each VLAN is its own firewall zone, so this policy is expressed as "which zones may forward to which", which is both easier to review and harder to get subtly wrong than a hand-written chain. See the OpenWrt router role for exactly how these zones and forwardings are generated per VLAN, and the archived [router Ansible role](../../ansible/roles/router/README.md) for the previous hand-written nftables equivalent.

#### Switch Port Assignments

| Port | Connected Device | VLAN Membership |
| --- | --- | --- |
| 1 | Pi Router (eth1) | Untagged: 1 (native, unused) + Tagged: 10, 20, 30 (trunk port) |
| 2 | PVE1 (Proxmox host 1) | Untagged: 1 (native, unused) + Tagged: 10, 20, 30 |
| 3 | PVE2 (Proxmox host 2) | Untagged: 1 (native, unused) + Tagged: 10, 20, 30 |
| 4 | (spare) | Untagged: 1 (native) |
| 5 | (spare) | Untagged: 1 (native) |

**How to read this table:** See [Network Devices — Tagged vs Untagged](../../../reference/network/Network_Devices.md#tagged-vs-untagged-8021q-vlan-tagging) for a full explanation of what tagged and untagged mean, how frames flow through the switch, and when to use each mode. Each port can be a member of multiple VLANs simultaneously. The "VLAN Membership" column lists **all** VLANs that a port participates in, separated by +. The keyword before each VLAN entry tells the switch how to handle frames for that VLAN on that port:
- **Untagged: 1** — Frames for VLAN 1 are sent/received **without** a VLAN tag in the [Ethernet frame header](../../../reference/network/Network_Models_and_Packets.md#anatomy-of-a-frame-layer-2). In this design, the native VLAN carries no production traffic — it exists only as a fallback recovery path. If all VLAN tagging breaks, untagged frames still flow, allowing you to reach the switch management interface.
- **Tagged: 10, 20, 30** — Frames for VLANs 10, 20, and 30 are sent/received **with** an 802.1Q VLAN tag in the [Ethernet frame header](../../../reference/network/Network_Models_and_Packets.md#anatomy-of-a-frame-layer-2) (a 4-byte field that says "this frame belongs to VLAN X"). The device on the other end must understand VLAN tags and process them — the Pi router uses sub-interfaces (eth1.10, eth1.20, eth1.30) and Proxmox uses VLAN-aware bridges to separate tagged traffic into the correct virtual networks. Each tagged VLAN carries both IPv4 and IPv6 traffic together — VLAN tagging is a Layer 2 mechanism and has no notion of which Layer 3 protocol rides inside the frame.

**The + does NOT mean "10, 20, and 30 are untagged from VLAN 1"** — it means the port carries four independent traffic streams: one untagged (VLAN 1, unused) and three tagged (VLAN 10, VLAN 20, VLAN 30). They coexist on the same physical cable but are completely separate at the logical level.

**Per-port explanation**
- **Port 1 — Pi Router (eth1):** The router is the gateway for all VLANs. Its physical eth1 interface is on the native VLAN (unused — no IP assigned, in either address family). Tagged traffic arrives on sub-interfaces eth1.10 (VLAN 10, IP 10.42.10.1 + fd42:10::1), eth1.20 (VLAN 20, IP 10.42.20.1 + fd42:20::1), and eth1.30 (VLAN 30, IP 10.42.30.1 + fd42:30::1). The router forwards traffic between VLANs (inter-VLAN routing) and applies firewall rules. This is a "trunk port" — it carries all VLANs.
- **Ports 2–3 — Proxmox hosts (PVE1, PVE2):** Each Proxmox host has one physical NIC connected to the switch. Management traffic (SSH to the host, Proxmox web UI) flows tagged on VLAN 10 — the host's management IP (10.42.10.10 or .11, plus its SLAAC-derived fd42:10::/64 address) is on a VLAN-aware bridge tagged to VLAN 10. VMs running on the host are placed into VLANs via Proxmox's VLAN-aware bridge (vmbr0): a service VM gets tagged into VLAN 20, an IoT gateway VM into VLAN 30. The switch delivers tagged frames for those VLANs to the port, and Proxmox's bridge routes them to the correct VM. PVE1 is the Acer laptop being set up now; PVE2 is a planned future addition and not yet physically connected.
- **Ports 4–5 — Spare:** Simple access ports — only untagged VLAN 1. Any device plugged in lands on the native VLAN (no production access by default). To give a device access to a specific VLAN, reconfigure the port.

**Why tagged for service VLANs instead of untagged (access ports)?** An alternative design would be to assign each port to a single VLAN as untagged (e.g. port 2 = untagged VLAN 10, port 3 = untagged VLAN 20). This is simpler per-port but has a critical limitation: **you only get 5 ports total**, and each device would be locked to a single VLAN. Since Proxmox hosts run VMs in multiple VLANs simultaneously (management + services + IoT on the same physical machine), the host's port MUST carry multiple VLANs — which requires tagging. **Summary of the tagging logic:**
- **VLAN 1 (native): untagged** — carries no production traffic; exists as a fallback recovery path if VLAN tagging breaks.
- **VLAN 10 (management): tagged** — router, switch, Proxmox hosts; requires VLAN-aware sub-interface/bridge.
- **VLAN 20 (services): tagged** — Kubernetes, all hosted applications; requires VLAN-aware bridge/sub-interface.
- **VLAN 30 (IoT): tagged** — smart devices, sensors; isolated from management for security.
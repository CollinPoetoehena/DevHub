# Goals & Hardware

This document covers the goals for this home lab and all decisions around choosing and buying hardware — including hardware types, purchasing strategy, recommended shops, and node setup.

---

## Table of Contents

- [Goals](#goals)
- [Hardware Purchasing Strategy](#hardware-purchasing-strategy)
  - [New vs. Refurbished vs. Second-Hand](#new-vs-refurbished-vs-second-hand)
  - [Refurbished Shops in Europe](#refurbished-shops-in-europe)
  - [What to Check When Buying Refurbished](#what-to-check-when-buying-refurbished)
- [Hardware Type Selection](#hardware-type-selection)
  - [Comparison: Main Compute Options](#comparison-main-compute-options)
  - [Why Mini PCs](#why-mini-pcs)
  - [Why Enterprise-Grade (e.g. Dell, Lenovo, HP)](#why-enterprise-grade-eg-dell-lenovo-hp)
  - [Why NOT Raspberry Pi](#why-not-raspberry-pi)
- [Node Setup](#node-setup)
  - [How Many Nodes](#how-many-nodes)
  - [Recommended Node Composition](#recommended-node-composition)
  - [Starting Small](#starting-small)
  - [Current Personal Setup](#current-personal-setup)

---

## Goals

The personal goal is described in detail in the [Home Lab README](../README.md#personal-goal). In short: learn DevOps fundamentals (Kubernetes, networking, Linux, monitoring, automation) through hands-on experimentation — because it's fun and directly relevant to daily engineering work.

The hardware choices below are driven by this goal: affordable, real-world-grade, and sufficient for running a small Kubernetes cluster with Proxmox, Ansible, Terraform, and monitoring tools.

---

## Hardware Purchasing Strategy

### New vs. Refurbished vs. Second-Hand

| Feature | Brand-New Retail | Professional Refurbished | Private Second-Hand |
|---|---|---|---|
| **Price** | Highest | Up to 60% cheaper with low risk | Cheap, but high risk |
| **Quality Control** | 100% factory-tested | Tested on critical points | No guarantees |
| **Battery / Wear** | 100% capacity / brand-new | Minimum guarantees (e.g. 85%), otherwise replaced | Unknown (often worn out) |
| **Warranty** | Standard 2-year warranty | 1–2 years full refurbisher warranty | "Warranty until the front door" — basically none |
| **Sustainability** | Requires new materials & manufacturing | Very circular (prevents e-waste) | Circular, as long as the device works |

**Verdict:**
- **Brand-new** → Too expensive for a learning lab. Not needed.
- **Professional refurbished** → Best balance. Enterprise-grade hardware (e.g. Lenovo, Dell, HP) at 40–80% less. These units come from companies replacing their fleets — the hardware is still high quality, power-efficient, and tested. This is the right choice for a home lab focused on learning real-world skills without breaking the bank.
- **Private second-hand** (e.g. Marktplaats, eBay) → Too risky. No proper testing, no guarantees. Avoid.

> **What is "refurbished"?** A previously used device that has been professionally inspected, cleaned, and extensively tested. Only when everything checks out technically is it offered as Refurbished. Not the same as second-hand.

---

## Refurbished Shops in Europe

### Personally Recommended

I personally found the best deals and experience with **Refurbed** and **BackMarket** (not sponsored). Both have a wide selection of enterprise-grade mini PCs, good reputation (e.g. been around for some time and trusted by many users), good warranties, and solid customer service, etc.:
- **[BackMarket](https://www.backmarket.nl)** is the largest European refurbished marketplace, well-known and reliable.
- **[Refurbed](https://www.refurbed.nl)** is an EU-wide marketplace with multiple vetted refurbishers. Refurbed enforces strict quality standards on its partners and offers:

Best for: maximum buyer protection and peace of mind across the EU.

### Other Shops Considered

| Shop | Notes | Verdict |
|---|---|---|
| **ReMarkt** | Dutch refurbisher with physical stores (ex-MediaMarkt). 12-month warranty, in-store testing, Dutch customer service. | Not chosen — limited mini PC selection, Dutch-local only. Refurbed EU is better. |
| **IT-Giant** | Dutch webshop for refurbished business hardware (servers, workstations, mini PCs). Lowest prices for business-grade gear, popular with home-lab builders. | Not chosen — Dutch-local only. Refurbed EU is better. |
| **eBay** | Cheap, but inconsistent quality and seller risk (I do not trust the sellers since there is not really a quality guarantee). | Avoid. |
| **Amazon Renewed** | Good warranty, but generally higher prices than dedicated refurbishers and I do not trust the sellers since there is not really a quality guarantee. | Not preferred. |
| **MediaMarkt / Coolblue** | Mostly brand-new; not ideal for refurbished mini PCs. | Not relevant. |

### Tip: Ask Your Employer

Companies replace hardware on a fixed cycle — often every 3–5 years, regardless of whether a device still works perfectly. Before spending money on a refurbished shop, it's worth simply asking your manager or IT department whether any old devices are being decommissioned. Many companies are happy to give them away for learning purposes to employees rather than deal with disposal.

> **Important:** Before using any company device for personal purposes, make sure you have explicit permission from your manager or IT department. Do not assume it is allowed — company hardware is company property until formally decommissioned and released.
>
> Once you have a device: **ensure all company data has been fully wiped and the device has been factory reset or re-imaged before use.** This protects both you and your employer. A full disk wipe (e.g. `shred`, `dd`, or a secure erase tool) or reinstalling the OS from scratch is the safest approach, your IT department can provide guidance on the best method to ensure data security and compliance.

---

### What to Check When Buying Refurbished

- **Certification**: Look for *Keurmerk Refurbished* (NL) or an equivalent quality label.
- **Refurb process**: Check that the seller lists their full refurbishment process and read it carefully.
- **Battery health**: Aim for 80%+ capacity, or a replaced battery.
- **Warranty length**: Minimum 12 months recommended.
- **Return policy**: 14–30 days is standard for reputable sellers.
- **Condition grading**: "Like New" vs. "Very Good" can mean big price differences — read the grading definitions carefully.

---

## Hardware Type Selection

### Comparison: Main Compute Options

| Category | CPU Power | RAM | Storage | Noise | Power Usage | Virtualization | Cost | Best Use Case |
|---|---|---|---|---|---|---|---|---|
| **Raspberry Pi** | Low | 1–8 GB | SD / USB SSD | Silent | Very low (5–10W) | Limited (ARM) | €50–€150 | Lightweight services, learning Linux |
| **Mini PC** | Medium to high | 8–64 GB | NVMe SSD (most common) | Silent / very quiet | Low (10–40W) | Excellent | €150–€400 | Proxmox, Docker, Kubernetes, CI/CD |
| **Laptop** | Medium | 8–32 GB | NVMe SSD | Quiet | Low–medium (10–60W) | Good | €200–€600 | Portable DevOps work, Docker, k3s |
| **Server** | Very high | 32–256 GB | RAID SSD/HDD | Loud | Very high (100–300W) | Enterprise-grade | €300–€800 | Production workloads (overkill for home labs) |

> A great DevOps home lab focuses on **production-like architecture, not production-grade hardware**. You don't need enterprise servers (very harmfull for your wallet) — but you do need reproducibility, automation, observability, and failure testing, etc.

### Why Mini PCs

- **Strong virtualization performance** — desktop-class CPUs (e.g. Intel i5/i7) handle Proxmox, Docker, and Kubernetes easily.
- **High RAM capacity** — up to 64 GB, which is good for running multiple VMs.
- **Silent operation** — can run 24/7 without fan noise (or minimal noise).
- **Low power usage** — typically 10–40W, far cheaper to run than servers.
- **Affordable** — €150–€400 per refurbished node for strong performance.
- **Compact size** — easy to stack for a small cluster.
- **Reliable business-grade hardware** — built for corporate environments, long lifespan (e.g. Dell, Lenovo, etc., see [Why Enterprise-Grade Hardware?](#why-enterprise-grade-eg-dell-lenovo-hp)).
- **Easy to upgrade** — RAM and NVMe SSD upgrades are simple.
- **Perfect for clustering** — ideal for a multi-node Proxmox or Kubernetes cluster.

### Why Enterprise-Grade (e.g. Dell, Lenovo, HP)

- **Enterprise-grade reliability** — built for 5–10+ years of nonstop corporate use.
- **Real-world relevance** — the same class of hardware used in actual IT jobs; your lab mimics production.
- **Excellent virtualization support** — stable BIOS, VT-x/VT-d, predictable behaviour under Proxmox, KVM, Docker, and Kubernetes.
- **Long lifespan** — designed for long service cycles, fewer failures, consistent performance.
- **Efficient power usage** — typically 10–40W, far lower than servers or desktops.
- **Quiet operation** — engineered for office environments, silent even under load.
- **Compact form factor** — perfect for stacking multiple nodes without taking up space.
- **Massive refurbished availability** — companies generally replace fleets every 3–5 years regardless of condition, so you get high-quality hardware at low prices.
- **Consistent performance** — stable, predictable components, not the random mix found in consumer machines.
- **Better thermals** — designed to stay cool in dense office deployments.
- **Low failure rate** — higher-quality components than consumer PCs.

### Why NOT Raspberry Pi

Mini PCs give more value for money because they are **complete computers**: a proper x86 CPU, upgradeable RAM, fast NVMe SSD storage, active cooling, a stable power supply, and reliable networking all in one device. They're designed to run 24/7 under load and handle Kubernetes workloads more consistently.

Raspberry Pi boards are bare single-board computers — you still need to add a case, cooling, storage, and sometimes extra networking gear. They also use weaker ARM hardware and rely on microSD cards or add-on storage, which is slower and less reliable. Even though the Pi itself is cheaper, you end up with less performance, less reliability, and less convenience — and it costs more in total than expected once you add all the accessories.

More importantly, the Pi uses ARM/Pi OS instead of x86/Ubuntu or RHEL — which is what you find in real enterprise environments. Mini PCs give a more realistic learning experience that better matches production.

---

## Node Setup

### How Many Nodes

**Aim for 3 nodes.** A 3-node setup gives you true cluster stability because it can form a **quorum** (a majority of nodes agree the cluster is healthy, so it can keep running even if one node fails). This enables real high-availability (HA) behaviour, proper leader election, and realistic distributed-systems scheduling — the way production clusters actually work.

More than 3 nodes is overkill for a learning lab: it increases power usage and cost without adding significant learning value.

You can of course add more nodes if you want but note that 3 is the sweet spot for a home lab that balances realism, cost, and manageability.

### Recommended Node Composition

- **2 identical refurbished enterprise-grade mini PCs** — the main compute nodes, providing real-world hardware experience (e.g. Lenovo ThinkCentre Tiny, Dell OptiPlex Micro, HP EliteDesk Mini, etc.).
- **1 older piece of hardware** — e.g. an old laptop. Lower specs are fine for a third node; it still completes the quorum and adds variety.

### Recommended Specs per Node

| Component | Recommended | Notes |
|-----------|-------------|-------|
| **CPU** | 4+ cores Intel N-series or 12th-gen Core i5 — full VT-x and VT-d support | Enough to run Proxmox + multiple VMs simultaneously without contention. |
| **RAM** | 16 GB | Minimum for comfortably running Proxmox with a few VMs. 32 GB if you can afford it for the main compute nodes. |
| **Storage** | NVMe SSD | Significantly faster than SATA SSD (3–7 GB/s vs ~550 MB/s) and far faster than HDD. Matters for VM boot times, live migration, snapshot I/O, and running multiple VMs in parallel. Most enterprise-grade mini PCs ship with an M.2 slot, making NVMe a natural fit — no cables, no adapters, compact form factor. |

**Storage sizing — intentional asymmetry:**

Not all nodes need the same storage size. A good approach is:
- **1× larger drive (e.g. 512 GB-1 TB)** on one node — acts as a "shock absorber": migration staging area, ISO storage, snapshots, and local VM disks when you need fast temporary storage, etc.
- **Smaller drives (e.g. 256 GB)** on the other compute nodes — sufficient for the OS, Proxmox, and their resident VMs, etc.

This asymmetry is intentional: the larger node handles temporary bulk workloads so the compute nodes stay lean and focused.

### Starting Small

If budget is a constraint, **start with 1 mini PC + 1–2 older devices** and expand later. You can still learn the fundamentals with a smaller cluster and add a second mini PC when ready. This keeps initial costs low while giving you a working multi-node environment from day one.

### Current Personal Setup
My current home lab setup consists of:

| Role | Device | CPU | RAM | Storage | Source | Why chosen |
|------|--------|-----|-----|---------|--------|------------|
| Compute node 1 + 2 | Dell OptiPlex 7050 Micro | Intel Core i5-7500T (3.2 GHz, TODO: cores and threads per core) | 16 GB | 256 GB SSD | BackMarket (refurbished), bought for €TODO: what did I buy them for eventually in 2026 | Enterprise-grade reliability, silent, low power (≈15W), VT-x/VT-d for virtualization, widely available refurbished at a good price (see [Why Enterprise-Grade](#why-enterprise-grade-eg-dell-lenovo-hp)). |
| Quorum node | Old personal Acer laptop (Acer Aspire A715-75G) | Intel Core i7-9750H (2.60 GHz, 6 cores, 2 threads per core) | 16 GB | 512 GB SSD | Personal (repurposed), bought in 2020 on Coolblue for about €600 | Already on hand — repurposed to complete the 3-node quorum at zero extra cost. |
| Extra node | Raspberry Pi 4 Model B | ARM Cortex-A72 (1.5 GHz, 4 cores, 4 threads) | 4 GB | 64 GB microSD | Personal (already owned), bought from Raspberry Store in 2025 for about €200 total (Raspberry Pi 4 Model B, Case, Case Fan, microSD, etc.) | Not the recommended choice for this lab — see [Why NOT Raspberry Pi](#why-not-raspberry-pi). However, it was already on hand so it was integrated into the cluster rather than left unused. |

#### How to Check Your Hardware Specs

**On Linux** (after OS is installed, or from a live USB):

```bash
# CPU: architecture, cores, threads, frequency
lscpu

# RAM: total and available memory
free -h

# Storage: disks, partitions, sizes
lsblk

# Full hardware overview (requires sudo)
sudo lshw -short

# Detailed CPU info (cores, threads, flags)
cat /proc/cpuinfo | grep -E 'model name|cpu cores|siblings' | sort -u
```

**On Windows** (before wiping the device — useful for checking before you buy or reinstall):

```powershell
# CPU name, cores, and logical processors
Get-WmiObject Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors

# RAM total (in GB)
(Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory / 1GB

# Storage disks
Get-PhysicalDisk | Select-Object FriendlyName, Size, MediaType
```

Alternatively, on Windows you can open **Task Manager → Performance** for a quick visual overview of CPU cores/threads, RAM, and disk.
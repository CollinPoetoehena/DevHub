# Design: Hardware & Prerequisites

This document is the **central place for every hardware decision in this homelab**: which physical devices are bought, why, with what specs, and from where — networking hardware (router/firewall appliance, switch, cabling) and compute/workload hardware (nodes) alike. If a piece of physical equipment is part of this lab, it is decided here and nowhere else.

Its counterpart is [Design: Software & Prerequisites](3_Design_Software_Prerequisites.md), which is the equivalent central place for every **software** decision (router OS, hypervisor, cluster, automation, observability, backup). Together the two documents own all concrete implementation choices; the remaining design documents (network, cluster, storage) describe the *architecture* and deliberately name no products or tools.

>**IMPORTANT NOTE:** This guide is focused on my personal homelab goals (see [Personal Goals](0_Goals.md)), the purchasing strategy and hardware choices may not be suitable for everyone. So, make sure to adapt it to your own needs and constraints.

## Why All Hardware Is in This One File

Hardware is one decision, made once, for one reason: **"what do I buy?"** Splitting that across several files would not make it smaller, only harder to answer.

- **One place to look for every physical device.** The router, the switch, the cables, and the nodes are bought against the same budget, from overlapping channels, under the same trade-offs (new vs. refurbished, official store vs. marketplace). Separating "networking hardware" from "compute hardware" would duplicate the purchasing reasoning in two places and let the two copies drift apart.
- **Every architecture document stays clean.** Because all brands, models, and prices are centralized here, the network and cluster design documents can describe topology, segmentation and policy without naming a single product — the classic separation between *architecture* and *implementation*.
- **Replacing a device is a one-file change.** Swap a node or the router and only this file changes; nothing else has to be hunted down and kept in sync.
- **Length is not the problem; structure is.** A long document with clear headings, tables and anchors is searchable (`Ctrl+F` finds everything), diffable in one review, and readable top to bottom. Split only when the parts have genuinely different audiences or lifecycles — which is exactly why *software* got its own document (see [the rationale there](3_Design_Software_Prerequisites.md)) and why hardware did not need further splitting.

## Table of Contents

- [Current Personal Setup](#current-personal-setup)
  - [Network](#network)
  - [Compute / Workload](#compute--workload)
- [Part 1 — Networking Hardware](#part-1--networking-hardware)
  - [Why a Firewall/Router Appliance Mini PC](#why-a-firewallrouter-appliance-mini-pc)
  - [Why New (and Not Refurbished) for the Router](#why-new-and-not-refurbished-for-the-router)
  - [Recommended Router Hardware Specs](#recommended-router-hardware-specs)
  - [Brand Comparison: Firewall Appliance Vendors](#brand-comparison-firewall-appliance-vendors)
  - [Where to Buy: AliExpress, Amazon, eBay & Official Stores](#where-to-buy-aliexpress-amazon-ebay--official-stores)
  - [Managed Switch](#managed-switch)
  - [Ethernet Cables](#ethernet-cables)
- [Part 2 — Compute / Workload Hardware](#part-2--compute--workload-hardware)
  - [Hardware Purchasing Strategy](#hardware-purchasing-strategy)
    - [New vs. Refurbished vs. Second-Hand](#new-vs-refurbished-vs-second-hand)
    - [Refurbished Shops in Europe](#refurbished-shops-in-europe)
    - [Why Not Amazon, AliExpress or eBay for Refurbished Compute](#why-not-amazon-aliexpress-or-ebay-for-refurbished-compute)
    - [Tip: Ask Your Employer](#tip-ask-your-employer)
    - [What to Check When Buying Refurbished](#what-to-check-when-buying-refurbished)
  - [Hardware Type Selection](#hardware-type-selection)
    - [Comparison: Main Compute Options](#comparison-main-compute-options)
    - [Why Mini PCs](#why-mini-pcs)
    - [Why Enterprise-Grade (e.g. Dell, Lenovo, HP)](#why-enterprise-grade-eg-dell-lenovo-hp)
    - [Why NOT Raspberry Pi](#why-not-raspberry-pi)
  - [Node Setup](#node-setup)
    - [How Many Nodes](#how-many-nodes)
    - [Recommended Node Composition](#recommended-node-composition)
    - [Recommended Specs per Node](#recommended-specs-per-node)
    - [Start Small, Expand Later](#start-small-expand-later)
- [Software](#software)

---

## Current Personal Setup

My current homelab setup is split into **network** (the things that move packets) and **compute/workload** (the things that run VMs and containers). The Raspberry Pi 4 that used to act as the lab router has been retired in favour of a dedicated x86 firewall/router appliance — see [Why a Firewall/Router Appliance Mini PC](#why-a-firewallrouter-appliance-mini-pc) for the reasoning.

### Network

| Role | Device | Key specs | Price | Source | Why chosen |
|------|--------|-----------|-------|--------|------------|
| Lab router / firewall | Firewall appliance mini PC: Topton Solid Fanless Firewall Mini PC Intel N150 Core | 4 cores x86, 8 GB DDR4, 128 GB NVMe, 4× Intel i226-V 2.5GbE, fanless | €339.39 | Bought **new** from the vendor's **official store** on AliExpress (see [Where to Buy](#where-to-buy-aliexpress-amazon-ebay--official-stores)); in this case [Topton Computer Store on AliExpress](https://nl.aliexpress.com/store/2546008) | Purpose-built for router/firewall software: multiple Intel NICs, x86, AES-NI, fanless, low power (the Intel N150 consumes about 6W). Runs OPNsense with room for VLANs, WireGuard and IDS/IPS (see [Router & Firewall Software](#router--firewall-software)). Specifically this model from Topton because it is a reputable brand (see [Brand Comparison: Firewall Appliance Vendors](#brand-comparison-firewall-appliance-vendors)) and this model was the most cost-effective option with the desired specifications and good reviews (at the time in 2026 about 20+ reviews and 250+ purchases in the Netherlands). *NOTE: I did not buy the SSD and RAM separately here because it was much cheaper to buy the complete unit with RAM and storage included and saves additional cost, effort and risk of buying incompatible components separately.* |
| Managed switch | NETGEAR GS305E | 5× 1GbE, 802.1Q VLAN tagging, web-managed | €24.99 | MediaMarkt (new) | Cheapest reliable way to get real VLAN tagging; reputable brand; 5 ports is enough for a router + 2 hosts + spares. The `TP-LINK TL-SG105E` is an equally good alternative. |
| WAN cable (ISP modem → router) | ISY IPC-6100-1-GB, Cat6, 10 m | Cat6, 10 m | €18.99 | MediaMarkt (new) | Long enough to run from the meter cabinet to the work room, through a wall or conduit if needed. |
| Router → switch and switch → hosts | ISY IPC-1012 CAT6A U/UTP Slim, 0.75 m | Cat6A, 0.75 m | €9.99 each | MediaMarkt (new) | Short patch cables keep the rack/shelf tidy; Cat6A is future-proof for 2.5GbE and beyond. |

>**Design choices behind the network hardware:** a **separate physical router** keeps the lab network independent of the virtualization platform (if Proxmox is down, the network is not), a **managed switch** is the minimum requirement for VLAN segmentation, and **short patch cables + one long WAN cable** is the cheapest layout that still lets the lab live in the work room instead of the meter cabinet. The full topology, subnetting, and VLAN policy are in the [3_Design_Network.md](3_Design_Network.md).

### Compute / Workload

| Role | Device | CPU | RAM | Storage | Price | Source | Why chosen |
|------|--------|-----|-----|---------|-------|--------|------------|
| Compute node 1 | Dell OptiPlex 7050 Micro | Intel Core i5-7500T (3.2 GHz, TODO: cores and threads per core) | TODO: 32 or 64 GB | TODO: 512 GB or 1 TB SSD | €TODO: what did I buy them for eventually in 2026 | BackMarket (refurbished) | Enterprise-grade reliability, silent, low power (≈15W), VT-x/VT-d for virtualization, widely available refurbished at a good price (see [Why Enterprise-Grade](#why-enterprise-grade-eg-dell-lenovo-hp)). |
| Compute node 2 | Old personal Acer laptop (Acer Aspire A715-75G) | Intel Core i7-9750H (2.60 GHz, 6 cores, 2 threads per core) | 16 GB | 512 GB SSD | ≈€600 in 2020 | Personal (repurposed), bought on Coolblue | Already on hand — repurposed to add a second physical host to experiment with, without extra purchasing cost. |

>**What I think is the best value here (for my personal homelab, which is mostly used for learning and experimenting (see [Personal Goals](./0_Design_Goals.md))):** one refurbished enterprise mini PC with as much RAM as you can get (32 GB is enough) plus one machine you already own. That combination costs the least, uses the least power, and still covers ~95% of the learning value (see [How Many Nodes](#how-many-nodes)). The router is the one device worth buying **new**; everything that runs workloads is worth buying **refurbished**.

---

## Part 1 — Networking Hardware

This part covers everything that moves packets: the router/firewall appliance (the main decision), the managed switch, and the cables. The network *design* — topology, subnets, VLANs, firewall policy — lives in the [3_Design_Network.md](3_Design_Network.md); this part is only about the physical boxes and how to buy them.

### Why a Firewall/Router Appliance Mini PC

A *firewall appliance mini PC* is a small, usually fanless (usually x86) machine whose defining feature is **multiple discrete Intel Ethernet ports** (typically 4× or 6× 2.5GbE) instead of the single NIC a normal mini PC or Raspberry Pi has. That one difference is the whole argument.

- **A router needs at least two real NICs.** One for WAN (towards the ISP modem) and at least one for LAN (towards the switch). A normal mini PC has exactly one. You can bolt on a USB-to-Ethernet adapter, but USB NICs are the single most common source of instability on BSD-based firewalls — drivers are hit-or-miss and links drop under load. For infrastructure that everything else depends on, that is not a trade worth making. You can also buy an additional NIC and attach it onto the mini PC or Raspberry Pi, but this also can cause instability and is often in total much more expensive than buying a firewall appliance mini PC, etc.
- **These boxes are built for exactly this job.** Intel i226-V 2.5GbE controllers or similar ones on firewall appliance mini PCs are natively supported by FreeBSD (which for example OPNsense is built on) through the `igc` driver, so there are no driver patches, no surprises after an upgrade, and no vendor-specific kernel modules. The chassis is fanless, the power supply is external, and the board exposes a serial console — all things you want in a device that runs 24/7 in a cupboard.
- **Completely silent — no moving parts at all.** These appliances are passively cooled: a solid aluminium chassis acts as the heatsink, so there is **no fan** and, with an NVMe or SATA SSD, **no spinning disk** either. Nothing in the box makes noise and nothing in the box can seize, clog with dust, or start whining after two years — fans and hard drives are the two components that fail most often in any always-on machine. That matters because the router lives in a work room or a cupboard and runs 24/7: a device you can hear very loudly is often a device you end up switching off.
- **Very low power draw, and that is real money.** The Alder Lake-N or similar CPUs in these firewall appliance mini PCs used in these boxes typically have a 6–15W base power figure, and a whole appliance typically idles around **8–15W** with a realistic ceiling near 20W under load. At ~€0.30/kWh (NL, 2026) that is roughly **€25–€40 per year** to run the entire lab network — versus a repurposed desktop/mini PC or an old 1U server, which would draw several times more and cost more in electricity every year than the appliance cost to buy. Low power also means low heat, which is exactly what makes the fanless design possible in the first place.
- **Cheap for what it is.** A complete multi-port appliance with RAM and an SSD lands around €250–€350 (at least in 2026) — comparable to a decent consumer router, and a fraction of a branded firewall appliance doing the same job. Crucially there is **no licence and no subscription**: the software is free and open-source, so the purchase price is the total price, where commercial firewall vendors charge annually for threat feeds and support. Against a DIY alternative with custom Ansible and nftables, dnsmasq, etc., it also wins on total cost, because a mini PC plus USB NICs plus adapters ends up in the same price range while being worse in every other respect.
- **Small, and easy to put somewhere sensible.** Roughly the footprint of a paperback, VESA-mountable, powered by a single external 12V brick. It fits on a shelf, behind a monitor, or in a meter cabinet without a rack, without special cooling, and without dominating the room.
- **Long service life and simple recovery.** With no fans and no spinning disks, the realistic failure modes are the SSD and the power supply — both cheap, both standard parts, both replaceable in minutes. The RAM and SSD are normal SO-DIMM and M.2 components, so the box can be upgraded rather than replaced.
- **Not a general-purpose mini PC.** A Beelink/Minisforum-style mini PC is a fine *compute* node, but as a router it means one NIC, a fan, consumer firmware, and often a Realtek NIC. You would spend the savings on adapters and then fight the driver.
- **Not a Raspberry Pi.** The Pi is ARM, has one built-in NIC, boots from an SD card, and — critically — **OPNsense and pfSense do not run on ARM at all**, they are FreeBSD-based and effectively x86-only. Running a Pi router means accepting a different router OS purely because of the hardware, which is not a good design decision. (The Pi was the original lab router here, which was abandoned because of the high maintenance cost and other drawbacks; see [2_Design_Software_Prerequisites.md — Router & Firewall Software](#router--firewall-software).)
- **Not a consumer router (MikroTik, UniFi, ASUS, etc.).** Dedicated routers are excellent products, but they are closed appliances running the vendor's OS. The whole point of this lab is to run a general-purpose, open-source firewall platform that can be version-controlled and rebuilt from scratch — which requires a general-purpose machine underneath.
- **Not a VM on the hypervisor.** Running the router as a VM on Proxmox puts the router and the path you use to fix the router in the same failure domain: the host goes down, the lab *and* your way in are gone at the same time. A separate physical box keeps the network up independently of the virtualization platform.

### Why New (and Not Refurbished) for the Router

For compute nodes, refurbished is clearly the right call (see [Part 2](#hardware-purchasing-strategy)). For the router, it is the opposite, and the reasons are specific rather than a general preference for new:

- **There is no meaningful refurbished market for these.** They are made in small volumes by Chinese ODMs and sold direct; companies do not buy fleets of them and retire them after three years, so the refurbished supply that makes enterprise mini PCs cheap simply does not exist.
- **New is already cheap.** A multi-port N100 appliance with RAM and an NVMe SSD sits roughly in the €250–€350 band — around the price of a good consumer router, and often less than a comparable branded firewall appliance.
- **It is a single point of failure for the whole lab.** Every device, every VLAN, and the jumphost path all depend on the router. Warranty coverage and a known-good unit are worth far more here than on a compute node you can simply power off and replace.
- **NIC quality is the entire product.** On a refurbished/second-hand unit you cannot verify which NIC controller is actually fitted, and a Realtek-based board that looks identical in photos will quietly cost you throughput and stability. Buying new from the official store means the spec sheet is the spec sheet.
- **Fanless hardware ages through thermal cycling, not through use.** Passive cooling, a long-life power supply, and fresh thermal pads matter on a box that runs at a constant temperature for years.

>**The one thing to verify before ordering:** that the listing photo explicitly shows **four RJ45 ports labelled Intel i226-V 2.5G**. Realtek 2.5GbE ports look identical in a product photo and are the single most common cause of disappointing throughput and link flapping on FreeBSD-based firewalls. If the listing will not confirm the NIC controller in writing, buy a different listing.

### Recommended Router Hardware Specs

**The recommended router specifications (as of 2026; may be different in a later year):**

| Component | Recommended | Why |
|-----------|-------------|-----|
| **Architecture** | **x86-64 only — NOT ARM** | OPNsense and pfSense are FreeBSD-based and have effectively no ARM support. Even where ARM "works" (OpenWrt, VyOS), driver and package coverage is thinner, hardware crypto offload is inconsistent, and you inherit board-specific quirks. x86-64 is the platform every router OS, every plugin, and every guide assumes. |
| **CPU** | Intel **N100** (fine) or **i3-N305** (preferred) | Both are Alder Lake-N, 6–15W, fanless-capable, and include **AES-NI** for hardware-accelerated VPN crypto. N100 is 4 cores and comfortably routes gigabit; the N305 is 8 cores and gives real headroom for IDS/IPS, WireGuard, and a multi-gig WAN later. CPU is the first bottleneck for firewall throughput, so buying one tier up is the cheapest future-proofing there is. |
| **NICs** | **4× Intel i226-V 2.5GbE** (minimum 2, 4 is the sweet spot) | Intel controllers are natively supported by FreeBSD's `igc` driver; Realtek 2.5GbE is the known problem child. Four ports = WAN + LAN trunk + two spare (a second WAN for failover, a dedicated management port, or a direct-attached host). 2.5GbE costs almost nothing extra and removes the gigabit ceiling. |
| **RAM** | **16 GB** DDR4/DDR5 SO-DIMM | 8 GB matches OPNsense's official recommendation and is enough for routing, DHCP, DNS, and VLANs. 16 GB is the honest recommendation once you enable Suricata IDS/IPS, Zenarmor, or keep local reporting data — those are memory-hungry, and N-series boards are **single-channel**, so a second stick buys you nothing; buy one 16 GB stick, not two 8 GB. |
| **Storage** | **256–512 GB NVMe SSD** | OPNsense itself needs very little, but logs, NetFlow data, IDS rule sets and reporting write constantly. NVMe is cheap, fast, and far more write-tolerant than eMMC. **Avoid eMMC-only and SD-card-based configurations** — they wear out under a firewall's write pattern. |
| **Cooling** | **Fanless** | No moving parts, silent, nothing to fail. These CPUs are low enough power that passive cooling is sufficient; just give the case some airflow. |
| **Extras worth having** | Serial/console port, VESA mount, external 12V PSU | A serial console is the recovery path when the network configuration locks you out — the router equivalent of a spare key. |

>**Sizing sanity check:** OPNsense's own documentation lists a ~1.5 GHz multi-core CPU, 8 GB RAM and a 120 GB SSD as the *recommended* specification — the figures above sit comfortably above that, which is deliberate: the official baseline gets the software running, it does not promise 2.5GbE performance with inspection enabled.

### Brand Comparison: Firewall Appliance Vendors

These vendors largely build on the same Intel reference designs, so the differences are in build quality, support, firmware, warranty, and price — not usually in raw performance.

| Brand | Origin / Model | Typical price (4-port N100/N305 class) | Strengths | Weaknesses | Verdict |
|---|---|---|---|---|---|
| **[CWWK](https://cwwk.net/)** (Changwang) | CN ODM, sells direct + AliExpress | ≈€230–€400 | Widest range of firewall/NAS boards, consistent use of Intel i226-V, active BIOS/driver downloads page, responsive support, good reputation in the homelab community | Documentation is thin and translation-quality varies; warranty handling is long-distance | **Best overall value.** The default recommendation for a 4× i226-V N100/N305 box. |
| **[Topton](https://topton.net/)** | CN ODM, primarily AliExpress | ≈€180–€350 | Often the cheapest for the same silicon; very broad model range including 10G SFP+ variants | Model naming is chaotic and listings change constantly; support is less consistent than CWWK; QC is more variable | **Good budget pick** if you read the listing carefully and confirm the NIC controller. |
| **[Qotom](https://qotom.net/)** | CN, established manufacturer since 2011, own website + AliExpress | ≈€200–€450 | Longest track record, genuinely industrial build, strong multi-port and Atom C3000 (Denverton) line-up with SFP+, proper product pages and drivers | Older Atom models are pricier per unit of performance than Alder Lake-N | **Best if you want more ports or SFP+**, or value a manufacturer with a long history. |
| **[Protectli](https://eu.protectli.com/)** | US, "Vault" series, sells direct (incl. EU store) | ≈€350–€650+ | Built specifically for open-source firewalls, **coreboot** support, 2-year warranty (extendable), real Western support, optional pre-installed OPNsense, EU shipping and VAT handled | Substantially more expensive; RAM/SSD options at their store are poor value | **Best if you want warranty and support** and are willing to pay roughly double. |
| **[Deciso (OPNsense DEC series)](https://shop.opnsense.com/product-categorie/hardware-appliances/)** | NL, made by the OPNsense developers | ≈€600–€1,600+ | Official OPNsense hardware, designed and shipped from Europe, first-class support, purchase directly funds the project | Homelab-unrealistic pricing for what is the same job | **Overkill for a homelab** — but the honest choice for a business. |
| **[Netgate](https://www.netgate.com/)** | US, official pfSense hardware | ≈€400–€700+ | Turnkey, pfSense Plus pre-installed, vendor support | Tied to pfSense; not the platform chosen here | Not chosen — see [Router & Firewall Software](#router--firewall-software). |
| **Amazon Rebrands** (ANDAQI, MOGINSOK, SPARKFLY, Ayemlpoi, KingNovyPC, etc.) | Rebadged/rebranded ODM boards, often originally manufactured by companies such as CWWK, Topton, Qotom, or similar OEM/ODM vendors | ≈€250–€600 | Fast delivery, easy EU returns, local consumer protection, Amazon customer support, no customs hassle, often available from local warehouses | Usually the same hardware sold at a markup compared to buying directly from the original manufacturer; firmware, BIOS updates, drivers, and documentation may be harder to obtain because the Amazon brand is often only a reseller and not the actual manufacturer; model specifications are sometimes less transparent; long-term support varies significantly between sellers | **Generally not recommended.** The hardware is often perfectly fine, but in most cases you pay more for essentially the same device available directly from CWWK, Topton, Qotom, or another OEM. Only worth considering if easy returns, local warranty handling, fast delivery, and Amazon buyer protection are more important to you than price and direct manufacturer support. |

**Bottom line:** **CWWK** for the best balance of price, Intel NICs, and support; **Topton** if you want the lowest price and will verify the listing yourself; **Qotom** for more ports or SFP+; **Protectli** if warranty and Western support are worth roughly double the price. All four run OPNsense or pfSense equally well — this is a support-and-trust decision, not a performance one.

> **General important points for choosing the brand & Related points to Chinese hardware in the EU:**
> - **Why are CWWK, Topton, and Qotom so much cheaper than Protectli, Netgate, or Deciso?** In most cases, the difference is not the hardware itself. Modern firewall appliances from CWWK, Topton, and Qotom often use the same Intel CPUs, Intel i226-V NICs, standard SO-DIMM memory, and NVMe SSDs found in more expensive competitors. The lower price comes primarily from their business model: direct-to-consumer sales, lower margins, limited documentation, minimal support, and long-distance warranty handling. By contrast, vendors such as Protectli, Netgate, and Deciso invest heavily in documentation, validation, firmware development (e.g. coreboot support), professional support teams, warranty services, certifications, and software ecosystem development. For a homelab, many of those extras provide limited value, making the Chinese ODM vendors significantly more cost-effective. For business or production use, however, the additional support and warranty coverage can easily justify the higher price.
> - **Buying the above hardware directly from Chinese ODMs is generally safe for homelab use.** These devices are typically standard x86 PCs with off-the-shelf Intel CPUs, Intel NICs, SO-DIMM RAM, NVMe storage, and a normal UEFI firmware. The first thing most users do is wipe the SSD and install their own operating system (e.g. OPNsense or pfSense), removing any preinstalled software. When purchased through the manufacturer's official store, marketplaces such as AliExpress provide buyer protection, VAT is usually handled at checkout, and established vendors such as CWWK, Topton, and Qotom have strong reputations within the homelab community. The primary trade-offs are slower shipping, more complicated warranty handling, and less comprehensive documentation and support compared to vendors such as Protectli, Netgate, or Deciso — not a significantly increased security risk as long as you stick to those reputable brands like CWWK, Topton, etc.

### Where to Buy: AliExpress, Amazon, eBay & Official Stores

> **Important tip before buying:** Always check the specifications and double-check with AI to ensure the hardware meets your performance and connectivity requirements as explained above to avoid buying the wrong device/a device that turns out not to meet your requirements, etc.!

Unlike refurbished compute hardware (where marketplaces are the problem — see [Part 2](#why-not-amazon-aliexpress-or-ebay-for-refurbished-compute)), **new** firewall appliances are mostly sold *direct from the manufacturer* on marketplaces. Here the marketplace is not a reseller risk; it is the payment and dispute layer on top of a factory.

| Channel | How it works | Pros | Cons |
|---|---|---|---|
| **AliExpress** | A Chinese marketplace where manufacturers open their own storefronts. You buy from a *store*, not from AliExpress itself; AliExpress holds the payment, provides Buyer Protection, and arbitrates disputes. EU orders now show **VAT included at checkout**, and most sellers ship DDP (duties handled) — so the checkout price is usually the final price. Delivery is typically 1–3 weeks. | Lowest prices, direct from the manufacturer, strong buyer protection, many photos and reviews from other homelabbers | Slow shipping, returns to China are impractical, listings and store URLs change, many copycat stores |
| **Manufacturer's own website** (e.g. cwwk.com / cwwk.net, qotom.com, protectli.com) | Buy direct from the factory or brand. CWWK offers free worldwide DDP shipping (duties and clearance included). | Often slightly cheaper than AliExpress, full spec pages, BIOS/driver downloads, direct contact for support | Weaker dispute mechanism — you are dealing with the vendor alone, with no third party holding the money |
| **Amazon (.nl/.de)** | Third-party sellers (often rebadgers) ship from EU warehouses. | Fast delivery, easy EU returns, consumer-law protection | 20–50% more expensive for the same board; rebadged brands you cannot go back to for firmware, so generally avoid buying here. |
| **eBay** | Mixed private and business sellers. | Occasional bargains | No quality guarantee, unverifiable sellers — same objection as for refurbished compute. **Avoid.** |

>**For a €250–€400 appliance I would buy from the official store on AliExpress if the price difference versus the manufacturer's own website is less than about €20–€30, purely for the extra buyer protection.** Above that gap, buy direct from the manufacturer.

**Always buy from the official store, never from a reseller.** Resellers list the same board with an inflated price, no BIOS support, and no way to verify which NIC controller is actually fitted. Official stores (e.g. the official Topton store on AliExpress)are the ones the manufacturer links to from their own website, they have multi-year store history, 95%+ positive ratings, and photos matching the official product pages.

**Official stores and links:**

| Brand | Official website | Official marketplace store |
|---|---|---|
| **CWWK** | [cwwk.net](https://cwwk.net/) · [cwwk.com](https://cwwk.com/) | [CWWK PC Store on AliExpress](https://www.aliexpress.com/wholesale?SearchText=CWWK) (search for *CWWK Official Store* / *CWWK PC Store*) |
| **Topton** | — (sells through marketplaces) | [Topton Computer Store on AliExpress](https://nl.aliexpress.com/store/2546008) |
| **Qotom** | [qotom.com](https://www.qotom.com/) · [qotom.net](https://www.qotom.net/) | [Qotom Official Store on AliExpress](https://m.pt.aliexpress.com/store/108231?) |
| **Protectli** | [protectli.com](https://protectli.com/products/) · [eu.protectli.com](https://eu.protectli.com/) (EU store) | Sells direct only |
| **Deciso / OPNsense** | [shop.opnsense.com](https://shop.opnsense.com/) | Sells direct only |

>**How to verify a store is the official one on AliExpress** (store URLs change, redirect per region, or require login, so searching is often more reliable than a saved link):
>1. Search AliExpress for the brand plus the product, e.g. `CWWK N100 firewall` or `Topton N305 firewall`.
>2. Open a listing and click the **store name** to open the store page.
>3. Verify: the store name clearly identifies the brand (e.g. *CWWK Official Store* / *CWWK PC Store*), the rating is **95%+ positive**, the store has been open for **multiple years**, they have sold many products (e.g. 1000+ orders), and the products and photos **match the official website**.
>4. Check the listing text explicitly states the NIC controller (e.g. **Intel i226-V**) — not just "2.5G LAN".

### Managed Switch

A **managed switch** does one essential thing for this lab: 802.1Q VLAN tagging. Without it there is no segmentation, and the whole network design collapses into one flat subnet. Everything else (PoE, layer 3, stacking) is optional.

- **Requirement:** 802.1Q VLAN support, at least 5 ports, a web UI. Gigabit is fine — the router's 2.5GbE ports are for WAN headroom, not for switching between two local hosts.
- **Note:** VLAN tagging is a Layer 2 mechanism, so the switch configuration is identical regardless of the router OS and carries IPv4 and IPv6 together without any dual-stack-specific change.

### Ethernet Cables

Cat6 or better. Buy one long cable for the WAN run and short patch cables for everything else.

- **WAN (ISP modem → router):** 1× 10 m Cat6 — long enough to reach a work room on another floor, through a wall or conduit (or optionally place the router and other hardware in the meter cabinet; assuming you have proper height and ventilation to avoid overheating and fires, etc.).
- **Router → switch and switch → each host:** 1× 0.75 m Cat6A per link — keeps the shelf tidy. 
- **Alternative:** putting the router and switch in the meter cabinet next to the ISP modem means much shorter cables, but worse physical access for maintenance. Keep ventilation in mind and do not obstruct the electrical installation.

---

## Part 2 — Compute / Workload Hardware

This part covers the machines that actually run workloads: Proxmox hosts, VMs, and the Kubernetes cluster. The purchasing logic here is **the opposite of the router**: buy refurbished enterprise hardware, from dedicated refurbishers, not from marketplaces.

### Hardware Purchasing Strategy

#### New vs. Refurbished vs. Second-Hand

| Feature | Brand-New Retail | Professional Refurbished | Private Second-Hand |
|---|---|---|---|
| **Price** | Highest | Up to 60% cheaper with low risk | Cheap, but high risk |
| **Quality Control** | 100% factory-tested | Tested on critical points | No guarantees |
| **Battery / Wear** | 100% capacity / brand-new | Minimum guarantees (e.g. 85%), otherwise replaced | Unknown (often worn out) |
| **Warranty** | Standard 2-year warranty | 1–2 years full refurbisher warranty | "Warranty until the front door" — basically none |
| **Sustainability** | Requires new materials & manufacturing | Very circular (prevents e-waste) | Circular, as long as the device works |

**Verdict:**
- **Brand-new** → Too expensive for a learning lab. Not needed. (The router is the deliberate exception — see [Why New for the Router](#why-new-and-not-refurbished-for-the-router).)
- **Professional refurbished** → Best balance. Enterprise-grade hardware (e.g. Lenovo, Dell, HP) at 40–80% less. These units come from companies replacing their fleets — the hardware is still high quality, power-efficient, and tested. This is the right choice for a home lab focused on learning real-world skills without breaking the bank.
- **Private second-hand** (e.g. Marktplaats, eBay) → Too risky. No proper testing, no guarantees. Avoid.

> **What is "refurbished"?** A previously used device that has been professionally inspected, cleaned, and extensively tested. Only when everything checks out technically is it offered as Refurbished. Not the same as second-hand.

#### Refurbished Shops in Europe

I personally found the best deals and experience with **Refurbed** and **BackMarket** (not sponsored). Both have a wide selection of enterprise-grade mini PCs, good reputation (e.g. been around for some time and trusted by many users), good warranties, and solid customer service, etc.:
- **[Refurbed (primary choice)](https://www.refurbed.nl)** is an EU-wide marketplace with multiple vetted refurbishers. Refurbed enforces strict quality standards on its partners.
- **[BackMarket (secondary choice/alternative)](https://www.backmarket.nl)** is the largest European refurbished marketplace, well-known and reliable. Less strict quality control compared to Refurbed (still good enough), but often cheaper; still a solid option for those looking for good deals on refurbished hardware.

Best for: maximum buyer protection and peace of mind across the EU.

**Other shops considered:**

| Shop | Notes | Verdict |
|---|---|---|
| **ReMarkt** | Dutch refurbisher with physical stores (ex-MediaMarkt). 12-month warranty, in-store testing, Dutch customer service. | Not chosen — limited mini PC selection, Dutch-local only. Refurbed EU is better. |
| **IT-Giant** | Dutch webshop for refurbished business hardware (servers, workstations, mini PCs). Lowest prices for business-grade gear, popular with home-lab builders. | Not chosen — Dutch-local only. Refurbed EU is better. |
| **MediaMarkt / Coolblue** | Mostly brand-new; not ideal for refurbished mini PCs. Useful for switches, cables and accessories (as used above). | Not relevant for compute. |

#### Why Not Amazon, AliExpress or eBay for Refurbished Compute

This is the mirror image of [Part 1](#where-to-buy-aliexpress-amazon-ebay--official-stores), and the reason is simple: **for new hardware you are buying from a manufacturer, for refurbished hardware you are buying from a process.** The marketplace model breaks down when the value of the product is the quality of the inspection that was done to it.

| Channel | Why not for refurbished compute |
|---|---|
| **AliExpress** | Effectively no refurbished enterprise market — these machines were sold to European companies and are retired in Europe. Anything listed as "used" is unverifiable, shipping a 1 kg mini PC from China makes no economic sense, and a return means shipping it back across the world. |
| **Amazon Renewed** | There *is* a warranty, but the grading is done by whichever third-party seller listed it, with no published refurbishment process. Prices are generally higher than dedicated refurbishers for a lower-quality guarantee. |
| **eBay / Marktplaats** | No testing, no grading standard, no warranty, seller risk. You cannot tell a 4-year-old fleet machine from a machine that was pulled because it was failing. |

By contrast, **Refurbed and BackMarket are built around the refurbishment process itself**: vetted partner refurbishers, a published grading system, a minimum 12-month warranty, a 30-day return window, and a marketplace that arbitrates when a unit does not match its grade. For a device that will run 24/7 for years, that process *is* the product. Both are also EU-based, so warranty and returns are covered by EU consumer law and do not involve international shipping.

#### Tip: Ask Your Employer

Companies replace hardware on a fixed cycle — often every 3–5 years, regardless of whether a device still works perfectly. Before spending money on a refurbished shop, it's worth simply asking your manager or IT department whether any old devices are being decommissioned. Many companies are happy to give them away for learning purposes to employees rather than deal with disposal. If not, that is also fine of course — you can always turn to refurbished shops or other sources.

> **Important:** Before using any company device for personal purposes, make sure you have explicit permission from your manager or IT department. Do not assume it is allowed — company hardware is company property until formally decommissioned and released.
>
> Once you have a device: **ensure all company data has been fully wiped and the device has been factory reset or re-imaged before use.** This protects both you and your employer. A full disk wipe (e.g. `shred`, `dd`, or a secure erase tool) or reinstalling the OS from scratch is the safest approach, your IT department can provide guidance on the best method to ensure data security and compliance.

#### What to Check When Buying Refurbished

- **Certification**: Look for *Keurmerk Refurbished* (NL) or an equivalent quality label.
- **Refurb process**: Check that the seller lists their full refurbishment process and read it carefully.
- **Battery health**: Aim for 80%+ capacity, or a replaced battery.
- **Warranty length**: Minimum 12 months recommended.
- **Return policy**: 14–30 days is standard for reputable sellers.
- **Condition grading**: "Like New" vs. "Very Good" can mean big price differences — read the grading definitions carefully.

### Hardware Type Selection

#### Comparison: Main Compute Options

| Category | CPU Power | RAM | Storage | Noise | Power Usage | Virtualization | Cost | Best Use Case |
|---|---|---|---|---|---|---|---|---|
| **Raspberry Pi** | Low | 1–8 GB | SD / USB SSD | Silent | Very low (5–10W) | Limited (ARM) | €50–€150 | Lightweight services, learning Linux |
| **Mini PC** | Medium to high | 8–64 GB | NVMe SSD (most common) | Silent / very quiet | Low (10–40W) | Excellent | €150–€600 | Proxmox, Docker, Kubernetes, CI/CD |
| **Laptop** | Medium | 8–32 GB | NVMe SSD | Quiet | Low–medium (10–60W) | Good | €200–€600 | Portable DevOps work, Docker, k3s |
| **Server / Workstation** | Very high | 32–256 GB | RAID SSD/HDD | Very loud (even at idle — ever been in a data centre? That constant hum comes from these machines) | Very high (100–300W) | Enterprise-grade | €300–€800 | Production workloads (overkill for home labs) |

> A great DevOps home lab focuses on **production-like architecture, not production-grade hardware**. You don't need enterprise servers (very harmful for your wallet and your ears) — but you do need reproducibility, automation, observability, and failure testing, etc.

#### Why Mini PCs

- **Strong virtualization performance** — desktop-class CPUs (e.g. Intel i5/i7) handle Proxmox, Docker, and Kubernetes easily.
- **High RAM capacity** — up to 64 GB, which is good for running multiple VMs.
- **Silent operation** — can run 24/7 without fan noise (or minimal noise).
- **Low power usage** — typically 10–40W, far cheaper to run than servers.
- **Affordable** — €150–€400 per refurbished node for strong performance.
- **Compact size** — easy to stack for a small cluster.
- **Reliable business-grade hardware** — built for corporate environments, long lifespan (e.g. Dell, Lenovo, etc., see [Why Enterprise-Grade Hardware?](#why-enterprise-grade-eg-dell-lenovo-hp)).
- **Easy to upgrade** — RAM and NVMe SSD upgrades are simple.
- **Perfect for clustering** — ideal for a multi-node Proxmox or Kubernetes cluster.

#### Why Enterprise-Grade (e.g. Dell, Lenovo, HP)

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

#### Why NOT Raspberry Pi

> **Scope note:** This section explains why Raspberry Pi is not the preferred choice for this home lab's computing nodes. For lightweight tasks like basic network services or low-power experiments it can still be viable — but note that it is **not** viable as the lab router either, for the reasons in [Why a Firewall/Router Appliance Mini PC](#why-a-firewallrouter-appliance-mini-pc).

Mini PCs give more value for money because they are **complete computers**: a proper x86 CPU, upgradeable RAM, fast NVMe SSD storage, active cooling, a stable power supply, and reliable networking all in one device. They're designed to run 24/7 under load and handle workloads more consistently.

Raspberry Pi boards are bare single-board computers — you still need to add a case, cooling, storage, and sometimes extra networking gear. They also use weaker ARM hardware and rely on microSD cards or add-on storage, which is slower and less reliable. Even though the Pi itself is cheaper, you end up with less performance, less reliability, and less convenience — and it costs more in total than expected once you add all the accessories.

More importantly, the Pi uses ARM/Pi OS instead of x86/Ubuntu or RHEL — which is what you find in real enterprise environments. Mini PCs give a more realistic learning experience that better matches production.

### Node Setup

#### How Many Nodes

**It depends on your situation — 1 node can be more than enough.** If your goal is learning Kubernetes, Docker, Ansible, and monitoring, a single well-specced mini PC handles all of that comfortably. If you are not even filling one node with workloads, buying more nodes just to "have a cluster" is not worth the purchase and energy cost. Add a second node only when you actually need more capacity — and anything beyond 1–2 nodes is only worth it if you intend to host a lot (a full home cloud replacing Netflix, OneDrive, etc.), which is not the goal of this lab (see [Goals](0_Goals.md)).
- **Prioritise fewer, more powerful node(s).** The biggest factor in energy cost is the **number of physical machines**, not how much RAM is in each one. RAM uses very little power compared to the CPU, motherboard, SSDs, and PSU losses — so one node with 64 GB uses roughly the same power as one node with 16 GB, while four 16 GB nodes use roughly 4× the power of one 64 GB node. At ~20W per node and ~€0.30/kWh (NL, 2026):

  | Setup | Total RAM | Typical Power | Est. Yearly Cost |
  |-------|-----------|---------------|------------------|
  | 1 × 64 GB | 64 GB | ~20 W | ~€53 |
  | 2 × 32 GB | 64 GB | ~40 W | ~€105 |
  | 4 × 16 GB | 64 GB | ~80 W | ~€210 |

  Same total RAM, but cost roughly doubles with each doubling of nodes — plus extra purchases, cables, maintenance, and points of failure. In learning value, one well-specced node already covers ~85–90% of DevOps learning; a second adds clustering, migration and multi-node Kubernetes (~95%); three or more add HA, Ceph and quorum — useful, but increasingly niche for a home lab. To practise clustering without buying hardware, temporarily add a machine you already own, spin up 3 VMs on one host to simulate a multi-node cluster (you can still drop a VM to test failover and quorum loss), or practise in a test environment at work where large-scale setups already exist.
- **Quorum, in short.** Quorum means a **majority of voting members agree** the cluster is healthy. That majority is required to elect a leader, commit configuration changes, and confirm writes. Without it the cluster stops making decisions and becomes unavailable — which is the point: it prevents **split-brain**, where two halves both think they are in charge and make conflicting changes.
- **Why odd numbers of voting members.** It is not that HA *requires* an odd total node count — what matters is an **odd number of voting members**, because majority is always `floor(n/2) + 1`:

  | Voting Nodes | Majority Needed | Failures Tolerated |
  |:---:|:---:|:---:|
  | 2 | 2 | 0 |
  | **3** | **2** | **1** |
  | 4 | 3 | 1 |
  | **5** | **3** | **2** |
  | 6 | 4 | 2 |
  | **7** | **4** | **3** |

  **3 and 4 nodes both tolerate only 1 failure** — the 4th node raises the total *and* the consensus bar, and the two cancel out. Only odd increments (3 → 5, 5 → 7) actually buy fault tolerance. With 2 voting nodes, majority = 2, so losing one takes the cluster down even though a machine is still running; with 3, the surviving 2 still form a majority.
- **Where quorum applies.** It applies to **consensus/voting members**, not to every node. In Proxmox, quorum spans all cluster nodes — with 3, losing 1 still leaves a majority and the cluster can fence the failed node. In Kubernetes it applies to the **etcd** cluster (the store for all cluster state) via the **Raft** consensus algorithm, not to worker nodes — typical setups are 1 control-plane node (not HA), 3 (HA, most common), or 5. The same principle holds for ZooKeeper, Consul, and databases with leader election.
- **Common misconception: "HA requires an odd number of nodes."** More accurately: **HA systems using majority-based consensus work most efficiently with an odd number of voting members.** Worker nodes never vote, so an even total (e.g. 3 control-plane + 20 workers) is perfectly fine.
- **When this actually matters.** In **production**, 3 voting members is the recommended minimum. In a **home lab** it is not a hard requirement — running 3 nodes to mimic production while not even filling one is not worth the cost. One well-specced node is a perfectly valid home lab.

#### Recommended Node Composition

- **1 refurbished enterprise-grade mini PC** — your main compute node, providing real-world hardware experience (e.g. Lenovo ThinkCentre Tiny, Dell OptiPlex Micro, HP EliteDesk Mini, etc.). A single well-specced node is enough for learning and running smaller workloads.
- **Optionally a 2nd mini PC or an old laptop you already have** — if you want more capacity or want to experiment with workload distribution. Only worth it if you're actually using the resources on the first node.

#### Recommended Specs per Node

| Component | Recommended | Notes |
|-----------|-------------|-------|
| **CPU** | 4+ cores Intel N-series or 12th-gen Core i5 — full VT-x and VT-d support | Enough to run Proxmox + multiple VMs simultaneously without contention. |
| **RAM** | 32–64 GB | 32 GB is comfortable for running Proxmox with several VMs. 64 GB gives plenty of headroom and is often more power-efficient than running two separate 32 GB nodes (if you need 64 GB RAM total; if you only need 32 GB RAM then you do not need the 64 GB RAM of course) — one well-specced machine uses less energy than two underpowered ones (see [How Many Nodes](#how-many-nodes)). |
| **Storage** | NVMe SSD | Significantly faster than SATA SSD (3–7 GB/s vs ~550 MB/s) and far faster than HDD. Matters for VM boot times, live migration, snapshot I/O, and running multiple VMs in parallel. Most enterprise-grade mini PCs ship with an M.2 slot, making NVMe a natural fit — no cables, no adapters, compact form factor. |

See for how to check hardware specs [reference/os_hardware/Hardware_Specs.md](../../../reference/os_hardware/Hardware_Specs.md#how-to-check-your-hardware-specs).

**Storage sizing — intentional asymmetry:**

Not all nodes need the same storage size. A good approach is:
- **1× larger drive (e.g. 512 GB-1 TB)** on one node — acts as a "shock absorber": migration staging area, ISO storage, snapshots, and local VM disks when you need fast temporary storage, etc.
- **Smaller drives (e.g. 256 GB-512 GB)** on the other compute nodes — sufficient for the OS, Proxmox, and their resident VMs, etc.

This asymmetry is intentional: the larger node handles temporary bulk workloads so the compute nodes stay lean and focused.

#### Start Small, Expand Later

**Start with 1 mini PC or 1 old laptop** and expand later if needed. You can learn all the fundamentals — Kubernetes, Docker, Ansible, monitoring — on a single well-specced node. Only add a second node when you're actually running out of resources on the first one.

If you want to practice clustering or quorum without buying extra hardware, see [How Many Nodes](#how-many-nodes) above — in short you can temporarily add a 3rd node (e.g. an old laptop you already have), use at least 3 VMs to simulate a multi-node cluster, or practice through your work environment if you have access to a larger setup.

That's how I started: my old Acer laptop. Later I expanded to the full setup described in [Current Personal Setup](#current-personal-setup).

---

## Software

All software decisions — the router/firewall OS, hypervisor, node and VM operating systems, container orchestration, IaC, configuration management, GitOps/CI, secrets, observability, and backup — live in their own central document: **[Design: Software & Prerequisites](3_Design_Software_Prerequisites.md)**.

The two documents are deliberately symmetrical: this one is the single source of truth for *what hardware is bought*, that one is the single source of truth for *what software runs on it*. Where a choice on one side constrains the other, it is noted explicitly in both (for example, the router appliance is x86-64 with Intel NICs **because** the chosen router OS requires it, and node RAM is sized **because** of what the hypervisor and cluster have to fit into).

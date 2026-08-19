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
    - [Prioritise Fewer, More Powerful Nodes](#prioritise-fewer-more-powerful-nodes)
    - [Quorum Explained](#quorum-explained)
    - [Why Odd Numbers of Voting Members?](#why-odd-numbers-of-voting-members)
    - [Where Does Quorum Apply?](#where-does-quorum-apply)
    - [When Does This Matter?](#when-does-this-matter)
  - [Recommended Node Composition](#recommended-node-composition)
  - [Start Small, Expand Later](#start-small-expand-later)
  - [Current Personal Setup](#current-personal-setup)
- [Next Step: Local Environment Setup](#next-step-local-environment-setup)

---

## Goals

This is a reference section — the full goal is described in the [Home Lab README](../README.md#personal-goal). In short:

- **Goal:** Learn DevOps fundamentals (Kubernetes, networking, Linux, monitoring, automation) through hands-on experimentation — because it's fun and directly relevant to daily engineering work.
- **What I am not:** I'm a DevOps Engineer, not a hardware, network, or storage specialist. This lab broadens my knowledge in those areas but doesn't aim for deep specialist mastery.
- **What this lab is not:** Not a self-hosting / home data centre project. Not production, not an obligation. No 24/7 uptime required, no self-hosted cloud replacements, no advanced hardware tinkering. If it breaks, nothing in the house stops working. The hardware choices below are driven by this: affordable, real-world-grade, and sufficient for a small homelab.

See further details in the [Home Lab README](../README.md#what-this-is-not) and [Home Lab Design](../README.md#home-lab-design).

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
| **Mini PC** | Medium to high | 8–64 GB | NVMe SSD (most common) | Silent / very quiet | Low (10–40W) | Excellent | €150–€600 | Proxmox, Docker, Kubernetes, CI/CD |
| **Laptop** | Medium | 8–32 GB | NVMe SSD | Quiet | Low–medium (10–60W) | Good | €200–€600 | Portable DevOps work, Docker, k3s |
| **Server / Workstation** | Very high | 32–256 GB | RAID SSD/HDD | Very loud (even at idle — ever been in a data centre? That constant hum comes from these machines) | Very high (100–300W) | Enterprise-grade | €300–€800 | Production workloads (overkill for home labs) |

> A great DevOps home lab focuses on **production-like architecture, not production-grade hardware**. You don't need enterprise servers (very harmful for your wallet and your ears) — but you do need reproducibility, automation, observability, and failure testing, etc.

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

**It depends on your situation — 1 node can be more than enough.** The number of nodes you need depends entirely on what you want to run and what your goals are. If your goal is learning Kubernetes, Docker, Ansible, and monitoring, a single well-specced mini PC can handle all of that comfortably. If you're not even filling one node with workloads, buying more nodes just to "have a cluster" is not worth the energy cost and purchasing cost.

You might want to add a second node if you want more compute capacity or redundancy for your workloads — but that's optional, not required.

You do not need more nodes than that unless you want to host many workloads (e.g. your entire home cloud replacing Netflix, cloud storage like OneDrive, etc.) — but that is not the goal of this lab (see [Goals](#goals)). If you're using the lab for learning and/or hosting smaller workloads like small home automations, 1–2 nodes is more than enough.

#### Prioritise Fewer, More Powerful Node(s)

The biggest factor in energy cost is the **number of physical machines**, not how much RAM is in each one. RAM itself uses very little power compared to the CPU, motherboard, SSDs, and PSU losses. One node with 64 GB RAM uses roughly the same power as one node with 16 GB RAM — but four 16 GB nodes use roughly 4× the power of one 64 GB node.

Using realistic numbers for modern business mini PCs (ThinkCentre Tiny, OptiPlex Micro, EliteDesk Mini) at typical homelab load (e.g. ~20W per node) and Dutch electricity prices (e.g. ~€0.30/kWh in 2026), the yearly cost of running a cluster of nodes looks like this:

| Setup | Total RAM | Typical Power | Est. Yearly Cost |
|-------|-----------|---------------|------------------|
| 1 × 64 GB | 64 GB | ~20 W | ~€53 |
| 2 × 32 GB | 64 GB | ~40 W | ~€105 |
| 4 × 16 GB | 64 GB | ~80 W | ~€210 |

Same total RAM — but power and cost roughly double with each doubling of nodes. On top of the energy cost, each additional node also means an additional purchase, more cables, more maintenance, and more points of failure.

In terms of learning value, one well-specced node already covers ~85–90% of DevOps learning (Proxmox, Docker, Kubernetes, Terraform, Ansible, monitoring). A second node adds clustering, VM migration, and multi-node Kubernetes (~95%). Three or more nodes add HA, Ceph, and quorum — useful, but increasingly niche for a home lab.

**Bottom line:** prioritise one powerful node over multiple smaller ones. It's cheaper to buy, cheaper to run, and covers nearly all the learning value. You can add a second node if you want (e.g. an old laptop you already have) — but don't feel obligated to buy more nodes just to "have a cluster." One node is enough for most learning goals.

> **What about clustering and quorum?** In production environments, you need at least 3 nodes for high availability through quorum (see [Quorum Explained](#quorum-explained) below). But this is a home lab — not production. If you want to practice clustering, you can temporarily add a 3rd node (e.g. an old laptop you already have) just for experimenting. It doesn't need to run 24/7 — only when you're testing clustering. You can also practice clustering with VMs on a single host or small numbers of hosts — spin up 3 VMs to simulate a multi-node cluster. It's not real physical separation, but it does simulate the clustering behaviour (e.g. you can drop a VM to test failover, practice quorum loss, etc.). Another option is to practice through your work environment (in a test environment of course!) where you likely have a large scale setups and resources (e.g. multiple notes, data centers, etc.), etc.

#### Quorum Explained

Quorum means a **majority of voting members agree** the cluster is healthy. This majority is required for critical operations: electing a leader, committing configuration changes, and confirming writes. Without a majority, the cluster cannot make decisions and becomes unavailable — this prevents **split-brain**, where two halves of a cluster both think they're in charge and start making conflicting changes.

#### Why Odd Numbers of Voting Members?

It's not that HA *requires* an odd total node count — what matters is an **odd number of voting/quorum members**. The reason is simple math: even numbers waste a node without improving fault tolerance.

| Voting Nodes | Majority Needed | Failures Tolerated |
|:---:|:---:|:---:|
| 2 | 2 | 0 |
| **3** | **2** | **1** |
| 4 | 3 | 1 |
| **5** | **3** | **2** |
| 6 | 4 | 2 |
| **7** | **4** | **3** |

Notice: **3 nodes and 4 nodes both tolerate only 1 failure.** The 4th node adds cost and power usage but zero extra fault tolerance. The same applies to 5 vs. 6, and so on. That's why architects prefer odd numbers of voters.

**Why does adding the 4th node not help?** Because majority is always `floor(n/2) + 1`. With 3 nodes, majority = 2, so you can lose 1 (3 − 2 = 1). With 4 nodes, majority jumps to 3, so you can still only lose 1 (4 − 3 = 1). The extra node raises both the total *and* the bar for consensus — the two cancel out. Every even node you add gets "absorbed" by the higher majority requirement. Only adding an odd node (3 → 5, 5 → 7) actually increases fault tolerance, because the majority threshold stays the same while the total grows.

**Example — 2 nodes (no HA):**
With 2 voting nodes, majority = 2. If one fails, only 1 vote remains — no majority, so the cluster goes down even though a node is still running.

**Example — 3 nodes (HA):**
With 3 voting nodes, majority = 2. If one fails, the remaining 2 still form a majority — the cluster stays operational.

#### Where Does Quorum Apply?

Quorum applies to **consensus/voting members**, not to every node in a system:

- **Proxmox** — quorum is managed across all cluster nodes. With 3 nodes, losing 1 still leaves a majority, so the cluster stays operational and can fence the failed node.
- **Kubernetes** — quorum applies to the **etcd cluster** (the backing store for all cluster state), not to worker nodes. etcd uses the **Raft consensus algorithm**, which requires a majority to elect a leader and commit writes. Typical setups: 1 control-plane node (not HA), 3 (HA, most common), or 5 (larger HA).
- **Other distributed systems** — the same principle applies to ZooKeeper, Consul, database replicas with leader election, and any system using majority-based consensus.

**Worker nodes are different.** They do not participate in quorum decisions. You can have 2, 4, 10, or 100 worker nodes — the odd-number recommendation applies only to quorum/consensus members.

> **Common misconception:** "HA requires an odd number of nodes." More accurately: **HA systems that use majority-based consensus work most efficiently with an odd number of voting members.** You can absolutely have an even total node count (e.g. 3 control-plane nodes + 20 worker nodes = 23 total) — what matters is the voter count.

#### When Does This Matter?

In **production**, quorum is essential — you need at least 3 voting members for high availability. If you're building a production cluster, 3 nodes is the recommended minimum.

But for a **home lab** focused on learning and experimentation, quorum is not a hard requirement. Tailor the number of nodes to your situation and your goals. If you're running 3 nodes just to mimic production but you're not even filling 1 or 2 nodes with workloads, it's not worth the extra energy and purchasing cost. Just do whatever fits your goals — 1 well-specced node is a perfectly valid home lab.

### Recommended Node Composition

- **1 refurbished enterprise-grade mini PC** — your main compute node, providing real-world hardware experience (e.g. Lenovo ThinkCentre Tiny, Dell OptiPlex Micro, HP EliteDesk Mini, etc.). A single well-specced node is enough for learning and running smaller workloads.
- **Optionally a 2nd mini PC or an old laptop you already have** — if you want more capacity or want to experiment with workload distribution. Only worth it if you're actually using the resources on the first node.

### Recommended Specs per Node

| Component | Recommended | Notes |
|-----------|-------------|-------|
| **CPU** | 4+ cores Intel N-series or 12th-gen Core i5 — full VT-x and VT-d support | Enough to run Proxmox + multiple VMs simultaneously without contention. |
| **RAM** | 32–64 GB | 32 GB is comfortable for running Proxmox with several VMs. 64 GB gives plenty of headroom and is often more power-efficient than running two separate 32 GB nodes (if you need 64 GB RAM total) — one well-specced machine uses less energy than two underpowered ones (see [Prioritise Fewer, More Powerful Node(s)](#prioritise-fewer-more-powerful-nodes)). |
| **Storage** | NVMe SSD | Significantly faster than SATA SSD (3–7 GB/s vs ~550 MB/s) and far faster than HDD. Matters for VM boot times, live migration, snapshot I/O, and running multiple VMs in parallel. Most enterprise-grade mini PCs ship with an M.2 slot, making NVMe a natural fit — no cables, no adapters, compact form factor. |

**Storage sizing — intentional asymmetry:**

Not all nodes need the same storage size. A good approach is:
- **1× larger drive (e.g. 512 GB-1 TB)** on one node — acts as a "shock absorber": migration staging area, ISO storage, snapshots, and local VM disks when you need fast temporary storage, etc.
- **Smaller drives (e.g. 256 GB-512 GB)** on the other compute nodes — sufficient for the OS, Proxmox, and their resident VMs, etc.

This asymmetry is intentional: the larger node handles temporary bulk workloads so the compute nodes stay lean and focused.

### Start Small, Expand Later

**Start with 1 mini PC or 1 old laptop** and expand later if needed. You can learn all the fundamentals — Kubernetes, Docker, Ansible, monitoring — on a single well-specced node. Only add a second node when you're actually running out of resources on the first one.

If you want to practice clustering or quorum without buying extra hardware, see [How Many Nodes](#how-many-nodes) above — in short you can temporarily add a 3rd node (e.g. an old laptop you already have), use at least 3 VMs to simulate a multi-node cluster, or practice through your work environment if you have access to a larger setup.

That's how I started: my old Acer laptop. Later I expanded to the full setup described in [Current Personal Setup](#current-personal-setup).

### Current Personal Setup
My current home lab setup consists of:

| Role | Device | CPU | RAM | Storage | Source | Why chosen |
|------|--------|-----|-----|---------|--------|------------|
| Compute node 1 | Dell OptiPlex 7050 Micro | Intel Core i5-7500T (3.2 GHz, TODO: cores and threads per core) | TODO: 32 or 64 GB | TODO: 512 GB or 1 TB SSD | BackMarket (refurbished), bought for €TODO: what did I buy them for eventually in 2026 | Enterprise-grade reliability, silent, low power (≈15W), VT-x/VT-d for virtualization, widely available refurbished at a good price (see [Why Enterprise-Grade](#why-enterprise-grade-eg-dell-lenovo-hp)). |
| Compute node 2 | Old personal Acer laptop (Acer Aspire A715-75G) | Intel Core i7-9750H (2.60 GHz, 6 cores, 2 threads per core) | 16 GB | 512 GB SSD | Personal (repurposed), bought in 2020 on Coolblue for about €600 | Already on hand — repurposed to add a second physical host to experiment with, without extra purchasing cost. |

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

---

## Next Step: Local Environment Setup

Once you've determined your goals and purchased your hardware, the first step is to set up the local development environment on your laptop (the Ansible controller). This is a one-time setup that generates an SSH key, installs dependencies, generates the inventory, and configures the Ansible Vault for secrets management.

### Prerequisites

- **Python 3** — required to run Ansible (comes pre-installed on most Linux distributions and macOS; on Windows use WSL)
- **Git** — to clone this repository

## Step 1: Generate an SSH Key Pair

Ansible connects to remote hosts via SSH. You need an Ed25519 key pair on your laptop — this is used for all homelab hosts (the Pi, future VMs, etc.). Generate it once and reuse it everywhere.

```bash
# Generate a new Ed25519 key (modern, compact, fast; recommended over RSA):
ssh-keygen -t ed25519 -C "your-email@example.com"
# Save with appropriate name (e.g., ~/.ssh/id_homelab).
# NOTE: you cannot use "~" in the path prompt — type the full path, e.g. /home/youruser/.ssh/id_homelab
# Enter a passphrase (strongly recommended — protects the key if your laptop is stolen).
#
# This creates two files:
#   ~/.ssh/id_homelab       — private key (NEVER share this)
#   ~/.ssh/id_homelab.pub   — public key  (safe to share; goes on remote hosts)
#
# Make sure to save these files and the passphrase securely (e.g., in a password manager
# like KeePassXC). If you lose the private key, you lose SSH access to all hosts.
```

This key is referenced in `ansible.cfg` as `private_key_file = ~/.ssh/id_homelab` and stored in the Ansible Vault as `vault_ssh_private_key_src_ansibleremote` so the `users` role can deploy the public key to remote hosts.

## Step 2: Install Ansible and Run Setup Playbook

```bash
# Go to the Ansible directory:
cd homelab/ansible

# Create a Python virtual environment and install Ansible:
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install ansible
ansible --version

# Run the local environment setup playbook. See details in the playbook itself, it describes what it does exactly.
# Safe to re-run — skips steps that are already done.
# --diff: show file changes made on the host
ansible-playbook setup_local_env.yml --diff
```

After this completes, your environment is ready to run playbooks. See the setup playbook itself (`ansible/setup_local_env.yml`) for full details on what each step does, and `ansible/vars/setup_local_env.yml` for how to add new hosts or vault secrets.
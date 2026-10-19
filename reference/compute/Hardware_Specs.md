# Compute Hardware Fundamentals

Computer performance and suitability depend on the complete system, not a single processor label. Start from the workload and understand the role of each component; then compare specific models and measured behavior.

---

## Table of Contents

- [Core Components](#core-components)
- [What to Compare](#what-to-compare)
- [How to Check Your Hardware Specs](#how-to-check-your-hardware-specs)

---

## Core Components

| Component | What it does | What matters when assessing a system |
|---|---|---|
| CPU (processor) | Executes instructions and schedules work across cores and hardware threads. | Architecture/instruction set, generation, core/thread count, sustained performance, cache, virtualization support, and power/thermal limits. More cores do not automatically make a system faster for a serial workload. |
| RAM (memory) | Holds code and data that active processes need quickly; it is volatile and normally cleared when power is lost. | Capacity for the workload, available headroom, memory channels/bandwidth, compatibility, and whether it is upgradeable. Insufficient RAM can cause paging/swapping and severe slowdowns. |
| Storage | Retains the OS, applications and data when the system is powered off. | Capacity, latency, throughput, random I/O, endurance, health and interface. SSDs are generally faster for random workloads; HDDs often cost less per unit of capacity. Neither storage type replaces a backup. |
| GPU (graphics processor) | Accelerates graphics and, where supported, parallel compute workloads. | Integrated versus discrete design, memory, supported software/driver stack, power, cooling, and whether the workload actually uses it. |
| Network interface | Connects the computer to local or external networks. | Wired/wireless capability, link speed, port count, driver/firmware support, and whether network paths or offloads match the workload. Advertised link speed is not the same as application throughput. |
| Motherboard, firmware and buses | Connect components and expose configuration, boot and device-management capabilities. | Memory/storage limits, expansion slots, I/O ports, firmware updates, boot options, virtualization/IOMMU features and hardware compatibility. |
| Power and cooling | Supplies stable power and removes heat so components can sustain operation. | Whole-system draw at idle and under real work, adapter/PSU quality, airflow, noise, thermal throttling and safe operating environment. Component TDP is not a measurement of wall power. |

---

## What to Compare

Read the complete specification and check upgradeability and support rather than relying on a product-family name or one headline number. Two systems with the same CPU model can behave differently because of cooling, memory configuration, firmware settings and power limits. A higher theoretical maximum does not guarantee higher sustained performance.

Match resources to the workload: interactive tasks may value per-core responsiveness; parallel builds can use more cores; virtualization needs adequate memory and storage I/O; graphics or machine-learning workloads may depend on a supported GPU. Leave headroom for operating-system overhead and concurrent work. Measure electricity and thermals if those affect the decision.

Use the [DevHub scope and tool-specificity guidance](../README.md#scope-and-tool-specificity): this page explains component fundamentals, not a catalogue of every vendor model or benchmark. Consult manufacturers' official specifications for exact product limits and use the following commands as an initial inventory, not a substitute for model-specific documentation.

---

## How to Check Your Hardware Specs

**On Linux**:

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

**On Windows**:

```powershell
# CPU name, cores, and logical processors
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors

# RAM total (in GB)
(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB

# Storage disks
Get-PhysicalDisk | Select-Object FriendlyName, Size, MediaType
```

Alternatively, on Windows you can open **Task Manager → Performance** for a quick visual overview of CPU cores/threads, RAM, and disk.

---

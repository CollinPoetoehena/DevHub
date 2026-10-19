# Storage Architecture

Storage design starts with the data and its recovery requirements, not a preferred filesystem or appliance. Identify what is irreplaceable, how much loss is acceptable, how quickly it must return, who needs access, and what can be rebuilt. The same device can contain several data classes with different protection needs.

---

## Table of Contents

- [Primary Storage Choices](#primary-storage-choices)
- [Availability Is Not Backup](#availability-is-not-backup)
- [Backup Design and 3-2-1](#backup-design-and-3-2-1)
- [Choose the Simplest Sufficient Design](#choose-the-simplest-sufficient-design)

---

## Primary Storage Choices

| Storage type | Typical strengths | Main trade-offs | Suitable when |
|---|---|---|---|
| Direct-attached SSD | Low latency, strong random I/O, silent operation, compact physical design | Capacity costs more than HDD; normally tied to one host; host or device loss can interrupt access | OS, VM/container disks, databases and frequently used working data |
| Direct-attached HDD | Low cost per capacity and useful for large sequential data | Slower random I/O, mechanical wear/noise, and a direct host/device dependency | Bulk data, archives, and backup targets where latency is less important |
| USB external HDD/SSD | Simple, portable, can be disconnected between backup runs | Cable/enclosure/power can fail; sharing and automation are limited; portable media can be lost | A small independent local backup or offline rotation without another server |
| NAS / network file service | Shared file access over protocols such as NFS or SMB; storage can outlive an individual workload | Another host/appliance, network, access-control and update lifecycle; shared service may become a dependency | Multiple clients genuinely need shared files or supported shared storage |
| Network block storage | Remote block devices for consumers designed for them | Requires careful ownership, locking, path and failure handling; a filesystem is not automatically safe for concurrent writers | A specific hypervisor/application architecture supports the chosen target |
| Distributed storage | Places/replicates data across nodes and can maintain service through designed failures | Requires independent failure domains, network capacity, spare usable capacity, quorum and ongoing repair work | Availability or learning goals specifically require distributed placement and there is enough hardware to support it |
| Cloud/object storage | Off-site capacity, API access and geographic separation | Recurring/egress costs, connectivity, provider/API dependence, privacy and key-management duties | Off-site recovery, archive, or a supported application workflow justifies the service |

An SSD is a medium, not a backup policy. A NAS is a computer/service that may itself contain SSDs or HDDs; RAID is one way to arrange devices inside a system; neither the enclosure nor the RAID layout creates an independent backup automatically. Select capacity and endurance from expected workload and retention, and check device health and replacement availability.

Network file access and block access have different semantics. NFS/SMB normally expose files to clients; iSCSI and similar protocols expose blocks whose filesystem ownership must be controlled. Confirm client compatibility, locking, access modes, permissions, throughput and failure recovery before choosing based on protocol familiarity.

---

## Availability Is Not Backup

RAID, mirrors and replicas can improve access when a device fails, but they may reproduce accidental deletion, corruption, malware or administrative mistakes. A snapshot can speed rollback but often shares the same system, power, credentials and location. Replication can protect against some hardware loss while copying bad changes just as efficiently.

Backups are separate recoverable copies with a known scope, retention policy, access path and restoration procedure. Protect configuration, encryption keys and application consistency as well as data blocks. A successful job log or a directory full of backup files does not prove the service or data can be restored.

---

## Backup Design and 3-2-1

The common 3-2-1 guideline means retaining at least three copies of important data, on two kinds of media, with one copy off-site. Treat it as a prompt to cover independent failure modes, not as a certification badge. Adapt it to the value of the data and the cost and risk the owner accepts.

Define recovery point objective (RPO) as the maximum acceptable data-loss interval and recovery time objective (RTO) as the acceptable time to restore service. Then decide:

1. Which datasets are backed up, and how often their change rate requires a new recovery point.
2. Where each copy lives and which power, host, account, administrator and physical site it shares.
3. Whether routine credentials can delete every copy; consider offline or retention-protected copies.
4. How encryption keys and service dependencies are recovered if the primary system is unavailable.
5. Which representative applications/data are restored, how often, and how results are recorded.

Use application-aware exports or quiescing for databases and other stateful services. For virtual machines, check guest-consistency support, not only hypervisor snapshot completion. Keep retention long enough to reach a known-good version and budget capacity for the actual change rate rather than assuming an optimistic deduplication ratio.

---

## Choose the Simplest Sufficient Design

Start with a clear primary-data location and a backup that is independent enough for the risk being addressed. Add a second offline/off-site copy if the data matters enough to justify it. Add a NAS for shared-access requirements; add distributed storage for demonstrated placement/availability requirements and adequate failure domains. Do not buy those systems just because a diagram includes them.

The homelab [storage](https://github.com/CollinPoetoehena/devhub-homelab/blob/main/docs/02-architecture/storage.md) and [backups](https://github.com/CollinPoetoehena/devhub-homelab/blob/main/docs/06-operations/backups.md) chapters apply these principles to small labs, including low-cost local-disk and external-drive options. Its discussion is not a substitute for professional requirements in a business or regulated environment.

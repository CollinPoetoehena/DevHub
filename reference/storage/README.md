# Storage Reference

This reference explains storage concepts and architecture independently of any one homelab or application. Use it to understand the media, protocols, and failure models behind a design; the homelab guides apply those ideas to small-scale purchasing and recovery decisions.

---

## Table of Contents

- [Architecture and Data Protection](#architecture-and-data-protection)
- [Linux Storage Background and Commands](#linux-storage-background-and-commands)
- [Kubernetes-Specific Exception](#kubernetes-specific-exception)

---

## Architecture and Data Protection

[Storage Architecture](./Storage_Architecture.md) explains how to choose between direct-attached storage, network file/block storage, and distributed storage; how to separate primary data from recovery copies; and how to reason about RAID, replication, snapshots, and the 3-2-1 rule.

---

## Linux Storage Background and Commands

[Storage Background & Commands](./Storage_Background_Commands.md) retains the Linux block-device, partition, filesystem, mount, LVM, RAID and NFS explanations alongside practical inspection and management commands.

---

## Kubernetes-Specific Exception

Kubernetes is a broad platform with its own APIs, drivers, and version-dependent behavior, so it is a deliberate and limited exception to this reference's focus on reusable fundamentals. This section is only an orientation: Kubernetes storage APIs let workloads request and mount storage, but the backend determines its durability, availability, and recovery behavior. That distinction builds on the general [scope and tool-specificity design](../README.md#scope-and-tool-specificity); this reference does not attempt to catalogue Kubernetes storage resources or commands.

For detailed, current guidance, use the official [Kubernetes Storage documentation](https://kubernetes.io/docs/concepts/storage/). General Linux storage concepts and commands remain covered in [Linux Storage Background and Commands](./Storage_Background_Commands.md).

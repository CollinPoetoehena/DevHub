# Storage Background & Commands

This document covers **general storage background and Linux storage commands**: block devices, partitions, filesystems, mounts, LVM, RAID, NFS and Linux inspection/management tools. It is intended to explain concepts that apply across systems, not a platform-specific storage guide.

This guide is about general storage concepts and Linux commands rather than a particular orchestration platform, following the [scope and tool-specificity design](../README.md#scope-and-tool-specificity). For a brief Kubernetes-specific orientation and a link to its official documentation, see the [Kubernetes-specific exception](./README.md#kubernetes-specific-exception). For reusable storage architecture and data-protection decisions, see [Storage Architecture](./Storage_Architecture.md).

---

## Table of Contents

- [Background: Storage Concepts](#background-storage-concepts)
  - [Block Devices](#block-devices)
  - [Partitions & Partition Tables](#partitions--partition-tables)
  - [Filesystems](#filesystems)
  - [Mounting](#mounting)
  - [LVM (Logical Volume Manager)](#lvm-logical-volume-manager)
  - [RAID (Redundant Array of Independent Disks)](#raid-redundant-array-of-independent-disks)
  - [NFS (Network File System)](#nfs-network-file-system)
- [Commands: Storage](#commands-storage)
  - [lsblk](#lsblk)
  - [df](#df)
  - [du](#du)
  - [blkid](#blkid)
  - [mount / umount](#mount--umount)
  - [fdisk / gdisk / parted](#fdisk--gdisk--parted)
  - [mkfs](#mkfs)
  - [findmnt](#findmnt)
  - [LVM Commands](#lvm-commands)
  - [smartctl](#smartctl)

---

## Background: Storage Concepts

### Block Devices

A block device is any storage hardware that the kernel exposes as a file under `/dev/`. Data is read and written in fixed-size blocks (typically 512 bytes or 4 KiB sectors). Examples: physical disks (`/dev/sda`, `/dev/nvme0n1`), partitions (`/dev/sda1`), USB drives, virtual disks attached to VMs.

**Naming conventions:**

| Pattern | Description |
|---------|-------------|
| `/dev/sda`, `/dev/sdb` | SCSI/SATA disks — `sd` = SCSI disk, `a`/`b` = first/second disk |
| `/dev/sda1`, `/dev/sda2` | Partitions on `/dev/sda` — numbered sequentially |
| `/dev/nvme0n1` | NVMe SSD — `nvme0` = first NVMe controller, `n1` = first namespace |
| `/dev/nvme0n1p1` | First partition on the NVMe drive |
| `/dev/vda`, `/dev/vdb` | Virtio disks (common in VMs under KVM/QEMU/Proxmox) |
| `/dev/loop0` | Loop device — a file mounted as if it were a block device |

**Key points:**
- A disk can be used raw (no partitions) or divided into partitions.
- A partition must be formatted with a filesystem before it can hold files.
- The kernel assigns device names at boot based on detection order — names can change across reboots. Use UUIDs or labels for reliable identification.

### Partitions & Partition Tables

A partition table defines how a disk is divided into sections (partitions). Each partition behaves like an independent disk and can have its own filesystem.

**Two partition table formats:**

| Format | Description |
|--------|-------------|
| **MBR** (Master Boot Record) | Legacy. Max 4 primary partitions (or 3 primary + 1 extended with logical partitions inside). Max disk size 2 TiB. |
| **GPT** (GUID Partition Table) | Modern. Up to 128 partitions by default. Supports disks larger than 2 TiB. Required for UEFI boot. |

Most modern systems use GPT. MBR is still found on older hardware or legacy VMs.

**Common partition layout (Linux server):**

| Partition | Mount Point | Purpose |
|-----------|-------------|---------|
| EFI System Partition | `/boot/efi` | Bootloader (UEFI systems) |
| Boot partition | `/boot` | Kernel and initramfs |
| Root partition | `/` | OS and applications |
| Swap partition | (none — used as swap space) | Virtual memory overflow |
| Data partition | `/data` or `/mnt/data` | User/application data |

### Filesystems

A filesystem is the structure that organises data on a partition into files and directories. Without a filesystem, a partition is just raw bytes. Formatting a partition creates the filesystem.

**Common Linux filesystems:**

| Filesystem | Description |
|------------|-------------|
| **ext4** | Default on most Linux distributions. Journaling, stable, mature, good general-purpose performance. Supports volumes up to 1 EiB, files up to 16 TiB. |
| **XFS** | High-performance journaling filesystem. Default on RHEL/CentOS. Excels at large files and parallel I/O. Cannot be shrunk (only grown). |
| **Btrfs** | Copy-on-write (COW) filesystem with built-in snapshots, checksums, compression, and RAID. More features than ext4/XFS but historically less stable for some workloads. |
| **ZFS** | Advanced COW filesystem + volume manager. Pooled storage, snapshots, checksums, deduplication, RAID-Z. Not in the mainline Linux kernel (license incompatibility) — installed via module. Used heavily in NAS and Proxmox. |
| **tmpfs** | In-memory filesystem. Fast, volatile — contents lost on reboot. Used for `/tmp`, `/run`. |
| **vfat/FAT32** | Legacy, no permissions, 4 GiB file size limit. Used for EFI System Partitions and USB drives for cross-OS compatibility. |

**Journaling:** ext4, XFS, and Btrfs are journaling filesystems — they log changes before writing them. If the system crashes, the journal is replayed on boot to restore consistency, avoiding a full disk scan (`fsck`).

### Mounting

Mounting is the act of attaching a filesystem (from a partition, disk, network share, etc.) to a directory in the existing directory tree. The directory where it attaches is called the **mount point**. After mounting, files on that filesystem appear as if they are part of the directory tree at that point.

**How it works:**
- Linux has a single root filesystem (`/`). All other filesystems are mounted as subdirectories within this tree.
- A mount point is just a normal directory (e.g. `/mnt/data`, `/media/usb`). When a filesystem is mounted there, the directory's previous contents are hidden (not deleted) until the filesystem is unmounted.
- The kernel maintains a list of all current mounts, visible via `/proc/mounts` or the `mount` command.

**Example:** A USB drive appears as `/dev/sdb1`. To access its files:
```bash
sudo mount /dev/sdb1 /mnt/usb
ls /mnt/usb    # now shows the files on the USB drive
```

**Unmounting:**
```bash
sudo umount /mnt/usb
```

**Persistent mounts — `/etc/fstab`:**

Mounts done with the `mount` command are temporary — they are lost on reboot. To make a mount permanent, add an entry to `/etc/fstab` (filesystem table). The system reads this file at boot and mounts everything listed.

**`/etc/fstab` format:**
```
<device>       <mount-point>  <type>  <options>       <dump>  <pass>
UUID=abc-123   /data          ext4    defaults        0       2
/dev/sda2      /boot          ext4    defaults        0       1
tmpfs          /tmp           tmpfs   defaults,size=2G 0      0
```

| Field | Description |
|-------|-------------|
| `<device>` | Block device, UUID, or label. Prefer `UUID=` — device names like `/dev/sda1` can change across reboots. |
| `<mount-point>` | Directory where the filesystem will be attached. |
| `<type>` | Filesystem type: `ext4`, `xfs`, `btrfs`, `tmpfs`, `nfs`, `vfat`, etc. |
| `<options>` | Mount options: `defaults` = `rw,suid,dev,exec,auto,nouser,async`. Others: `noatime` (skip access time updates — performance boost), `ro` (read-only), `nofail` (don't halt boot if device is missing). |
| `<dump>` | Used by the `dump` backup utility. `0` = don't dump. Almost always `0` on modern systems. |
| `<pass>` | `fsck` order at boot: `0` = don't check, `1` = check first (root), `2` = check after root. |

**Finding UUIDs:**
```bash
blkid              # shows UUID, TYPE, LABEL for all block devices
lsblk -f           # tree view with filesystem type, UUID, mount point
```

### LVM (Logical Volume Manager)

LVM adds a layer of abstraction between physical disks and filesystems, giving you flexible volume management — resize volumes, span them across disks, and create snapshots without worrying about physical partition boundaries.

**Three layers:**

```
Physical Disks/Partitions
        │
        ▼
┌─────────────────────────┐
│  PV (Physical Volume)   │  ← initialized disk/partition (pvcreate)
└─────────────────────────┘
        │
        ▼
┌─────────────────────────┐
│  VG (Volume Group)      │  ← pool of storage from one or more PVs (vgcreate)
└─────────────────────────┘
        │
        ▼
┌─────────────────────────┐
│  LV (Logical Volume)    │  ← virtual partition carved from a VG (lvcreate)
└─────────────────────────┘
        │
        ▼
   Filesystem (ext4, xfs, …) → mount point
```

| Layer | What it is | Command |
|-------|-----------|---------|
| **PV** (Physical Volume) | A disk or partition marked for LVM use. | `pvcreate /dev/sdb` |
| **VG** (Volume Group) | A pool that combines one or more PVs into a single storage space. | `vgcreate myvg /dev/sdb /dev/sdc` |
| **LV** (Logical Volume) | A virtual partition allocated from a VG. This is what you format and mount. | `lvcreate -L 50G -n mydata myvg` |

**Why use LVM:**
- **Resize volumes live** — grow (and sometimes shrink) a logical volume and its filesystem without downtime.
- **Span multiple disks** — create a volume group from several physical disks; a logical volume can be larger than any single disk.
- **Snapshots** — create a point-in-time copy of a volume for backup or testing.
- **Thin provisioning** — allocate more space than physically available (overcommit); actual disk usage grows on demand.

**Example workflow:**
```bash
pvcreate /dev/sdb                          # mark disk as PV
vgcreate datavg /dev/sdb                   # create VG from the PV
lvcreate -L 40G -n appdata datavg          # create 40 GiB LV
mkfs.ext4 /dev/datavg/appdata              # format the LV
mount /dev/datavg/appdata /mnt/appdata     # mount it
```

### RAID (Redundant Array of Independent Disks)

RAID combines multiple physical disks into a single logical unit for redundancy, performance, or both. If a disk fails, RAID can keep the system running without data loss (depending on the RAID level).

**Common RAID levels:**

| Level | Min Disks | Description | Capacity | Fault Tolerance |
|-------|-----------|-------------|----------|-----------------|
| **RAID 0** (Stripe) | 2 | Data striped across disks. Maximum performance, zero redundancy. One disk failure = all data lost. | 100% | None |
| **RAID 1** (Mirror) | 2 | Data mirrored identically on both disks. If one fails, the other has a full copy. | 50% | 1 disk |
| **RAID 5** (Stripe + Parity) | 3 | Data striped with distributed parity. Can survive one disk failure. | $(n-1)/n$ | 1 disk |
| **RAID 6** (Stripe + Double Parity) | 4 | Like RAID 5 but with two parity blocks. Can survive two simultaneous disk failures. | $(n-2)/n$ | 2 disks |
| **RAID 10** (Mirror (RAID 1) + Stripe (RAID 0) -> combined=RAID 10) | 4 | Mirrors pairs of disks, then stripes across mirrors. Best performance + redundancy. | 50% | 1 disk per mirror pair |

**RAID is not a backup.** RAID protects against disk failure — it does not protect against accidental deletion, ransomware, corruption, or disasters. Always have separate backups.

**Implementation:**
- **Hardware RAID** — a dedicated RAID controller handles disk management; the OS sees a single virtual disk.
- **Software RAID (mdadm)** — Linux kernel manages the array. No special hardware needed. Configured with `mdadm`.
- **ZFS RAID-Z** — ZFS implements its own RAID (RAID-Z1 ≈ RAID 5, RAID-Z2 ≈ RAID 6) with added checksums and self-healing.

### NFS (Network File System)

NFS allows a server to share directories over the network. Client machines mount these remote directories as if they were local filesystems. NFS is the standard way to share storage between Linux hosts.

**How it works:**
1. The server exports a directory (e.g. `/srv/nfs/data`) by adding it to `/etc/exports`.
2. The client mounts the remote export: `mount server:/srv/nfs/data /mnt/shared`.
3. Files appear local to the client — reads and writes happen over the network transparently.

**Key points:**
- **Stateless (NFSv3)** / **Stateful (NFSv4)** — NFSv4 maintains state and supports better security and performance.
- **Performance** depends on network speed — Gigabit Ethernet is the minimum for practical use.
- **Permissions** — NFS maps UIDs/GIDs between client and server. If `uid=1000` on the client and server are different users, permissions can be confusing. Use consistent UID/GID mappings.

**General use case:** An NFS server can export shared files to multiple Linux clients over a network. Client and server UID/GID mappings should be planned together.

---

## Commands: Storage

General storage commands with output format explanations. Used for inspecting disks, filesystems, mounts, and managing storage on Linux.

---

### `lsblk`

Lists block devices in a tree structure showing the relationship between disks, partitions, and mount points.

**Output columns (default):**

| Column | Description |
|--------|-------------|
| `NAME` | Device name (without `/dev/` prefix) |
| `MAJ:MIN` | Major and minor device numbers (kernel internal) |
| `RM` | Removable device: `1` = yes (USB), `0` = no |
| `SIZE` | Size of the device |
| `RO` | Read-only: `1` = yes, `0` = no |
| `TYPE` | `disk` = whole physical/virtual disk (e.g. /dev/sda), `part` = partition on a disk (e.g. /dev/sda1), `lvm` = Logical Volume Manager volume, `loop` = loopback device used to mount disk images or Snap packages, `rom` = rom = read-only optical media device such as a CD-ROM (Compact Disc Read-Only Memory) or DVD-ROM (Digital Versatile Disc Read-Only Memory). CDs and DVDs are optical storage discs that store data and are read by a laser in an optical drive. |
| `MOUNTPOINTS` | Where the device is currently mounted (empty = not mounted) |

```
lsblk
```

Example output:
```
NAME                  MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
sda                     8:0    0 238.5G  0 disk
├─sda1                  8:1    0   512M  0 part /boot/efi
├─sda2                  8:2    0     1G  0 part /boot
└─sda3                  8:3    0   237G  0 part
  ├─ubuntu--vg-root   253:0    0   100G  0 lvm  /
  └─ubuntu--vg-swap   253:1    0     4G  0 lvm  [SWAP]
nvme0n1               259:0    0 476.9G  0 disk
└─nvme0n1p1           259:1    0 476.9G  0 part /data
```

- `sda` is a SATA disk with 3 partitions: EFI, boot, and an LVM partition.
- The LVM partition (`sda3`) contains two logical volumes: root and swap.
- `nvme0n1` is an NVMe SSD with a single partition mounted at `/data`.

**Useful flags:**
```bash
lsblk -f              # show filesystem type, label, UUID, and available space
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,UUID   # custom columns
```

---

### `df`

Reports filesystem disk space usage for mounted filesystems.

**Common usage:**
```bash
df -h                 # human-readable sizes (GiB, MiB)
df -hT                # include filesystem type column
```

**Output columns:**

| Column | Description |
|--------|-------------|
| `Filesystem` | Device or filesystem name |
| `Type` | Filesystem type (with `-T` flag) |
| `Size` | Total size of the filesystem |
| `Used` | Space used |
| `Avail` | Space available |
| `Use%` | Percentage used |
| `Mounted on` | Mount point |

Example output:
```
Filesystem                  Type  Size  Used Avail Use% Mounted on
/dev/mapper/ubuntu--vg-root ext4  100G   45G   50G  48% /
/dev/sda2                   ext4  974M  250M  657M  28% /boot
/dev/sda1                   vfat  511M  6.1M  505M   2% /boot/efi
/dev/nvme0n1p1              ext4  469G  200G  245G  45% /data
tmpfs                       tmpfs 7.8G     0  7.8G   0% /dev/shm
```

---

### `du`

Estimates file and directory space usage.

```bash
du -sh /var/log          # total size of /var/log in human-readable format
du -h --max-depth=1 /    # size of each top-level directory
du -sh *                 # size of each item in current directory
```

**Flags:**

| Flag | Description |
|------|-------------|
| `-s` | Summary — total only, don't list subdirectories |
| `-h` | Human-readable sizes |
| `--max-depth=N` | Limit directory depth to N levels |

---

### `blkid`

Shows attributes (UUID, filesystem type, label) of block devices.

```bash
blkid
```

Example output:
```
/dev/sda1: UUID="ABCD-1234" BLOCK_SIZE="512" TYPE="vfat" PARTLABEL="EFI System Partition" PARTUUID="..."
/dev/sda2: UUID="f1e2d3c4-..." BLOCK_SIZE="4096" TYPE="ext4" PARTUUID="..."
/dev/sda3: UUID="a1b2c3d4-..." TYPE="LVM2_member" PARTUUID="..."
/dev/mapper/ubuntu--vg-root: UUID="e5f6a7b8-..." BLOCK_SIZE="4096" TYPE="ext4"
```

- Use the UUID in `/etc/fstab` rather than device names for reliable mounts.

---

### `mount` / `umount`

Mount and unmount filesystems.

```bash
mount                              # list all current mounts
mount /dev/sdb1 /mnt/usb           # mount a partition to a directory
mount -t nfs server:/share /mnt/nfs   # mount an NFS share
umount /mnt/usb                    # unmount
```

**Useful flags:**

| Flag | Description |
|------|-------------|
| `-t <type>` | Specify filesystem type (`ext4`, `xfs`, `nfs`, `tmpfs`, etc.) |
| `-o <options>` | Mount options: `ro` (read-only), `noatime`, `rw`, `remount` |
| `-a` | Mount all entries in `/etc/fstab` |

**Remount with different options (no unmount needed):**
```bash
mount -o remount,rw /              # remount root filesystem as read-write
```

---

### `fdisk` / `gdisk` / `parted`

Disk partitioning tools.

| Tool | Description |
|------|-------------|
| `fdisk` | Interactive MBR/GPT partitioner. Good for quick partition tasks. |
| `gdisk` | GPT-only partitioner. Use when working exclusively with GPT. |
| `parted` | Supports both MBR and GPT. Scriptable. Can resize partitions. |

```bash
fdisk -l                  # list all disks and partitions (read-only)
fdisk /dev/sdb            # interactive partitioning of /dev/sdb
parted /dev/sdb print     # print partition table
```

**Warning:** Partitioning a disk that is in use or has mounted filesystems can cause data loss. Always unmount first.

---

### `mkfs`

Creates (formats) a filesystem on a partition or logical volume.

```bash
mkfs.ext4 /dev/sdb1                  # format as ext4
mkfs.xfs /dev/mapper/datavg-appdata  # format LVM volume as XFS
mkfs.vfat /dev/sdb1                  # format as FAT32 (for EFI, USB)
```

**Warning:** Formatting destroys all existing data on the target device.

---

### `findmnt`

Shows mounted filesystems in a tree or flat view. More readable than `mount` output.

```bash
findmnt                   # tree view of all mounts
findmnt -t ext4           # only ext4 mounts
findmnt /data             # info about a specific mount point
findmnt -n -o SOURCE,TARGET,FSTYPE,OPTIONS /data   # custom columns, no header
```

---

### LVM Commands

Commands for managing Logical Volume Manager.

**Physical Volumes:**
```bash
pvs                       # brief list of PVs
pvdisplay                 # detailed PV info
pvcreate /dev/sdb         # initialize a disk as a PV
```

**Volume Groups:**
```bash
vgs                       # brief list of VGs
vgdisplay                 # detailed VG info
vgcreate datavg /dev/sdb  # create VG from PV
vgextend datavg /dev/sdc  # add another PV to existing VG
```

**Logical Volumes:**
```bash
lvs                       # brief list of LVs
lvdisplay                 # detailed LV info
lvcreate -L 50G -n mydata datavg           # create 50 GiB LV
lvextend -L +20G /dev/datavg/mydata        # grow LV by 20 GiB
lvextend -l +100%FREE /dev/datavg/mydata   # use all remaining VG space
resize2fs /dev/datavg/mydata               # resize ext4 filesystem to fill the LV
xfs_growfs /mnt/mydata                     # resize XFS filesystem (XFS uses mount point)
```

---

### `smartctl`

Reads SMART (Self-Monitoring, Analysis, and Reporting Technology) data from disks to check disk health.

```bash
smartctl -a /dev/sda            # full SMART info
smartctl -H /dev/sda            # quick health check (PASSED/FAILED)
smartctl -t short /dev/sda      # run a short self-test
```

Requires the `smartmontools` package. Useful for detecting failing drives before they die.

---

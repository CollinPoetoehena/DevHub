# Storage Commands

See the [cheat sheet README](README.md) for scope, usage, placeholders, and safety.

## Table of Contents

- [Inspection](#inspection)
  - [lsblk](#lsblk)
  - [df](#df)
  - [du](#du)
  - [blkid](#blkid)
  - [findmnt](#findmnt)
- [Mounts](#mounts)
  - [mount](#mount)
  - [umount](#umount)
- [Partitions and filesystems](#partitions-and-filesystems)
  - [fdisk](#fdisk)
  - [gdisk](#gdisk)
  - [parted](#parted)
  - [mkfs.ext4](#mkfsext4)
  - [mkfs.xfs](#mkfsxfs)
  - [mkfs.vfat](#mkfsvfat)
- [LVM](#lvm)
  - [pvs](#pvs)
  - [pvdisplay](#pvdisplay)
  - [vgs](#vgs)
  - [vgdisplay](#vgdisplay)
  - [lvs](#lvs)
  - [lvdisplay](#lvdisplay)
  - [pvcreate](#pvcreate)
  - [vgcreate](#vgcreate)
  - [vgextend](#vgextend)
  - [lvcreate](#lvcreate)
  - [lvextend](#lvextend)
  - [resize2fs](#resize2fs)
  - [xfs_growfs](#xfs_growfs)
- [Disk health](#disk-health)
  - [smartctl](#smartctl)

---

## Inspection

### lsblk

[Manual](https://man7.org/linux/man-pages/man8/lsblk.8.html).

```bash
lsblk                                # Block devices and their hierarchy
lsblk -f                             # Filesystem types, labels, UUIDs, and mounts
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,UUID # Selected columns
```

### df

[Official manual](https://www.gnu.org/software/coreutils/manual/html_node/df-invocation.html).

```bash
df -hT                               # Mounted filesystem usage and type
df -h /data                          # Usage of the filesystem containing /data
df -i                                # Inode usage; useful when space remains but file creation fails
```

### du

[Official manual](https://www.gnu.org/software/coreutils/manual/html_node/du-invocation.html).

```bash
du -sh /var/log                       # Total allocated space under a directory
sudo du -xh --max-depth=1 /var        # One level deep, without crossing filesystem boundaries
```

### blkid

[Manual](https://man7.org/linux/man-pages/man8/blkid.8.html).

```bash
sudo blkid                           # Filesystem signatures, labels, and UUIDs
sudo blkid /dev/sdb1                  # Inspect one verified partition
```

### findmnt

[Manual](https://man7.org/linux/man-pages/man8/findmnt.8.html).

```bash
findmnt                              # Tree of mounted filesystems
findmnt --target /data               # Filesystem containing a path
findmnt -t nfs,nfs4                   # Mounted NFS filesystems
findmnt --fstab                      # Entries configured in /etc/fstab
findmnt --verify --verbose           # Check fstab parsability and usability; does not mount it
```

---

## Mounts

### mount

[Manual](https://man7.org/linux/man-pages/man8/mount.8.html).

**Changes state:** verify the source and an existing mount-point directory. Mounting hides any existing contents at that directory until unmounted.

```bash
sudo mount /dev/sdb1 /mnt/data        # Mount a verified partition
sudo mount -o ro /dev/sdb1 /mnt/data  # Request read-only access; some filesystems may replay journals
sudo mount -t nfs server.example:/export /mnt/nfs # Mount an authorized NFS export
```

### umount

[Manual](https://man7.org/linux/man-pages/man8/umount.8.html).

**Changes state:** stop users of the mount first; do not force or lazily detach it as a default workaround.

```bash
sudo umount /mnt/data                 # Unmount after applications finish using it
```

---

## Partitions and filesystems

Partition edits and formatting can destroy data. Verify device identity with `lsblk`, check backups, and unmount affected filesystems before making changes.

### fdisk

[Manual](https://man7.org/linux/man-pages/man8/fdisk.8.html).

```bash
sudo fdisk -l                        # List partition tables without changing them
sudo fdisk -l /dev/sdb                # Inspect a specific disk
# Destructive if written: review the target before entering the editor.
sudo fdisk /dev/sdb                   # Interactive partition editor; q exits without saving
```

### gdisk

[Official manual](https://www.rodsbooks.com/gdisk/gdisk.html).

```bash
sudo gdisk -l /dev/sdb                # Inspect a GPT disk without writing changes
```

### parted

[Official manual](https://www.gnu.org/software/parted/manual/parted.html).

```bash
sudo parted /dev/sdb print            # Inspect the partition table
sudo parted /dev/sdb unit GiB print free # Show partition layout and unallocated space
```

### mkfs.ext4

[Manual](https://man7.org/linux/man-pages/man8/mke2fs.8.html) and [official manual source](https://github.com/tytso/e2fsprogs/blob/master/misc/mke2fs.8.in).

**Destructive:** creates a new filesystem on the verified, unmounted target; existing data is lost.

```bash
sudo mkfs.ext4 /dev/sdb1               # Create an ext4 filesystem
```

### mkfs.xfs

[Manual](https://man7.org/linux/man-pages/man8/mkfs.xfs.8.html).

**Destructive:** formats the verified, unmounted logical volume; do not run on an existing data volume.

```bash
sudo mkfs.xfs /dev/datavg/appdata      # Create an XFS filesystem
```

### mkfs.vfat

[Official manual](https://github.com/dosfstools/dosfstools/blob/master/manpages/mkfs.fat.8.in). `mkfs.vfat` is an alias for `mkfs.fat`.

**Destructive:** formats the verified, unmounted partition.

```bash
sudo mkfs.vfat -F 32 /dev/sdb1         # Create FAT32 explicitly
```

---

## LVM

Inspection commands are independent. Creation and growth examples are alternatives, not a script: verify the actual physical volumes, volume group, logical volume, filesystem, and free capacity first.

### pvs

[Official manual source](https://github.com/lvmteam/lvm2/blob/main/man/pvs.8_pregen).

```bash
sudo pvs                             # Physical volume summary
```

### pvdisplay

[Official manual source](https://github.com/lvmteam/lvm2/blob/main/man/pvdisplay.8_pregen).

```bash
sudo pvdisplay /dev/sdb               # Detailed information for a physical volume
```

### vgs

[Official manual source](https://github.com/lvmteam/lvm2/blob/main/man/vgs.8_pregen).

```bash
sudo vgs                             # Volume groups and free capacity
```

### vgdisplay

[Official manual source](https://github.com/lvmteam/lvm2/blob/main/man/vgdisplay.8_pregen).

```bash
sudo vgdisplay datavg                 # Detailed volume group information
```

### lvs

[Official manual source](https://github.com/lvmteam/lvm2/blob/main/man/lvs.8_pregen).

```bash
sudo lvs -a -o +devices               # Logical volumes, including internal volumes and backing devices
```

### lvdisplay

[Official manual source](https://github.com/lvmteam/lvm2/blob/main/man/lvdisplay.8_pregen).

```bash
sudo lvdisplay /dev/datavg/appdata    # Detailed logical volume information
```

### pvcreate

[Official manual source](https://github.com/lvmteam/lvm2/blob/main/man/pvcreate.8_pregen).

**Destructive:** initializes a verified unused disk for LVM; can overwrite existing metadata.

```bash
sudo pvcreate /dev/sdb                # Initialize the selected disk as a physical volume
```

### vgcreate

[Official manual source](https://github.com/lvmteam/lvm2/blob/main/man/vgcreate.8_pregen).

**Changes state:**

```bash
sudo vgcreate datavg /dev/sdb         # Create a group from an initialized, unused PV
```

### vgextend

[Official manual source](https://github.com/lvmteam/lvm2/blob/main/man/vgextend.8_pregen).

**Changes state:**

```bash
sudo vgextend datavg /dev/sdc         # Add a prepared, unused PV to an existing group
```

### lvcreate

[Official manual source](https://github.com/lvmteam/lvm2/blob/main/man/lvcreate.8_pregen).

**Changes state:**

```bash
sudo lvcreate -L 50G -n appdata datavg # Allocate a new 50 GiB logical volume
```

### lvextend

[Official manual source](https://github.com/lvmteam/lvm2/blob/main/man/lvextend.8_pregen).

**Changes state:** these are alternatives. Neither command grows the filesystem; use its matching tool afterward.

```bash
sudo lvextend -L +20G /dev/datavg/appdata       # Add 20 GiB to an existing LV
sudo lvextend -l +100%FREE /dev/datavg/appdata  # Consume all remaining free extents in the VG
```

### resize2fs

[Manual](https://man7.org/linux/man-pages/man8/resize2fs.8.html) and [official manual source](https://github.com/tytso/e2fsprogs/blob/master/resize/resize2fs.8.in).

**Changes state:** only for ext2/ext3/ext4; verify the underlying volume was grown.

```bash
sudo resize2fs /dev/datavg/appdata     # Grow the ext filesystem to fill the device
```

### xfs_growfs

[Manual](https://man7.org/linux/man-pages/man8/xfs_growfs.8.html).

**Changes state:** XFS must be mounted; verify the underlying volume was grown. XFS cannot be shrunk.

```bash
sudo xfs_growfs /mnt/appdata           # Grow XFS using its mount point, not the device path
```

---

## Disk health

### smartctl

[Official manual source](https://github.com/smartmontools/smartmontools/blob/master/smartmontools/smartctl.8.in). Requires smartmontools and device/controller support.

```bash
sudo smartctl -a /dev/sda             # SMART information, attributes, and test history
sudo smartctl -H /dev/sda             # Device-reported health; not a guarantee against failure
sudo smartctl -t short /dev/sda       # Start a short device self-test; may affect performance
sudo smartctl -l selftest /dev/sda    # Read results after the test has completed
```

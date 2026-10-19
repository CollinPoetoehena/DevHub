# Booting and Installing an Operating System

This guide explains the general boot and installation flow shared by many computers. Firmware menus, installer screens, disk layouts, bootloaders and recovery steps vary by platform and release, so use this page for orientation and the selected OS or hypervisor's official documentation for exact instructions. This follows DevHub's [scope and tool-specificity design](../README.md#scope-and-tool-specificity).

---

## Table of Contents

- [How a computer boots](#how-a-computer-boots)
- [Prepare before installation](#prepare-before-installation)
- [Create and boot installation media](#create-and-boot-installation-media)
- [Install and verify the operating system](#install-and-verify-the-operating-system)
- [General troubleshooting](#general-troubleshooting)
- [Official installation documentation](#official-installation-documentation)

---

## How a computer boots

The boot process passes control through a series of components:

1. **Firmware** (BIOS or UEFI) initializes hardware and selects a boot device according to its boot entries and boot order.
2. **Bootloader or OS boot manager** loads the operating-system kernel and any required early-startup files. Its exact design depends on the OS.
3. **Kernel** initializes system resources and starts the processes and services that make the machine usable.

When installing an OS, removable media temporarily provides an installer environment. After installation, the system should start from the OS boot entry on the target storage device. Firmware keys, menus, boot entries, security checks, and recovery options are hardware- and OS-specific.

---

## Prepare before installation

Plan the installation before changing firmware settings or writing media:

- Confirm that the OS supports the target processor architecture and hardware. Check minimum requirements, storage-controller support, network drivers, and lifecycle/support policy in the OS's official documentation.
- Back up any data that must be kept, and verify that the backup is usable. An installer may erase or repartition the selected disk.
- Identify the exact target computer and storage device. If multiple drives are present, confirm which one contains existing data before proceeding.
- Decide how the system should be used and administered: for example, desktop or server, standalone OS or virtualization host, local console or remote management.
- Plan the initial network configuration, user and administrator access, disk layout, encryption and recovery method. The available options depend on the selected OS and use case.
- Keep power stable during installation. For portable systems, connect AC power and avoid interrupting firmware updates or disk operations.

Firmware changes can affect existing installations. Use the one-time boot menu when possible instead of permanently changing boot order. Prefer UEFI on systems and OS releases that support it. Secure Boot, storage-controller mode, and other security or compatibility settings are platform-specific: follow the target OS and hardware vendor's documentation, and do not disable protections or change disk modes without understanding the consequences for existing systems.

---

## Create and boot installation media

An installation image is commonly distributed as an ISO file. A media-writing utility writes that image in a bootable form to a removable drive; simply copying the ISO file onto a USB drive usually does not create bootable media.

1. Download the installer image from the OS or hypervisor's official source.
2. Verify its checksum or signature when the publisher provides verification instructions.
3. Use a trusted image-writing utility and select the intended removable drive carefully. Writing an image usually erases the selected drive.
4. Safely eject the media, connect it to the target computer, and open the firmware's one-time boot menu or select the USB device as the temporary boot option.
5. Choose the installer or live environment entry. If the media does not appear or start, check the device, image, firmware mode and platform-specific Secure Boot requirements using official documentation.

After the installer starts, its workflow is specific to the selected OS. Read prompts carefully, especially those about disk selection, repartitioning, erasure, encryption and user credentials.

---

## Install and verify the operating system

Most installations follow a similar high-level sequence:

1. Select language, keyboard and locale settings.
2. Select the installation target and disk layout; check that the intended data may be overwritten before confirming.
3. Configure network connectivity and required update or repository settings.
4. Create the initial user and apply the OS's recommended security and recovery options.
5. Review the summary and let the installer complete without interrupting it.
6. Remove or disconnect installation media when prompted, then restart and confirm that firmware boots the installed system.
7. Apply supported updates and verify basic operation: storage, network connectivity, time, administrator access, and recovery or backup arrangements.

For a hypervisor or other infrastructure platform, continue with its official host-configuration and security guidance. Keep deployment-specific addresses, host settings, automation and verification results in the project documentation that owns that implementation rather than duplicating them in this general reference.

---

## General troubleshooting

| Symptom | General checks |
|---|---|
| Installation media is not listed | Confirm that the image was written as bootable media, try another USB port, check the one-time boot menu, and verify firmware mode and media requirements for the target OS. |
| Media starts but returns to firmware | Check the boot entry and image integrity; consult the OS and hardware vendor's troubleshooting guidance for Secure Boot and firmware compatibility. |
| Installer cannot find a disk or network adapter | Check hardware support and firmware settings using official documentation. Do not change storage-controller settings on an existing system without a tested backup and a recovery plan. |
| The installed system does not start | Remove installation media, confirm the intended internal boot entry and firmware mode, and use the OS's documented recovery process. |
| System starts but networking or storage is unavailable | Confirm that the relevant device is detected and supported, then use the OS's standard diagnostic tools and official driver or configuration guidance. |

Avoid applying a fix from another OS, hardware model or release without checking applicability. Firmware and installation troubleshooting is particularly sensitive to machine-specific settings and can make existing data inaccessible.

---

## Official installation documentation

Use the selected platform's maintained instructions for current requirements, supported releases, installer screens, security settings and recovery:

- **Proxmox VE:** [Installation](https://pve.proxmox.com/wiki/Installation) and [official documentation](https://pve.proxmox.com/pve-docs/).
- **Ubuntu Server:** [Ubuntu Server installation tutorial](https://ubuntu.com/tutorials/install-ubuntu-server) and [Ubuntu documentation](https://documentation.ubuntu.com/).
- **Debian:** [Debian installation manual](https://www.debian.org/releases/stable/installmanual).
- **Fedora:** [Fedora installation guide](https://docs.fedoraproject.org/en-US/fedora/latest/install-guide/).
- **Windows:** [Microsoft Windows download and installation](https://www.microsoft.com/software-download/windows11).
- **macOS:** [Apple macOS recovery and reinstallation](https://support.apple.com/en-us/102655).

For general OS concepts, see [Operating-System Fundamentals](./Operating_Systems.md). Related shared foundations are covered in the [network reference](../network/README.md) and [storage reference](../storage/README.md).

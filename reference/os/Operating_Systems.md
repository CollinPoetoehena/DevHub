# Operating-System Fundamentals

An operating system (OS) manages a computer's hardware resources and provides common services and interfaces for programs. Applications do not normally control storage devices, memory or network hardware directly; the OS coordinates access, isolates workloads and supplies abstractions that applications can use.

This guide focuses on concepts that remain useful across platforms. It follows DevHub's [scope and tool-specificity design](../README.md#scope-and-tool-specificity): understand the fundamentals here, and use the official documentation for detailed behavior, configuration and release-specific instructions.

---

## Table of Contents

- [Core Responsibilities](#core-responsibilities)
- [Kernel and User Space](#kernel-and-user-space)
- [Operating-System Families](#operating-system-families)
- [Selecting and Learning a Platform](#selecting-and-learning-a-platform)

---

## Core Responsibilities

- **Process and CPU management:** creates processes and threads, schedules their access to CPU time, and provides mechanisms for communication and synchronization.
- **Memory management:** assigns virtual memory to processes, maintains isolation, manages physical memory and may page data to storage when memory is under pressure.
- **Storage and filesystems:** organizes persistent data into files/directories, applies permissions, and mediates access to disks and other storage devices.
- **Device and I/O management:** uses drivers and common interfaces to operate processors, network adapters, displays, keyboards and storage.
- **Networking:** provides network interfaces and protocol implementations that programs use to communicate, subject to routing, firewall and name-resolution configuration.
- **Security and identity:** authenticates users and services, enforces permissions and separates workloads; the exact model differs by OS and configuration.
- **Services and system interfaces:** starts background services, exposes system APIs and records events/logs used to operate and troubleshoot the computer.
- **Boot and recovery:** initializes hardware and loads the kernel and system services; recovery and update mechanisms depend on the platform.

An OS is not just its kernel. The complete environment also includes libraries, system utilities, package/update mechanisms, service management and user-facing tools. A distribution or product combines these components and chooses how they are maintained and released.

---

## Kernel and User Space

The **kernel** runs with privileged access and manages CPU scheduling, memory, device drivers, filesystems and core networking. **User-space** programs—such as shells, servers and desktop applications—run with more restricted privileges and request services through defined system interfaces. This separation helps contain application failures, although bugs or misconfiguration in privileged software can still affect the whole system.

On Linux systems, `uname -r` prints the running kernel release. The command reports one component of the system, not the complete distribution or its support status. Consult the relevant distribution's documentation to determine how its kernel is packaged, updated and supported.

---

## Operating-System Families

| Family | General characteristics | Examples and authoritative documentation |
|---|---|---|
| Linux | An open-source kernel used with distributions that package user-space tools, libraries, services and release/update policies. Server and desktop choices can vary widely while sharing many kernel and command-line fundamentals. | **Ubuntu** emphasizes an integrated release/support and package ecosystem; see [Ubuntu documentation](https://documentation.ubuntu.com/). **Debian** is a community distribution with its own release and package policies; see [Debian documentation](https://www.debian.org/doc/). **Fedora** provides a distinct community release cadence and technology set; see [Fedora documentation](https://docs.fedoraproject.org/). For kernel internals, see the [Linux kernel documentation](https://docs.kernel.org/). |
| Windows | A commercial OS family with its own kernel, APIs, administration tools, filesystem and release/support lifecycle. PowerShell and graphical management are common interfaces; Windows also supports Linux-related development through separately documented features. | Use [Microsoft Learn for Windows](https://learn.microsoft.com/windows/) and the applicable product documentation for administration, deployment and support lifecycle. |
| macOS | Apple's desktop OS built on the Darwin foundation, which includes the XNU kernel. It is not a Linux distribution, even though many command-line and Unix concepts are familiar. Hardware integration, user tools and software distribution are Apple-specific. | See the [macOS User Guide](https://support.apple.com/guide/mac-help/welcome/mac) and [Apple Platform Security](https://support.apple.com/guide/security/welcome/web) for product-specific features and security. |

These examples illustrate families and a few widely used distributions, not a ranking or exhaustive list. Raspberry Pi OS is one Linux distribution intended for Raspberry Pi hardware; it is an example of Linux in a specific device context, not a separate general-purpose OS concept for this reference. See [Raspberry Pi's official documentation](https://www.raspberrypi.com/documentation/computers/getting-started.html) for its supported hardware and setup.

---

## Selecting and Learning a Platform

Choose an OS based on the software you need, supported hardware, security/update policy, administration skills, compatibility and recovery requirements. A shared concept such as a process, filesystem or network socket can transfer across systems, but commands, configuration locations and service managers are not interchangeable.

For a specific distribution or product, consult its official docs for installation, release lifecycle, package management, security controls, upgrades and troubleshooting. DevHub intentionally explains the foundation rather than maintaining a copy of every product manual.

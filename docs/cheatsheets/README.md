# Command Cheat Sheets

A small collection of useful commands for quick lookup, with one file per topic:

- [Networking](NETWORKING.md): host networking, connectivity, DNS, DHCP, packet capture, performance, and BGP.
- [Storage](STORAGE.md): devices, disk usage, mounts, partitions, filesystems, LVM, and disk health.
- [Kubernetes](KUBERNETES.md): everyday `kubectl` inspection, troubleshooting, and workload management.

## Scope and usage

These lists are intentionally selective, not exhaustive or meant to be 100% complete. Keep commands that are useful to have at hand, with short comments rather than concept chapters, full option inventories, or an obligation to record everything learned.

Consult the linked official documentation, Linux `man` pages (for example, `man lsblk`), and the installed command's `--help` or help subcommand for details and version-specific behavior. Commands and options depend on the installed tools; these files are reminders, not substitutes for understanding the operation.

Examples target Linux and use illustrative names, addresses, paths, and sizes. Replace them with verified values before running a command. Run individual examples, not entire blocks as scripts. Install the relevant tool through the system's package manager when needed; `sudo` examples require appropriate privileges.

Check the target host, disk, cluster context, and namespace first. Commands marked **Changes state**, **Disruptive**, or **Destructive** need particular care; confirm backups and recovery access where relevant. Scan or capture traffic only on authorized networks, and treat captures and diagnostic output as potentially sensitive.

Project-specific configuration, operational procedures, and recovery instructions stay in the owning project. This collection is **not a replacement for the retired reference library**: the [reference retirement decision](../../archive/REFERENCE.md) still applies. It keeps a few practical commands accessible, not a new technical encyclopedia.

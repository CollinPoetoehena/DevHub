# Hardware Specifications

TODO: explain here shortly what hardware specifications you have like CPU, RAM, storage, and any other relevant components in general.


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
Get-WmiObject Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors

# RAM total (in GB)
(Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory / 1GB

# Storage disks
Get-PhysicalDisk | Select-Object FriendlyName, Size, MediaType
```

Alternatively, on Windows you can open **Task Manager → Performance** for a quick visual overview of CPU cores/threads, RAM, and disk.

---

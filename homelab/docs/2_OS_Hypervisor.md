# TODO: OS and/or Hypervisor Installation and Configuration

TODO: this is now copied from my earlier experience with installing an OS on an old laptop and made generic and some small changes, etc. Update it with the specific setup from the homelab when I start on it and have the specific setup, etc.


Each node needs a clean, consistent operating system or hypervisor.

TODO: make this generic for OS or Hypervisor: Proxmox VE, Ubuntu, etc. Add that when I start doing the actual steps, etc.

TODO: short introduction on this, since this is the first step to setting up the homelab after buying the hardware: the first step is to install the OS on the hardware, which will be the foundation for everything else. This involves creating a bootable USB drive with the OS installer, configuring the BIOS settings to boot from the USB, and then following the installation process. The choice of OS will depend on your preferences and requirements.

TODO: add here specific instructions later, such as on my old laptop I can install Proxmox VE, then on the others maybe a different OS, etc., think about that?

TODO: TOC here

## Prerequisites

Before beginning the installation, gather the following:

- [ ] USB flash drive (8GB minimum, 16GB recommended)
- [ ] ISO file of the chosen OS 
- [ ] USB creation tool (Rufus, balenaEtcher, or dd)
- [ ] Hardware to install on (e.g. old laptop, desktop, mini PC, etc.)

---

## Installation Process

### Creating a Bootable USB

1. **Download the ISO file of the chosen OS**:
   - Visit the official distribution website
   - Download the appropriate ISO file

2. **Download Rufus** or **balenaEtcher**:
   - Rufus: https://rufus.ie/
   - balenaEtcher: https://www.balena.io/etcher/

3. **Create Bootable USB**:
   - Insert USB drive (will be erased!)
   - Launch Rufus/Etcher (from laptop, not necessary to run from the USB itself!)
   - Select the ISO file
   - Select the USB drive as the device (probably listed as "NO LABEL (D:)" or similar)
   - Check other settings (default usually fine)
   - Click "Start" and wait for completion (click "OK" on any prompts)

### BIOS Configuration
The BIOS Configuration section explains how to access your hardware's firmware settings (BIOS/UEFI) to configure it for booting from USB. This is not a Windows application, it's a low-level system interface that exists before Windows even loads.

To configure these settings:

1. **Access BIOS/UEFI**:
   - Shut down your compute device completely (not restart)
   - Press the power button to turn it on
   - Immediately and repeatedly press one of these keys:
      - F2 (most common for Windows computers, in this experiment it was F2)
      - F12 (opens boot menu)
      - Del or Esc (alternative keys)
      - Watch the screen during boot, the computer usually shows a splash screen with the correct key

2. **Adjust Settings**:
   - **Boot Order**: Move USB to first position
   - **Secure Boot**: Disable (if present, may prevent Linux from booting)
     - **Important**: Security settings are often locked by default
     - If you cannot edit settings, you must first set a Supervisor Password:
       1. Select "Set Supervisor Password"
       2. Enter and confirm a new password
       3. **Write this password down** - you'll need it to access BIOS later (if you forget it, you may be locked out of BIOS and need to contact the manufacturer for a reset)
       4. Settings will now become editable
     - **Alternative Approach (I selected this option during the experiment)**: Skip this step and try installing Ubuntu with Secure Boot enabled (Ubuntu 24.04 LTS supports Secure Boot). Only return to disable Secure Boot if installation fails.
   - **Fast Boot**: Disable (helps with boot issues)
   - **Intel RST/Optane**: Change to AHCI mode (will otherwise cause installation issues on Ubuntu). 
      - If you're **erasing Windows** (Option 1 of Disk Partitioning), this change is completely safe and you do not need to back up any data
      - On some computers the option may be hidden. In this experiment (Acer laptop), pressing Ctrl+s revealed the option under Main > SATA Mode, where you could select AHCI.
      - On Ubuntu it may prompt you to disable it if you skip this step: [Intel RST (Rapid Storage Technology)](https://documentation.ubuntu.com/desktop/en/latest/reference/intel-rst-during-ubuntu-installation/)
   - You'll see a message: "Turn off RST" or "Change storage controller to AHCI"
   - **Legacy/UEFI Mode**: Note your current setting
     - Modern systems: Use UEFI
     - Older systems: May require Legacy/CSM mode

3. **Save and Exit** (usually F10)
---

### Booting from USB

It may already start from the USB if you set it as the first boot device in the previous step (skip the first steps). If not, you can manually follow the first steps to boot from the USB:

1. **Insert the bootable USB (if not done already)** into the computer
2. **Restart** the computer
3. **Select USB as boot device**:
   - Either from BIOS boot menu (F12, F9, or similar)
   - Or automatically if USB is first in boot order
4. **Select "Try or Install Linux Ubuntu" (the option to install Linux from the USB)** from the boot menu
5. **Follow on-screen instructions** to load the live environment or start installation. Follow the official installation guide for your chosen distribution for detailed steps, such as [Ubuntu Installation Guide](https://ubuntu.com/tutorials/install-ubuntu-desktop).

### Disk Partitioning

Choose your installation strategy:

#### Option 1: Erase Disk (Simplest)
- **Use Case**: No need to keep Windows
- **Result**: Entire disk used for Linux
- Select "Erase disk and install Linux" in the installer

#### Option 2: Dual Boot (Keep Windows)
- **Use Case**: Want both Windows and Linux
- **Steps**:
  1. Shrink Windows partition from Windows Disk Management first
  2. Create free space (50GB+ recommended for Linux)
  3. During Linux installation, select "Install alongside Windows"
  4. Or manually partition:
     - `/` (root): 25GB+ (ext4)
     - `/home`: Remaining space (ext4)
     - `swap`: 2GB or equal to RAM (swap)
     - `/boot/efi`: 512MB (if UEFI, FAT32)

#### Option 3: Manual Partitioning
```
Recommended partition scheme for standalone Linux:
/boot/efi   512MB   FAT32   (UEFI systems only)
/           30GB    ext4    (root filesystem)
swap        4GB     swap    (equal to RAM for hibernation)
/home       Rest    ext4    (user data)
```

#### Recommended Choice: Option 1 - Erase Disk
It is recommended to erase the disk and do a clean installation, since dual booting reduces the available disk space for Linux and adds complexity to the installation process. For a homelab environment, it's often more beneficial to have a dedicated Linux system without the overhead of maintaining a dual boot setup.

---

## Post-Installation Setup

### System Updates

First thing after installation:

```bash
# For Debian/Ubuntu-based distributions
sudo apt update
sudo apt upgrade -y

# For Arch-based distributions
sudo pacman -Syu

# For Fedora
sudo dnf update -y
```

TODO: when starting homelab, make the specific post install steps here, such as using a separate .md file for this!

### Restore Bootable USB back to normal use (optional):

1. Insert the USB drive back into your computer
2. Open File Explorer (Windows laptop or Linux does not really matter)
3. Select your USB drive on the left
4. Click the gear icon under the USB drive name and select Format
5. Choose Format Partition…
6. Select FAT32 (or exFAT if you want large file support) & Select overwrite existing data to get a clean USB drive
7. Click Format

If the USB has multiple partitions (common after using Rufus):
1. Click the minus (–) button to delete each partition
2. Then click the + button to create one new partition
3. Format it as FAT32

After that, the USB is completely normal again.

---

## Troubleshooting

### Common Issues and Solutions encountered:

#### Boot Issues
- **Problem**: System won't boot from USB
  - **Solution**: Check BIOS boot order, disable Secure Boot
  
- **Problem**: GRUB error after installation
  - **Solution**: Reinstall GRUB from live USB

- **Problem**: System freezes during boot, such as "Your device ran into a problem and needs to restart. We'll restart for you." 
  - **Solution**: This often happens if Intel RST driver was removed from Storage Controllers but BIOS is still in RST/Optane mode. Boot into Windows Safe Mode to restore:
    1. Power off the laptop completely
    2. Remove the USB drive
    3. Turn on and immediately start tapping **F8** or **Shift+F8** repeatedly to enter Windwos Recovery/Automatic Repair Mode. This can be tricky on modern laptops due to fast boot times, so you may need to try a few times. In this experiment, it went to a mode where it did not have a network connection and prompted to press Enter to see other recovery options. Here I selected Quick Repair and enabled Hotspot on my mobile phone for network connection.
    4. If that doesn't work, go back into the BIOS/UEFI settings and set the SATA Mode to AHCI and boot with Ubuntu on USB:
       - Press power button
       - Enter BIOS/UEFI (see steps above for explanation)
       - Change SATA Mode to AHCI as explained in the earlier steps for BIOS/UEFI configuration
       - Save and Exit
       - Boot from the USB with Linux, such as Ubuntu, and continue the installation
       - Repeat this 3 times - Windows will boot into Recovery mode

#### Hardware Issues
- **Problem**: Wi-Fi not working
  - **Solution**: Install proprietary drivers, use USB Wi-Fi adapter temporarily
  
- **Problem**: Screen resolution incorrect
  - **Solution**: Install graphics drivers, edit `/etc/X11/xorg.conf`

#### Performance Issues
- **Problem**: System slow/laggy
  - **Solution**: Check running processes with `htop`, disable unnecessary startup programs

#### Sound Issues
- **Problem**: No audio output
  - **Solution**: 
    ```bash
    # Check audio devices
    aplay -l
    
    # Restart audio service
    pulseaudio -k
    pulseaudio --start
    ```
---

## Resources

- [Article on how to install Linux on old hardware](https://www.linuxoperatingsystem.net/how-to-install-linux-os-on-your-old-pc/) - Full install guide on how to install Linux on old hardware
- [Article on installing Linux on Windows laptops](https://linuxvox.com/blog/how-to-install-ubuntu-from-windows/) - Guide on how to install Linux on Windows laptops
- [Ubuntu Documentation](https://documentation.ubuntu.com/) - Official Ubuntu documentation
- [Ubuntu Installation Guide](https://ubuntu.com/tutorials/install-ubuntu-desktop) - Official Ubuntu installation instructions
- [Linux Journey](https://linuxjourney.com/) - Interactive Linux learning   
- [The Linux Command Line](http://linuxcommand.org/) - Command line tutorial
- [DistroWatch](https://distrowatch.com/) - Linux distribution information

### Useful Commands Reference

```bash
# System information
uname -a                   # Kernel information
lsb_release -a             # Distribution information
df -h                      # Disk usage
free -h                    # Memory usage
lscpu                      # CPU information

# Package management (Debian/Ubuntu)
sudo apt update            # Update package list
sudo apt upgrade           # Upgrade packages
sudo apt install [package] # Install package
sudo apt remove [package]  # Remove package
sudo apt search [keyword]  # Search for package

# File operations
ls -lah                    # List files with details
cd [directory]             # Change directory
cp [source] [dest]         # Copy files
mv [source] [dest]         # Move/rename files
rm [file]                  # Remove file
mkdir [directory]          # Create directory

# System management
sudo systemctl status [service]  # Check service status
sudo systemctl start [service]   # Start service
sudo systemctl enable [service]  # Enable service at boot
journalctl -xe                   # View system logs
```

---
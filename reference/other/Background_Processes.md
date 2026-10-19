# Background Processes and tmux

A process normally belongs to the session that started it. Closing an interactive terminal can send a hangup signal to its jobs, so a command may stop when an SSH connection or terminal closes. Choose a process-lifecycle method according to whether the work is a short command, an interactive task that needs reconnection, or a service that must survive logout/reboot and start reliably.

This page follows DevHub's [scope and tool-specificity design](../README.md#scope-and-tool-specificity). It explains the general background-process concepts first, then includes a focused tmux section because tmux is a personally preferred tool for retaining and reconnecting to interactive terminal sessions. The tmux settings below are personal defaults, not universal recommendations; use the [official tmux documentation](https://github.com/tmux/tmux/wiki) and manual pages for complete current behavior.

---

## Table of Contents

- [Background Process Options](#background-process-options)
- [tmux](#tmux)
  - [Installation](#installation)
  - [Personal Configuration](#personal-configuration)
  - [Daily Usage](#daily-usage)
  - [Scrollback and Copy Mode](#scrollback-and-copy-mode)
  - [Capture Output](#capture-output)

---

## Background Process Options

| Method | What it provides | Suitable for | Important limitations |
|---|---|---|---|
| Shell job control (`&`, `jobs`, `fg`, `bg`) | Runs a job asynchronously in the current shell and lets the shell manage it. | Short-lived work while the shell remains open. | The job is still associated with that shell; closing the terminal can end it. |
| `nohup` | Starts a command ignoring the hangup signal and commonly redirects terminal output. | A simple non-interactive command that should continue after logout. | Does not provide an interactive reconnectable terminal, supervision, automatic restart or reboot persistence. Manage output files and process cleanup deliberately. |
| `disown` | Removes a shell job from the shell's job table or prevents it receiving a shell's hangup signal, depending on shell/options. | A command already running in a shell when detaching is needed. | Shell behavior varies; it does not provide session reattachment, service supervision or reboot persistence. |
| Terminal multiplexer (for example, tmux) | Keeps a terminal session on a server so a client can detach and reattach later. | Interactive commands, remote administration and long-running tasks that need a terminal. | The process/session generally ends if the host reboots or the tmux server is stopped. It does not replace a service manager or backup/recovery design. |
| Service manager (for example, systemd) | Defines a service's startup, dependencies, restart policy, identity and logging. | Long-running services that should start at boot and be operated consistently. | Requires a service definition and appropriate permissions; use the OS/service manager's documentation and avoid wrapping one-off interactive work as a service without need. |

Select the behavior deliberately. A shell background job is not equivalent to a daemon; tmux protects an interactive session from client disconnects but does not guarantee the work will survive host failure or reboot. For unattended services, use the platform's service-management facilities and an explicit restart, logging and shutdown policy.

---

## tmux

tmux is a terminal multiplexer: it keeps terminal sessions running on the host while clients detach and reconnect. It is useful for interactive operational tasks such as upgrades, troubleshooting or commands that should continue when an SSH connection drops. For non-interactive long-running services, use the OS service manager instead.

### Installation

```bash
# Debian/Ubuntu
sudo apt install tmux

# Fedora/RHEL family (package availability and package manager depend on release)
sudo dnf install tmux
```

---

### Personal Configuration

Edit your tmux config file:

```bash
vim ~/.tmux.conf
```

Add these useful defaults:

```bash
# Increase scrollback buffer for all tmux sessions
set -g history-limit 200000

# Enable mouse support for scrolling and selecting text
set -g mouse on

# Use vi-style key bindings in copy mode
setw -g mode-keys vi
```

> **Note:** With mouse mode enabled, normal terminal selection and paste actions may require holding Shift, for example Shift + mouse select or Shift + right-click paste.

Reload and verify the configuration:

```bash
tmux source-file ~/.tmux.conf
tmux show-options -g | grep history-limit
tmux show-options -gw | grep mode-keys
```

If the config still does not apply, you can restart the tmux server, but this stops all tmux sessions:

```bash
tmux kill-server
```

---

### Daily Usage

| Action | Command / shortcut |
|--------|-------------------|
| Start a named session | `tmux new-session -s upgrade` |
| Detach from a session | `Ctrl + b`, then `d` |
| List sessions | `tmux ls` |
| Reconnect to a session | `tmux attach -t upgrade` |
| Attach if it exists, otherwise create it | `tmux new-session -A -s upgrade` |
| Stop the current session from inside tmux | `exit` |
| Stop a session from outside tmux | `tmux kill-session -t upgrade` |

---

### Scrollback and Copy Mode

Enter copy mode to scroll through history:

`Ctrl + b`, then `[`

Useful vi-style navigation keys:

| Key | Action | Key | Action |
|-----|--------|-----|--------|
| `h` / `j` / `k` / `l` | Move left / down / up / right | `w` / `b` / `e` | Move by word |
| `0` / `^` / `$` | Move to beginning / first non-blank / end of line | `Ctrl + f` | Page down |
| `Ctrl + b` | Page up | `gg` | Go to top |
| `Shift + g` | Jump back to live output / bottom | `/text` / `?text` | Search forward / backward |
| `n` / `N` | Next / previous match | `q` | Exit copy mode |

---

### Capture Output

To save the current pane output, including scrollback history, run this inside the tmux session:

```bash
tmux capture-pane -p -S - > ~/tmp/tmux-output.txt
```

Copy the captured output to your clipboard if available:

```bash
xclip -selection clipboard -i ~/tmp/tmux-output.txt
```

If clipboard access is unavailable, for example in a secured environment without a display, print the file and copy it manually OR copy the file from the secured environment to your local computer with FileTrans and WinSCP (if available):

```bash
cat ~/tmp/tmux-output.txt
```

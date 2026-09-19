# tmux Quick Reference

A concise guide for installing tmux, applying a practical personal configuration, using sessions, scrolling through history, and capturing output.

tmux is a terminal multiplexer: it lets you keep shell sessions running in the background, detach from them, and reconnect later. It is especially useful for operational tasks such as long-running upgrades, troubleshooting sessions, or commands that must continue even if your SSH connection drops.

See for more details for example: [tmux Wiki](https://github.com/tmux/tmux/wiki), [Getting Started with tmux](https://linuxize.com/post/getting-started-with-tmux/), [tmux in Linux](https://www.geeksforgeeks.org/linux-unix/tmux-in-linux/)

## Installation

```bash
# Debian/Ubuntu
sudo apt install tmux

# CentOS/RHEL
sudo yum install tmux
```

## Recommended personal configuration

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

## Daily usage

| Action | Command / shortcut |
|--------|-------------------|
| Start a named session | `tmux new-session -s upgrade` |
| Detach from a session | `Ctrl + b`, then `d` |
| List sessions | `tmux ls` |
| Reconnect to a session | `tmux attach -t upgrade` |
| Attach if it exists, otherwise create it | `tmux new-session -A -s upgrade` |
| Stop the current session from inside tmux | `exit` |
| Stop a session from outside tmux | `tmux kill-session -t upgrade` |

## Scrollback and copy mode

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

## Capture output

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

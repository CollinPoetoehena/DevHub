# DevHub Installation

This is the central entry point for installing DevHub resources locally. A single [install.py](./install.py) contains installation, uninstall, and focused component functions; currently it installs personal Copilot skills and agents only. Future components could install shared command-line utilities into a user-local tools directory without coupling them to AI customization setup.

## Table of contents

- [Requirements and trust](#requirements-and-trust)
- [Why Python](#why-python)
- [Install](#install)
  - [Verify the installation](#verify-the-installation)
- [Run at shell login](#run-at-shell-login)
- [Updates, ownership, and recovery](#updates-ownership-and-recovery)
- [Uninstall](#uninstall)
- [Extend and test](#extend-and-test)

---

## Requirements and trust

The installer targets Linux and WSL with Python 3.10 or newer and Git. All Python dependencies are in the standard library; no pip packages, root privileges, GNU `timeout`, or external `flock` command are required. Native Windows and macOS are not supported by this implementation; locking uses Python's Unix `fcntl` module.

Installation automatically downloads the latest `main` branch from DevHub and runs its installer code. Enable login updates only if you trust that source and your device's policies permit personal customizations. This trades review-before-update for automatic freshness; a compromised upstream installer can run with your user's permissions. It does not install third-party skills or change project repositories.

Install on the machine where Copilot runs, including separately inside WSL or a remote development environment. The host must support personal customizations and symbolic-link discovery. Verify the installed agents in the picker and skills in the supported customization UI; installation alone cannot guarantee host discovery or activation.

---

## Why Python

Python makes the installer easier to read, understand, and maintain as it grows: path handling, process execution, temporary directories, file replacement, error handling, locking, and testing are expressed through consistent language APIs rather than stitched together from shell syntax and external commands. Its standard library also provides the functionality needed here without adding third-party dependencies. Component operations can remain as named functions in one file, which keeps installation and uninstall logic together while making new components straightforward to add and test.

Python 3 is commonly preinstalled or readily available on Linux and WSL development systems, where this installer currently runs. It is still an explicit prerequisite—not guaranteed on every minimal system—so install Python 3.10+ before using the script if `python3` is unavailable. The shell login hook remains a short launcher; the installation logic itself is Python.

The shell still starts the installer at login; it does not contain installation logic. Python does not remove the need for ownership checks or make downloaded code safe: the same trust and authorization boundaries apply.

---

## Install

> DevHub is public, so anyone can view and clone the repository (see [DevHub README.md](../README.md)).

From an existing DevHub checkout, run:

```sh
python3 /path/to/DevHub/install/install.py
```

The checkout is used only to start the bootstrap: it is never fetched, pulled, switched, or modified. The installer resolves GitHub's `main`, downloads a separate temporary clone when that commit is not already cached, and removes the temporary checkout on exit.

Alternatively, bootstrap without a development clone, after reviewing the source:

```sh
(
    set -eu
    temporary="$(mktemp -d)"
    trap 'rm -rf -- "$temporary"' EXIT
    git clone --depth 1 --branch main https://github.com/CollinPoetoehena/DevHub.git "$temporary/DevHub"
    python3 "$temporary/DevHub/install/install.py"
)
```

These commands require the installation files to have been published to DevHub's `main` branch. For an alternative source or branch, pass `--source REPOSITORY --ref BRANCH`; use the same arguments on subsequent runs, including in a login hook. These options are explicit overrides, not changes to an existing checkout.

The installed bootstrap is `${XDG_DATA_HOME:-$HOME/.local/share}/devhub/install.py`. Customizations are copied into persistent, commit-specific snapshots there, then linked individually into `~/.copilot/skills/` and `~/.copilot/agents/`. Links never point at the temporary clone or your development clone. Complete skill directories and the agents folder are retained, including supporting resources. The downloaded revision's component functions are used immediately and its Python file becomes the installed bootstrap for future updates and uninstall.

### Verify the installation

After a successful install, inspect the customization links and recorded installation state:

```sh
ls -ltr "$HOME/.copilot/skills/" "$HOME/.copilot/agents/"
cat "${XDG_DATA_HOME:-$HOME/.local/share}/devhub/installed-commit"
cat "${XDG_DATA_HOME:-$HOME/.local/share}/devhub/ai-links"
readlink -f "${XDG_DATA_HOME:-$HOME/.local/share}/devhub/current"
```

The `devhub-*` entries should be symbolic links through `devhub/current/ai/`. The recorded commit should match the installer's success message, and `current` should resolve to the corresponding `releases/<commit>` directory. The manifest lists the customization destinations managed by DevHub; unrelated personal customizations may also appear in the directory listing.

Confirm that a skill's content is readable through its installed link:

```sh
head -n 15 "$HOME/.copilot/skills/devhub-docs/SKILL.md"
```

Finally, open a consuming repository in your supported Copilot host and check that the DevHub agents appear in the agent picker and the skills appear in its customization UI (e.g. in Copilot chat use `/<devhub-skill>`, such as `/devhub-docs`). Refresh or restart the Copilot session if needed, then try a relevant task with a DevHub skill or agent. Filesystem checks verify installation, not host discovery or activation.

---

## Run at shell login

Adding the login hook automates keeping your personal Copilot customizations aligned with the latest version on the selected DevHub branch. It checks for changes whenever you start a login shell and updates the installed setup when a newer commit is available, so you do not need to remember to run the installer manually. It follows the branch's latest published revision; use this only when you trust automatic updates from that source.

After a successful first installation, add this block to your existing Bash login file (`~/.bash_profile`, `~/.bash_login`, or `~/.profile`, whichever Bash already reads), or `~/.zprofile` for Zsh. Do not create a new Bash login file that unintentionally hides an existing one. The installer does not edit shell startup files for you.

```sh
# My personal preferences (e.g. AI customizations, etc.), maintained in DevHub: https://github.com/CollinPoetoehena/DevHub
if ! python3 "${XDG_DATA_HOME:-$HOME/.local/share}/devhub/install.py"; then
    printf '%s\n' 'DevHub update failed; inspect the error above. Previous installed files remain available.' >&2
fi
```

This checks GitHub at each login, not each prompt. It does not affect existing development clones. Network resolution is limited to 30 seconds and clone operations to 120 seconds; concurrent installer runs wait up to 30 seconds for a lock. A failed update reports an error without preventing the rest of your login file from running. Existing installed files remain on disk, but a failed partial reconciliation may need a retry.

An editor terminal is not necessarily a login shell, and opening VS Code need not trigger this block. Run the installed bootstrap manually when needed. Restart or refresh the relevant Copilot session if it does not discover changes immediately. This is login-time convergence, not a continuously running updater.

Keep `python3` available in the login shell's PATH, or replace it with your chosen interpreter's absolute path.

---

## Updates, ownership, and recovery

- `installed-commit` records the Git commit only after all current components and the installed bootstrap complete successfully. Cached snapshots avoid re-cloning an unchanged revision; link reconciliation still runs to repair missing links.
- `ai-links` records the relative destinations managed by the AI installer. It removes an obsolete link only if the link still points to DevHub's managed source. Manually replaced entries and unrelated personal customizations are preserved.
- A conflicting existing file, directory, or differently targeted link at a desired destination fails installation explicitly. Review and move that item aside yourself, then retry. Existing copies and links from the earlier manual installation instructions are also conflicts; the installer does not assume ownership of them.
- Offline or failed downloads leave the installed snapshot usable and do not record the failed revision. Retry when connectivity returns. State, snapshots, and the installed bootstrap live together under the user data directory; keep `XDG_DATA_HOME` consistent between installation and login.
- Do not edit managed snapshots or generated links; upstream updates select another snapshot. Develop changes in your own DevHub clone and publish them separately.
- Commit snapshots are retained for inspection while installed; there is no automatic cache pruning. Use the uninstaller below to remove managed snapshots and customizations.

---

## Uninstall

First remove the DevHub login block from your shell startup file so it no longer attempts updates. Then use the same installed Python file with `--uninstall`; it works offline and does not require Git or a development clone:

```sh
python3 "${XDG_DATA_HOME:-$HOME/.local/share}/devhub/install.py" --uninstall
```

Alternatively, use `python3 /path/to/DevHub/install/install.py --uninstall`, including for repeated cleanup after the installed bootstrap has been removed.

The central uninstall function runs component uninstall functions in reverse installation order. Currently it removes AI links only when their destinations and exact targets match the ownership manifest, then removes the managed active pointer, marked DevHub commit snapshots, installed Python file, and commit state. Personal replacements, unrelated Copilot content, and unrecognized cache entries are preserved and reported. Empty parent directories and the lock file remain to avoid deleting user-owned directories or racing waiting installers. Shell startup files are never edited automatically.

---

## Extend and test

Add paired `install_<component>` and `uninstall_<component>` functions to [install.py](./install.py). Call installers from `apply_release` in dependency order and uninstallers from `uninstall` in reverse order. Keeping orchestration and components in one file avoids script-to-script contracts and makes the installed bootstrap self-contained; more functions can be added without introducing a plugin framework.

Each component must preserve unrelated user data, report conflicts and failures, reconcile its own state idempotently, and remove only artifacts it owns. Components must not record overall success themselves. If a component needs source files beyond the currently copied installer and AI folders, extend `prepare_release`. Test both installation and uninstall, including personal replacements and repeated runs.

Run the isolated regression tests without network access or changes to your actual home (the `install/tests` directory contains the tests for the installation and uninstallation process):

```sh
python3 -B -m unittest discover -s install/tests -v
```

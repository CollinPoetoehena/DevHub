#!/usr/bin/env python3
"""Install, update, and uninstall DevHub customizations for the current user.

Purpose and source of truth
---------------------------
DevHub keeps reusable customizations (currently skills and agents) in its Git
repository. This script is the single Python entry point that brings those files
into the current user's Copilot customization directories and keeps them aligned
with a selected DevHub branch. The checked-out remote revision is the source of
truth; installation does not modify the user's DevHub working tree.

The script can be run manually with Python, or called by a small login-shell
snippet. The shell snippet is only a trigger: revision lookup, downloading,
locking, filesystem changes, ownership tracking, and uninstall behavior all live
here. A regular install resolves the selected branch to a commit and downloads
only when that exact commit is not already cached. It does not fetch or change
the user's separate local DevHub clone.

Why the installation logic is Python
-------------------------------------
Python's standard library provides readable path and filesystem APIs, safe
symbolic-link inspection, subprocess timeouts, atomic file replacement, and
process locking. Keeping these related operations in one maintainable program
makes the installation and recovery rules easier to understand and test than
scattering them through shell startup commands. Python 3 is commonly available
on Linux and WSL systems; Python is used for the actual installation logic, not
as a requirement to embed a large program in the login shell.

Managed installation layout
----------------------------
The user's data directory (``$XDG_DATA_HOME/devhub`` or
``~/.local/share/devhub``) contains:

* ``releases/<commit>/``: immutable, commit-named snapshots with a marker file
  used to recognize installer-owned cache entries;
* ``current``: a symlink to the active release, switched atomically during an
  update so existing customization links keep a stable destination;
* ``ai-links``: a manifest of the skill and agent paths this installer owns;
* ``installed-commit``: the commit last applied, suitable for a login hook to
  compare before invoking an update;
* ``install.py``: the installed version of this program, copied from the
  selected release for subsequent local use.

Skills and agents are linked below ``~/.copilot/``. The installer only manages
DevHub-namespaced entries (currently ``devhub-*``) and does not claim unrelated
Copilot files or remove empty parent directories.

Safety and failure behavior
---------------------------
The installer deliberately favors preserving user data over silently repairing
an ambiguous state:

* Existing files or links at a desired customization path are treated as
  conflicts unless the ownership manifest and link target identify them as
  DevHub-managed. Conflicts stop the install and are reported for review.
* The ownership manifest is validated before it is used. Cleanup only unlinks
  entries that still point to the expected managed location; personal
  replacements are preserved and reported.
* Releases are downloaded into temporary locations, checked against the
  resolved commit, marked, and then published by an atomic rename. A partially
  downloaded checkout is therefore not mistaken for a usable release.
* An exclusive process lock serializes login-triggered and manual operations.
  Individual state files are replaced atomically to avoid leaving truncated
  metadata after interruption.
* Git prompts are disabled and operations have time limits. Download, validation,
  filesystem, and conflict errors are printed to stderr and return a failure
  exit status; they are not converted into a success-shaped result.

These checks are local integrity and ownership safeguards, not a signature
verification system. Users should only install from a DevHub source and branch
they trust. ``--source`` and ``--ref`` intentionally allow selecting another
trusted repository or branch.

Extending the installer
-----------------------
Keep this as the one installation program and add a focused install function for
each future component. Call component install functions from ``apply_release``
in dependency order and corresponding uninstall functions from ``uninstall`` in
reverse order. Each component should track its own managed files and remove only
those files during uninstall. Component logic should remain idempotent so manual
runs, login checks, and recovery after interruption all converge to the same
state.

Usage
-----
Run ``python3 install/install.py`` to install/update from the default DevHub
repository's ``main`` branch. Use ``--source URL`` and ``--ref BRANCH`` to select
another trusted source. Run ``python3 install/install.py --uninstall`` to remove
the managed installation offline. Uninstall does not remove the user's login
snippet; that snippet must be removed separately to stop future update checks.
"""

import argparse
from contextlib import contextmanager
import fcntl
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Iterator


SOURCE = "https://github.com/CollinPoetoehena/DevHub.git"
COMMIT = re.compile(r"[0-9a-f]{40,64}")
ENTRY = re.compile(r"(skills/devhub-[a-z0-9.-]+|agents/devhub-[a-z0-9.-]+\.agent\.md)")


def locations() -> tuple[Path, Path]:
    # Keep a single managed data directory under the user's home, which makes
    # uninstall/reinstall and shell-login convergence predictable across updates.
    home = Path(os.environ.get("HOME") or Path.home())
    base = Path(os.environ.get("XDG_DATA_HOME") or home / ".local/share")
    if not home.is_absolute() or not base.is_absolute():
        raise ValueError("HOME and XDG_DATA_HOME must resolve to absolute paths.")
    return home, base / "devhub"


@contextmanager
def installation_lock(data: Path) -> Iterator[None]:
    # A simple process lock prevents two login-triggered or manual installs from
    # racing each other while they reconcile the same symlinks and cache entries.
    data.mkdir(parents=True, exist_ok=True)
    with (data / "install.lock").open("a") as lock:
        deadline = time.monotonic() + 30
        while True:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("Another DevHub installation is running.") from None
                time.sleep(0.1)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def git(*arguments: str, timeout: int = 30) -> str:
    # The installer intentionally uses a tiny wrapper so callers can rely on a
    # consistent timeout and quiet prompts for networked Git operations.
    environment = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    result = subprocess.run(
        ["git", *arguments], env=environment, capture_output=True,
        text=True, check=True, timeout=timeout,
    )
    return result.stdout.strip()


def atomic_write(target: Path, content: str) -> None:
    # Write via a temporary sibling file and replace atomically so a crash does not
    # leave truncated state files behind.
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=target.parent, delete=False
    ) as temporary:
        temporary.write(content)
        name = Path(temporary.name)
    try:
        name.replace(target)
    finally:
        name.unlink(missing_ok=True)


def exists(path: Path) -> bool:
    # Path.exists() is false for dangling symlinks, but those still occupy a name
    # and must be treated as existing during conflict and cleanup checks.
    return path.exists() or path.is_symlink()


def owned_link(target: Path, expected: Path) -> bool:
    # Managed links must point to the exact cached DevHub snapshot path for the
    # active release, not just any symlink in the same folder.
    return target.is_symlink() and os.readlink(target) == str(expected)


def manifest_entries(data: Path) -> set[str]:
    # The ownership manifest lists the current managed customization entries for the
    # installed release. It is the source of truth for safe cleanup and conflict checks.
    manifest = data / "ai-links"
    if not manifest.exists():
        return set()
    entries = set(manifest.read_text(encoding="utf-8").splitlines())
    for entry in entries:
        if not ENTRY.fullmatch(entry):
            raise ValueError(f"Invalid ownership manifest entry: {entry}")
    return entries


def marked_release(release: Path) -> bool:
    # Require a real directory and a matching marker before deleting any cache
    # entry; a similarly named user-created path is not installer-owned.
    marker = release / ".devhub-release"
    return bool(
        COMMIT.fullmatch(release.name) and release.is_dir()
        and not release.is_symlink() and marker.is_file()
        and not marker.is_symlink()
        and marker.read_text(encoding="utf-8").strip() == release.name
    )


def prepare_release(data: Path, source: str, ref: str) -> tuple[Path, str]:
    # Resolve the target commit and use a commit-named cached snapshot so repeated
    # updates can reuse the same release instead of re-cloning unchanged revisions.
    remote = git("ls-remote", "--exit-code", "--refs", source, f"refs/heads/{ref}")
    lines = remote.splitlines()
    commit = lines[0].split("\t")[0] if len(lines) == 1 else ""
    if not COMMIT.fullmatch(commit):
        raise ValueError(f"Could not resolve a single branch commit: {ref}")
    releases = data / "releases"
    releases.mkdir(exist_ok=True)
    release = releases / commit
    if exists(release):
        if not marked_release(release) or not (release / "install/install.py").is_file():
            raise ValueError(f"Refusing to use an unrecognized cached release: {release}")
        return release, commit
    with tempfile.TemporaryDirectory(prefix="devhub-checkout-") as checkout:
        repository = Path(checkout) / "repository"
        git("clone", "--quiet", "--depth", "1", "--single-branch", "--branch",
            ref, "--", source, str(repository), timeout=120)
        if git("-C", str(repository), "rev-parse", "HEAD") != commit:
            raise ValueError("Remote branch changed during download; retry installation.")
        # Stage on the destination filesystem so publication is an atomic rename.
        with tempfile.TemporaryDirectory(prefix=".staging-", dir=releases) as staging:
            snapshot = Path(staging) / "snapshot"
            snapshot.mkdir()
            (snapshot / ".devhub-release").write_text(commit + "\n", encoding="utf-8")
            shutil.copytree(repository / "install", snapshot / "install")
            for kind in ("skills", "agents"):
                source_directory = repository / ".github" / kind
                destination = snapshot / "ai" / kind
                if source_directory.is_dir():
                    shutil.copytree(source_directory, destination)
                else:
                    destination.mkdir(parents=True)
            snapshot.rename(release)
    return release, commit


def install_ai_customizations(home: Path, data: Path, release: Path) -> None:
    # Discover only explicitly DevHub-namespaced customization formats. This lets
    # new DevHub skills and agents join the install automatically without claiming
    # arbitrary user or repository files.
    desired = {
        f"skills/{skill.parent.name}"
        for skill in (release / "ai/skills").glob("devhub-*/SKILL.md")
        if skill.is_file()
    }
    desired.update(
        f"agents/{agent.name}"
        for agent in (release / "ai/agents").glob("devhub-*.agent.md")
        if agent.is_file()
    )
    for entry in desired:
        if not ENTRY.fullmatch(entry):
            raise ValueError(f"Unsupported customization name: {entry}")
    previous = manifest_entries(data)

    # Validate every destination before changing any of them, so a conflict does
    # not leave only part of the requested customization set installed.
    conflicts = []
    for entry in sorted(desired):
        target = home / ".copilot" / entry
        if exists(target) and not owned_link(target, data / "current/ai" / entry):
            conflicts.append(str(target))
    if conflicts:
        raise ValueError("Conflict: refusing to replace personal customizations:\n"
                         + "\n".join(conflicts) + "\nMove them aside after review and retry.")
    current = data / "current"
    if exists(current) and not current.is_symlink():
        raise ValueError(f"Refusing to replace non-symlink: {current}")

    # Create only the expected Copilot parents; customization destinations
    # themselves are created as links below.
    for kind in ("skills", "agents"):
        (home / ".copilot" / kind).mkdir(parents=True, exist_ok=True)

    # Journal both old and new ownership before switching the release pointer.
    # If interrupted later, the next run or uninstall can still identify links
    # created by this operation.
    atomic_write(data / "ai-links", "".join(e + "\n" for e in sorted(previous | desired)))

    # Create the new pointer beside the old one and replace it atomically. All
    # customization links refer through this stable path, so switching releases
    # updates their contents together without recreating each link.
    with tempfile.TemporaryDirectory(prefix=".current-", dir=data) as temporary:
        pointer = Path(temporary) / "link"
        pointer.symlink_to(release, target_is_directory=True)
        pointer.replace(current)
    for entry in sorted(desired):
        target = home / ".copilot" / entry
        if not target.is_symlink():
            target.symlink_to(data / "current/ai" / entry,
                             target_is_directory=entry.startswith("skills/"))
    # Remove entries deleted from the new DevHub revision only if they still
    # point through the managed current path. Preserve anything a user replaced.
    for entry in sorted(previous - desired):
        target = home / ".copilot" / entry
        if owned_link(target, data / "current/ai" / entry):
            target.unlink()
        elif exists(target):
            print(f"Preserving replaced, formerly managed customization: {target}")
    atomic_write(data / "ai-links", "".join(e + "\n" for e in sorted(desired)))


def uninstall_ai_customizations(home: Path, data: Path) -> None:
    # Uninstall is intentionally offline. Use the recorded manifest and compare
    # exact symlink destinations instead of querying the source repository.
    for entry in sorted(manifest_entries(data)):
        target = home / ".copilot" / entry
        if owned_link(target, data / "current/ai" / entry):
            target.unlink()
        elif exists(target):
            print(f"Preserving personal replacement: {target}")
    (data / "ai-links").unlink(missing_ok=True)


def apply_release(home: Path, data: Path, release: Path, commit: str) -> None:
    # Install components in dependency order. Keep state publication last so the
    # recorded commit means all component reconciliation completed successfully.
    install_ai_customizations(home, data, release)
    atomic_write(data / "install.py",
                 (release / "install/install.py").read_text(encoding="utf-8"))
    atomic_write(data / "installed-commit", commit + "\n")
    print(f"DevHub installation is current at {commit}")


def uninstall(home: Path, data: Path) -> None:
    # Uninstall components in reverse dependency order so dependents can clean up
    # before any shared resources they rely on.
    uninstall_ai_customizations(home, data)
    current = data / "current"
    if current.is_symlink():
        target = Path(os.readlink(current))
        # The target must be exactly one of our commit-named releases; do not
        # unlink a pointer that has been replaced or redirected by the user.
        if COMMIT.fullmatch(target.name) and target == data / "releases" / target.name:
            current.unlink()
        else:
            print(f"Preserving replaced current pointer: {current}")
    elif current.exists():
        print(f"Preserving non-managed current directory: {current}")
    releases = data / "releases"
    if releases.is_dir():
        # Remove only releases bearing our marker. Leave unexpected cache entries
        # untouched rather than treating the whole data directory as disposable.
        for release in releases.iterdir():
            if marked_release(release):
                shutil.rmtree(release)
            else:
                print(f"Preserving unrecognized cache entry: {release}")
    for name in ("install.py", "installed-commit"):
        (data / name).unlink(missing_ok=True)
    print("DevHub uninstalled. Remove its login-shell block to stop future update attempts.")
    # Keep the lock inode to avoid races with waiting processes.


def main() -> int:
    # Parse source selection before touching the filesystem; argparse also
    # provides the standard help and invalid-option behavior.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=SOURCE, help="Git repository to download")
    parser.add_argument("--ref", default="main", help="Branch to track")
    parser.add_argument("--uninstall", action="store_true", help="Remove managed installation offline")
    args = parser.parse_args()
    if not sys.platform.startswith("linux"):
        parser.error("This installer currently supports Linux and WSL only.")
    try:
        home, data = locations()
        # Avoid creating installer state merely to report that there is nothing
        # to uninstall.
        if args.uninstall and not data.exists():
            print("DevHub is not installed.")
            return 0
        with installation_lock(data):
            if args.uninstall:
                uninstall(home, data)
            else:
                release, commit = prepare_release(data, args.source, args.ref)
                # Execute component logic from the selected release, not stale
                # functions bundled in a previously installed bootstrap copy.
                functions = runpy.run_path(str(release / "install/install.py"))
                functions["apply_release"](home, data, release, commit)
        return 0
    except subprocess.CalledProcessError as error:
        print(f"Git failed ({error.returncode}): {error.stderr.strip()}", file=sys.stderr)
    except subprocess.TimeoutExpired as error:
        print(f"Git operation exceeded {error.timeout} seconds.", file=sys.stderr)
    except (OSError, ValueError) as error:
        print(f"DevHub installation failed: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

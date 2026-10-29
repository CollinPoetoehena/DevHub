#!/usr/bin/env python3
"""Update a trusted DevHub clone and link its Copilot files into a personal workspace.

Requires Linux/WSL, Python 3.10+, and Git. Uses no packages or user-global
customizations. Run with --workspace PATH; --no-pull applies the clean local
checkout offline, and --uninstall removes only recorded, unchanged links.
"""

import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import tempfile


ENTRY = re.compile(
    r"copilot-instructions\.md|instructions/[a-z0-9.-]+\.instructions\.md"
    r"|skills/devhub-[a-z0-9.-]+|agents/devhub-[a-z0-9.-]+\.agent\.md"
)
STATE = ".devhub-setup.json"
# Canonical customization sources; the clone's .github/ entries are symlinks to them.
CUSTOMIZATIONS = Path("docs/copilot")


def git(source: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(source), *arguments],
        env=dict(os.environ, GIT_TERMINAL_PROMPT="0"),
        text=True, capture_output=True, check=True, timeout=30,
    )
    return result.stdout.strip()


def atomic_write(path: Path, content: str) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as temporary:
        name = Path(temporary.name)
        try:
            temporary.write(content)
        except OSError:
            name.unlink(missing_ok=True)
            raise
    try:
        name.replace(path)
    finally:
        name.unlink(missing_ok=True)


def directory(path: Path) -> None:
    if path.is_symlink():
        raise ValueError(f"Refusing a symlinked destination directory: {path}")
    path.mkdir(exist_ok=True)


def read_state(path: Path, source: Path) -> set[str]:
    if path.is_symlink():
        raise ValueError(f"Refusing a symlinked state file: {path}")
    if not path.exists():
        return set()
    state = json.loads(path.read_text(encoding="utf-8"))
    if (
        not isinstance(state, dict)
        or state.get("version") != 1
        or state.get("source") != str(source)
        or not isinstance(state.get("entries"), list)
        or any(not isinstance(e, str) or not ENTRY.fullmatch(e) for e in state["entries"])
    ):
        raise ValueError(
            f"Invalid setup state or different source clone: {path}. "
            "Uninstall using the original clone before changing its location."
        )
    return set(state["entries"])


def write_state(path: Path, source: Path, entries: set[str], commit: str | None) -> None:
    atomic_write(path, json.dumps({
        "version": 1, "source": str(source), "entries": sorted(entries),
        "commit": commit,
    }, indent=2) + "\n")


def owned_link(path: Path, target: Path) -> bool:
    return path.is_symlink() and os.readlink(path) == str(target)


def desired_entries(source: Path) -> set[str]:
    root = source / CUSTOMIZATIONS
    baseline = root / "copilot-instructions.md"
    if not baseline.is_file():
        raise ValueError(f"Missing baseline instructions: {baseline}")
    entries = {"copilot-instructions.md"}
    for path in (root / "instructions").glob("*.instructions.md"):
        entries.add(path.relative_to(root).as_posix())
    for path in (root / "agents").glob("devhub-*.agent.md"):
        entries.add(path.relative_to(root).as_posix())
    for path in (root / "skills").glob("devhub-*/SKILL.md"):
        entries.add(path.parent.relative_to(root).as_posix())
    for entry in entries:
        if not ENTRY.fullmatch(entry):
            raise ValueError(f"Unsupported customization name: {entry}")
        path = root / entry
        if not path.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"Customization points outside the clone: {path}")
        if not (path.is_dir() if entry.startswith("skills/") else path.is_file()):
            raise ValueError(f"Invalid customization: {path}")
    return entries


def synchronize(source: Path, workspace: Path, uninstall: bool) -> None:
    root = workspace / ".github"
    state = root / STATE
    previous = read_state(state, source)
    desired = set() if uninstall else desired_entries(source)
    for kind in sorted({e.split("/")[0] for e in previous | desired if "/" in e}):
        directory(root / kind)

    conflicts = [
        str(root / e) for e in sorted(desired)
        if ((root / e).exists() or (root / e).is_symlink())
        and not (e in previous and owned_link(root / e, source / CUSTOMIZATIONS / e))
    ]
    if conflicts:
        raise ValueError(
            "Conflict: move these files aside after review, then retry:\n"
            + "\n".join(conflicts)
        )
    if not uninstall:
        # Journal ownership before changing links, so interrupted runs can recover.
        write_state(state, source, previous | desired, None)
    for entry in sorted(desired):
        path = root / entry
        if not path.is_symlink():
            path.symlink_to(source / CUSTOMIZATIONS / entry,
                            target_is_directory=entry.startswith("skills/"))
    for entry in sorted(previous - desired):
        path = root / entry
        if owned_link(path, source / CUSTOMIZATIONS / entry):
            path.unlink()
        elif path.exists() or path.is_symlink():
            print(f"Preserving personal replacement: {path}", file=sys.stderr)
    if uninstall:
        state.unlink(missing_ok=True)
        print("DevHub workspace links removed. Remove the shell hook to stop updates.")
    else:
        commit = git(source, "rev-parse", "HEAD")
        write_state(state, source, desired, commit)
        print(f"DevHub workspace is current at {commit}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True,
                        help="Existing personal-only workspace parent directory")
    parser.add_argument("--no-pull", action="store_true",
                        help="Apply a clean local checkout without network access")
    parser.add_argument("--uninstall", action="store_true",
                        help="Remove recorded workspace links offline; keep the clone")
    args = parser.parse_args()
    if not sys.platform.startswith("linux"):
        parser.error("This script supports Linux and WSL only.")
    source = Path(__file__).resolve().parents[1]
    workspace = args.workspace.expanduser().resolve()
    try:
        if not workspace.is_dir() or workspace.is_relative_to(source):
            raise ValueError("Choose an existing personal workspace outside the DevHub clone.")
        if Path(git(source, "rev-parse", "--show-toplevel")).resolve() != source:
            raise ValueError("Run tools/setup.py from a DevHub Git clone.")
        root = workspace / ".github"
        if args.uninstall and not root.exists() and not root.is_symlink():
            print("No DevHub workspace setup found.")
            return 0
        directory(root)
        lock_path = root / ".devhub-setup.lock"
        if lock_path.is_symlink():
            raise ValueError(f"Refusing a symlinked lock: {lock_path}")
        git_dir = Path(git(source, "rev-parse", "--absolute-git-dir"))
        with (git_dir / "devhub-setup.lock").open("a") as source_lock, lock_path.open("a") as lock:
            try:
                fcntl.flock(source_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise ValueError("Another DevHub setup is running; retry after it finishes.") from None
            read_state(root / STATE, source)
            if args.uninstall:
                synchronize(source, workspace, True)
            else:
                if git(source, "status", "--porcelain"):
                    raise ValueError("DevHub clone has local changes. Commit or move them before updating.")
                if not args.no_pull:
                    git(source, "symbolic-ref", "--quiet", "HEAD")
                    git(source, "rev-parse", "--abbrev-ref", "@{upstream}")
                    if git(source, "rev-list", "--count", "@{upstream}..HEAD") != "0":
                        raise ValueError("DevHub clone has unpublished commits. Use a clean update clone.")
                    git(source, "pull", "--ff-only", "--no-rebase")
                # Apply this revision's code, including a setup.py updated by pull.
                updated = runpy.run_path(str(source / "tools/setup.py"))
                updated["synchronize"](source, workspace, False)
        return 0
    except subprocess.CalledProcessError as error:
        print(
            f"DevHub Git operation failed ({' '.join(error.cmd)}): "
            f"{error.stderr.strip() or 'Check the branch and its configured upstream.'}",
            file=sys.stderr,
        )
    except subprocess.TimeoutExpired as error:
        print(f"DevHub Git operation exceeded {error.timeout} seconds.", file=sys.stderr)
    except (OSError, ValueError) as error:
        print(f"DevHub setup failed: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

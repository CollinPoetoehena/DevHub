#!/usr/bin/env python3
"""Remove recorded links from the retired clone-based Copilot setup.

Requires Linux/WSL, Python 3.10+, Git, and the original clone location.
Only --uninstall is supported; missing historical source files are allowed.
Use the common APM package for new installations and updates.
"""

import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import sys


ENTRY = re.compile(
    r"copilot-instructions\.md|instructions/[a-z0-9.-]+\.instructions\.md"
    r"|skills/devhub-[a-z0-9.-]+|agents/devhub-[a-z0-9.-]+\.agent\.md"
)
STATE = ".devhub-setup.json"
# Historical targets used only to recognize unchanged links during uninstall.
CUSTOMIZATIONS = Path("docs/copilot")
RETIRED = (
    "Legacy Copilot install/update is retired. Use the common APM package: "
    "see packages/apm/common/README.md in the DevHub clone. "
    "To remove historical links, rerun with --workspace PATH --uninstall "
    "from the original clone location."
)


def git(source: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(source), *arguments],
        env=dict(os.environ, GIT_TERMINAL_PROMPT="0"),
        text=True, capture_output=True, check=True, timeout=30,
    )
    return result.stdout.strip()


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


def owned_link(path: Path, target: Path) -> bool:
    return path.is_symlink() and os.readlink(path) == str(target)


def synchronize(source: Path, workspace: Path, uninstall: bool) -> None:
    if not uninstall:
        raise ValueError(RETIRED)
    root = workspace / ".github"
    state = root / STATE
    previous = read_state(state, source)
    for kind in sorted({e.split("/")[0] for e in previous if "/" in e}):
        directory(root / kind)
    for entry in sorted(previous):
        path = root / entry
        if owned_link(path, source / CUSTOMIZATIONS / entry):
            path.unlink()
        elif path.exists() or path.is_symlink():
            print(f"Preserving personal replacement: {path}", file=sys.stderr)
    state.unlink(missing_ok=True)
    print("DevHub workspace links removed. Remove the legacy shell hook; use APM for updates.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True,
                        help="Existing personal-only workspace parent directory")
    parser.add_argument("--no-pull", action="store_true",
                        help="Legacy option; install/update is no longer supported")
    parser.add_argument("--uninstall", action="store_true",
                        help="Remove recorded workspace links offline; keep the clone")
    args = parser.parse_args()
    if not sys.platform.startswith("linux"):
        parser.error("This script supports Linux and WSL only.")
    source = Path(__file__).resolve().parents[1]
    workspace = args.workspace.expanduser().resolve()
    try:
        if not args.uninstall:
            raise ValueError(RETIRED)
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
            synchronize(source, workspace, True)
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

"""Run external commands as argument lists, never through a shell."""

import logging
import os
import re
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from repo_fleet.errors import CommandError

LOGGER = logging.getLogger(__name__)
NON_INTERACTIVE_ENV = {"GIT_TERMINAL_PROMPT": "0", "GH_PROMPT_DISABLED": "1"}
TOKEN_PATTERN = re.compile(
    r"\b(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"
)
REDACTED = "[REDACTED]"


@dataclass(frozen=True)
class CommandResult:
    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


class CommandRunner(Protocol):
    def run(self, args: Sequence[str], *, cwd: Path | None = None) -> CommandResult:
        """Run a command; raise CommandError when it fails."""
        ...


def redact(text: str) -> str:
    return TOKEN_PATTERN.sub(REDACTED, text)


def describe(args: Sequence[str]) -> str:
    """Short command description for logs; omits arguments such as PR bodies."""
    return " ".join(args[:2])


class SubprocessRunner:
    def run(self, args: Sequence[str], *, cwd: Path | None = None) -> CommandResult:
        command = tuple(args)
        LOGGER.debug("running %s", describe(command))
        try:
            completed = subprocess.run(
                list(command),
                cwd=cwd,
                check=False,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
                env={**os.environ, **NON_INTERACTIVE_ENV},
            )
        except OSError as err:
            raise CommandError(f"cannot run {describe(command)}: {err}") from err
        result = CommandResult(
            command, completed.returncode, completed.stdout, completed.stderr
        )
        if result.returncode != 0:
            raise CommandError(
                f"{describe(command)} failed with exit code {result.returncode}: "
                f"{redact(result.stderr.strip())}"
            )
        return result

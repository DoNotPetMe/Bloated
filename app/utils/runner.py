"""Subprocess wrapper for CMD and PowerShell with structured results."""
from __future__ import annotations

import subprocess
import threading
from dataclasses import dataclass
from typing import Callable, Optional, Sequence

from .logger import get_logger

log = get_logger("runner")

# Hide consoles when spawning processes on Windows.
_CREATE_NO_WINDOW = 0x08000000


@dataclass
class CommandResult:
    command: str
    shell: str  # "cmd" or "powershell"
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    @property
    def text(self) -> str:
        if self.stdout and self.stderr:
            return f"{self.stdout}\n[stderr]\n{self.stderr}"
        return self.stdout or self.stderr or "(no output)"


def _run(args: Sequence[str], display_cmd: str, shell: str, timeout: Optional[int]) -> CommandResult:
    log.info("Running [%s] %s", shell, display_cmd)
    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=_CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
        result = CommandResult(
            command=display_cmd,
            shell=shell,
            returncode=proc.returncode,
            stdout=(proc.stdout or "").strip(),
            stderr=(proc.stderr or "").strip(),
        )
    except subprocess.TimeoutExpired:
        result = CommandResult(display_cmd, shell, -1, "", f"Timed out after {timeout}s")
    except FileNotFoundError as e:
        result = CommandResult(display_cmd, shell, -1, "", f"Shell not found: {e}")
    except Exception as e:  # noqa: BLE001
        result = CommandResult(display_cmd, shell, -1, "", f"{type(e).__name__}: {e}")

    log.info("Result rc=%s len(out)=%s len(err)=%s",
             result.returncode, len(result.stdout), len(result.stderr))
    return result


def run_cmd(command: str, timeout: Optional[int] = 120) -> CommandResult:
    """Run a CMD one-liner."""
    return _run(["cmd.exe", "/c", command], command, "cmd", timeout)


def run_powershell(command: str, timeout: Optional[int] = 180) -> CommandResult:
    """Run a PowerShell one-liner (bypasses execution policy for this call only)."""
    return _run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy", "Bypass",
            "-Command", command,
        ],
        command,
        "powershell",
        timeout,
    )


def run_async(
    func: Callable[[], CommandResult],
    on_done: Callable[[CommandResult], None],
) -> threading.Thread:
    """Run a command function on a background thread, call on_done with the result."""
    def _worker():
        result = func()
        try:
            on_done(result)
        except Exception:  # noqa: BLE001
            log.exception("on_done callback failed")
    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    return t

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
    duration_sec: float = 0.0

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
    import time
    started = time.monotonic()
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
            duration_sec=time.monotonic() - started,
        )
    except subprocess.TimeoutExpired:
        result = CommandResult(
            display_cmd, shell, -1, "",
            f"Timed out after {timeout}s",
            duration_sec=time.monotonic() - started,
        )
    except FileNotFoundError as e:
        result = CommandResult(display_cmd, shell, -1, "", f"Shell not found: {e}",
                               duration_sec=time.monotonic() - started)
    except Exception as e:  # noqa: BLE001
        result = CommandResult(display_cmd, shell, -1, "", f"{type(e).__name__}: {e}",
                               duration_sec=time.monotonic() - started)

    log.info("Result rc=%s len(out)=%s len(err)=%s elapsed=%.1fs",
             result.returncode, len(result.stdout),
             len(result.stderr), result.duration_sec)
    return result


# Generous default timeouts. SFC, DISM, big winget installs, chkdsk all
# routinely run for several minutes; the old 120 s cut them off silently.
def run_cmd(command: str, timeout: Optional[int] = 600) -> CommandResult:
    """Run a CMD one-liner. 10-minute default timeout."""
    return _run(["cmd.exe", "/c", command], command, "cmd", timeout)


def run_powershell(command: str, timeout: Optional[int] = 600) -> CommandResult:
    """Run a PowerShell one-liner (bypasses execution policy for this call only).
    10-minute default timeout."""
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


# ---------------------------------------------------------------------------
# Streaming runner
# ---------------------------------------------------------------------------


def _stream(
    args: Sequence[str],
    display_cmd: str,
    shell: str,
    on_line: Callable[[str, str], None],
    on_tick: Optional[Callable[[float], None]] = None,
    timeout: Optional[int] = 1800,
    tick_interval: float = 5.0,
) -> CommandResult:
    """Spawn a process and feed each output line through `on_line(stream, line)`
    as it's produced.

    `on_line` is called from background threads with stream="out" or "err".
    `on_tick` (optional) is called every `tick_interval` seconds with the
    elapsed time, so callers can paint a heartbeat for output-less commands.
    Returns the full CommandResult at the end (stdout/stderr also collected
    into the result for the file log)."""
    import time

    log.info("Running [%s, streaming] %s", shell, display_cmd)
    started = time.monotonic()
    try:
        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # line-buffered
            creationflags=_CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
    except FileNotFoundError as e:
        return CommandResult(display_cmd, shell, -1, "",
                             f"Shell not found: {e}",
                             duration_sec=time.monotonic() - started)
    except Exception as e:  # noqa: BLE001
        return CommandResult(display_cmd, shell, -1, "",
                             f"{type(e).__name__}: {e}",
                             duration_sec=time.monotonic() - started)

    out_lines: list[str] = []
    err_lines: list[str] = []

    def _reader(stream, sink: list[str], tag: str) -> None:
        try:
            for raw in iter(stream.readline, ""):
                # Many CLIs use \r for in-place progress updates. Split on
                # either so we surface progress as soon as it's flushed.
                for chunk in raw.replace("\r", "\n").splitlines():
                    line = chunk.rstrip()
                    if not line:
                        continue
                    sink.append(line)
                    try:
                        on_line(tag, line)
                    except Exception:
                        pass
        finally:
            try:
                stream.close()
            except Exception:
                pass

    t_out = threading.Thread(target=_reader, args=(proc.stdout, out_lines, "out"), daemon=True)
    t_err = threading.Thread(target=_reader, args=(proc.stderr, err_lines, "err"), daemon=True)
    t_out.start(); t_err.start()

    tick_stop = threading.Event()
    if on_tick is not None:
        def _ticker():
            while not tick_stop.wait(tick_interval):
                if proc.poll() is not None:
                    return
                try:
                    on_tick(time.monotonic() - started)
                except Exception:
                    pass
        threading.Thread(target=_ticker, daemon=True).start()

    timed_out = False
    try:
        rc = proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        proc.kill()
        try:
            rc = proc.wait(timeout=5)
        except Exception:
            rc = -1

    tick_stop.set()
    t_out.join(timeout=2)
    t_err.join(timeout=2)

    result = CommandResult(
        command=display_cmd,
        shell=shell,
        returncode=-1 if timed_out else rc,
        stdout="\n".join(out_lines),
        stderr=("\n".join(err_lines) + (f"\nTimed out after {timeout}s"
                                         if timed_out else "")).strip(),
        duration_sec=time.monotonic() - started,
    )
    log.info("Result rc=%s len(out)=%s len(err)=%s elapsed=%.1fs (streamed)",
             result.returncode, len(result.stdout),
             len(result.stderr), result.duration_sec)
    return result


def run_cmd_stream(command: str,
                   on_line: Callable[[str, str], None],
                   on_tick: Optional[Callable[[float], None]] = None,
                   timeout: Optional[int] = 1800) -> CommandResult:
    return _stream(["cmd.exe", "/c", command], command, "cmd",
                   on_line, on_tick, timeout)


def run_powershell_stream(command: str,
                          on_line: Callable[[str, str], None],
                          on_tick: Optional[Callable[[float], None]] = None,
                          timeout: Optional[int] = 1800) -> CommandResult:
    return _stream(
        ["powershell.exe", "-NoProfile", "-NonInteractive",
         "-ExecutionPolicy", "Bypass", "-Command", command],
        command, "powershell", on_line, on_tick, timeout,
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

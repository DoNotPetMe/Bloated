"""Detect and request administrator privileges (Windows)."""
from __future__ import annotations

import ctypes
import os
import sys


def is_admin() -> bool:
    """True when the process is running with elevated rights."""
    if os.name != "nt":
        # Non-Windows: treat as not-admin so users see the banner during dev.
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin() -> None:
    """Re-launch the current Python process with a UAC prompt."""
    if os.name != "nt":
        return
    params = " ".join(f'"{a}"' for a in sys.argv)
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, None, 1
    )
    sys.exit(0)


def is_windows() -> bool:
    return os.name == "nt"

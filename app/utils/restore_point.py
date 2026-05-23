"""Create Windows System Restore Points via PowerShell."""
from __future__ import annotations

from .runner import run_powershell, CommandResult


def create_restore_point(description: str = "Bloated — pre-change snapshot") -> CommandResult:
    """Create a system restore point. Requires admin + System Protection enabled on C:."""
    script = (
        "Enable-ComputerRestore -Drive 'C:\\' -ErrorAction SilentlyContinue;"
        f"Checkpoint-Computer -Description '{description}' "
        "-RestorePointType 'MODIFY_SETTINGS'"
    )
    return run_powershell(script, timeout=120)

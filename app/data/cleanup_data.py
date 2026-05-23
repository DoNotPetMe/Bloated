"""Disk cleanup actions — temp folders, caches, logs."""
from __future__ import annotations

from ..tabs._models import Action


# Each command is wrapped in a do-not-fail block so that a missing folder
# doesn’t abort the whole sweep.
def _rm(path: str) -> str:
    return (f'powershell -NoProfile -Command "if (Test-Path \'{path}\') '
            f'{{ Remove-Item -Path \'{path}\\*\' -Recurse -Force '
            f'-ErrorAction SilentlyContinue }} ; Write-Host \'Cleared {path}\'"')


ACTIONS: list[Action] = [
    Action(
        title="Empty user TEMP (%TEMP%)",
        description="Wipes the per-user temp folder used by installers and apps.",
        command=_rm("$env:TEMP"),
        shell="cmd",
        category="Temp files",
        enabled_by_default=True,
    ),
    Action(
        title="Empty system TEMP (C:\\Windows\\Temp)",
        description="Wipes the system-wide temp folder.",
        command=_rm("C:\\Windows\\Temp"),
        shell="cmd",
        category="Temp files",
        enabled_by_default=True,
    ),
    Action(
        title="Empty Prefetch",
        description="Clears C:\\Windows\\Prefetch — will be rebuilt automatically.",
        command=_rm("C:\\Windows\\Prefetch"),
        shell="cmd",
        category="Caches",
        enabled_by_default=False,
    ),
    Action(
        title="Clear Windows Update download cache",
        description=("Stops the wuauserv service, wipes "
                     "C:\\Windows\\SoftwareDistribution\\Download, restarts it. "
                     "Forces Update to redownload."),
        command=(
            "net stop wuauserv & "
            'powershell -NoProfile -Command "Remove-Item -Path '
            "'C:\\Windows\\SoftwareDistribution\\Download\\*' "
            '-Recurse -Force -ErrorAction SilentlyContinue" & '
            "net start wuauserv"
        ),
        shell="cmd",
        category="Caches",
        enabled_by_default=True,
    ),
    Action(
        title="Empty Recycle Bin",
        description="Permanently removes everything in the Recycle Bin on every drive.",
        command="powershell -NoProfile -Command \"Clear-RecycleBin -Force -ErrorAction SilentlyContinue\"",
        shell="cmd",
        category="Disk",
        enabled_by_default=True,
        danger=True,
    ),
    Action(
        title="Run Disk Cleanup (cleanmgr /sagerun)",
        description="Runs the built-in Disk Cleanup with the preset profile.",
        command="cleanmgr /sagerun:1",
        shell="cmd",
        category="Disk",
        enabled_by_default=False,
    ),
    Action(
        title="Flush DNS cache",
        description="Clears resolved hostnames — fixes some browsing issues.",
        command="ipconfig /flushdns",
        shell="cmd",
        category="Network",
        enabled_by_default=True,
    ),
    Action(
        title="Clear thumbnail cache",
        description="Forces Explorer to rebuild folder thumbnails.",
        command=(
            "taskkill /f /im explorer.exe & "
            'del /f /s /q "%LOCALAPPDATA%\\Microsoft\\Windows\\Explorer\\thumbcache_*.db" & '
            "start explorer.exe"
        ),
        shell="cmd",
        category="Caches",
        enabled_by_default=False,
    ),
    Action(
        title="Clear icon cache",
        description="Rebuilds Explorer’s icon cache. Fixes ‘wrong icon’ glitches.",
        command=(
            "taskkill /f /im explorer.exe & "
            'del /f /s /q "%LOCALAPPDATA%\\IconCache.db" & '
            "start explorer.exe"
        ),
        shell="cmd",
        category="Caches",
        enabled_by_default=False,
    ),
    Action(
        title="Clear Microsoft Store cache",
        description="wsreset.exe clears Store download cache without removing installs.",
        command="wsreset.exe -i",
        shell="cmd",
        category="Caches",
        enabled_by_default=False,
    ),
    Action(
        title="Clear Windows event logs",
        description="Truncates every Windows event log. Useful before sharing a PC.",
        command=(
            "powershell -NoProfile -Command \"Get-WinEvent -ListLog * "
            "| Where-Object { $_.IsEnabled -and $_.RecordCount -gt 0 } "
            "| ForEach-Object { try { wevtutil cl $_.LogName } catch { } }\""
        ),
        shell="cmd",
        category="Logs",
        enabled_by_default=False,
        danger=True,
    ),
    Action(
        title="Remove Windows.old folder",
        description=("Frees a LOT of space after a Windows upgrade. "
                     "After this, rollback to the previous build is no longer possible."),
        command=(
            'takeown /f C:\\Windows.old /r /d Y >nul & '
            'icacls C:\\Windows.old /grant administrators:F /T >nul & '
            'rd /s /q C:\\Windows.old'
        ),
        shell="cmd",
        category="Disk",
        enabled_by_default=False,
        danger=True,
    ),
]

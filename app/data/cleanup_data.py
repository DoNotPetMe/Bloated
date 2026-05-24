"""Disk cleanup actions — temp folders, caches, logs, package leftovers.

Most of these free anywhere from a few MB to many GB depending on how long
the PC has been in use. Each action prints what it cleaned to the output
console so you can see the impact.
"""
from __future__ import annotations

from ..tabs._models import Action


def _rm(path: str) -> str:
    """Wrap a Remove-Item in a guard so a missing folder is a no-op, not
    a failure that aborts the whole batch."""
    return (f'powershell -NoProfile -Command "if (Test-Path \'{path}\') '
            f'{{ Remove-Item -Path \'{path}\\*\' -Recurse -Force '
            f'-ErrorAction SilentlyContinue }} ; Write-Host \'Cleared {path}\'"')


ACTIONS: list[Action] = [
    # ── Temp files ──────────────────────────────────────────────────────────
    Action(
        title="Empty your user TEMP folder (%TEMP%)",
        description=(
            "Wipes the per-user temp folder. This is where installers, "
            "browsers and apps drop scratch files — and they almost never "
            "clean up after themselves. Usually reclaims hundreds of MB to "
            "several GB."),
        command=_rm("$env:TEMP"),
        shell="cmd",
        category="Temp files",
        enabled_by_default=True,
    ),
    Action(
        title="Empty system-wide TEMP (C:\\Windows\\Temp)",
        description=(
            "Same idea as above, but for the system-wide TEMP that "
            "background services and updaters use. Requires admin."),
        command=_rm("C:\\Windows\\Temp"),
        shell="cmd",
        category="Temp files",
        enabled_by_default=True,
    ),
    Action(
        title="Empty Crash dumps (%LOCALAPPDATA%\\CrashDumps)",
        description=(
            "Removes WER per-app crash dumps. These are sometimes several "
            "GB if you’ve had a misbehaving app."),
        command=_rm("$env:LOCALAPPDATA\\CrashDumps"),
        shell="cmd",
        category="Temp files",
        enabled_by_default=True,
    ),

    # ── Caches ──────────────────────────────────────────────────────────────
    Action(
        title="Empty Prefetch",
        description=(
            "C:\\Windows\\Prefetch tracks app launch patterns to make "
            "frequently used apps start faster. Windows rebuilds it "
            "automatically, so emptying it is harmless — you’ll just have "
            "slightly slower first launches for a few days."),
        command=_rm("C:\\Windows\\Prefetch"),
        shell="cmd",
        category="Caches",
        enabled_by_default=False,
    ),
    Action(
        title="Clear Windows Update download cache",
        description=(
            "Stops the Windows Update service, wipes "
            "C:\\Windows\\SoftwareDistribution\\Download (often 5–20 GB on "
            "an old install), then restarts the service. Updates will "
            "re-download as needed. Frequently fixes stuck/failing updates."),
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
        title="Compact / shrink the WinSxS component store",
        description=(
            "DISM /StartComponentCleanup removes superseded versions of "
            "Windows components left behind by past updates. On a 2-3 year "
            "old install this typically reclaims 3–8 GB. Takes a few minutes."),
        command="DISM /Online /Cleanup-Image /StartComponentCleanup /ResetBase",
        shell="cmd",
        category="Caches",
        enabled_by_default=False,
    ),
    Action(
        title="Clear thumbnail cache",
        description=(
            "Forces Explorer to rebuild the per-folder image thumbnails. "
            "Fixes ‘wrong thumbnail’ glitches after moving or replacing "
            "image files."),
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
        description=(
            "Rebuilds Explorer’s app/shortcut icon cache. The classic fix "
            "for ‘all my icons turned blank / generic-EXE’ glitches."),
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
        title="Reset Microsoft Store cache (wsreset)",
        description=(
            "Clears the Store’s download cache without removing any of "
            "your installed apps. Fixes Store ‘something happened on our "
            "end’ errors."),
        command="wsreset.exe -i",
        shell="cmd",
        category="Caches",
        enabled_by_default=False,
    ),
    Action(
        title="Clear Microsoft Edge cache + cookies",
        description=(
            "Wipes Edge’s default-profile cache, cookies, history. Useful "
            "if Edge is misbehaving or you want a fresh state. Close Edge "
            "first."),
        command=(
            'powershell -NoProfile -Command "Get-ChildItem '
            "'$env:LOCALAPPDATA\\Microsoft\\Edge\\User Data\\Default' "
            "-Include 'Cache','Code Cache','GPUCache','Service Worker','Cookies*' "
            "-Recurse -Force -ErrorAction SilentlyContinue "
            '| Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"'
        ),
        shell="cmd",
        category="Caches",
        enabled_by_default=False,
    ),
    Action(
        title="Clear DNS cache (ipconfig /flushdns)",
        description=(
            "Wipes the local DNS resolver’s memory of hostname → IP "
            "lookups. Fixes ‘this site loads on my phone but not my PC’ "
            "problems after a DNS change."),
        command="ipconfig /flushdns",
        shell="cmd",
        category="Network",
        enabled_by_default=True,
    ),
    Action(
        title="Reset ARP cache (network neighbour table)",
        description=(
            "Flushes the local table of IP↔MAC mappings. Useful after "
            "changing routers or when LAN devices appear unreachable."),
        command="arp -d *",
        shell="cmd",
        category="Network",
        enabled_by_default=False,
    ),

    # ── Disk ────────────────────────────────────────────────────────────────
    Action(
        title="Empty the Recycle Bin",
        description=(
            "Permanently removes everything currently in the Recycle Bin "
            "on every drive. Items deleted before today included."),
        command="powershell -NoProfile -Command \"Clear-RecycleBin -Force -ErrorAction SilentlyContinue\"",
        shell="cmd",
        category="Disk",
        enabled_by_default=True,
        danger=True,
    ),
    Action(
        title="Run built-in Disk Cleanup (cleanmgr /sagerun:1)",
        description=(
            "Launches Windows’ own cleanmgr.exe with its ‘sage:1’ profile, "
            "which sweeps the standard candidates (temp internet files, "
            "delivery optimisation, error reports, etc.) without prompting."),
        command="cleanmgr /sagerun:1",
        shell="cmd",
        category="Disk",
        enabled_by_default=False,
    ),
    Action(
        title="Trim / optimise all SSDs",
        description=(
            "Tells every drive Windows recognises as an SSD to perform a "
            "TRIM pass — basically ‘here are the blocks you can forget’. "
            "Improves long-term write performance, especially on older SATA "
            "SSDs that haven’t been TRIMmed in months."),
        command=(
            "powershell -NoProfile -Command \"Get-Volume "
            "| Where-Object DriveType -eq 'Fixed' "
            "| ForEach-Object { Optimize-Volume -DriveLetter $_.DriveLetter -ReTrim -Verbose }\""
        ),
        shell="cmd",
        category="Disk",
        enabled_by_default=False,
    ),
    Action(
        title="Remove the Windows.old folder",
        description=(
            "After a major Windows upgrade, your previous build is kept in "
            "C:\\Windows.old in case you want to roll back. It’s often "
            "10–25 GB. This action deletes it permanently — you can no "
            "longer ‘Go back to previous version’ after running this."),
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

    # ── Logs ────────────────────────────────────────────────────────────────
    Action(
        title="Clear all Windows event logs",
        description=(
            "Truncates every Windows event log (Application, System, "
            "Security, and all the chatter logs under "
            "Microsoft-Windows-*). Useful before handing the PC over or "
            "after fixing a problem to start with a clean slate."),
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
        title="Empty the WER report archive",
        description=(
            "Deletes archived Windows Error Reporting reports under "
            "ProgramData\\Microsoft\\Windows\\WER. Usually a few hundred MB."),
        command=_rm("$env:PROGRAMDATA\\Microsoft\\Windows\\WER\\ReportArchive"),
        shell="cmd",
        category="Logs",
        enabled_by_default=False,
    ),

    # ── Misc ────────────────────────────────────────────────────────────────
    Action(
        title="Reset every Store app (re-register)",
        description=(
            "Re-registers all built-in Store/UWP apps. Heavy-handed but "
            "fixes the classic ‘the Start menu won’t open / the Calculator "
            "won’t launch’ symptoms after a botched update. Takes a minute "
            "or two; Start menu may flicker."),
        command=(
            "powershell -NoProfile -Command \"Get-AppXPackage -AllUsers "
            "| ForEach-Object { Add-AppxPackage -DisableDevelopmentMode "
            "-Register \\\"$($_.InstallLocation)\\AppXManifest.xml\\\" "
            "-ErrorAction SilentlyContinue }\""
        ),
        shell="cmd",
        category="Repair",
        enabled_by_default=False,
        danger=True,
    ),
]

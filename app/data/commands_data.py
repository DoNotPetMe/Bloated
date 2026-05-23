"""Built-in catalogue of useful CMD / PowerShell commands with explanations.

Users can also add/save their own from the Commands tab; those are persisted
under %LOCALAPPDATA%\\Bloated\\custom_commands.json.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SavedCommand:
    name: str
    description: str
    command: str
    shell: str = "cmd"     # "cmd" or "powershell"
    tags: tuple[str, ...] = ()


BUILTIN: list[SavedCommand] = [
    # ── Repair ──────────────────────────────────────────────────────────────
    SavedCommand(
        "SFC — System File Checker",
        "Scans Windows protected files and repairs missing/corrupt ones from the local cache.",
        "sfc /scannow", "cmd", ("repair", "integrity"),
    ),
    SavedCommand(
        "DISM — restore health",
        "Repairs the Windows component store using Windows Update as the source.",
        "DISM /Online /Cleanup-Image /RestoreHealth", "cmd", ("repair", "wim"),
    ),
    SavedCommand(
        "CHKDSK — check C: (next reboot)",
        "Schedules a full /f /r filesystem check on C: at the next boot.",
        "chkdsk C: /f /r", "cmd", ("repair", "disk"),
    ),

    # ── Diagnostics ─────────────────────────────────────────────────────────
    SavedCommand(
        "Battery health report",
        "Generates a detailed battery wear & cycle report in your user folder.",
        "powercfg /batteryreport /output \"%USERPROFILE%\\battery-report.html\"", "cmd",
        ("laptop", "diagnostics"),
    ),
    SavedCommand(
        "Power efficiency report",
        "Runs a 60-second trace and writes a power efficiency HTML report.",
        "powercfg /energy /output \"%USERPROFILE%\\energy-report.html\"", "cmd",
        ("laptop", "diagnostics"),
    ),
    SavedCommand(
        "Full system info",
        "Dumps OS build, hotfixes, BIOS, RAM, NICs.",
        "systeminfo", "cmd", ("diagnostics", "info"),
    ),
    SavedCommand(
        "List installed hotfixes",
        "Shows every Windows Update KB applied to this machine.",
        "wmic qfe list brief /format:table", "cmd", ("diagnostics", "updates"),
    ),

    # ── Networking ──────────────────────────────────────────────────────────
    SavedCommand(
        "Show open TCP ports + owning PIDs",
        "Lists listening sockets with the process that opened them.",
        "netstat -ano -p tcp", "cmd", ("network",),
    ),
    SavedCommand(
        "Show Wi-Fi profile passwords",
        "Dumps saved Wi-Fi profiles WITH their plaintext keys. Admin required.",
        ("for /f \"skip=9 tokens=2 delims=:\" %a in ('netsh wlan show profiles') "
         "do @(netsh wlan show profile name=%a key=clear | findstr /C:\"Key Content\")"),
        "cmd", ("network", "wifi", "secrets"),
    ),
    SavedCommand(
        "Trace route to 1.1.1.1",
        "Standard tracert to Cloudflare.",
        "tracert 1.1.1.1", "cmd", ("network",),
    ),

    # ── Drivers / hardware ─────────────────────────────────────────────────
    SavedCommand(
        "List installed third-party drivers",
        "Shows non-Microsoft drivers — useful before a clean re-install.",
        "driverquery /v /fo list", "cmd", ("drivers", "info"),
    ),
    SavedCommand(
        "List physical disks (PowerShell)",
        "Modern Get-PhysicalDisk view with health + media type.",
        "Get-PhysicalDisk | Format-Table FriendlyName, MediaType, HealthStatus, Size -AutoSize",
        "powershell", ("disk", "info"),
    ),
    SavedCommand(
        "Trim all SSDs",
        "Forces a TRIM/retrim pass on every drive recognised as SSD.",
        "Optimize-Volume -DriveLetter (Get-Volume | Where-Object DriveType -eq 'Fixed').DriveLetter -ReTrim -Verbose",
        "powershell", ("disk", "ssd", "maintenance"),
    ),

    # ── Maintenance ─────────────────────────────────────────────────────────
    SavedCommand(
        "Rebuild Boot Configuration Data (BCD)",
        "Last-resort: rebuilds BCD. Run from recovery for boot issues.",
        "bcdedit /export C:\\bcd-backup & bootrec /rebuildbcd", "cmd",
        ("boot", "repair"),
    ),
    SavedCommand(
        "Group Policy refresh",
        "Applies pending Group Policy changes immediately.",
        "gpupdate /force", "cmd", ("policy",),
    ),
    SavedCommand(
        "Restart Windows Explorer",
        "Kills explorer.exe and relaunches it. Reapplies many shell tweaks.",
        "taskkill /f /im explorer.exe & start explorer.exe", "cmd",
        ("shell",),
    ),

    # ── Info ────────────────────────────────────────────────────────────────
    SavedCommand(
        "Show Windows product key (OEM)",
        "Reads the OA3 OEM key embedded in firmware (if present).",
        "wmic path softwarelicensingservice get OA3xOriginalProductKey",
        "cmd", ("license", "info"),
    ),
    SavedCommand(
        "Windows activation status",
        "Reports activation/licensing state.",
        "cscript //nologo C:\\Windows\\System32\\slmgr.vbs /xpr",
        "cmd", ("license", "info"),
    ),
]

"""Built-in catalogue of useful CMD / PowerShell commands with full,
plain-English explanations of what they do and when you’d want them.

Users can also add their own from the Commands tab; those are persisted
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
    # ── Repair / integrity ─────────────────────────────────────────────────
    SavedCommand(
        "SFC — System File Checker",
        "Scans every Windows system file and repairs missing or corrupt "
        "ones from the protected local cache. First-line fix for ‘weird "
        "Windows behaviour’ after a botched update or malware cleanup. "
        "Takes a few minutes. Safe — only repairs.",
        "sfc /scannow", "cmd", ("repair", "integrity"),
    ),
    SavedCommand(
        "DISM — restore Windows image health",
        "Repairs the Windows component store itself (which SFC pulls from). "
        "If SFC says ‘could not fix some files’, run this then SFC again. "
        "Downloads bits from Windows Update as needed.",
        "DISM /Online /Cleanup-Image /RestoreHealth", "cmd", ("repair", "wim"),
    ),
    SavedCommand(
        "DISM — check health only",
        "Quick non-destructive check — reports whether the component store "
        "is healthy without actually downloading anything.",
        "DISM /Online /Cleanup-Image /CheckHealth", "cmd", ("repair", "wim"),
    ),
    SavedCommand(
        "CHKDSK — full filesystem check of C: at next reboot",
        "Schedules a full /f (fix errors) /r (locate bad sectors and "
        "recover readable data) pass against the C: drive on the next "
        "boot. Can take hours on a large spinning disk; fast on an SSD.",
        "chkdsk C: /f /r", "cmd", ("repair", "disk"),
    ),
    SavedCommand(
        "Rebuild Boot Configuration Data (BCD)",
        "Last-resort boot repair: exports a backup of the current BCD to "
        "C:\\bcd-backup, then rebuilds it. Usually run from the Windows "
        "Recovery Environment when the PC refuses to boot.",
        "bcdedit /export C:\\bcd-backup & bootrec /rebuildbcd", "cmd",
        ("boot", "repair"),
    ),
    SavedCommand(
        "Group Policy refresh",
        "Forces every Group Policy change to apply immediately instead "
        "of waiting for the next 90-minute cycle.",
        "gpupdate /force", "cmd", ("policy",),
    ),
    SavedCommand(
        "Restart Windows Explorer",
        "Kills explorer.exe and re-launches it. Re-applies a lot of the "
        "registry tweaks under the Tweaks tab without needing a sign-out, "
        "and unsticks a frozen taskbar.",
        "taskkill /f /im explorer.exe & start explorer.exe", "cmd",
        ("shell",),
    ),

    # ── Diagnostics ────────────────────────────────────────────────────────
    SavedCommand(
        "Battery health report (HTML)",
        "Generates a detailed battery wear-and-cycle report at "
        "%USERPROFILE%\\battery-report.html. Shows design capacity vs "
        "current full-charge capacity — i.e. how much battery life you "
        "have already lost.",
        "powercfg /batteryreport /output \"%USERPROFILE%\\battery-report.html\"", "cmd",
        ("laptop", "diagnostics"),
    ),
    SavedCommand(
        "Power efficiency report (HTML)",
        "Runs a 60-second trace of CPU usage, drivers, USB devices, etc. "
        "Then writes an HTML report listing anything that’s preventing "
        "the PC from going into sleep states efficiently.",
        "powercfg /energy /output \"%USERPROFILE%\\energy-report.html\"", "cmd",
        ("laptop", "diagnostics"),
    ),
    SavedCommand(
        "Sleep study (laptops on modern standby)",
        "Detailed report on what’s keeping the laptop awake when it’s "
        "supposed to be sleeping. Useful for diagnosing ‘my laptop is hot "
        "in the bag’ problems.",
        "powercfg /sleepstudy /output \"%USERPROFILE%\\sleep-study.html\"", "cmd",
        ("laptop", "diagnostics"),
    ),
    SavedCommand(
        "Full system summary",
        "Dumps OS build, hotfixes, BIOS version, RAM, network adapters — "
        "everything you’d need to attach to a support ticket.",
        "systeminfo", "cmd", ("diagnostics", "info"),
    ),
    SavedCommand(
        "List installed Windows updates (KB numbers)",
        "Shows every Windows hotfix / cumulative update applied. Useful "
        "for ‘am I patched against CVE-XYZ?’ checks. Uses Get-HotFix because "
        "wmic was removed in Windows 11 24H2+.",
        "Get-HotFix | Sort-Object InstalledOn -Descending "
        "| Format-Table HotFixID, Description, InstalledOn -AutoSize",
        "powershell", ("diagnostics", "updates"),
    ),
    SavedCommand(
        "Generate Reliability Monitor report",
        "Opens Reliability Monitor — Windows’ underrated tool that scores "
        "each day from 1–10 based on app crashes / update failures / "
        "hardware errors.",
        "perfmon /rel", "cmd", ("diagnostics",),
    ),

    # ── Networking ──────────────────────────────────────────────────────────
    SavedCommand(
        "Show open TCP ports + owning process",
        "Every listening / established TCP socket on the machine, with "
        "the PID of the process that owns it. Pair with `tasklist /fi "
        "\"PID eq <pid>\"` to identify the program.",
        "netstat -ano -p tcp", "cmd", ("network",),
    ),
    SavedCommand(
        "Show all saved Wi-Fi passwords (plain text)",
        "Dumps every saved Wi-Fi network with its password in clear text. "
        "Requires admin. Handy when you’ve forgotten the Wi-Fi key for a "
        "network you’re already connected to.",
        ("for /f \"skip=9 tokens=2 delims=:\" %a in ('netsh wlan show profiles') "
         "do @(netsh wlan show profile name=%a key=clear | findstr /C:\"Key Content\")"),
        "cmd", ("network", "wifi", "secrets"),
    ),
    SavedCommand(
        "Trace route to Cloudflare (1.1.1.1)",
        "Standard tracert. Helps identify which hop along your route to "
        "the internet is responsible for high ping / packet loss.",
        "tracert 1.1.1.1", "cmd", ("network",),
    ),
    SavedCommand(
        "Continuous ping with timestamp",
        "Pings 1.1.1.1 forever with timestamps — leave it running in a "
        "second window when you suspect intermittent disconnects, then "
        "check when the failures happened.",
        "ping -t 1.1.1.1", "cmd", ("network",),
    ),
    SavedCommand(
        "Show wireless adapter capabilities",
        "Lists every Wi-Fi standard your card supports, current PHY type, "
        "channel, signal strength, etc. Useful when wondering why your "
        "‘Wi-Fi 6’ adapter is only doing 200 Mbps.",
        "netsh wlan show drivers && netsh wlan show interfaces", "cmd",
        ("network", "wifi"),
    ),

    # ── Drivers / hardware ─────────────────────────────────────────────────
    SavedCommand(
        "List installed third-party drivers",
        "Filters driverquery output down to non-Microsoft drivers. The "
        "right thing to inventory before re-installing Windows so you know "
        "which OEM packages to grab again.",
        "driverquery /v /fo list", "cmd", ("drivers", "info"),
    ),
    SavedCommand(
        "List physical disks (PowerShell modern)",
        "Modern Get-PhysicalDisk view — shows friendly name, media type "
        "(HDD / SSD), health status (Healthy / Warning / Unhealthy) and "
        "size for every drive.",
        "Get-PhysicalDisk | Format-Table FriendlyName, MediaType, HealthStatus, Size -AutoSize",
        "powershell", ("disk", "info"),
    ),
    SavedCommand(
        "TRIM all SSDs now",
        "Forces a TRIM / retrim pass on every drive Windows recognises "
        "as an SSD. Improves long-term write performance, particularly "
        "on older SATA SSDs that haven’t been TRIMmed in months.",
        ("powershell -NoProfile -Command \"Get-Volume "
         "| Where-Object DriveType -eq 'Fixed' "
         "| ForEach-Object { Optimize-Volume -DriveLetter $_.DriveLetter -ReTrim -Verbose }\""),
        "powershell", ("disk", "ssd", "maintenance"),
    ),
    SavedCommand(
        "List USB devices ever seen by Windows",
        "Dumps every USB device ID that has ever been plugged in (even "
        "if not currently connected). Useful for forensics or removing "
        "stale device entries.",
        "Get-PnpDevice -Class USB | Format-Table FriendlyName, Status, InstanceId -AutoSize",
        "powershell", ("hardware", "usb"),
    ),

    # ── System info / license ──────────────────────────────────────────────
    SavedCommand(
        "Show Windows product key (OEM, baked into firmware)",
        "Reads the OEM activation key Microsoft baked into your "
        "motherboard’s BIOS at the factory. Handy before a wipe — "
        "Windows can re-activate from this even without a key prompt. "
        "Uses CIM because wmic was removed in Win 11 24H2+.",
        "(Get-CimInstance -ClassName SoftwareLicensingService).OA3xOriginalProductKey",
        "powershell", ("license", "info"),
    ),
    SavedCommand(
        "Show Windows activation status (slmgr)",
        "Reports whether Windows is permanently activated, in grace "
        "period, or unlicensed.",
        "cscript //nologo C:\\Windows\\System32\\slmgr.vbs /xpr",
        "cmd", ("license", "info"),
    ),
    SavedCommand(
        "Show installed RAM details",
        "Per-stick info: capacity, speed, manufacturer, part number, "
        "slot location.",
        ("Get-CimInstance Win32_PhysicalMemory "
         "| Format-Table BankLabel,Capacity,Speed,Manufacturer,PartNumber -AutoSize"),
        "powershell", ("hardware", "ram"),
    ),
    SavedCommand(
        "Show motherboard model + BIOS version",
        "Useful when you need to download the right chipset / BIOS update.",
        ("Get-CimInstance Win32_BaseBoard | Select-Object Manufacturer, Product, Version; "
         "Get-CimInstance Win32_BIOS    | Select-Object Manufacturer, Name, Version, ReleaseDate"),
        "powershell", ("hardware",),
    ),
    SavedCommand(
        "Uptime — how long has the PC been on?",
        "Shows when Windows last booted. ‘Have you tried turning it off "
        "and on again?’ — find out when you last actually did.",
        "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime", "powershell",
        ("info",),
    ),

    # ── Maintenance / cleanup ──────────────────────────────────────────────
    SavedCommand(
        "Empty Recycle Bin on every drive",
        "PowerShell one-liner equivalent to right-click → Empty Recycle Bin "
        "on every drive at once. Irreversible.",
        "Clear-RecycleBin -Force -ErrorAction SilentlyContinue", "powershell",
        ("cleanup",),
    ),
    SavedCommand(
        "Flush DNS cache",
        "Wipes all cached hostname→IP lookups. Try this first when a site "
        "loads fine on your phone but not your PC.",
        "ipconfig /flushdns", "cmd", ("network", "cleanup"),
    ),
    SavedCommand(
        "Defragment / re-trim C: drive",
        "Lets Windows decide — defrag if it’s a spinning HDD, TRIM if it’s "
        "an SSD. The safe ‘just maintain my drive’ button.",
        "defrag C: /O", "cmd", ("disk", "maintenance"),
    ),
    SavedCommand(
        "Sign out all other users",
        "Force-signs-out any other accounts that are still logged in "
        "behind the lock screen. Frees their RAM. Useful on shared PCs.",
        ("powershell -NoProfile -Command \"quser | ForEach-Object { "
         "$id = ($_ -split '\\s+')[2]; if ($id -match '^\\d+$') { logoff $id } }\""),
        "cmd", ("users",),
    ),
]

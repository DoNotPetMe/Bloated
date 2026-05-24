"""Windows Update — pause, defer, block drivers, force, revert."""
from __future__ import annotations

from ..tabs._models import Action


ACTIONS: list[Action] = [
    # ── Pause / quiet ───────────────────────────────────────────────────────
    Action(
        title="Pause Windows Update for 35 days",
        description=(
            "Sets the same ‘Pause until’ date you can set from Settings, but "
            "to the maximum value the UI allows (35 days). After that, "
            "Windows will start checking again — re-run this action to "
            "extend further."),
        command=(
            "$d = (Get-Date).AddDays(35).ToString('yyyy-MM-ddTHH:mm:ssZ'); "
            "New-Item -Path 'HKCU:\\Software\\Microsoft\\WindowsUpdate\\UX\\Settings' "
            "-Force | Out-Null; "
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\WindowsUpdate\\UX\\Settings' "
            "-Name PauseUpdatesExpiryTime -Value $d -Type String; "
            "Write-Host \"Updates paused until $d\""
        ),
        shell="powershell",
        category="Pause",
        enabled_by_default=False,
    ),
    Action(
        title="Mark Ethernet + cellular networks as ‘metered’",
        description=(
            "When Windows thinks the connection is metered, it pauses "
            "background downloads (including most updates) and reduces "
            "Store / OneDrive activity. Useful on a tethered phone or "
            "capped home plan."),
        command=(
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\NetworkList\\DefaultMediaCost" '
            '/v Ethernet /t REG_DWORD /d 2 /f & '
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\NetworkList\\DefaultMediaCost" '
            '/v 3G /t REG_DWORD /d 2 /f & '
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\NetworkList\\DefaultMediaCost" '
            '/v 4G /t REG_DWORD /d 2 /f'
        ),
        shell="cmd",
        category="Pause",
        enabled_by_default=False,
    ),
    Action(
        title="Disable automatic restart after updates",
        description=(
            "Stops Windows from rebooting you mid-task to ‘finish "
            "installing updates’. You still have to reboot eventually — "
            "but on YOUR schedule, not Microsoft’s."),
        command=(
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" '
            '/v NoAutoRebootWithLoggedOnUsers /t REG_DWORD /d 1 /f'
        ),
        shell="cmd",
        category="Pause",
        enabled_by_default=True,
    ),

    # ── Defer / restrict scope ──────────────────────────────────────────────
    Action(
        title="Stop Windows Update from installing drivers",
        description=(
            "Prevents Windows Update from silently replacing your installed "
            "GPU / Wi-Fi / chipset drivers. Strongly recommended — Windows "
            "Update drivers are usually older than what you manually "
            "installed."),
        command=(
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate" '
            '/v ExcludeWUDriversInQualityUpdate /t REG_DWORD /d 1 /f'
        ),
        shell="cmd",
        category="Defer",
        enabled_by_default=True,
    ),
    Action(
        title="Defer feature updates (big version jumps) for 365 days",
        description=(
            "Stops Windows from auto-upgrading you from e.g. 24H2 → 25H2 "
            "for a full year after release. Security & quality updates are "
            "unaffected — only the big version bumps are deferred."),
        command=(
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate" '
            '/v DeferFeatureUpdates /t REG_DWORD /d 1 /f & '
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate" '
            '/v DeferFeatureUpdatesPeriodInDays /t REG_DWORD /d 365 /f'
        ),
        shell="cmd",
        category="Defer",
        enabled_by_default=False,
    ),
    Action(
        title="Defer quality (monthly cumulative) updates for 14 days",
        description=(
            "Holds back monthly security/quality updates by 14 days so "
            "you’re not the first to install a buggy one. Reduces the "
            "chance of a Patch-Tuesday-broke-my-PC moment."),
        command=(
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate" '
            '/v DeferQualityUpdates /t REG_DWORD /d 1 /f & '
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate" '
            '/v DeferQualityUpdatesPeriodInDays /t REG_DWORD /d 14 /f'
        ),
        shell="cmd",
        category="Defer",
        enabled_by_default=False,
    ),
    Action(
        title="Disable peer-to-peer Delivery Optimization",
        description=(
            "Stops Windows from using your bandwidth to upload update "
            "chunks to other PCs on the internet. Updates still download "
            "from Microsoft directly."),
        command=(
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DeliveryOptimization" '
            '/v DODownloadMode /t REG_DWORD /d 0 /f'
        ),
        shell="cmd",
        category="Defer",
        enabled_by_default=True,
    ),

    # ── Manual ──────────────────────────────────────────────────────────────
    Action(
        title="Force a Windows Update check right now",
        description=(
            "Triggers usoclient to poll Microsoft immediately. Useful "
            "when you’ve just changed an update policy and want to see "
            "the new behaviour."),
        command="UsoClient StartScan",
        shell="cmd",
        category="Manual",
        enabled_by_default=False,
    ),
    Action(
        title="Open Settings → Windows Update",
        description=(
            "Just opens ms-settings:windowsupdate — same as clicking it in "
            "the Settings app."),
        command="start ms-settings:windowsupdate",
        shell="cmd",
        category="Manual",
        enabled_by_default=False,
    ),
    Action(
        title="Reset Windows Update components (heavy repair)",
        description=(
            "Stops the WU services, renames the cache folders to .old (so "
            "you can roll back), then restarts the services. Classic fix "
            "for ‘0x80…’ Windows Update errors."),
        command=(
            "net stop wuauserv & net stop cryptSvc & net stop bits & net stop msiserver & "
            'ren C:\\Windows\\SoftwareDistribution SoftwareDistribution.old & '
            'ren C:\\Windows\\System32\\catroot2 catroot2.old & '
            "net start wuauserv & net start cryptSvc & net start bits & net start msiserver"
        ),
        shell="cmd",
        category="Manual",
        enabled_by_default=False,
        danger=True,
    ),

    # ── Revert ──────────────────────────────────────────────────────────────
    Action(
        title="Undo all of the above (revert update policies)",
        description=(
            "Removes every WindowsUpdate / DeliveryOptimization / metered "
            "registry value this tab created. After running, Windows "
            "Update behaviour returns to factory defaults."),
        command=(
            'reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate" /f & '
            'reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /f & '
            'reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DeliveryOptimization" /f & '
            'reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\NetworkList\\DefaultMediaCost" /f & '
            'reg delete "HKCU\\Software\\Microsoft\\WindowsUpdate\\UX\\Settings" /v PauseUpdatesExpiryTime /f'
        ),
        shell="cmd",
        category="Revert",
        enabled_by_default=False,
        danger=True,
    ),
]

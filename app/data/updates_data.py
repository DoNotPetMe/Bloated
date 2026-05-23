"""Windows Update controls."""
from __future__ import annotations

from ..tabs._models import Action


ACTIONS: list[Action] = [
    Action(
        title="Pause Windows Update for 35 days",
        description=(
            "Sets the Settings → Windows Update pause-until date to 35 days from now. "
            "This is the maximum the UI supports without policy."),
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
        title="Set network as metered (slows background downloads)",
        description="Marks Ethernet/Wi-Fi default as metered so Update downloads pause.",
        command=(
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\NetworkList\\DefaultMediaCost" '
            '/v Ethernet /t REG_DWORD /d 2 /f & '
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\NetworkList\\DefaultMediaCost" '
            '/v 3G /t REG_DWORD /d 2 /f'
        ),
        shell="cmd",
        category="Pause",
        enabled_by_default=False,
    ),
    Action(
        title="Disable automatic driver updates via Windows Update",
        description="Prevents Windows Update from replacing your installed drivers.",
        command=(
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate" '
            '/v ExcludeWUDriversInQualityUpdate /t REG_DWORD /d 1 /f'
        ),
        shell="cmd",
        category="Defer",
        enabled_by_default=True,
    ),
    Action(
        title="Defer feature updates for 365 days",
        description="Branch readiness: stay on current feature build for up to a year.",
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
        title="Force check for updates now",
        description="Triggers the Update agent to poll Microsoft right now.",
        command="UsoClient StartScan",
        shell="cmd",
        category="Manual",
        enabled_by_default=False,
    ),
    Action(
        title="Open Windows Update settings",
        description="Opens Settings → Update directly.",
        command="start ms-settings:windowsupdate",
        shell="cmd",
        category="Manual",
        enabled_by_default=False,
    ),
    Action(
        title="Re-enable everything (undo all of the above)",
        description="Removes the Pause/Defer/MeteredNetwork policy values.",
        command=(
            'reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate" /f & '
            'reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\NetworkList\\DefaultMediaCost" /f & '
            'reg delete "HKCU\\Software\\Microsoft\\WindowsUpdate\\UX\\Settings" /v PauseUpdatesExpiryTime /f'
        ),
        shell="cmd",
        category="Revert",
        enabled_by_default=False,
        danger=True,
    ),
]

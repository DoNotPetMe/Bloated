"""Privacy hardening actions — registry tweaks + scheduled task disables."""
from __future__ import annotations

from ..tabs._models import Action


def _reg(hive: str, path: str, name: str, val, kind: str = "DWORD") -> str:
    """Build a `reg add` CMD line."""
    if kind == "DWORD":
        return (f'reg add "{hive}\\{path}" /v "{name}" /t REG_DWORD '
                f'/d {int(val)} /f')
    return (f'reg add "{hive}\\{path}" /v "{name}" /t REG_SZ '
            f'/d "{val}" /f')


ACTIONS: list[Action] = [
    Action(
        title="Disable Telemetry (DiagTrack)",
        description=(
            "Sets AllowTelemetry=0 and stops/disables the Connected User "
            "Experiences and Telemetry service (DiagTrack). This is the "
            "single biggest data-collection surface in Windows."),
        command=(
            _reg("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",
                 "AllowTelemetry", 0) + " & " +
            _reg("HKLM",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection",
                 "AllowTelemetry", 0) + " & " +
            "sc stop DiagTrack & sc config DiagTrack start=disabled"
        ),
        shell="cmd",
        category="Telemetry",
        enabled_by_default=True,
    ),
    Action(
        title="Disable Advertising ID",
        description="Apps can no longer use a unique ID to track you for ads.",
        command=_reg("HKCU",
                     r"SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
                     "Enabled", 0),
        shell="cmd",
        category="Telemetry",
        enabled_by_default=True,
    ),
    Action(
        title="Disable Activity History / Timeline",
        description=(
            "Stops Windows from collecting your app & file activity, and "
            "from syncing it to Microsoft."),
        command=(
            _reg("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\System",
                 "EnableActivityFeed", 0) + " & " +
            _reg("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\System",
                 "PublishUserActivities", 0) + " & " +
            _reg("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\System",
                 "UploadUserActivities", 0)
        ),
        shell="cmd",
        category="Telemetry",
        enabled_by_default=True,
    ),
    Action(
        title="Disable Cortana",
        description="Disables Cortana via policy. Search still works.",
        command=(
            _reg("HKLM",
                 r"SOFTWARE\Policies\Microsoft\Windows\Windows Search",
                 "AllowCortana", 0) + " & " +
            _reg("HKLM",
                 r"SOFTWARE\Policies\Microsoft\Windows\Windows Search",
                 "DisableWebSearch", 1)
        ),
        shell="cmd",
        category="Cortana / Search",
        enabled_by_default=True,
    ),
    Action(
        title="Disable Web Search in Start Menu",
        description="Hides Bing web results from the Start menu search.",
        command=(
            _reg("HKCU",
                 r"SOFTWARE\Policies\Microsoft\Windows\Explorer",
                 "DisableSearchBoxSuggestions", 1) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                 "BingSearchEnabled", 0)
        ),
        shell="cmd",
        category="Cortana / Search",
        enabled_by_default=True,
    ),
    Action(
        title="Disable Suggested Apps & Tips",
        description="Removes the ‘suggested’ apps in Start, lock screen ads, and tips.",
        command=(
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                 "SilentInstalledAppsEnabled", 0) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                 "SystemPaneSuggestionsEnabled", 0) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                 "SubscribedContent-338388Enabled", 0) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                 "SubscribedContent-338389Enabled", 0) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                 "RotatingLockScreenEnabled", 0)
        ),
        shell="cmd",
        category="Suggestions / Ads",
        enabled_by_default=True,
    ),
    Action(
        title="Disable Location Tracking",
        description="Globally denies location access at the system level.",
        command=_reg(
            "HKLM",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location",
            "Value", "Deny", kind="SZ"),
        shell="cmd",
        category="Sensors",
        enabled_by_default=False,
    ),
    Action(
        title="Disable Windows Recall (W11)",
        description=(
            "Disables Recall on Copilot+ PCs by policy. Recall snapshots your "
            "screen continuously — this turns the whole feature off."),
        command=(
            _reg("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\WindowsAI",
                 "DisableAIDataAnalysis", 1) + " & " +
            _reg("HKCU", r"SOFTWARE\Policies\Microsoft\Windows\WindowsAI",
                 "DisableAIDataAnalysis", 1)
        ),
        shell="cmd",
        category="Copilot / AI",
        enabled_by_default=True,
    ),
    Action(
        title="Disable Copilot button & Copilot in Windows",
        description="Hides the Copilot button and disables Copilot.",
        command=(
            _reg("HKCU", r"SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot",
                 "TurnOffWindowsCopilot", 1) + " & " +
            _reg("HKCU", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                 "ShowCopilotButton", 0)
        ),
        shell="cmd",
        category="Copilot / AI",
        enabled_by_default=True,
    ),
    Action(
        title="Disable CEIP / Customer Experience scheduled tasks",
        description="Disables the Customer Experience Improvement Program tasks.",
        command=(
            'schtasks /Change /TN "Microsoft\\Windows\\Application Experience\\Microsoft Compatibility Appraiser" /Disable & '
            'schtasks /Change /TN "Microsoft\\Windows\\Application Experience\\ProgramDataUpdater" /Disable & '
            'schtasks /Change /TN "Microsoft\\Windows\\Autochk\\Proxy" /Disable & '
            'schtasks /Change /TN "Microsoft\\Windows\\Customer Experience Improvement Program\\Consolidator" /Disable & '
            'schtasks /Change /TN "Microsoft\\Windows\\Customer Experience Improvement Program\\UsbCeip" /Disable'
        ),
        shell="cmd",
        category="Telemetry",
        enabled_by_default=True,
    ),
    Action(
        title="Disable Error Reporting",
        description="Stops Windows Error Reporting (WER) uploads.",
        command=(
            _reg("HKLM",
                 r"SOFTWARE\Microsoft\Windows\Windows Error Reporting",
                 "Disabled", 1) + " & " +
            "sc stop WerSvc & sc config WerSvc start=disabled"
        ),
        shell="cmd",
        category="Telemetry",
        enabled_by_default=True,
    ),
    Action(
        title="Disable Wi-Fi Sense",
        description="Prevents auto-sharing of Wi-Fi credentials.",
        command=(
            _reg("HKLM",
                 r"SOFTWARE\Microsoft\PolicyManager\default\WiFi\AllowWiFiHotSpotReporting",
                 "Value", 0) + " & " +
            _reg("HKLM",
                 r"SOFTWARE\Microsoft\PolicyManager\default\WiFi\AllowAutoConnectToWiFiSenseHotspots",
                 "Value", 0)
        ),
        shell="cmd",
        category="Network",
        enabled_by_default=True,
    ),
]

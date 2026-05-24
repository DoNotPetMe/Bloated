"""Privacy hardening — telemetry, ads, tracking, suggested content, AI features."""
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
    # ── Telemetry ───────────────────────────────────────────────────────────
    Action(
        title="Disable Telemetry (DiagTrack)",
        description=(
            "The biggest data-collection switch in Windows. Sets "
            "AllowTelemetry=0 and stops/disables the ‘Connected User "
            "Experiences and Telemetry’ service. After this, Windows stops "
            "sending diagnostic + usage data back to Microsoft. Some "
            "Feedback / Troubleshoot features will go quiet — that’s "
            "intentional."),
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
        description=(
            "Every Windows account has a per-user ‘advertising ID’ that apps "
            "use to track you across the system for targeted ads. Turning "
            "this off makes ads less personalised — they don’t go away, "
            "but they can’t follow you between apps."),
        command=_reg("HKCU",
                     r"SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
                     "Enabled", 0),
        shell="cmd",
        category="Telemetry",
        enabled_by_default=True,
    ),
    Action(
        title="Disable Activity History / Windows Timeline",
        description=(
            "‘Activity History’ records which apps you open and which files "
            "you touch, then optionally syncs that across your Microsoft "
            "account. This action stops both the local recording and the "
            "cloud sync. The Win+Tab Timeline view will be empty afterwards."),
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
        title="Disable ‘Inking & Typing’ data collection",
        description=(
            "When this is on, Windows learns from what you type and write "
            "to improve autocomplete — and ships a snapshot to Microsoft. "
            "Disabling has no visible effect on day-to-day typing."),
        command=(
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\InputPersonalization",
                 "RestrictImplicitTextCollection", 1) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\InputPersonalization",
                 "RestrictImplicitInkCollection", 1) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Personalization\Settings",
                 "AcceptedPrivacyPolicy", 0)
        ),
        shell="cmd",
        category="Telemetry",
        enabled_by_default=True,
    ),
    Action(
        title="Disable Error Reporting (WER)",
        description=(
            "When an app crashes, Windows Error Reporting bundles up a "
            "crash dump and uploads it to Microsoft. Turning this off "
            "removes those uploads. You’ll still see ‘app is not "
            "responding’ dialogs locally — they just don’t phone home."),
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
        title="Disable CEIP scheduled tasks",
        description=(
            "Microsoft’s ‘Customer Experience Improvement Program’ runs "
            "background scheduled tasks that profile your hardware and app "
            "compatibility, then upload reports. This disables all five "
            "main tasks at once: Compatibility Appraiser, ProgramDataUpdater, "
            "Autochk Proxy, Consolidator, and UsbCeip."),
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

    # ── Cortana / Search ────────────────────────────────────────────────────
    Action(
        title="Disable Cortana",
        description=(
            "Switches Cortana off via Group Policy. Local Start-menu search "
            "still works perfectly — only the ‘ask Cortana’ assistant goes "
            "away. Microsoft has already deprecated Cortana in Windows 11 "
            "anyway."),
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
        title="Remove Bing web results from Start menu",
        description=(
            "Stops the Start menu from sending what you type to Bing and "
            "showing web suggestions / sponsored results inside the Start "
            "search box. Result: Start search becomes local-only and "
            "noticeably faster."),
        command=(
            _reg("HKCU",
                 r"SOFTWARE\Policies\Microsoft\Windows\Explorer",
                 "DisableSearchBoxSuggestions", 1) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                 "BingSearchEnabled", 0) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                 "CortanaConsent", 0)
        ),
        shell="cmd",
        category="Cortana / Search",
        enabled_by_default=True,
    ),

    # ── Suggestions / Ads ───────────────────────────────────────────────────
    Action(
        title="Disable ‘Suggested apps’ in Start menu",
        description=(
            "Removes the rotating ‘Suggested’ row in Start (often pushing "
            "Microsoft 365, Edge, Game Pass, etc.) and turns off the "
            "‘install new apps occasionally’ silent push from Microsoft."),
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
                 "SubscribedContent-310093Enabled", 0)
        ),
        shell="cmd",
        category="Suggestions / Ads",
        enabled_by_default=True,
    ),
    Action(
        title="Disable Lock-screen ads & ‘Windows Spotlight’ tips",
        description=(
            "Stops the lock screen from rotating through Microsoft’s "
            "marketing pictures and ‘fun facts’ — usually a thinly-veiled "
            "ad. After this, your lock screen uses a static image you set "
            "yourself."),
        command=(
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                 "RotatingLockScreenEnabled", 0) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                 "RotatingLockScreenOverlayEnabled", 0) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                 "SubscribedContent-338387Enabled", 0)
        ),
        shell="cmd",
        category="Suggestions / Ads",
        enabled_by_default=True,
    ),
    Action(
        title="Disable ‘Tips, tricks and suggestions’ notifications",
        description=(
            "Stops the periodic ‘Did you know you can…’ popups in the "
            "Action Center and the welcome / tour overlays after updates."),
        command=(
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                 "SoftLandingEnabled", 0) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                 "SubscribedContent-338393Enabled", 0) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                 "SubscribedContent-353694Enabled", 0) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                 "SubscribedContent-353696Enabled", 0)
        ),
        shell="cmd",
        category="Suggestions / Ads",
        enabled_by_default=True,
    ),
    Action(
        title="Disable File Explorer ads (‘ads in your File Explorer’)",
        description=(
            "Yes, File Explorer is sometimes used to advertise OneDrive / "
            "Microsoft 365. Turns off ‘Sync provider notifications’."),
        command=_reg(
            "HKCU",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
            "ShowSyncProviderNotifications", 0),
        shell="cmd",
        category="Suggestions / Ads",
        enabled_by_default=True,
    ),
    Action(
        title="Disable ‘Finish setting up your device’ nag",
        description=(
            "The full-screen popup after major updates that pushes OneDrive, "
            "Outlook, Edge defaults, etc. Disabled by policy."),
        command=_reg(
            "HKCU",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\UserProfileEngagement",
            "ScoobeSystemSettingEnabled", 0),
        shell="cmd",
        category="Suggestions / Ads",
        enabled_by_default=True,
    ),

    # ── Copilot / AI ────────────────────────────────────────────────────────
    Action(
        title="Disable Windows Recall (W11 / Copilot+ PCs)",
        description=(
            "Recall takes a continuous screenshot of EVERYTHING you do and "
            "stores it locally so the AI can ‘remember’ it. This action "
            "completely disables that feature via policy. Recommended unless "
            "you specifically opted in to Recall."),
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
        title="Disable Copilot in Windows + hide the Copilot button",
        description=(
            "Turns off Windows Copilot entirely and removes the Copilot "
            "button from the taskbar. Edge’s sidebar Copilot is separate "
            "(see ‘Disable Edge Copilot/sidebar’ if you also want that)."),
        command=(
            _reg("HKCU", r"SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot",
                 "TurnOffWindowsCopilot", 1) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                 "ShowCopilotButton", 0)
        ),
        shell="cmd",
        category="Copilot / AI",
        enabled_by_default=True,
    ),
    Action(
        title="Disable Bing chat / Copilot in Edge sidebar",
        description=(
            "Removes the discover/Copilot button from the Edge sidebar and "
            "prevents new Copilot tabs from popping up on browser launch."),
        command=(
            _reg("HKLM", r"SOFTWARE\Policies\Microsoft\Edge",
                 "HubsSidebarEnabled", 0) + " & " +
            _reg("HKLM", r"SOFTWARE\Policies\Microsoft\Edge",
                 "EdgeAssetDeliveryService", 0)
        ),
        shell="cmd",
        category="Copilot / AI",
        enabled_by_default=False,
    ),
    Action(
        title="Disable Click-to-Do / AI in Snipping Tool",
        description=(
            "Disables the new ‘Click to Do’ AI overlay (analyse anything "
            "on screen) and AI features bundled into Snipping Tool / "
            "Notepad on newer Copilot+ devices."),
        command=(
            _reg("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\WindowsAI",
                 "DisableClickToDo", 1) + " & " +
            _reg("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\WindowsAI",
                 "DisableAIDataAnalysisProgramHistory", 1)
        ),
        shell="cmd",
        category="Copilot / AI",
        enabled_by_default=True,
    ),

    # ── Sensors ─────────────────────────────────────────────────────────────
    Action(
        title="Block all apps from using your Location",
        description=(
            "Sets the system-wide location consent to ‘Deny’. After this, "
            "even apps that were previously granted location access stop "
            "getting coordinates."),
        command=_reg(
            "HKLM",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location",
            "Value", "Deny", kind="SZ"),
        shell="cmd",
        category="Sensors",
        enabled_by_default=False,
    ),
    Action(
        title="Block all apps from using your Camera",
        description=(
            "System-wide deny for the Camera privacy switch. Useful on a "
            "shared / public PC. Reverse from Settings → Privacy → Camera."),
        command=_reg(
            "HKLM",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam",
            "Value", "Deny", kind="SZ"),
        shell="cmd",
        category="Sensors",
        enabled_by_default=False,
    ),
    Action(
        title="Block all apps from using your Microphone",
        description=(
            "System-wide deny for the Microphone privacy switch."),
        command=_reg(
            "HKLM",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone",
            "Value", "Deny", kind="SZ"),
        shell="cmd",
        category="Sensors",
        enabled_by_default=False,
    ),

    # ── Network privacy ─────────────────────────────────────────────────────
    Action(
        title="Disable Wi-Fi Sense",
        description=(
            "‘Wi-Fi Sense’ used to auto-share Wi-Fi passwords with your "
            "contacts. Microsoft killed most of it years ago but the "
            "scaffolding remains — this turns it off properly."),
        command=(
            _reg("HKLM",
                 r"SOFTWARE\Microsoft\PolicyManager\default\WiFi\AllowWiFiHotSpotReporting",
                 "Value", 0) + " & " +
            _reg("HKLM",
                 r"SOFTWARE\Microsoft\PolicyManager\default\WiFi\AllowAutoConnectToWiFiSenseHotspots",
                 "Value", 0)
        ),
        shell="cmd",
        category="Network privacy",
        enabled_by_default=True,
    ),
    Action(
        title="Stop sending typing / handwriting samples (P2P)",
        description=(
            "Disables peer-to-peer delivery of typing / inking improvement "
            "data over the LAN."),
        command=_reg(
            "HKLM", r"SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization",
            "DODownloadMode", 0),
        shell="cmd",
        category="Network privacy",
        enabled_by_default=False,
    ),
]

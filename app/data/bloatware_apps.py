"""Curated list of Windows 10/11 stock UWP apps commonly considered bloatware.

Each entry produces an Action that runs:
    Get-AppxPackage -AllUsers <pkg> | Remove-AppxPackage -AllUsers
which uninstalls the app for every user and prevents it from re-provisioning
for new accounts.

The list errs on the side of "safe to remove for most desktop users"; nothing
in here will brick Windows. Keep your selection conservative if you actually
use any of these apps.
"""
from __future__ import annotations

from ..tabs._models import Action

# (PackageFullName-pattern, friendly title, description, category)
_APPS = [
    # ── Microsoft default UWP ────────────────────────────────────────────────
    ("Microsoft.BingWeather",            "Bing Weather",
     "Stock weather app — usually replaced by browser/widgets.",         "Microsoft"),
    ("Microsoft.BingNews",               "Bing News",
     "News feed UWP app, often unused.",                                 "Microsoft"),
    ("Microsoft.BingSearch",             "Bing Search",
     "Web search panel embedded in the taskbar.",                        "Microsoft"),
    ("Microsoft.GetHelp",                "Get Help",
     "Microsoft’s support chat app.",                                     "Microsoft"),
    ("Microsoft.Getstarted",             "Tips / Get Started",
     "First-run tutorial app — safe to remove.",                          "Microsoft"),
    ("Microsoft.Microsoft3DViewer",      "3D Viewer",
     "Legacy 3D model viewer (Paint 3D companion).",                      "Microsoft"),
    ("Microsoft.MicrosoftOfficeHub",     "Office Hub",
     "‘Get Office’ launcher — does not uninstall a real Office install.", "Microsoft"),
    ("Microsoft.MicrosoftSolitaireCollection", "Solitaire Collection",
     "Microsoft Solitaire (ad-supported).",                               "Games"),
    ("Microsoft.MixedReality.Portal",    "Mixed Reality Portal",
     "Windows MR portal — only useful if you own a WMR headset.",         "Microsoft"),
    ("Microsoft.MSPaint",                "Paint 3D",
     "Old Paint 3D (note: ‘mspaint.exe’ classic Paint is separate).",     "Microsoft"),
    ("Microsoft.NetworkSpeedTest",       "Network Speed Test",
     "Legacy Microsoft speed test app.",                                  "Microsoft"),
    ("Microsoft.News",                   "MSN News",
     "MSN-branded news app.",                                             "Microsoft"),
    ("Microsoft.Office.OneNote",         "OneNote (Store)",
     "UWP OneNote — distinct from desktop OneNote.",                      "Microsoft"),
    ("Microsoft.OneConnect",             "OneConnect / Mobile Plans",
     "Mobile broadband purchase app.",                                    "Microsoft"),
    ("Microsoft.People",                 "People",
     "Stock contacts hub.",                                               "Microsoft"),
    ("Microsoft.Print3D",                "Print 3D",
     "3D printing companion to Paint 3D.",                                "Microsoft"),
    ("Microsoft.SkypeApp",               "Skype",
     "Pre-installed Skype client.",                                       "Microsoft"),
    ("Microsoft.Wallet",                 "Wallet",
     "Deprecated Microsoft Wallet app.",                                  "Microsoft"),
    ("Microsoft.WindowsAlarms",          "Alarms & Clock",
     "Built-in alarms / world clock / timer.",                            "Microsoft"),
    ("Microsoft.WindowsCamera",          "Camera",
     "Stock webcam app. Removing means no built-in camera UI.",           "Microsoft"),
    ("microsoft.windowscommunicationsapps", "Mail and Calendar",
     "Stock UWP mail + calendar client.",                                 "Microsoft"),
    ("Microsoft.WindowsFeedbackHub",     "Feedback Hub",
     "Insider feedback app — pure telemetry surface.",                    "Microsoft"),
    ("Microsoft.WindowsMaps",            "Maps",
     "Bing Maps UWP app.",                                                "Microsoft"),
    ("Microsoft.WindowsSoundRecorder",   "Sound Recorder",
     "Stock voice recorder.",                                             "Microsoft"),
    ("Microsoft.YourPhone",              "Phone Link / Your Phone",
     "Phone mirroring app — remove if you don’t link an Android.",        "Microsoft"),
    ("Microsoft.ZuneMusic",              "Groove Music / Media Player",
     "Legacy Groove (now part of Windows Media Player).",                 "Microsoft"),
    ("Microsoft.ZuneVideo",              "Movies & TV",
     "Microsoft Films/TV storefront.",                                    "Microsoft"),
    ("Microsoft.MicrosoftStickyNotes",   "Sticky Notes",
     "Floating notes app.",                                               "Microsoft"),
    ("Microsoft.Todos",                  "Microsoft To Do",
     "MS To-Do task app.",                                                "Microsoft"),
    ("Clipchamp.Clipchamp",              "Clipchamp",
     "Bundled video editor (acquired by Microsoft).",                     "Microsoft"),
    ("Microsoft.PowerAutomateDesktop",   "Power Automate Desktop",
     "RPA tool — bundled in W11. Useful for some, bloat for most.",       "Microsoft"),
    ("Microsoft.MicrosoftFamilySafety",  "Family Safety",
     "Parental controls app.",                                            "Microsoft"),
    ("Microsoft.WindowsTerminal",        "Windows Terminal",
     "WARNING: removing breaks the new default console.",                 "Microsoft"),

    # ── Xbox stack ──────────────────────────────────────────────────────────
    ("Microsoft.XboxApp",                "Xbox (legacy)",                 "Old Xbox app.",                                                    "Xbox / Gaming"),
    ("Microsoft.XboxGamingOverlay",      "Xbox Game Bar",                 "Win+G overlay. Removing disables screen recording shortcut.",       "Xbox / Gaming"),
    ("Microsoft.XboxGameOverlay",        "Xbox Game Overlay",             "Companion to Game Bar.",                                            "Xbox / Gaming"),
    ("Microsoft.XboxIdentityProvider",   "Xbox Identity Provider",        "Auth for Xbox Live in games.",                                       "Xbox / Gaming"),
    ("Microsoft.XboxSpeechToTextOverlay","Xbox Speech-to-Text Overlay",   "Accessibility overlay for Xbox.",                                    "Xbox / Gaming"),
    ("Microsoft.Xbox.TCUI",              "Xbox TCUI",
     "Required UI shell for Xbox-aware games. Only remove if you don’t game.", "Xbox / Gaming"),
    ("Microsoft.GamingApp",              "Xbox app (Windows 11)",         "Current Xbox app + Game Pass client.",                              "Xbox / Gaming"),

    # ── Misc / 3rd-party often pre-bundled on OEM Windows ──────────────────
    ("*EclipseManager*",        "Eclipse Manager",         "OEM bloat.",       "OEM / 3rd-party"),
    ("*ActiproSoftwareLLC*",    "Actipro Code Editor",     "Sample UWP app.",  "OEM / 3rd-party"),
    ("*AdobePhotoshopExpress*", "Adobe Photoshop Express", "Promo install.",   "OEM / 3rd-party"),
    ("*Duolingo-LearnLanguagesForFree*","Duolingo",        "Promo install.",   "OEM / 3rd-party"),
    ("*PandoraMediaInc*",       "Pandora",                 "Promo install.",   "OEM / 3rd-party"),
    ("*CandyCrush*",            "Candy Crush",             "Promo game.",      "OEM / 3rd-party"),
    ("*BubbleWitch3Saga*",      "Bubble Witch 3",          "Promo game.",      "OEM / 3rd-party"),
    ("*Wunderlist*",            "Wunderlist",              "Discontinued.",    "OEM / 3rd-party"),
    ("*Flipboard*",             "Flipboard",               "News reader.",     "OEM / 3rd-party"),
    ("*Twitter*",               "Twitter (Store)",         "UWP Twitter app.", "OEM / 3rd-party"),
    ("*Facebook*",              "Facebook (Store)",        "UWP Facebook app.","OEM / 3rd-party"),
    ("*Spotify*",               "Spotify (Store edition)", "Pre-installed Spotify UWP — desktop install is separate.", "OEM / 3rd-party"),
    ("*Netflix*",               "Netflix",                 "Pre-installed Netflix UWP.", "OEM / 3rd-party"),
    ("*Disney*",                "Disney+",                 "Pre-installed Disney+ UWP.", "OEM / 3rd-party"),
    ("*TikTok*",                "TikTok",                  "Pre-installed TikTok UWP.",  "OEM / 3rd-party"),
    ("*LinkedIn*",              "LinkedIn",                "Pre-installed LinkedIn UWP.","OEM / 3rd-party"),
    ("*Instagram*",             "Instagram",               "Pre-installed Instagram UWP.","OEM / 3rd-party"),
]

# Defaults we recommend turning on
_RECOMMENDED = {
    "Microsoft.BingNews", "Microsoft.BingSearch", "Microsoft.MicrosoftOfficeHub",
    "Microsoft.MicrosoftSolitaireCollection", "Microsoft.MixedReality.Portal",
    "Microsoft.Microsoft3DViewer", "Microsoft.MSPaint", "Microsoft.OneConnect",
    "Microsoft.Print3D", "Microsoft.SkypeApp", "Microsoft.WindowsFeedbackHub",
    "Microsoft.WindowsMaps", "Microsoft.YourPhone", "Microsoft.ZuneMusic",
    "Microsoft.ZuneVideo", "Microsoft.GetHelp", "Microsoft.Getstarted",
    "Microsoft.MicrosoftFamilySafety", "Microsoft.NetworkSpeedTest",
    "Microsoft.Wallet", "Clipchamp.Clipchamp",
    "*CandyCrush*", "*BubbleWitch3Saga*", "*Duolingo-LearnLanguagesForFree*",
    "*PandoraMediaInc*", "*Flipboard*", "*Twitter*", "*Facebook*",
    "*TikTok*", "*LinkedIn*", "*Instagram*", "*Netflix*", "*Disney*",
}


def _ps_remove(pkg: str) -> str:
    """Build the PowerShell one-liner that removes the AppX for everyone and
    de-provisions it from new accounts."""
    # Single quote escaping: PowerShell uses '' inside ''
    safe = pkg.replace("'", "''")
    return (
        f"Get-AppxPackage -AllUsers -Name '{safe}' -ErrorAction SilentlyContinue "
        f"| Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue; "
        f"Get-AppxProvisionedPackage -Online "
        f"| Where-Object {{ $_.DisplayName -like '{safe}' }} "
        f"| Remove-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue "
        f"| Out-Null; Write-Host 'Done: {safe}'"
    )


def build() -> list[Action]:
    actions: list[Action] = []
    for pkg, title, desc, cat in _APPS:
        actions.append(Action(
            title=f"Remove {title}",
            description=desc + f"  ·  package: {pkg}",
            command=_ps_remove(pkg),
            shell="powershell",
            category=cat,
            danger=True,
            enabled_by_default=(pkg in _RECOMMENDED),
        ))
    return actions

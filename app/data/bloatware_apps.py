"""Curated list of Windows 10/11 stock UWP apps commonly considered bloatware.

Each entry produces an Action that uninstalls the app for *every* user account
on the PC and also de-provisions it so it won't reinstall itself for any
brand-new account created later.

The list is conservative — nothing in here will brick Windows. But "bloat" is
in the eye of the beholder: leave anything ticked off that you actually use.
"""
from __future__ import annotations

from ..tabs._models import Action

# (PackageFullName-pattern, friendly title, plain-English description, category)
_APPS = [
    # ── Microsoft default UWP ────────────────────────────────────────────────
    ("Microsoft.BingWeather",            "Bing Weather",
     "The little weather tile in the Start menu. Most people just check the "
     "weather in their browser or on their phone, so this is usually safe to "
     "remove.",                                                          "Microsoft"),

    ("Microsoft.BingNews",               "Bing News",
     "MSN/Bing news feed app. Same content shows up in Edge’s new-tab page "
     "and the taskbar widgets, so removing this rarely loses anything.",
                                                                        "Microsoft"),

    ("Microsoft.BingSearch",             "Bing Search",
     "The web-search panel that pops up when you start typing in the Start "
     "menu. Removing it makes Start search local-only, which is exactly what "
     "most people want.",                                                "Microsoft"),

    ("Microsoft.GetHelp",                "Get Help",
     "Microsoft’s built-in support chat / troubleshoot wizard. Almost no one "
     "uses this — when something’s broken people google the error message.",
                                                                        "Microsoft"),

    ("Microsoft.Getstarted",             "Tips / Get Started",
     "The little ‘welcome to Windows’ walkthrough that shows on first launch. "
     "Pure first-run nag — completely safe to delete.",                  "Microsoft"),

    ("Microsoft.Microsoft3DViewer",      "3D Viewer",
     "Lets you spin around .fbx and .glb 3D models. Useful for designers, "
     "useless for everyone else.",                                       "Microsoft"),

    ("Microsoft.MicrosoftOfficeHub",     "Office Hub (‘Get Office’)",
     "An ad/launcher for Microsoft 365. Removing this does NOT touch a real "
     "Office install — it only kills the ‘Buy Office now’ tile.",        "Microsoft"),

    ("Microsoft.MicrosoftSolitaireCollection", "Microsoft Solitaire",
     "Solitaire/FreeCell/etc. Ad-supported — if you actually play, keep it; "
     "otherwise it’s just background updates and notifications.",        "Games"),

    ("Microsoft.MixedReality.Portal",    "Mixed Reality Portal",
     "Setup app for Windows Mixed Reality headsets (Acer/HP/Samsung Odyssey, "
     "etc.). Pointless unless you own one, and WMR is being retired in 2026.",
                                                                        "Microsoft"),

    ("Microsoft.MSPaint",                "Paint 3D",
     "Old ‘Paint 3D’ — NOT the classic Paint program. Classic Paint "
     "(mspaint.exe) stays installed and untouched.",                     "Microsoft"),

    ("Microsoft.NetworkSpeedTest",       "Network Speed Test",
     "Microsoft’s ancient speed-test app. Fast.com or speedtest.net do it "
     "better and don’t need installing.",                                "Microsoft"),

    ("Microsoft.News",                   "MSN News",
     "Almost identical to Bing News, just an older shell. Safe to remove.",
                                                                        "Microsoft"),

    ("Microsoft.Office.OneNote",         "OneNote for Windows 10",
     "The store-version of OneNote. If you use desktop OneNote (part of "
     "Office), this duplicate is harmless to remove.",                   "Microsoft"),

    ("Microsoft.OneConnect",             "OneConnect / Mobile Plans",
     "‘Buy cellular data plans from your PC.’ Only useful on a few LTE-enabled "
     "Surface devices. Everyone else can wipe it.",                       "Microsoft"),

    ("Microsoft.People",                 "People",
     "Stock contacts hub that nobody opens. Removing it also removes the "
     "‘People’ pinned-contacts feature on the taskbar.",                  "Microsoft"),

    ("Microsoft.Print3D",                "Print 3D",
     "Send 3D models to a 3D printer. If you don’t own a 3D printer this "
     "is doing nothing for you.",                                         "Microsoft"),

    ("Microsoft.SkypeApp",               "Skype",
     "Pre-installed Skype. Microsoft retired consumer Skype in May 2025 — "
     "this is just a leftover icon now.",                                 "Microsoft"),

    ("Microsoft.Wallet",                 "Wallet",
     "Microsoft’s discontinued attempt at Apple Wallet. Doesn’t do anything "
     "anymore.",                                                          "Microsoft"),

    ("Microsoft.WindowsAlarms",          "Alarms & Clock",
     "Built-in alarms, world clock and timer. Handy on a tablet, useless on "
     "a desktop — keep if you ever set an alarm on your PC.",             "Microsoft"),

    ("Microsoft.WindowsCamera",          "Camera",
     "The built-in webcam app. Removing it doesn’t disable your webcam — "
     "other apps (Zoom, Teams, OBS, the browser) still see it. You just "
     "lose the simple ‘take a photo’ UI.",                                "Microsoft"),

    ("microsoft.windowscommunicationsapps", "Mail and Calendar",
     "Stock UWP Mail + Calendar. Being replaced by ‘new Outlook’ anyway; "
     "remove if you use Gmail/Outlook web / Thunderbird / a desktop client.",
                                                                         "Microsoft"),

    ("Microsoft.WindowsFeedbackHub",     "Feedback Hub",
     "Where Insider builds send ‘how was this build?’ surveys. If you’re not "
     "in the Insider program this is just a telemetry channel.",          "Microsoft"),

    ("Microsoft.WindowsMaps",            "Maps",
     "Bing-powered offline-capable maps. Most people just use Google Maps in "
     "their browser; remove unless you actually use it for navigation.",  "Microsoft"),

    ("Microsoft.WindowsSoundRecorder",   "Sound Recorder",
     "Stock voice-recorder app. If you ever record voice memos on your PC, "
     "keep it; otherwise gone.",                                          "Microsoft"),

    ("Microsoft.YourPhone",              "Phone Link (‘Your Phone’)",
     "Mirrors texts/calls/notifications from an Android (and limited iOS) "
     "phone onto your PC. Only useful if you actually link your phone — "
     "otherwise it sits in the background doing pings.",                  "Microsoft"),

    ("Microsoft.ZuneMusic",              "Groove Music / Media Player",
     "The old Groove player, now folded into the modern Windows Media "
     "Player. If you stream music in a browser, you don’t need it.",      "Microsoft"),

    ("Microsoft.ZuneVideo",              "Movies & TV",
     "Microsoft’s film/TV storefront. Almost nobody buys movies here — "
     "Netflix, Prime, Disney+ etc. cover this in the browser.",           "Microsoft"),

    ("Microsoft.MicrosoftStickyNotes",   "Sticky Notes",
     "Yellow Post-it notes on the desktop. Some people live in these; "
     "if you’ve never opened it, remove it.",                             "Microsoft"),

    ("Microsoft.Todos",                  "Microsoft To Do",
     "Microsoft’s task-list app (acquired Wunderlist). Keep only if you "
     "actually use it.",                                                  "Microsoft"),

    ("Clipchamp.Clipchamp",              "Clipchamp Video Editor",
     "Microsoft’s in-browser-feeling video editor. Free tier is heavily "
     "watermarked/limited — most people grab a real editor instead.",     "Microsoft"),

    ("Microsoft.PowerAutomateDesktop",   "Power Automate Desktop",
     "Microsoft’s ‘record and replay’ desktop automation tool. Powerful for "
     "office workflows, total bloat if you never open it.",               "Microsoft"),

    ("Microsoft.MicrosoftFamilySafety",  "Family Safety",
     "Parental controls dashboard. Only useful if you actually manage a "
     "child account on this PC.",                                         "Microsoft"),

    ("Microsoft.WindowsTerminal",        "Windows Terminal",
     "⚠️ The new default terminal in Windows 11. Removing this means "
     "right-click → ‘Open in Terminal’ and Ctrl+~ in many apps will break. "
     "Only remove if you know you don’t want it.",                        "Microsoft"),

    ("Microsoft.OutlookForWindows",      "New Outlook",
     "The ‘new’ web-based Outlook Microsoft is force-installing. Removing "
     "is safe if you use classic Outlook, the browser, or another mail "
     "client.",                                                            "Microsoft"),

    ("Microsoft.GamingApp",              "Xbox app (Windows 11)",
     "Current Xbox app + Game Pass client. Remove only if you don’t use "
     "Game Pass on PC.",                                                  "Xbox / Gaming"),

    # ── Xbox stack ──────────────────────────────────────────────────────────
    ("Microsoft.XboxApp",                "Xbox (legacy app)",
     "The OLD Xbox app from Windows 10. Replaced by ‘Xbox app (Windows 11)’ "
     "above. Almost always safe to remove.",                              "Xbox / Gaming"),

    ("Microsoft.XboxGamingOverlay",      "Xbox Game Bar",
     "The Win+G overlay used for screen recording, FPS counter, etc. "
     "Removing it kills the keyboard shortcut to start a screen recording.",
                                                                          "Xbox / Gaming"),

    ("Microsoft.XboxGameOverlay",        "Xbox Game Overlay",
     "Internal companion package to Game Bar. Remove together with Game Bar "
     "above for a clean uninstall.",                                      "Xbox / Gaming"),

    ("Microsoft.XboxIdentityProvider",   "Xbox Identity Provider",
     "Background sign-in service for games that talk to Xbox Live. Keep if "
     "you play any Microsoft Store / Game Pass games.",                   "Xbox / Gaming"),

    ("Microsoft.XboxSpeechToTextOverlay","Xbox Speech-to-Text Overlay",
     "Accessibility overlay that turns voice chat into on-screen captions "
     "for Xbox games. Useless on non-Xbox games.",                        "Xbox / Gaming"),

    ("Microsoft.Xbox.TCUI",              "Xbox TCUI",
     "Trusted Cross-platform UI — the popup UI Xbox-aware games use for "
     "invites, leaderboards, etc. Remove only if you genuinely never play "
     "Xbox-connected games.",                                              "Xbox / Gaming"),

    # ── Misc / 3rd-party often pre-bundled on OEM Windows ──────────────────
    ("*EclipseManager*",        "Eclipse Manager",
     "OEM time-management bloat. Always safe to remove.",                 "OEM / 3rd-party"),

    ("*ActiproSoftwareLLC*",    "Actipro Code Editor",
     "Microsoft sample app shipped on a few OEM builds. Useless.",        "OEM / 3rd-party"),

    ("*AdobePhotoshopExpress*", "Adobe Photoshop Express",
     "Free Photoshop Express. Pre-installed promo — remove unless you "
     "actually use it.",                                                  "OEM / 3rd-party"),

    ("*Duolingo-LearnLanguagesForFree*","Duolingo",
     "Promo install of the Duolingo language app.",                       "OEM / 3rd-party"),

    ("*PandoraMediaInc*",       "Pandora",
     "Promo install of the Pandora music app. Doesn’t even work outside "
     "the US for many users.",                                            "OEM / 3rd-party"),

    ("*CandyCrush*",            "Candy Crush",
     "Yes, Windows still pre-installs Candy Crush in 2026. Remove.",      "OEM / 3rd-party"),

    ("*BubbleWitch3Saga*",      "Bubble Witch 3",
     "Same publisher (King) as Candy Crush. Promo game.",                 "OEM / 3rd-party"),

    ("*Wunderlist*",            "Wunderlist",
     "Discontinued — replaced by Microsoft To Do years ago. Just a dead "
     "icon now.",                                                         "OEM / 3rd-party"),

    ("*Flipboard*",             "Flipboard",
     "Pre-installed RSS-style news reader. Hardly anyone uses it.",       "OEM / 3rd-party"),

    ("*Twitter*",               "Twitter / X (Store)",
     "Pre-installed Twitter/X UWP app. The website works fine in the "
     "browser if you use it.",                                            "OEM / 3rd-party"),

    ("*Facebook*",              "Facebook (Store)",
     "Pre-installed Facebook UWP app.",                                   "OEM / 3rd-party"),

    ("*Spotify*",               "Spotify (Store edition)",
     "Promo install. If you actually use Spotify, grab the proper desktop "
     "installer afterwards — it’s nicer.",                                "OEM / 3rd-party"),

    ("*Netflix*",               "Netflix",
     "Promo install. The website + browser PiP is just as good.",         "OEM / 3rd-party"),

    ("*Disney*",                "Disney+",
     "Promo install. Same story — works fine in any browser.",            "OEM / 3rd-party"),

    ("*TikTok*",                "TikTok",
     "Pre-installed TikTok UWP. Privacy hawks usually remove this immediately.",
                                                                          "OEM / 3rd-party"),

    ("*LinkedIn*",              "LinkedIn",
     "Pre-installed LinkedIn UWP app.",                                   "OEM / 3rd-party"),

    ("*Instagram*",             "Instagram",
     "Pre-installed Instagram UWP app.",                                  "OEM / 3rd-party"),
]

# Defaults we recommend turning on for the "Recommended" preset
_RECOMMENDED = {
    "Microsoft.BingNews", "Microsoft.BingSearch", "Microsoft.MicrosoftOfficeHub",
    "Microsoft.MicrosoftSolitaireCollection", "Microsoft.MixedReality.Portal",
    "Microsoft.Microsoft3DViewer", "Microsoft.MSPaint", "Microsoft.OneConnect",
    "Microsoft.Print3D", "Microsoft.SkypeApp", "Microsoft.WindowsFeedbackHub",
    "Microsoft.WindowsMaps", "Microsoft.YourPhone", "Microsoft.ZuneMusic",
    "Microsoft.ZuneVideo", "Microsoft.GetHelp", "Microsoft.Getstarted",
    "Microsoft.MicrosoftFamilySafety", "Microsoft.NetworkSpeedTest",
    "Microsoft.Wallet", "Clipchamp.Clipchamp", "Microsoft.OutlookForWindows",
    "*CandyCrush*", "*BubbleWitch3Saga*", "*Duolingo-LearnLanguagesForFree*",
    "*PandoraMediaInc*", "*Flipboard*", "*Twitter*", "*Facebook*",
    "*TikTok*", "*LinkedIn*", "*Instagram*", "*Netflix*", "*Disney*",
    "*Wunderlist*", "*EclipseManager*", "*ActiproSoftwareLLC*",
    "Microsoft.XboxApp",
}


def _ps_remove(pkg: str) -> str:
    """Build the PowerShell one-liner that removes the AppX for everyone and
    de-provisions it from new accounts."""
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
            description=f"{desc}  ·  Package id: {pkg}",
            command=_ps_remove(pkg),
            shell="powershell",
            category=cat,
            danger=True,
            enabled_by_default=(pkg in _RECOMMENDED),
        ))
    return actions

"""Curated apps to install via winget — with friendly descriptions."""
from __future__ import annotations

from ..tabs._models import Action


# (winget id, friendly name, plain-English description, category)
APPS = [
    # ── Browsers ────────────────────────────────────────────────────────────
    ("Mozilla.Firefox",          "Mozilla Firefox",
     "Independent, open-source browser. Strong privacy defaults, the only "
     "major non-Chromium engine left.",                                   "Browsers"),

    ("Brave.Brave",              "Brave Browser",
     "Chromium-based browser with a built-in ad and tracker blocker. "
     "Crypto wallet built-in (can be ignored).",                          "Browsers"),

    ("Google.Chrome",            "Google Chrome",
     "Google’s flagship browser. Best web compatibility, heaviest "
     "telemetry — pick the right trade-off for you.",                     "Browsers"),

    ("Microsoft.Edge",           "Microsoft Edge",
     "Chromium-based Edge. Already on the system, but this re-installs "
     "the latest version if yours got mangled.",                          "Browsers"),

    ("LibreWolf.LibreWolf",      "LibreWolf",
     "Firefox fork with all telemetry stripped out and security settings "
     "cranked up.",                                                       "Browsers"),

    ("Vivaldi.Vivaldi",          "Vivaldi",
     "Power-user Chromium browser from the original Opera team. Vertical "
     "tabs, tiling, mouse gestures out of the box.",                      "Browsers"),

    # ── Development ─────────────────────────────────────────────────────────
    ("Microsoft.VisualStudioCode","Visual Studio Code",
     "Microsoft’s free code editor — the industry default. Massive "
     "extension ecosystem.",                                              "Dev"),

    ("Microsoft.VisualStudio.2022.Community", "Visual Studio 2022 Community",
     "Full Microsoft IDE for C#, C++, .NET, Unity. Free for personal use. "
     "Large install (~10 GB).",                                           "Dev"),

    ("JetBrains.Toolbox",        "JetBrains Toolbox",
     "Manager for JetBrains IDEs (IntelliJ, PyCharm, WebStorm, Rider…). "
     "Lets you install / update them with one click.",                    "Dev"),

    ("Git.Git",                  "Git",
     "The git command-line client. Required for almost any modern dev "
     "workflow.",                                                         "Dev"),

    ("GitHub.cli",               "GitHub CLI (gh)",
     "Official GitHub command-line tool. Create PRs, view issues, run "
     "Actions from the terminal.",                                        "Dev"),

    ("Python.Python.3.12",       "Python 3.12",
     "Latest stable Python interpreter + pip. Includes the py.exe "
     "launcher.",                                                         "Dev"),

    ("OpenJS.NodeJS.LTS",        "Node.js LTS",
     "JavaScript runtime + npm. The LTS channel is the safe choice for "
     "most projects.",                                                    "Dev"),

    ("Docker.DockerDesktop",     "Docker Desktop",
     "Run Linux containers on Windows via WSL2. Free for personal / small "
     "business use.",                                                     "Dev"),

    ("astral-sh.uv",             "uv (Python package manager)",
     "Astral’s blazing-fast pip/venv replacement written in Rust.",       "Dev"),

    ("Postman.Postman",          "Postman",
     "GUI HTTP / API testing client. Free tier is plenty for solo work.", "Dev"),

    # ── Shells / terminals ──────────────────────────────────────────────────
    ("Microsoft.WindowsTerminal","Windows Terminal",
     "Microsoft’s modern multi-tab terminal — the new default in W11. "
     "Re-install if you removed it during debloat and changed your mind.",
                                                                          "Shell"),

    ("Microsoft.PowerShell",     "PowerShell 7",
     "The cross-platform successor to Windows PowerShell 5.1. Coexists "
     "with the built-in one.",                                            "Shell"),

    ("Starship.Starship",        "Starship prompt",
     "Slick, fast cross-shell prompt. Drop one line into your PowerShell "
     "profile to enable.",                                                "Shell"),

    # ── Media ───────────────────────────────────────────────────────────────
    ("VideoLAN.VLC",             "VLC media player",
     "Plays literally every video / audio format ever invented. Always "
     "the right answer.",                                                 "Media"),

    ("OBSProject.OBSStudio",     "OBS Studio",
     "Free, open-source streaming and screen-recording. The standard for "
     "Twitch / YouTube creators.",                                        "Media"),

    ("Audacity.Audacity",        "Audacity",
     "Free multi-track audio editor. Good for podcasts and voice memos.", "Media"),

    ("GIMP.GIMP",                "GIMP",
     "Free Photoshop alternative for raster images.",                     "Media"),

    ("dotPDN.PaintDotNet",       "Paint.NET",
     "Image editor that fits between Paint and Photoshop — simple, fast, "
     "free.",                                                              "Media"),

    ("BlenderFoundation.Blender","Blender",
     "Free, industry-grade 3D modelling, animation, video editing, "
     "compositing.",                                                       "Media"),

    ("Spotify.Spotify",          "Spotify",
     "Music streaming desktop client. The proper installer (not the Store "
     "UWP).",                                                              "Media"),

    # ── Utilities ───────────────────────────────────────────────────────────
    ("7zip.7zip",                "7-Zip",
     "Open-source archive manager. Reads/writes 7z, zip, rar, tar.gz, "
     "iso… better than the Windows built-in.",                            "Utilities"),

    ("Microsoft.PowerToys",      "Microsoft PowerToys",
     "Microsoft’s power-user toolkit — FancyZones, PowerRename, "
     "PowerToys Run launcher, Always-On-Top, Color Picker, Text "
     "Extractor, and a dozen more. Anyone serious about Windows installs "
     "this.",                                                              "Utilities"),

    ("voidtools.Everything",     "Everything",
     "Instant filename search across every NTFS drive. ‘Find a file’ in "
     "milliseconds. Once you use it you can’t go back.",                  "Utilities"),

    ("ShareX.ShareX",            "ShareX",
     "The swiss-army knife of screenshots — region/window/scrolling "
     "capture, recording, OCR, instant upload.",                          "Utilities"),

    ("Notepad++.Notepad++",      "Notepad++",
     "Lightweight syntax-highlighting text editor. Great for editing "
     "config files when you don’t want to load VS Code.",                 "Utilities"),

    ("WinDirStat.WinDirStat",    "WinDirStat",
     "Visualises which folders/files are eating your disk. Essential "
     "before any cleanup.",                                                "Utilities"),

    ("Bitwarden.Bitwarden",      "Bitwarden",
     "Open-source password manager. Free tier syncs across all your "
     "devices.",                                                           "Utilities"),

    ("Mozilla.Thunderbird",      "Mozilla Thunderbird",
     "Free desktop email client — IMAP/POP/Exchange. Built-in calendar "
     "and address book.",                                                  "Utilities"),

    ("LibreOffice.LibreOffice",  "LibreOffice",
     "Free office suite — Writer (Word), Calc (Excel), Impress (PowerPoint). "
     "Reads/writes .docx, .xlsx, .pptx.",                                  "Utilities"),

    ("KeePassXCTeam.KeePassXC",  "KeePassXC",
     "Offline encrypted password vault — local file, no cloud. Pair with "
     "your own Dropbox/OneDrive for sync.",                                "Utilities"),

    ("Cryptomator.Cryptomator",  "Cryptomator",
     "Adds client-side encryption to any cloud folder (Dropbox, OneDrive, "
     "Drive). Zero-knowledge — only you can read it.",                     "Utilities"),

    ("HandBrake.HandBrake",      "HandBrake",
     "Open-source video transcoder. Shrink huge videos for streaming or "
     "phones.",                                                            "Utilities"),

    ("qBittorrent.qBittorrent",  "qBittorrent",
     "Clean, ad-free open-source BitTorrent client. The right answer "
     "instead of uTorrent.",                                               "Utilities"),

    # ── Comms ───────────────────────────────────────────────────────────────
    ("Discord.Discord",          "Discord",
     "Voice + text chat for gaming / communities.",                       "Comms"),

    ("OpenWhisperSystems.Signal","Signal",
     "End-to-end encrypted messenger. Open source, recommended by "
     "security pros worldwide.",                                          "Comms"),

    ("Telegram.TelegramDesktop", "Telegram",
     "Cross-device messenger with big group support.",                    "Comms"),

    ("Zoom.Zoom",                "Zoom",
     "Video conferencing client. Required for many work calls.",          "Comms"),

    # ── System / Hardware tools ─────────────────────────────────────────────
    ("CPUID.CPU-Z",              "CPU-Z",
     "Reads exact CPU/RAM/motherboard model and speeds. The reference "
     "tool for hardware ID.",                                              "System"),

    ("TechPowerUp.GPU-Z",        "GPU-Z",
     "Detailed GPU info, real-time clock/temperature/voltage sensors. "
     "Pair with HWiNFO for the full picture.",                             "System"),

    ("REALiX.HWiNFO",            "HWiNFO",
     "The most thorough hardware monitor on Windows — every sensor on "
     "your board exposed in one place. Free for personal use.",            "System"),

    ("CrystalDewWorld.CrystalDiskInfo","CrystalDiskInfo",
     "Reads disk SMART data — gives you a health verdict (‘Good’, "
     "‘Caution’, ‘Bad’) plus the raw counters. First thing to run if a "
     "drive feels slow.",                                                  "System"),

    ("CrystalDewWorld.CrystalDiskMark","CrystalDiskMark",
     "Quick sequential + random read/write benchmark. The standard way "
     "to compare SSDs.",                                                   "System"),

    ("FinalWire.AIDA64.Extreme", "AIDA64 Extreme",
     "Heavy-duty hardware reporting + benchmark suite. Paid software, "
     "but very thorough.",                                                 "System"),

    ("Rufus.Rufus",              "Rufus",
     "Creates bootable USB drives from ISOs (Windows installers, Linux, "
     "tools). Faster and more reliable than the built-in Media Creation "
     "Tool.",                                                              "System"),

    ("Belarc.BelarcAdvisor",     "Belarc Advisor",
     "Generates a detailed HTML inventory of installed software, "
     "licenses, hardware, hotfixes. Useful before a wipe.",                "System"),

    ("Microsoft.Sysinternals.ProcessExplorer", "Process Explorer",
     "Mark Russinovich’s super-Task-Manager. Shows handle trees, DLLs "
     "loaded, VirusTotal hashes, and more.",                               "System"),

    ("Microsoft.Sysinternals.Autoruns",        "Autoruns",
     "Lists EVERYTHING that auto-starts with Windows — services, "
     "scheduled tasks, shell extensions, drivers. The deep version of "
     "Task Manager’s Startup tab.",                                        "System"),
]


def build() -> list[Action]:
    out: list[Action] = []
    for wid, name, desc, cat in APPS:
        out.append(Action(
            title=f"Install {name}",
            description=f"{desc}  ·  winget id: {wid}",
            command=(f'winget install --id {wid} '
                     f'-e --accept-source-agreements --accept-package-agreements'),
            shell="cmd",
            category=cat,
            enabled_by_default=False,
        ))
    return out

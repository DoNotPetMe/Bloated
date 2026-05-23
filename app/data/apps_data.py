"""Curated apps to install via winget."""
from __future__ import annotations

from ..tabs._models import Action


# (winget id, friendly name, description, category)
APPS = [
    # Browsers
    ("Mozilla.Firefox",          "Mozilla Firefox",          "Open-source browser.",                  "Browsers"),
    ("Brave.Brave",              "Brave Browser",            "Chromium browser with built-in adblock.","Browsers"),
    ("Google.Chrome",            "Google Chrome",            "Google’s browser.",                       "Browsers"),

    # Dev
    ("Microsoft.VisualStudioCode","VS Code",                 "Microsoft’s code editor.",                "Dev"),
    ("Git.Git",                  "Git",                      "Git VCS.",                                "Dev"),
    ("GitHub.cli",               "GitHub CLI (gh)",          "Command-line GitHub client.",             "Dev"),
    ("Python.Python.3.12",       "Python 3.12",              "Python interpreter + pip.",               "Dev"),
    ("OpenJS.NodeJS.LTS",        "Node.js LTS",              "JavaScript runtime + npm.",               "Dev"),
    ("Docker.DockerDesktop",     "Docker Desktop",           "Containers on Windows.",                  "Dev"),

    # Terminals / shells
    ("Microsoft.WindowsTerminal","Windows Terminal",         "Modern multi-tab terminal.",              "Shell"),
    ("Microsoft.PowerShell",     "PowerShell 7",             "Cross-platform PowerShell.",              "Shell"),

    # Media
    ("VideoLAN.VLC",             "VLC media player",         "Plays everything.",                       "Media"),
    ("OBSProject.OBSStudio",     "OBS Studio",               "Stream / screen-record.",                 "Media"),
    ("Spotify.Spotify",          "Spotify",                  "Music streaming.",                        "Media"),

    # Utilities
    ("7zip.7zip",                "7-Zip",                    "Archive tool.",                           "Utilities"),
    ("Microsoft.PowerToys",      "PowerToys",                "Microsoft’s power-user toolkit.",         "Utilities"),
    ("voidtools.Everything",     "Everything",               "Instant filename search.",                "Utilities"),
    ("ShareX.ShareX",            "ShareX",                   "Screenshot + screen recording.",          "Utilities"),
    ("Notepad++.Notepad++",      "Notepad++",                "Lightweight text editor.",                "Utilities"),
    ("WinDirStat.WinDirStat",    "WinDirStat",               "Visual disk usage analyser.",             "Utilities"),
    ("Bitwarden.Bitwarden",      "Bitwarden",                "Open-source password manager.",           "Utilities"),

    # Comms
    ("Discord.Discord",          "Discord",                  "Voice / text chat.",                      "Comms"),
    ("OpenWhisperSystems.Signal","Signal",                   "End-to-end encrypted messenger.",         "Comms"),

    # Drivers / system
    ("CPUID.CPU-Z",              "CPU-Z",                    "Hardware ID utility.",                    "System"),
    ("TechPowerUp.GPU-Z",        "GPU-Z",                    "GPU info & sensors.",                     "System"),
    ("CrystalDewWorld.CrystalDiskInfo","CrystalDiskInfo",    "Disk SMART health.",                      "System"),
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

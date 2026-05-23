# Bloated — Windows PC Powerhouse

A modern, native-feeling Windows desktop application written in **Python + CustomTkinter** that turns dozens of arcane PowerShell, registry, and WMI incantations into a single, well-explained, click-driven control center.

Every action ships with a plain-English explanation of *what* it does, *why* you might want it, and the exact command(s) that will be executed against your system — so nothing happens behind your back.

## Highlights

- **Debloater** — uninstall stock UWP apps (Cortana, Xbox, Bing Weather, Copilot, OneDrive, Edge widgets…), per-checkbox with descriptions. Works on fresh installs *and* existing systems.
- **Privacy Hardener** — disable telemetry, advertising ID, activity history, suggested content, location tracking, Recall/Copilot data collection.
- **Performance** — power plans (incl. Ultimate Performance), visual effects tuning, GameMode, hardware-accelerated GPU scheduling, prefetcher controls.
- **Services Manager** — stop & disable known offender services (Connected User Experiences, Diagnostic Tracking, Retail Demo, etc.) with one-click revert.
- **Registry Tweaks** — show seconds in clock, classic context menu (Win11), end task in taskbar, dark mode, taskbar alignment, verbose status, etc.
- **Cleanup** — temp files, prefetch, Windows.old, update cache, recycle bin, DNS cache, event logs, thumbnail cache — with byte-size preview.
- **Network** — flush DNS, reset Winsock, set Cloudflare/Google/Quad9 DNS, TCP auto-tuning, MTU helpers, latency ping panel.
- **Updates** — pause Windows Update for N days, set metered, disable driver auto-install, defer feature updates.
- **App Installer** — bulk install curated apps via `winget` (browsers, dev tools, media, utilities) — checkbox + install all.
- **Custom Commands** — your own library of saved CMD / PowerShell one-liners with descriptions, tags, and a single-click run with live output.
- **System Info** — CPU, GPU, RAM, disks, motherboard, BIOS, network adapters, installed updates, drivers.
- **Safety** — every destructive action confirms first, creates a System Restore Point on request, and logs every command + result to a rotating file.

## Quick start

```cmd
git clone https://github.com/DoNotPetMe/Bloated.git
cd Bloated
install.bat
run.bat
```

Or manually:

```cmd
python -m pip install -r requirements.txt
python main.py
```

> **Run as Administrator** for tweaks/services/registry to apply system-wide. The app detects elevation and warns you.

## Requirements

- Windows 10 (1809+) or Windows 11
- Python 3.10+ (3.12 recommended)
- ~30 MB disk

## Project layout

```
Bloated/
├── main.py                  # entry point
├── requirements.txt
├── install.bat / run.bat
├── app/
│   ├── main_window.py       # shell + sidebar router
│   ├── theme.py             # palette + ctk setup
│   ├── utils/
│   │   ├── admin.py         # UAC / elevation
│   │   ├── runner.py        # subprocess wrapper (cmd + ps)
│   │   ├── registry.py      # safe reg read/write helpers
│   │   ├── restore_point.py # System Restore creator
│   │   └── logger.py
│   ├── tabs/
│   │   ├── dashboard.py
│   │   ├── debloat.py
│   │   ├── privacy.py
│   │   ├── performance.py
│   │   ├── services.py
│   │   ├── tweaks.py
│   │   ├── cleanup.py
│   │   ├── network.py
│   │   ├── updates.py
│   │   ├── apps.py
│   │   ├── commands.py
│   │   └── system_info.py
│   └── data/
│       ├── bloatware_apps.py
│       ├── services_data.py
│       ├── tweaks_data.py
│       ├── privacy_data.py
│       ├── apps_data.py
│       └── commands_data.py
```

## Safety notes

Most actions in this app reach into the registry, services, or scheduled tasks. They are **reversible** but, like any system tool, please:

1. Create a System Restore Point first (**Dashboard → Create Restore Point**).
2. Read each action's description — they are written in plain English.
3. Reboot after major changes.

## License

MIT.

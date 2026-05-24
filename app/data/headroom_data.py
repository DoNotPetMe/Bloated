"""Headroom checks — read-only diagnostics that flag whether the PC is
silently held back by a setting or a missing tweak.

Each check is a function that takes a fresh HardwareProfile and returns a
``CheckResult``. The Headroom tab calls them in order and prints the
results to the terminal-style console.

A check is INTENTIONALLY non-destructive: it only reads system state. The
follow-up fix (if any) is described in the ``hint`` text, with a pointer to
which other tab in Bloated already has the action.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable

from ..utils.hardware import HardwareProfile
from ..utils.runner import run_cmd, run_powershell


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------

OK   = "ok"
WARN = "warn"
FAIL = "err"      # uses the console 'err' tag
INFO = "info"


@dataclass
class CheckResult:
    name: str
    status: str            # OK / WARN / FAIL / INFO
    message: str           # short result, one sentence
    hint: str = ""         # what to do about it (optional)


CheckFn = Callable[[HardwareProfile], CheckResult]


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_power_plan(p: HardwareProfile) -> CheckResult:
    r = run_cmd("powercfg /getactivescheme", timeout=10)
    text = r.text.lower()
    if "power saver" in text:
        return CheckResult(
            "Active power plan", WARN,
            "currently on POWER SAVER — CPU is being capped",
            "Performance tab → ‘Switch to High Performance’ or ‘Ultimate Performance’.")
    if "ultimate" in text:
        return CheckResult("Active power plan", OK,
                           "Ultimate Performance — no CPU caps")
    if "high performance" in text:
        return CheckResult("Active power plan", OK,
                           "High Performance — no CPU caps")
    return CheckResult("Active power plan", INFO,
                       "Balanced (default) — fine for most users, swap to High "
                       "Performance for gaming if you don’t care about wattage")


def _check_processor_state(p: HardwareProfile) -> CheckResult:
    r = run_cmd("powercfg /q SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX",
                timeout=10)
    m = re.search(r"Current AC Power Setting Index:\s*0x([0-9A-Fa-f]+)", r.text)
    if not m:
        return CheckResult("Max processor state (AC)", INFO,
                           "could not read setting")
    pct = int(m.group(1), 16)
    if pct >= 100:
        return CheckResult("Max processor state (AC)", OK,
                           f"{pct}% — CPU can boost freely")
    return CheckResult(
        "Max processor state (AC)", WARN,
        f"capped at {pct}% — CPU will never use full boost",
        "powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR "
        "bc5038f7-23e0-4960-96da-33abaf5935ec 100")


def _check_ram_xmp(p: HardwareProfile) -> CheckResult:
    if not (p.ram_configured_mhz and p.ram_max_mhz):
        return CheckResult("RAM at rated speed (XMP/EXPO)", INFO,
                           "could not read SPD speed")
    diff = p.ram_max_mhz - p.ram_configured_mhz
    if diff <= 50:
        return CheckResult(
            "RAM at rated speed (XMP/EXPO)", OK,
            f"running at {p.ram_configured_mhz} MT/s — matches SPD")
    return CheckResult(
        "RAM at rated speed (XMP/EXPO)", WARN,
        f"running at {p.ram_configured_mhz} MT/s but sticks rated for "
        f"{p.ram_max_mhz} MT/s",
        "Enable XMP (Intel) or EXPO (AMD) in BIOS — single biggest free "
        "performance win on modern PCs.")


def _check_ram_channels(p: HardwareProfile) -> CheckResult:
    if p.ram_sticks <= 0:
        return CheckResult("Memory channels", INFO, "could not read stick count")
    if p.ram_sticks == 1:
        return CheckResult(
            "Memory channels", WARN,
            "only 1 stick installed — single-channel halves memory bandwidth",
            "Add an identical stick in the matching slot (usually A2+B2 / "
            "DIMM 2+4) for dual-channel.")
    return CheckResult("Memory channels", OK,
                       f"{p.ram_sticks} sticks installed — dual-channel likely")


def _check_trim(p: HardwareProfile) -> CheckResult:
    r = run_cmd("fsutil behavior query DisableDeleteNotify", timeout=10)
    if "DisableDeleteNotify = 0" in r.text or "NTFS DisableDeleteNotify = 0" in r.text:
        return CheckResult("TRIM enabled", OK, "TRIM is on for NTFS volumes")
    if "DisableDeleteNotify = 1" in r.text:
        return CheckResult(
            "TRIM enabled", WARN,
            "TRIM is OFF — SSD writes will get slower over time",
            "`fsutil behavior set DisableDeleteNotify 0`")
    return CheckResult("TRIM enabled", INFO, "could not read TRIM state")


def _check_storage_health(p: HardwareProfile) -> CheckResult:
    r = run_powershell(
        "Get-PhysicalDisk | Select-Object FriendlyName, HealthStatus "
        "| ConvertTo-Json -Compress",
        timeout=15)
    import json
    try:
        data = json.loads(r.stdout) if r.ok else None
    except Exception:
        data = None
    if data is None:
        return CheckResult("Storage SMART health", INFO,
                           "could not read SMART status")
    if isinstance(data, dict):
        data = [data]
    bad = [d for d in data if str(d.get("HealthStatus", "")).lower() != "healthy"]
    if bad:
        names = ", ".join(str(d.get("FriendlyName")) for d in bad)
        return CheckResult(
            "Storage SMART health", FAIL,
            f"unhealthy disk(s): {names}",
            "Back up before it dies. Run CrystalDiskInfo for full attributes.")
    return CheckResult(
        "Storage SMART health", OK,
        f"all {len(data)} drive(s) reported as Healthy")


def _check_hags(p: HardwareProfile) -> CheckResult:
    r = run_cmd(
        'reg query "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers"'
        ' /v HwSchMode', timeout=10)
    if "0x2" in r.text:
        return CheckResult("Hardware-Accelerated GPU Scheduling", OK,
                           "HAGS is ENABLED")
    if "0x1" in r.text:
        return CheckResult(
            "Hardware-Accelerated GPU Scheduling", INFO,
            "HAGS is disabled — may help or hurt depending on driver/game",
            "Performance tab → ‘Enable HAGS’ to test.")
    return CheckResult("Hardware-Accelerated GPU Scheduling", INFO,
                       "could not read HwSchMode (older Windows build?)")


def _check_fast_startup(p: HardwareProfile) -> CheckResult:
    r = run_cmd(
        'reg query "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power"'
        ' /v HiberbootEnabled', timeout=10)
    if "0x0" in r.text:
        return CheckResult("Fast Startup", OK, "disabled — clean boot every time")
    if "0x1" in r.text:
        return CheckResult(
            "Fast Startup", WARN,
            "ENABLED — partial-hibernate boot can cause driver weirdness",
            "Performance tab → ‘Disable Fast Startup’.")
    return CheckResult("Fast Startup", INFO, "could not read state")


def _check_gpu_driver_age(p: HardwareProfile) -> CheckResult:
    if not p.gpu_driver_date:
        return CheckResult("GPU driver age", INFO, "driver date not available")
    try:
        d = datetime.strptime(p.gpu_driver_date, "%Y-%m-%d")
    except Exception:
        return CheckResult("GPU driver age", INFO, "could not parse driver date")
    age = datetime.now() - d
    months = age.days / 30
    if age > timedelta(days=365):
        return CheckResult(
            "GPU driver age", WARN,
            f"driver is {months:.0f} months old ({p.gpu_driver_date})",
            f"Grab the latest from {p.gpu_vendor}'s website / app.")
    if age > timedelta(days=180):
        return CheckResult(
            "GPU driver age", INFO,
            f"driver is {months:.0f} months old — check for newer once a quarter")
    return CheckResult("GPU driver age", OK,
                       f"driver from {p.gpu_driver_date} — recent")


def _check_bios_age(p: HardwareProfile) -> CheckResult:
    if not p.bios_date:
        return CheckResult("BIOS age", INFO, "BIOS date not available")
    try:
        d = datetime.strptime(p.bios_date, "%Y-%m-%d")
    except Exception:
        return CheckResult("BIOS age", INFO, "could not parse BIOS date")
    age_years = (datetime.now() - d).days / 365
    if age_years > 3:
        return CheckResult(
            "BIOS age", INFO,
            f"BIOS is ~{age_years:.1f} years old (released {p.bios_date})",
            "Check your motherboard vendor’s site — newer BIOS can fix RAM "
            "stability and CPU boost behaviour.")
    if age_years > 1.5:
        return CheckResult("BIOS age", INFO,
                           f"BIOS is ~{age_years:.1f} years old — fine for most use")
    return CheckResult("BIOS age", OK,
                       f"BIOS recent (released {p.bios_date})")


def _check_monitor_refresh(p: HardwareProfile) -> CheckResult:
    if not p.monitor_refresh_hz:
        return CheckResult("Display refresh rate", INFO,
                           "refresh rate not reported")
    if p.monitor_refresh_hz <= 60:
        return CheckResult(
            "Display refresh rate", INFO,
            f"running at {p.monitor_refresh_hz} Hz — if your monitor is "
            "higher-refresh, set it in Settings → Display → Advanced.")
    return CheckResult(
        "Display refresh rate", OK,
        f"running at {p.monitor_refresh_hz} Hz")


def _check_nic_link(p: HardwareProfile) -> CheckResult:
    if not p.nic_link_mbps:
        return CheckResult("Network link speed", INFO, "link speed unknown")
    if p.nic_type == "Ethernet":
        if p.nic_link_mbps < 1000:
            return CheckResult(
                "Network link speed", WARN,
                f"Ethernet at {p.nic_link_mbps} Mbps — check cable category "
                "(Cat5e+) and switch port",
                "Bad cable or 100 Mbps switch port halves your throughput.")
        return CheckResult(
            "Network link speed", OK,
            f"Ethernet at {p.nic_link_mbps} Mbps — looks normal")
    if p.nic_type == "Wi-Fi":
        if p.nic_link_mbps < 300:
            return CheckResult(
                "Wi-Fi link speed", WARN,
                f"only {p.nic_link_mbps} Mbps — probably on 2.4 GHz or far "
                "from the AP",
                "Switch to the 5 GHz/6 GHz network if available.")
        return CheckResult("Wi-Fi link speed", OK,
                           f"{p.nic_link_mbps} Mbps — looks healthy")
    return CheckResult("Network link speed", INFO,
                       f"{p.nic_link_mbps} Mbps")


def _check_pagefile(p: HardwareProfile) -> CheckResult:
    r = run_powershell(
        "Get-CimInstance Win32_PageFileUsage | "
        "Select-Object Name,CurrentUsage,PeakUsage,AllocatedBaseSize | "
        "ConvertTo-Json -Compress",
        timeout=10)
    import json
    try:
        data = json.loads(r.stdout) if r.ok else None
    except Exception:
        data = None
    if not data:
        return CheckResult("Pagefile", INFO, "no active pagefile detected")
    if isinstance(data, dict): data = [data]
    return CheckResult(
        "Pagefile", OK,
        ", ".join(f"{d.get('Name')}: {d.get('AllocatedBaseSize')} MB allocated"
                  for d in data))


def _check_telemetry_service(p: HardwareProfile) -> CheckResult:
    r = run_cmd("sc query DiagTrack", timeout=10)
    if "STOPPED" in r.text:
        return CheckResult("Telemetry (DiagTrack) service", OK,
                           "stopped — no diagnostic uploads")
    if "RUNNING" in r.text:
        return CheckResult(
            "Telemetry (DiagTrack) service", INFO,
            "running — sending diagnostic data to Microsoft",
            "Privacy tab → ‘Disable Telemetry (DiagTrack)’.")
    return CheckResult("Telemetry (DiagTrack) service", INFO,
                       "could not read state")


# ---------------------------------------------------------------------------
# Public list of checks
# ---------------------------------------------------------------------------


CHECKS: list[tuple[str, CheckFn]] = [
    ("Power",     _check_power_plan),
    ("Power",     _check_processor_state),
    ("Memory",    _check_ram_xmp),
    ("Memory",    _check_ram_channels),
    ("Storage",   _check_trim),
    ("Storage",   _check_storage_health),
    ("GPU",       _check_hags),
    ("GPU",       _check_gpu_driver_age),
    ("System",    _check_fast_startup),
    ("System",    _check_bios_age),
    ("System",    _check_pagefile),
    ("System",    _check_telemetry_service),
    ("Display",   _check_monitor_refresh),
    ("Network",   _check_nic_link),
]

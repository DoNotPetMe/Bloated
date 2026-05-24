"""Hardware detection — shared by the Game Tune and Headroom tabs.

We run a handful of small PowerShell / WMI / powercfg queries, parse the
results into a structured :class:`HardwareProfile`, and cache the result
process-wide. Every field has a safe default so the UI keeps working when
a query fails or we’re running on a non-Windows host (e.g. during dev).
"""
from __future__ import annotations

import json
import re
import threading
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

from .admin import is_windows
from .logger import get_logger
from .runner import run_cmd, run_powershell

log = get_logger("hardware")


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------


@dataclass
class HardwareProfile:
    # CPU
    cpu_vendor: str = "Unknown"          # "Intel" / "AMD" / "ARM"
    cpu_name: str = "Unknown CPU"
    cpu_cores: int = 0
    cpu_threads: int = 0
    cpu_max_mhz: int = 0
    cpu_hybrid: bool = False             # Intel 12th-gen+ with P + E cores

    # GPU (primary discrete if any, else first listed)
    gpu_vendor: str = "Unknown"          # "NVIDIA" / "AMD" / "Intel"
    gpu_name: str = "Unknown GPU"
    gpu_vram_gb: float = 0.0
    gpu_driver_date: str = ""            # YYYY-MM-DD

    # Memory
    ram_total_gb: float = 0.0
    ram_configured_mhz: int = 0          # current MT/s reported by WMI
    ram_max_mhz: int = 0                 # rated MT/s from SPD
    ram_sticks: int = 0

    # Storage (primary / boot)
    storage_primary_model: str = ""
    storage_primary_media: str = "Unknown"   # "SSD", "HDD"
    storage_primary_bus: str = ""            # "NVMe", "SATA", "USB"…

    # Display (primary)
    monitor_width: int = 0
    monitor_height: int = 0
    monitor_refresh_hz: int = 0

    # Network (best active adapter)
    nic_type: str = "Unknown"            # "Ethernet" / "Wi-Fi"
    nic_link_mbps: int = 0
    wifi_band: str = ""                  # "2.4 GHz" / "5 GHz" / "6 GHz"
    wifi_standard: str = ""              # "802.11ax", etc.

    # Firmware / OS
    bios_date: str = ""                  # YYYY-MM-DD
    os_caption: str = ""
    os_build: str = ""

    # Form factor
    is_laptop: bool = False              # detected by presence of a battery

    # Detection diagnostics
    errors: list[str] = field(default_factory=list)

    # ---- Convenience helpers ----------------------------------------------

    @property
    def cpu_summary(self) -> str:
        bits = [self.cpu_name]
        if self.cpu_cores and self.cpu_threads:
            bits.append(f"{self.cpu_cores}C/{self.cpu_threads}T")
        if self.cpu_hybrid:
            bits.append("hybrid P+E")
        return " · ".join(bits)

    @property
    def gpu_summary(self) -> str:
        parts = [self.gpu_name]
        if self.gpu_vram_gb:
            parts.append(f"{self.gpu_vram_gb:.0f} GB")
        if self.gpu_driver_date:
            parts.append(f"drv {self.gpu_driver_date}")
        return " · ".join(parts)

    @property
    def ram_summary(self) -> str:
        parts = []
        if self.ram_total_gb:
            parts.append(f"{self.ram_total_gb:.0f} GB")
        if self.ram_configured_mhz:
            if self.ram_max_mhz and self.ram_max_mhz != self.ram_configured_mhz:
                parts.append(f"{self.ram_configured_mhz} / {self.ram_max_mhz} MT/s")
            else:
                parts.append(f"{self.ram_configured_mhz} MT/s")
        if self.ram_sticks:
            chan = "dual-ch" if self.ram_sticks >= 2 else "single-ch"
            parts.append(f"{self.ram_sticks} sticks · {chan}")
        return " · ".join(parts) or "—"

    @property
    def storage_summary(self) -> str:
        parts = [self.storage_primary_model or "—"]
        if self.storage_primary_bus and self.storage_primary_media:
            parts.append(f"{self.storage_primary_bus} {self.storage_primary_media}")
        return " · ".join(parts)

    @property
    def display_summary(self) -> str:
        if not self.monitor_refresh_hz:
            return "—"
        return f"{self.monitor_width}×{self.monitor_height} @ {self.monitor_refresh_hz} Hz"

    @property
    def network_summary(self) -> str:
        parts = [self.nic_type]
        if self.nic_link_mbps:
            parts.append(f"{self.nic_link_mbps} Mbps")
        if self.wifi_standard:
            parts.append(self.wifi_standard)
        if self.wifi_band:
            parts.append(self.wifi_band)
        return " · ".join(p for p in parts if p) or "—"

    def as_lines(self) -> list[tuple[str, str]]:
        """Pretty key→value pairs for the Game Tune profile card."""
        return [
            ("CPU",     self.cpu_summary),
            ("GPU",     self.gpu_summary),
            ("RAM",     self.ram_summary),
            ("STORAGE", self.storage_summary),
            ("DISPLAY", self.display_summary),
            ("NETWORK", self.network_summary),
            ("OS",      f"{self.os_caption} · build {self.os_build}" if self.os_build else self.os_caption),
            ("FORM",    "Laptop" if self.is_laptop else "Desktop"),
        ]


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


_cache: Optional[HardwareProfile] = None
_cache_lock = threading.Lock()


def _ps_json(script: str, timeout: int = 30) -> Any:
    """Run a PowerShell command whose output ends with `| ConvertTo-Json`
    and return the parsed JSON, or None on any failure."""
    if not is_windows():
        return None
    full = script.rstrip().rstrip(";")
    if "ConvertTo-Json" not in full:
        full = f"{full} | ConvertTo-Json -Depth 4 -Compress"
    r = run_powershell(full, timeout=timeout)
    if not r.ok or not r.stdout:
        log.debug("ps_json failed: rc=%s err=%s", r.returncode, r.stderr[:120])
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        log.debug("ps_json non-JSON output: %s", r.stdout[:120])
        return None


_INTEL_HYBRID_RE = re.compile(
    r"(?i)(core\s+ultra|i[3-9]-1[2-9]\d{3}|i[3-9]-2\d{4})"
)


def _detect_cpu(p: HardwareProfile) -> None:
    data = _ps_json(
        "Get-CimInstance Win32_Processor | Select-Object "
        "Name,Manufacturer,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed"
    )
    if isinstance(data, list):
        data = data[0] if data else None
    if not isinstance(data, dict):
        p.errors.append("cpu: query failed")
        return
    name = str(data.get("Name") or "").strip()
    mfr  = str(data.get("Manufacturer") or "").strip()
    p.cpu_name    = name or p.cpu_name
    p.cpu_cores   = int(data.get("NumberOfCores") or 0)
    p.cpu_threads = int(data.get("NumberOfLogicalProcessors") or 0)
    p.cpu_max_mhz = int(data.get("MaxClockSpeed") or 0)
    if "intel" in mfr.lower() or "intel" in name.lower():
        p.cpu_vendor = "Intel"
    elif "amd" in mfr.lower() or "amd" in name.lower() or "ryzen" in name.lower():
        p.cpu_vendor = "AMD"
    elif "arm" in mfr.lower() or "snapdragon" in name.lower():
        p.cpu_vendor = "ARM"
    if p.cpu_vendor == "Intel" and _INTEL_HYBRID_RE.search(name):
        p.cpu_hybrid = True


def _detect_gpu(p: HardwareProfile) -> None:
    data = _ps_json(
        "Get-CimInstance Win32_VideoController | Select-Object "
        "Name,AdapterRAM,DriverDate,DriverVersion"
    )
    if isinstance(data, dict):
        data = [data]
    if not data:
        p.errors.append("gpu: query failed")
        return

    def _score(d: dict) -> int:
        name = str(d.get("Name") or "").lower()
        if "nvidia" in name or "geforce" in name or "rtx" in name or "quadro" in name:
            return 3
        if "radeon" in name or "amd" in name:
            return 2
        if "intel" in name or "uhd" in name or "iris" in name:
            return 1
        return 0

    best = max(data, key=_score)
    name = str(best.get("Name") or "").strip()
    p.gpu_name = name or p.gpu_name
    n = name.lower()
    if "nvidia" in n or "geforce" in n or "rtx" in n or "quadro" in n:
        p.gpu_vendor = "NVIDIA"
    elif "radeon" in n or "amd" in n:
        p.gpu_vendor = "AMD"
    elif "intel" in n or "uhd" in n or "iris" in n or "arc" in n:
        p.gpu_vendor = "Intel"
    try:
        # AdapterRAM under-reports >4 GB on 32-bit fields; use as a floor.
        p.gpu_vram_gb = int(best.get("AdapterRAM") or 0) / (1024 ** 3)
    except Exception:
        pass

    raw_date = str(best.get("DriverDate") or "")
    m = re.search(r"(\d{4})(\d{2})(\d{2})", raw_date)
    if m:
        p.gpu_driver_date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"


def _detect_ram(p: HardwareProfile) -> None:
    data = _ps_json(
        "Get-CimInstance Win32_PhysicalMemory | Select-Object "
        "Capacity,Speed,ConfiguredClockSpeed,DeviceLocator"
    )
    if isinstance(data, dict):
        data = [data]
    if not data:
        p.errors.append("ram: query failed")
        return
    total_bytes = 0
    speeds: list[int] = []
    configs: list[int] = []
    for stick in data:
        try:
            total_bytes += int(stick.get("Capacity") or 0)
        except Exception:
            pass
        try:
            s = int(stick.get("Speed") or 0)
            if s: speeds.append(s)
        except Exception:
            pass
        try:
            c = int(stick.get("ConfiguredClockSpeed") or 0)
            if c: configs.append(c)
        except Exception:
            pass
    p.ram_total_gb = total_bytes / (1024 ** 3)
    p.ram_sticks   = len(data)
    if configs:
        p.ram_configured_mhz = max(configs)
    if speeds:
        p.ram_max_mhz = max(speeds)


def _detect_storage(p: HardwareProfile) -> None:
    data = _ps_json(
        "Get-PhysicalDisk | Select-Object "
        "FriendlyName,MediaType,BusType,Size,DeviceId,HealthStatus"
    )
    if isinstance(data, dict):
        data = [data]
    if not data:
        return
    # Heuristic: boot disk is usually the smallest fixed disk, or first NVMe.
    # We prefer one whose BusType is NVMe; else the first.
    nvmes = [d for d in data if str(d.get("BusType") or "").lower() == "nvme"]
    chosen = nvmes[0] if nvmes else data[0]
    p.storage_primary_model = str(chosen.get("FriendlyName") or "").strip()
    media_raw = str(chosen.get("MediaType") or "").lower()
    if "ssd" in media_raw:
        p.storage_primary_media = "SSD"
    elif "hdd" in media_raw:
        p.storage_primary_media = "HDD"
    else:
        # MediaType is sometimes a numeric code: 3=HDD, 4=SSD, 5=SCM
        try:
            n = int(chosen.get("MediaType"))
            p.storage_primary_media = {3: "HDD", 4: "SSD", 5: "SCM"}.get(n, "Unknown")
        except Exception:
            pass
    bus = str(chosen.get("BusType") or "").strip()
    p.storage_primary_bus = bus


def _detect_display(p: HardwareProfile) -> None:
    data = _ps_json(
        "Get-CimInstance Win32_VideoController | Select-Object "
        "CurrentHorizontalResolution,CurrentVerticalResolution,CurrentRefreshRate"
    )
    if isinstance(data, dict):
        data = [data]
    if not data:
        return
    # Pick the display with the highest refresh rate.
    best = max(
        data,
        key=lambda d: int(d.get("CurrentRefreshRate") or 0)
    )
    p.monitor_width      = int(best.get("CurrentHorizontalResolution") or 0)
    p.monitor_height     = int(best.get("CurrentVerticalResolution")   or 0)
    p.monitor_refresh_hz = int(best.get("CurrentRefreshRate")          or 0)


def _detect_network(p: HardwareProfile) -> None:
    data = _ps_json(
        "Get-NetAdapter -Physical "
        "| Where-Object Status -eq 'Up' "
        "| Select-Object Name,InterfaceDescription,LinkSpeed,MediaType,PhysicalMediaType"
    )
    if isinstance(data, dict):
        data = [data]
    if not data:
        return

    def _mbps(s: str) -> int:
        if not s: return 0
        m = re.match(r"\s*([\d.]+)\s*(G|M|K)?bps", str(s))
        if not m: return 0
        val = float(m.group(1)); unit = (m.group(2) or "").upper()
        if unit == "G": return int(val * 1000)
        if unit == "M": return int(val)
        if unit == "K": return int(val / 1000)
        return int(val)

    # Prefer Ethernet > Wi-Fi by score then by link speed.
    def _score(d: dict) -> tuple:
        desc = str(d.get("InterfaceDescription") or "").lower()
        kind = 0
        if "ethernet" in desc or "gigabit" in desc:
            kind = 2
        elif any(k in desc for k in ("wireless", "wi-fi", "wifi", "ax", "802.11")):
            kind = 1
        return (kind, _mbps(d.get("LinkSpeed", "")))

    best = max(data, key=_score)
    desc = str(best.get("InterfaceDescription") or "").lower()
    p.nic_link_mbps = _mbps(best.get("LinkSpeed", ""))
    if any(k in desc for k in ("wireless", "wi-fi", "wifi", "802.11")):
        p.nic_type = "Wi-Fi"
        # Sub-query: get the live PHY for the Wi-Fi adapter
        wifi = run_cmd("netsh wlan show interfaces", timeout=10)
        if wifi.ok:
            phy = re.search(r"Radio type\s*:\s*(\S+)", wifi.text)
            if phy:
                p.wifi_standard = phy.group(1)
            band = re.search(r"Band\s*:\s*(\S+\s*\S+)", wifi.text)
            if band:
                p.wifi_band = band.group(1)
    else:
        p.nic_type = "Ethernet"


def _detect_firmware_and_os(p: HardwareProfile) -> None:
    bios = _ps_json(
        "Get-CimInstance Win32_BIOS | Select-Object ReleaseDate,Manufacturer,Name,Version"
    )
    if isinstance(bios, list): bios = bios[0] if bios else None
    if isinstance(bios, dict):
        raw = str(bios.get("ReleaseDate") or "")
        m = re.search(r"(\d{4})(\d{2})(\d{2})", raw)
        if m:
            p.bios_date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    osd = _ps_json(
        "Get-CimInstance Win32_OperatingSystem | Select-Object Caption,BuildNumber,Version"
    )
    if isinstance(osd, list): osd = osd[0] if osd else None
    if isinstance(osd, dict):
        p.os_caption = str(osd.get("Caption") or "").replace("Microsoft ", "")
        p.os_build   = str(osd.get("BuildNumber") or "")


def _detect_form_factor(p: HardwareProfile) -> None:
    # Presence of any battery → laptop (best heuristic available without WMI
    # chassis types being unreliable).
    data = _ps_json("(Get-CimInstance Win32_Battery | Measure-Object).Count")
    try:
        p.is_laptop = int(data or 0) > 0
    except Exception:
        p.is_laptop = False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def detect(force_refresh: bool = False) -> HardwareProfile:
    """Detect hardware and cache the result.

    First call may take ~2-5 seconds on Windows (several PowerShell queries).
    Subsequent calls return the cached profile instantly.
    """
    global _cache
    with _cache_lock:
        if _cache is not None and not force_refresh:
            return _cache
        prof = HardwareProfile()
        if not is_windows():
            prof.errors.append("not running on Windows — detection skipped")
            prof.os_caption = "non-Windows host"
            _cache = prof
            return prof
        for step in (
            _detect_cpu, _detect_gpu, _detect_ram, _detect_storage,
            _detect_display, _detect_network, _detect_firmware_and_os,
            _detect_form_factor,
        ):
            try:
                step(prof)
            except Exception as e:        # noqa: BLE001
                prof.errors.append(f"{step.__name__}: {type(e).__name__}: {e}")
                log.exception("hardware detection step %s failed", step.__name__)
        _cache = prof
        return prof


def reset_cache() -> None:
    global _cache
    with _cache_lock:
        _cache = None

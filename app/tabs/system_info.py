"""System info — read-only inventory."""
from __future__ import annotations

import platform
import threading

import customtkinter as ctk

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore

from ._base import TabBase, OutputConsole
from ..theme import COLORS, font
from ..utils.admin import is_windows
from ..utils.runner import run_cmd, run_powershell


class SystemInfoTab(TabBase):
    title = "System Info"
    subtitle = "Hardware, OS, drivers, installed updates. Read-only."

    def build(self) -> None:
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_rowconfigure(1, weight=1)

        # Top: summary card
        top = ctk.CTkFrame(self.body, fg_color=COLORS["panel"], corner_radius=12)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        self.summary = ctk.CTkLabel(top, text="Loading…", anchor="w",
                                    justify="left", font=("Consolas", 11),
                                    text_color=COLORS["text"])
        self.summary.grid(row=0, column=0, sticky="ew", padx=14, pady=14)

        # Buttons row
        btns = ctk.CTkFrame(self.body, fg_color="transparent")
        btns.grid(row=1, column=0, sticky="new", pady=8)
        for i in range(6):
            btns.grid_columnconfigure(i, weight=1, uniform="b")

        for i, (label, fn) in enumerate([
            ("OS + BIOS",        self._show_os),
            ("CPU",              self._show_cpu),
            ("GPU",              self._show_gpu),
            ("Memory",           self._show_ram),
            ("Disks",            self._show_disks),
            ("Network adapters", self._show_net),
            ("Installed apps",   self._show_apps),
            ("Installed updates",self._show_updates),
            ("Drivers (3rd-party)", self._show_drivers),
        ]):
            ctk.CTkButton(
                btns, text=label, height=32,
                fg_color=COLORS["panel_alt"], hover_color=COLORS["accent"],
                command=fn,
            ).grid(row=i // 6, column=i % 6, sticky="ew", padx=4, pady=4)

        # Console
        self.console = OutputConsole(self.body, height=350)
        self.console.grid(row=2, column=0, sticky="nsew", pady=(8, 0))
        self.body.grid_rowconfigure(2, weight=1)

        self._populate_summary()

    # ------------------------------------------------------------------
    def _populate_summary(self) -> None:
        lines: list[str] = []
        lines.append(f" OS        : {platform.system()} {platform.release()} ({platform.version()})")
        lines.append(f" Machine   : {platform.machine()}  ·  Node: {platform.node()}")
        lines.append(f" Python    : {platform.python_version()}")
        if psutil:
            try:
                cores = psutil.cpu_count(logical=False)
                threads = psutil.cpu_count(logical=True)
                mem = psutil.virtual_memory().total / (1024 ** 3)
                lines.append(f" CPU       : {cores} cores / {threads} threads")
                lines.append(f" Memory    : {mem:.1f} GiB total")
            except Exception:
                pass
        self.summary.configure(text="\n".join(lines))

    # ------------------------------------------------------------------
    def _run(self, header: str, cb) -> None:
        self.after(0, self.console.separator, header.upper())

        def worker():
            r = cb()
            text = r.text if hasattr(r, "text") else str(r)
            ok  = getattr(r, "ok", True)
            rc  = getattr(r, "returncode", 0)
            self.after(0, self.console.result, ok, rc)
            self.after(0, self.console.output, text, 200)
        threading.Thread(target=worker, daemon=True).start()

    def _show_os(self):
        self._run("OS + BIOS",
                  lambda: run_powershell(
                      "systeminfo | Select-String 'OS Name','OS Version','System Manufacturer',"
                      "'System Model','BIOS Version','Boot Device','System Locale','Time Zone'"))

    def _show_cpu(self):
        self._run("CPU", lambda: run_powershell(
            "Get-CimInstance Win32_Processor | Format-List Name,NumberOfCores,"
            "NumberOfLogicalProcessors,MaxClockSpeed,Manufacturer,SocketDesignation,VirtualizationFirmwareEnabled"))

    def _show_gpu(self):
        self._run("GPU", lambda: run_powershell(
            "Get-CimInstance Win32_VideoController | Format-List Name,AdapterRAM,DriverVersion,DriverDate,VideoProcessor"))

    def _show_ram(self):
        self._run("Memory", lambda: run_powershell(
            "Get-CimInstance Win32_PhysicalMemory | Format-Table BankLabel,Capacity,Speed,Manufacturer,PartNumber -AutoSize"))

    def _show_disks(self):
        self._run("Disks", lambda: run_powershell(
            "Get-PhysicalDisk | Format-Table FriendlyName,MediaType,HealthStatus,Size,BusType -AutoSize"))

    def _show_net(self):
        self._run("Network adapters", lambda: run_powershell(
            "Get-NetAdapter | Format-Table Name,InterfaceDescription,Status,LinkSpeed,MacAddress -AutoSize"))

    def _show_apps(self):
        self._run("Installed apps (winget)", lambda: run_cmd("winget list", timeout=120))

    def _show_updates(self):
        self._run("Installed updates",
                  lambda: run_cmd("wmic qfe list brief /format:table", timeout=60))

    def _show_drivers(self):
        self._run("3rd-party drivers",
                  lambda: run_cmd("driverquery /v /fo csv | findstr /v Microsoft", timeout=60))

"""Dashboard — live system stats + global one-shot actions."""
from __future__ import annotations

import threading
import time
import tkinter as tk

import customtkinter as ctk

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None  # type: ignore

from ._base import TabBase, OutputConsole
from ..theme import COLORS, font
from ..utils.admin import is_admin, is_windows
from ..utils.restore_point import create_restore_point
from ..utils.runner import run_cmd, run_powershell


class _Card(ctk.CTkFrame):
    """A stat card with a big number + label."""
    def __init__(self, master, label: str, value: str = "—", accent: str = COLORS["accent"]):
        super().__init__(master, fg_color=COLORS["panel"], corner_radius=14)
        self.value_var = tk.StringVar(value=value)
        ctk.CTkLabel(self, text=label, font=font(11, "bold"),
                     text_color=COLORS["text_dim"], anchor="w").pack(
            anchor="w", padx=16, pady=(14, 0))
        ctk.CTkLabel(self, textvariable=self.value_var, font=font(28, "bold"),
                     text_color=accent, anchor="w").pack(
            anchor="w", padx=16, pady=(2, 16))


class DashboardTab(TabBase):
    title = "Dashboard"
    subtitle = "Live system health + global one-shot actions."

    def build(self) -> None:
        self.body.grid_rowconfigure(0, weight=0)
        self.body.grid_rowconfigure(1, weight=0)
        self.body.grid_rowconfigure(2, weight=1)

        # ----- Stat cards -----
        cards = ctk.CTkFrame(self.body, fg_color=COLORS["bg"])
        cards.grid(row=0, column=0, sticky="ew")
        for i in range(4):
            cards.grid_columnconfigure(i, weight=1, uniform="c", pad=8)

        self.card_cpu  = _Card(cards, "CPU",  "—%", COLORS["accent"])
        self.card_ram  = _Card(cards, "RAM",  "—%", COLORS["warn"])
        self.card_disk = _Card(cards, "Disk C:", "—%", COLORS["ok"])
        self.card_up   = _Card(cards, "Uptime", "—", COLORS["text"])
        for i, c in enumerate((self.card_cpu, self.card_ram, self.card_disk, self.card_up)):
            c.grid(row=0, column=i, sticky="nsew", padx=6, pady=6)

        # ----- Quick actions -----
        qa = ctk.CTkFrame(self.body, fg_color=COLORS["panel"], corner_radius=12)
        qa.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        ctk.CTkLabel(qa, text="Quick actions", font=font(13, "bold"),
                     text_color=COLORS["text"], anchor="w").grid(
            row=0, column=0, columnspan=4, sticky="w", padx=14, pady=(10, 6))

        actions: list[tuple[str, str, str]] = [
            ("Create Restore Point",  "restore",  "Create a System Restore Point named ‘Bloated — pre-change snapshot’."),
            ("Open Task Manager",     "taskmgr",  "Launch Task Manager."),
            ("Open Resource Monitor", "resmon",   "Launch Resource Monitor."),
            ("Open Services",         "services", "Launch services.msc."),
            ("Flush DNS",             "flushdns", "ipconfig /flushdns."),
            ("Restart Explorer",      "restart_explorer", "Reload the Windows shell."),
            ("SFC scan",              "sfc",      "sfc /scannow — repair protected system files."),
            ("Open log folder",       "logs",     "Open Bloated’s log folder in Explorer."),
        ]
        for i, (label, key, tip) in enumerate(actions):
            btn = ctk.CTkButton(
                qa, text=label, height=36, corner_radius=10,
                fg_color=COLORS["panel_alt"], hover_color=COLORS["accent"],
                text_color=COLORS["text"], font=font(12),
                command=lambda k=key: self._handle_quick(k),
            )
            btn.grid(row=1 + i // 4, column=i % 4, padx=8, pady=6, sticky="ew")
            qa.grid_columnconfigure(i % 4, weight=1, uniform="qa")

        # ----- Output console -----
        self.console = OutputConsole(self.body, height=260)
        self.console.grid(row=2, column=0, sticky="nsew", pady=(12, 0))

        # ----- Admin / OS banner -----
        if not is_admin():
            self.console.append("⚠  Not running as Administrator — system-wide tweaks will fail.")
        if not is_windows():
            self.console.append("ℹ  Not on Windows — actions are visible for preview but won’t apply.")
        self.console.append("Welcome. Pick a category on the left to begin.")

        # Start the live stats poller
        if psutil is not None:
            self._poll_running = True
            self._start_polling()

    # ------------------------------------------------------------------
    def _start_polling(self) -> None:
        def worker():
            boot = psutil.boot_time() if psutil else time.time()
            while getattr(self, "_poll_running", False):
                try:
                    cpu = psutil.cpu_percent(interval=1.0)
                    ram = psutil.virtual_memory().percent
                    try:
                        disk = psutil.disk_usage("C:\\" if is_windows() else "/").percent
                    except Exception:
                        disk = 0.0
                    up = int(time.time() - boot)
                    self.after(0, self._update_cards, cpu, ram, disk, up)
                except Exception:
                    time.sleep(2)
        threading.Thread(target=worker, daemon=True).start()

    def _update_cards(self, cpu, ram, disk, up_sec):
        self.card_cpu.value_var.set(f"{cpu:.0f}%")
        self.card_ram.value_var.set(f"{ram:.0f}%")
        self.card_disk.value_var.set(f"{disk:.0f}%")
        d, rem = divmod(up_sec, 86400)
        h, rem = divmod(rem, 3600)
        m, _  = divmod(rem, 60)
        if d:
            self.card_up.value_var.set(f"{d}d {h}h")
        elif h:
            self.card_up.value_var.set(f"{h}h {m}m")
        else:
            self.card_up.value_var.set(f"{m}m")

    # ------------------------------------------------------------------
    def _handle_quick(self, key: str) -> None:
        from ..utils.logger import log_path
        import os, subprocess

        def append(msg: str): self.after(0, self.console.append, msg)

        def run(label: str, cb):
            append(f"▶ {label}")
            def worker():
                try:
                    result = cb()
                    append(f"  ✔ {result}" if result else "  ✔ done")
                except Exception as e:
                    append(f"  ✖ {e}")
            threading.Thread(target=worker, daemon=True).start()

        if key == "restore":
            run("Create restore point", lambda: create_restore_point().text)
        elif key == "taskmgr":
            run("Task Manager", lambda: run_cmd("start taskmgr").text or "launched")
        elif key == "resmon":
            run("Resource Monitor", lambda: run_cmd("start resmon").text or "launched")
        elif key == "services":
            run("services.msc", lambda: run_cmd("start services.msc").text or "launched")
        elif key == "flushdns":
            run("Flush DNS", lambda: run_cmd("ipconfig /flushdns").text)
        elif key == "restart_explorer":
            run("Restart Explorer",
                lambda: run_cmd("taskkill /f /im explorer.exe & start explorer.exe").text)
        elif key == "sfc":
            append("  sfc may take several minutes — running in background.")
            run("SFC /scannow", lambda: run_cmd("sfc /scannow", timeout=900).text)
        elif key == "logs":
            try:
                folder = log_path().parent
                if is_windows():
                    os.startfile(str(folder))  # type: ignore[attr-defined]
                else:
                    subprocess.Popen(["xdg-open", str(folder)])
                append(f"Opened {folder}")
            except Exception as e:
                append(f"Could not open log folder: {e}")

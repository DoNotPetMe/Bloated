"""The main application window: sidebar navigation + content area."""
from __future__ import annotations

import customtkinter as ctk

from . import __app_name__, __version__
from .theme import COLORS, apply_theme, font
from .utils.admin import is_admin, is_windows, relaunch_as_admin
from .tabs.dashboard import DashboardTab
from .tabs.debloat import DebloatTab
from .tabs.privacy import PrivacyTab
from .tabs.performance import PerformanceTab
from .tabs.game_tune import GameTuneTab
from .tabs.services import ServicesTab
from .tabs.tweaks import TweaksTab
from .tabs.cleanup import CleanupTab
from .tabs.network import NetworkTab
from .tabs.updates import UpdatesTab
from .tabs.apps import AppsTab
from .tabs.commands import CommandsTab
from .tabs.headroom import HeadroomTab
from .tabs.system_info import SystemInfoTab


# (label, icon-glyph, tab-class)
TABS = [
    ("Dashboard",   "☰",  DashboardTab),
    ("Debloater",   "✂",  DebloatTab),
    ("Privacy",     "\U0001F512", PrivacyTab),
    ("Performance", "⚡",  PerformanceTab),
    ("Game Tune",   "\U0001F3AE", GameTuneTab),
    ("Services",    "⚙",  ServicesTab),
    ("Tweaks",      "\U0001F527", TweaksTab),
    ("Cleanup",     "\U0001F9F9", CleanupTab),
    ("Network",     "\U0001F310", NetworkTab),
    ("Updates",     "↻",  UpdatesTab),
    ("Apps",        "\U0001F4E6", AppsTab),
    ("Commands",    "▶",  CommandsTab),
    ("Headroom",    "\U0001F4CA", HeadroomTab),
    ("System Info", "\U0001F4BB", SystemInfoTab),
]


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        apply_theme()
        super().__init__(fg_color=COLORS["bg"])
        self.title(f"{__app_name__} — Windows PC Powerhouse v{__version__}")
        self.geometry("1280x800")
        self.minsize(1100, 680)

        # Grid: sidebar | content
        self.grid_columnconfigure(0, weight=0, minsize=210)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self._build_sidebar()
        self._build_content()
        self._build_status_bar()

        self._tabs: dict[str, ctk.CTkFrame] = {}
        self._current: str | None = None
        self._select_tab(TABS[0][0])

    # ---------- UI construction ----------

    def _build_sidebar(self) -> None:
        side = ctk.CTkFrame(self, fg_color=COLORS["sidebar"], corner_radius=0)
        side.grid(row=0, column=0, rowspan=2, sticky="nsew")
        side.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(side, fg_color="transparent", height=80)
        header.grid(row=0, column=0, sticky="ew", padx=14, pady=(18, 8))
        ctk.CTkLabel(
            header, text="Bloated", font=font(22, "bold"),
            text_color=COLORS["accent"], anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            header, text="PC Powerhouse", font=font(11),
            text_color=COLORS["text_dim"], anchor="w",
        ).pack(anchor="w")

        # Buttons
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        row = 1
        for label, icon, _cls in TABS:
            btn = ctk.CTkButton(
                side,
                text=f"  {icon}   {label}",
                anchor="w",
                height=40,
                corner_radius=10,
                fg_color="transparent",
                hover_color=COLORS["panel_alt"],
                text_color=COLORS["text"],
                font=font(13),
                command=lambda lbl=label: self._select_tab(lbl),
            )
            btn.grid(row=row, column=0, sticky="ew", padx=10, pady=2)
            self._nav_buttons[label] = btn
            row += 1

        # Footer (admin badge)
        side.grid_rowconfigure(row, weight=1)
        footer = ctk.CTkFrame(side, fg_color="transparent")
        footer.grid(row=row + 1, column=0, sticky="ew", padx=14, pady=14)

        admin_ok = is_admin()
        badge_color = COLORS["ok"] if admin_ok else COLORS["warn"]
        badge_text = "● Admin" if admin_ok else "● Standard user"
        ctk.CTkLabel(footer, text=badge_text, text_color=badge_color,
                     font=font(11, "bold"), anchor="w").pack(anchor="w")

        if not admin_ok and is_windows():
            ctk.CTkButton(
                footer, text="Restart as Admin",
                fg_color=COLORS["warn"], hover_color="#D89A1A",
                text_color="#1a1a1a", height=30,
                font=font(11, "bold"),
                command=relaunch_as_admin,
            ).pack(fill="x", pady=(8, 0))

        if not is_windows():
            ctk.CTkLabel(
                footer, text="Non-Windows: preview mode",
                text_color=COLORS["text_dim"], font=font(10), anchor="w",
            ).pack(anchor="w", pady=(6, 0))

    def _build_content(self) -> None:
        self.content = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def _build_status_bar(self) -> None:
        bar = ctk.CTkFrame(self, fg_color=COLORS["panel"], height=28, corner_radius=0)
        bar.grid(row=1, column=1, sticky="ew")
        bar.grid_columnconfigure(0, weight=1)
        self.status_var = ctk.StringVar(value="Ready.")
        ctk.CTkLabel(
            bar, textvariable=self.status_var, anchor="w",
            font=font(11), text_color=COLORS["text_dim"],
        ).grid(row=0, column=0, sticky="ew", padx=14)
        ctk.CTkLabel(
            bar, text=f"v{__version__}",
            font=font(11), text_color=COLORS["text_dim"],
        ).grid(row=0, column=1, sticky="e", padx=14)

    # ---------- Navigation ----------

    def _select_tab(self, label: str) -> None:
        if self._current == label:
            return

        # Highlight active button
        for lbl, btn in self._nav_buttons.items():
            if lbl == label:
                btn.configure(fg_color=COLORS["panel_alt"], text_color=COLORS["accent"])
            else:
                btn.configure(fg_color="transparent", text_color=COLORS["text"])

        # Lazy-instantiate the tab
        if label not in self._tabs:
            cls = next(c for l, _i, c in TABS if l == label)
            tab = cls(self.content, status_setter=self.set_status)
            tab.grid(row=0, column=0, sticky="nsew")
            self._tabs[label] = tab

        # Show selected tab, hide others
        for lbl, frame in self._tabs.items():
            if lbl == label:
                frame.tkraise()

        self._current = label
        self.set_status(f"{label} ready.")

    # ---------- Status helper exposed to tabs ----------

    def set_status(self, text: str) -> None:
        try:
            self.status_var.set(text)
        except Exception:
            pass

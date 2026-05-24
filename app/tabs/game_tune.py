"""Game Tune — hardware-aware game performance tweaks with presets.

Subclasses :class:`ActionListTab`. On open:
  1. detects hardware (cached after first call)
  2. builds the action list filtered for that hardware
  3. adds a hardware profile card above the list
  4. adds preset buttons (Esports / AAA / Streaming / Laptop) that
     auto-tick every action carrying that preset tag
  5. adds a BIOS-level checklist at the bottom of the left column
"""
from __future__ import annotations

import threading
import tkinter as tk

import customtkinter as ctk

from ._base import ActionListTab
from ..data.game_tweaks_data import (
    PRESETS, BIOS_CHECKLIST, build_for,
)
from ..theme import COLORS, font
from ..utils.hardware import HardwareProfile, detect, reset_cache


class GameTuneTab(ActionListTab):
    title = "Game Tune"
    subtitle = (
        "Hardware-aware game performance tweaks. Detects your CPU / GPU / "
        "RAM / display / network and only offers actions that actually "
        "apply. Pick a preset to auto-tick a sensible set, then Run."
    )

    # ---------- build ----------

    def build(self) -> None:
        # Placeholder while detection runs (first time only).
        self._profile: HardwareProfile = HardwareProfile()
        self._profile.os_caption = "detecting…"
        self.actions = build_for(self._profile)  # tiny universal set
        super().build()
        # Kick off proper detection in a background thread.
        threading.Thread(target=self._detect_and_refresh, daemon=True).start()

    # ---------- detection ----------

    def _detect_and_refresh(self) -> None:
        prof = detect()
        self.after(0, self._apply_profile, prof)

    def _apply_profile(self, prof: HardwareProfile) -> None:
        self._profile = prof
        # Rebuild action list to include hardware-conditional ones.
        new_actions = build_for(prof)
        self.actions = new_actions
        self._rows.clear()
        for a in new_actions:
            from ._base import _Row
            row = _Row(action=a)
            row.var.set(a.enabled_by_default)
            row.var.trace_add("write", lambda *_: self._update_count())
            self._rows.append(row)
        self._render_rows()
        self._update_count()
        # Refresh profile card.
        if hasattr(self, "_profile_card"):
            self._populate_profile_card()
        if prof.errors:
            self.status(f"Hardware detection: {len(prof.errors)} warnings — "
                        "check the log.")

    # ---------- extra layout ----------

    def _extend_layout(self) -> None:
        # Insert above the action toolbar: preset bar.
        self._build_preset_bar()
        # Insert above everything in the left panel: profile card.
        self._build_profile_card()
        # Append below the run-button bar: BIOS checklist.
        self._build_bios_card()

    def _build_preset_bar(self) -> None:
        bar = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 0))
        for i in range(len(PRESETS) + 1):
            bar.grid_columnconfigure(i, weight=1, uniform="presets")
        ctk.CTkLabel(
            bar, text="PRESETS:", font=font(11, "bold"),
            text_color=COLORS["text_dim"], anchor="w",
        ).grid(row=0, column=0, sticky="w")
        for i, name in enumerate(PRESETS):
            ctk.CTkButton(
                bar, text=name, height=28, corner_radius=8,
                fg_color=COLORS["panel_alt"], hover_color=COLORS["accent"],
                text_color=COLORS["text"], font=font(11, "bold"),
                command=lambda n=name: self._apply_preset(n),
            ).grid(row=0, column=i + 1, padx=4, sticky="ew")

        # Push the original toolbar / scroll / run-button bar down one row.
        # Move the run-button bar (originally at row 2) FIRST, before scroll
        # claims row 2 — otherwise the row-2 filter would pick up scroll too.
        for child in self.left_panel.winfo_children():
            info = child.grid_info()
            if info and int(info.get("row", 0)) == 2 and child not in (
                self.tools_frame, self.scroll, bar,
            ):
                child.grid_configure(row=3)
        self.scroll.grid_configure(row=2)
        self.tools_frame.grid_configure(row=1)

        # Reset row weights so only the scroll area expands.
        self.left_panel.grid_rowconfigure(0, weight=0)   # preset bar
        self.left_panel.grid_rowconfigure(1, weight=0)   # toolbar
        self.left_panel.grid_rowconfigure(2, weight=1)   # action list
        self.left_panel.grid_rowconfigure(3, weight=0)   # run-button bar

    def _build_profile_card(self) -> None:
        card = ctk.CTkFrame(self.body, fg_color=COLORS["panel"],
                            corner_radius=10)
        # The body already has the actions/console row at row 0. Push them
        # down to row 1 and use row 0 for the card.
        self.body.grid_rowconfigure(0, weight=0)
        self.body.grid_rowconfigure(1, weight=1)
        for child in self.body.winfo_children():
            info = child.grid_info()
            if info and int(info.get("row", 0)) == 0 and child is not card:
                child.grid_configure(row=1)
        card.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        card.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 4))
        ctk.CTkLabel(
            header, text="DETECTED HARDWARE",
            font=("Cascadia Mono", 11, "bold"),
            text_color=COLORS["accent"], anchor="w",
        ).pack(side="left")
        ctk.CTkButton(
            header, text="Re-scan", width=80, height=24,
            fg_color=COLORS["panel_alt"], hover_color=COLORS["border"],
            text_color=COLORS["text_dim"], font=font(11),
            command=self._rescan,
        ).pack(side="right")

        self._profile_grid = ctk.CTkFrame(card, fg_color="transparent")
        self._profile_grid.grid(row=1, column=0, sticky="ew",
                                padx=14, pady=(0, 10))
        self._profile_grid.grid_columnconfigure(1, weight=1)
        self._profile_grid.grid_columnconfigure(3, weight=1)
        self._profile_card = card
        self._populate_profile_card()

    def _populate_profile_card(self) -> None:
        for w in list(self._profile_grid.children.values()):
            w.destroy()
        lines = self._profile.as_lines()
        # Two columns for compactness.
        for idx, (k, v) in enumerate(lines):
            col = (idx % 2) * 2
            row = idx // 2
            ctk.CTkLabel(
                self._profile_grid, text=k, anchor="w",
                font=("Cascadia Mono", 11, "bold"),
                text_color=COLORS["text_dim"],
                width=80,
            ).grid(row=row, column=col, sticky="w", padx=(0, 6), pady=2)
            ctk.CTkLabel(
                self._profile_grid, text=v or "—", anchor="w",
                font=("Cascadia Mono", 11),
                text_color=COLORS["text"], wraplength=420, justify="left",
            ).grid(row=row, column=col + 1, sticky="w", padx=(0, 30), pady=2)

    def _build_bios_card(self) -> None:
        """Read-only ‘BIOS-level things Bloated cannot touch’ panel.

        Collapsible — defaults to collapsed so the Run button on the action
        list above is always visible. Click the header to expand.
        """
        card = ctk.CTkFrame(self.body, fg_color=COLORS["panel"],
                            corner_radius=10)
        # Append at the bottom with zero weight so it never steals vertical
        # space from the action list / console row above.
        self.body.grid_rowconfigure(2, weight=0)
        card.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        card.grid_columnconfigure(0, weight=1)

        self._bios_expanded = False
        self._bios_card = card

        # Clickable header (acts as the expand/collapse toggle).
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 4))
        header.grid_columnconfigure(1, weight=1)

        self._bios_arrow = ctk.CTkLabel(
            header, text="▸", font=("Cascadia Mono", 12, "bold"),
            text_color=COLORS["warn"], width=14,
        )
        self._bios_arrow.grid(row=0, column=0, sticky="w")
        title = ctk.CTkLabel(
            header,
            text=f"DO IN BIOS  ({len(BIOS_CHECKLIST)} items Bloated can’t touch)",
            font=("Cascadia Mono", 11, "bold"),
            text_color=COLORS["warn"], anchor="w",
        )
        title.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        for w in (header, self._bios_arrow, title):
            w.bind("<Button-1>", lambda _e: self._toggle_bios())

        # Container for the per-item rows (created on first expand).
        self._bios_items = ctk.CTkFrame(card, fg_color="transparent")

    def _toggle_bios(self) -> None:
        self._bios_expanded = not self._bios_expanded
        self._bios_arrow.configure(text="▾" if self._bios_expanded else "▸")
        if self._bios_expanded:
            # Build rows lazily on first expand.
            if not self._bios_items.winfo_children():
                self._bios_items.grid_columnconfigure(0, weight=1)
                for i, (name, desc) in enumerate(BIOS_CHECKLIST):
                    self._make_bios_row(self._bios_items, i, name, desc)
            self._bios_items.grid(row=1, column=0, sticky="ew",
                                  padx=8, pady=(0, 10))
        else:
            self._bios_items.grid_forget()

    def _make_bios_row(self, parent, i: int, name: str, desc: str) -> None:
        row = ctk.CTkFrame(parent, fg_color=COLORS["panel_alt"],
                           corner_radius=6)
        row.grid(row=i, column=0, sticky="ew", padx=0, pady=2)
        row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            row, text=f"✔ {name}", anchor="w",
            font=font(11, "bold"), text_color=COLORS["text"],
            width=240,
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(6, 0))
        ctk.CTkLabel(
            row, text=desc, anchor="w",
            font=font(11), text_color=COLORS["text_dim"],
            wraplength=720, justify="left",
            ).grid(row=0, column=1, sticky="ew", padx=(6, 10), pady=(6, 6))

    # ---------- preset handling ----------

    def _apply_preset(self, preset: str) -> None:
        """Auto-tick every action whose `presets` tuple contains `preset`."""
        for r in self._rows:
            r.var.set(preset in r.action.presets)
        self.console.separator(f"PRESET · {preset.upper()}")
        n_on = sum(1 for r in self._rows if r.var.get())
        self.console.log(
            f"{n_on} action(s) auto-selected for the {preset} preset.",
            "head")
        self.console.log(
            "review the list, untick anything you don’t want, then Run.",
            "dim")

    def _rescan(self) -> None:
        self.console.action("Re-scan hardware")
        reset_cache()
        threading.Thread(target=self._detect_and_refresh, daemon=True).start()
        self.console.log("scanning…", "dim")

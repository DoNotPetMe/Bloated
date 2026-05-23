"""Shared building blocks for tabs.

`ActionListTab` is a generic tab that displays a list of checkbox-selectable
actions (each with title, description and command), plus an output console.
Most of the heavy-lifting tabs subclass it and just supply data.
"""
from __future__ import annotations

import threading
import tkinter as tk
from dataclasses import dataclass, field
from typing import Callable, List

import customtkinter as ctk

from ..theme import COLORS, font
from ..utils.runner import (
    CommandResult,
    run_cmd,
    run_powershell,
)
from ._models import Action  # re-exported for convenience


# ---------------------------------------------------------------------------
# Base classes
# ---------------------------------------------------------------------------


class TabBase(ctk.CTkFrame):
    """Common shell + header for every tab."""
    title: str = "Tab"
    subtitle: str = ""

    def __init__(self, master, status_setter: Callable[[str], None]) -> None:
        super().__init__(master, fg_color=COLORS["bg"], corner_radius=0)
        self.status_setter = status_setter
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_header()
        self.body = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        self.body.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 16))
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_rowconfigure(0, weight=1)
        self.build()

    def _build_header(self) -> None:
        h = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0, height=72)
        h.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        h.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            h, text=self.title, font=font(22, "bold"),
            text_color=COLORS["text"], anchor="w",
        ).grid(row=0, column=0, sticky="w")
        if self.subtitle:
            ctk.CTkLabel(
                h, text=self.subtitle, font=font(12),
                text_color=COLORS["text_dim"], anchor="w",
            ).grid(row=1, column=0, sticky="w", pady=(2, 0))

    # Subclasses override this.
    def build(self) -> None:  # pragma: no cover - UI
        ctk.CTkLabel(self.body, text="(not implemented)").pack()

    # Convenience.
    def status(self, msg: str) -> None:
        self.status_setter(msg)


# ---------------------------------------------------------------------------
# Output console widget
# ---------------------------------------------------------------------------


class OutputConsole(ctk.CTkFrame):
    """Read-only console with append() and clear()."""
    def __init__(self, master, height: int = 200):
        super().__init__(master, fg_color=COLORS["panel"], corner_radius=10)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 4))
        ctk.CTkLabel(bar, text="Output", font=font(12, "bold"),
                     text_color=COLORS["text_dim"]).pack(side="left")
        ctk.CTkButton(
            bar, text="Clear", width=70, height=24,
            fg_color="transparent", hover_color=COLORS["panel_alt"],
            text_color=COLORS["text_dim"], font=font(11),
            command=self.clear,
        ).pack(side="right")

        self.text = ctk.CTkTextbox(
            self, height=height,
            fg_color=COLORS["bg"], text_color=COLORS["text"],
            font=("Consolas", 11), corner_radius=8, wrap="word",
        )
        self.text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.text.configure(state="disabled")

    def append(self, line: str) -> None:
        self.text.configure(state="normal")
        self.text.insert("end", line + "\n")
        self.text.see("end")
        self.text.configure(state="disabled")

    def clear(self) -> None:
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")


# ---------------------------------------------------------------------------
# Action list tab (used by debloat / privacy / tweaks / cleanup / etc.)
# ---------------------------------------------------------------------------


@dataclass
class _Row:
    action: Action
    var: tk.BooleanVar = field(default_factory=tk.BooleanVar)


class ActionListTab(TabBase):
    """A scrollable list of selectable actions with a Run-Selected console."""
    actions: List[Action] = []
    select_all_default: bool = False

    def build(self) -> None:
        self.body.grid_rowconfigure(0, weight=1)
        self.body.grid_rowconfigure(1, weight=0)

        # Two-column body: list (left) | console (right)
        self.body.grid_columnconfigure(0, weight=3)
        self.body.grid_columnconfigure(1, weight=2)

        # ----- left: scroll frame of actions -----
        left = ctk.CTkFrame(self.body, fg_color=COLORS["panel"], corner_radius=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)

        # Toolbar
        tools = ctk.CTkFrame(left, fg_color="transparent")
        tools.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
        tools.grid_columnconfigure(3, weight=1)
        ctk.CTkButton(tools, text="Select all", width=90, height=28,
                      fg_color=COLORS["panel_alt"], hover_color=COLORS["border"],
                      command=self._select_all,
                      font=font(11)).grid(row=0, column=0, padx=(0, 6))
        ctk.CTkButton(tools, text="None", width=70, height=28,
                      fg_color=COLORS["panel_alt"], hover_color=COLORS["border"],
                      command=self._select_none,
                      font=font(11)).grid(row=0, column=1, padx=(0, 6))
        ctk.CTkButton(tools, text="Recommended", width=120, height=28,
                      fg_color=COLORS["panel_alt"], hover_color=COLORS["border"],
                      command=self._select_recommended,
                      font=font(11)).grid(row=0, column=2, padx=(0, 6))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._refresh_filter())
        ctk.CTkEntry(tools, placeholder_text="Search…",
                     textvariable=self.search_var, height=28,
                     fg_color=COLORS["bg"], border_color=COLORS["border"],
                     ).grid(row=0, column=3, sticky="ew", padx=(6, 0))

        self.scroll = ctk.CTkScrollableFrame(
            left, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"],
        )
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=6, pady=(4, 6))
        self.scroll.grid_columnconfigure(0, weight=1)

        # Bottom action bar
        bottom = ctk.CTkFrame(left, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        bottom.grid_columnconfigure(1, weight=1)
        self.run_button = ctk.CTkButton(
            bottom, text="Run selected", height=36,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#0a0a0a", font=font(13, "bold"),
            command=self._run_selected,
        )
        self.run_button.grid(row=0, column=0)
        self.count_var = tk.StringVar(value="0 selected")
        ctk.CTkLabel(bottom, textvariable=self.count_var,
                     text_color=COLORS["text_dim"], font=font(11),
                     ).grid(row=0, column=1, padx=12, sticky="w")

        # ----- right: console -----
        self.console = OutputConsole(self.body, height=400)
        self.console.grid(row=0, column=1, sticky="nsew")

        # Build rows
        self._rows: list[_Row] = []
        self._row_widgets: list[ctk.CTkFrame] = []
        for a in self.actions:
            row = _Row(action=a)
            row.var.set(a.enabled_by_default or self.select_all_default)
            row.var.trace_add("write", lambda *_: self._update_count())
            self._rows.append(row)
        self._render_rows()
        self._update_count()

    # ---------- rendering ----------

    def _render_rows(self) -> None:
        for w in self._row_widgets:
            w.destroy()
        self._row_widgets.clear()

        q = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
        # Group by category
        by_cat: dict[str, list[_Row]] = {}
        for r in self._rows:
            if q and q not in r.action.title.lower() and q not in r.action.description.lower():
                continue
            by_cat.setdefault(r.action.category, []).append(r)

        i = 0
        for cat, rows in by_cat.items():
            hdr = ctk.CTkLabel(
                self.scroll, text=cat.upper(),
                text_color=COLORS["text_dim"], font=font(10, "bold"),
                anchor="w",
            )
            hdr.grid(row=i, column=0, sticky="ew", padx=8, pady=(10, 4))
            self._row_widgets.append(hdr)
            i += 1
            for r in rows:
                card = ctk.CTkFrame(self.scroll, fg_color=COLORS["panel_alt"],
                                    corner_radius=8)
                card.grid(row=i, column=0, sticky="ew", padx=4, pady=3)
                card.grid_columnconfigure(1, weight=1)

                cb = ctk.CTkCheckBox(
                    card, text="", variable=r.var, width=20,
                    fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                    border_color=COLORS["border"],
                )
                cb.grid(row=0, column=0, rowspan=2, padx=(12, 8), pady=10, sticky="n")

                title_color = COLORS["danger"] if r.action.danger else COLORS["text"]
                ctk.CTkLabel(card, text=r.action.title, anchor="w",
                             text_color=title_color, font=font(12, "bold"),
                             ).grid(row=0, column=1, sticky="ew", pady=(8, 0))
                ctk.CTkLabel(card, text=r.action.description, anchor="w",
                             text_color=COLORS["text_dim"], font=font(11),
                             wraplength=520, justify="left",
                             ).grid(row=1, column=1, sticky="ew", pady=(2, 8))

                self._row_widgets.append(card)
                i += 1

    def _refresh_filter(self) -> None:
        self._render_rows()

    # ---------- toolbar handlers ----------

    def _select_all(self) -> None:
        for r in self._rows:
            r.var.set(True)

    def _select_none(self) -> None:
        for r in self._rows:
            r.var.set(False)

    def _select_recommended(self) -> None:
        for r in self._rows:
            r.var.set(r.action.enabled_by_default)

    def _update_count(self) -> None:
        n = sum(1 for r in self._rows if r.var.get())
        self.count_var.set(f"{n} selected")

    # ---------- execution ----------

    def _run_selected(self) -> None:
        chosen = [r.action for r in self._rows if r.var.get()]
        if not chosen:
            self.console.append("Nothing selected.")
            return

        if any(a.danger for a in chosen):
            from tkinter import messagebox
            if not messagebox.askokcancel(
                "Confirm destructive actions",
                f"{sum(1 for a in chosen if a.danger)} of {len(chosen)} actions are "
                "marked destructive (uninstall, remove, etc.). Continue?",
            ):
                return

        self.run_button.configure(state="disabled", text="Running…")
        self.status(f"Running {len(chosen)} action(s)…")

        def worker():
            for a in chosen:
                self._append_safe(f"▶ {a.title}")
                self._append_safe(f"  $ {a.shell}> {a.command}")
                result: CommandResult = (
                    run_powershell(a.command) if a.shell == "powershell"
                    else run_cmd(a.command)
                )
                marker = "✔" if result.ok else "✖"
                self._append_safe(f"  {marker} rc={result.returncode}")
                if result.text and result.text != "(no output)":
                    for line in result.text.splitlines()[:30]:
                        self._append_safe(f"    {line}")
                self._append_safe("")
            self.after(0, self._finish_run, len(chosen))

        threading.Thread(target=worker, daemon=True).start()

    def _append_safe(self, line: str) -> None:
        self.after(0, self.console.append, line)

    def _finish_run(self, count: int) -> None:
        self.run_button.configure(state="normal", text="Run selected")
        self.status(f"Finished {count} action(s).")

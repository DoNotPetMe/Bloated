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


# Terminal-style colour palette used INSIDE the OutputConsole only.
# Black background, neon green text, cyan accents — like a classic CRT terminal.
TERM = {
    "bg":         "#000000",
    "border":     "#1A8C2D",
    "text":       "#19E03A",   # default bright matrix green
    "dim":        "#0E7A1F",   # darker green for timestamps / output lines
    "head":       "#21F3FF",   # cyan for section headers / shell tag
    "action":     "#19E03A",   # green for action titles
    "command":    "#7BFF8A",   # light green for the actual command line
    "ok":         "#19E03A",
    "warn":       "#FFCC00",
    "err":        "#FF3344",
    "sep":        "#21F3FF",
    "user":       "#FFFFFF",
    "scroll":     "#1A8C2D",
    "scroll_hov": "#19E03A",
}


def _now_ts() -> str:
    """[HH:MM:SS] prefix used on every line, matching the screenshot."""
    from datetime import datetime
    return datetime.now().strftime("[%H:%M:%S]")


class OutputConsole(ctk.CTkFrame):
    """Terminal-style read-only console.

    Renders every entry with a coloured `[HH:MM:SS]` prefix and a severity
    tag (OK / WARN / ERR / etc.), on a pure-black background with neon-green
    text — the ‘hacker terminal’ look.

    Public API:
        log(message, level="info")    — generic line with timestamp
        separator(label=None)         — ASCII separator
        action(title)                 — start an action block
        command(cmd, shell)           — show the actual command being run
        result(ok, rc)                — show the exit status
        output(lines)                 — show captured stdout
        append(message)               — back-compat shim → log(message)
        clear()
    """
    def __init__(self, master, height: int = 200):
        super().__init__(
            master,
            fg_color=TERM["bg"],
            border_color=TERM["border"], border_width=1,
            corner_radius=4,
        )
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Title bar: ─ SYSTEM LOG ────────────────────────  [ Clear ] ──
        bar = ctk.CTkFrame(self, fg_color=TERM["bg"], corner_radius=0,
                           height=26)
        bar.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 0))
        bar.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            bar, text="── SYSTEM LOG ──",
            font=("Consolas", 11, "bold"),
            text_color=TERM["head"], anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            bar, text="[ CLEAR ]", width=80, height=22,
            fg_color=TERM["bg"], hover_color="#082008",
            text_color=TERM["head"], font=("Consolas", 10, "bold"),
            border_color=TERM["head"], border_width=1, corner_radius=2,
            command=self.clear,
        ).grid(row=0, column=1, sticky="e")

        # ── Body text widget ──
        self.text = ctk.CTkTextbox(
            self, height=height,
            fg_color=TERM["bg"], text_color=TERM["text"],
            font=("Cascadia Mono", 11), corner_radius=2, wrap="word",
            border_width=0,
            scrollbar_button_color=TERM["scroll"],
            scrollbar_button_hover_color=TERM["scroll_hov"],
        )
        self.text.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))

        # Tag styles (configured on the underlying tk.Text widget). CTk stores
        # it as `_textbox`; fall back to scanning children if that ever changes.
        raw = getattr(self.text, "_textbox", None)
        if raw is None:
            for child in self.text.winfo_children():
                if isinstance(child, tk.Text):
                    raw = child
                    break
        if raw is None:           # last-ditch: act as if CTkTextbox is the Text
            raw = self.text
        raw.tag_configure("ts",      foreground=TERM["dim"])
        raw.tag_configure("info",    foreground=TERM["text"])
        raw.tag_configure("dim",     foreground=TERM["dim"])
        raw.tag_configure("ok",      foreground=TERM["ok"])
        raw.tag_configure("warn",    foreground=TERM["warn"])
        raw.tag_configure("err",     foreground=TERM["err"])
        raw.tag_configure("head",    foreground=TERM["head"])
        raw.tag_configure("sep",     foreground=TERM["sep"])
        raw.tag_configure("cmd",     foreground=TERM["command"])
        raw.tag_configure("action",  foreground=TERM["action"])
        raw.tag_configure("shell",   foreground=TERM["head"])

        self.text.configure(state="disabled")
        self._raw = raw

        # Boot line so the panel never looks empty.
        self.separator("BLOATED // CONSOLE")
        self.log("ready — awaiting command", level="dim")

    # ------------------------------------------------------------------
    # Low-level writer

    def _write(self, segments: list[tuple[str, str]]) -> None:
        """Insert a sequence of (text, tag) pairs followed by a newline."""
        self.text.configure(state="normal")
        for text, tag in segments:
            self._raw.insert("end", text, tag)
        self._raw.insert("end", "\n")
        self.text.see("end")
        self.text.configure(state="disabled")

    # ------------------------------------------------------------------
    # Public API

    _LEVEL_TAGS = {
        "info":  ("info",  ""),
        "dim":   ("dim",   ""),
        "ok":    ("ok",    "[ OK ]   "),
        "warn":  ("warn",  "[WARN]   "),
        "err":   ("err",   "[ERR ]   "),
        "head":  ("head",  ""),
        "cmd":   ("cmd",   ""),
    }

    def log(self, message: str, level: str = "info") -> None:
        tag, prefix = self._LEVEL_TAGS.get(level, ("info", ""))
        segments: list[tuple[str, str]] = [(f"{_now_ts()} ", "ts")]
        if prefix:
            segments.append((prefix, tag))
        segments.append((str(message), tag))
        self._write(segments)

    def separator(self, label: str | None = None) -> None:
        if label:
            line = f"═══ {label} " + "═" * max(4, 56 - len(label))
        else:
            line = "═" * 60
        self._write([(line, "sep")])

    def action(self, title: str) -> None:
        """Open a new action block — bright-green title with >>> marker."""
        self._write([
            (f"{_now_ts()} ", "ts"),
            (">>> ", "head"),
            (title, "action"),
        ])

    def command(self, cmd: str, shell: str = "cmd") -> None:
        """Show the actual command about to run, like a shell echo."""
        shell_tag = f"{shell.lower()}>"
        self._write([
            (f"{_now_ts()} ", "ts"),
            ("    $ ", "dim"),
            (f"{shell_tag} ", "shell"),
            (cmd, "cmd"),
        ])

    def result(self, ok: bool, rc: int, duration_sec: float = 0.0) -> None:
        if duration_sec >= 0.1:
            self.log(f"exit code {rc}  ·  {duration_sec:.1f}s",
                     level="ok" if ok else "err")
        else:
            self.log(f"exit code {rc}", level="ok" if ok else "err")

    def output(self, text: str, max_lines: int = 30, level: str = "dim") -> None:
        """Print captured stdout/stderr from a command, lightly indented.

        `level` controls the colour of the output lines:
          - "dim"  for normal stdout (the default)
          - "warn" for stderr when rc=0 (informational warnings)
          - "err"  for stderr when rc!=0 (real failures)
        """
        if not text or text.strip() == "(no output)":
            return
        lines = text.splitlines()
        for line in lines[:max_lines]:
            self._write([
                (f"{_now_ts()} ", "ts"),
                ("    │ ", "dim"),
                (line, level),
            ])
        if len(lines) > max_lines:
            self._write([
                (f"{_now_ts()} ", "ts"),
                ("    │ ", "dim"),
                (f"... ({len(lines) - max_lines} more lines truncated)", "warn"),
            ])

    def stdio(self, stdout: str, stderr: str, ok: bool) -> None:
        """Convenience: print stdout dim, then stderr in the right colour for
        whether the overall command succeeded."""
        if stdout:
            self.output(stdout, level="dim")
        if stderr:
            self.output(stderr, level="warn" if ok else "err")

    def banner(self, text: str) -> None:
        """Big eye-catching header, like SYSTEM LOG in the screenshot."""
        self._write([(f"┌─ {text} " + "─" * max(4, 56 - len(text)) + "─┐", "head")])

    # ----- Back-compat -----
    def append(self, line: str) -> None:
        """Old API: plain timestamped line. Kept so existing callers work."""
        self.log(line, level="info")

    def clear(self) -> None:
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")
        self.separator("CLEARED")
        self.log("console cleared", level="dim")


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
        self.left_panel = left

        # Toolbar
        tools = ctk.CTkFrame(left, fg_color="transparent")
        tools.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
        tools.grid_columnconfigure(3, weight=1)
        self.tools_frame = tools
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

        # Hook for subclasses to inject extra widgets (preset bar, profile
        # card, etc.) into the just-built layout.
        self._extend_layout()

    def _extend_layout(self) -> None:
        """Subclass hook called at the end of :meth:`build`. Default no-op."""
        return None

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
            self.after(0, self.console.log, "nothing selected.", "warn")
            return

        if any(a.danger for a in chosen):
            from tkinter import messagebox
            if not messagebox.askokcancel(
                "Confirm destructive actions",
                f"{sum(1 for a in chosen if a.danger)} of {len(chosen)} actions are "
                "marked destructive (uninstall, remove, etc.). Continue?",
            ):
                self.after(0, self.console.log,
                           "user aborted at confirmation prompt.", "warn")
                return

        self.run_button.configure(state="disabled", text="Running…")
        self.status(f"Running {len(chosen)} action(s)…")

        def worker():
            self.after(0, self.console.separator,
                       f"RUN BATCH · {len(chosen)} ACTION(S)")
            ok_count = err_count = 0
            for a in chosen:
                self.after(0, self.console.action, a.title)
                self.after(0, self.console.command, a.command, a.shell)
                result: CommandResult = (
                    run_powershell(a.command) if a.shell == "powershell"
                    else run_cmd(a.command)
                )
                self.after(0, self.console.result,
                           result.ok, result.returncode, result.duration_sec)
                self.after(0, self.console.stdio, result.stdout, result.stderr, result.ok)
                if result.ok:
                    ok_count += 1
                else:
                    err_count += 1
            self.after(0, self.console.separator,
                       f"DONE · {ok_count} OK / {err_count} FAIL")
            self.after(0, self._finish_run, len(chosen))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_run(self, count: int) -> None:
        self.run_button.configure(state="normal", text="Run selected")
        self.status(f"Finished {count} action(s).")

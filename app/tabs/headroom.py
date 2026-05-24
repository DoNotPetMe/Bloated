"""Hardware Headroom — read-only diagnostic checks that print
PASS / WARN / FAIL verdicts into the terminal-style console."""
from __future__ import annotations

import threading

import customtkinter as ctk

from ._base import TabBase, OutputConsole
from ..data.headroom_data import CHECKS, CheckResult, OK, WARN, FAIL, INFO
from ..theme import COLORS, font
from ..utils.hardware import HardwareProfile, detect, reset_cache


_LEVEL_TO_TAG = {OK: "ok", WARN: "warn", FAIL: "err", INFO: "info"}


class HeadroomTab(TabBase):
    title = "Hardware Headroom"
    subtitle = (
        "Read-only diagnostics. Flags settings that are silently capping "
        "your PC (XMP off, capped CPU, TRIM disabled, old drivers, etc.) "
        "and tells you which Bloated tab fixes each one."
    )

    def build(self) -> None:
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_rowconfigure(2, weight=1)

        # ----- Top: category buttons + Run all -----
        top = ctk.CTkFrame(self.body, fg_color=COLORS["panel"],
                           corner_radius=10)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        bar = ctk.CTkFrame(top, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=14, pady=10)
        bar.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            bar, text="Run a category of checks",
            font=font(13, "bold"), text_color=COLORS["text"], anchor="w",
        ).grid(row=0, column=0, sticky="w")
        self.run_all_btn = ctk.CTkButton(
            bar, text="▶  Run all checks", height=32,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#0a0a0a", font=font(12, "bold"),
            command=lambda: self._run_checks(None),
        )
        self.run_all_btn.grid(row=0, column=1, sticky="e")

        # Categories collected from CHECKS
        cats = []
        seen = set()
        for cat, _ in CHECKS:
            if cat not in seen:
                cats.append(cat); seen.add(cat)

        catbar = ctk.CTkFrame(top, fg_color="transparent")
        catbar.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 12))
        for i in range(len(cats)):
            catbar.grid_columnconfigure(i, weight=1, uniform="c")
        for i, cat in enumerate(cats):
            ctk.CTkButton(
                catbar, text=cat, height=28,
                fg_color=COLORS["panel_alt"], hover_color=COLORS["accent"],
                text_color=COLORS["text"], font=font(11),
                command=lambda c=cat: self._run_checks(c),
            ).grid(row=0, column=i, padx=4, sticky="ew")

        # ----- Middle: profile summary -----
        self.profile_card = ctk.CTkFrame(self.body, fg_color=COLORS["panel"],
                                         corner_radius=10)
        self.profile_card.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        self.profile_card.grid_columnconfigure(0, weight=1)
        self.profile_label = ctk.CTkLabel(
            self.profile_card, text="detecting hardware…",
            font=("Cascadia Mono", 11), text_color=COLORS["text"],
            anchor="w", justify="left",
        )
        self.profile_label.grid(row=0, column=0, sticky="ew",
                                padx=14, pady=10)

        # ----- Bottom: terminal-style console -----
        self.console = OutputConsole(self.body, height=420)
        self.console.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        self.console.separator("HARDWARE HEADROOM · READY")
        self.console.log(
            "click a category or ‘Run all checks’ to begin.", "dim")

        # Kick off async hardware detection so the profile populates.
        threading.Thread(target=self._populate_profile, daemon=True).start()

    # ------------------------------------------------------------------
    def _populate_profile(self) -> None:
        prof = detect()
        text = "\n".join(f"  {k:<8} {v}" for k, v in prof.as_lines())
        self.after(0, self.profile_label.configure, {"text": text})

    # ------------------------------------------------------------------
    def _run_checks(self, category: str | None) -> None:
        """Run all checks (category=None) or only the named category."""
        targets = [
            fn for cat, fn in CHECKS
            if category is None or cat == category
        ]
        if not targets:
            self.console.log(f"no checks for category {category}", "warn")
            return
        self.run_all_btn.configure(state="disabled")
        self.console.separator(
            f"RUN · {category or 'ALL CHECKS'}  ({len(targets)} checks)")
        self.status(f"Running {len(targets)} check(s)…")

        def worker():
            # Make sure detection has run.
            prof = detect()
            counts = {OK: 0, WARN: 0, FAIL: 0, INFO: 0}
            for fn in targets:
                try:
                    res: CheckResult = fn(prof)
                except Exception as e:  # noqa: BLE001
                    res = CheckResult(
                        getattr(fn, "__name__", "check"), FAIL,
                        f"{type(e).__name__}: {e}",
                    )
                counts[res.status] = counts.get(res.status, 0) + 1
                self._report(res)
            self.after(0, self.console.separator,
                       f"DONE · {counts[OK]} OK · {counts[WARN]} WARN "
                       f"· {counts[FAIL]} FAIL · {counts[INFO]} INFO")
            self.after(0, self._finish, len(targets))

        threading.Thread(target=worker, daemon=True).start()

    def _report(self, res: CheckResult) -> None:
        tag = _LEVEL_TO_TAG.get(res.status, "info")
        self.after(0, self.console.log, f"[{res.name}] {res.message}", tag)
        if res.hint:
            self.after(0, self.console.log, f"    ↳ hint: {res.hint}", "dim")

    def _finish(self, n: int) -> None:
        self.run_all_btn.configure(state="normal")
        self.status(f"Finished {n} check(s).")

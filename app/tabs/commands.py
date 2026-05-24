"""Custom Commands tab — built-in library + user-saved commands."""
from __future__ import annotations

import json
import os
import threading
import tkinter as tk
from dataclasses import asdict
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from ._base import TabBase, OutputConsole
from ..data.commands_data import BUILTIN, SavedCommand
from ..theme import COLORS, font
from ..utils.runner import run_cmd, run_powershell


_STORE = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "Bloated" / "custom_commands.json"


def _load_custom() -> list[SavedCommand]:
    if not _STORE.exists():
        return []
    try:
        raw = json.loads(_STORE.read_text(encoding="utf-8"))
        out = []
        for it in raw:
            out.append(SavedCommand(
                name=it.get("name", ""),
                description=it.get("description", ""),
                command=it.get("command", ""),
                shell=it.get("shell", "cmd"),
                tags=tuple(it.get("tags", [])),
            ))
        return out
    except Exception:
        return []


def _save_custom(items: list[SavedCommand]) -> None:
    _STORE.parent.mkdir(parents=True, exist_ok=True)
    payload = [{**asdict(i), "tags": list(i.tags)} for i in items]
    _STORE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


class CommandsTab(TabBase):
    title = "Custom Commands"
    subtitle = ("Run useful CMD / PowerShell one-liners with full explanations. "
                "Add your own and they’ll persist between sessions.")

    def build(self) -> None:
        self.body.grid_columnconfigure(0, weight=2)
        self.body.grid_columnconfigure(1, weight=3)
        self.body.grid_rowconfigure(0, weight=1)

        self._custom: list[SavedCommand] = _load_custom()

        # ----- Left: list -----
        left = ctk.CTkFrame(self.body, fg_color=COLORS["panel"], corner_radius=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(left, text="Command library", font=font(13, "bold"),
                     text_color=COLORS["text"], anchor="w").grid(
            row=0, column=0, sticky="ew", padx=14, pady=(10, 0))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._refresh_list())
        ctk.CTkEntry(left, placeholder_text="Filter…",
                     textvariable=self.search_var, height=30,
                     fg_color=COLORS["bg"], border_color=COLORS["border"],
                     ).grid(row=1, column=0, sticky="ew", padx=10, pady=8)

        self.list_frame = ctk.CTkScrollableFrame(
            left, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"],
        )
        self.list_frame.grid(row=2, column=0, sticky="nsew", padx=6, pady=(0, 8))
        self.list_frame.grid_columnconfigure(0, weight=1)

        # Buttons
        btns = ctk.CTkFrame(left, fg_color="transparent")
        btns.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        btns.grid_columnconfigure(0, weight=1)
        btns.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(btns, text="+ New command", height=32,
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      text_color="#0a0a0a", font=font(12, "bold"),
                      command=self._new_command).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ctk.CTkButton(btns, text="Delete selected", height=32,
                      fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
                      command=self._delete_selected).grid(row=0, column=1, sticky="ew", padx=(4, 0))

        # ----- Right: details + run -----
        right = ctk.CTkFrame(self.body, fg_color=COLORS["panel"], corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(3, weight=1)

        self.name_var = tk.StringVar(value="")
        self.shell_var = tk.StringVar(value="cmd")

        header = ctk.CTkFrame(right, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkEntry(header, textvariable=self.name_var, height=34,
                     fg_color=COLORS["bg"], border_color=COLORS["border"],
                     placeholder_text="Command name").grid(
            row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkSegmentedButton(header, variable=self.shell_var,
                               values=["cmd", "powershell"],
                               fg_color=COLORS["bg"],
                               selected_color=COLORS["accent"],
                               selected_hover_color=COLORS["accent_hover"],
                               unselected_color=COLORS["panel_alt"],
                               unselected_hover_color=COLORS["border"],
                               ).grid(row=0, column=1)

        ctk.CTkLabel(right, text="Description", font=font(11, "bold"),
                     text_color=COLORS["text_dim"], anchor="w").grid(
            row=1, column=0, sticky="ew", padx=14)
        self.desc_box = ctk.CTkTextbox(right, height=70,
                                       fg_color=COLORS["bg"], text_color=COLORS["text"],
                                       border_color=COLORS["border"], border_width=1,
                                       font=font(11), wrap="word")
        self.desc_box.grid(row=2, column=0, sticky="ew", padx=14, pady=(2, 8))

        ctk.CTkLabel(right, text="Command", font=font(11, "bold"),
                     text_color=COLORS["text_dim"], anchor="w").grid(
            row=3, column=0, sticky="nw", padx=14)
        self.cmd_box = ctk.CTkTextbox(right, height=90,
                                      fg_color=COLORS["bg"], text_color=COLORS["text"],
                                      border_color=COLORS["border"], border_width=1,
                                      font=("Consolas", 11), wrap="none")
        self.cmd_box.grid(row=4, column=0, sticky="nsew", padx=14, pady=(2, 8))
        right.grid_rowconfigure(4, weight=1)

        actions = ctk.CTkFrame(right, fg_color="transparent")
        actions.grid(row=5, column=0, sticky="ew", padx=14, pady=(0, 8))
        actions.grid_columnconfigure(3, weight=1)
        ctk.CTkButton(actions, text="▶ Run", height=34, width=110,
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      text_color="#0a0a0a", font=font(12, "bold"),
                      command=self._run_current).grid(row=0, column=0, padx=(0, 6))
        ctk.CTkButton(actions, text="Save changes", height=34, width=120,
                      fg_color=COLORS["panel_alt"], hover_color=COLORS["border"],
                      command=self._save_current).grid(row=0, column=1, padx=(0, 6))
        ctk.CTkButton(actions, text="Copy command", height=34, width=120,
                      fg_color=COLORS["panel_alt"], hover_color=COLORS["border"],
                      command=self._copy_cmd).grid(row=0, column=2)

        self.console = OutputConsole(right, height=180)
        self.console.grid(row=6, column=0, sticky="nsew", padx=14, pady=(0, 14))

        self._selected_key: str | None = None
        self._refresh_list()
        if self._all_items():
            self._select(self._all_items()[0][0])

    # ------------------------------------------------------------------

    def _all_items(self) -> list[tuple[str, SavedCommand, bool]]:
        out: list[tuple[str, SavedCommand, bool]] = []
        for i, c in enumerate(BUILTIN):
            out.append((f"b:{i}", c, False))
        for i, c in enumerate(self._custom):
            out.append((f"u:{i}", c, True))
        return out

    def _find(self, key: str) -> SavedCommand | None:
        for k, c, _ in self._all_items():
            if k == key:
                return c
        return None

    def _refresh_list(self) -> None:
        for w in list(self.list_frame.children.values()):
            w.destroy()
        q = self.search_var.get().strip().lower()
        row = 0
        for key, cmd, is_user in self._all_items():
            if q and q not in cmd.name.lower() and q not in cmd.description.lower():
                continue
            card = ctk.CTkFrame(
                self.list_frame,
                fg_color=(COLORS["accent"] if key == self._selected_key
                          else COLORS["panel_alt"]),
                corner_radius=8,
            )
            card.grid(row=row, column=0, sticky="ew", padx=4, pady=3)
            card.grid_columnconfigure(0, weight=1)

            badge = " ✱" if is_user else ""
            ctk.CTkLabel(
                card, text=cmd.name + badge, anchor="w",
                text_color=("#0a0a0a" if key == self._selected_key else COLORS["text"]),
                font=font(12, "bold"),
            ).grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 0))
            ctk.CTkLabel(
                card,
                text=f"[{cmd.shell}] {cmd.description[:80]}{'…' if len(cmd.description) > 80 else ''}",
                anchor="w",
                text_color=("#0a0a0a" if key == self._selected_key else COLORS["text_dim"]),
                font=font(10),
            ).grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))
            card.bind("<Button-1>", lambda _e, k=key: self._select(k))
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda _e, k=key: self._select(k))
            row += 1

    def _select(self, key: str) -> None:
        cmd = self._find(key)
        if not cmd:
            return
        self._selected_key = key
        self.name_var.set(cmd.name)
        self.shell_var.set(cmd.shell)
        self.desc_box.delete("1.0", "end")
        self.desc_box.insert("1.0", cmd.description)
        self.cmd_box.delete("1.0", "end")
        self.cmd_box.insert("1.0", cmd.command)
        self._refresh_list()

    # ------------------------------------------------------------------

    def _new_command(self) -> None:
        new = SavedCommand("New command", "Describe what this does.",
                           "echo hello", "cmd", ())
        self._custom.append(new)
        _save_custom(self._custom)
        key = f"u:{len(self._custom) - 1}"
        self._refresh_list()
        self._select(key)
        self.status("New command created.")

    def _delete_selected(self) -> None:
        if not self._selected_key or not self._selected_key.startswith("u:"):
            messagebox.showinfo("Cannot delete", "Built-in commands cannot be deleted.")
            return
        idx = int(self._selected_key.split(":")[1])
        if not messagebox.askokcancel("Delete", f"Delete ‘{self._custom[idx].name}’?"):
            return
        del self._custom[idx]
        _save_custom(self._custom)
        self._selected_key = None
        self.name_var.set("")
        self.desc_box.delete("1.0", "end")
        self.cmd_box.delete("1.0", "end")
        self._refresh_list()

    def _save_current(self) -> None:
        if not self._selected_key:
            return
        cmd = SavedCommand(
            name=self.name_var.get().strip() or "(untitled)",
            description=self.desc_box.get("1.0", "end").strip(),
            command=self.cmd_box.get("1.0", "end").strip(),
            shell=self.shell_var.get(),
            tags=(),
        )
        if self._selected_key.startswith("u:"):
            idx = int(self._selected_key.split(":")[1])
            self._custom[idx] = cmd
            _save_custom(self._custom)
            self.status("Saved.")
        else:
            # Built-in: clone into custom
            self._custom.append(cmd)
            _save_custom(self._custom)
            self._selected_key = f"u:{len(self._custom) - 1}"
            self.status("Built-in cloned to your custom library.")
        self._refresh_list()

    def _copy_cmd(self) -> None:
        text = self.cmd_box.get("1.0", "end").strip()
        if not text:
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self.status("Command copied to clipboard.")

    def _run_current(self) -> None:
        text = self.cmd_box.get("1.0", "end").strip()
        if not text:
            self.console.log("no command in editor", "warn")
            return
        shell = self.shell_var.get()
        name = self.name_var.get().strip() or "(untitled)"
        self.console.action(name)
        self.console.command(text, shell)

        def worker():
            r = run_powershell(text) if shell == "powershell" else run_cmd(text)
            self.after(0, self.console.result, r.ok, r.returncode)
            self.after(0, self.console.stdio, r.stdout, r.stderr, r.ok)
        threading.Thread(target=worker, daemon=True).start()

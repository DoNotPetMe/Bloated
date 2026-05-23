"""Pure-data models shared by data/ modules and tab UI.

Kept separate from `_base` so that data files (and unit tests) don’t need
tkinter just to enumerate their action lists.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Action:
    """One toggleable action exposed in an ActionListTab."""
    title: str
    description: str
    command: str
    shell: str = "powershell"   # "powershell" or "cmd"
    category: str = "General"
    danger: bool = False
    enabled_by_default: bool = False

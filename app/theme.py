"""Centralised colour palette + CustomTkinter appearance setup."""
from __future__ import annotations

import customtkinter as ctk

# Palette — modern dark, accent cyan/teal
COLORS = {
    "bg":            "#0F1116",  # window background
    "panel":         "#161A22",  # cards
    "panel_alt":     "#1C2230",  # alt rows / hover
    "border":        "#2A3142",
    "text":          "#E6EAF2",
    "text_dim":      "#8B93A7",
    "accent":        "#3BD4C7",  # primary accent (teal)
    "accent_hover":  "#2BB4A8",
    "warn":          "#F0B429",
    "danger":        "#E5484D",
    "danger_hover":  "#C53438",
    "ok":            "#46C57F",
    "sidebar":       "#0B0D12",
}

FONT_FAMILY = "Segoe UI"


def apply_theme() -> None:
    """Apply global CustomTkinter appearance settings."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")


def font(size: int = 13, weight: str = "normal") -> tuple:
    return (FONT_FAMILY, size, weight)

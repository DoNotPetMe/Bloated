"""Rotating file + console logger."""
from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "Bloated" / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)
_LOG_FILE = _LOG_DIR / "bloated.log"

_FMT = logging.Formatter(
    "%(asctime)s [%(levelname)-7s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_configured = False


def _configure() -> None:
    global _configured
    if _configured:
        return
    root = logging.getLogger("bloated")
    root.setLevel(logging.DEBUG)

    fh = RotatingFileHandler(_LOG_FILE, maxBytes=512 * 1024, backupCount=4, encoding="utf-8")
    fh.setFormatter(_FMT)
    fh.setLevel(logging.DEBUG)
    root.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(_FMT)
    ch.setLevel(logging.INFO)
    root.addHandler(ch)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    _configure()
    return logging.getLogger(f"bloated.{name}")


def log_path() -> Path:
    return _LOG_FILE

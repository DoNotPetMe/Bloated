"""
Bloated — Windows PC Powerhouse
Entry point.
"""
from __future__ import annotations

import sys
import traceback

try:
    import customtkinter as ctk  # noqa: F401
except ImportError:
    print("CustomTkinter is not installed. Run install.bat or:")
    print("    python -m pip install -r requirements.txt")
    sys.exit(1)

from app.main_window import MainWindow
from app.utils.logger import get_logger


def main() -> int:
    log = get_logger("main")
    log.info("Starting Bloated")
    try:
        app = MainWindow()
        app.mainloop()
    except Exception:
        log.error("Fatal: %s", traceback.format_exc())
        raise
    log.info("Bloated exited cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())

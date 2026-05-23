"""Thin safe wrapper around the Windows registry."""
from __future__ import annotations

from typing import Optional, Union

from .logger import get_logger
from .admin import is_windows

log = get_logger("registry")

if is_windows():
    import winreg  # type: ignore
else:
    winreg = None  # type: ignore


_HIVES = {
    "HKCU": "HKEY_CURRENT_USER",
    "HKLM": "HKEY_LOCAL_MACHINE",
    "HKCR": "HKEY_CLASSES_ROOT",
    "HKU":  "HKEY_USERS",
    "HKCC": "HKEY_CURRENT_CONFIG",
}


def _resolve_hive(name: str):
    full = _HIVES.get(name.upper(), name.upper())
    return getattr(winreg, full)


def reg_set(hive: str, path: str, name: str, value: Union[int, str], kind: str = "DWORD") -> bool:
    """Create the key path if missing, then set the value."""
    if not is_windows():
        log.warning("reg_set called on non-Windows: %s\\%s\\%s = %r", hive, path, name, value)
        return False
    try:
        root = _resolve_hive(hive)
        with winreg.CreateKeyEx(root, path, 0, winreg.KEY_SET_VALUE) as k:
            t = getattr(winreg, f"REG_{kind}")
            winreg.SetValueEx(k, name, 0, t, value)
        return True
    except Exception:
        log.exception("reg_set failed %s\\%s\\%s", hive, path, name)
        return False


def reg_get(hive: str, path: str, name: str) -> Optional[Union[int, str]]:
    if not is_windows():
        return None
    try:
        root = _resolve_hive(hive)
        with winreg.OpenKeyEx(root, path, 0, winreg.KEY_READ) as k:
            val, _ = winreg.QueryValueEx(k, name)
            return val
    except FileNotFoundError:
        return None
    except Exception:
        log.exception("reg_get failed %s\\%s\\%s", hive, path, name)
        return None


def reg_delete_value(hive: str, path: str, name: str) -> bool:
    if not is_windows():
        return False
    try:
        root = _resolve_hive(hive)
        with winreg.OpenKeyEx(root, path, 0, winreg.KEY_SET_VALUE) as k:
            winreg.DeleteValue(k, name)
        return True
    except FileNotFoundError:
        return True
    except Exception:
        log.exception("reg_delete_value failed %s\\%s\\%s", hive, path, name)
        return False

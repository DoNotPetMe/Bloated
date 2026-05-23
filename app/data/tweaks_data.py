"""Quality-of-life registry tweaks for Explorer / taskbar / shell."""
from __future__ import annotations

from ..tabs._models import Action


def _reg(hive, path, name, val, kind="DWORD"):
    if kind == "DWORD":
        return f'reg add "{hive}\\{path}" /v "{name}" /t REG_DWORD /d {int(val)} /f'
    return f'reg add "{hive}\\{path}" /v "{name}" /t REG_SZ /d "{val}" /f'


_EXPLORER_ADV = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"


ACTIONS: list[Action] = [
    Action(
        title="Show file extensions",
        description="Always show .exe, .txt, etc. — protects you from double-extension trickery.",
        command=_reg("HKCU", _EXPLORER_ADV, "HideFileExt", 0),
        shell="cmd",
        category="Explorer",
        enabled_by_default=True,
    ),
    Action(
        title="Show hidden files & folders",
        description="Reveals hidden items in Explorer.",
        command=_reg("HKCU", _EXPLORER_ADV, "Hidden", 1),
        shell="cmd",
        category="Explorer",
        enabled_by_default=True,
    ),
    Action(
        title="Show full path in title bar",
        description="Explorer title shows the full folder path.",
        command=_reg(
            "HKCU",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\CabinetState",
            "FullPath", 1),
        shell="cmd",
        category="Explorer",
        enabled_by_default=False,
    ),
    Action(
        title="Enable verbose status messages at logon",
        description="Shows what Windows is actually doing during startup/shutdown.",
        command=_reg("HKLM",
                     r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
                     "VerboseStatus", 1),
        shell="cmd",
        category="System",
        enabled_by_default=False,
    ),
    Action(
        title="Disable Lock Screen (go straight to login)",
        description="Skips the swipe/click lock screen before sign-in.",
        command=_reg("HKLM",
                     r"SOFTWARE\Policies\Microsoft\Windows\Personalization",
                     "NoLockScreen", 1),
        shell="cmd",
        category="System",
        enabled_by_default=False,
    ),
    Action(
        title="Restore classic right-click menu (Windows 11)",
        description="Brings back the W10-style full context menu, no ‘Show more options’.",
        command=(
            'reg add "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32" /f /ve'
        ),
        shell="cmd",
        category="Windows 11",
        enabled_by_default=True,
    ),
    Action(
        title="Align taskbar to the left (W11)",
        description="Moves Start + apps to the left like Windows 10.",
        command=_reg("HKCU", _EXPLORER_ADV, "TaskbarAl", 0),
        shell="cmd",
        category="Windows 11",
        enabled_by_default=False,
    ),
    Action(
        title="Disable Widgets / News & Interests",
        description="Hides the weather/news widgets pane on the taskbar.",
        command=_reg("HKCU", _EXPLORER_ADV, "TaskbarDa", 0),
        shell="cmd",
        category="Windows 11",
        enabled_by_default=True,
    ),
    Action(
        title="Disable Chat (Teams) icon",
        description="Removes the Teams Consumer chat button from the taskbar.",
        command=_reg("HKCU", _EXPLORER_ADV, "TaskbarMn", 0),
        shell="cmd",
        category="Windows 11",
        enabled_by_default=True,
    ),
    Action(
        title="Enable ‘End Task’ in taskbar right-click",
        description="Adds an End Task option directly to taskbar context menus.",
        command=_reg(
            "HKCU",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\TaskbarDeveloperSettings",
            "TaskbarEndTask", 1),
        shell="cmd",
        category="Windows 11",
        enabled_by_default=True,
    ),
    Action(
        title="Show seconds in system clock",
        description="Adds seconds to the taskbar clock.",
        command=_reg("HKCU", _EXPLORER_ADV, "ShowSecondsInSystemClock", 1),
        shell="cmd",
        category="Windows 11",
        enabled_by_default=False,
    ),
    Action(
        title="Enable Dark Mode (apps + system)",
        description="Switches Windows + apps to dark theme.",
        command=(
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                 "AppsUseLightTheme", 0) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                 "SystemUsesLightTheme", 0)
        ),
        shell="cmd",
        category="Appearance",
        enabled_by_default=True,
    ),
    Action(
        title="Disable Transparency Effects",
        description="Speeds up older GPUs, removes acrylic blur.",
        command=_reg("HKCU",
                     r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                     "EnableTransparency", 0),
        shell="cmd",
        category="Appearance",
        enabled_by_default=False,
    ),
    Action(
        title="Disable Animations",
        description=("Turns off most window minimise/maximise/menu animations "
                     "— often a noticeable snappiness boost."),
        command=(
            _reg("HKCU", r"Control Panel\Desktop\WindowMetrics",
                 "MinAnimate", "0", kind="SZ") + " & " +
            'reg add "HKCU\\Control Panel\\Desktop" /v UserPreferencesMask '
            '/t REG_BINARY /d 9012038010000000 /f'
        ),
        shell="cmd",
        category="Appearance",
        enabled_by_default=False,
    ),
    Action(
        title="Restart Explorer (apply changes)",
        description="Closes and re-opens Explorer so the above tweaks take effect immediately.",
        command="taskkill /f /im explorer.exe & start explorer.exe",
        shell="cmd",
        category="Apply",
        enabled_by_default=True,
    ),
]

"""Quality-of-life registry tweaks for Explorer, taskbar, theme, etc.

These are all reversible and none of them touch anything dangerous — they
just adjust user-interface defaults that Microsoft chose for you.
"""
from __future__ import annotations

from ..tabs._models import Action


def _reg(hive, path, name, val, kind="DWORD"):
    if kind == "DWORD":
        return f'reg add "{hive}\\{path}" /v "{name}" /t REG_DWORD /d {int(val)} /f'
    return f'reg add "{hive}\\{path}" /v "{name}" /t REG_SZ /d "{val}" /f'


_EXPLORER_ADV = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"


ACTIONS: list[Action] = [
    # ── Explorer ────────────────────────────────────────────────────────────
    Action(
        title="Always show file extensions (.exe, .txt, .pdf…)",
        description=(
            "Windows hides file extensions by default, which makes it easy "
            "for malware to disguise itself (‘invoice.pdf.exe’ shows as "
            "‘invoice.pdf’). Turning extensions on is a basic security "
            "hardening step everyone should take."),
        command=_reg("HKCU", _EXPLORER_ADV, "HideFileExt", 0),
        shell="cmd",
        category="Explorer",
        enabled_by_default=True,
    ),
    Action(
        title="Show hidden files & folders",
        description=(
            "Reveals files / folders the system normally hides (AppData, "
            ".git, .vscode, etc.). Mostly useful for power users and devs."),
        command=_reg("HKCU", _EXPLORER_ADV, "Hidden", 1),
        shell="cmd",
        category="Explorer",
        enabled_by_default=True,
    ),
    Action(
        title="Show protected system files",
        description=(
            "Goes one step further than ‘hidden’ — shows the protected OS "
            "files Microsoft normally hides even from advanced users. Useful "
            "for troubleshooting; usually fine to leave off."),
        command=_reg("HKCU", _EXPLORER_ADV, "ShowSuperHidden", 1),
        shell="cmd",
        category="Explorer",
        enabled_by_default=False,
    ),
    Action(
        title="Show full path in Explorer title bar",
        description=(
            "Instead of just the folder name (‘Downloads’), Explorer shows "
            "the full path (‘C:\\Users\\you\\Downloads’) in its title bar."),
        command=_reg(
            "HKCU",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\CabinetState",
            "FullPath", 1),
        shell="cmd",
        category="Explorer",
        enabled_by_default=False,
    ),
    Action(
        title="Open Explorer to ‘This PC’ instead of ‘Home/Quick Access’",
        description=(
            "Opens a fresh Explorer window directly to the drive list "
            "instead of the Recent / Quick Access screen. Less clutter."),
        command=_reg("HKCU", _EXPLORER_ADV, "LaunchTo", 1),
        shell="cmd",
        category="Explorer",
        enabled_by_default=False,
    ),
    Action(
        title="Disable Explorer ‘recent files’ list",
        description=(
            "Stops Explorer from tracking which files you’ve recently "
            "opened and showing them in Quick Access / jump lists."),
        command=(
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer",
                 "ShowRecent", 0) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer",
                 "ShowFrequent", 0)
        ),
        shell="cmd",
        category="Explorer",
        enabled_by_default=False,
    ),

    # ── Windows 11 specifics ────────────────────────────────────────────────
    Action(
        title="Restore the classic right-click menu (Windows 11)",
        description=(
            "Windows 11 hides half of the right-click menu behind a ‘Show "
            "more options’ click. This tweak brings back the full Windows-10 "
            "context menu in one step. Reverse with the ‘Revert classic "
            "right-click menu’ action below."),
        command=(
            'reg add "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32" /f /ve'
        ),
        shell="cmd",
        category="Windows 11",
        enabled_by_default=True,
    ),
    Action(
        title="Revert classic right-click menu (back to W11 default)",
        description=(
            "Undoes the previous tweak — context menus go back to the "
            "‘Show more options’ submenu style."),
        command=(
            'reg delete "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" /f'
        ),
        shell="cmd",
        category="Windows 11",
        enabled_by_default=False,
    ),
    Action(
        title="Align taskbar to the left (Windows 11)",
        description=(
            "Moves Start + pinned apps to the left edge of the taskbar, "
            "Windows-10 style. Reverse: set TaskbarAl back to 1."),
        command=_reg("HKCU", _EXPLORER_ADV, "TaskbarAl", 0),
        shell="cmd",
        category="Windows 11",
        enabled_by_default=False,
    ),
    Action(
        title="Hide Widgets / News & Interests button",
        description=(
            "Removes the weather/news/sports widgets button from the "
            "taskbar. Frees a few inches of taskbar real estate."),
        command=_reg("HKCU", _EXPLORER_ADV, "TaskbarDa", 0),
        shell="cmd",
        category="Windows 11",
        enabled_by_default=True,
    ),
    Action(
        title="Hide Chat (Teams Consumer) icon",
        description=(
            "Removes the purple Chat button from the taskbar (the Teams "
            "consumer one that nobody uses). Doesn’t touch the actual Teams "
            "desktop app if you have one installed."),
        command=_reg("HKCU", _EXPLORER_ADV, "TaskbarMn", 0),
        shell="cmd",
        category="Windows 11",
        enabled_by_default=True,
    ),
    Action(
        title="Hide Search button on taskbar (icon only / off)",
        description=(
            "Replaces the big search box with a small search icon. Setting "
            "this value to 0 hides search entirely, 1 = icon, 2 = box."),
        command=_reg(
            "HKCU",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
            "SearchboxTaskbarMode", 1),
        shell="cmd",
        category="Windows 11",
        enabled_by_default=True,
    ),
    Action(
        title="Add ‘End task’ to taskbar right-click",
        description=(
            "Adds an End Task option directly when you right-click an app "
            "on the taskbar, so you don’t need to open Task Manager to "
            "kill a frozen window."),
        command=_reg(
            "HKCU",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\TaskbarDeveloperSettings",
            "TaskbarEndTask", 1),
        shell="cmd",
        category="Windows 11",
        enabled_by_default=True,
    ),
    Action(
        title="Never combine taskbar buttons (W11 22H2+)",
        description=(
            "Each open window gets its own taskbar button with a label — "
            "the old Windows 10/7 style. Setting MMTaskbarGlomLevel=2."),
        command=(
            _reg("HKCU", _EXPLORER_ADV, "TaskbarGlomLevel", 2) + " & " +
            _reg("HKCU", _EXPLORER_ADV, "MMTaskbarGlomLevel", 2)
        ),
        shell="cmd",
        category="Windows 11",
        enabled_by_default=False,
    ),
    Action(
        title="Show seconds in taskbar clock",
        description=(
            "Adds seconds to the system tray clock. Slightly increases "
            "background CPU on very old hardware; on anything modern it "
            "doesn’t matter."),
        command=_reg("HKCU", _EXPLORER_ADV, "ShowSecondsInSystemClock", 1),
        shell="cmd",
        category="Windows 11",
        enabled_by_default=False,
    ),

    # ── Appearance ──────────────────────────────────────────────────────────
    Action(
        title="Enable Dark Mode (apps + system)",
        description=(
            "Switches both the system shell and modern apps to their dark "
            "theme. Doesn’t affect classic Win32 apps (those depend on the "
            "app itself)."),
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
        title="Enable Light Mode",
        description=(
            "Flips the same two switches the other way. Use this if you "
            "applied Dark Mode and want to revert."),
        command=(
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                 "AppsUseLightTheme", 1) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                 "SystemUsesLightTheme", 1)
        ),
        shell="cmd",
        category="Appearance",
        enabled_by_default=False,
    ),
    Action(
        title="Disable Transparency / Acrylic blur",
        description=(
            "Removes the frosted-glass effect on Start, taskbar and menus. "
            "Looks more boring but saves a noticeable amount of GPU work on "
            "older / integrated graphics."),
        command=_reg("HKCU",
                     r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                     "EnableTransparency", 0),
        shell="cmd",
        category="Appearance",
        enabled_by_default=False,
    ),
    Action(
        title="Adjust visual effects for ‘best performance’",
        description=(
            "Equivalent of going into ‘Adjust the appearance and "
            "performance of Windows → Adjust for best performance’. Turns "
            "off almost every animation; UI looks like Win 2000 but feels "
            "snappier on slow PCs."),
        command=_reg(
            "HKCU",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
            "VisualFXSetting", 2),
        shell="cmd",
        category="Appearance",
        enabled_by_default=False,
    ),
    Action(
        title="Disable window minimise/maximise animations",
        description=(
            "Turns off just the window-minimise / restore animations. Other "
            "animations stay. Makes the desktop feel a little faster without "
            "going full ‘Adjust for best performance’."),
        command=(
            _reg("HKCU", r"Control Panel\Desktop\WindowMetrics",
                 "MinAnimate", "0", kind="SZ")
        ),
        shell="cmd",
        category="Appearance",
        enabled_by_default=False,
    ),

    # ── System / Misc ───────────────────────────────────────────────────────
    Action(
        title="Show verbose status messages at logon",
        description=(
            "Replaces ‘Welcome’ / ‘Please wait’ on startup and shutdown "
            "with the actual operation Windows is performing. Helpful for "
            "diagnosing slow logins."),
        command=_reg(
            "HKLM",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
            "VerboseStatus", 1),
        shell="cmd",
        category="System",
        enabled_by_default=False,
    ),
    Action(
        title="Skip the Lock Screen (go straight to sign-in)",
        description=(
            "Removes the swipe-up / click-anywhere lock screen so you go "
            "straight to the password prompt. Saves one click on every "
            "wake."),
        command=_reg(
            "HKLM",
            r"SOFTWARE\Policies\Microsoft\Windows\Personalization",
            "NoLockScreen", 1),
        shell="cmd",
        category="System",
        enabled_by_default=False,
    ),
    Action(
        title="Enable long file path support (>260 chars)",
        description=(
            "Removes the legacy 260-character path limit. Required for some "
            "modern dev workflows (Node/Python projects with deep "
            "node_modules). Apps must opt in to use it, but most modern "
            "ones do."),
        command=_reg(
            "HKLM",
            r"SYSTEM\CurrentControlSet\Control\FileSystem",
            "LongPathsEnabled", 1),
        shell="cmd",
        category="System",
        enabled_by_default=False,
    ),
    Action(
        title="Disable Sticky Keys prompt (5×Shift)",
        description=(
            "Stops the annoying ‘Do you want to turn on Sticky Keys?’ "
            "popup when you tap Shift five times in a row — common during "
            "gaming."),
        command=_reg(
            "HKCU", r"Control Panel\Accessibility\StickyKeys",
            "Flags", "506", kind="SZ"),
        shell="cmd",
        category="System",
        enabled_by_default=False,
    ),
    Action(
        title="Show ‘This PC’ on the Desktop",
        description=(
            "Adds the This PC, Recycle Bin, User folder and Network icons "
            "back to the desktop, like Windows XP/7."),
        command=(
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel",
                 "{20D04FE0-3AEA-1069-A2D8-08002B30309D}", 0) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel",
                 "{59031a47-3f72-44a7-89c5-5595fe6b30ee}", 0) + " & " +
            _reg("HKCU",
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel",
                 "{645FF040-5081-101B-9F08-00AA002F954E}", 0)
        ),
        shell="cmd",
        category="System",
        enabled_by_default=False,
    ),
    Action(
        title="Re-enable old-style F8 boot menu",
        description=(
            "Restores the F8 ‘Advanced Boot Options’ menu from XP/7. Useful "
            "if you ever need Safe Mode on a PC that refuses to boot all "
            "the way to the recovery environment."),
        command="bcdedit /set {default} bootmenupolicy legacy",
        shell="cmd",
        category="System",
        enabled_by_default=False,
    ),

    # ── Apply ───────────────────────────────────────────────────────────────
    Action(
        title="Restart Explorer (apply all changes above)",
        description=(
            "Closes Explorer and re-launches it so the registry tweaks "
            "above take effect immediately, without needing a sign-out."),
        command="taskkill /f /im explorer.exe & start explorer.exe",
        shell="cmd",
        category="Apply",
        enabled_by_default=True,
    ),
]

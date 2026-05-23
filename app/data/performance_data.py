"""Performance / power related tweaks."""
from __future__ import annotations

from ..tabs._models import Action


ACTIONS: list[Action] = [
    Action(
        title="Activate High Performance power plan",
        description="Switches the active power plan to the built-in High Performance plan.",
        command="powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
        shell="cmd",
        category="Power",
        enabled_by_default=False,
    ),
    Action(
        title="Reveal & activate Ultimate Performance",
        description=(
            "Duplicates the hidden Ultimate Performance plan (workstation SKUs) "
            "and makes it active. Best for desktops on AC power."),
        command=(
            "powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 & "
            "powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61"
        ),
        shell="cmd",
        category="Power",
        enabled_by_default=False,
    ),
    Action(
        title="Disable USB selective suspend",
        description="Stops Windows suspending idle USB devices (fixes flaky mice/audio).",
        command=(
            "powercfg /setacvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 "
            "48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0 & "
            "powercfg /setactive SCHEME_CURRENT"
        ),
        shell="cmd",
        category="Power",
        enabled_by_default=False,
    ),
    Action(
        title="Disable Hibernation",
        description="Removes hiberfil.sys (frees several GB on the system drive).",
        command="powercfg /h off",
        shell="cmd",
        category="Power",
        enabled_by_default=False,
    ),
    Action(
        title="Enable Game Mode",
        description="Prioritises CPU/GPU for the foreground game.",
        command='reg add "HKCU\\Software\\Microsoft\\GameBar" /v AllowAutoGameMode /t REG_DWORD /d 1 /f',
        shell="cmd",
        category="Gaming",
        enabled_by_default=True,
    ),
    Action(
        title="Enable Hardware-Accelerated GPU Scheduling",
        description="HAGS — reduces CPU overhead on supported GPUs. Reboot required.",
        command=(
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" '
            '/v HwSchMode /t REG_DWORD /d 2 /f'
        ),
        shell="cmd",
        category="Gaming",
        enabled_by_default=False,
    ),
    Action(
        title="Adjust visual effects → best performance",
        description="Sets the classic ‘Adjust for best performance’ option in SystemPropertiesPerformance.",
        command='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f',
        shell="cmd",
        category="UI",
        enabled_by_default=False,
    ),
    Action(
        title="Show MsConfig (System Configuration)",
        description="Opens msconfig.exe for manual boot/services tweaking.",
        command="msconfig",
        shell="cmd",
        category="Tools",
        enabled_by_default=False,
    ),
    Action(
        title="Show Task Manager → Startup tab",
        description="Opens Task Manager so you can disable startup programs.",
        command="taskmgr /0 /startup",
        shell="cmd",
        category="Tools",
        enabled_by_default=False,
    ),
]

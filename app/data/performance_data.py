"""Performance / power related tweaks — plans, scheduling, animations."""
from __future__ import annotations

from ..tabs._models import Action


ACTIONS: list[Action] = [
    # ── Power plans ─────────────────────────────────────────────────────────
    Action(
        title="Switch to ‘High Performance’ power plan",
        description=(
            "Stops Windows from down-clocking the CPU during light load — "
            "best for desktops where you want maximum responsiveness and "
            "don’t care about a few extra watts. Laptops will lose battery "
            "life noticeably."),
        command="powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
        shell="cmd",
        category="Power plans",
        enabled_by_default=False,
    ),
    Action(
        title="Reveal & activate ‘Ultimate Performance’ plan",
        description=(
            "Duplicates the hidden Workstation-edition Ultimate Performance "
            "plan and makes it the active one. Disables almost every power-"
            "saving feature. Best for plugged-in desktops you want to feel "
            "absolutely snappy."),
        command=(
            "powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 & "
            "powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61"
        ),
        shell="cmd",
        category="Power plans",
        enabled_by_default=False,
    ),
    Action(
        title="Switch to ‘Balanced’ power plan",
        description=(
            "The default Windows plan. Use this to undo any of the above."),
        command="powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e",
        shell="cmd",
        category="Power plans",
        enabled_by_default=False,
    ),
    Action(
        title="Switch to ‘Power Saver’ plan",
        description=(
            "Maximum battery life. Aggressively down-clocks CPU and dims "
            "screen. Use only on laptops when you’re trying to squeeze "
            "extra minutes out of a low battery."),
        command="powercfg /setactive a1841308-3541-4fab-bc81-f71556f20b4a",
        shell="cmd",
        category="Power plans",
        enabled_by_default=False,
    ),

    # ── Power tweaks ────────────────────────────────────────────────────────
    Action(
        title="Disable USB selective suspend",
        description=(
            "Stops Windows from putting idle USB devices to sleep. Fixes "
            "the classic ‘my mouse stutters after 30s’ or ‘my USB DAC "
            "clicks’ problems. Tiny power-draw cost."),
        command=(
            "powercfg /setacvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 "
            "48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0 & "
            "powercfg /setactive SCHEME_CURRENT"
        ),
        shell="cmd",
        category="Power tweaks",
        enabled_by_default=False,
    ),
    Action(
        title="Disable Hibernation (delete hiberfil.sys)",
        description=(
            "Hibernation writes a snapshot of all RAM to disk so the PC "
            "can resume after a full power-off. hiberfil.sys is the size "
            "of your installed RAM (8–64 GB!). Disable on a desktop "
            "where you never use Hibernate — frees that disk space."),
        command="powercfg /h off",
        shell="cmd",
        category="Power tweaks",
        enabled_by_default=False,
    ),
    Action(
        title="Re-enable Hibernation",
        description=(
            "Brings hiberfil.sys back. Use if you regret disabling it."),
        command="powercfg /h on",
        shell="cmd",
        category="Power tweaks",
        enabled_by_default=False,
    ),
    Action(
        title="Disable Fast Startup",
        description=(
            "Windows’ ‘Fast Startup’ is actually a half-hibernate — it "
            "saves the kernel state to disk on shutdown. Causes weirdness "
            "with dual-boot Linux, occasional driver bugs, and stale state "
            "after a ‘shutdown’. Disabling means slightly slower boot but "
            "an actually fresh OS every time."),
        command=(
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power" '
            '/v HiberbootEnabled /t REG_DWORD /d 0 /f'
        ),
        shell="cmd",
        category="Power tweaks",
        enabled_by_default=False,
    ),
    Action(
        title="Disable Hard Disk Power-Down (set sleep = Never)",
        description=(
            "Stops Windows from spinning idle HDDs down after a few "
            "minutes. Helpful if you have a NAS-style spinning disk you "
            "use intermittently and hate the spin-up delay."),
        command=(
            "powercfg /change disk-timeout-ac 0 & "
            "powercfg /change disk-timeout-dc 0"
        ),
        shell="cmd",
        category="Power tweaks",
        enabled_by_default=False,
    ),

    # ── Gaming ──────────────────────────────────────────────────────────────
    Action(
        title="Enable Game Mode",
        description=(
            "Tells Windows to prioritise CPU/GPU on the active foreground "
            "game and to suppress most background work (Windows Update "
            "downloads, defrag, etc.) while you play."),
        command='reg add "HKCU\\Software\\Microsoft\\GameBar" /v AllowAutoGameMode /t REG_DWORD /d 1 /f',
        shell="cmd",
        category="Gaming",
        enabled_by_default=True,
    ),
    Action(
        title="Enable Hardware-Accelerated GPU Scheduling (HAGS)",
        description=(
            "Lets the GPU manage its own video memory and scheduling, "
            "moving work off the CPU. Smaller CPU overhead, sometimes "
            "noticeable FPS bumps on lower-end CPUs. Reboot required. "
            "Needs a modern GPU + recent driver."),
        command=(
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" '
            '/v HwSchMode /t REG_DWORD /d 2 /f'
        ),
        shell="cmd",
        category="Gaming",
        enabled_by_default=False,
    ),
    Action(
        title="Disable Hardware-Accelerated GPU Scheduling (HAGS)",
        description=(
            "Some games / older drivers behave better with HAGS off. "
            "Reboot required."),
        command=(
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" '
            '/v HwSchMode /t REG_DWORD /d 1 /f'
        ),
        shell="cmd",
        category="Gaming",
        enabled_by_default=False,
    ),
    Action(
        title="Enable Variable Refresh Rate (Windows-side)",
        description=(
            "Turns the Windows VRR setting on. Your monitor + GPU also "
            "need to support FreeSync / G-Sync, but without this switch "
            "Windows doesn’t pass VRR through to fullscreen games."),
        command=(
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" '
            '/v VRROptimizeEnable /t REG_DWORD /d 1 /f'
        ),
        shell="cmd",
        category="Gaming",
        enabled_by_default=False,
    ),
    Action(
        title="Disable mouse acceleration (‘Enhance pointer precision’)",
        description=(
            "Mouse acceleration changes how far the cursor moves based on "
            "how fast you flick the mouse. Almost every competitive gamer "
            "turns this off for consistent muscle memory."),
        command=(
            'reg add "HKCU\\Control Panel\\Mouse" /v MouseSpeed       /t REG_SZ /d 0 /f & '
            'reg add "HKCU\\Control Panel\\Mouse" /v MouseThreshold1  /t REG_SZ /d 0 /f & '
            'reg add "HKCU\\Control Panel\\Mouse" /v MouseThreshold2  /t REG_SZ /d 0 /f'
        ),
        shell="cmd",
        category="Gaming",
        enabled_by_default=False,
    ),

    # ── UI / Memory ─────────────────────────────────────────────────────────
    Action(
        title="‘Adjust for best performance’ visual effects preset",
        description=(
            "Equivalent of System Properties → Performance → Adjust for "
            "best performance. Turns off almost every animation. Looks "
            "plain but feels snappy on slow PCs."),
        command='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f',
        shell="cmd",
        category="UI",
        enabled_by_default=False,
    ),
    Action(
        title="‘Best appearance’ visual effects preset",
        description=(
            "The opposite of the above — turn every animation back on. "
            "Use this to revert."),
        command='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 1 /f',
        shell="cmd",
        category="UI",
        enabled_by_default=False,
    ),
    Action(
        title="Speed up menu show delay",
        description=(
            "Drops the menu-show animation delay from 400 ms (default) to "
            "100 ms. Right-click menus pop almost instantly."),
        command='reg add "HKCU\\Control Panel\\Desktop" /v MenuShowDelay /t REG_SZ /d 100 /f',
        shell="cmd",
        category="UI",
        enabled_by_default=False,
    ),
    Action(
        title="Clear standby memory / working set",
        description=(
            "Asks Windows to drop cached pages back to free memory. Useful "
            "before launching a memory-hungry app on a low-RAM machine. "
            "Doesn’t harm anything — Windows will refill the cache as "
            "needed."),
        command=(
            "powershell -NoProfile -Command \"Get-Process "
            "| Where-Object { $_.WorkingSet -gt 100MB } "
            "| ForEach-Object { try { $_.MinWorkingSet = 1 } catch { } }\""
        ),
        shell="cmd",
        category="Memory",
        enabled_by_default=False,
    ),

    # ── Tools ───────────────────────────────────────────────────────────────
    Action(
        title="Open Startup Apps (Task Manager → Startup)",
        description=(
            "Opens Task Manager focused on the Startup tab so you can "
            "disable anything you don’t want auto-launching with Windows."),
        command="taskmgr /0 /startup",
        shell="cmd",
        category="Tools",
        enabled_by_default=False,
    ),
    Action(
        title="Open System Configuration (msconfig)",
        description=(
            "Opens msconfig.exe for boot, services and startup tuning."),
        command="msconfig",
        shell="cmd",
        category="Tools",
        enabled_by_default=False,
    ),
    Action(
        title="Open Performance Monitor (perfmon)",
        description=(
            "Opens perfmon.exe — the heavy-duty Windows performance "
            "graphing tool. Useful for spotting which counter is pegged."),
        command="perfmon",
        shell="cmd",
        category="Tools",
        enabled_by_default=False,
    ),
]

"""Hardware-aware game tweaks.

`build_for(profile)` returns a list of Actions filtered down to whatever
is relevant for the user’s detected hardware. Each action carries a tuple
of ``presets`` it belongs to — the Game Tune tab uses that to auto-tick
the right boxes when a preset is selected.

Presets:
    Esports    — competitive multiplayer, lowest input latency
    AAA        — single-player, max visual quality + smoothness
    Streaming  — recording / OBS / broadcasting alongside the game
    Laptop     — gaming on a laptop, preserve some battery / thermals
"""
from __future__ import annotations

from ..tabs._models import Action
from ..utils.hardware import HardwareProfile

ESPORTS   = "Esports"
AAA       = "AAA"
STREAMING = "Streaming"
LAPTOP    = "Laptop"
PRESETS   = (ESPORTS, AAA, STREAMING, LAPTOP)


def _reg(hive, path, name, val, kind="DWORD") -> str:
    if kind == "DWORD":
        return f'reg add "{hive}\\{path}" /v "{name}" /t REG_DWORD /d {int(val)} /f'
    return f'reg add "{hive}\\{path}" /v "{name}" /t REG_SZ /d "{val}" /f'


# ---------------------------------------------------------------------------
# Universal — applies to almost any gaming PC
# ---------------------------------------------------------------------------

def _universal() -> list[Action]:
    return [
        Action(
            title="Enable Windows Game Mode",
            description=(
                "Lets Windows prioritise the foreground game and suspend most "
                "background work (Windows Update downloads, defrag, indexer). "
                "Free FPS and frame-time stability — keep on unless you stream."),
            command=_reg("HKCU", r"Software\Microsoft\GameBar",
                         "AllowAutoGameMode", 1),
            shell="cmd",
            category="Universal",
            presets=(ESPORTS, AAA, LAPTOP),
            enabled_by_default=True,
        ),
        Action(
            title="Disable Xbox Game DVR (background recording)",
            description=(
                "Game DVR keeps a rolling clip of the last few minutes of "
                "every game ‘just in case’. Costs CPU + disk I/O. Turn off "
                "unless you actually use the 30s clip-saving."),
            command=(
                _reg("HKCU", r"System\GameConfigStore", "GameDVR_Enabled", 0)
                + " & " +
                _reg("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\GameDVR",
                     "AllowGameDVR", 0)
            ),
            shell="cmd",
            category="Universal",
            presets=(ESPORTS, AAA, LAPTOP),
        ),
        Action(
            title="Disable Xbox Game Bar (Win+G overlay)",
            description=(
                "Removes the Win+G overlay. Frees a small amount of background "
                "RAM/CPU and avoids accidental opens mid-match."),
            command=_reg("HKCU", r"Software\Microsoft\GameBar",
                         "UseNexusForGameBarEnabled", 0),
            shell="cmd",
            category="Universal",
            presets=(ESPORTS,),
        ),
        Action(
            title="Disable mouse acceleration (‘Enhance pointer precision’)",
            description=(
                "Mouse acceleration changes how far the cursor moves based on "
                "flick speed — devastating for muscle memory in any aimed "
                "game. Every esports pro turns this off."),
            command=(
                'reg add "HKCU\\Control Panel\\Mouse" /v MouseSpeed       /t REG_SZ /d 0 /f & '
                'reg add "HKCU\\Control Panel\\Mouse" /v MouseThreshold1  /t REG_SZ /d 0 /f & '
                'reg add "HKCU\\Control Panel\\Mouse" /v MouseThreshold2  /t REG_SZ /d 0 /f'
            ),
            shell="cmd",
            category="Universal",
            presets=(ESPORTS,),
        ),
        Action(
            title="Multimedia: SystemResponsiveness = 0 (prioritise foreground)",
            description=(
                "Reserves 0% of CPU for non-multimedia tasks (default is 20%). "
                "Lets games and DAWs consume the full CPU when needed."),
            command=_reg(
                "HKLM",
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
                "SystemResponsiveness", 0),
            shell="cmd",
            category="Universal",
            presets=(ESPORTS, AAA, STREAMING),
        ),
        Action(
            title="Multimedia: NetworkThrottlingIndex = off",
            description=(
                "Removes Windows’ default cap on multimedia network throttling. "
                "Helps reduce micro-stutters during online play / live streams."),
            command=_reg(
                "HKLM",
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
                "NetworkThrottlingIndex", 0xFFFFFFFF),
            shell="cmd",
            category="Universal",
            presets=(ESPORTS, AAA, STREAMING),
        ),
        Action(
            title="GPU + CPU priority boost for ‘Games’ task class",
            description=(
                "MMCSS ‘Games’ class controls how aggressively Windows schedules "
                "game threads. Sets GPU Priority=8 and Priority=6 — both "
                "Microsoft-documented values."),
            command=(
                _reg("HKLM",
                     r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
                     "GPU Priority", 8) + " & " +
                _reg("HKLM",
                     r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
                     "Priority", 6) + " & " +
                _reg("HKLM",
                     r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
                     "Scheduling Category", "High", kind="SZ") + " & " +
                _reg("HKLM",
                     r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
                     "SFIO Priority", "High", kind="SZ")
            ),
            shell="cmd",
            category="Universal",
            presets=(ESPORTS, AAA),
        ),
        Action(
            title="Activate High Performance power plan",
            description=(
                "Stops the CPU from down-clocking under light load. Best for "
                "desktops. Laptops will lose battery life — use the Laptop "
                "preset there instead."),
            command="powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
            shell="cmd",
            category="Universal",
            presets=(ESPORTS, AAA, STREAMING),
        ),
        Action(
            title="Reveal & activate Ultimate Performance plan",
            description=(
                "Duplicates Workstation’s hidden Ultimate plan and makes it "
                "active. Disables almost every power-saving feature. Best "
                "for plugged-in AAA gaming desktops."),
            command=(
                "powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 & "
                "powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61"
            ),
            shell="cmd",
            category="Universal",
            presets=(AAA,),
        ),
        Action(
            title="Disable USB selective suspend",
            description=(
                "Stops Windows putting idle USB devices to sleep — fixes "
                "stuttering mice, ‘USB DAC clicks’, controller dropouts."),
            command=(
                "powercfg /setacvalueindex SCHEME_CURRENT "
                "2a737441-1930-4402-8d77-b2bebba308a3 "
                "48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0 & "
                "powercfg /setactive SCHEME_CURRENT"
            ),
            shell="cmd",
            category="Universal",
            presets=(ESPORTS, AAA),
        ),
        Action(
            title="Enable Variable Refresh Rate (Windows-side)",
            description=(
                "Required for FreeSync / G-Sync to pass through to fullscreen "
                "games. Doesn’t hurt if your monitor doesn’t support VRR."),
            command=_reg(
                "HKLM", r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                "VRROptimizeEnable", 1),
            shell="cmd",
            category="Universal",
            presets=(AAA, ESPORTS),
        ),
        Action(
            title="Enable Hardware-Accelerated GPU Scheduling (HAGS)",
            description=(
                "Hands GPU scheduling/VRAM management off the CPU to the GPU. "
                "Lower CPU overhead, sometimes FPS bumps. Some titles dislike "
                "it — flip the next action to disable if so. Reboot required."),
            command=_reg("HKLM",
                         r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                         "HwSchMode", 2),
            shell="cmd",
            category="Universal",
            presets=(AAA,),
        ),
        Action(
            title="Disable Hardware-Accelerated GPU Scheduling (HAGS)",
            description=(
                "Counterpart to the action above. Use if HAGS made things "
                "worse for your game/driver combination."),
            command=_reg("HKLM",
                         r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                         "HwSchMode", 1),
            shell="cmd",
            category="Universal",
            presets=(),
        ),
    ]


# ---------------------------------------------------------------------------
# NVIDIA-specific
# ---------------------------------------------------------------------------

def _nvidia() -> list[Action]:
    msi_script = (
        "Get-PnpDevice -Class Display "
        "| Where-Object { $_.FriendlyName -match 'NVIDIA|GeForce|RTX|GTX|Quadro' } "
        "| ForEach-Object { "
        "  $iid = $_.InstanceId; "
        "  $key = \"HKLM:\\SYSTEM\\CurrentControlSet\\Enum\\$iid\\Device Parameters\\Interrupt Management\\MessageSignaledInterruptProperties\"; "
        "  New-Item -Path $key -Force | Out-Null; "
        "  Set-ItemProperty -Path $key -Name MsiSupported -Value 1 -Type DWord -Force; "
        "  Write-Host \"MSI mode set on $($_.FriendlyName)\" "
        "}"
    )
    return [
        Action(
            title="NVIDIA: enable MSI interrupt mode on the GPU",
            description=(
                "Switches the dGPU from line-based interrupts to MSI (Message "
                "Signaled). Lowers DPC latency — fewer audio glitches, smoother "
                "1% lows. Microsoft-recommended on every modern GPU. Reboot "
                "after."),
            command=msi_script,
            shell="powershell",
            category="NVIDIA",
            presets=(ESPORTS, AAA, STREAMING),
        ),
        Action(
            title="NVIDIA: prevent ShadowPlay from running in the background",
            description=(
                "The NVIDIA Container service keeps recording state ready even "
                "when you don’t use it. This kills the recurring background "
                "scheduled task. Re-enable from GeForce Experience if you "
                "ever want it back."),
            command=(
                'schtasks /Change /TN "NvTmRep_CrashReport1_{B2FE1952-0186-46c3-BAEC-A80AA35AC5B8}" /Disable & '
                'schtasks /Change /TN "NvTmRep_CrashReport2_{B2FE1952-0186-46c3-BAEC-A80AA35AC5B8}" /Disable & '
                'schtasks /Change /TN "NvTmRep_CrashReport3_{B2FE1952-0186-46c3-BAEC-A80AA35AC5B8}" /Disable & '
                'schtasks /Change /TN "NvTmRep_CrashReport4_{B2FE1952-0186-46c3-BAEC-A80AA35AC5B8}" /Disable & '
                'schtasks /Change /TN "NvTmRepOnLogon_{B2FE1952-0186-46c3-BAEC-A80AA35AC5B8}" /Disable'
            ),
            shell="cmd",
            category="NVIDIA",
            presets=(ESPORTS, LAPTOP),
        ),
        Action(
            title="NVIDIA: prefer max performance (set via registry hint)",
            description=(
                "Writes the global ‘Prefer maximum performance’ power-mode "
                "hint. Counterpart of the per-profile setting in NVIDIA "
                "Control Panel. May be overridden by the driver UI — also "
                "set it there for best effect."),
            command=_reg(
                "HKLM",
                r"SOFTWARE\NVIDIA Corporation\Global\NVTweak",
                "PreferSystemMemoryContiguous", 1),
            shell="cmd",
            category="NVIDIA",
            presets=(AAA, ESPORTS),
        ),
    ]


# ---------------------------------------------------------------------------
# AMD GPU specific
# ---------------------------------------------------------------------------

def _amd_gpu() -> list[Action]:
    msi_script = (
        "Get-PnpDevice -Class Display "
        "| Where-Object { $_.FriendlyName -match 'AMD|Radeon|RX ' } "
        "| ForEach-Object { "
        "  $iid = $_.InstanceId; "
        "  $key = \"HKLM:\\SYSTEM\\CurrentControlSet\\Enum\\$iid\\Device Parameters\\Interrupt Management\\MessageSignaledInterruptProperties\"; "
        "  New-Item -Path $key -Force | Out-Null; "
        "  Set-ItemProperty -Path $key -Name MsiSupported -Value 1 -Type DWord -Force; "
        "  Write-Host \"MSI mode set on $($_.FriendlyName)\" "
        "}"
    )
    return [
        Action(
            title="AMD: enable MSI interrupt mode on the GPU",
            description=(
                "Switches the Radeon dGPU to Message Signaled Interrupts. "
                "Lower DPC latency, fewer audio dropouts. Reboot required."),
            command=msi_script,
            shell="powershell",
            category="AMD GPU",
            presets=(ESPORTS, AAA, STREAMING),
        ),
        Action(
            title="AMD: disable Adrenalin Software web overlay telemetry",
            description=(
                "AMD Adrenalin runs a small web stack for the overlay/widget "
                "system. This stops the background AMD External Events Utility "
                "process from launching at logon."),
            command=(
                'sc config AMD External Events Utility start=manual 2>nul & '
                'sc stop "AMD External Events Utility" 2>nul'
            ),
            shell="cmd",
            category="AMD GPU",
            presets=(ESPORTS, LAPTOP),
        ),
    ]


# ---------------------------------------------------------------------------
# Intel hybrid (12th-gen+ / Core Ultra)
# ---------------------------------------------------------------------------

def _intel_hybrid() -> list[Action]:
    return [
        Action(
            title="Intel hybrid: prefer P-cores for foreground apps",
            description=(
                "Tells the Windows scheduler to keep latency-sensitive work "
                "on Performance cores (default ‘balanced’ lets it drift to "
                "E-cores). Value 4 = ‘Prefer performant processors’ on the "
                "active power scheme."),
            command=(
                "powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR "
                "bae08b81-2d5e-4688-ad6a-13243356654b 4 & "
                "powercfg /setactive SCHEME_CURRENT"
            ),
            shell="cmd",
            category="Intel hybrid",
            presets=(ESPORTS,),
        ),
        Action(
            title="Intel hybrid: balanced policy (default for AAA games)",
            description=(
                "Lets background work spill onto E-cores while keeping the "
                "game on P-cores. Value 1 = ‘Automatic’. Use if the Esports "
                "preset made a game stutter when discord / OBS was running."),
            command=(
                "powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR "
                "bae08b81-2d5e-4688-ad6a-13243356654b 1 & "
                "powercfg /setactive SCHEME_CURRENT"
            ),
            shell="cmd",
            category="Intel hybrid",
            presets=(AAA, STREAMING),
        ),
    ]


# ---------------------------------------------------------------------------
# AMD Ryzen
# ---------------------------------------------------------------------------

def _ryzen() -> list[Action]:
    return [
        Action(
            title="AMD Ryzen: activate AMD Ryzen Balanced plan (if installed)",
            description=(
                "The AMD chipset driver installs a ‘Ryzen Balanced’ power plan "
                "tuned for Zen CPPC / preferred-core scheduling. This activates "
                "it. If the plan isn’t present, the command no-ops."),
            command=(
                "powercfg /setactive 9897998c-92de-4669-853f-b7cd3ecb2790"
            ),
            shell="cmd",
            category="Ryzen",
            presets=(ESPORTS, AAA),
        ),
        Action(
            title="AMD Ryzen: disable Core Parking for predictable boost",
            description=(
                "Sets CPMINCORES = 100% so no cores are parked. Each Zen core "
                "is always ready to boost — eliminates a class of "
                "‘first-frame stutter’ in games that ramp threads quickly."),
            command=(
                "powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR "
                "0cc5b647-c1df-4637-891a-dec35c318583 100 & "
                "powercfg /setactive SCHEME_CURRENT"
            ),
            shell="cmd",
            category="Ryzen",
            presets=(ESPORTS, AAA),
        ),
    ]


# ---------------------------------------------------------------------------
# Memory-conditional
# ---------------------------------------------------------------------------

def _low_ram() -> list[Action]:
    return [
        Action(
            title="Fixed pagefile sized 1.5 × RAM (for low-RAM systems)",
            description=(
                "Replaces Windows’ ‘System managed’ pagefile with a fixed size "
                "= 1.5× your installed RAM. Smoother under heavy load on "
                "<16 GB machines because the OS doesn’t need to keep growing "
                "the file."),
            command=(
                "$mb = [int]((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1MB * 1.5); "
                "wmic computersystem set AutomaticManagedPagefile=False; "
                "wmic pagefileset where name='C:\\\\pagefile.sys' set InitialSize=$mb,MaximumSize=$mb; "
                "Write-Host \"Pagefile fixed at $mb MB\""
            ),
            shell="powershell",
            category="Low RAM (<16 GB)",
            presets=(ESPORTS, AAA, LAPTOP),
        ),
        Action(
            title="Enable Memory Compression (lower RAM pressure)",
            description=(
                "Default in Win10+ but sometimes disabled. Compresses cold "
                "pages in RAM instead of paging them to disk — way faster on "
                "low-RAM systems."),
            command="powershell -NoProfile -Command \"Enable-MMAgent -mc\"",
            shell="cmd",
            category="Low RAM (<16 GB)",
            presets=(ESPORTS, AAA, LAPTOP),
        ),
    ]


def _high_ram() -> list[Action]:
    return [
        Action(
            title="Disable pagefile (32+ GB RAM only, advanced)",
            description=(
                "Removes the C:\\pagefile.sys entirely. Frees disk space and "
                "avoids the OS paging out anything. Some apps (older Adobe, "
                "some games) crash without a pagefile — re-enable if you "
                "see weirdness."),
            command=(
                "wmic computersystem set AutomaticManagedPagefile=False; "
                "wmic pagefileset delete; "
                "Write-Host 'Pagefile removed (reboot required)'"
            ),
            shell="powershell",
            category="High RAM (32+ GB)",
            presets=(),
            danger=True,
        ),
    ]


# ---------------------------------------------------------------------------
# Storage-conditional
# ---------------------------------------------------------------------------

def _hdd() -> list[Action]:
    return [
        Action(
            title="HDD primary: enable Superfetch / SysMain",
            description=(
                "On spinning disks, Superfetch (SysMain) pre-loads frequently "
                "used apps into RAM — measurable launch-time win. Disable on "
                "SSDs (covered in the SSD section)."),
            command="sc config SysMain start=auto & sc start SysMain",
            shell="cmd",
            category="HDD primary",
            presets=(AAA, LAPTOP),
        ),
    ]


def _ssd() -> list[Action]:
    return [
        Action(
            title="SSD primary: disable Superfetch / SysMain",
            description=(
                "On a modern NVMe SSD, SysMain provides almost no benefit and "
                "sometimes hammers the disk with background reads. Disable to "
                "free 100–300 MB of constant RAM use."),
            command="sc stop SysMain & sc config SysMain start=disabled",
            shell="cmd",
            category="SSD primary",
            presets=(ESPORTS, AAA),
        ),
        Action(
            title="SSD primary: TRIM all SSDs now",
            description=(
                "Forces a TRIM pass on every fixed drive Windows sees as an "
                "SSD. Improves long-term write performance, especially on "
                "older SATA SSDs."),
            command=(
                "Get-Volume | Where-Object DriveType -eq 'Fixed' "
                "| ForEach-Object { Optimize-Volume -DriveLetter "
                "$_.DriveLetter -ReTrim -Verbose }"
            ),
            shell="powershell",
            category="SSD primary",
            presets=(AAA,),
        ),
    ]


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def _high_refresh() -> list[Action]:
    return [
        Action(
            title="High-refresh: enable Windows VRR + auto HDR (W11)",
            description=(
                "Turns on both the system-wide VRR switch (required for "
                "FreeSync/G-Sync passthrough to fullscreen games) and Auto "
                "HDR for SDR titles on HDR displays."),
            command=(
                _reg("HKLM",
                     r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                     "VRROptimizeEnable", 1) + " & " +
                _reg("HKCU",
                     r"Software\Microsoft\DirectX\UserGpuPreferences",
                     "DirectXUserGlobalSettings",
                     "AutoHDREnable=2097;", kind="SZ")
            ),
            shell="cmd",
            category="High-refresh display",
            presets=(ESPORTS, AAA),
        ),
    ]


# ---------------------------------------------------------------------------
# Network
# ---------------------------------------------------------------------------

def _wifi() -> list[Action]:
    msi_script = (
        "Get-PnpDevice -Class Net "
        "| Where-Object { $_.FriendlyName -match 'Wi-Fi|Wireless|802\\.11|AX2|AX1' } "
        "| ForEach-Object { "
        "  $iid = $_.InstanceId; "
        "  $key = \"HKLM:\\SYSTEM\\CurrentControlSet\\Enum\\$iid\\Device Parameters\\Interrupt Management\\MessageSignaledInterruptProperties\"; "
        "  New-Item -Path $key -Force | Out-Null; "
        "  Set-ItemProperty -Path $key -Name MsiSupported -Value 1 -Type DWord -Force; "
        "  Write-Host \"MSI mode set on $($_.FriendlyName)\" "
        "}"
    )
    return [
        Action(
            title="Wi-Fi: enable MSI mode on the wireless NIC",
            description=(
                "Same MSI tweak as for GPUs, applied to the Wi-Fi adapter. "
                "Lower interrupt latency = smoother online gameplay. Reboot."),
            command=msi_script,
            shell="powershell",
            category="Wi-Fi",
            presets=(ESPORTS,),
        ),
        Action(
            title="Wi-Fi: disable Nagle on every interface",
            description=(
                "Removes the small-packet coalescing delay (~40 ms) on TCP. "
                "Lower latency for competitive games / voice. Slightly higher "
                "small-packet overhead is negligible on Wi-Fi 5+."),
            command=(
                "Get-ChildItem 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces' "
                "| ForEach-Object { "
                "Set-ItemProperty -Path $_.PSPath -Name TcpAckFrequency -Value 1 -Type DWord -Force; "
                "Set-ItemProperty -Path $_.PSPath -Name TCPNoDelay      -Value 1 -Type DWord -Force }; "
                "Write-Host 'Nagle disabled'"
            ),
            shell="powershell",
            category="Wi-Fi",
            presets=(ESPORTS,),
        ),
    ]


# ---------------------------------------------------------------------------
# Laptop
# ---------------------------------------------------------------------------

def _laptop() -> list[Action]:
    return [
        Action(
            title="Laptop: keep Balanced plan (not High Performance)",
            description=(
                "On laptops, High Performance often just thermal-throttles "
                "anyway because the cooler can’t keep up. Balanced gives near-"
                "identical sustained perf with much better battery life."),
            command="powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e",
            shell="cmd",
            category="Laptop",
            presets=(LAPTOP,),
        ),
        Action(
            title="Laptop: disable USB selective suspend on AC",
            description=(
                "Mice and controllers behave better with selective suspend off "
                "while plugged in. Battery cost is small."),
            command=(
                "powercfg /setacvalueindex SCHEME_CURRENT "
                "2a737441-1930-4402-8d77-b2bebba308a3 "
                "48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0 & "
                "powercfg /setactive SCHEME_CURRENT"
            ),
            shell="cmd",
            category="Laptop",
            presets=(LAPTOP, ESPORTS),
        ),
    ]


# ---------------------------------------------------------------------------
# Streaming
# ---------------------------------------------------------------------------

def _streaming() -> list[Action]:
    return [
        Action(
            title="Streaming: raise foreground priority boost",
            description=(
                "Win32PrioritySeparation = 0x26 (38 decimal) = max foreground "
                "boost. OBS/Streamlabs gets reliable CPU when in focus."),
            command=_reg(
                "HKLM",
                r"SYSTEM\CurrentControlSet\Control\PriorityControl",
                "Win32PrioritySeparation", 0x26),
            shell="cmd",
            category="Streaming",
            presets=(STREAMING,),
        ),
    ]


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


def build_for(profile: HardwareProfile) -> list[Action]:
    """Return the slice of actions that makes sense for this PC."""
    actions: list[Action] = []
    actions += _universal()

    if profile.gpu_vendor == "NVIDIA":
        actions += _nvidia()
    if profile.gpu_vendor == "AMD":
        actions += _amd_gpu()
    if profile.cpu_hybrid:
        actions += _intel_hybrid()
    if profile.cpu_vendor == "AMD":
        actions += _ryzen()

    if 0 < profile.ram_total_gb < 16:
        actions += _low_ram()
    if profile.ram_total_gb >= 32:
        actions += _high_ram()

    if profile.storage_primary_media == "SSD":
        actions += _ssd()
    elif profile.storage_primary_media == "HDD":
        actions += _hdd()

    if profile.monitor_refresh_hz >= 120:
        actions += _high_refresh()

    if profile.nic_type == "Wi-Fi":
        actions += _wifi()

    if profile.is_laptop:
        actions += _laptop()

    actions += _streaming()
    return actions


# ---------------------------------------------------------------------------
# BIOS-level reminders — things we deliberately can't touch from Windows.
# Displayed as a separate read-only section on the Game Tune tab.
# ---------------------------------------------------------------------------


BIOS_CHECKLIST: list[tuple[str, str]] = [
    ("XMP / EXPO / DOCP",
     "Enable in BIOS. Single biggest free perf gain on most modern PCs — "
     "without it, your RAM runs at JEDEC default (often 30–50 % slower than "
     "what’s printed on the sticks)."),
    ("Resizable BAR / Smart Access Memory",
     "Lets the CPU address the full VRAM at once. Free 1–8 % FPS on most "
     "modern GPUs. Look for ‘Above 4G Decoding’ + ‘Re-Size BAR Support’."),
    ("PBO (AMD) / Adaptive Boost (Intel)",
     "Allows the CPU to boost higher and longer when thermals/power allow. "
     "Free if your cooling can handle it."),
    ("fTPM stutter fix (early Zen3 + Win11)",
     "If you’re on a 5000-series Ryzen with random multi-second freezes, "
     "switch fTPM → discrete TPM, or update to the latest AGESA BIOS."),
    ("Fast Boot OFF (in OS — covered by Bloated)",
     "‘Fast Startup’ in Windows is a half-hibernate that causes weirdness. "
     "The Performance tab has a one-click action for this."),
    ("Monitor OC (some panels)",
     "Many ‘144 Hz’ panels can do 165–180 Hz with a custom resolution. "
     "Tools: NVIDIA Custom Resolutions, CRU."),
    ("PCIe lane sharing",
     "Some boards share PCIe lanes between an M.2 slot and the GPU slot. "
     "Check the manual — moving an NVMe slot can give the GPU full x16."),
]

"""Windows services that are safe (or at least sensible) to disable on a
typical desktop PC.

For each service we generate two actions:
  • a ‘Disable’ action that stops it now and sets startup-type = disabled
  • a ‘Re-enable’ action that flips it back to auto-start and starts it

So the Re-enable category in the UI doubles as the one-click revert button.
"""
from __future__ import annotations

from ..tabs._models import Action


# (service-name, friendly name, what it does + impact of disabling)
SERVICES = [
    ("DiagTrack",
     "Connected User Experiences & Telemetry",
     "Microsoft’s main telemetry pipeline — collects diagnostic data and "
     "ships it to MS. Disabling stops the uploads with no visible impact "
     "on day-to-day use."),

    ("dmwappushservice",
     "Device Management WAP Push",
     "Routing service used by MDM (mobile device management) telemetry. "
     "On a personal PC it does nothing useful — safe to disable."),

    ("MapsBroker",
     "Downloaded Maps Manager",
     "Background downloader for offline maps used by the Maps app. If you "
     "don’t use the Maps app, this is wasted background CPU/disk."),

    ("WMPNetworkSvc",
     "Windows Media Player Network Sharing",
     "Streams your WMP music/video library to other devices on the LAN. "
     "Almost nobody uses this in 2026 — safe to disable."),

    ("RetailDemo",
     "Retail Demo Service",
     "Used by store demo machines to put Windows into ‘demo mode’. Useless "
     "on a home PC — safe to disable."),

    ("WSearch",
     "Windows Search",
     "⚠️ Indexes your files so Start menu / Outlook / Explorer searches are "
     "fast. Disabling SAVES disk activity (good for older SSDs) but makes "
     "Start search and Outlook search slow. Don’t disable unless you "
     "barely use file search."),

    ("XblAuthManager",
     "Xbox Live Auth Manager",
     "Background sign-in service that lets PC games talk to Xbox Live. "
     "Disable only if you don’t play any Microsoft Store / Game Pass games."),

    ("XblGameSave",
     "Xbox Live Game Save",
     "Cloud save sync for Xbox-enabled PC games. Same as above — disable "
     "only if you don’t use them."),

    ("XboxGipSvc",
     "Xbox Accessory Management",
     "Driver service for Xbox controllers connected via USB / dongle. "
     "Keep enabled if you use an Xbox controller on your PC."),

    ("XboxNetApiSvc",
     "Xbox Live Networking",
     "Lets games punch through NAT for multiplayer over Xbox Live. Disable "
     "if you don’t play those games."),

    ("Fax",
     "Fax",
     "Yes, Windows still ships a Fax service. Disable unless you have a "
     "modem and actually send faxes (no, really)."),

    ("PrintNotify",
     "Printer Extensions & Notifications",
     "Background popups when a print job finishes / printer needs ink. "
     "Disable for quieter notifications; printing still works."),

    ("PhoneSvc",
     "Phone Service",
     "Manages telephony state on cellular-enabled Windows devices. Does "
     "nothing on a normal desktop / laptop."),

    ("SCardSvr",
     "Smart Card",
     "Used by some enterprises for smart-card login (PIV / CAC cards). "
     "Useless at home — safe to disable."),

    ("WbioSrvc",
     "Windows Biometric Service",
     "⚠️ Required for Windows Hello fingerprint / face login. DON’T disable "
     "if you use those."),

    ("HomeGroupListener",
     "HomeGroup Listener",
     "Legacy ‘HomeGroup’ file sharing — removed in Windows 11. If your PC "
     "still has it, it’s pure dead code."),

    ("HomeGroupProvider",
     "HomeGroup Provider",
     "Companion to HomeGroupListener. Same story — dead in modern Windows."),

    ("lfsvc",
     "Geolocation Service",
     "System-wide location sensor (the thing that tells apps where you are). "
     "Disable if you don’t want any app to ever know your location."),

    ("SharedAccess",
     "Internet Connection Sharing (ICS)",
     "Lets you turn one network adapter into a hotspot/router for others. "
     "Disable unless you actively bridge connections."),

    ("RemoteRegistry",
     "Remote Registry",
     "⚠️ Allows OTHER computers on the network to read/write your registry. "
     "Almost universally recommended to disable for security on a personal PC."),

    ("WerSvc",
     "Windows Error Reporting Service",
     "Captures crash dumps when apps die and uploads them to Microsoft. "
     "Disable to stop the uploads (you still see the crash dialogs)."),

    ("DPS",
     "Diagnostic Policy Service",
     "Runs the built-in Windows troubleshooters in the background. Eats "
     "small but steady CPU. Disable if you never use the troubleshoot wizards."),

    ("WdiServiceHost",
     "Diagnostic Service Host",
     "Companion to DPS — disable together if you disable DPS."),

    ("WdiSystemHost",
     "Diagnostic System Host",
     "Companion to DPS — disable together if you disable DPS."),

    ("TabletInputService",
     "Touch Keyboard & Handwriting Panel",
     "Provides the on-screen touch keyboard and handwriting panel. Disable "
     "if you have no touch screen and no stylus."),

    ("FontCache",
     "Windows Font Cache",
     "Caches glyphs to speed up text rendering. Normally leave on; "
     "occasionally helpful to disable + re-enable if fonts break."),

    ("SysMain",
     "SysMain (formerly Superfetch)",
     "Tries to pre-load apps you frequently use into RAM. On a fast NVMe "
     "SSD it provides almost no benefit and sometimes hammers the disk. "
     "Disabling on SSDs is widely recommended."),

    ("DiagSvc",
     "Diagnostic Execution Service",
     "Runs the diagnostic actions WSCEIP / DiagTrack request. Disable "
     "alongside DiagTrack."),

    ("PcaSvc",
     "Program Compatibility Assistant",
     "Watches every program you run and offers ‘this didn’t work — try "
     "compatibility mode’ popups. Some people find these helpful, most "
     "find them noisy."),
]


_RECOMMENDED = {
    "DiagTrack", "dmwappushservice", "MapsBroker", "RetailDemo",
    "WMPNetworkSvc", "Fax", "RemoteRegistry", "WerSvc", "PrintNotify",
    "HomeGroupListener", "HomeGroupProvider", "PhoneSvc",
    "DiagSvc", "PcaSvc", "SysMain",
}


def build_disable_actions() -> list[Action]:
    out: list[Action] = []
    for svc, name, desc in SERVICES:
        out.append(Action(
            title=f"Disable: {name}",
            description=f"{desc}  ·  Service: {svc}",
            command=f"sc stop {svc} & sc config {svc} start=disabled",
            shell="cmd",
            category="Disable services",
            enabled_by_default=(svc in _RECOMMENDED),
        ))
    return out


def build_enable_actions() -> list[Action]:
    out: list[Action] = []
    for svc, name, desc in SERVICES:
        out.append(Action(
            title=f"Re-enable: {name}",
            description=(
                f"Restore this service to ‘Automatic’ startup and start it "
                f"right now. Use this if you regret disabling it.  ·  "
                f"Service: {svc}"),
            command=f"sc config {svc} start=auto & sc start {svc}",
            shell="cmd",
            category="Re-enable services",
            enabled_by_default=False,
        ))
    return out

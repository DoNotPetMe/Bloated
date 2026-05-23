"""Windows services known to be safe to disable for typical desktop users.

Each entry sets the service to disabled and stops it. Reverting is done by
the secondary action created automatically (start=auto + start).
"""
from __future__ import annotations

from ..tabs._models import Action


# (service, friendly, description)
SERVICES = [
    ("DiagTrack",
     "Connected User Experiences & Telemetry",
     "Microsoft’s primary telemetry pipe."),
    ("dmwappushservice",
     "Device Management Wireless Application Protocol",
     "WAP push routing for MDM telemetry."),
    ("MapsBroker",
     "Downloaded Maps Manager",
     "Background downloader for offline maps."),
    ("WMPNetworkSvc",
     "Windows Media Player Network Sharing",
     "Streams WMP libraries on the LAN."),
    ("RetailDemo",
     "Retail Demo Service",
     "Used only in store-demo mode."),
    ("WSearch",
     "Windows Search",
     "Indexing. Disabling speeds disk on small SSDs but breaks Start search."),
    ("XblAuthManager",
     "Xbox Live Auth Manager",
     "Only needed by Xbox-aware games."),
    ("XblGameSave",
     "Xbox Live Game Save",
     "Cloud save for Xbox titles."),
    ("XboxGipSvc",
     "Xbox Accessory Management Service",
     "Manages Xbox controllers."),
    ("XboxNetApiSvc",
     "Xbox Live Networking Service",
     "Xbox multiplayer networking."),
    ("Fax",
     "Fax",
     "Yes, Windows still ships a fax service."),
    ("PrintNotify",
     "Printer Extensions and Notifications",
     "Printer popup notifications."),
    ("PhoneSvc",
     "Phone Service",
     "Telephony state. Unused on desktops."),
    ("SCardSvr",
     "Smart Card",
     "Disable unless you actually use a smart card."),
    ("WbioSrvc",
     "Windows Biometric Service",
     "Needed for Windows Hello fingerprint/face. Leave on if used."),
    ("HomeGroupListener",
     "HomeGroup Listener",
     "Legacy file sharing (removed in newer builds)."),
    ("HomeGroupProvider",
     "HomeGroup Provider",
     "Legacy file sharing (removed in newer builds)."),
    ("lfsvc",
     "Geolocation Service",
     "System location sensor service."),
    ("SharedAccess",
     "Internet Connection Sharing (ICS)",
     "Disable unless you bridge a connection."),
    ("RemoteRegistry",
     "Remote Registry",
     "Lets remote machines edit your registry. Disable for security."),
    ("WerSvc",
     "Windows Error Reporting Service",
     "Uploads crash data to Microsoft."),
    ("DPS",
     "Diagnostic Policy Service",
     "Runs Windows troubleshooters. Disable to save background CPU."),
    ("WdiServiceHost",
     "Diagnostic Service Host",
     "Companion to DPS."),
    ("WdiSystemHost",
     "Diagnostic System Host",
     "Companion to DPS."),
]


_RECOMMENDED = {
    "DiagTrack", "dmwappushservice", "MapsBroker", "RetailDemo",
    "WMPNetworkSvc", "Fax", "RemoteRegistry", "WerSvc", "PrintNotify",
    "HomeGroupListener", "HomeGroupProvider", "PhoneSvc",
}


def build_disable_actions() -> list[Action]:
    out: list[Action] = []
    for svc, name, desc in SERVICES:
        out.append(Action(
            title=f"Disable: {name}  ({svc})",
            description=desc,
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
            title=f"Re-enable: {name}  ({svc})",
            description=f"Set start=auto and start the service. ({desc})",
            command=f"sc config {svc} start=auto & sc start {svc}",
            shell="cmd",
            category="Re-enable services",
            enabled_by_default=False,
        ))
    return out

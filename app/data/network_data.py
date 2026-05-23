"""Network optimisation + repair actions."""
from __future__ import annotations

from ..tabs._models import Action


def _set_dns(dns1: str, dns2: str) -> str:
    """Set DNS on all enabled IPv4 adapters."""
    return (
        f"Get-NetAdapter -Physical | Where-Object Status -eq 'Up' "
        f"| ForEach-Object {{ Set-DnsClientServerAddress "
        f"-InterfaceIndex $_.ifIndex -ServerAddresses ('{dns1}','{dns2}') }}; "
        f"ipconfig /flushdns; Write-Host 'DNS set to {dns1} / {dns2}'"
    )


ACTIONS: list[Action] = [
    Action(
        title="Flush DNS cache",
        description="Clears resolved hostnames (ipconfig /flushdns).",
        command="ipconfig /flushdns",
        shell="cmd",
        category="Repair",
        enabled_by_default=True,
    ),
    Action(
        title="Release & renew DHCP lease",
        description="ipconfig /release then /renew.",
        command="ipconfig /release & ipconfig /renew",
        shell="cmd",
        category="Repair",
        enabled_by_default=False,
    ),
    Action(
        title="Reset Winsock",
        description="netsh winsock reset — fixes broken socket stack. Reboot after.",
        command="netsh winsock reset",
        shell="cmd",
        category="Repair",
        enabled_by_default=False,
        danger=True,
    ),
    Action(
        title="Reset TCP/IP stack",
        description="netsh int ip reset — full network reset. Reboot after.",
        command="netsh int ip reset",
        shell="cmd",
        category="Repair",
        enabled_by_default=False,
        danger=True,
    ),
    Action(
        title="Set DNS → Cloudflare (1.1.1.1 / 1.0.0.1)",
        description="Fast, privacy-respecting public resolver.",
        command=_set_dns("1.1.1.1", "1.0.0.1"),
        shell="powershell",
        category="DNS",
        enabled_by_default=False,
    ),
    Action(
        title="Set DNS → Google (8.8.8.8 / 8.8.4.4)",
        description="Google Public DNS.",
        command=_set_dns("8.8.8.8", "8.8.4.4"),
        shell="powershell",
        category="DNS",
        enabled_by_default=False,
    ),
    Action(
        title="Set DNS → Quad9 (9.9.9.9 / 149.112.112.112)",
        description="Filters known-malicious domains.",
        command=_set_dns("9.9.9.9", "149.112.112.112"),
        shell="powershell",
        category="DNS",
        enabled_by_default=False,
    ),
    Action(
        title="Reset DNS to DHCP defaults",
        description="Reverts adapters to whatever the router hands out.",
        command=(
            "Get-NetAdapter -Physical | Where-Object Status -eq 'Up' "
            "| ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ResetServerAddresses }; "
            "ipconfig /flushdns; Write-Host 'DNS reset to DHCP'"
        ),
        shell="powershell",
        category="DNS",
        enabled_by_default=False,
    ),
    Action(
        title="Enable TCP auto-tuning (normal)",
        description="Restores default Windows receive-window auto-tuning. Fixes slow downloads.",
        command="netsh int tcp set global autotuninglevel=normal",
        shell="cmd",
        category="Tuning",
        enabled_by_default=False,
    ),
    Action(
        title="Disable Nagle (TCPNoDelay) for all interfaces",
        description=("Reduces latency for real-time games / VoIP at the cost of "
                     "slightly more small packets. Per-interface in HKLM."),
        command=(
            "Get-ChildItem 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces' "
            "| ForEach-Object { "
            "Set-ItemProperty -Path $_.PSPath -Name TcpAckFrequency -Value 1 -Type DWord -Force; "
            "Set-ItemProperty -Path $_.PSPath -Name TCPNoDelay        -Value 1 -Type DWord -Force }; "
            "Write-Host 'Nagle disabled on all interfaces'"
        ),
        shell="powershell",
        category="Tuning",
        enabled_by_default=False,
    ),
    Action(
        title="Show current IP / DNS / gateway",
        description="Prints ipconfig /all for inspection.",
        command="ipconfig /all",
        shell="cmd",
        category="Inspect",
        enabled_by_default=False,
    ),
    Action(
        title="Ping Cloudflare (latency check)",
        description="ping 1.1.1.1 -n 4",
        command="ping 1.1.1.1 -n 4",
        shell="cmd",
        category="Inspect",
        enabled_by_default=False,
    ),
]

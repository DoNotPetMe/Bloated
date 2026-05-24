"""Network — DNS providers, stack reset, tuning, inspection."""
from __future__ import annotations

from ..tabs._models import Action


def _set_dns(dns1: str, dns2: str) -> str:
    """Set IPv4 DNS on all up adapters."""
    return (
        f"Get-NetAdapter -Physical | Where-Object Status -eq 'Up' "
        f"| ForEach-Object {{ Set-DnsClientServerAddress "
        f"-InterfaceIndex $_.ifIndex -ServerAddresses ('{dns1}','{dns2}') }}; "
        f"ipconfig /flushdns; Write-Host 'DNS set to {dns1} / {dns2}'"
    )


ACTIONS: list[Action] = [
    # ── Repair ──────────────────────────────────────────────────────────────
    Action(
        title="Flush DNS cache",
        description=(
            "Throws away all cached hostname → IP lookups. The very first "
            "thing to try when ‘a site works on my phone but not my PC’."),
        command="ipconfig /flushdns",
        shell="cmd",
        category="Repair",
        enabled_by_default=True,
    ),
    Action(
        title="Release & renew DHCP lease",
        description=(
            "Gives back your current IP to the router and asks for a fresh "
            "one. Helps when you’re stuck on a 169.254 ‘limited connectivity’ "
            "address or your IP conflicts with another device."),
        command="ipconfig /release & ipconfig /renew",
        shell="cmd",
        category="Repair",
        enabled_by_default=False,
    ),
    Action(
        title="Reset Winsock catalog",
        description=(
            "Resets the Windows socket layer to defaults. Heavy hammer — "
            "useful after VPN clients / antivirus / proxy tools mess with "
            "your TCP stack. Reboot required afterwards."),
        command="netsh winsock reset",
        shell="cmd",
        category="Repair",
        enabled_by_default=False,
        danger=True,
    ),
    Action(
        title="Reset TCP/IP stack",
        description=(
            "Full reset of the IPv4/IPv6 stack to factory defaults. "
            "Combine with Winsock reset above if your network is badly "
            "broken. Reboot required."),
        command="netsh int ip reset",
        shell="cmd",
        category="Repair",
        enabled_by_default=False,
        danger=True,
    ),
    Action(
        title="Reset Windows Firewall to defaults",
        description=(
            "Removes every custom firewall rule you (or apps) have ever "
            "added and re-applies Microsoft’s defaults. Use only if your "
            "firewall is hopelessly mangled."),
        command="netsh advfirewall reset",
        shell="cmd",
        category="Repair",
        enabled_by_default=False,
        danger=True,
    ),

    # ── DNS providers ───────────────────────────────────────────────────────
    Action(
        title="Switch DNS → Cloudflare (1.1.1.1 / 1.0.0.1)",
        description=(
            "The fastest mainstream public resolver in most regions. "
            "Cloudflare doesn’t log your queries to disk. Good default if "
            "you don’t want to use whatever DNS your ISP gave you."),
        command=_set_dns("1.1.1.1", "1.0.0.1"),
        shell="powershell",
        category="DNS",
        enabled_by_default=False,
    ),
    Action(
        title="Switch DNS → Google (8.8.8.8 / 8.8.4.4)",
        description=(
            "Google’s public DNS — fast, reliable, but logged. Use if "
            "Cloudflare is blocked on your network."),
        command=_set_dns("8.8.8.8", "8.8.4.4"),
        shell="powershell",
        category="DNS",
        enabled_by_default=False,
    ),
    Action(
        title="Switch DNS → Quad9 (9.9.9.9 / 149.112.112.112)",
        description=(
            "Quad9 actively blocks known malicious / phishing domains at "
            "the DNS level. Slight extra security with almost no downside "
            "for normal browsing."),
        command=_set_dns("9.9.9.9", "149.112.112.112"),
        shell="powershell",
        category="DNS",
        enabled_by_default=False,
    ),
    Action(
        title="Switch DNS → AdGuard (94.140.14.14 / 94.140.15.15)",
        description=(
            "AdGuard’s public DNS — blocks ads and trackers at the DNS "
            "level. Browsing is noticeably cleaner; some apps may break "
            "if they need a blocked tracking domain."),
        command=_set_dns("94.140.14.14", "94.140.15.15"),
        shell="powershell",
        category="DNS",
        enabled_by_default=False,
    ),
    Action(
        title="Reset DNS to whatever the router hands out (DHCP)",
        description=(
            "Undoes any of the DNS choices above. Adapter goes back to "
            "the router’s default DNS server."),
        command=(
            "Get-NetAdapter -Physical | Where-Object Status -eq 'Up' "
            "| ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ResetServerAddresses }; "
            "ipconfig /flushdns; Write-Host 'DNS reset to DHCP'"
        ),
        shell="powershell",
        category="DNS",
        enabled_by_default=False,
    ),

    # ── Tuning ──────────────────────────────────────────────────────────────
    Action(
        title="Enable TCP auto-tuning (Normal level)",
        description=(
            "Lets Windows dynamically scale the TCP receive window. Some "
            "older guides recommend disabling this, but on a modern "
            "Windows install the correct value is ‘normal’ — this fixes "
            "weirdly slow downloads on fast connections."),
        command="netsh int tcp set global autotuninglevel=normal",
        shell="cmd",
        category="Tuning",
        enabled_by_default=False,
    ),
    Action(
        title="Disable Nagle’s algorithm (lower latency for games)",
        description=(
            "Nagle bundles small TCP packets together for efficiency, at "
            "the cost of a few ms of latency. Disabling helps competitive "
            "games / VoIP, slightly hurts throughput on low-bandwidth "
            "links. Applies to every network interface."),
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
        title="Set network throttling index to ‘off’",
        description=(
            "Windows throttles multimedia network traffic by default. "
            "Setting NetworkThrottlingIndex to 0xFFFFFFFF disables that "
            "behaviour — slightly better throughput for streaming uploads."),
        command=(
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" '
            '/v NetworkThrottlingIndex /t REG_DWORD /d 4294967295 /f'
        ),
        shell="cmd",
        category="Tuning",
        enabled_by_default=False,
    ),

    # ── Inspect ─────────────────────────────────────────────────────────────
    Action(
        title="Show full IP / DNS / gateway info",
        description=(
            "ipconfig /all — dumps every adapter, IP, DNS, gateway and "
            "DHCP lease. The first thing to run when diagnosing any "
            "network problem."),
        command="ipconfig /all",
        shell="cmd",
        category="Inspect",
        enabled_by_default=False,
    ),
    Action(
        title="Ping Cloudflare (latency check)",
        description=(
            "Sends 4 ICMP echoes to 1.1.1.1 and shows round-trip times. "
            "Good for ‘is the internet up or is it me?’ checks."),
        command="ping 1.1.1.1 -n 4",
        shell="cmd",
        category="Inspect",
        enabled_by_default=False,
    ),
    Action(
        title="Trace route to google.com",
        description=(
            "Shows every hop your packets take to reach Google. Long times "
            "on a specific hop point at where the bottleneck is."),
        command="tracert google.com",
        shell="cmd",
        category="Inspect",
        enabled_by_default=False,
    ),
    Action(
        title="Show all listening TCP ports + owning process",
        description=(
            "netstat -ano -p tcp — every open socket and the PID that owns "
            "it. Pair with Task Manager (or ‘Get-Process -Id <PID>’) to "
            "see what’s using your network."),
        command="netstat -ano -p tcp",
        shell="cmd",
        category="Inspect",
        enabled_by_default=False,
    ),
    Action(
        title="Show saved Wi-Fi networks (without passwords)",
        description=(
            "Lists every Wi-Fi profile Windows has remembered."),
        command="netsh wlan show profiles",
        shell="cmd",
        category="Inspect",
        enabled_by_default=False,
    ),
]

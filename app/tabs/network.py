from ._base import ActionListTab
from ..data.network_data import ACTIONS


class NetworkTab(ActionListTab):
    title = "Network"
    subtitle = ("DNS switchers (Cloudflare/Google/Quad9), flush/reset stack, "
                "TCP auto-tuning, Nagle, latency checks.")
    actions = ACTIONS

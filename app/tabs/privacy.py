from ._base import ActionListTab
from ..data.privacy_data import ACTIONS


class PrivacyTab(ActionListTab):
    title = "Privacy Hardener"
    subtitle = ("Disable telemetry, advertising ID, suggested content, Cortana, "
                "Recall, Copilot, and other data-collection surfaces.")
    actions = ACTIONS

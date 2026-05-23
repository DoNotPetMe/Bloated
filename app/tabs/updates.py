from ._base import ActionListTab
from ..data.updates_data import ACTIONS


class UpdatesTab(ActionListTab):
    title = "Windows Update"
    subtitle = ("Pause for 35 days, mark networks metered, disable driver "
                "auto-install, defer feature updates, force a check, revert.")
    actions = ACTIONS

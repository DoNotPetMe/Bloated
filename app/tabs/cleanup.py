from ._base import ActionListTab
from ..data.cleanup_data import ACTIONS


class CleanupTab(ActionListTab):
    title = "Cleanup"
    subtitle = ("Temp folders, caches, prefetch, recycle bin, event logs, "
                "Windows.old. Read each item — some are irreversible.")
    actions = ACTIONS

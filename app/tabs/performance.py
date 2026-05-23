from ._base import ActionListTab
from ..data.performance_data import ACTIONS


class PerformanceTab(ActionListTab):
    title = "Performance"
    subtitle = ("Power plans, GPU scheduling, USB suspend, hibernation, "
                "visual effects, Game Mode.")
    actions = ACTIONS

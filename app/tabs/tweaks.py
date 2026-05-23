from ._base import ActionListTab
from ..data.tweaks_data import ACTIONS


class TweaksTab(ActionListTab):
    title = "Registry Tweaks"
    subtitle = ("Explorer, taskbar, theme, Windows 11 quality-of-life. "
                "Pick what you want and click Run — Explorer will restart at the end.")
    actions = ACTIONS

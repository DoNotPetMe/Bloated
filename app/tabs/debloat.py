from ._base import ActionListTab
from ..data.bloatware_apps import build as _build


class DebloatTab(ActionListTab):
    title = "Debloater"
    subtitle = ("Uninstall pre-installed Microsoft UWP apps and OEM crapware. "
                "Works on fresh installs and existing systems. "
                "‘Recommended’ selects safe-to-remove items.")
    actions = _build()

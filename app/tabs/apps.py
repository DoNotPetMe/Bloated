from ._base import ActionListTab
from ..data.apps_data import build as _build


class AppsTab(ActionListTab):
    title = "App Installer"
    subtitle = ("Bulk install curated apps via winget. Tick what you want and "
                "click Run — each app installs unattended.")
    actions = _build()

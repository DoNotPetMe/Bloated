from ._base import ActionListTab
from ..data.services_data import build_disable_actions, build_enable_actions


class ServicesTab(ActionListTab):
    title = "Services Manager"
    subtitle = ("Stop & disable known offender Windows services. "
                "The ‘Re-enable services’ category is the one-click revert.")
    actions = build_disable_actions() + build_enable_actions()

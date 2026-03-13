"""ui/idle_ign_tab.py — Idle and ignition trim tables."""
from digitool.ui.table_widgets import CorrectionTabBase

class IdleIgnTab(CorrectionTabBase):
    _MAP_NAMES = [
        "Advance vs ECT",
        "Idle Advance Time",
        "Idle Ign High Limit",
        "Idle Ign Low Limit",
        "Idle Ignition",
    ]

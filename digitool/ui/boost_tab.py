"""ui/boost_tab.py — Boost & ISV control tables."""
from digitool.ui.table_widgets import CorrectionTabBase

class BoostTab(CorrectionTabBase):
    _MAP_NAMES = [
        "RPM Scalar",
        "Boost Cut (No Knock)",
        "Boost Cut (Knock)",
        "ISV Boost Control",
        "Startup ISV vs ECT",
    ]

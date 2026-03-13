"""ui/knock_dwell_tab.py — Knock control and coil dwell tables."""
from digitool.ui.table_widgets import CorrectionTabBase

class KnockDwellTab(CorrectionTabBase):
    _MAP_NAMES = [
        "Coil Dwell",
        "Knock Multiplier",
        "Knock Retard Rate",
        "Knock Decay Rate",
    ]

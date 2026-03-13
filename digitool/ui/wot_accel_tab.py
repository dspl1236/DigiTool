"""ui/wot_accel_tab.py — WOT enrichment and acceleration enrichment tables."""
from digitool.ui.table_widgets import CorrectionTabBase

class WotAccelTab(CorrectionTabBase):
    _MAP_NAMES = [
        "WOT Enrichment",
        "WOT Initial Enrichment",
        "CO Adj vs MAP",
        "Accel Enrich Min \u0394MAP",
        "Accel Enrich Mult ECT",
        "Accel Enrich Adder ECT",
    ]

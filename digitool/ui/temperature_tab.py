"""ui/temperature_tab.py — Temperature-based enrichment and compensation tables."""
from digitool.ui.table_widgets import CorrectionTabBase

class TemperatureTab(CorrectionTabBase):
    _MAP_NAMES = [
        "Warm Up Enrichment",
        "IAT Compensation",
        "ECT Compensation 1",
        "ECT Compensation 2",
        "Startup Enrichment",
        "Hot Start Enrichment",
        "Battery Compensation",
    ]

"""ui/lambda_tab.py — Lambda / OXS and injector scaling tables."""
from digitool.ui.table_widgets import CorrectionTabBase

class LambdaTab(CorrectionTabBase):
    _MAP_NAMES = [
        "Injector Lag",
        "OXS Upswing",
        "OXS Downswing",
    ]

"""
ui/map_editor_tab.py
Ignition and Fuel map editors — 16×16 heatmaps with cell info panel.
Supports single-map (G60/G40) and triple-map (G60 triple) variants.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QGroupBox, QLabel, QSizePolicy, QSpinBox,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from digitool.rom_profiles import DetectionResult, MapDef, raw_to_ign_deg, ign_deg_to_raw, MAP_FAMILY_TRIPLE
from digitool.ui.map_table import MapTable


# Generic 16-step axis labels (address decoded from ROM if known, else generic)
_RPM_LABELS  = ["600","800","1000","1250","1500","1750","2000","2250",
                 "2500","2750","3000","3500","4000","5000","6000","6300"]
_LOAD_LABELS = ["20","30","40","50","60","80","100","120",
                "140","160","170","180","190","200","210","220"]


class _MapPanel(QWidget):
    """Single map panel: table + info strip."""

    def __init__(self, title: str, map_type: str = "ign", parent=None):
        super().__init__(parent)
        self._map_def: MapDef | None = None
        self._rom: bytearray | None  = None
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        # Header
        hdr = QLabel(title)
        hdr.setFont(QFont("Segoe UI", 12, QFont.Bold))
        hdr.setStyleSheet("color: #00d4ff; margin-bottom: 4px;")
        root.addWidget(hdr)

        # Table
        self.table = MapTable(16, 16, map_type)
        self.table.set_axis_labels(_RPM_LABELS, _LOAD_LABELS)
        root.addWidget(self.table, 1)

        # Info strip
        info_row = QHBoxLayout()
        self.lbl_cell   = QLabel("Cell: —")
        self.lbl_addr   = QLabel("Addr: —")
        self.lbl_raw    = QLabel("Raw: —")
        self.lbl_deg    = QLabel("Value: —")
        for lbl in [self.lbl_cell, self.lbl_addr, self.lbl_raw, self.lbl_deg]:
            lbl.setStyleSheet("color: #3d5068; font-size: 11px; font-family: Consolas;")
            info_row.addWidget(lbl)
        info_row.addStretch()
        root.addLayout(info_row)

        self.table.cell_selected.connect(self._on_cell)

    def load(self, map_def: MapDef, rom: bytearray):
        self._map_def = map_def
        self._rom     = rom
        start = map_def.data_addr   # ECU address = file offset directly
        data  = list(rom[start: start + map_def.size])
        self.table.load_data(data)

    def get_data(self) -> list:
        return self.table.get_data()

    def write_back(self, rom: bytearray) -> bytearray:
        if self._map_def is None:
            return rom
        start = self._map_def.data_addr   # direct file offset
        data  = self.get_data()
        for i, b in enumerate(data):
            rom[start + i] = b
        return rom

    def _on_cell(self, row: int, col: int, raw: int, display: float):
        addr = 0
        if self._map_def:
            addr = self._map_def.data_addr + row * 16 + col
        self.lbl_cell.setText(f"Cell: [{row},{col}]")
        self.lbl_addr.setText(f"Addr: 0x{addr:04X}")
        self.lbl_raw.setText(f"Raw: {raw}")
        if self.table.map_type == "ign":
            self.lbl_deg.setText(f"Value: {display:.1f}°BTDC")
        else:
            self.lbl_deg.setText(f"Value: {raw}")


class MapEditorTab(QWidget):
    """
    Tab containing ignition (1 or 3 maps) + fuel map editors.
    Dynamically reconfigures based on ROM family.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._result: DetectionResult | None = None
        self._rom:    bytearray | None = None
        self._panels: list[_MapPanel] = []
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(0)

        # Sub-tab widget holds ignition tab(s) + fuel tab
        self.sub_tabs = QTabWidget()
        self.sub_tabs.setDocumentMode(True)
        root.addWidget(self.sub_tabs)

        self._show_placeholder()

    def _show_placeholder(self):
        self.sub_tabs.clear()
        self._panels.clear()
        ph = QWidget()
        pl = QVBoxLayout(ph)
        lbl = QLabel("No ROM loaded.\nOpen a .BIN file from the Overview tab.")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color: #3d5068; font-size: 14px;")
        pl.addWidget(lbl)
        self.sub_tabs.addTab(ph, "Maps")

    # ── Public API ────────────────────────────────────────────────────────────

    def load_rom(self, result: DetectionResult, rom: bytearray):
        self._result = result
        self._rom    = rom
        self.sub_tabs.clear()
        self._panels.clear()

        maps = result.maps

        # Identify ignition + fuel map defs
        if result.is_triple:
            ign_defs  = [m for m in maps if "Ignition" in m.name]
            fuel_defs = [m for m in maps if m.name == "Fuel"]
        else:
            ign_defs  = [m for m in maps if m.name == "Ignition"]
            fuel_defs = [m for m in maps if m.name == "Fuel"]

        # Build ignition panels
        for i, md in enumerate(ign_defs):
            title  = md.name if result.is_triple else "Ignition"
            panel  = _MapPanel(title, "ign")
            try:
                panel.load(md, rom)
            except Exception as e:
                pass
            self._panels.append(panel)
            self.sub_tabs.addTab(panel, f"IGN{i+1}" if result.is_triple else "Ignition")

        # Build fuel panel(s)
        for md in fuel_defs:
            panel = _MapPanel("Fuel", "fuel")
            try:
                panel.load(md, rom)
            except Exception as e:
                pass
            self._panels.append(panel)
            self.sub_tabs.addTab(panel, "Fuel")

    def write_back(self) -> bytearray:
        """Apply all edits back to ROM bytearray."""
        if self._rom is None:
            return bytearray()
        rom = bytearray(self._rom)
        for panel in self._panels:
            rom = panel.write_back(rom)
        self._rom = rom
        return rom

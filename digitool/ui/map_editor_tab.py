"""
ui/map_editor_tab.py
Single 16×16 map editor panel — ignition or fuel.
Used as a standalone tab widget by main_window.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from digitool.rom_profiles import DetectionResult, MapDef
from digitool.ui.map_table import MapTable


_RPM_LABELS  = ["600","800","1000","1250","1500","1750","2000","2250",
                 "2500","2750","3000","3500","4000","5000","6000","6300"]
_LOAD_LABELS = ["20","30","40","50","60","80","100","120",
                "140","160","170","180","190","200","210","220"]


class MapPanel(QWidget):
    """
    Single editable 16×16 heatmap panel with cell info strip.
    map_type: 'ign' or 'fuel'
    """

    def __init__(self, title: str, map_type: str = "ign", parent=None):
        super().__init__(parent)
        self._map_def: MapDef | None = None
        self._rom:     bytearray | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 8)
        root.setSpacing(6)

        hdr = QLabel(title)
        hdr.setFont(QFont("Segoe UI", 12, QFont.Bold))
        hdr.setStyleSheet("color: #00d4ff; margin-bottom: 4px;")
        root.addWidget(hdr)

        self.table = MapTable(16, 16, map_type)
        self.table.set_axis_labels(_RPM_LABELS, _LOAD_LABELS)
        root.addWidget(self.table, 1)

        info_row = QHBoxLayout()
        self.lbl_cell = QLabel("Cell: —")
        self.lbl_addr = QLabel("Addr: —")
        self.lbl_raw  = QLabel("Raw: —")
        self.lbl_val  = QLabel("Value: —")
        for lbl in [self.lbl_cell, self.lbl_addr, self.lbl_raw, self.lbl_val]:
            lbl.setStyleSheet("color: #3d5068; font-size: 11px; font-family: Consolas;")
            info_row.addWidget(lbl)
        info_row.addStretch()
        root.addLayout(info_row)

        self.table.cell_selected.connect(self._on_cell)
        self._map_type = map_type

    def load(self, map_def: MapDef, rom: bytearray):
        self._map_def = map_def
        self._rom     = rom
        data = list(rom[map_def.data_addr: map_def.data_addr + map_def.size])
        self.table.load_data(data)

    def write_back(self, rom: bytearray) -> bytearray:
        if self._map_def is None:
            return rom
        data = self.table.get_data()
        start = self._map_def.data_addr
        for i, b in enumerate(data):
            rom[start + i] = b
        return rom

    def _on_cell(self, row: int, col: int, raw: int, display: float):
        addr = (self._map_def.data_addr + row * 16 + col) if self._map_def else 0
        self.lbl_cell.setText(f"Cell: [{row},{col}]")
        self.lbl_addr.setText(f"Addr: 0x{addr:04X}")
        self.lbl_raw.setText(f"Raw: {raw}")
        if self._map_type == "ign":
            self.lbl_val.setText(f"Value: {display:.1f}°BTDC")
        else:
            self.lbl_val.setText(f"Value: {raw}")

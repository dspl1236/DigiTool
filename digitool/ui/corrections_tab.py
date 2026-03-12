"""
ui/corrections_tab.py
1D correction / scalar tables: warmup enrichment, ECT, IAT, boost cut, etc.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QGroupBox, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush

from digitool.rom_profiles import DetectionResult, MapDef, MAP_FAMILY_MK2


def _heat(val: int, lo: int, hi: int) -> QColor:
    if hi == lo:
        return QColor("#1a2332")
    t = max(0.0, min(1.0, (val - lo) / (hi - lo)))
    if t < 0.5:
        u = t / 0.5
        return QColor(0, int(u * 200), int(100 + u * 155))
    else:
        u = (t - 0.5) / 0.5
        return QColor(int(u * 255), int(200 - u * 200), 0)


class _Table1D(QWidget):
    """Single 1D table display (N×1 or N×M collapsed to 1D)."""

    def __init__(self, map_def: MapDef, parent=None):
        super().__init__(parent)
        self._map_def = map_def
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(2)

        lbl = QLabel(map_def.name)
        lbl.setStyleSheet("color: #bccdd8; font-size: 11px; font-weight: bold;")
        addr_lbl = QLabel(f"@ 0x{map_def.data_addr:04X}  ·  {map_def.cols}×{map_def.rows}")
        addr_lbl.setStyleSheet("color: #3d5068; font-size: 10px; font-family: Consolas;")
        root.addWidget(lbl)
        root.addWidget(addr_lbl)

        self.table = QTableWidget(map_def.rows, map_def.cols)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(map_def.rows > 1)
        self.table.setMaximumHeight(30 + map_def.rows * 28)
        self.table.setFont(QFont("Consolas", 10))
        root.addWidget(self.table)

    def load(self, rom: bytes):
        md   = self._map_def
        # Digifant ROMs start at 0x4000 — subtract base
        base = 0x4000
        start = md.data_addr - base
        data = []
        for i in range(md.size):
            try:
                data.append(rom[start + i])
            except IndexError:
                data.append(0)

        lo, hi = min(data), max(data)
        self.table.blockSignals(True)
        for r in range(md.rows):
            for c in range(md.cols):
                val = data[r * md.cols + c]
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                bg = _heat(val, lo, hi)
                item.setBackground(QBrush(bg))
                item.setForeground(QBrush(QColor("#e0eaf2")))
                self.table.setItem(r, c, item)
        self.table.blockSignals(False)


class CorrectionsTab(QWidget):
    """
    Scrollable view of all 1D correction/scalar maps for the loaded ROM.
    Shows everything except the main ignition and fuel 16×16 maps.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        root.addWidget(scroll)

        self._content = QWidget()
        self._layout  = QVBoxLayout(self._content)
        self._layout.setContentsMargins(12, 12, 12, 12)
        self._layout.setSpacing(14)
        scroll.setWidget(self._content)

        self._lbl_empty = QLabel("No ROM loaded.")
        self._lbl_empty.setAlignment(Qt.AlignCenter)
        self._lbl_empty.setStyleSheet("color: #3d5068; font-size: 14px;")
        self._layout.addWidget(self._lbl_empty)
        self._layout.addStretch()

    def load_rom(self, result: DetectionResult, rom: bytes):
        # Clear old content
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if result.is_mk2:
            lbl = QLabel("G40 Mk2 — correction map addresses not yet confirmed.\nMain ignition/fuel maps available in the Maps tab.")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #e8b84b; font-size: 13px;")
            lbl.setWordWrap(True)
            self._layout.addWidget(lbl)
            self._layout.addStretch()
            return

        # Filter to 1D maps only (skip the main 16×16 ignition/fuel)
        skip = {"Ignition", "Fuel", "Ignition Map 1 (Low Load)",
                "Ignition Map 2 (Mid Load)", "Ignition Map 3 (WOT)"}
        maps_1d = [m for m in result.maps if m.name not in skip]

        if not maps_1d:
            lbl = QLabel("No correction tables found for this variant.")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #3d5068;")
            self._layout.addWidget(lbl)
        else:
            # Group into two columns
            col_a = QVBoxLayout()
            col_b = QVBoxLayout()
            for i, md in enumerate(maps_1d):
                t = _Table1D(md)
                try:
                    t.load(rom)
                except Exception:
                    pass
                (col_a if i % 2 == 0 else col_b).addWidget(t)

            row = QHBoxLayout()
            row.addLayout(col_a)
            row.addLayout(col_b)
            self._layout.addLayout(row)

        self._layout.addStretch()

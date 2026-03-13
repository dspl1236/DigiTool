"""
ui/corrections_tab.py
1D correction / scalar tables: warmup enrichment, ECT, IAT, boost cut, etc.
All tables are editable — changes write through to the shared ROM bytearray in-place.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame
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
    """Single 1D table — editable, writes through to shared ROM bytearray."""

    def __init__(self, map_def: MapDef, parent=None):
        super().__init__(parent)
        self._map_def = map_def
        self._rom: bytearray | None = None

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

        self.table.itemChanged.connect(self._on_item_changed)

    def load(self, rom: bytearray):
        self._rom = rom
        md = self._map_def
        start = md.data_addr

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
                item.setBackground(QBrush(_heat(val, lo, hi)))
                item.setForeground(QBrush(QColor("#e0eaf2")))
                self.table.setItem(r, c, item)
        self.table.blockSignals(False)

    def _on_item_changed(self, item: QTableWidgetItem):
        """Validate and write changed cell back to the shared ROM bytearray."""
        if self._rom is None:
            return
        try:
            val = int(item.text())
        except ValueError:
            self._revert_cell(item)
            return

        if not (0 <= val <= 255):
            self._revert_cell(item)
            return

        r, c = item.row(), item.column()
        offset = self._map_def.data_addr + r * self._map_def.cols + c
        if offset < len(self._rom):
            self._rom[offset] = val

        # Recolor based on new range
        all_vals = [self._rom[self._map_def.data_addr + i] for i in range(self._map_def.size)]
        lo, hi = min(all_vals), max(all_vals)
        self.table.blockSignals(True)
        item.setBackground(QBrush(_heat(val, lo, hi)))
        item.setForeground(QBrush(QColor("#e0eaf2")))
        self.table.blockSignals(False)

    def _revert_cell(self, item: QTableWidgetItem):
        """Revert a cell to the current ROM value after bad input."""
        if self._rom is None:
            return
        r, c = item.row(), item.column()
        offset = self._map_def.data_addr + r * self._map_def.cols + c
        if offset < len(self._rom):
            self.table.blockSignals(True)
            item.setText(str(self._rom[offset]))
            self.table.blockSignals(False)

    def write_back(self, rom: bytearray) -> bytearray:
        """Write current table values into the given ROM bytearray."""
        md = self._map_def
        self.table.blockSignals(True)
        for r in range(md.rows):
            for c in range(md.cols):
                item = self.table.item(r, c)
                if item is None:
                    continue
                try:
                    val = max(0, min(255, int(item.text())))
                except ValueError:
                    continue
                offset = md.data_addr + r * md.cols + c
                if offset < len(rom):
                    rom[offset] = val
        self.table.blockSignals(False)
        return rom


class CorrectionsTab(QWidget):
    """
    Scrollable view of all 1D correction/scalar maps for the loaded ROM.
    All tables are editable and write through to the shared ROM bytearray.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tables: list[_Table1D] = []
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

    def load_rom(self, result: DetectionResult, rom: bytearray):
        self._tables = []

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

        skip = {"Ignition", "Fuel", "Ignition Map 1 (Low Load)",
                "Ignition Map 2 (Mid Load)", "Ignition Map 3 (WOT)"}
        maps_1d = [m for m in result.maps if m.name not in skip]

        if not maps_1d:
            lbl = QLabel("No correction tables found for this variant.")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #3d5068;")
            self._layout.addWidget(lbl)
        else:
            col_a = QVBoxLayout()
            col_b = QVBoxLayout()
            for i, md in enumerate(maps_1d):
                t = _Table1D(md)
                try:
                    t.load(rom)
                except Exception:
                    pass
                self._tables.append(t)
                (col_a if i % 2 == 0 else col_b).addWidget(t)

            row = QHBoxLayout()
            row.addLayout(col_a)
            row.addLayout(col_b)
            self._layout.addLayout(row)

        self._layout.addStretch()

    def write_back(self, rom: bytearray) -> bytearray:
        """Write all 1D table edits into the given ROM bytearray and return it."""
        for t in self._tables:
            rom = t.write_back(rom)
        return rom

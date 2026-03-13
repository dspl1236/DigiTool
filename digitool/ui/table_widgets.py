"""
ui/table_widgets.py
Shared editable 1D table widget and helpers used by all correction tabs.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush

from digitool.rom_profiles import MapDef


def heat_color(val: int, lo: int, hi: int) -> QColor:
    if hi == lo:
        return QColor("#1a2332")
    t = max(0.0, min(1.0, (val - lo) / (hi - lo)))
    if t < 0.5:
        u = t / 0.5
        return QColor(0, int(u * 200), int(100 + u * 155))
    else:
        u = (t - 0.5) / 0.5
        return QColor(int(u * 255), int(200 - u * 200), 0)


class Table1D(QWidget):
    """
    Editable 1D (or flat 2D) table — writes changed cells through to
    the shared ROM bytearray in-place immediately on edit.
    """

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
        data = [rom[md.data_addr + i] if md.data_addr + i < len(rom) else 0
                for i in range(md.size)]
        lo, hi = min(data), max(data)
        self.table.blockSignals(True)
        for r in range(md.rows):
            for c in range(md.cols):
                val = data[r * md.cols + c]
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                item.setBackground(QBrush(heat_color(val, lo, hi)))
                item.setForeground(QBrush(QColor("#e0eaf2")))
                self.table.setItem(r, c, item)
        self.table.blockSignals(False)

    def _on_item_changed(self, item: QTableWidgetItem):
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
        all_vals = [self._rom[self._map_def.data_addr + i]
                    for i in range(self._map_def.size)]
        lo, hi = min(all_vals), max(all_vals)
        self.table.blockSignals(True)
        item.setBackground(QBrush(heat_color(val, lo, hi)))
        item.setForeground(QBrush(QColor("#e0eaf2")))
        self.table.blockSignals(False)

    def _revert_cell(self, item: QTableWidgetItem):
        if self._rom is None:
            return
        r, c = item.row(), item.column()
        offset = self._map_def.data_addr + r * self._map_def.cols + c
        if offset < len(self._rom):
            self.table.blockSignals(True)
            item.setText(str(self._rom[offset]))
            self.table.blockSignals(False)

    def write_back(self, rom: bytearray) -> bytearray:
        md = self._map_def
        self.table.blockSignals(True)
        for r in range(md.rows):
            for c in range(md.cols):
                it = self.table.item(r, c)
                if it is None:
                    continue
                try:
                    val = max(0, min(255, int(it.text())))
                except ValueError:
                    continue
                offset = md.data_addr + r * md.cols + c
                if offset < len(rom):
                    rom[offset] = val
        self.table.blockSignals(False)
        return rom


class CorrectionTabBase(QWidget):
    """
    Base class for all correction tabs.
    Subclasses define _MAP_NAMES (ordered list of map names to show)
    and call _build_tables(result, rom) from load_rom().
    """

    _MAP_NAMES: list[str] = []   # override in subclass

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tables: list[Table1D] = []
        self._rom: bytearray | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        root.addWidget(scroll)

        self._content = QWidget()
        self._grid = QHBoxLayout(self._content)
        self._grid.setContentsMargins(12, 12, 12, 12)
        self._grid.setSpacing(16)
        scroll.setWidget(self._content)

        self._col_a = QVBoxLayout()
        self._col_b = QVBoxLayout()
        self._col_a.setSpacing(14)
        self._col_b.setSpacing(14)
        self._grid.addLayout(self._col_a)
        self._grid.addLayout(self._col_b)

        self._show_placeholder("No ROM loaded.")

    def _show_placeholder(self, msg: str):
        self._clear_cols()
        lbl = QLabel(msg)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color: #3d5068; font-size: 13px;")
        lbl.setWordWrap(True)
        self._col_a.addWidget(lbl)
        self._col_a.addStretch()
        self._col_b.addStretch()

    def _clear_cols(self):
        self._tables = []
        for layout in (self._col_a, self._col_b):
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

    def load_rom(self, result, rom: bytearray):
        self._rom = rom
        self._clear_cols()

        if result.is_mk2:
            self._show_placeholder(
                "G40 Mk2 — correction map addresses not yet confirmed."
            )
            return

        # Build a name→MapDef lookup from result.maps
        map_lookup = {m.name: m for m in result.maps}
        found = [map_lookup[n] for n in self._MAP_NAMES if n in map_lookup]

        if not found:
            self._show_placeholder("No tables available for this variant.")
            return

        for i, md in enumerate(found):
            t = Table1D(md)
            t.load(rom)
            self._tables.append(t)
            if i % 2 == 0:
                self._col_a.addWidget(t)
            else:
                self._col_b.addWidget(t)

        self._col_a.addStretch()
        self._col_b.addStretch()

    def write_back(self, rom: bytearray) -> bytearray:
        for t in self._tables:
            rom = t.write_back(rom)
        return rom

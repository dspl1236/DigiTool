"""
ui/map_table.py
Reusable 16×16 (and N×M) heatmap table widget for DigiTool.
"""

from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QBrush


def _heat_color(value: float, lo: float, hi: float) -> QColor:
    """Blue (lo) → Cyan → Green → Yellow → Red (hi)."""
    if hi == lo:
        return QColor("#1a2332")
    t = max(0.0, min(1.0, (value - lo) / (hi - lo)))
    if t < 0.25:
        u = t / 0.25
        return QColor(0, int(u * 180), int(120 + u * 135))
    elif t < 0.5:
        u = (t - 0.25) / 0.25
        return QColor(0, int(180 + u * 75), int(255 - u * 255))
    elif t < 0.75:
        u = (t - 0.5) / 0.25
        return QColor(int(u * 255), 255, 0)
    else:
        u = (t - 0.75) / 0.25
        return QColor(255, int(255 - u * 255), 0)


def _ign_color(raw: int) -> QColor:
    """Signed-aware colour for ignition maps (retard = blue, advance = red)."""
    signed = raw if raw < 128 else raw - 256
    return _heat_color(signed, -10, 40)


class MapTable(QTableWidget):
    """
    Editable N×M table with heatmap background.

    map_type:
      'ign'  — ignition, signed-aware colouring, shows °BTDC
      'fuel' — fuel, unsigned 0-255 scale
      'raw'  — raw bytes, unsigned 0-255 scale
    """

    cell_selected = pyqtSignal(int, int, int, float)   # row, col, raw, display

    def __init__(self, rows: int, cols: int, map_type: str = "raw", parent=None):
        super().__init__(rows, cols, parent)
        self.map_type   = map_type
        self._data      = [0] * (rows * cols)
        self._rows      = rows
        self._cols      = cols
        self._editable  = True

        self._setup_table()
        self.itemChanged.connect(self._on_cell_changed)
        self.currentCellChanged.connect(self._on_cell_selected)

    # ── Setup ─────────────────────────────────────────────────────────────────

    def _setup_table(self):
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setMinimumSectionSize(36)
        self.verticalHeader().setMinimumSectionSize(22)
        font = QFont("Consolas", 10)
        self.setFont(font)
        self.setEditTriggers(
            QTableWidget.DoubleClicked | QTableWidget.SelectedClicked
        )

    def set_axis_labels(self, row_labels: list, col_labels: list):
        self.setVerticalHeaderLabels([str(x) for x in row_labels])
        self.setHorizontalHeaderLabels([str(x) for x in col_labels])

    # ── Data ──────────────────────────────────────────────────────────────────

    def load_data(self, data: list):
        """Load flat list of raw bytes (len = rows*cols)."""
        self._data = list(data)
        self._refresh()

    def get_data(self) -> list:
        """Return current flat list of raw bytes."""
        return list(self._data)

    def _refresh(self):
        self.blockSignals(True)
        lo = min(self._data)
        hi = max(self._data)
        for r in range(self._rows):
            for c in range(self._cols):
                raw = self._data[r * self._cols + c]
                display = self._display(raw)
                item = QTableWidgetItem(f"{display:.1f}" if isinstance(display, float) else str(display))
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(QBrush(QColor("#e0eaf2")))
                if self.map_type == "ign":
                    bg = _ign_color(raw)
                else:
                    bg = _heat_color(raw, lo, hi)
                item.setBackground(QBrush(bg))
                self.setItem(r, c, item)
        self.blockSignals(False)

    def _display(self, raw: int):
        if self.map_type == "ign":
            return round((210 - raw) / 2.86, 1)
        return raw

    def _raw_from_display(self, display_str: str, row: int, col: int) -> int:
        try:
            val = float(display_str)
        except ValueError:
            return self._data[row * self._cols + col]
        if self.map_type == "ign":
            return max(0, min(255, round(210 - val * 2.86)))
        return max(0, min(255, round(val)))

    # ── Signals ───────────────────────────────────────────────────────────────

    def _on_cell_changed(self, item: QTableWidgetItem):
        r, c = item.row(), item.column()
        raw = self._raw_from_display(item.text(), r, c)
        self._data[r * self._cols + c] = raw
        # Recolour just this cell
        self.blockSignals(True)
        lo = min(self._data)
        hi = max(self._data)
        display = self._display(raw)
        item.setText(f"{display:.1f}" if isinstance(display, float) else str(display))
        bg = _ign_color(raw) if self.map_type == "ign" else _heat_color(raw, lo, hi)
        item.setBackground(QBrush(bg))
        self.blockSignals(False)

    def _on_cell_selected(self, row, col, *_):
        if row < 0 or col < 0:
            return
        raw = self._data[row * self._cols + col]
        display = self._display(raw)
        self.cell_selected.emit(row, col, raw, display if isinstance(display, float) else float(display))

    # ── Highlight (live operating cell) ───────────────────────────────────────

    def highlight_cell(self, row: int, col: int):
        for r in range(self._rows):
            for c in range(self._cols):
                item = self.item(r, c)
                if item:
                    if r == row and c == col:
                        item.setForeground(QBrush(QColor("#00d4ff")))
                    else:
                        item.setForeground(QBrush(QColor("#e0eaf2")))

    def set_overlay(self, rpm_col: int | None, load_row: int | None,
                    o2s_rich: bool | None = None):
        """
        Paint live cursor lines and active cell highlight.
          rpm_col  — column index for current RPM (vertical cursor line)
          load_row — row index for current load (horizontal cursor line)
          o2s_rich — True=rich(green), False=lean(amber), None=no O2S data
        """
        # O2S tint colour for active cell
        if o2s_rich is True:
            tint = QColor(45, 255, 110, 50)     # green — rich
        elif o2s_rich is False:
            tint = QColor(255, 170, 0, 60)      # amber — lean
        else:
            tint = QColor(0, 212, 255, 40)      # cyan — no O2S data

        lo = min(self._data) if self._data else 0
        hi = max(self._data) if self._data else 255

        self.blockSignals(True)
        for r in range(self._rows):
            for c in range(self._cols):
                item = self.item(r, c)
                if item is None:
                    continue
                raw = self._data[r * self._cols + c]
                base = _ign_color(raw) if self.map_type == "ign" else _heat_color(raw, lo, hi)

                is_active  = (r == load_row and c == rpm_col)
                is_rpm_col = (c == rpm_col and load_row is not None)
                is_ld_row  = (r == load_row and rpm_col is not None)

                if is_active:
                    bg = QColor(
                        min(255, base.red()   + tint.red()   * tint.alpha() // 255),
                        min(255, base.green() + tint.green() * tint.alpha() // 255),
                        min(255, base.blue()  + tint.blue()  * tint.alpha() // 255),
                    )
                    item.setBackground(QBrush(bg))
                    item.setForeground(QBrush(QColor("#ffffff")))
                elif is_rpm_col or is_ld_row:
                    lighter = base.lighter(130)
                    item.setBackground(QBrush(lighter))
                    item.setForeground(QBrush(QColor("#e0eaf2")))
                else:
                    item.setBackground(QBrush(base))
                    item.setForeground(QBrush(QColor("#e0eaf2")))
        self.blockSignals(False)

    def clear_overlay(self):
        """Remove all overlay highlights — restore base heatmap colours."""
        if not self._data:
            return
        lo = min(self._data)
        hi = max(self._data)
        self.blockSignals(True)
        for r in range(self._rows):
            for c in range(self._cols):
                item = self.item(r, c)
                if item is None:
                    continue
                raw = self._data[r * self._cols + c]
                bg  = _ign_color(raw) if self.map_type == "ign" else _heat_color(raw, lo, hi)
                item.setBackground(QBrush(bg))
                item.setForeground(QBrush(QColor("#e0eaf2")))
        self.blockSignals(False)

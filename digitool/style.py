"""
style.py — DigiTool dark stylesheet (PyQt5)
Matches the tuner_app aesthetic: #080b0e background, #00d4ff accent.
"""

DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #080b0e;
    color: #bccdd8;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}

QTabWidget::pane {
    border: 1px solid #1a2332;
    background: #0d1117;
}

QTabBar::tab {
    background: #0d1117;
    color: #3d5068;
    border: 1px solid #1a2332;
    padding: 8px 20px;
    font-size: 12px;
    min-width: 130px;
}

QTabBar::tab:selected {
    background: #111820;
    color: #00d4ff;
    border-bottom: 2px solid #00d4ff;
}

QTabBar::tab:hover {
    color: #bccdd8;
    background: #111820;
}

QPushButton {
    background: #111820;
    color: #00d4ff;
    border: 1px solid #1a2332;
    padding: 6px 18px;
    font-size: 12px;
    letter-spacing: 1px;
}

QPushButton:hover {
    background: #1a2840;
    border-color: #00d4ff;
}

QPushButton:pressed {
    background: #00d4ff;
    color: #080b0e;
}

QPushButton:disabled {
    color: #3d5068;
    border-color: #1a2332;
}

QPushButton#btn_open {
    background: #0a1a10;
    color: #2dff6e;
    border-color: #2dff6e;
    font-weight: bold;
    padding: 8px 24px;
}

QPushButton#btn_open:hover  { background: #0f2a18; }

QPushButton#btn_save {
    background: #101a30;
    color: #00d4ff;
    border-color: #00d4ff;
    font-weight: bold;
}

QPushButton#btn_save:hover  { background: #182840; }

QPushButton#btn_danger {
    background: #200a0a;
    color: #ff4444;
    border-color: #ff4444;
}

QPushButton#btn_danger:hover { background: #300f0f; }

QComboBox {
    background: #111820;
    color: #bccdd8;
    border: 1px solid #1a2332;
    padding: 5px 10px;
    min-width: 160px;
}

QComboBox::drop-down { border: none; width: 24px; }

QComboBox QAbstractItemView {
    background: #111820;
    color: #bccdd8;
    border: 1px solid #1a2332;
    selection-background-color: #1a2840;
    selection-color: #00d4ff;
}

QLabel { color: #bccdd8; }

QLabel#lbl_dim   { color: #3d5068; font-size: 11px; }
QLabel#lbl_good  { color: #2dff6e; }
QLabel#lbl_warn  { color: #e8b84b; }
QLabel#lbl_bad   { color: #ff4444; }
QLabel#lbl_title {
    color: #00d4ff;
    font-size: 14px;
    font-weight: bold;
    letter-spacing: 1px;
}

QGroupBox {
    border: 1px solid #1a2332;
    border-top: 2px solid #1a2332;
    margin-top: 10px;
    padding: 12px 8px 8px 8px;
    color: #3d5068;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    color: #3d5068;
}

QTableWidget {
    background: #0d1117;
    color: #bccdd8;
    gridline-color: #1a2332;
    border: 1px solid #1a2332;
    selection-background-color: #1a2840;
    font-family: 'Consolas', monospace;
    font-size: 11px;
}

QTableWidget::item:selected {
    background: #1a2840;
    color: #00d4ff;
}

QHeaderView::section {
    background: #0d1117;
    color: #3d5068;
    border: 1px solid #1a2332;
    padding: 4px;
    font-size: 10px;
    letter-spacing: 1px;
}

QScrollBar:vertical {
    background: #0d1117;
    width: 8px;
    border: none;
}

QScrollBar::handle:vertical {
    background: #1a2332;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover { background: #3d5068; }

QScrollBar:horizontal {
    background: #0d1117;
    height: 8px;
    border: none;
}

QScrollBar::handle:horizontal {
    background: #1a2332;
    min-width: 20px;
}

QLineEdit {
    background: #111820;
    color: #bccdd8;
    border: 1px solid #1a2332;
    padding: 5px 10px;
}

QLineEdit:focus { border-color: #00d4ff; }

QSpinBox, QDoubleSpinBox {
    background: #111820;
    color: #bccdd8;
    border: 1px solid #1a2332;
    padding: 4px 8px;
}

QSpinBox:focus, QDoubleSpinBox:focus { border-color: #00d4ff; }

QStatusBar {
    background: #0d1117;
    color: #3d5068;
    border-top: 1px solid #1a2332;
    font-size: 11px;
}

QSplitter::handle { background: #1a2332; }

QTextEdit {
    background: #0d1117;
    color: #2dff6e;
    border: 1px solid #1a2332;
    font-family: 'Consolas', monospace;
    font-size: 12px;
}

QCheckBox {
    color: #bccdd8;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #1a2332;
    background: #111820;
}

QCheckBox::indicator:checked {
    background: #00d4ff;
    border-color: #00d4ff;
}

QProgressBar {
    background: #0d1117;
    border: 1px solid #1a2332;
    height: 6px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk { background: #00d4ff; }

QToolTip {
    background: #111820;
    color: #bccdd8;
    border: 1px solid #1a2332;
    padding: 4px;
    font-size: 11px;
}
"""

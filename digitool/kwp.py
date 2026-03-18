"""
digitool/kwp.py — KWPBridge integration for DigiTool.

Same pattern as hachirom/kwp.py, adapted for Digifant 1 G60/G40:

  - Digifant ECUs report RPM in group 1 cell 1 (not group 0 cell 3)
  - No closed-loop lambda — O2S is a raw voltage (0-1.1V)
  - Load is VAF signal (raw 0-255), not calculated %
  - Ignition timing not directly readable on Digifant 1

KWPBridge workflow:
  1. Launch KWPBridge.exe → ⚙ Mock ECU → Digifant 1
  2. Open DigiTool → load G60 ROM
  3. KWP monitor detects KWPBridge on :50266
  4. Safety gate: ECU part number matches ROM variant
  5. Live overlay activates on ignition and fuel maps
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)

# ── Optional imports ──────────────────────────────────────────────────────────

try:
    from kwpbridge.client import KWPClient, is_running as _kwp_is_running
    from kwpbridge.constants import DEFAULT_PORT
    _KWP_AVAILABLE = True
except ImportError:
    _KWP_AVAILABLE = False
    DEFAULT_PORT   = 50266

try:
    from PyQt5.QtCore import QObject, QTimer, pyqtSignal
    _QT_AVAILABLE = True
except ImportError:
    _QT_AVAILABLE = False


def kwpbridge_available() -> bool:
    return _KWP_AVAILABLE


def kwpbridge_running() -> bool:
    if not _KWP_AVAILABLE:
        return False
    try:
        return _kwp_is_running(port=DEFAULT_PORT)
    except Exception:
        return False


# ── Live values from Digifant state dict ──────────────────────────────────────

class LiveValues:
    """
    Decoded Digifant 1 measuring block values from a KWPBridge state dict.

    Digifant 1 group 1 layout (sent as group "0" by mock server):
      cell 1 = Engine Speed       (RPM)
      cell 2 = Engine Load        (VAF signal, raw 0-255)
      cell 3 = Coolant Temp       (inverse NTC — lower = hotter)
      cell 4 = Injection Time     (ms)

    No closed-loop lambda — O2S voltage readable separately.
    """

    def __init__(self, state: dict):
        self.rpm:         Optional[float] = None
        self.load:        Optional[float] = None   # VAF raw 0-255
        self.load_pct:    Optional[float] = None   # approx % (load/255*100)
        self.coolant:     Optional[float] = None   # approx °C
        self.inj_time:    Optional[float] = None   # injection time (raw)
        self.o2s_voltage: Optional[float] = None   # O2S 0-1.1V (if available)
        self.o2s_rich:    Optional[bool]  = None   # True=rich, False=lean, None=unknown
        self.ecu_pn:      str = ""

        if not state or not state.get("connected"):
            return

        self.ecu_pn = state.get("ecu_id", {}).get("part_number", "")

        groups = state.get("groups", {})
        # Mock sends primary group as "0" regardless of Digifant convention
        group0 = groups.get("0", groups.get(0, {}))
        cells  = {c["index"]: c for c in group0.get("cells", [])}

        def _val(idx):
            c = cells.get(idx)
            return c["value"] if c else None

        # Detect layout: Digifant has RPM at cell 1, 7A has RPM at cell 3
        pn = self.ecu_pn.upper()
        is_digifant = (pn.startswith("037906") or pn.startswith("039906")
                       or not pn)  # unknown ECU — assume Digifant in DigiTool

        if is_digifant:
            self.rpm      = _val(1)
            self.load     = _val(2)
            self.coolant  = _val(3)   # already decoded to approx °C by mock
            self.inj_time = _val(4)
        else:
            # Fallback for Motronic — shouldn't happen in DigiTool
            self.rpm     = _val(3)
            self.load    = _val(2)
            self.coolant = _val(1)

        if self.load is not None:
            self.load_pct = (self.load / 255.0) * 100.0

        # O2S voltage from group 0 cell 5 if available
        # (only present when mock sends full group 0, not group 1)
        group0_raw = groups.get("0", groups.get(0, {}))
        if isinstance(group0_raw, dict):
            cells0 = {c["index"]: c for c in group0_raw.get("cells", [])}
            o2s_cell = cells0.get(5)
            if o2s_cell and o2s_cell.get("unit") == "V":
                self.o2s_voltage = o2s_cell["value"]
                # Binary switching: <0.45V = lean, >0.65V = rich
                if self.o2s_voltage is not None:
                    self.o2s_rich = self.o2s_voltage > 0.55

    @property
    def valid(self) -> bool:
        return self.rpm is not None

    def o2s_colour(self) -> str:
        """Colour for O2S state indicator."""
        if self.o2s_rich is None:
            return "#444444"
        return "#2dff6e" if self.o2s_rich else "#ff9900"   # green=rich, amber=lean

    def o2s_label(self) -> str:
        """Rich/lean/unknown string."""
        if self.o2s_rich is None:
            return "—"
        return "RICH" if self.o2s_rich else "LEAN"


# ── Qt monitor (only when Qt + kwpbridge available) ───────────────────────────

if _QT_AVAILABLE and _KWP_AVAILABLE:

    class KWPMonitor(QObject):
        """
        Qt wrapper around KWPClient for DigiTool.

        Signals
        -------
        connected(str)        — ECU part number on connect
        disconnected()
        live_data(LiveValues) — new state at poll rate
        mismatch(str, str)    — (ecu_pn, rom_pn) when mismatch
        """

        connected    = pyqtSignal(str)
        disconnected = pyqtSignal()
        live_data    = pyqtSignal(object)    # LiveValues
        mismatch     = pyqtSignal(str, str)

        def __init__(self, parent=None):
            super().__init__(parent)
            self._client:  KWPClient | None = None
            self._rom_pn:  str = ""
            self._matched  = False

            self._timer = QTimer(self)
            self._timer.timeout.connect(self._poll)
            self._timer.start(1000)

        def set_rom_part_number(self, pn: str):
            self._rom_pn = pn.upper().replace("-", "").strip()
            self._check_match()

        def stop(self):
            self._timer.stop()
            if self._client:
                try: self._client.disconnect()
                except Exception: pass
                self._client = None

        def is_matched(self) -> bool:
            return self._matched

        def current_pn(self) -> str:
            if self._client and self._client.state:
                return self._client.state.get(
                    "ecu_id", {}).get("part_number", "")
            return ""

        def _poll(self):
            if self._client and self._client.connected:
                state = self._client.state
                if state:
                    lv = LiveValues(state)
                    if lv.valid:
                        self.live_data.emit(lv)
                    self._check_match()
                return
            if kwpbridge_running():
                self._connect_client()

        def _connect_client(self):
            try:
                self._client = KWPClient(port=DEFAULT_PORT)
                self._client.on_connect(self._on_connect)
                self._client.on_disconnect(self._on_disconnect)
                self._client.on_state(self._on_state)
                self._client.connect(auto_reconnect=False)
            except Exception as e:
                log.debug(f"KWPMonitor connect error: {e}")
                self._client = None

        def _on_connect(self):
            pn = self.current_pn()
            log.info(f"KWPMonitor: connected, ECU={pn}")
            self.connected.emit(pn)
            self._check_match()

        def _on_disconnect(self):
            self._matched = False
            self.disconnected.emit()

        def _on_state(self, state: dict):
            lv = LiveValues(state)
            if lv.valid:
                self.live_data.emit(lv)
            self._check_match()

        def _check_match(self):
            if not self._client or not self._client.state:
                self._matched = False
                return
            ecu_pn = self.current_pn().upper().replace("-", "").strip()
            if not ecu_pn or not self._rom_pn:
                self._matched = False
                return
            new_match = (ecu_pn == self._rom_pn)
            if not new_match and ecu_pn:
                self.mismatch.emit(ecu_pn, self._rom_pn)
            self._matched = new_match

else:
    class _NoOpSignal:
        def connect(self, *a, **kw):    pass
        def disconnect(self, *a, **kw): pass
        def emit(self, *a, **kw):       pass

    class KWPMonitor:   # type: ignore
        connected    = _NoOpSignal()
        disconnected = _NoOpSignal()
        live_data    = _NoOpSignal()
        mismatch     = _NoOpSignal()

        def __init__(self, parent=None): pass
        def set_rom_part_number(self, pn): pass
        def stop(self): pass
        def is_matched(self) -> bool: return False
        def current_pn(self) -> str:  return ""


# ── Status helpers ────────────────────────────────────────────────────────────

def status_label(monitor: "KWPMonitor", rom_pn: str) -> tuple[str, str]:
    """Return (text, colour) for KWP status indicator."""
    if not _KWP_AVAILABLE:
        return "KWPBridge not installed", "#555555"
    if not kwpbridge_running():
        return "KWPBridge not running", "#555555"
    ecu_pn = monitor.current_pn() if monitor else ""
    if not ecu_pn:
        return "KWPBridge running — no ECU", "#ffaa00"
    if monitor and monitor.is_matched():
        return f"🟢  {ecu_pn}  ·  ECU matches ROM", "#2dff6e"
    return f"🟡  {ecu_pn}  ≠  {rom_pn}  ·  mismatch", "#ffaa00"


def live_summary(lv: "LiveValues") -> str:
    """One-line status string."""
    if lv is None or not lv.valid:
        return ""
    parts = []
    if lv.rpm      is not None: parts.append(f"{lv.rpm:.0f} RPM")
    if lv.coolant  is not None: parts.append(f"{lv.coolant:.0f}°C")
    if lv.load_pct is not None: parts.append(f"{lv.load_pct:.0f}% load")
    if lv.inj_time is not None: parts.append(f"{lv.inj_time/10:.1f}ms inj")
    return "  ·  ".join(parts)


# ── DashboardWindow ───────────────────────────────────────────────────────────

class DashboardWindow:
    """
    Floating live-data dashboard for DigiTool / Digifant 1.

    Shows the values relevant while editing Digifant maps:
    RPM, coolant, load (VAF %), injection time, O2S voltage + rich/lean.

    Digifant 1 has no closed-loop lambda numerically — only the binary
    O2S switching signal — so the lambda gauge is replaced by an O2S
    voltage bar with a RICH/LEAN indicator.
    """

    _C_BG     = "#0d1117"
    _C_PANEL  = "#131920"
    _C_BORDER = "#1a2332"
    _C_TEXT   = "#8b9cb0"
    _C_DIM    = "#4a5568"
    _C_GREEN  = "#2dff6e"
    _C_AMBER  = "#ffaa00"
    _C_RED    = "#ff4444"
    _C_BLUE   = "#4488ff"
    _C_PURPLE = "#7c5fd4"

    def __init__(self, monitor, parent=None):
        from PyQt5.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
            QLabel, QFrame, QProgressBar,
        )
        from PyQt5.QtCore import Qt

        self._monitor = monitor
        self._win = QWidget(parent, Qt.Window)
        self._win.setWindowTitle("Live ECU — DigiTool / Digifant 1")
        self._win.setMinimumSize(560, 300)
        self._win.setStyleSheet(
            f"background:{self._C_BG}; color:{self._C_TEXT};"
        )

        root = QVBoxLayout(self._win)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        sr = QHBoxLayout()
        self._lbl_status = QLabel("● Waiting for data…")
        self._lbl_status.setStyleSheet(
            f"color:{self._C_DIM}; font-size:10px; letter-spacing:1px;"
        )
        sr.addWidget(self._lbl_status); sr.addStretch()
        root.addLayout(sr)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color:{self._C_BORDER};"); root.addWidget(sep)

        grid = QGridLayout(); grid.setSpacing(8); root.addLayout(grid)
        self._gauges = {}

        # Standard gauges: 2 rows × 3 cols
        # (key, label, unit, min, max, warn_lo, warn_hi, crit_hi, row, col)
        specs = [
            ("rpm",      "RPM",      "",   200, 7000, None, 6500, 7000, 0, 0),
            ("coolant",  "COOLANT",  "°C", -10,  120,   60,  105,  115, 0, 1),
            ("load",     "LOAD",     "%",    0,  100, None,   90,   98, 0, 2),
            ("inj_time", "INJ TIME", "ms",   1,   20, None, None, None, 1, 0),
            ("o2s",      "O2S",      "V",    0,  1.1, None, None, None, 1, 1),
        ]

        for key, label, unit, vmin, vmax, wl, wh, ch, row, col in specs:
            panel = self._make_panel(key, label, unit, vmin, vmax, wl, wh, ch)
            grid.addWidget(panel, row, col)

        # O2S rich/lean badge (col 2, row 1)
        self._o2s_badge = QLabel("—")
        self._o2s_badge.setAlignment(Qt.AlignCenter)
        self._o2s_badge.setStyleSheet(
            f"background:{self._C_PANEL}; border:1px solid {self._C_BORDER}; "
            f"border-radius:4px; color:{self._C_DIM}; font-size:24px; font-weight:bold;"
        )
        self._o2s_badge.setMinimumHeight(90)
        grid.addWidget(self._o2s_badge, 1, 2)

        sep2 = QFrame(); sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet(f"color:{self._C_BORDER};"); root.addWidget(sep2)

        self._lbl_strip = QLabel("")
        self._lbl_strip.setStyleSheet(
            f"color:{self._C_DIM}; font-size:10px; font-family:Consolas;"
        )
        root.addWidget(self._lbl_strip)

        monitor.live_data.connect(self._on_live)
        monitor.disconnected.connect(self._on_disconnect)
        monitor.connected.connect(self._on_connect)

    def _make_panel(self, key, label, unit, vmin, vmax, wl, wh, ch):
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
        from PyQt5.QtCore import Qt
        panel = QWidget()
        panel.setStyleSheet(
            f"background:{self._C_PANEL}; border:1px solid {self._C_BORDER}; border-radius:4px;"
        )
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(8, 6, 8, 6); lay.setSpacing(2)
        ln = QLabel(label)
        ln.setStyleSheet(f"color:{self._C_DIM}; font-size:9px; letter-spacing:2px; border:none;")
        lv = QLabel("—"); lv.setAlignment(Qt.AlignCenter)
        lv.setStyleSheet(f"color:{self._C_TEXT}; font-size:24px; font-weight:bold; border:none;")
        lu = QLabel(unit); lu.setAlignment(Qt.AlignCenter)
        lu.setStyleSheet(f"color:{self._C_DIM}; font-size:10px; border:none;")
        bar = QProgressBar()
        bar.setRange(int(vmin * 100), int(vmax * 100))
        bar.setValue(int(vmin * 100)); bar.setTextVisible(False); bar.setFixedHeight(4)
        bar.setStyleSheet(
            f"QProgressBar{{background:{self._C_BG}; border-radius:2px; border:none;}}"
            f"QProgressBar::chunk{{background:{self._C_GREEN}; border-radius:2px;}}"
        )
        lay.addWidget(ln); lay.addWidget(lv); lay.addWidget(lu); lay.addWidget(bar)
        self._gauges[key] = dict(lv=lv, bar=bar, unit=unit,
                                  vmin=vmin, vmax=vmax, wl=wl, wh=wh, ch=ch)
        return panel

    def _colour(self, key, val):
        if val is None: return self._C_DIM
        g = self._gauges[key]
        if g["ch"] is not None and val >= g["ch"]: return self._C_RED
        if g["wh"] is not None and val >= g["wh"]: return self._C_AMBER
        if g["wl"] is not None and val <= g["wl"]: return self._C_AMBER
        return self._C_GREEN

    def _update(self, key, val):
        if key not in self._gauges: return
        g = self._gauges[key]; col = self._colour(key, val)
        if val is None:
            g["lv"].setText("—")
            g["lv"].setStyleSheet(f"color:{self._C_DIM}; font-size:24px; font-weight:bold; border:none;")
            return
        u = g["unit"]
        txt = f"{val:.2f}" if u == "V" else f"{val:.1f}" if u == "ms" else f"{val:.0f}"
        g["lv"].setText(txt)
        g["lv"].setStyleSheet(f"color:{col}; font-size:24px; font-weight:bold; border:none;")
        clamped = max(g["vmin"], min(g["vmax"], val))
        g["bar"].setValue(int(clamped * 100))
        g["bar"].setStyleSheet(
            f"QProgressBar{{background:{self._C_BG}; border-radius:2px; border:none;}}"
            f"QProgressBar::chunk{{background:{col}; border-radius:2px;}}"
        )

    def _on_live(self, lv):
        self._update("rpm",      lv.rpm)
        self._update("coolant",  lv.coolant)
        self._update("load",     lv.load_pct)
        self._update("inj_time", lv.inj_time)
        self._update("o2s",      lv.o2s_voltage)

        # Rich/lean badge
        if lv.o2s_rich is None:
            self._o2s_badge.setText("—")
            self._o2s_badge.setStyleSheet(
                f"background:{self._C_PANEL}; border:1px solid {self._C_BORDER}; "
                f"border-radius:4px; color:{self._C_DIM}; font-size:24px; font-weight:bold;"
            )
        elif lv.o2s_rich:
            self._o2s_badge.setText("RICH")
            self._o2s_badge.setStyleSheet(
                f"background:{self._C_PANEL}; border:1px solid {self._C_BORDER}; "
                f"border-radius:4px; color:{self._C_GREEN}; font-size:24px; font-weight:bold;"
            )
        else:
            self._o2s_badge.setText("LEAN")
            self._o2s_badge.setStyleSheet(
                f"background:{self._C_PANEL}; border:1px solid {self._C_BORDER}; "
                f"border-radius:4px; color:{self._C_AMBER}; font-size:24px; font-weight:bold;"
            )

        parts = []
        if lv.rpm      is not None: parts.append(f"{lv.rpm:.0f} RPM")
        if lv.coolant  is not None: parts.append(f"{lv.coolant:.0f}°C")
        if lv.load_pct is not None: parts.append(f"{lv.load_pct:.0f}% load")
        if lv.inj_time is not None: parts.append(f"{lv.inj_time:.1f} ms")
        if lv.o2s_voltage is not None: parts.append(f"O2S {lv.o2s_voltage:.2f}V")
        self._lbl_strip.setText("  ·  ".join(parts))
        self._lbl_status.setText(f"● Live  ·  {lv.ecu_pn or '—'}")
        self._lbl_status.setStyleSheet(f"color:{self._C_GREEN}; font-size:10px; letter-spacing:1px;")

    def _on_connect(self, ecu_pn):
        self._lbl_status.setText(f"● Connected  ·  {ecu_pn}")
        self._lbl_status.setStyleSheet(f"color:{self._C_GREEN}; font-size:10px; letter-spacing:1px;")

    def _on_disconnect(self):
        self._lbl_status.setText("● Disconnected")
        self._lbl_status.setStyleSheet(f"color:{self._C_RED}; font-size:10px; letter-spacing:1px;")
        self._lbl_strip.setText("")
        for k in self._gauges: self._update(k, None)
        self._o2s_badge.setText("—")
        self._o2s_badge.setStyleSheet(
            f"background:{self._C_PANEL}; border:1px solid {self._C_BORDER}; "
            f"border-radius:4px; color:{self._C_DIM}; font-size:24px; font-weight:bold;"
        )

    def show(self):
        self._win.show(); self._win.raise_(); self._win.activateWindow()

    def hide(self): self._win.hide()
    def is_visible(self): return self._win.isVisible()

    def close(self):
        try:
            self._monitor.live_data.disconnect(self._on_live)
            self._monitor.disconnected.disconnect(self._on_disconnect)
            self._monitor.connected.disconnect(self._on_connect)
        except Exception: pass
        self._win.close()

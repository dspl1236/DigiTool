# DigiTool

**Digifant 1 ECU ROM Editor** — for VW/Audi G60 and G40 Digifant-1 ECUs (Corrado G60, Polo G40, PG-engine variants)

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20Mac-blue)
![ROM](https://img.shields.io/badge/ROM-27C256%2032KB-yellow)
![ECU](https://img.shields.io/badge/ECU-Digifant--1%20G60%2FG40-orange)
[![Build Windows EXE](https://github.com/dspl1236/DigifantTool/actions/workflows/build.yml/badge.svg)](https://github.com/dspl1236/DigifantTool/actions/workflows/build.yml)

## ⬇ Download the Desktop App (Windows)

**→ [Download DigiTool.exe (latest build)](https://github.com/dspl1236/DigifantTool/releases/latest)**

No install required. Just download and run.

---

## Features

- 🔥 **Ignition Map** — 16×16 heatmap, click any cell for °BTDC decoded value
- ⛽ **Fuel Map** — 16×16 heatmap with raw byte inspection
- 🌀 **Boost & ISV** — Boost cut (no-knock + knock), ISV control, WOT enrichment
- ⚙ **Corrections** — Warmup, ECT, IAT, knock retard, coil dwell, accel enrichment
- ⊕ **ROM Compare/Diff** — Byte-by-byte diff with map region tagging and delta
- ⚑ **ROM Detection** — Auto-identifies variant, calibration status, MAP sensor range (200 vs 250 kPa)
- ⚑ **G60 Code Flags** — Auto-detects Digilag disable, Open Loop Lambda, ISV disable patches
- 〒 **Hex View** — Full raw hex with region labels, jump-to-address/region
- ↓ **Rev Limit Editor** — Enter target RPM → calculates bytes → exports modified BIN
- ↓ **27C512 Export** — Mirrors 32KB ROM to 64KB for 27C512/27SF512 chips

## Supported ECUs

| ECU | Chip | Notes |
|-----|------|-------|
| VW Corrado G60 (PG engine) | 27C256 (32KB) | Primary target |
| VW Polo G40 Mk3 | 27C256 (32KB) | Same firmware family |
| VW Golf / Jetta G60 | 27C256 (32KB) | Compatible |
| VW Passat G60 Syncro | 27C256 (32KB) | Compatible |
| G60 Triple-Map variants | 27C256 (32KB) | Corrado SLS, SNS tunes |
| VW Polo G40 Mk2 | 27C256 (32KB) | Earlier ECU, map offsets differ |

## Map Locations (G60 PG / G40 Mk3)

| Map | Address | Size |
|-----|---------|------|
| Ignition | 0x4004 | 16×16 |
| Fuel | 0x4104 | 16×16 |
| RPM Scalar | 0x420C | 16×1 (16-bit) |
| Coil Dwell | 0x422C | 16×1 |
| Knock Retard | 0x425C | 16×1 |
| Warmup Enrichment | 0x42DD | 17×1 |
| IAT Compensation | 0x42EE | 17×1 |
| ECT Compensation 1 | 0x42FF | 17×1 |
| Boost Cut (No Knock) | 0x450F | 17×1 |
| Boost Cut (Knock) | 0x4520 | 17×1 |
| ISV Control | 0x4531 | 16×1 |
| WOT Enrichment | 0x4541 | 17×1 |
| Rev Limit (G60 single) | 0x4BF2 | 16-bit word |
| Rev Limit (G40 Mk3) | 0x5BC2 | 16-bit word |

## Usage

### Desktop App (Windows .exe)
Download from the link above — no install, just run.

### Run from Source
```bash
pip install PyQt5
python -m digitool.main
```

### Build EXE
```bash
pip install pyinstaller
python build.py
```

## G60 Code Patches Detected

| Patch | Address | Stock | Patched |
|-------|---------|-------|---------|
| Digilag Disable | 0x4433/0x4435 | 01 00 / 03 00 | 00 00 / 00 00 |
| Open Loop Lambda | 0x6269 | BD 6D 07 | 01 01 01 |
| ISV Disable | 0x6287 | BD 66 0C | 01 01 01 |

## Formula Reference

- **Ignition**: `(210 - byte_value) / 2.86 = degrees BTDC`
- **Rev Limit**: `30,000,000 / 16-bit_word = RPM`
- **RPM Scalar**: `15,000,000 / 16-bit_word = RPM`
- **Load**: `0–200 kPa (or 0–250 kPa) divided into 16 equal slices`

## Reference ROMs

Stock EPROM dumps are in [`roms/`](roms/). See [`roms/README.md`](roms/README.md) for details.

Included: G60 PG stock, G60 16v Limited, G40 Mk3 stock, G40 Mk2 stock.

## References

- [PoloG40Digifant Wiki](https://github.com/YOU54F/PoloG40Digifant/wiki) by Yousaf Nabi — Binary decompilation, map locations, XDF files
- [audi90-teensy-ecu](https://github.com/dspl1236/audi90-teensy-ecu) — Related Teensy EPROM emulator project

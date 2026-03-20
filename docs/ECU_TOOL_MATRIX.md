# ECU and Tool Coverage Matrix

Which tool for which ECU. Covers all Bosch and Hitachi ECUs from VW/Audi Group 1987–2000.

---

## Quick Reference

| Engine | Displacement | ECU family | CPU | ROM | Tool |
|--------|-------------|------------|-----|-----|------|
| G60 | 1.8L SC | Digifant 1 | HD6303 | 27C256 32KB | **DigiTool** |
| G40 | 1.3L SC | Digifant 1 | HD6303 | 27C256 32KB | **DigiTool** |
| 2E, PF, RV | 2.0 / 1.8 8v | Digifant 2 | HD6303 | 27C256 32KB | **DigiTool** |
| ABF | 2.0 16v | Digifant 3 | HD6303 | 27C256 32KB | **DigiTool** |
| ABA, ADY | 2.0 8v (Golf 3) | Digifant 3 | HD6303 | 27C256 32KB | **DigiTool** |
| 9A | 2.0 16v Corrado | Digifant 3 | HD6303 | 27C256 32KB | **DigiTool** |
| AAA, ABV, AES | 2.8 / 2.9 VR6 | Motronic M3 / MP9.0 | SAB80C535 | 27C512 64KB | **M35Tool** |
| ABA (VR6 board) | 2.0 8v | Motronic M3 | SAB80C535 | 27C512 64KB | **M35Tool** |
| AAN, 3B, ABH | 2.2 inline-5T | Motronic M2.3 | M68 | 27C512 64KB | **UrROM** |
| ABC, AAH | 2.6 V6 | Motronic M2.3.2 | M68 | 27C512 64KB | **UrROM** |
| RS2 | 2.2 inline-5T | Motronic M2.3 | M68 | 27C512 64KB | **UrROM** |
| AGU, AEB, AJL | 1.8T (20v) | Motronic M3.8.x | SAB80C535 | 27C512 EPROM | TBD |
| AGU, AEB (later) | 1.8T (20v) | Motronic M5.9.x | SAB80C535 | Flash 128–512KB | Out of scope |
| AGU+ (ME7) | 1.8T (20v) | Bosch ME7/ME7.5 | ST10 | Flash | Out of scope |
| AHF, ASV | 1.9 TDI | Bosch EDC15 | — | Flash | Out of scope |

---

## Digifant ECUs — DigiTool

### HD6303 CPU (confirmed all variants)
NOP = `0x01`. Ignition formula `(210 − raw) / 2.86 = °BTDC`. Rev limit = `30,000,000 / uint16_be`.

### Digifant 1 — G60 Supercharged

| Application | Year | ECU PN | Bosch PN | Map layout | Immo |
|-------------|------|--------|----------|------------|------|
| Corrado G60 | 1989–93 | 037906023 | 026120XXXX | Single-map | No |
| Golf G60 | 1989–92 | 037906023 | 026120XXXX | Single-map | No |
| Jetta G60 | 1990–92 | 037906023 | 026120XXXX | Single-map | No |
| Passat G60 Syncro | 1990–93 | 037906023 | 026120XXXX | Single-map | No |
| Golf G60 Limited (16v) | 1990–91 | 037906023 | 026120XXXX | Single-map | No |
| Corrado SLS / G60 triple | 1991–93 | 037906023 | 026120XXXX | Triple-map | No |

Reset vectors: `45FD` = single-map, `4C14` = triple-map.

### Digifant 1 — G40 Polo

| Application | Year | ECU PN | Map layout | Immo |
|-------------|------|--------|------------|------|
| Polo G40 Mk3 | 1990–94 | 037906025 | Single-map (same as G60) | No |
| Polo G40 Mk2 | 1987–90 | 037906023 | Mk2 layout, mirrored ROM | No |

Reset vectors: `54AA` = Mk3, `E000` = Mk2.

### Digifant 2 — Golf 2 / Jetta 2

| Application | Year | ECU PN | Bosch PN | Immo |
|-------------|------|--------|----------|------|
| Golf 2 / Jetta 2 2.0 8v (2E) | 1989–92 | 037906023B/C/D/E | 0261200262/263/264 | No |
| Golf 2 / Jetta 2 1.8 8v (PF/RV) | 1987–90 | 037906023/A | 0261200169/170 | No |

No immobilizer. Separate 7-pin Ignition Control Unit (ICU) — coil driven by ICU, not direct from ECU. Map addresses UNCONFIRMED — awaiting ROM collection.

### Digifant 3 — Golf 3 / Vento / Corrado

| Application | Year | ECU PN | Hardware | Immo |
|-------------|------|--------|----------|------|
| Golf 3 GTI 2.0 16v (ABF) | 1992–97 | 037906024G/H, 1H0906025x | Siemens 5WP4307 | **Yes** |
| Golf 3 2.0 8v (ABA/ADY) | 1992–97 | Various | Bosch/Siemens | **Yes** |
| Corrado 2.0 16v (9A) | 1991–93 | 5WP4/5WP5 | Siemens | **Yes** |

**Immobilizer present.** ROM-patchable bypass: replace `BNE`/`BEQ` branch after immo check with `NOP NOP` (HD6303: `0x01 0x01`). Addresses UNCONFIRMED pending Ghidra disassembly. See DigiTool → Immo tab.

Ghidra settings for ABF: Language = Motorola 6800, base address = **0x8000**.

---

## Motronic M3 / MP9.0 — M35Tool

### SAB80C535 CPU (8051-compatible, confirmed)
NOP = `0x00`. Ignition formula `raw × 0.75 − 22.5 = °BTDC`. Separate from Digifant.

All use 27C512 EPROM (64KB). Map addresses are file offsets into the full 64KB image.

| Application | Year | VW PN | Bosch PN | Rev | Immo |
|-------------|------|-------|----------|-----|------|
| Corrado / Golf 3 VR6 2.8 AAA (dist.) | 1992–95 | 021906258CD | 0261203041 | M3 rev1 | No |
| Corrado VR6 2.8 AAA | 1992–95 | 021906258DJ | 0261203045 | M3 rev1 | No |
| Corrado VR6 2.9 ABV | 1992–95 | 021906258AG | 0261203109 | M3 rev1 | No |
| Passat VR6 2.8 AAA | 1994–96 | 021906258BS | 0261203215 | M3 rev2 | No |
| Golf 3 VR6 2.8 AAA | 1994–96 | 021906258CH | 0261203569 | M3 rev2 | No |
| T4 Transporter VR6 AES | 1996–03 | 021906256H | 0261203971 | M3.x | No |
| Golf 3 2.0 8v ABA (M3 board) | 1994–97 | Various | 0261203720 | M3 | No |

**No immobilizer** on any of these. Pre-1995 production, pre-mandate. Nothing to patch.

---

## Motronic M2.3 / M2.3.2 — UrROM

M68-family CPU (Motorola 68000 derivative). 27C512 EPROM (64KB).

| Application | ECU family | Immo |
|-------------|------------|------|
| Audi S2 / S4 2.2T (AAN, 3B, ABH) | Bosch M2.3 | No |
| Audi S6 4.2 V8 | Bosch M2.3 | No |
| Audi A6 2.6 V6 (ABC) | Bosch M2.3.2 | No |
| Audi 100 / A6 2.6 V6 (AAH) | Bosch M2.3.2 | No |
| Audi RS2 Avant 2.2T | Bosch M2.3 | No |

---

## Bosch M3.8.x — EPROM variant (future M35Tool scope)

SAB80C535 CPU (confirmed, same as M3). 27C512 EPROM (64KB). **Has immobilizer (EEPROM-side).**

| Application | ECU PN | Bosch PN |
|-------------|--------|----------|
| A3 1.8T AGU 125hp | 06A906018C | 0261204127 |
| A3 1.8T AGU 150hp | 06A906018D | 0261204254 |
| A4 1.8T 150hp | 8D0907557T | 0261204185 |
| Golf 3 / Vento 1.8T | Various | 026120 4xxx |

**Immobilizer is EEPROM-side** (companion 93Cxx serial EEPROM). Patching the main ROM binary does not affect the immobilizer. Requires separate EEPROM read/write tooling (XPROG, TNM5000 etc.) to bypass. M35Tool does not currently implement this — planned future feature.

**Note on M3.8 vs M5.9 confusion:** Bosch `026120 4xxx` ECU numbers span both M3.8.x (EPROM) and M5.9.x (flash). Check the internal firmware version string — M5.9 files are 128–512KB flash-based and out of scope for M35Tool.

---

## Out of Scope (all tools)

| ECU family | CPU | Why out of scope |
|------------|-----|-----------------|
| Bosch ME7 / ME7.5 | ST10 (32-bit) | Flash, complex immo, WinOLS territory |
| Bosch M5.9.x | SAB80C535 | Flash-based, 128–512KB, different architecture |
| Bosch EDC15/16 (diesel) | — | Diesel ECU, different scope |
| Siemens SIMOS | — | Different manufacturer |
| Marelli IAW | — | Different manufacturer |

---

## Immobilizer Summary

| ECU | Immo present? | Type | ROM patch? | Status |
|-----|---------------|------|------------|--------|
| Digifant 1 (G60 / G40) | No | — | N/A | No action needed |
| Digifant 2 (2E / PF) | No | — | N/A | No action needed |
| Digifant 3 (ABF / ABA / 9A) | **Yes** | ROM-based (HD6303 branch) | **Yes — 2-byte NOP patch** | DigiTool Immo tab — addresses UNCONFIRMED |
| Motronic M3 VR6 (AAA/ABV/AES) | No | — | N/A | No action needed |
| Motronic M3.8.x (1.8T EPROM) | **Yes** | **EEPROM-side** (93Cxx) | **No — ROM patch doesn't work** | Requires EEPROM tooling |
| Motronic M5.9.x / ME7 | Yes | Complex | No | Out of scope |

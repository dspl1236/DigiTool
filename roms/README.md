# Reference ROMs

Stock / factory EPROM dumps for use as baselines in DigiTool.

These are 27C256 (32KB) dumps of unmodified factory EPROMs from Digifant 1 ECUs.
Provided for reference, comparison, and verification purposes only.

---

## Included ROMs

| File | Application | Rev Limit | MAP Sensor | CRC32 | Notes |
|------|-------------|-----------|------------|-------|-------|
| `G60_PG_StockEprom_022B93EE.BIN` | Corrado G60 / Golf G60 / Jetta G60 (PG engine) | 6201 RPM | 200 kPa | `0x8c6fec45` | Primary G60 reference, single-map |
| `limited_16v_G60.BIN` | G60 16v Limited (1.8 16v supercharged) | 7000 RPM | 200 kPa | `0x65550fd6` | Single-map, high-rev, higher WOT enrichment |
| `G40_StockEprom.BIN` | VW Polo G40 Mk3 | ~6601 RPM | 200 kPa | `0xb2bec49d` | Source: YOU54F/PoloG40Digifant |
| `G40_Mk2_StockEprom.BIN` | VW Polo G40 Mk2 | — | unknown | `0xbf9d8fef` | Earlier ECU generation, mirrored ROM |

> **Missing stock ROMs** — PRs welcome for verified dumps of:
> Passat G60 Syncro (`0xb6367c2f`), G60 Triple-Map stock (`0x1b198171`), Corrado SLS (`0x2cbd1e7a`)

---

## MAP Sensor Detection

DigiTool auto-detects the MAP sensor range from the firmware's ADC scaling constant.

The HD6303 firmware stores the sensor's full-scale value as a 16-bit literal:

| Opcode | Meaning | Sensor |
|--------|---------|--------|
| `CE 00 C8` | `LDX #200` | 200 kPa (standard stock) |
| `CE 00 FA` | `LDX #250` | 250 kPa (high-boost upgrade) |

In 32KB single-map ROMs where the LDX pattern falls in the fill area, the tool
falls back to scanning for `C1 C8` / `C1 FA` (`CMPB #200` / `CMPB #250`).

**All stock ROMs in this repo are 200 kPa.** No factory 250 kPa Digifant 1 ROM
has been identified yet. A tuner-modified ROM calibrated for a 250 kPa sensor
will show `CE 00 FA` in its firmware and DigiTool will badge it accordingly.

### Load axis scaling

The 16 load columns in every 16×16 map span the full ADC range (0–255).
The physical kPa value each column represents depends on which sensor is installed:

| Sensor | Full scale | Per column (÷16) |
|--------|-----------|-----------------|
| 200 kPa | 200 kPa | **12.5 kPa** |
| 250 kPa | 250 kPa | **15.6 kPa** |

Swapping sensor types without retuning the maps will cause the fuel and ignition
to be read from the wrong columns at any given boost level.

---

## Map Layout (G60 PG + G40 Mk3 — confirmed matching)

| Map | Address | Size |
|-----|---------|------|
| Ignition 16×16 | `0x4004` | 256 bytes |
| Fuel 16×16 | `0x4104` | 256 bytes |
| RPM Scalar | `0x420C` | 16 × 16-bit |
| Rev Limit (G60 single-map) | `0x4BF2` | 16-bit BE |
| Rev Limit (G40 Mk3) | `0x5BC2` | 16-bit BE |
| Rev Limit (G60 triple-map) | `0x4456` | 16-bit BE |

---

## Guidelines

- **Only stock / factory ROMs belong here.** No aftermarket tunes, no paid tune files.
- These ROMs are widely circulated in the Digifant community and are provided for
  educational and restoration purposes.
- VW/Bosch factory firmware is copyright Bosch GmbH / Volkswagen AG.

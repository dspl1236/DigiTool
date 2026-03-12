# Digifant 1 ECU — Map Locations

## G60 PG / G40 Mk3 (PY) — Standard Layout
> Shared layout. G60 ROM: `022B_93EE`. G40 Mk3 ROM: `G40_StockEprom.BIN`.
> Source: YOU54F/PoloG40Digifant (XDF by Joseph Davis / Chad Robertson)

| Map | Address | Size | Notes |
|-----|---------|------|-------|
| Ignition | 0x4004 | 16×16 | Formula: `(210 - byte) / 2.86 = °BTDC` |
| Fuel | 0x4104 | 16×16 | |
| RPM Scalar | 0x420C | 16×1 16-bit | `15,000,000 / 16bit = RPM` |
| Coil Dwell Time | 0x422C | 16×1 | |
| Knock Multiplier | 0x424C | 16×1 | |
| Knock Retard Rate | 0x425C | 16×1 | |
| Knock Decay Rate | 0x426C | 16×1 | |
| UncalledTable1 | 0x427C | 16×1 | Purpose unknown |
| Advance vs Coolant Temp | 0x429C | 17×1 | |
| Min MAP for Knock Retard | 0x428C | 16×1 | |
| Idle Advance Time | 0x42AD | 16×1 | |
| Idle Ignition High Limit | 0x42BD | 16×1 | |
| Idle Ignition Low Limit | 0x42CD | 16×1 | |
| Warm Up Enrichment | 0x42DD | 17×1 | |
| IAT Temperature Compensation | 0x42EE | 17×1 | |
| ECT Temperature Compensation 1 | 0x42FF | 17×1 | |
| ECT Temperature Compensation 2 | 0x4310 | 17×1 | |
| Startup Enrichment | 0x4321 | 17×1 | |
| Startup Enrichment vs ECT | 0x4332 | 17×1 | |
| Battery Compensation | 0x4343 | 17×1 | |
| Injector Lag | 0x4354 | 17×1 | |
| Accel Enrichment Min Delta-MAP | 0x4365 | 16×1 | |
| Accel Enrichment Multiplier vs ECT | 0x4375 | 17×1 | |
| Accel Enrichment Adder vs ECT | 0x4386 | 17×1 | |
| Accel Enrichment Adder vs ECT 2 | 0x4397 | 17×1 | |
| Pressure Raise Enrichment vs ECT | 0x43A8 | 17×1 | |
| IgnitionRelated_1 | 0x43B9 | 16×1 | Purpose TBD |
| Hot Start Enrichment | 0x43C9 | 17×1 | |
| OXS Upswing | 0x43DA | 16×4 | Lambda O2 control |
| OXS Downswing | 0x441A | 16×4 | Lambda O2 control |
| Startup ISV vs ECT | 0x446A | 17×1 | |
| Idle Ignition | 0x447B | 16×1 | |
| Boost Cut (No Knock) | 0x450F | 17×1 | |
| Boost Cut (Knock) | 0x4520 | 17×1 | |
| ISV Boost Control | 0x4531 | 16×1 | |
| WOT Enrichment | 0x4541 | 17×1 | |
| OXS Decay | 0x445A | 16×1 | |
| CO Adj vs MAP | 0x4562 | 17×1 | |
| WOT Initial Enrichment | 0x4573 | 9×5 | |
| **Rev Limit (G40 Mk3)** | **0x5BC2** | 16-bit | `30,000,000 / 16bit = RPM` |
| **Rev Limit (G60 PG)** | **0x4BF2** | 16-bit | G60 triple-map firmware |

### G60 Code Patches

| Patch | Address | Stock | Patched |
|-------|---------|-------|---------|
| Digilag disable (low RPM) | 0x4433 | `01 00` | `00 00` |
| Digilag disable (high RPM) | 0x4435 | `03 00` | `00 00` |
| Open loop lambda | 0x6269 | `BD 6D 07` | `01 01 01` |
| ISV disable | 0x6287 | `BD 66 0C` | `01 01 01` |

---

## G40 Mk2 — Different ROM Layout
> Source: YOU54F/PoloG40Digifant (`G40_Mk2_StockEprom.xdf`, authored 2014)
> ROM structure: 0x0000–0x3FFF = 0xFF fill. Code occupies 0x4000–0x7FFF.
> **The ROM is mirrored** — 0x4000–0x5FFF mirrors 0x6000–0x7FFF exactly.
> Canonical (non-mirrored) map addresses are in the 0x4000–0x5FFF range.

| # | Address | Size | Notes |
|---|---------|------|-------|
| 3 | 0x50A0 | 16×16 | **Ignition map** (avg 22.4° BTDC — plausible) |
| 4 | 0x51A0 | 16×16 | **Fuel map** (avg ~95 raw) |
| 5 | 0x48C0 | 16×1 | 1D table (corrections/scalar) |
| 6 | 0x52D2 | 16×1 | 1D table |
| 7 | 0x53E0 | 12×1 | 1D table (smaller — 12 bins) |

Mirror addresses (identical content, use canonical above):

| Mirror | Canonical |
|--------|-----------|
| 0x70A0 | 0x50A0 |
| 0x71A0 | 0x51A0 |
| 0x72D2 | 0x52D2 |
| 0x73E0 | 0x53E0 |

Rev limit: Not at 0x5BC2 (reads 0xFFFF on Mk2). Likely encoded differently — scan pending.

---

## Reset Vectors (ROM fingerprinting)

| Vector @0x7FFE | Variant |
|----------------|---------|
| `45 FD` | G60 PG triple-map |
| `54 AA` | G40 Mk3 (PY) |
| `E0 00` | G40 Mk2 |

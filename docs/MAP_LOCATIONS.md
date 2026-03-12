# Digifant 1 G60 Map Locations

Source: https://github.com/YOU54F/PoloG40Digifant/wiki/G40-Map-Table-Locations-&-Info

All addresses are direct offsets into the 32KB (0x0000–0x7FFF) ROM image.

## 2D Maps (16×16)

| Map | Start | End | Notes |
|-----|-------|-----|-------|
| Ignition | 0x4004 | 0x4103 | Formula: (210 - val) / 2.86 = °BTDC |
| Fuel | 0x4104 | 0x4203 | Raw byte, higher = richer |

## 1D Tables

| Map | Address | Size | Format |
|-----|---------|------|--------|
| RPM Scalar | 0x420C | 16×1 | 16-bit hi-lo, rpm = 15000000/val |
| Coil Dwell | 0x422C | 16×1 | 8-bit |
| Max Advance | 0x423C | 16×1 | 8-bit |
| Knock Multiplier | 0x424C | 16×1 | 8-bit |
| Knock Retard Rate | 0x425C | 16×1 | 8-bit |
| Knock Decay Rate | 0x426C | 16×1 | 8-bit |
| Warmup Enrichment | 0x42DD | 17×1 | 8-bit |
| IAT Compensation | 0x42EE | 17×1 | 8-bit |
| ECT Compensation 1 | 0x42FF | 17×1 | 8-bit |
| ECT Compensation 2 | 0x4310 | 17×1 | 8-bit |
| Startup Enrichment | 0x4321 | 17×1 | 8-bit |
| Accel Enrichment vs ECT | 0x4375 | 17×1 | 8-bit |
| Boost Cut (No Knock) | 0x450F | 17×1 | 8-bit |
| Boost Cut (Knock) | 0x4520 | 17×1 | 8-bit |
| ISV Boost Control | 0x4531 | 16×1 | 8-bit |
| WOT Enrichment | 0x4541 | 17×1 | 8-bit |
| Rev Limit | 0x5BC2 | 16-bit | rpm = 30000000/val |

## G60 Code Patches

| Patch | Address | Stock Bytes | Patch Bytes |
|-------|---------|-------------|-------------|
| Digilag disable (low RPM) | 0x4433 | 01 00 | 00 00 |
| Digilag disable (high RPM) | 0x4435 | 03 00 | 00 00 |
| Open loop lambda | 0x6269 | BD 6D 07 | 01 01 01 |
| ISV disable | 0x6287 | BD 66 0C | 01 01 01 |

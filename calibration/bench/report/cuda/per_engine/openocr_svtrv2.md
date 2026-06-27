# `openocr_svtrv2` deep dive

## Headline

- Effective accuracy: **100.0%** (550 PASS + 44 RECOVERED of 594 data cells)
- Failure modes: hallucinate=0, drop=0, substitute=44, reject=0
- Per-cell mean: **55.8 ms** (p95 58.7 ms, max 67.4 ms)
- Init: load 947 ms + warmup 321 ms
- RSS: warmup 908 MB, final 942 MB
- Subprocess wall: **36.4 s**

## Confidence distribution

min=0.601  p25=0.900  median=0.959  p75=0.998  max=1.000  mean=0.936

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 100.0% | 202+44 | 246 |
| `level` | 100.0% | 144+0 | 144 |
| `rank_level` | 100.0% | 102+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p01.r01 | `name` | RECOVERED | substitute | `'Aim'` | `'Am'` | 0.601 |
| skill p11.r03 | `name` | RECOVERED | substitute | `'Stamina'` | `'stamia'` | 0.669 |
| skill p03.r06 | `name` | RECOVERED | substitute | `'Courage'` | `'Courge'` | 0.698 |
| skill p01.r05 | `name` | RECOVERED | substitute | `'Angling'` | `'AＡngliｎg'` | 0.705 |
| skill p10.r02 | `name` | RECOVERED | substitute | `'Scan Animal'` | `'ScanAnima'` | 0.706 |
| skill p03.r05 | `name` | RECOVERED | substitute | `'Coolness'` | `'Cooinessc'` | 0.712 |
| skill p05.r04 | `name` | RECOVERED | substitute | `'Gastronomy'` | `'Gastrnomy'` | 0.728 |
| skill p10.r03 | `name` | RECOVERED | substitute | `'Scan Human'` | `'Scanuman'` | 0.730 |
| skill p12.r02 | `name` | RECOVERED | substitute | `'Translocation'` | `'Transocation'` | 0.732 |
| skill p10.r01 | `name` | RECOVERED | substitute | `'Rifle'` | `'Rifie'` | 0.761 |
| skill p08.r00 | `name` | RECOVERED | substitute | `'Melee Damage Assessment'` | `'Melee  Damage  ssessmen.'` | 0.775 |
| skill p03.r03 | `name` | RECOVERED | substitute | `'Computer'` | `'Compute'` | 0.780 |
| skill p07.r08 | `name` | RECOVERED | substitute | `'Marksmanship'` | `'Marksmanshi'` | 0.796 |
| profession p12.r03 | `name` | RECOVERED | substitute | `'Jammer'` | `'Jamme'` | 0.807 |
| profession p01.r04 | `name` | RECOVERED | substitute | `'Knifefighter (Dmg)'` | `'Knifefighter (Dmg.）'` | 0.808 |
| profession p01.r05 | `name` | RECOVERED | substitute | `'Pyro Kinetic (Dmg)'` | `'Pyro  Kinetic (Dmg.)）'` | 0.808 |
| skill p07.r00 | `name` | RECOVERED | substitute | `'Manufacture Attachments'` | `'Manufacture  ttachments'` | 0.818 |
| profession p11.r00 | `name` | RECOVERED | substitute | `'Fish Looter'` | `'FishLoote'` | 0.821 |
| profession p06.r07 | `name` | RECOVERED | substitute | `'Metal Engineer'` | `'Metal Enginee'` | 0.825 |
| skill p11.r04 | `name` | RECOVERED | substitute | `'Strength'` | `'sstrength'` | 0.830 |

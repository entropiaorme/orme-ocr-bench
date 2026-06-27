# `openocr_svtrv2` deep dive

## Headline

- Effective accuracy: **99.0%** (544 PASS + 44 RECOVERED of 594 data cells)
- Failure modes: hallucinate=0, drop=0, substitute=50, reject=0
- Per-cell mean: **0.0 ms** (p95 0.0 ms, max 0.0 ms)
- Init: load 450 ms + warmup 10 ms
- RSS: warmup 111 MB, final 313 MB
- Subprocess wall: **7.0 s**

## Confidence distribution

min=0.335  p25=0.890  median=0.951  p75=0.998  max=1.000  mean=0.925

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 100.0% | 202+44 | 246 |
| `level` | 95.8% | 138+0 | 144 |
| `rank_level` | 100.0% | 102+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p02.r00 | `level` | UNRECOVERABLE | substitute | `1` | `2` | 0.339 |
| skill p03.r00 | `level` | UNRECOVERABLE | substitute | `1` | `2` | 0.383 |
| skill p07.r00 | `level` | UNRECOVERABLE | substitute | `1` | `2` | 0.383 |
| skill p12.r00 | `level` | UNRECOVERABLE | substitute | `1` | `2` | 0.395 |
| skill p10.r00 | `level` | UNRECOVERABLE | substitute | `1` | `2` | 0.402 |
| skill p05.r00 | `level` | UNRECOVERABLE | substitute | `1` | `2` | 0.409 |
| skill p01.r01 | `name` | RECOVERED | substitute | `'Aim'` | `'Am'` | 0.599 |
| skill p11.r03 | `name` | RECOVERED | substitute | `'Stamina'` | `'stamia'` | 0.668 |
| skill p03.r06 | `name` | RECOVERED | substitute | `'Courage'` | `'Courge'` | 0.697 |
| skill p01.r05 | `name` | RECOVERED | substitute | `'Angling'` | `'AＡngliｎg'` | 0.704 |
| skill p10.r02 | `name` | RECOVERED | substitute | `'Scan Animal'` | `'ScanAnima'` | 0.706 |
| skill p03.r05 | `name` | RECOVERED | substitute | `'Coolness'` | `'Cooinessc'` | 0.712 |
| skill p05.r04 | `name` | RECOVERED | substitute | `'Gastronomy'` | `'Gastrnomy'` | 0.727 |
| skill p10.r03 | `name` | RECOVERED | substitute | `'Scan Human'` | `'Scanuman'` | 0.730 |
| skill p12.r02 | `name` | RECOVERED | substitute | `'Translocation'` | `'Transocation'` | 0.732 |
| skill p10.r01 | `name` | RECOVERED | substitute | `'Rifle'` | `'Rifie'` | 0.760 |
| skill p08.r00 | `name` | RECOVERED | substitute | `'Melee Damage Assessment'` | `'Melee  Damage  ssessmen.'` | 0.775 |
| skill p03.r03 | `name` | RECOVERED | substitute | `'Computer'` | `'Compute'` | 0.780 |
| skill p07.r08 | `name` | RECOVERED | substitute | `'Marksmanship'` | `'Marksmanshi'` | 0.796 |
| profession p01.r04 | `name` | RECOVERED | substitute | `'Knifefighter (Dmg)'` | `'Knifefighter (Dmg.）'` | 0.808 |

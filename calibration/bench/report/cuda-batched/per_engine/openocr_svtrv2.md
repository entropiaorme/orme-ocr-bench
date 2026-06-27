# `openocr_svtrv2` deep dive

## Headline

- Effective accuracy: **99.0%** (544 PASS + 44 RECOVERED of 594 data cells)
- Failure modes: hallucinate=0, drop=0, substitute=50, reject=0
- Per-cell mean: **0.0 ms** (p95 0.0 ms, max 0.0 ms)
- Init: load 1110 ms + warmup 328 ms
- RSS: warmup 907 MB, final 1036 MB
- Subprocess wall: **2.4 s**

## Confidence distribution

min=0.335  p25=0.890  median=0.950  p75=0.998  max=1.000  mean=0.925

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
| skill p02.r00 | `level` | UNRECOVERABLE | substitute | `1` | `2` | 0.340 |
| skill p03.r00 | `level` | UNRECOVERABLE | substitute | `1` | `2` | 0.382 |
| skill p07.r00 | `level` | UNRECOVERABLE | substitute | `1` | `2` | 0.384 |
| skill p12.r00 | `level` | UNRECOVERABLE | substitute | `1` | `2` | 0.396 |
| skill p10.r00 | `level` | UNRECOVERABLE | substitute | `1` | `2` | 0.404 |
| skill p05.r00 | `level` | UNRECOVERABLE | substitute | `1` | `2` | 0.409 |
| skill p01.r01 | `name` | RECOVERED | substitute | `'Aim'` | `'Am'` | 0.601 |
| skill p11.r03 | `name` | RECOVERED | substitute | `'Stamina'` | `'stamia'` | 0.669 |
| skill p03.r06 | `name` | RECOVERED | substitute | `'Courage'` | `'Courge'` | 0.698 |
| skill p01.r05 | `name` | RECOVERED | substitute | `'Angling'` | `'AＡngliｎg'` | 0.704 |
| skill p10.r02 | `name` | RECOVERED | substitute | `'Scan Animal'` | `'ScanAnima'` | 0.706 |
| skill p03.r05 | `name` | RECOVERED | substitute | `'Coolness'` | `'Cooinessc'` | 0.712 |
| skill p05.r04 | `name` | RECOVERED | substitute | `'Gastronomy'` | `'Gastrnomy'` | 0.728 |
| skill p10.r03 | `name` | RECOVERED | substitute | `'Scan Human'` | `'Scanuman'` | 0.730 |
| skill p12.r02 | `name` | RECOVERED | substitute | `'Translocation'` | `'Transocation'` | 0.732 |
| skill p10.r01 | `name` | RECOVERED | substitute | `'Rifle'` | `'Rifie'` | 0.761 |
| skill p08.r00 | `name` | RECOVERED | substitute | `'Melee Damage Assessment'` | `'Melee  Damage  ssessmen.'` | 0.775 |
| skill p03.r03 | `name` | RECOVERED | substitute | `'Computer'` | `'Compute'` | 0.780 |
| skill p07.r08 | `name` | RECOVERED | substitute | `'Marksmanship'` | `'Marksmanshi'` | 0.796 |
| profession p01.r04 | `name` | RECOVERED | substitute | `'Knifefighter (Dmg)'` | `'Knifefighter (Dmg.）'` | 0.808 |

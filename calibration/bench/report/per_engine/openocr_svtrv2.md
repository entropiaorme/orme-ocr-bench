# `openocr_svtrv2` deep dive

## Headline

- Effective accuracy: **100.0%** (550 PASS + 44 RECOVERED of 594 data cells)
- Failure modes: hallucinate=0, drop=0, substitute=44, reject=0
- Per-cell mean: **12.3 ms** (p95 19.3 ms, max 26.5 ms)
- Init: load 381 ms + warmup 12 ms
- RSS: warmup 110 MB, final 122 MB
- Subprocess wall: **8.9 s**

## Confidence distribution

min=0.599  p25=0.901  median=0.958  p75=0.998  max=1.000  mean=0.937

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
| profession p12.r03 | `name` | RECOVERED | substitute | `'Jammer'` | `'Jamme'` | 0.808 |
| profession p01.r05 | `name` | RECOVERED | substitute | `'Pyro Kinetic (Dmg)'` | `'Pyro  Kinetic (Dmg.)）'` | 0.808 |
| skill p07.r00 | `name` | RECOVERED | substitute | `'Manufacture Attachments'` | `'Manufacture  ttachments'` | 0.818 |
| profession p11.r00 | `name` | RECOVERED | substitute | `'Fish Looter'` | `'FishLoote'` | 0.822 |
| profession p06.r07 | `name` | RECOVERED | substitute | `'Metal Engineer'` | `'Metal Enginee'` | 0.825 |
| skill p11.r04 | `name` | RECOVERED | substitute | `'Strength'` | `'sstrength'` | 0.829 |

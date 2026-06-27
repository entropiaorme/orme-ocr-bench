# `ppocrv5_latin_mobile` deep dive

## Headline

- Effective accuracy: **91.4%** (460 PASS + 83 RECOVERED of 594 data cells)
- Failure modes: hallucinate=5, drop=36, substitute=92, reject=1
- Per-cell mean: **33.3 ms** (p95 36.2 ms, max 75.4 ms)
- Init: load 363 ms + warmup 340 ms
- RSS: warmup 848 MB, final 872 MB
- Subprocess wall: **21.7 s**

## Confidence distribution

min=0.200  p25=0.714  median=0.921  p75=0.993  max=1.000  mean=0.823

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 86.2% | 129+83 | 246 |
| `level` | 99.3% | 143+0 | 144 |
| `rank_level` | 84.3% | 86+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p11.r01 | `name` | UNRECOVERABLE | drop | `'Spacecraft Systems'` | `'Saca'` | 0.200 |
| profession p12.r04 | `name` | UNRECOVERABLE | drop | `'Sweat Gatherer'` | `'Sw'` | 0.243 |
| skill p07.r07 | `name` | UNRECOVERABLE | drop | `'Manufacture Weapons'` | `'n'` | 0.244 |
| skill p06.r01 | `name` | UNRECOVERABLE | drop | `'Heavy Weapons'` | `'Hea'` | 0.252 |
| skill p10.r11 | `name` | RECOVERED | drop | `'Spacecraft Engineering'` | `'Spac'` | 0.275 |
| skill p12.r09 | `name` | RECOVERED | drop | `'Wood Carving'` | `'Womow'` | 0.276 |
| profession p03.r04 | `name` | UNRECOVERABLE | drop | `'Knifefighter (Hit)'` | `'n'` | 0.277 |
| profession p03.r03 | `rank_level` | UNRECOVERABLE | drop | `23` | `'Sw'` | 0.280 |
| profession p07.r03 | `rank_level` | UNRECOVERABLE | drop | `2` | `'Bno'` | 0.281 |
| skill p04.r11 | `name` | RECOVERED | drop | `'Fishing Rod Technology'` | `'id Tc'` | 0.286 |
| skill p06.r11 | `name` | RECOVERED | drop | `'Manufacture Armor'` | `'Manuc r'` | 0.290 |
| skill p06.r06 | `name` | UNRECOVERABLE | drop | `'Laser Weaponry Technology'` | `'a ec'` | 0.301 |
| skill p11.r05 | `name` | RECOVERED | substitute | `'Support Weapon Systems'` | `'Suppot eaon'` | 0.305 |
| profession p07.r04 | `name` | UNRECOVERABLE | drop | `'Tool Engineer'` | `'T'` | 0.310 |
| skill p12.r07 | `name` | RECOVERED | substitute | `'Weapons Handling'` | `'Weaonndn'` | 0.317 |
| skill p11.r11 | `name` | UNRECOVERABLE | drop | `'Texture Pattern Matching'` | `'Text'` | 0.319 |
| skill p06.r07 | `name` | UNRECOVERABLE | reject | `'Light Melee Weapons'` | `' '` | 0.321 |
| profession p10.r04 | `name` | RECOVERED | drop | `'Treasure Hunter'` | `'Trea n'` | 0.327 |
| skill p08.r05 | `name` | RECOVERED | substitute | `'Mining Laser Operator'` | `'inin ar ratr'` | 0.329 |
| skill p10.r02 | `name` | RECOVERED | substitute | `'Scan Animal'` | `'Scan a'` | 0.329 |

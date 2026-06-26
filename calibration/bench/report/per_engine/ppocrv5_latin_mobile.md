# `ppocrv5_latin_mobile` deep dive

## Headline

- Effective accuracy: **91.1%** (452 PASS + 89 RECOVERED of 594 data cells)
- Failure modes: hallucinate=5, drop=35, substitute=101, reject=1
- Per-cell mean: **50.6 ms** (p95 112.7 ms, max 153.4 ms)
- Init: load 202 ms + warmup 116 ms
- RSS: warmup 87 MB, final 89 MB
- Subprocess wall: **32.1 s**

## Confidence distribution

min=0.195  p25=0.713  median=0.922  p75=0.993  max=1.000  mean=0.822

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 85.4% | 121+89 | 246 |
| `level` | 99.3% | 143+0 | 144 |
| `rank_level` | 84.3% | 86+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p11.r01 | `name` | UNRECOVERABLE | drop | `'Spacecraft Systems'` | `'Sac'` | 0.195 |
| profession p12.r04 | `name` | UNRECOVERABLE | drop | `'Sweat Gatherer'` | `'Sw'` | 0.242 |
| skill p07.r07 | `name` | UNRECOVERABLE | drop | `'Manufacture Weapons'` | `'n'` | 0.243 |
| skill p06.r01 | `name` | UNRECOVERABLE | drop | `'Heavy Weapons'` | `'ea'` | 0.254 |
| skill p12.r09 | `name` | UNRECOVERABLE | drop | `'Wood Carving'` | `'amow'` | 0.259 |
| skill p10.r11 | `name` | RECOVERED | drop | `'Spacecraft Engineering'` | `'Spac'` | 0.273 |
| profession p03.r04 | `name` | UNRECOVERABLE | drop | `'Knifefighter (Hit)'` | `'n'` | 0.277 |
| profession p03.r03 | `rank_level` | UNRECOVERABLE | drop | `23` | `'Sw'` | 0.279 |
| profession p07.r03 | `rank_level` | UNRECOVERABLE | drop | `2` | `'Bno'` | 0.281 |
| skill p04.r11 | `name` | RECOVERED | drop | `'Fishing Rod Technology'` | `'id Tc'` | 0.285 |
| skill p06.r11 | `name` | RECOVERED | drop | `'Manufacture Armor'` | `'Manuc r'` | 0.287 |
| skill p06.r06 | `name` | UNRECOVERABLE | drop | `'Laser Weaponry Technology'` | `'a ec'` | 0.301 |
| skill p11.r05 | `name` | RECOVERED | substitute | `'Support Weapon Systems'` | `'Suppot eaon'` | 0.303 |
| profession p07.r04 | `name` | UNRECOVERABLE | drop | `'Tool Engineer'` | `'T'` | 0.310 |
| skill p12.r07 | `name` | RECOVERED | substitute | `'Weapons Handling'` | `'Weaonndn'` | 0.312 |
| skill p11.r11 | `name` | UNRECOVERABLE | drop | `'Texture Pattern Matching'` | `'Text'` | 0.317 |
| skill p06.r07 | `name` | UNRECOVERABLE | reject | `'Light Melee Weapons'` | `' '` | 0.320 |
| skill p10.r02 | `name` | RECOVERED | substitute | `'Scan Animal'` | `'Scan a'` | 0.327 |
| profession p10.r04 | `name` | RECOVERED | drop | `'Treasure Hunter'` | `'Trea n'` | 0.328 |
| skill p08.r03 | `name` | RECOVERED | substitute | `'Mindforce Harmony'` | `'indforc aron'` | 0.331 |

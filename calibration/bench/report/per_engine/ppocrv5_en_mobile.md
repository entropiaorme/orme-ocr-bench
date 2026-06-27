# `ppocrv5_en_mobile` deep dive

## Headline

- Effective accuracy: **86.7%** (474 PASS + 41 RECOVERED of 594 data cells)
- Failure modes: hallucinate=7, drop=35, substitute=61, reject=17
- Per-cell mean: **51.6 ms** (p95 112.8 ms, max 130.8 ms)
- Init: load 179 ms + warmup 111 ms
- RSS: warmup 86 MB, final 88 MB
- Subprocess wall: **32.6 s**

## Confidence distribution

min=0.000  p25=0.563  median=0.917  p75=0.993  max=1.000  mean=0.769

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 83.7% | 165+41 | 246 |
| `level` | 95.1% | 137+0 | 144 |
| `rank_level` | 68.6% | 70+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p01.r07 | `name` | UNRECOVERABLE | reject | `'Animal Taming'` | `''` | 0.000 |
| skill p05.r07 | `level` | UNRECOVERABLE | reject | `2` | `''` | 0.000 |
| skill p06.r03 | `name` | UNRECOVERABLE | reject | `'Inflict Ranged Damage'` | `''` | 0.000 |
| skill p07.r02 | `name` | UNRECOVERABLE | reject | `'Manufacture Enhancers'` | `''` | 0.000 |
| skill p07.r06 | `name` | UNRECOVERABLE | reject | `'Manufacture Vehicle'` | `''` | 0.000 |
| skill p07.r07 | `name` | UNRECOVERABLE | reject | `'Manufacture Weapons'` | `''` | 0.000 |
| skill p08.r06 | `name` | UNRECOVERABLE | reject | `'Mining Laser Technology'` | `''` | 0.000 |
| skill p12.r05 | `level` | UNRECOVERABLE | reject | `25` | `''` | 0.000 |
| skill p12.r06 | `name` | UNRECOVERABLE | reject | `'Weapon Technology'` | `''` | 0.000 |
| profession p04.r04 | `rank_level` | UNRECOVERABLE | reject | `9` | `''` | 0.000 |
| profession p07.r03 | `rank_level` | UNRECOVERABLE | reject | `2` | `''` | 0.000 |
| profession p07.r04 | `rank_level` | UNRECOVERABLE | reject | `2` | `''` | 0.000 |
| profession p12.r04 | `rank_level` | UNRECOVERABLE | reject | `8` | `''` | 0.000 |
| profession p08.r04 | `rank_level` | UNRECOVERABLE | reject | `2` | `' '` | 0.099 |
| profession p11.r04 | `rank_level` | UNRECOVERABLE | drop | `2` | `' n'` | 0.140 |
| profession p08.r03 | `rank_level` | UNRECOVERABLE | drop | `2` | `'Gen'` | 0.157 |
| skill p04.r03 | `level` | UNRECOVERABLE | substitute | `13` | `1` | 0.158 |
| skill p01.r11 | `name` | UNRECOVERABLE | drop | `'Attachments Technology'` | `'enolo'` | 0.175 |
| skill p06.r07 | `name` | UNRECOVERABLE | drop | `'Light Melee Weapons'` | `'e   on'` | 0.175 |
| skill p03.r08 | `name` | UNRECOVERABLE | drop | `'Deep Ocean Fishing'` | `'eihin'` | 0.180 |

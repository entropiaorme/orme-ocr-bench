# `florence2_base` deep dive

## Headline

- Effective accuracy: **46.0%** (219 PASS + 54 RECOVERED of 594 data cells)
- Failure modes: hallucinate=0, drop=106, substitute=269, reject=0
- Per-cell mean: **144.7 ms** (p95 178.3 ms, max 239.7 ms)
- Init: load 19110 ms + warmup 1004 ms
- RSS: warmup 1735 MB, final 1790 MB
- Subprocess wall: **111.7 s**

## Confidence distribution

min=0.249  p25=0.496  median=0.695  p75=0.804  max=0.982  mean=0.652

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 35.4% | 33+54 | 246 |
| `level` | 79.2% | 114+0 | 144 |
| `rank_level` | 12.7% | 13+0 | 102 |
| `percent` | 57.8% | 59+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p09.r09 | `name` | RECOVERED | substitute | `'Ranged Damage Assessment'` | `'Kangen Dansing Assessn'` | 0.249 |
| skill p07.r08 | `name` | UNRECOVERABLE | substitute | `'Marksmanship'` | `'LAVISAN'` | 0.264 |
| skill p07.r00 | `name` | UNRECOVERABLE | substitute | `'Manufacture Attachments'` | `'Lanvelleme Avechiens'` | 0.277 |
| skill p01.r11 | `name` | UNRECOVERABLE | substitute | `'Attachments Technology'` | `'AMANIS ICONNOV'` | 0.278 |
| skill p03.r08 | `name` | UNRECOVERABLE | drop | `'Deep Ocean Fishing'` | `'WOW OEN'` | 0.290 |
| skill p03.r11 | `name` | UNRECOVERABLE | drop | `'Dispense Decoy'` | `'MOMAS'` | 0.295 |
| skill p07.r03 | `name` | UNRECOVERABLE | substitute | `'Manufacture Mechanical Equipment'` | `'HANNAHNE HENANICAL E'` | 0.296 |
| skill p05.r04 | `name` | UNRECOVERABLE | substitute | `'Gastronomy'` | `'CAMVIN'` | 0.296 |
| skill p03.r00 | `name` | UNRECOVERABLE | substitute | `'Color Matching'` | `'WOW WALL'` | 0.297 |
| skill p06.r00 | `name` | UNRECOVERABLE | substitute | `'Heavy Melee Weapons'` | `'Havn Hiee HEWONS'` | 0.302 |
| skill p06.r11 | `name` | UNRECOVERABLE | drop | `'Manufacture Armor'` | `'LAMMA'` | 0.307 |
| skill p08.r00 | `name` | RECOVERED | substitute | `'Melee Damage Assessment'` | `'Mae Danana Assasnien'` | 0.308 |
| skill p12.r06 | `name` | UNRECOVERABLE | drop | `'Weapon Technology'` | `'MAMN'` | 0.308 |
| skill p08.r11 | `name` | UNRECOVERABLE | substitute | `'Plastic Surgery'` | `'MAMIA SWIMON'` | 0.315 |
| skill p10.r00 | `name` | UNRECOVERABLE | substitute | `'Resource Gathering'` | `'RESVIE CALGIN'` | 0.315 |
| skill p02.r03 | `name` | UNRECOVERABLE | substitute | `'Bioregenesis'` | `'PANMYSIC'` | 0.316 |
| profession p04.r06 | `rank_level` | UNRECOVERABLE | drop | `9` | `'inlal'` | 0.316 |
| profession p04.r04 | `rank_level` | UNRECOVERABLE | drop | `9` | `'inlal'` | 0.316 |
| profession p04.r05 | `rank_level` | UNRECOVERABLE | drop | `9` | `'inlal'` | 0.318 |
| profession p01.r04 | `rank_level` | UNRECOVERABLE | drop | `36` | `'VeLg'` | 0.323 |

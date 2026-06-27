# `ppocrv5_mobile` deep dive

## Headline

- Effective accuracy: **96.0%** (542 PASS + 28 RECOVERED of 594 data cells)
- Failure modes: hallucinate=9, drop=0, substitute=43, reject=0
- Per-cell mean: **36.4 ms** (p95 37.5 ms, max 81.1 ms)
- Init: load 413 ms + warmup 368 ms
- RSS: warmup 881 MB, final 903 MB
- Subprocess wall: **23.8 s**

## Confidence distribution

min=0.235  p25=0.920  median=0.976  p75=0.995  max=1.000  mean=0.923

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 98.8% | 215+28 | 246 |
| `level` | 94.4% | 136+0 | 144 |
| `rank_level` | 87.3% | 89+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p10.r06 | `level` | UNRECOVERABLE | hallucinate | `1` | `12` | 0.235 |
| skill p12.r03 | `level` | UNRECOVERABLE | hallucinate | `1` | `102` | 0.266 |
| profession p04.r04 | `name` | RECOVERED | substitute | `'BLP Sniper (Hit)'` | `'caLPSniperHit'` | 0.311 |
| profession p12.r04 | `name` | UNRECOVERABLE | substitute | `'Sweat Gatherer'` | `'cYnaaeataGateeer'` | 0.354 |
| profession p10.r04 | `name` | RECOVERED | substitute | `'Treasure Hunter'` | `'cTaeeetuntew'` | 0.372 |
| skill p02.r01 | `level` | UNRECOVERABLE | hallucinate | `1` | `15` | 0.401 |
| profession p01.r04 | `name` | RECOVERED | substitute | `'Knifefighter (Dmg)'` | `'cYnfefghteDmg'` | 0.408 |
| skill p10.r01 | `name` | RECOVERED | hallucinate | `'Rifle'` | `'Rifle美楼一'` | 0.410 |
| profession p02.r01 | `rank_level` | UNRECOVERABLE | substitute | `33` | `'Yansperingm3lb'` | 0.419 |
| skill p03.r00 | `level` | UNRECOVERABLE | hallucinate | `1` | `12` | 0.427 |
| profession p03.r04 | `name` | UNRECOVERABLE | substitute | `'Knifefighter (Hit)'` | `'cYmnegtaow'` | 0.439 |
| profession p14.r04 | `name` | RECOVERED | substitute | `'Hair Stylist'` | `'cYartliselwb'` | 0.439 |
| profession p02.r04 | `name` | RECOVERED | substitute | `'Ranged BLP (Dmg)'` | `'RangedbLPDmg'` | 0.499 |
| skill p02.r05 | `level` | UNRECOVERABLE | hallucinate | `1` | `19` | 0.500 |
| skill p08.r06 | `name` | RECOVERED | substitute | `'Mining Laser Technology'` | `'[maning LaserTechnologyw'` | 0.520 |
| skill p07.r05 | `level` | UNRECOVERABLE | hallucinate | `1` | `10` | 0.541 |
| profession p05.r04 | `name` | RECOVERED | substitute | `'Grenadier (Hit)'` | `'cGrenadierHitw'` | 0.565 |
| profession p08.r01 | `rank_level` | UNRECOVERABLE | substitute | `2` | `'cYBegnnnerlb'` | 0.577 |
| profession p13.r04 | `name` | UNRECOVERABLE | substitute | `'Pet Handler'` | `'caanlow'` | 0.591 |
| profession p06.r04 | `name` | RECOVERED | substitute | `'Longblades Engineer'` | `'Yongblades Engnneer'` | 0.601 |

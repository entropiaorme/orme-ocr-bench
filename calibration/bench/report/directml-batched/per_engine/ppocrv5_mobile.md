# `ppocrv5_mobile` deep dive

## Headline

- Effective accuracy: **95.6%** (541 PASS + 27 RECOVERED of 594 data cells)
- Failure modes: hallucinate=9, drop=0, substitute=44, reject=0
- Per-cell mean: **0.0 ms** (p95 0.0 ms, max 0.0 ms)
- Init: load 349 ms + warmup 113 ms
- RSS: warmup 149 MB, final 232 MB
- Subprocess wall: **4.2 s**

## Confidence distribution

min=0.234  p25=0.920  median=0.976  p75=0.995  max=1.000  mean=0.923

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 98.8% | 216+27 | 246 |
| `level` | 94.4% | 136+0 | 144 |
| `rank_level` | 85.3% | 87+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p10.r06 | `level` | UNRECOVERABLE | hallucinate | `1` | `12` | 0.234 |
| skill p12.r03 | `level` | UNRECOVERABLE | hallucinate | `1` | `102` | 0.265 |
| profession p04.r04 | `name` | RECOVERED | substitute | `'BLP Sniper (Hit)'` | `'caLPSniperHit'` | 0.305 |
| profession p12.r04 | `name` | UNRECOVERABLE | substitute | `'Sweat Gatherer'` | `'cYnaaeanaGateee'` | 0.359 |
| profession p10.r04 | `name` | RECOVERED | substitute | `'Treasure Hunter'` | `'cTaeeetuntw'` | 0.374 |
| profession p01.r04 | `name` | RECOVERED | substitute | `'Knifefighter (Dmg)'` | `'cYnfefghteemg'` | 0.401 |
| skill p02.r01 | `level` | UNRECOVERABLE | hallucinate | `1` | `15` | 0.402 |
| skill p10.r01 | `name` | RECOVERED | hallucinate | `'Rifle'` | `'Rifle美楼一'` | 0.409 |
| profession p02.r01 | `rank_level` | UNRECOVERABLE | substitute | `33` | `'Yansperingm3lb'` | 0.417 |
| skill p03.r00 | `level` | UNRECOVERABLE | hallucinate | `1` | `12` | 0.428 |
| profession p03.r04 | `name` | UNRECOVERABLE | substitute | `'Knifefighter (Hit)'` | `'cYamnegtaow'` | 0.429 |
| profession p14.r04 | `name` | RECOVERED | substitute | `'Hair Stylist'` | `'cYartliselwb'` | 0.440 |
| profession p02.r04 | `name` | RECOVERED | substitute | `'Ranged BLP (Dmg)'` | `'RangedbLPDmg'` | 0.490 |
| skill p02.r05 | `level` | UNRECOVERABLE | hallucinate | `1` | `19` | 0.502 |
| skill p08.r06 | `name` | RECOVERED | substitute | `'Mining Laser Technology'` | `'[maning LaserTechnologyw'` | 0.519 |
| skill p07.r05 | `level` | UNRECOVERABLE | hallucinate | `1` | `10` | 0.541 |
| profession p05.r04 | `name` | RECOVERED | substitute | `'Grenadier (Hit)'` | `'cGrenadierHitw'` | 0.561 |
| profession p08.r01 | `rank_level` | UNRECOVERABLE | substitute | `2` | `'cYBegnnnerlb'` | 0.577 |
| profession p13.r04 | `name` | UNRECOVERABLE | substitute | `'Pet Handler'` | `'caanlow'` | 0.593 |
| skill p01.r05 | `level` | UNRECOVERABLE | hallucinate | `1` | `10` | 0.603 |

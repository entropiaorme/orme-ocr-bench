# `ppocrv5_mobile` deep dive

## Headline

- Effective accuracy: **95.8%** (541 PASS + 28 RECOVERED of 594 data cells)
- Failure modes: hallucinate=8, drop=0, substitute=45, reject=0
- Per-cell mean: **0.0 ms** (p95 0.0 ms, max 0.0 ms)
- Init: load 273 ms + warmup 289 ms
- RSS: warmup 882 MB, final 962 MB
- Subprocess wall: **5.9 s**

## Confidence distribution

min=0.236  p25=0.921  median=0.976  p75=0.995  max=1.000  mean=0.922

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 98.8% | 215+28 | 246 |
| `level` | 94.4% | 136+0 | 144 |
| `rank_level` | 86.3% | 88+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p10.r06 | `level` | UNRECOVERABLE | hallucinate | `1` | `12` | 0.236 |
| skill p12.r03 | `level` | UNRECOVERABLE | hallucinate | `1` | `102` | 0.273 |
| profession p04.r04 | `name` | RECOVERED | substitute | `'BLP Sniper (Hit)'` | `'caLPSniperHit'` | 0.311 |
| profession p12.r04 | `name` | UNRECOVERABLE | substitute | `'Sweat Gatherer'` | `'cYnaaeataGateeer'` | 0.354 |
| profession p10.r04 | `name` | RECOVERED | substitute | `'Treasure Hunter'` | `'cTaeeetuntw'` | 0.376 |
| skill p02.r01 | `level` | UNRECOVERABLE | hallucinate | `1` | `15` | 0.401 |
| profession p01.r04 | `name` | RECOVERED | substitute | `'Knifefighter (Dmg)'` | `'cYnfefghteDmg'` | 0.408 |
| profession p02.r01 | `rank_level` | UNRECOVERABLE | substitute | `33` | `'Yansperingm3b'` | 0.415 |
| skill p03.r00 | `level` | UNRECOVERABLE | hallucinate | `1` | `12` | 0.425 |
| profession p03.r04 | `name` | UNRECOVERABLE | substitute | `'Knifefighter (Hit)'` | `'cYmnegtaow'` | 0.439 |
| profession p14.r04 | `name` | RECOVERED | substitute | `'Hair Stylist'` | `'cYartliselwb'` | 0.439 |
| skill p10.r01 | `name` | RECOVERED | substitute | `'Rifle'` | `'Rifle美楼'` | 0.453 |
| profession p02.r04 | `name` | RECOVERED | substitute | `'Ranged BLP (Dmg)'` | `'RangedbLPDmg'` | 0.498 |
| skill p02.r05 | `level` | UNRECOVERABLE | hallucinate | `1` | `19` | 0.502 |
| skill p08.r06 | `name` | RECOVERED | substitute | `'Mining Laser Technology'` | `'[maning LaserTechnologyw'` | 0.521 |
| skill p07.r05 | `level` | UNRECOVERABLE | hallucinate | `1` | `10` | 0.539 |
| profession p05.r04 | `name` | RECOVERED | substitute | `'Grenadier (Hit)'` | `'cGrenadierHitw'` | 0.565 |
| profession p08.r01 | `rank_level` | UNRECOVERABLE | substitute | `2` | `'cYBegnnnerlb'` | 0.577 |
| profession p13.r04 | `name` | UNRECOVERABLE | substitute | `'Pet Handler'` | `'caanlow'` | 0.591 |
| skill p01.r05 | `level` | UNRECOVERABLE | hallucinate | `1` | `10` | 0.599 |

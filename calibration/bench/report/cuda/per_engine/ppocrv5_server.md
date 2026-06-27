# `ppocrv5_server` deep dive

## Headline

- Effective accuracy: **81.6%** (383 PASS + 102 RECOVERED of 594 data cells)
- Failure modes: hallucinate=1, drop=73, substitute=137, reject=0
- Per-cell mean: **93.4 ms** (p95 96.8 ms, max 98.5 ms)
- Init: load 491 ms + warmup 362 ms
- RSS: warmup 960 MB, final 1003 MB
- Subprocess wall: **59.4 s**

## Confidence distribution

min=0.175  p25=0.629  median=0.887  p75=0.992  max=1.000  mean=0.790

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 63.0% | 53+102 | 246 |
| `level` | 99.3% | 143+0 | 144 |
| `rank_level` | 86.3% | 88+0 | 102 |
| `percent` | 97.1% | 99+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p09.r06 | `name` | UNRECOVERABLE | drop | `'Provisioning'` | `'avs'` | 0.175 |
| skill p02.r11 | `name` | UNRECOVERABLE | drop | `'Clubs'` | `'e'` | 0.183 |
| profession p01.r06 | `name` | UNRECOVERABLE | drop | `'Cryogenic (Dmg)'` | `'yc'` | 0.222 |
| skill p09.r08 | `name` | UNRECOVERABLE | drop | `'Pyrokinesis'` | `'Patto'` | 0.248 |
| skill p06.r08 | `name` | UNRECOVERABLE | drop | `'Longblades'` | `'mnn'` | 0.257 |
| skill p12.r11 | `name` | UNRECOVERABLE | drop | `'Wounding'` | `'cao'` | 0.260 |
| skill p09.r10 | `name` | UNRECOVERABLE | drop | `'Reclaiming'` | `'an e'` | 0.272 |
| skill p10.r01 | `name` | UNRECOVERABLE | drop | `'Rifle'` | `'ae'` | 0.272 |
| skill p11.r04 | `name` | UNRECOVERABLE | drop | `'Strength'` | `'an'` | 0.272 |
| skill p12.r09 | `name` | UNRECOVERABLE | substitute | `'Wood Carving'` | `'Waoe n'` | 0.281 |
| skill p09.r03 | `name` | UNRECOVERABLE | drop | `'Probing'` | `'Pgn'` | 0.284 |
| profession p04.r04 | `name` | UNRECOVERABLE | drop | `'BLP Sniper (Hit)'` | `'a  te'` | 0.298 |
| profession p05.r04 | `name` | UNRECOVERABLE | drop | `'Grenadier (Hit)'` | `'Gaen'` | 0.299 |
| skill p08.r11 | `name` | UNRECOVERABLE | drop | `'Plastic Surgery'` | `'aaas  o'` | 0.307 |
| skill p03.r10 | `name` | UNRECOVERABLE | substitute | `'Diagnosis'` | `'canao'` | 0.307 |
| skill p02.r02 | `name` | UNRECOVERABLE | substitute | `'Biology'` | `'Beonnn'` | 0.313 |
| profession p13.r04 | `name` | UNRECOVERABLE | substitute | `'Pet Handler'` | `'caene ta'` | 0.314 |
| skill p05.r02 | `name` | UNRECOVERABLE | drop | `'Force Merge'` | `'ae n'` | 0.315 |
| profession p07.r04 | `name` | UNRECOVERABLE | drop | `'Tool Engineer'` | `'aGnn t'` | 0.321 |
| skill p10.r02 | `name` | UNRECOVERABLE | substitute | `'Scan Animal'` | `'SnGn en'` | 0.326 |

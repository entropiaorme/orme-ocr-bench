# `ppocrv5_server` deep dive

## Headline

- Effective accuracy: **81.8%** (383 PASS + 103 RECOVERED of 594 data cells)
- Failure modes: hallucinate=1, drop=73, substitute=137, reject=0
- Per-cell mean: **0.0 ms** (p95 0.0 ms, max 0.0 ms)
- Init: load 465 ms + warmup 153 ms
- RSS: warmup 164 MB, final 247 MB
- Subprocess wall: **5.4 s**

## Confidence distribution

min=0.176  p25=0.628  median=0.889  p75=0.992  max=1.000  mean=0.791

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 63.4% | 53+103 | 246 |
| `level` | 99.3% | 143+0 | 144 |
| `rank_level` | 86.3% | 88+0 | 102 |
| `percent` | 97.1% | 99+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p09.r06 | `name` | UNRECOVERABLE | drop | `'Provisioning'` | `'avs'` | 0.176 |
| skill p02.r11 | `name` | UNRECOVERABLE | drop | `'Clubs'` | `'e'` | 0.182 |
| profession p01.r06 | `name` | UNRECOVERABLE | drop | `'Cryogenic (Dmg)'` | `'yc'` | 0.222 |
| skill p09.r08 | `name` | UNRECOVERABLE | drop | `'Pyrokinesis'` | `'Patto'` | 0.249 |
| skill p06.r08 | `name` | UNRECOVERABLE | drop | `'Longblades'` | `'mnn'` | 0.256 |
| skill p12.r11 | `name` | UNRECOVERABLE | drop | `'Wounding'` | `'cao'` | 0.259 |
| skill p09.r10 | `name` | UNRECOVERABLE | drop | `'Reclaiming'` | `'an e'` | 0.272 |
| skill p11.r04 | `name` | UNRECOVERABLE | drop | `'Strength'` | `'an'` | 0.273 |
| skill p10.r01 | `name` | UNRECOVERABLE | drop | `'Rifle'` | `'ae'` | 0.274 |
| skill p12.r09 | `name` | RECOVERED | substitute | `'Wood Carving'` | `'Wooe n'` | 0.282 |
| skill p09.r03 | `name` | UNRECOVERABLE | drop | `'Probing'` | `'Pgn'` | 0.285 |
| profession p07.r04 | `name` | UNRECOVERABLE | drop | `'Tool Engineer'` | `'aGnnt'` | 0.286 |
| skill p05.r02 | `name` | UNRECOVERABLE | drop | `'Force Merge'` | `'ane n'` | 0.290 |
| profession p04.r04 | `name` | UNRECOVERABLE | drop | `'BLP Sniper (Hit)'` | `'a  te'` | 0.298 |
| profession p05.r04 | `name` | UNRECOVERABLE | drop | `'Grenadier (Hit)'` | `'Gaen'` | 0.300 |
| skill p08.r11 | `name` | UNRECOVERABLE | drop | `'Plastic Surgery'` | `'aaas  o'` | 0.306 |
| skill p03.r10 | `name` | UNRECOVERABLE | substitute | `'Diagnosis'` | `'canao'` | 0.309 |
| skill p02.r02 | `name` | UNRECOVERABLE | substitute | `'Biology'` | `'Beonnn'` | 0.312 |
| profession p13.r04 | `name` | UNRECOVERABLE | substitute | `'Pet Handler'` | `'caene ta'` | 0.317 |
| profession p09.r04 | `name` | UNRECOVERABLE | substitute | `'Nutritionist'` | `'cYnmntol'` | 0.323 |

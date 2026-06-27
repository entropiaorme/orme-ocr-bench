# `onnxtr_vitstr` deep dive

## Headline

- Effective accuracy: **83.5%** (291 PASS + 205 RECOVERED of 594 data cells)
- Failure modes: hallucinate=33, drop=0, substitute=270, reject=0
- Per-cell mean: **234.6 ms** (p95 526.5 ms, max 906.1 ms)
- Init: load 36058 ms + warmup 1075 ms
- RSS: warmup 247 MB, final 254 MB
- Subprocess wall: **183.8 s**

## Confidence distribution

min=0.681  p25=0.928  median=0.983  p75=0.999  max=1.000  mean=0.955

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 96.7% | 33+205 | 246 |
| `level` | 100.0% | 144+0 | 144 |
| `rank_level` | 62.7% | 64+0 | 102 |
| `percent` | 49.0% | 50+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| profession p04.r00 | `percent` | UNRECOVERABLE | substitute | `64.9` | `66.9` | 0.681 |
| profession p06.r07 | `name` | RECOVERED | substitute | `'Metal Engineer'` | `'MetalEngineerr'` | 0.709 |
| profession p06.r02 | `name` | RECOVERED | substitute | `'Gardener'` | `'Gardenerr-'` | 0.736 |
| profession p02.r02 | `name` | RECOVERED | substitute | `'Brawler (Dmg)'` | `'Brawler(Dmg)-'` | 0.752 |
| profession p10.r00 | `percent` | UNRECOVERABLE | substitute | `68.9` | `688.9` | 0.765 |
| profession p09.r00 | `name` | RECOVERED | substitute | `'Enhancer Constructor'` | `'EnhancerConstoonsrrucorutoor'` | 0.775 |
| profession p08.r02 | `percent` | UNRECOVERABLE | substitute | `64.6` | `664.0` | 0.778 |
| profession p07.r02 | `percent` | UNRECOVERABLE | substitute | `84.4` | `844.0` | 0.785 |
| profession p07.r06 | `percent` | UNRECOVERABLE | substitute | `64.6` | `664.0` | 0.793 |
| profession p06.r06 | `percent` | UNRECOVERABLE | substitute | `56.2` | `566.0` | 0.794 |
| profession p05.r00 | `name` | RECOVERED | substitute | `'Mounted Laser (Hit)'` | `'MountedLaaerr(Hittt'` | 0.794 |
| profession p02.r00 | `name` | RECOVERED | substitute | `'One Handed Clubber (Dmg)'` | `"One'aaddedClubbrrDDmg)"` | 0.799 |
| profession p08.r01 | `percent` | UNRECOVERABLE | substitute | `64.6` | `664.0` | 0.803 |
| profession p08.r00 | `percent` | UNRECOVERABLE | substitute | `64.6` | `664.0` | 0.806 |
| profession p06.r03 | `percent` | UNRECOVERABLE | substitute | `73.7` | `733.0` | 0.806 |
| profession p07.r07 | `percent` | UNRECOVERABLE | substitute | `64.6` | `664.0` | 0.808 |
| profession p01.r00 | `percent` | UNRECOVERABLE | substitute | `46.2` | `466.0` | 0.811 |
| profession p02.r07 | `percent` | UNRECOVERABLE | substitute | `9.5` | `9.55` | 0.814 |
| profession p09.r00 | `rank_level` | UNRECOVERABLE | substitute | `1` | `111` | 0.815 |
| profession p14.r02 | `percent` | UNRECOVERABLE | substitute | `84.7` | `84.0` | 0.817 |

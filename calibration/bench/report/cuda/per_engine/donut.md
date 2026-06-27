# `donut` deep dive

## Headline

- Effective accuracy: **0.0%** (0 PASS + 0 RECOVERED of 594 data cells)
- Failure modes: hallucinate=0, drop=0, substitute=0, reject=594
- Per-cell mean: **1015.6 ms** (p95 1265.3 ms, max 1508.0 ms)
- Init: load 20004 ms + warmup 1283 ms
- RSS: warmup 1664 MB, final 2025 MB
- Subprocess wall: **654.5 s**

## Confidence distribution

min=0.540  p25=0.620  median=0.654  p75=0.701  max=0.750  mean=0.655

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 0.0% | 0+0 | 246 |
| `level` | 0.0% | 0+0 | 144 |
| `rank_level` | 0.0% | 0+0 | 102 |
| `percent` | 0.0% | 0+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| profession p05.r03 | `percent` | UNRECOVERABLE | reject | `9.1` | `''` | 0.540 |
| profession p10.r06 | `percent` | UNRECOVERABLE | reject | `11.5` | `''` | 0.541 |
| profession p14.r02 | `percent` | UNRECOVERABLE | reject | `84.7` | `''` | 0.548 |
| profession p05.r05 | `percent` | UNRECOVERABLE | reject | `9.1` | `''` | 0.548 |
| profession p05.r06 | `percent` | UNRECOVERABLE | reject | `14.7` | `''` | 0.549 |
| profession p10.r07 | `percent` | UNRECOVERABLE | reject | `91.3` | `''` | 0.551 |
| skill p04.r00 | `level` | UNRECOVERABLE | reject | `2534` | `''` | 0.551 |
| profession p12.r01 | `percent` | UNRECOVERABLE | reject | `51.8` | `''` | 0.551 |
| profession p01.r06 | `percent` | UNRECOVERABLE | reject | `19.6` | `''` | 0.551 |
| profession p10.r02 | `percent` | UNRECOVERABLE | reject | `51.5` | `''` | 0.551 |
| profession p01.r01 | `percent` | UNRECOVERABLE | reject | `98.1` | `''` | 0.552 |
| profession p09.r01 | `percent` | UNRECOVERABLE | reject | `69.0` | `''` | 0.552 |
| profession p10.r04 | `percent` | UNRECOVERABLE | reject | `39.7` | `''` | 0.553 |
| profession p04.r05 | `percent` | UNRECOVERABLE | reject | `32.8` | `''` | 0.553 |
| profession p10.r05 | `percent` | UNRECOVERABLE | reject | `11.6` | `''` | 0.554 |
| profession p07.r06 | `percent` | UNRECOVERABLE | reject | `64.6` | `''` | 0.554 |
| profession p07.r05 | `percent` | UNRECOVERABLE | reject | `73.0` | `''` | 0.555 |
| profession p04.r06 | `percent` | UNRECOVERABLE | reject | `32.8` | `''` | 0.555 |
| profession p03.r06 | `percent` | UNRECOVERABLE | reject | `96.5` | `''` | 0.556 |
| profession p01.r05 | `percent` | UNRECOVERABLE | reject | `19.6` | `''` | 0.556 |

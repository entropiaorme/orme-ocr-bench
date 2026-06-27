# `tesseract` deep dive

## Headline

- Effective accuracy: **84.0%** (491 PASS + 8 RECOVERED of 594 data cells)
- Failure modes: hallucinate=66, drop=1, substitute=36, reject=0
- Per-cell mean: **632.4 ms** (p95 1114.3 ms, max 1125.4 ms)
- Init: load 135 ms + warmup 297 ms
- RSS: warmup 46 MB, final 54 MB
- Subprocess wall: **396.3 s**

## Confidence distribution

min=0.000  p25=0.760  median=0.900  p75=0.950  max=0.960  mean=0.823

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 100.0% | 238+8 | 246 |
| `level` | 38.9% | 56+0 | 144 |
| `rank_level` | 100.0% | 102+0 | 102 |
| `percent` | 93.1% | 95+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p10.r09 | `name` | RECOVERED | substitute | `'Shortblades'` | `'Shortblades"'` | 0.000 |
| skill p03.r05 | `level` | UNRECOVERABLE | substitute | `1147` | `4147` | 0.100 |
| profession p05.r03 | `percent` | UNRECOVERABLE | drop | `9.1` | `'|'` | 0.140 |
| skill p11.r00 | `level` | UNRECOVERABLE | hallucinate | `7` | `'ora'` | 0.160 |
| skill p12.r05 | `level` | UNRECOVERABLE | substitute | `25` | `5` | 0.230 |
| skill p07.r00 | `level` | UNRECOVERABLE | substitute | `1` | `4` | 0.290 |
| skill p05.r00 | `level` | UNRECOVERABLE | substitute | `1` | `4` | 0.340 |
| skill p01.r03 | `name` | RECOVERED | substitute | `'Analysis'` | `'Analysis”'` | 0.360 |
| skill p02.r00 | `level` | UNRECOVERABLE | substitute | `1` | `4` | 0.360 |
| skill p10.r00 | `level` | UNRECOVERABLE | substitute | `1` | `4` | 0.370 |
| skill p12.r04 | `level` | UNRECOVERABLE | substitute | `88` | `'BB.'` | 0.380 |
| skill p12.r00 | `level` | UNRECOVERABLE | substitute | `1` | `4` | 0.390 |
| skill p01.r02 | `level` | UNRECOVERABLE | substitute | `2937` | `9937` | 0.410 |
| skill p02.r11 | `name` | RECOVERED | substitute | `'Clubs'` | `'Clubs”'` | 0.420 |
| skill p03.r05 | `name` | RECOVERED | substitute | `'Coolness'` | `'Coolness:'` | 0.420 |
| skill p06.r00 | `level` | UNRECOVERABLE | substitute | `3329` | `3399` | 0.420 |
| skill p01.r03 | `level` | UNRECOVERABLE | hallucinate | `1` | `41` | 0.440 |
| skill p01.r05 | `level` | UNRECOVERABLE | substitute | `1` | `4` | 0.460 |
| skill p07.r02 | `level` | UNRECOVERABLE | hallucinate | `1` | `4` | 0.470 |
| skill p08.r02 | `level` | UNRECOVERABLE | hallucinate | `1` | `4` | 0.470 |

# `easyocr` deep dive

## Headline

- Effective accuracy: **71.0%** (421 PASS + 1 RECOVERED of 594 data cells)
- Failure modes: hallucinate=0, drop=1, substitute=69, reject=103
- Per-cell mean: **47.3 ms** (p95 84.3 ms, max 272.2 ms)
- Init: load 12907 ms + warmup 84 ms
- RSS: warmup 629 MB, final 674 MB
- Subprocess wall: **42.3 s**

## Confidence distribution

min=0.000  p25=0.680  median=0.924  p75=0.998  max=1.000  mean=0.737

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 99.6% | 244+1 | 246 |
| `level` | 29.9% | 43+0 | 144 |
| `rank_level` | 39.2% | 40+0 | 102 |
| `percent` | 92.2% | 94+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p01.r00 | `level` | UNRECOVERABLE | reject | `68` | `''` | 0.000 |
| skill p01.r03 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |
| skill p01.r05 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |
| skill p01.r06 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |
| skill p01.r07 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |
| skill p01.r09 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |
| skill p01.r11 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |
| skill p02.r00 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |
| skill p02.r01 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |
| skill p02.r02 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |
| skill p02.r04 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |
| skill p02.r05 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |
| skill p02.r08 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |
| skill p02.r09 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |
| skill p02.r10 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |
| skill p02.r11 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |
| skill p03.r00 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |
| skill p03.r01 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |
| skill p03.r03 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |
| skill p03.r07 | `level` | UNRECOVERABLE | reject | `1` | `''` | 0.000 |

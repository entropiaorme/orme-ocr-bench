# `mmocr_robustscanner` deep dive

## Headline

- Effective accuracy: **86.0%** (379 PASS + 132 RECOVERED of 594 data cells)
- Failure modes: hallucinate=32, drop=0, substitute=183, reject=0
- Per-cell mean: **113.9 ms** (p95 123.6 ms, max 126.4 ms)
- Init: load 8715 ms + warmup 168 ms
- RSS: warmup 776 MB, final 782 MB
- Subprocess wall: **80.2 s**

## Confidence distribution

min=0.228  p25=0.801  median=0.963  p75=1.000  max=1.000  mean=0.871

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 80.1% | 65+132 | 246 |
| `level` | 81.2% | 117+0 | 144 |
| `rank_level` | 94.1% | 96+0 | 102 |
| `percent` | 99.0% | 101+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p11.r00 | `level` | UNRECOVERABLE | substitute | `7` | `'>'` | 0.228 |
| skill p05.r00 | `level` | UNRECOVERABLE | substitute | `1` | `'-'` | 0.258 |
| skill p03.r00 | `level` | UNRECOVERABLE | hallucinate | `1` | `10` | 0.345 |
| skill p01.r01 | `name` | UNRECOVERABLE | hallucinate | `'Aim'` | `'Allencers'` | 0.348 |
| skill p07.r00 | `level` | UNRECOVERABLE | hallucinate | `1` | `10` | 0.392 |
| skill p09.r03 | `level` | UNRECOVERABLE | hallucinate | `1` | `10` | 0.426 |
| skill p08.r04 | `level` | UNRECOVERABLE | hallucinate | `1` | `11` | 0.445 |
| skill p03.r03 | `level` | UNRECOVERABLE | hallucinate | `1` | `1990` | 0.449 |
| skill p11.r02 | `level` | UNRECOVERABLE | hallucinate | `1` | `18` | 0.450 |
| skill p07.r03 | `level` | UNRECOVERABLE | hallucinate | `1` | `1993` | 0.455 |
| skill p12.r03 | `level` | UNRECOVERABLE | hallucinate | `1` | `1993` | 0.460 |
| skill p07.r02 | `level` | UNRECOVERABLE | hallucinate | `1` | `18` | 0.464 |
| skill p08.r02 | `level` | UNRECOVERABLE | hallucinate | `1` | `18` | 0.466 |
| skill p10.r03 | `level` | UNRECOVERABLE | hallucinate | `1` | `1990` | 0.472 |
| skill p01.r09 | `level` | UNRECOVERABLE | hallucinate | `1` | `13` | 0.473 |
| skill p02.r09 | `level` | UNRECOVERABLE | hallucinate | `1` | `13` | 0.478 |
| skill p09.r02 | `level` | UNRECOVERABLE | hallucinate | `1` | `18` | 0.494 |
| skill p06.r03 | `name` | RECOVERED | substitute | `'Inflict Ranged Damage'` | `'halic...Rec.Rec.longedDamage.c'` | 0.502 |
| skill p08.r01 | `level` | UNRECOVERABLE | hallucinate | `1` | `17` | 0.509 |
| skill p10.r02 | `level` | UNRECOVERABLE | hallucinate | `1` | `18` | 0.522 |

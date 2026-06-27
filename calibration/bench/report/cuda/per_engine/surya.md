# `surya` deep dive

## Headline

- Effective accuracy: **100.0%** (594 PASS + 0 RECOVERED of 594 data cells)
- Failure modes: hallucinate=0, drop=0, substitute=0, reject=0
- Per-cell mean: **338.2 ms** (p95 677.2 ms, max 1128.0 ms)
- Init: load 13260 ms + warmup 3126 ms
- RSS: warmup 1653 MB, final 1754 MB
- Subprocess wall: **224.8 s**

## Confidence distribution

min=0.900  p25=0.986  median=0.996  p75=0.999  max=1.000  mean=0.991

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 100.0% | 246+0 | 246 |
| `level` | 100.0% | 144+0 | 144 |
| `rank_level` | 100.0% | 102+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

*No failures (or no confidence data) to sample.*

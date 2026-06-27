# `tesseract` deep dive

## Headline

- Effective accuracy: **42.4%** (250 PASS + 2 RECOVERED of 594 data cells)
- Failure modes: hallucinate=77, drop=57, substitute=210, reject=0
- Per-cell mean: **83.7 ms** (p95 94.5 ms, max 108.9 ms)
- Init: load 84 ms + warmup 122 ms
- RSS: warmup 54 MB, final 61 MB
- Subprocess wall: **52.8 s**

## Confidence distribution

min=0.000  p25=0.115  median=0.294  p75=0.884  max=0.960  mean=0.463

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 49.2% | 119+2 | 246 |
| `level` | 25.0% | 36+0 | 144 |
| `rank_level` | 61.8% | 63+0 | 102 |
| `percent` | 31.4% | 32+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p01.r09 | `level` | UNRECOVERABLE | hallucinate | `1` | `'.o'` | 0.000 |
| skill p01.r11 | `level` | UNRECOVERABLE | hallucinate | `1` | `'. i'` | 0.000 |
| skill p02.r03 | `level` | UNRECOVERABLE | hallucinate | `999` | `'a etetee'` | 0.000 |
| skill p02.r11 | `level` | UNRECOVERABLE | hallucinate | `1` | `'. i'` | 0.000 |
| skill p03.r07 | `level` | UNRECOVERABLE | hallucinate | `1` | `'.o'` | 0.000 |
| skill p03.r10 | `name` | UNRECOVERABLE | drop | `'Diagnosis'` | `'PEs'` | 0.000 |
| skill p03.r11 | `level` | UNRECOVERABLE | hallucinate | `1` | `'. i'` | 0.000 |
| skill p04.r01 | `name` | UNRECOVERABLE | substitute | `'Drilling'` | `'Soya tes'` | 0.000 |
| skill p04.r05 | `level` | UNRECOVERABLE | substitute | `2665` | `'wlacce'` | 0.000 |
| skill p04.r06 | `level` | UNRECOVERABLE | hallucinate | `1` | `'.o'` | 0.000 |
| skill p04.r11 | `level` | UNRECOVERABLE | hallucinate | `1` | `'. i'` | 0.000 |
| skill p05.r09 | `level` | UNRECOVERABLE | hallucinate | `1` | `'.o'` | 0.000 |
| skill p06.r01 | `name` | UNRECOVERABLE | drop | `'Heavy Weapons'` | `'DAs'` | 0.000 |
| skill p06.r01 | `level` | UNRECOVERABLE | substitute | `1` | `7` | 0.000 |
| skill p06.r11 | `level` | UNRECOVERABLE | hallucinate | `1` | `'. i'` | 0.000 |
| skill p07.r04 | `level` | UNRECOVERABLE | substitute | `181` | `'SToe'` | 0.000 |
| skill p07.r07 | `level` | UNRECOVERABLE | hallucinate | `1` | `'.o'` | 0.000 |
| skill p07.r10 | `name` | UNRECOVERABLE | drop | `'Mechanics'` | `'Oreo'` | 0.000 |
| skill p08.r03 | `level` | UNRECOVERABLE | substitute | `5645` | `'ra.'` | 0.000 |
| skill p08.r04 | `name` | UNRECOVERABLE | substitute | `'Mining'` | `'Ors'` | 0.000 |

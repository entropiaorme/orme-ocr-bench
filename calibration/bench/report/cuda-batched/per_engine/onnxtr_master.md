# `onnxtr_master` deep dive

## Headline

- Effective accuracy: **96.8%** (391 PASS + 184 RECOVERED of 594 data cells)
- Failure modes: hallucinate=33, drop=0, substitute=170, reject=0
- Per-cell mean: **0.0 ms** (p95 0.0 ms, max 0.0 ms)
- Init: load 17374 ms + warmup 418 ms
- RSS: warmup 1124 MB, final 1237 MB
- Subprocess wall: **33.9 s**

## Confidence distribution

min=0.332  p25=0.689  median=0.917  p75=0.998  max=1.000  mean=0.827

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 98.4% | 58+184 | 246 |
| `level` | 100.0% | 144+0 | 144 |
| `rank_level` | 85.3% | 87+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p10.r01 | `name` | RECOVERED | hallucinate | `'Rifle'` | `'Rifle----'` | 0.332 |
| skill p02.r02 | `name` | RECOVERED | hallucinate | `'Biology'` | `'Biology----'` | 0.336 |
| skill p08.r01 | `name` | RECOVERED | hallucinate | `'Mentor'` | `'Mentor----'` | 0.337 |
| skill p04.r01 | `name` | RECOVERED | substitute | `'Drilling'` | `'Drilling----'` | 0.337 |
| skill p03.r01 | `name` | RECOVERED | substitute | `'Coloring'` | `'Coloring3---'` | 0.344 |
| profession p06.r00 | `name` | RECOVERED | substitute | `'Tailor'` | `'Tailor--'` | 0.352 |
| skill p01.r01 | `name` | RECOVERED | hallucinate | `'Aim'` | `'Aim----'` | 0.354 |
| skill p05.r06 | `name` | RECOVERED | substitute | `'Genetics'` | `'Geneticss---'` | 0.355 |
| skill p04.r05 | `name` | RECOVERED | hallucinate | `'Evade'` | `'Evade----'` | 0.364 |
| skill p01.r05 | `name` | RECOVERED | hallucinate | `'Angling'` | `'Angling----'` | 0.367 |
| skill p02.r05 | `name` | RECOVERED | hallucinate | `'Botany'` | `'Botany----'` | 0.369 |
| skill p01.r00 | `name` | RECOVERED | hallucinate | `'Agility'` | `'Agility----'` | 0.369 |
| skill p08.r04 | `name` | RECOVERED | hallucinate | `'Mining'` | `'Mining----'` | 0.370 |
| skill p01.r10 | `name` | RECOVERED | substitute | `'Athletics'` | `'Athleticss---'` | 0.372 |
| skill p07.r06 | `name` | RECOVERED | substitute | `'Manufacture Vehicle'` | `'ManufactureVehicle--'` | 0.376 |
| skill p04.r00 | `name` | RECOVERED | hallucinate | `'Dodge'` | `'Dodge----'` | 0.378 |
| skill p12.r08 | `name` | RECOVERED | hallucinate | `'Whip'` | `'Whip----'` | 0.380 |
| skill p05.r08 | `name` | RECOVERED | hallucinate | `'Gutting'` | `'Gutting----'` | 0.383 |
| skill p01.r02 | `name` | RECOVERED | substitute | `'Alertness'` | `'Alertnesss---'` | 0.383 |
| skill p02.r11 | `name` | RECOVERED | hallucinate | `'Clubs'` | `'Clubs----'` | 0.386 |

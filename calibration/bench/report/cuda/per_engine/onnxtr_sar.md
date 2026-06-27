# `onnxtr_sar` deep dive

## Headline

- Effective accuracy: **96.1%** (381 PASS + 190 RECOVERED of 594 data cells)
- Failure modes: hallucinate=34, drop=0, substitute=179, reject=0
- Per-cell mean: **124.7 ms** (p95 148.2 ms, max 160.9 ms)
- Init: load 3734 ms + warmup 416 ms
- RSS: warmup 1085 MB, final 1170 MB
- Subprocess wall: **81.8 s**

## Confidence distribution

min=0.173  p25=0.483  median=0.552  p75=0.662  max=0.999  mean=0.578

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 98.4% | 52+190 | 246 |
| `level` | 100.0% | 144+0 | 144 |
| `rank_level` | 81.4% | 83+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| profession p06.r00 | `name` | RECOVERED | substitute | `'Tailor'` | `'TailotalI'` | 0.255 |
| profession p11.r00 | `name` | RECOVERED | substitute | `'Fish Looter'` | `'FishLooterA'` | 0.327 |
| profession p10.r05 | `name` | RECOVERED | substitute | `'Prospector'` | `'Prospector-'` | 0.352 |
| profession p03.r00 | `name` | RECOVERED | substitute | `'Dodger'` | `'DodgerTA'` | 0.364 |
| profession p03.r05 | `rank_level` | UNRECOVERABLE | substitute | `19` | `1919` | 0.373 |
| profession p13.r01 | `name` | RECOVERED | substitute | `'Humanoid Investigator'` | `'Humanoidlnvestigator'` | 0.379 |
| profession p13.r00 | `name` | RECOVERED | substitute | `'Gunner (Dmg)'` | `'Gunner(Dmg)-'` | 0.382 |
| profession p03.r06 | `name` | RECOVERED | substitute | `'Paramedic'` | `'Paramedic-'` | 0.387 |
| profession p08.r01 | `name` | RECOVERED | substitute | `'Powerfist Engineer'` | `'Powerfistengingineer'` | 0.399 |
| profession p06.r01 | `rank_level` | UNRECOVERABLE | substitute | `6` | `'Apprentice,'` | 0.400 |
| skill p04.r07 | `name` | RECOVERED | substitute | `'Face Sculpting'` | `'FacesculptingI--'` | 0.411 |
| profession p04.r02 | `rank_level` | UNRECOVERABLE | substitute | `14` | `1414` | 0.415 |
| profession p10.r03 | `name` | RECOVERED | substitute | `'Resource Gatherer'` | `'ResourceGathererer'` | 0.416 |
| skill p04.r05 | `name` | RECOVERED | hallucinate | `'Evade'` | `'Evade-I--'` | 0.419 |
| profession p11.r02 | `name` | RECOVERED | substitute | `'Driller'` | `'Driller-I'` | 0.421 |
| profession p03.r02 | `name` | RECOVERED | substitute | `'Cryogenic (Hit)'` | `'Cryogenic(Hit)0'` | 0.424 |
| skill p03.r05 | `name` | RECOVERED | substitute | `'Coolness'` | `'CoolnessSI-I'` | 0.428 |
| profession p10.r00 | `name` | RECOVERED | substitute | `'Animal Looter'` | `'AnimalLooter-'` | 0.430 |
| skill p08.r01 | `name` | RECOVERED | hallucinate | `'Mentor'` | `'Mentor-I--'` | 0.432 |
| skill p10.r03 | `name` | RECOVERED | substitute | `'Scan Human'` | `'ScanHuman---'` | 0.432 |

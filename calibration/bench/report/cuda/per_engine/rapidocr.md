# `rapidocr` deep dive

## Headline

- Effective accuracy: **100.0%** (581 PASS + 13 RECOVERED of 594 data cells)
- Failure modes: hallucinate=0, drop=0, substitute=13, reject=0
- Per-cell mean: **34.7 ms** (p95 36.1 ms, max 37.4 ms)
- Init: load 712 ms + warmup 325 ms
- RSS: warmup 902 MB, final 919 MB
- Subprocess wall: **23.0 s**

## Confidence distribution

min=0.231  p25=0.910  median=0.951  p75=0.995  max=1.000  mean=0.935

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 100.0% | 233+13 | 246 |
| `level` | 100.0% | 144+0 | 144 |
| `rank_level` | 100.0% | 102+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p12.r04 | `name` | RECOVERED | substitute | `'Vehicle Repairing'` | `'VehicleReairing'` | 0.778 |
| skill p02.r04 | `name` | RECOVERED | substitute | `'Body Sculpting'` | `'BodyScupting'` | 0.781 |
| profession p14.r02 | `name` | RECOVERED | substitute | `'Animal Investigator'` | `'Animallnvestigator'` | 0.873 |
| skill p08.r01 | `name` | RECOVERED | substitute | `'Mentor'` | `'Mentor.'` | 0.879 |
| profession p03.r02 | `name` | RECOVERED | substitute | `'Cryogenic (Hit)'` | `'Cryogenic （Hit）'` | 0.884 |
| profession p02.r02 | `name` | RECOVERED | substitute | `'Brawler (Dmg)'` | `'Brawler(Dmg）'` | 0.901 |
| skill p02.r02 | `name` | RECOVERED | substitute | `'Biology'` | `'Biology-'` | 0.902 |
| profession p02.r03 | `name` | RECOVERED | substitute | `'Whipper (Dmg)'` | `'Whipper(Dmg）'` | 0.920 |
| profession p01.r05 | `name` | RECOVERED | substitute | `'Pyro Kinetic (Dmg)'` | `'PyroKinetic（Dmg）'` | 0.927 |
| profession p03.r01 | `name` | RECOVERED | substitute | `'Pyro Kinetic (Hit)'` | `'PyroKinetic（Hit)'` | 0.930 |
| profession p01.r06 | `name` | RECOVERED | substitute | `'Cryogenic (Dmg)'` | `'Cryogenic（Dmg）'` | 0.937 |
| profession p03.r04 | `name` | RECOVERED | substitute | `'Knifefighter (Hit)'` | `'Knifefighter（Hit)'` | 0.946 |
| profession p01.r04 | `name` | RECOVERED | substitute | `'Knifefighter (Dmg)'` | `'Knifefighter（Dmg)'` | 0.946 |

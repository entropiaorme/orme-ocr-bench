# `rapidocr` deep dive

## Headline

- Effective accuracy: **100.0%** (581 PASS + 13 RECOVERED of 594 data cells)
- Failure modes: hallucinate=0, drop=0, substitute=13, reject=0
- Per-cell mean: **0.0 ms** (p95 0.0 ms, max 0.0 ms)
- Init: load 990 ms + warmup 407 ms
- RSS: warmup 899 MB, final 992 MB
- Subprocess wall: **5.8 s**

## Confidence distribution

min=0.245  p25=0.915  median=0.954  p75=0.996  max=1.000  mean=0.939

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
| skill p12.r04 | `name` | RECOVERED | substitute | `'Vehicle Repairing'` | `'VehicleReairing'` | 0.779 |
| skill p02.r04 | `name` | RECOVERED | substitute | `'Body Sculpting'` | `'BodyScupting'` | 0.782 |
| profession p14.r02 | `name` | RECOVERED | substitute | `'Animal Investigator'` | `'Animallnvestigator'` | 0.873 |
| skill p08.r01 | `name` | RECOVERED | substitute | `'Mentor'` | `'Mentor.'` | 0.881 |
| profession p03.r02 | `name` | RECOVERED | substitute | `'Cryogenic (Hit)'` | `'Cryogenic （Hit）'` | 0.884 |
| skill p02.r02 | `name` | RECOVERED | substitute | `'Biology'` | `'Biology-'` | 0.901 |
| profession p02.r02 | `name` | RECOVERED | substitute | `'Brawler (Dmg)'` | `'Brawler(Dmg）'` | 0.901 |
| profession p02.r03 | `name` | RECOVERED | substitute | `'Whipper (Dmg)'` | `'Whipper(Dmg）'` | 0.920 |
| profession p01.r05 | `name` | RECOVERED | substitute | `'Pyro Kinetic (Dmg)'` | `'PyroKinetic（Dmg）'` | 0.927 |
| profession p03.r01 | `name` | RECOVERED | substitute | `'Pyro Kinetic (Hit)'` | `'PyroKinetic（Hit)'` | 0.930 |
| profession p01.r06 | `name` | RECOVERED | substitute | `'Cryogenic (Dmg)'` | `'Cryogenic（Dmg）'` | 0.937 |
| profession p03.r04 | `name` | RECOVERED | substitute | `'Knifefighter (Hit)'` | `'Knifefighter（Hit)'` | 0.946 |
| profession p01.r04 | `name` | RECOVERED | substitute | `'Knifefighter (Dmg)'` | `'Knifefighter（Dmg)'` | 0.946 |

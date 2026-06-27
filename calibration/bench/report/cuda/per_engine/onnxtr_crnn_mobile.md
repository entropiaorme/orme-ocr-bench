# `onnxtr_crnn_mobile` deep dive

## Headline

- Effective accuracy: **94.6%** (366 PASS + 196 RECOVERED of 594 data cells)
- Failure modes: hallucinate=29, drop=0, substitute=199, reject=0
- Per-cell mean: **58.8 ms** (p95 72.3 ms, max 76.4 ms)
- Init: load 2802 ms + warmup 300 ms
- RSS: warmup 947 MB, final 992 MB
- Subprocess wall: **39.8 s**

## Confidence distribution

min=0.344  p25=0.677  median=0.857  p75=0.990  max=1.000  mean=0.821

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 98.4% | 46+196 | 246 |
| `level` | 100.0% | 144+0 | 144 |
| `rank_level` | 72.5% | 74+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| profession p05.r06 | `name` | RECOVERED | substitute | `'Mining Laser (Hit)'` | `'MiningLaser(HiHO'` | 0.344 |
| profession p04.r07 | `name` | RECOVERED | substitute | `'Laser Pistoleer (Hit)'` | `'LaserPistoleer(HitHiO)'` | 0.410 |
| profession p04.r06 | `name` | RECOVERED | substitute | `'Gauss Sniper (Hit)'` | `"Gauss'Sniper(Hi0"` | 0.410 |
| profession p01.r03 | `name` | RECOVERED | substitute | `'Swordsman (Hit)'` | `'Swordsman(HiO)40'` | 0.412 |
| profession p04.r04 | `name` | RECOVERED | substitute | `'BLP Sniper (Hit)'` | `'BLPSniper(HHr(HIO0'` | 0.429 |
| profession p05.r00 | `name` | RECOVERED | substitute | `'Mounted Laser (Hit)'` | `'MountedLaser(Hiti)'` | 0.481 |
| profession p04.r03 | `name` | RECOVERED | substitute | `'Laser Sniper (Hit)'` | `'LaserSniper(Hitg)'` | 0.487 |
| profession p03.r06 | `name` | RECOVERED | substitute | `'Paramedic'` | `'Paramedic-'` | 0.493 |
| skill p12.r00 | `name` | RECOVERED | substitute | `'Tier Upgrading'` | `'TierUpgrading---'` | 0.496 |
| profession p05.r03 | `name` | RECOVERED | substitute | `'Mounted BLP (Hit)'` | `'MountedBLP(HIHi'` | 0.506 |
| profession p01.r01 | `name` | RECOVERED | substitute | `'Electro Kinetic (Hit)'` | `'ElectroKinetic(HitIO'` | 0.510 |
| profession p04.r02 | `name` | RECOVERED | substitute | `'Whipper (Hit)'` | `'Whipper(HitHO)-'` | 0.511 |
| skill p06.r05 | `name` | RECOVERED | hallucinate | `'Jamming'` | `'Jamminga---'` | 0.511 |
| skill p09.r01 | `name` | RECOVERED | substitute | `'Power Fist'` | `'PowerFist---'` | 0.521 |
| profession p04.r05 | `name` | RECOVERED | substitute | `'Plasma Sniper (Hit)'` | `'PlasmaSniper(Hi)'` | 0.527 |
| profession p04.r00 | `name` | RECOVERED | substitute | `'Brawler (Hit)'` | `'Brawler(HitHR)-'` | 0.538 |
| skill p09.r11 | `name` | RECOVERED | substitute | `'Reputation'` | `'Reputation---'` | 0.538 |
| profession p06.r00 | `name` | RECOVERED | substitute | `'Tailor'` | `'Tailor--'` | 0.545 |
| skill p10.r11 | `name` | RECOVERED | substitute | `'Spacecraft Engineering'` | `'SpacecraftEngineering--'` | 0.547 |
| profession p01.r06 | `name` | RECOVERED | substitute | `'Cryogenic (Dmg)'` | `'Cryogenic(Dmgo)'` | 0.549 |

# `onnxtr_viptr` deep dive

## Headline

- Effective accuracy: **95.8%** (469 PASS + 100 RECOVERED of 594 data cells)
- Failure modes: hallucinate=0, drop=0, substitute=125, reject=0
- Per-cell mean: **0.0 ms** (p95 0.0 ms, max 0.0 ms)
- Init: load 14914 ms + warmup 487 ms
- RSS: warmup 1011 MB, final 1145 MB
- Subprocess wall: **3.1 s**

## Confidence distribution

min=0.334  p25=0.729  median=0.854  p75=0.998  max=1.000  mean=0.843

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 98.8% | 143+100 | 246 |
| `level` | 98.6% | 142+0 | 144 |
| `rank_level` | 80.4% | 82+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p06.r00 | `level` | UNRECOVERABLE | substitute | `3329` | `3829` | 0.525 |
| profession p13.r06 | `name` | RECOVERED | substitute | `'Gunner (Hit)'` | `'Gunner(Hito)'` | 0.538 |
| skill p08.r00 | `name` | RECOVERED | substitute | `'Melee Damage Assessment'` | `'MeleeDamageAssessessmentI'` | 0.555 |
| skill p07.r00 | `name` | RECOVERED | substitute | `'Manufacture Attachments'` | `'ManuacureAtachments3'` | 0.558 |
| profession p13.r00 | `name` | RECOVERED | substitute | `'Gunner (Dmg)'` | `'Gunner(Dmg)-'` | 0.563 |
| skill p02.r00 | `name` | UNRECOVERABLE | substitute | `'BLP Weaponry Technology'` | `'ELPWGspOTYyTechnologygy-'` | 0.565 |
| profession p04.r03 | `name` | RECOVERED | substitute | `'Laser Sniper (Hit)'` | `'LaserSniper(Hit'` | 0.601 |
| skill p09.r00 | `name` | RECOVERED | substitute | `'Power Catalyst'` | `'Povercalalyst'` | 0.604 |
| profession p09.r00 | `rank_level` | UNRECOVERABLE | substitute | `1` | `11` | 0.612 |
| skill p11.r02 | `name` | RECOVERED | substitute | `'Spacecraft Weaponry'` | `'SpacecraftWeaponry-'` | 0.612 |
| skill p04.r00 | `level` | UNRECOVERABLE | substitute | `2534` | `2584` | 0.617 |
| profession p05.r03 | `name` | RECOVERED | substitute | `'Mounted BLP (Hit)'` | `'MountedBLP(HItit)'` | 0.618 |
| profession p03.r01 | `name` | RECOVERED | substitute | `'Pyro Kinetic (Hit)'` | `'PyroKinetic(Hit'` | 0.622 |
| profession p11.r02 | `rank_level` | UNRECOVERABLE | substitute | `2` | `222` | 0.628 |
| profession p01.r02 | `name` | RECOVERED | substitute | `'Swordsman (Dmg)'` | `'Swordsman(Dmg'` | 0.629 |
| profession p02.r02 | `name` | RECOVERED | substitute | `'Brawler (Dmg)'` | `'Brawler(Dmg))'` | 0.634 |
| skill p11.r00 | `name` | RECOVERED | substitute | `'Spacecraft Pilot'` | `'SpacccrattPlloaPllot'` | 0.638 |
| skill p03.r02 | `name` | RECOVERED | substitute | `'Combat Reflexes'` | `'CombatReflexesS--'` | 0.643 |
| profession p03.r00 | `name` | RECOVERED | substitute | `'Dodger'` | `'Dodger-'` | 0.649 |
| profession p03.r04 | `name` | RECOVERED | substitute | `'Knifefighter (Hit)'` | `'Knifefighter(Hiter(Hit'` | 0.653 |

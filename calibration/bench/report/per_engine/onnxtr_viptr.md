# `onnxtr_viptr` deep dive

## Headline

- Effective accuracy: **95.6%** (376 PASS + 192 RECOVERED of 594 data cells)
- Failure modes: hallucinate=0, drop=0, substitute=218, reject=0
- Per-cell mean: **689.4 ms** (p95 1504.9 ms, max 3038.0 ms)
- Init: load 54180 ms + warmup 1233 ms
- RSS: warmup 388 MB, final 276 MB
- Subprocess wall: **489.4 s**

## Confidence distribution

min=0.333  p25=0.727  median=0.858  p75=0.998  max=1.000  mean=0.843

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 98.4% | 50+192 | 246 |
| `level` | 98.6% | 142+0 | 144 |
| `rank_level` | 80.4% | 82+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| profession p01.r01 | `name` | RECOVERED | substitute | `'Electro Kinetic (Hit)'` | `'ElectroKinetic(Hit)'` | 0.472 |
| profession p05.r01 | `name` | RECOVERED | substitute | `'BLP Pistoleer (Hit)'` | `'BLPPistoleer(Hit)'` | 0.499 |
| profession p13.r01 | `name` | RECOVERED | substitute | `'Humanoid Investigator'` | `'HumanoidInvestigator'` | 0.517 |
| profession p09.r00 | `name` | RECOVERED | substitute | `'Enhancer Constructor'` | `'EnhancerConstructor'` | 0.521 |
| skill p06.r00 | `level` | UNRECOVERABLE | substitute | `3329` | `3829` | 0.524 |
| skill p10.r00 | `name` | RECOVERED | substitute | `'Resource Gathering'` | `'ResourceGathering'` | 0.530 |
| profession p13.r06 | `name` | RECOVERED | substitute | `'Gunner (Hit)'` | `'Gunner(Hito)'` | 0.537 |
| profession p04.r00 | `name` | RECOVERED | substitute | `'Brawler (Hit)'` | `'Brawler(Hit)'` | 0.553 |
| skill p07.r00 | `name` | RECOVERED | substitute | `'Manufacture Attachments'` | `'ManuacureAtachments3'` | 0.561 |
| profession p13.r00 | `name` | RECOVERED | substitute | `'Gunner (Dmg)'` | `'Gunner(Dmg)-'` | 0.562 |
| skill p08.r00 | `name` | RECOVERED | substitute | `'Melee Damage Assessment'` | `'MeleeDamageAssessessmentI'` | 0.563 |
| skill p02.r00 | `name` | UNRECOVERABLE | substitute | `'BLP Weaponry Technology'` | `'ELPWGspOTYyTechnologygy-'` | 0.570 |
| profession p05.r02 | `name` | RECOVERED | substitute | `'Plasma Pistoleer (Hit)'` | `'PlasmaPistoleer(Hit)'` | 0.587 |
| profession p04.r03 | `name` | RECOVERED | substitute | `'Laser Sniper (Hit)'` | `'LaserSniper(Hit'` | 0.601 |
| skill p04.r06 | `name` | RECOVERED | substitute | `'Explosive Projectile Weaponry Technology'` | `'ExplosiveProjectileWeaponryTechnology'` | 0.602 |
| skill p09.r00 | `name` | RECOVERED | substitute | `'Power Catalyst'` | `'Povercalalyst'` | 0.604 |
| profession p09.r00 | `rank_level` | UNRECOVERABLE | substitute | `1` | `11` | 0.606 |
| profession p14.r01 | `name` | RECOVERED | substitute | `'Technology Investigator'` | `'Technologyinvestigator'` | 0.608 |
| skill p11.r02 | `name` | RECOVERED | substitute | `'Spacecraft Weaponry'` | `'SpacecraftWeaponry-'` | 0.612 |
| profession p05.r03 | `name` | RECOVERED | substitute | `'Mounted BLP (Hit)'` | `'MountedBLP(HItit)'` | 0.618 |

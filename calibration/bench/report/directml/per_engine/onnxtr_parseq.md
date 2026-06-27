# `onnxtr_parseq` deep dive

## Headline

- Effective accuracy: **95.5%** (375 PASS + 192 RECOVERED of 594 data cells)
- Failure modes: hallucinate=33, drop=0, substitute=186, reject=0
- Per-cell mean: **150.0 ms** (p95 231.6 ms, max 264.0 ms)
- Init: load 5764 ms + warmup 296 ms
- RSS: warmup 290 MB, final 326 MB
- Subprocess wall: **100.3 s**

## Confidence distribution

min=0.757  p25=0.988  median=0.999  p75=1.000  max=1.000  mean=0.988

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 98.4% | 50+192 | 246 |
| `level` | 100.0% | 144+0 | 144 |
| `rank_level` | 77.5% | 79+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| profession p08.r05 | `rank_level` | UNRECOVERABLE | substitute | `2` | `222` | 0.757 |
| profession p08.r06 | `rank_level` | UNRECOVERABLE | substitute | `2` | `222` | 0.763 |
| profession p08.r04 | `rank_level` | UNRECOVERABLE | substitute | `2` | `222` | 0.780 |
| profession p11.r04 | `rank_level` | UNRECOVERABLE | substitute | `2` | `222` | 0.780 |
| profession p06.r07 | `name` | RECOVERED | substitute | `'Metal Engineer'` | `'MetalEngineerr'` | 0.797 |
| profession p06.r02 | `name` | RECOVERED | substitute | `'Gardener'` | `'Gardenerr-'` | 0.810 |
| profession p12.r00 | `name` | RECOVERED | substitute | `'Biotropic'` | `'Biotropicc-'` | 0.826 |
| profession p14.r05 | `name` | RECOVERED | substitute | `'Body Sculptor'` | `'BodySculptor-'` | 0.826 |
| profession p03.r02 | `name` | RECOVERED | substitute | `'Cryogenic (Hit)'` | `'Cryogenic(Hit))'` | 0.835 |
| profession p01.r01 | `rank_level` | UNRECOVERABLE | substitute | `74` | `744` | 0.874 |
| profession p12.r01 | `name` | RECOVERED | substitute | `'Telepath'` | `'Telepath--'` | 0.894 |
| profession p10.r00 | `name` | RECOVERED | substitute | `'Animal Looter'` | `'AnimalLooter-'` | 0.897 |
| skill p03.r02 | `name` | RECOVERED | substitute | `'Combat Reflexes'` | `'CombatReflexeflexess--'` | 0.911 |
| skill p04.r08 | `name` | RECOVERED | substitute | `'First Aid'` | `'FirstAid1---'` | 0.922 |
| skill p03.r01 | `name` | RECOVERED | substitute | `'Coloring'` | `'Coloringa---'` | 0.927 |
| skill p03.r06 | `name` | RECOVERED | hallucinate | `'Courage'` | `'Courage----'` | 0.929 |
| skill p01.r03 | `name` | RECOVERED | substitute | `'Analysis'` | `'Analysiss---'` | 0.933 |
| profession p13.r00 | `name` | RECOVERED | substitute | `'Gunner (Dmg)'` | `'Gunner(Dmg)-'` | 0.934 |
| profession p11.r01 | `name` | UNRECOVERABLE | substitute | `'Archaeologist'` | `'Archaeologist-'` | 0.937 |
| skill p07.r00 | `name` | RECOVERED | substitute | `'Manufacture Attachments'` | `'ManufactureAttachmentss-'` | 0.945 |

# `got_ocr2` deep dive

## Headline

- Effective accuracy: **51.5%** (164 PASS + 142 RECOVERED of 594 data cells)
- Failure modes: hallucinate=428, drop=0, substitute=2, reject=0
- Per-cell mean: **8588.4 ms** (p95 8606.3 ms, max 8659.0 ms)
- Init: load 24189 ms + warmup 9264 ms
- RSS: warmup 2530 MB, final 2607 MB
- Subprocess wall: **5394.7 s**

## Confidence distribution

min=0.667  p25=0.878  median=0.938  p75=0.965  max=0.996  mean=0.918

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 90.7% | 81+142 | 246 |
| `level` | 20.1% | 29+0 | 144 |
| `rank_level` | 2.9% | 3+0 | 102 |
| `percent` | 50.0% | 51+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p04.r11 | `name` | UNRECOVERABLE | hallucinate | `'Fishing Rod Technology'` | `'Fishing Rod Technology，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，，'` | 0.667 |
| profession p12.r00 | `rank_level` | UNRECOVERABLE | hallucinate | `30` | `3055555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555` | 0.688 |
| skill p06.r00 | `name` | RECOVERED | hallucinate | `'Heavy Melee Weapons'` | `'Heavy Melle e Weapons   1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1'` | 0.725 |
| skill p10.r02 | `name` | RECOVERED | hallucinate | `'Scan Animal'` | `'S can Animal    1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1'` | 0.737 |
| profession p04.r06 | `name` | RECOVERED | hallucinate | `'Gauss Sniper (Hit)'` | `'GaussSniper(Hit)MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM'` | 0.743 |
| skill p09.r00 | `name` | RECOVERED | hallucinate | `'Power Catalyst'` | `'Power Catalyst   11 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1'` | 0.749 |
| profession p11.r02 | `rank_level` | UNRECOVERABLE | hallucinate | `2` | `5` | 0.753 |
| profession p06.r03 | `name` | RECOVERED | hallucinate | `'Spacecraft Engineering'` | `'Spacecraft EngineeringIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI\nI'` | 0.755 |
| skill p02.r02 | `name` | RECOVERED | hallucinate | `'Biology'` | `'Biology100110111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'` | 0.757 |
| profession p01.r05 | `name` | UNRECOVERABLE | hallucinate | `'Pyro Kinetic (Dmg)'` | `'Pyro Kinetic (Dmg)(Ch3C)Cl</smiles>11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'` | 0.760 |
| skill p09.r01 | `name` | RECOVERED | hallucinate | `'Power Fist'` | `'Power   Fis   t    t    t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t  t\nPower   Fis'` | 0.763 |
| skill p10.r11 | `name` | RECOVERED | hallucinate | `'Spacecraft Engineering'` | `'Spacecraft Engineering11 Spacecraft EngineeringSpacecraft EngineeringSpacecraft EngineeringSpacecraft EngineeringSpacecraft EngineeringSpacecraft Engineering1111Spacecraft EngineeringSpacecraft Engineering1111Spacecraft EngineeringSpacecraft Engineering11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'` | 0.766 |
| skill p12.r00 | `name` | RECOVERED | hallucinate | `'Tier Upgrading'` | `'Tier Upgrading 1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'` | 0.769 |
| skill p07.r00 | `name` | RECOVERED | hallucinate | `'Manufacture Attachments'` | `'Manufacture Attachments111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'` | 0.774 |
| profession p09.r00 | `name` | UNRECOVERABLE | hallucinate | `'Enhancer Constructor'` | `'Enhancer\xa0PrognTnstructoiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni'` | 0.777 |
| profession p14.r04 | `name` | RECOVERED | hallucinate | `'Hair Stylist'` | `'Hair Stylist    111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'` | 0.787 |
| profession p04.r00 | `name` | RECOVERED | hallucinate | `'Brawler (Hit)'` | `'Brawler (Hit)iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni\ni'` | 0.790 |
| skill p06.r01 | `name` | UNRECOVERABLE | hallucinate | `'Heavy Weapons'` | `'Heavy Weapons111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'` | 0.792 |
| profession p10.r05 | `name` | RECOVERED | hallucinate | `'Prospector'` | `'Prospector1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'` | 0.793 |
| profession p03.r02 | `name` | UNRECOVERABLE | hallucinate | `'Cryogenic (Hit)'` | `'Cryogenic (Hit)(1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'` | 0.795 |

# `rapidocr` deep dive

## Headline

- Effective accuracy: **98.7%** (488 PASS + 98 RECOVERED of 594 data cells)
- Failure modes: hallucinate=0, drop=0, substitute=106, reject=0
- Per-cell mean: **9.6 ms** (p95 18.9 ms, max 47.1 ms)
- Init: load 555 ms + warmup 54 ms
- RSS: warmup 105 MB, final 112 MB
- Subprocess wall: **7.2 s**

## Confidence distribution

min=0.299  p25=0.706  median=0.799  p75=0.864  max=0.948  mean=0.755

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 99.6% | 147+98 | 246 |
| `level` | 100.0% | 144+0 | 144 |
| `rank_level` | 93.1% | 95+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| profession p09.r03 | `rank_level` | UNRECOVERABLE | substitute | `0` | `'Poor,o'` | 0.729 |
| profession p09.r02 | `rank_level` | UNRECOVERABLE | substitute | `0` | `'Mediocre,o'` | 0.739 |
| profession p05.r06 | `rank_level` | UNRECOVERABLE | substitute | `0` | `'Inept.o'` | 0.751 |
| profession p05.r07 | `rank_level` | UNRECOVERABLE | substitute | `0` | `'Inept.o'` | 0.770 |
| profession p14.r03 | `rank_level` | UNRECOVERABLE | substitute | `0` | `'Mediocre,o'` | 0.772 |
| profession p09.r04 | `rank_level` | UNRECOVERABLE | substitute | `0` | `'Poor.o'` | 0.773 |
| profession p09.r05 | `rank_level` | UNRECOVERABLE | substitute | `0` | `'Poor.o'` | 0.773 |
| profession p04.r00 | `name` | RECOVERED | substitute | `'Brawler (Hit)'` | `'Brawler (Hit)兴'` | 0.777 |
| profession p04.r02 | `name` | RECOVERED | substitute | `'Whipper (Hit)'` | `'Whipper(Hit)'` | 0.800 |
| profession p13.r00 | `name` | RECOVERED | substitute | `'Gunner (Dmg)'` | `'Gunner(Dmg）兴'` | 0.805 |
| profession p01.r02 | `name` | RECOVERED | substitute | `'Swordsman (Dmg)'` | `'Swordsman(Dmg)'` | 0.824 |
| profession p02.r03 | `name` | RECOVERED | substitute | `'Whipper (Dmg)'` | `'Whipper(Dmg）'` | 0.825 |
| skill p04.r08 | `name` | RECOVERED | substitute | `'First Aid'` | `'FirstAid'` | 0.831 |
| profession p02.r07 | `name` | RECOVERED | substitute | `'Grenadier (Dmg)'` | `'Grenadier(Dmg)'` | 0.835 |
| profession p10.r04 | `name` | RECOVERED | substitute | `'Treasure Hunter'` | `'Treasure hunter'` | 0.842 |
| skill p06.r10 | `name` | RECOVERED | substitute | `'Make Textile'` | `'MakeTextile'` | 0.843 |
| skill p12.r01 | `name` | RECOVERED | substitute | `'Tools Technology'` | `'ToolsTechnology'` | 0.844 |
| skill p07.r11 | `name` | RECOVERED | substitute | `'Melee Combat'` | `'MeleeCombat'` | 0.846 |
| profession p02.r02 | `name` | RECOVERED | substitute | `'Brawler (Dmg)'` | `'Brawler(Dmg)'` | 0.846 |
| skill p12.r00 | `name` | RECOVERED | substitute | `'Tier Upgrading'` | `'TierUpgrading'` | 0.847 |

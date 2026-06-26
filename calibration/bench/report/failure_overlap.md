# Failure-cell overlap analysis

Engines reporting cells: **1** of 1 engines.

## Distribution of cell failure across engines

How many engines fail on each cell? If the distribution skews toward 'few engines fail' (heavy 0-failures bin), failures are engine-specific and ensembling helps. If it skews toward 'many engines fail' (heavy high-N-failures tail), some cells are intrinsically hard and ensembling won't save them.

| # engines failing | # cells | share | bar |
| --- | --- | --- | --- |
| 0 | 550 | 92.6% | ████████████████████████████████████████ |
| 1 | 44 | 7.4% | ███ |

## Hardest cells (failed by ≥ 1 engines)

Top 30 by # failing engines.

| Cell | # fail | Expected | Sample OCR (top-3 engines) |
| --- | --- | --- | --- |
| skill p01.r01.name | 1 | `Aim` | `'Am'` |
| skill p01.r05.name | 1 | `Angling` | `'AＡngliｎg'` |
| skill p03.r03.name | 1 | `Computer` | `'Compute'` |
| skill p03.r05.name | 1 | `Coolness` | `'Cooinessc'` |
| skill p03.r06.name | 1 | `Courage` | `'Courge'` |
| skill p04.r02.name | 1 | `Electrokinesis` | `'Electrkinesis'` |
| skill p05.r04.name | 1 | `Gastronomy` | `'Gastrnomy'` |
| skill p07.r00.name | 1 | `Manufacture Attachments` | `'Manufacture  ttachments'` |
| skill p07.r08.name | 1 | `Marksmanship` | `'Marksmanshi'` |
| skill p08.r00.name | 1 | `Melee Damage Assessment` | `'Melee  Damage  ssessmen.'` |
| skill p10.r01.name | 1 | `Rifle` | `'Rifie'` |
| skill p10.r02.name | 1 | `Scan Animal` | `'ScanAnima'` |
| skill p10.r03.name | 1 | `Scan Human` | `'Scanuman'` |
| skill p11.r03.name | 1 | `Stamina` | `'stamia'` |
| skill p11.r04.name | 1 | `Strength` | `'sstrength'` |
| skill p12.r02.name | 1 | `Translocation` | `'Transocation'` |
| skill p12.r03.name | 1 | `Treasure Sense` | `'Treasureense'` |
| profession p01.r00.name | 1 | `Electro Kinetic (Dmg)` | `'Electro Kinetic(Dmg）'` |
| profession p01.r02.name | 1 | `Swordsman (Dmg)` | `'Swordsman(Dmg）'` |
| profession p01.r04.name | 1 | `Knifefighter (Dmg)` | `'Knifefighter (Dmg.）'` |
| profession p01.r05.name | 1 | `Pyro Kinetic (Dmg)` | `'Pyro  Kinetic (Dmg.)）'` |
| profession p01.r06.name | 1 | `Cryogenic (Dmg)` | `'Cryogenic (Dmg.）'` |
| profession p02.r03.name | 1 | `Whipper (Dmg)` | `'Whipper(Dmg）'` |
| profession p02.r05.name | 1 | `Ranged Plasma (Dmg)` | `'Ranged Plasma(Dmg）'` |
| profession p02.r06.name | 1 | `Ranged Gauss (Dmg)` | `'Ranged Gauss(Dmg）'` |
| profession p03.r02.name | 1 | `Cryogenic (Hit)` | `'Cryogenic (Hit)）'` |
| profession p04.r05.name | 1 | `Plasma Sniper (Hit)` | `'Plasma Sniper (Hit.)'` |
| profession p06.r04.name | 1 | `Longblades Engineer` | `'Longblades Enginee'` |
| profession p06.r06.name | 1 | `Electronics Engineer` | `'Electronics Enginee'` |
| profession p06.r07.name | 1 | `Metal Engineer` | `'Metal Enginee'` |

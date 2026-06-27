# Failure-cell overlap analysis

Engines reporting cells: **26** of 26 engines.

## Distribution of cell failure across engines

How many engines fail on each cell? If the distribution skews toward 'few engines fail' (heavy 0-failures bin), failures are engine-specific and ensembling helps. If it skews toward 'many engines fail' (heavy high-N-failures tail), some cells are intrinsically hard and ensembling won't save them.

| # engines failing | # cells | share | bar |
| --- | --- | --- | --- |
| 3 | 6 | 1.0% | ███ |
| 4 | 22 | 3.7% | ██████████ |
| 5 | 39 | 6.6% | █████████████████ |
| 6 | 54 | 9.1% | ████████████████████████ |
| 7 | 90 | 15.2% | ████████████████████████████████████████ |
| 8 | 52 | 8.8% | ███████████████████████ |
| 9 | 24 | 4.0% | ███████████ |
| 10 | 25 | 4.2% | ███████████ |
| 11 | 17 | 2.9% | ████████ |
| 12 | 28 | 4.7% | ████████████ |
| 13 | 27 | 4.5% | ████████████ |
| 14 | 31 | 5.2% | ██████████████ |
| 15 | 22 | 3.7% | ██████████ |
| 16 | 38 | 6.4% | █████████████████ |
| 17 | 51 | 8.6% | ███████████████████████ |
| 18 | 30 | 5.1% | █████████████ |
| 19 | 19 | 3.2% | ████████ |
| 20 | 13 | 2.2% | ██████ |
| 21 | 3 | 0.5% | █ |
| 22 | 3 | 0.5% | █ |

## Hardest cells (failed by ≥ 13 engines)

Top 30 by # failing engines.

| Cell | # fail | Expected | Sample OCR (top-3 engines) |
| --- | --- | --- | --- |
| profession p02.r03.name | 22 | `Whipper (Dmg)` | `''`, `'Winper Omg'`, `'Whipper (Omg)'` |
| profession p03.r04.name | 22 | `Knifefighter (Hit)` | `''`, `'Knitebrührer (Foll)'`, `'Künterführer (Hilf)'` |
| profession p12.r04.name | 22 | `Sweat Gatherer` | `''`, `'Sweat Galherer'`, `'Sweat Gatherrer'` |
| skill p01.r06.name | 21 | `Animal Lore` | `''`, `'MIMO'`, `'Animal Love'` |
| skill p08.r08.name | 21 | `Particle Beamer Technology` | `''`, `'PAVIC BEANET TECHNOLOGY'`, `'Paricle Beamer Technology'` |
| skill p11.r02.name | 21 | `Spacecraft Weaponry` | `''`, `'SPECIAL NEWW'`, `'Spacewan Weaponry'` |
| skill p02.r01.name | 20 | `Baitfishing` | `''`, `'PALMOND'`, `'Bakshiny'` |
| skill p02.r06.name | 20 | `Bravado` | `''`, `'M'`, `'branniettii'` |
| skill p03.r06.name | 20 | `Courage` | `''`, `'WOM'`, `'commeetit'` |
| skill p04.r02.name | 20 | `Electrokinesis` | `''`, `'EMINIS'`, `'Electronnests'` |
| skill p06.r02.name | 20 | `Inflict Melee Damage` | `''`, `'Michele Wallange'`, `'Innict Meeee Damage'` |
| skill p06.r03.name | 20 | `Inflict Ranged Damage` | `''`, `'Miche Royal Dansing'`, `'Innict Range Damage'` |
| skill p06.r07.name | 20 | `Light Melee Weapons` | `''`, `'MAY MADE HEAVORS'`, `'LIGHT Micee Weapons'` |
| skill p08.r02.name | 20 | `Metallurgy` | `''`, `'MOMMY'`, `'Mezalury'` |
| skill p10.r02.name | 20 | `Scan Animal` | `''`, `'SALMIA'`, `'S can Animal    1 1 1 1 1 1 1 1 1 1 1 1` |
| skill p10.r05.name | 20 | `Scan Robot` | `''`, `'SALIOM'`, `'Scan Roody'` |
| skill p11.r06.name | 20 | `Surveying` | `''`, `'SIMON'`, `'Surveyor'` |
| skill p11.r11.name | 20 | `Texture Pattern Matching` | `''`, `'TOMMY PACHIN LENCHING'`, `'Texture Pattern Maching'` |
| profession p03.r02.name | 20 | `Cryogenic (Hit)` | `''`, `'Cryogenic (H)'`, `'Cryogenic (Hif)'` |
| skill p01.r05.name | 19 | `Angling` | `''`, `'٠٠'`, `'ANOM'` |
| skill p01.r08.name | 19 | `Armor Technology` | `''`, `'ALM'`, `'Anor Technology'` |
| skill p02.r02.name | 19 | `Biology` | `''`, `'M'`, `'Biolog'` |
| skill p03.r02.name | 19 | `Combat Reflexes` | `''`, `'CAMMA BALAYAS'`, `'Combat Relayes'` |
| skill p04.r11.name | 19 | `Fishing Rod Technology` | `''`, `'FISHING ROI TECHNOLOGY'`, `'Fishing Rat Technology'` |
| skill p06.r06.name | 19 | `Laser Weaponry Technology` | `''`, `'LOST WEARONY TECHNOLOGY'`, `'Laser Weap onry Technology\\\\\\\\\\\\\` |
| skill p07.r08.name | 19 | `Marksmanship` | `''`, `'LAVISAN'`, `'marksmanshipMarksmanship%%%%%%%%%%%%%%%` |
| skill p07.r09.name | 19 | `Martial Arts` | `''`, `'MAM'`, `'Mental Arts'` |
| skill p08.r06.name | 19 | `Mining Laser Technology` | `''`, `'Mining LOST TECHNOLOGY'`, `'Mining Laser Technology1111111111111111` |
| skill p09.r02.name | 19 | `Precision Artefact Extraction` | `''`, `'PERSONAL AMERICAN EXACATION'`, `'Precision Arezet Extracion'` |
| skill p10.r11.name | 19 | `Spacecraft Engineering` | `''`, `'SPECIAL SYNICON'`, `'Spacewaft Engineering'` |

# Failure-cell overlap analysis

Engines reporting cells: **13** of 13 engines.

## Distribution of cell failure across engines

How many engines fail on each cell? If the distribution skews toward 'few engines fail' (heavy 0-failures bin), failures are engine-specific and ensembling helps. If it skews toward 'many engines fail' (heavy high-N-failures tail), some cells are intrinsically hard and ensembling won't save them.

| # engines failing | # cells | share | bar |
| --- | --- | --- | --- |
| 0 | 205 | 34.5% | ████████████████████████████████████████ |
| 1 | 94 | 15.8% | ██████████████████ |
| 2 | 37 | 6.2% | ███████ |
| 3 | 16 | 2.7% | ███ |
| 4 | 22 | 3.7% | ████ |
| 5 | 16 | 2.7% | ███ |
| 6 | 53 | 8.9% | ██████████ |
| 7 | 52 | 8.8% | ██████████ |
| 8 | 29 | 4.9% | ██████ |
| 9 | 35 | 5.9% | ███████ |
| 10 | 24 | 4.0% | █████ |
| 11 | 8 | 1.3% | ██ |
| 12 | 3 | 0.5% | █ |

## Hardest cells (failed by ≥ 7 engines)

Top 30 by # failing engines.

| Cell | # fail | Expected | Sample OCR (top-3 engines) |
| --- | --- | --- | --- |
| skill p03.r06.name | 12 | `Courage` | `'Courage---'`, `'Courage----'`, `'Courage----'` |
| profession p02.r03.name | 12 | `Whipper (Dmg)` | `'Whipper(Dmg))'`, `'Whipper(Dmg))'`, `'Whipper(Dmg))'` |
| profession p13.r03.name | 12 | `Animal Tamer` | `'AnimalTamer-'`, `'AnimalTamer-'`, `'AnimalTamer-'` |
| skill p02.r06.name | 11 | `Bravado` | `'Bravado---'`, `'Bravado>---'`, `'Bravado----'` |
| skill p08.r06.name | 11 | `Mining Laser Technology` | `'MiningLaserTechnology2-'`, `'MiningLaserTechnologyI-'`, `'MiningLaserTechnology--'` |
| skill p10.r02.name | 11 | `Scan Animal` | `'ScanAnimal---'`, `'ScanAnimal---'`, `'ScanAnimal---'` |
| skill p10.r06.name | 11 | `Scan Technology` | `'ScanTechnologyy--'`, `'ScanTechnologyy--'`, `'ScanTechnologyy--'` |
| skill p12.r02.name | 11 | `Translocation` | `'Translocatiotlon---'`, `'Translocation---'`, `'Translocation---'` |
| profession p01.r01.rank_level | 11 | `74` | `74744`, `7474`, `744` |
| profession p03.r04.name | 11 | `Knifefighter (Hit)` | `'Knifefighter(Hiter(Hig10'`, `'Knifefighter(Hiter(Hit)'`, `'Knifefighter(Hiter(Hit)'` |
| profession p12.r04.name | 11 | `Sweat Gatherer` | `'SweatGathererer'`, `'SweatGathererer'`, `'SweatGathererer'` |
| skill p01.r06.name | 10 | `Animal Lore` | `'AnimalLore---'`, `'AnimalLore---'`, `'AnimalLore---'` |
| skill p01.r08.name | 10 | `Armor Technology` | `'ArmorTechnologyGy--'`, `'ArmorTechnologygy--'`, `'ArmorTechnologygy--'` |
| skill p03.r02.name | 10 | `Combat Reflexes` | `'CombatReflexeflexes--'`, `'CombatReflexeflexess--'`, `'CombatReflexeflexess--'` |
| skill p04.r02.name | 10 | `Electrokinesis` | `'Electrokinesis---'`, `'Electrokinesis---'`, `'Electrokinesinesis---'` |
| skill p05.r01.name | 10 | `Food Technology` | `'FoodTechnologyy--'`, `'FoodTechnologyy--'`, `'FoodTechnologyy--'` |
| skill p05.r04.name | 10 | `Gastronomy` | `'Gastronomy---'`, `'Gastronomy---'`, `'Gastronomy---'` |
| skill p05.r06.name | 10 | `Genetics` | `'Genetics---'`, `'Geneticss---'`, `'Geneticss---'` |
| skill p06.r02.name | 10 | `Inflict Melee Damage` | `'InflictMeleeDamage--'`, `'InflictMeleeDamage--'`, `'Inflict.MeleeDamage--'` |
| skill p06.r03.name | 10 | `Inflict Ranged Damage` | `'InflictRangedDamage--'`, `'InflictRangedDamage--'`, `'InflictRangedDamage--'` |
| skill p06.r06.name | 10 | `Laser Weaponry Technology` | `'LaserWeaponryTechnologyy'`, `'LaserWeaponryTechnologyy'`, `'LaserWeaponryTechnologyy'` |
| skill p06.r09.name | 10 | `Machinery` | `'Machineryry---'`, `'Machineryry---'`, `'Machineryry---'` |
| skill p07.r02.name | 10 | `Manufacture Enhancers` | `'ManufactureEnhancers--'`, `'ManufactureEnhancers--'`, `'ManufactureEnhancers--'` |
| skill p07.r05.name | 10 | `Manufacture Tools` | `'ManufactureToolsXe--'`, `'ManufactureToolsls--'`, `'ManufactureToolsls--'` |
| skill p08.r02.name | 10 | `Metallurgy` | `'Metallurgyay---'`, `'Metallurgygy---'`, `'Metallurgygy---'` |
| skill p08.r08.name | 10 | `Particle Beamer Technology` | `'ParticleBeamerTechnologyy'`, `'ParticleBeamerTechnologyy'`, `'ParticleBeamerTechnologyy'` |
| skill p09.r06.name | 10 | `Provisioning` | `'Provisioning---'`, `'Provisioning---'`, `'Provisioning---'` |
| skill p11.r02.name | 10 | `Spacecraft Weaponry` | `'SpacecraftWeaponry--'`, `'SpacecraftWeaponry--'`, `'SpacecraftWeat.Weaponry--'` |
| skill p11.r06.name | 10 | `Surveying` | `'Surveyingng---'`, `'Surveyingng---'`, `'Surveyingng---'` |
| skill p11.r11.name | 10 | `Texture Pattern Matching` | `'TexturePatternMatching--'`, `'TexturePatternMatching--'`, `'TexturePatternMatching--'` |

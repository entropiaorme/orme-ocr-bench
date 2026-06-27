# Failure-cell overlap analysis

Engines reporting cells: **13** of 13 engines.

## Distribution of cell failure across engines

How many engines fail on each cell? If the distribution skews toward 'few engines fail' (heavy 0-failures bin), failures are engine-specific and ensembling helps. If it skews toward 'many engines fail' (heavy high-N-failures tail), some cells are intrinsically hard and ensembling won't save them.

| # engines failing | # cells | share | bar |
| --- | --- | --- | --- |
| 0 | 103 | 17.3% | ███████████████████████████████████████ |
| 1 | 98 | 16.5% | █████████████████████████████████████ |
| 2 | 105 | 17.7% | ████████████████████████████████████████ |
| 3 | 45 | 7.6% | █████████████████ |
| 4 | 72 | 12.1% | ███████████████████████████ |
| 5 | 52 | 8.8% | ████████████████████ |
| 6 | 39 | 6.6% | ███████████████ |
| 7 | 43 | 7.2% | ████████████████ |
| 8 | 25 | 4.2% | ██████████ |
| 9 | 9 | 1.5% | ███ |
| 10 | 3 | 0.5% | █ |

## Hardest cells (failed by ≥ 7 engines)

Top 30 by # failing engines.

| Cell | # fail | Expected | Sample OCR (top-3 engines) |
| --- | --- | --- | --- |
| skill p03.r06.name | 10 | `Courage` | `'Courage---'`, `'Courage----'`, `'Courage-'` |
| profession p02.r03.name | 10 | `Whipper (Dmg)` | `'Whipper(Dmg))'`, `'Whipper(Dmg))'`, `'Whipper(Dmg))'` |
| profession p13.r03.name | 10 | `Animal Tamer` | `'AnimalTamer-'`, `'AnimalTamer-'`, `'AnimalTamer-'` |
| skill p01.r06.name | 9 | `Animal Lore` | `'AnimalLore---'`, `'AnimalLore---'`, `'AnimalLore---'` |
| skill p02.r06.name | 9 | `Bravado` | `'Bravado---'`, `'Bravado----'`, `'Bravado-'` |
| skill p08.r06.name | 9 | `Mining Laser Technology` | `'MiningLaserTechnology2-'`, `'MiningLaserTechnology--'`, `'MiningLaserTechnology-'` |
| skill p10.r02.name | 9 | `Scan Animal` | `'ScanAnimal---'`, `'ScanAnimal---'`, `'ScanAnimal--'` |
| skill p10.r06.name | 9 | `Scan Technology` | `'ScanTechnologyy--'`, `'ScanTechnologyy--'`, `'ScanTechnologyy'` |
| skill p12.r02.name | 9 | `Translocation` | `'Translocatiotlon---'`, `'Translocation---'`, `'Translocation-'` |
| profession p01.r01.rank_level | 9 | `74` | `74744`, `744`, `74744` |
| profession p03.r04.name | 9 | `Knifefighter (Hit)` | `'Knifefighter(Hiter(Hig10'`, `'Knifefighter(Hiter(Hit)'`, `'Knifefighter(Hiter(Hit'` |
| profession p12.r04.name | 9 | `Sweat Gatherer` | `'SweatGathererer'`, `'SweatGathererer'`, `'SweatGathererer'` |
| profession p09.r01.rank_level | 8 | `1` | `'Green;'`, `11`, `11` |
| skill p01.r08.name | 8 | `Armor Technology` | `'ArmorTechnologyGy--'`, `'ArmorTechnologygy--'`, `'ArmorTechnologygy'` |
| skill p03.r02.name | 8 | `Combat Reflexes` | `'CombatReflexeflexes--'`, `'CombatReflexeflexess--'`, `'CombatReflexesS--'` |
| skill p04.r02.name | 8 | `Electrokinesis` | `'Electrokinesis---'`, `'Electrokinesinesis---'`, `'Electrokinesis---'` |
| skill p05.r01.name | 8 | `Food Technology` | `'FoodTechnologyy--'`, `'FoodTechnologyy--'`, `'FoodTechnologyy'` |
| skill p05.r04.name | 8 | `Gastronomy` | `'Gastronomy---'`, `'Gastronomy---'`, `'Gastronomy---'` |
| skill p05.r06.name | 8 | `Genetics` | `'Genetics---'`, `'Geneticss---'`, `'Geneticss'` |
| skill p06.r02.name | 8 | `Inflict Melee Damage` | `'InflictMeleeDamage--'`, `'Inflict.MeleeDamage--'`, `'InflictMeleeDamage-'` |
| skill p06.r03.name | 8 | `Inflict Ranged Damage` | `'InflictRangedDamage--'`, `'InflictRangedDamage--'`, `'InfictRangedDamage'` |
| skill p06.r06.name | 8 | `Laser Weaponry Technology` | `'LaserWeaponryTechnologyy'`, `'LaserWeaponryTechnologyy'`, `'LaserWeaponryTechnologyy'` |
| skill p06.r09.name | 8 | `Machinery` | `'Machineryry---'`, `'Machineryry---'`, `'Machineryry'` |
| skill p07.r02.name | 8 | `Manufacture Enhancers` | `'ManufactureEnhancers--'`, `'ManufactureEnhancers--'`, `'ManufactureEnhancers-'` |
| skill p07.r05.name | 8 | `Manufacture Tools` | `'ManufactureToolsXe--'`, `'ManufactureToolsls--'`, `'ManufactureToolsls'` |
| skill p07.r09.name | 8 | `Martial Arts` | `'MartialArts---'`, `'MartialArts---'`, `'MartialArts---'` |
| skill p08.r02.name | 8 | `Metallurgy` | `'Metallurgyay---'`, `'Metallurgygy---'`, `'Metallurgygy'` |
| skill p08.r08.name | 8 | `Particle Beamer Technology` | `'ParticleBeamerTechnologyy'`, `'ParticleBeamerTechnologyy'`, `'ParticleBeamerTechnologyy'` |
| skill p09.r06.name | 8 | `Provisioning` | `'Provisioning---'`, `'Provisioning---'`, `'Provisioning---'` |
| skill p11.r02.name | 8 | `Spacecraft Weaponry` | `'SpacecraftWeaponry--'`, `'SpacecraftWeat.Weaponry--'`, `'SpacecraftWeaponry-'` |

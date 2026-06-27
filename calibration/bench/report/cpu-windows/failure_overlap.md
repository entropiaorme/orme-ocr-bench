# Failure-cell overlap analysis

Engines reporting cells: **18** of 18 engines.

## Distribution of cell failure across engines

How many engines fail on each cell? If the distribution skews toward 'few engines fail' (heavy 0-failures bin), failures are engine-specific and ensembling helps. If it skews toward 'many engines fail' (heavy high-N-failures tail), some cells are intrinsically hard and ensembling won't save them.

| # engines failing | # cells | share | bar |
| --- | --- | --- | --- |
| 0 | 25 | 4.2% | ███████████ |
| 1 | 53 | 8.9% | ████████████████████████ |
| 2 | 78 | 13.1% | ███████████████████████████████████ |
| 3 | 44 | 7.4% | ████████████████████ |
| 4 | 89 | 15.0% | ████████████████████████████████████████ |
| 5 | 48 | 8.1% | ██████████████████████ |
| 6 | 18 | 3.0% | ████████ |
| 7 | 25 | 4.2% | ███████████ |
| 8 | 38 | 6.4% | █████████████████ |
| 9 | 41 | 6.9% | ██████████████████ |
| 10 | 40 | 6.7% | ██████████████████ |
| 11 | 31 | 5.2% | ██████████████ |
| 12 | 32 | 5.4% | ██████████████ |
| 13 | 21 | 3.5% | █████████ |
| 14 | 9 | 1.5% | ████ |
| 15 | 2 | 0.3% | █ |

## Hardest cells (failed by ≥ 9 engines)

Top 30 by # failing engines.

| Cell | # fail | Expected | Sample OCR (top-3 engines) |
| --- | --- | --- | --- |
| skill p03.r06.name | 15 | `Courage` | `'commeetit'`, `'Cowage'`, `'Correspondence'` |
| profession p02.r03.name | 15 | `Whipper (Dmg)` | `'whippermmgiascco'`, `'Whipper/Dmg)'`, `'Whipper/Ding)'` |
| skill p01.r06.name | 14 | `Animal Lore` | `'animallnneessssssca'`, `'Arigations'`, `'Anthallowers/parting'` |
| skill p02.r06.name | 14 | `Bravado` | `'branniettii'`, `'Brivato'`, `'Birdstropperson'` |
| skill p08.r06.name | 14 | `Mining Laser Technology` | `'wininglseerechnologyy'`, `'Wininglacer7edgetrapy'`, `'Nntp-Posting-Host:'` |
| skill p10.r02.name | 14 | `Scan Animal` | `'scananinall1333344'`, `'Scamanal'`, `'SextAinstresses'` |
| skill p12.r02.name | 14 | `Translocation` | `'transloatinnnss33aa'`, `'Tansboation'`, `'Transconscientious'` |
| profession p01.r01.rank_level | 14 | `74` | `74200`, `740`, `'Elite,740.CA>'` |
| profession p03.r04.name | 14 | `Knifefighter (Hit)` | `'knilefighterhii'`, `'Knitefighter/Hic)'`, `'Kailefighter(Hingtonousex'` |
| profession p12.r04.name | 14 | `Sweat Gatherer` | `'sweatatheeeerccccmm'`, `'SweatHerer'`, `'SweatGatherer@thyde.com'` |
| profession p13.r03.name | 14 | `Animal Tamer` | `'animaltaerrsssccee'`, `'AnimalTamer@rando.utech.e'`, `'AnimalTamer-'` |
| skill p01.r08.name | 13 | `Armor Technology` | `'armoriecnnlogyycssseeee'`, `'Amaritechnology'`, `'Autorianations/parking'` |
| skill p03.r02.name | 13 | `Combat Reflexes` | `'contattullnesssccccsged'`, `'CombarketRes'`, `'ContextRessensionary'` |
| skill p04.r02.name | 13 | `Electrokinesis` | `'elecroiinesssss33cce'`, `'Electroliness'`, `'Electroencephalograms'` |
| skill p05.r01.name | 13 | `Food Technology` | `'foodfechaalogyycffccee'`, `'FoodTrechnology'`, `'Fooliebrooks@sund.com'` |
| skill p05.r06.name | 13 | `Genetics` | `'gonlicstti'`, `'Genellicates'`, `'Carlishness@news.com'` |
| skill p06.r02.name | 13 | `Inflict Melee Damage` | `'bnllitteeeeoooooppppeecc'`, `'bitchelbe.Dannes.com'`, `'intellectorspon.com'` |
| skill p06.r03.name | 13 | `Inflict Ranged Damage` | `'bailitaaageeaaaageeeeecc'`, `'halic...Rec.Rec.longedDamage.c'`, `'interRogational'` |
| skill p06.r06.name | 13 | `Laser Weaponry Technology` | `'laserlosporrrcccnnooooo'`, `'Laserpomyrechnology'`, `'LawrillascryTechnology.mi'` |
| skill p07.r02.name | 13 | `Manufacture Enhancers` | `'manudichneehhaarnnssseec'`, `'ManufactureFace..ucs'`, `'Newsgroups:'` |
| skill p07.r09.name | 13 | `Martial Arts` | `'warialarssccsssccaeeeee'`, `'Martalations'`, `'Nntp-Posting-Host:'` |
| skill p08.r02.name | 13 | `Metallurgy` | `'netluggessis'`, `'Metalugy'`, `'Newsgroups:'` |
| skill p08.r08.name | 13 | `Particle Beamer Technology` | `'partilebaaer7tchoollggocc'`, `'ParticleBeamerlechnology'`, `'Patterdenetics.midemit.ed'` |
| skill p10.r06.name | 13 | `Scan Technology` | `'scantechnologrrcsccceuu'`, `'SeaTietrogen@theng.com'`, `'ScanTechnologyy--'` |
| skill p11.r02.name | 13 | `Spacecraft Weaponry` | `'sprcecaatnnppaoonyyyccc'`, `'Spatecrain/Verpory.COP.'`, `'Speechleapnystations'` |
| skill p11.r06.name | 13 | `Surveying` | `'sumeyingssssssscc'`, `'Sumveying'`, `'Sunfing@cs.us.edu'` |
| skill p11.r11.name | 13 | `Texture Pattern Matching` | `'tentunpotenmaatiingggeccd'`, `'TextmePathing'`, `'Techne-Premilating'` |
| skill p12.r01.name | 13 | `Tools Technology` | `'toolstehnologyycffcceec'`, `'Todstectment.'`, `'TobTchology,Markiship'` |
| skill p12.r07.name | 13 | `Weapons Handling` | `'weeppnshindiinggscccecc'`, `'WeaponsHanding'`, `'Newsgroups:'` |
| skill p12.r10.name | 13 | `Wood Processing` | `'weodproeesinggsssshhhccc'`, `'WeotPlecessing'`, `'Nntp-Posting-Host:'` |

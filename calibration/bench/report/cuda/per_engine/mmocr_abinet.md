# `mmocr_abinet` deep dive

## Headline

- Effective accuracy: **34.5%** (71 PASS + 134 RECOVERED of 594 data cells)
- Failure modes: hallucinate=176, drop=0, substitute=347, reject=0
- Per-cell mean: **72.8 ms** (p95 83.6 ms, max 91.6 ms)
- Init: load 9755 ms + warmup 114 ms
- RSS: warmup 814 MB, final 825 MB
- Subprocess wall: **55.8 s**

## Confidence distribution

min=0.103  p25=0.423  median=0.654  p75=0.920  max=1.000  mean=0.653

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 54.9% | 1+134 | 246 |
| `level` | 47.9% | 69+0 | 144 |
| `rank_level` | 1.0% | 1+0 | 102 |
| `percent` | 0.0% | 0+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p08.r07 | `name` | UNRECOVERABLE | substitute | `'Nutrition'` | `'nensi'` | 0.103 |
| skill p01.r00 | `name` | UNRECOVERABLE | hallucinate | `'Agility'` | `'nntpposiinnnos'` | 0.125 |
| skill p01.r04 | `name` | RECOVERED | hallucinate | `'Anatomy'` | `'anatomnnssssss'` | 0.140 |
| skill p01.r01 | `name` | UNRECOVERABLE | hallucinate | `'Aim'` | `'antsrroit'` | 0.145 |
| skill p08.r04 | `name` | RECOVERED | hallucinate | `'Mining'` | `'ninnggottsnns'` | 0.152 |
| skill p05.r06 | `name` | UNRECOVERABLE | substitute | `'Genetics'` | `'gonlicstti'` | 0.154 |
| skill p04.r08 | `name` | UNRECOVERABLE | hallucinate | `'First Aid'` | `'frstaasssscc3s3'` | 0.156 |
| skill p02.r06 | `name` | UNRECOVERABLE | hallucinate | `'Bravado'` | `'branniettii'` | 0.163 |
| skill p05.r07 | `name` | UNRECOVERABLE | hallucinate | `'Geology'` | `'golngrottiinc'` | 0.164 |
| skill p02.r11 | `name` | UNRECOVERABLE | hallucinate | `'Clubs'` | `'causstsssssass'` | 0.177 |
| skill p06.r04 | `name` | RECOVERED | substitute | `'Intelligence'` | `'hneelllnccaasssscc'` | 0.179 |
| skill p04.r05 | `name` | RECOVERED | hallucinate | `'Evade'` | `'exadereatiaaaa'` | 0.182 |
| skill p10.r01 | `name` | UNRECOVERABLE | hallucinate | `'Rifle'` | `'messareii'` | 0.184 |
| skill p01.r02 | `name` | RECOVERED | hallucinate | `'Alertness'` | `'mletiessssasss'` | 0.189 |
| skill p11.r04 | `name` | UNRECOVERABLE | hallucinate | `'Strength'` | `'steeqiiissscss'` | 0.191 |
| skill p09.r00 | `name` | UNRECOVERABLE | hallucinate | `'Power Catalyst'` | `'poneetttnipssss333sseee'` | 0.197 |
| skill p05.r04 | `name` | RECOVERED | substitute | `'Gastronomy'` | `'gasdtnommyssct'` | 0.205 |
| skill p01.r10 | `name` | UNRECOVERABLE | hallucinate | `'Athletics'` | `'ahillcsscssssssssseee'` | 0.207 |
| skill p06.r02 | `name` | UNRECOVERABLE | substitute | `'Inflict Melee Damage'` | `'bnllitteeeeoooooppppeecc'` | 0.227 |
| skill p06.r03 | `name` | UNRECOVERABLE | substitute | `'Inflict Ranged Damage'` | `'bailitaaageeaaaageeeeecc'` | 0.229 |

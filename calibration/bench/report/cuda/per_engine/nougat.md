# `nougat` deep dive

## Headline

- Effective accuracy: **7.1%** (6 PASS + 36 RECOVERED of 594 data cells)
- Failure modes: hallucinate=393, drop=12, substitute=175, reject=8
- Per-cell mean: **1228.1 ms** (p95 1745.3 ms, max 1790.0 ms)
- Init: load 19041 ms + warmup 2021 ms
- RSS: warmup 1711 MB, final 1747 MB
- Subprocess wall: **784.2 s**

## Confidence distribution

min=0.169  p25=0.412  median=0.712  p75=0.730  max=0.821  mean=0.592

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 17.1% | 6+36 | 246 |
| `level` | 0.0% | 0+0 | 144 |
| `rank_level` | 0.0% | 0+0 | 102 |
| `percent` | 0.0% | 0+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p07.r00 | `name` | UNRECOVERABLE | drop | `'Manufacture Attachments'` | `'**Matthew'` | 0.169 |
| skill p09.r08 | `name` | UNRECOVERABLE | substitute | `'Pyrokinesis'` | `'## Appendix'` | 0.183 |
| skill p11.r04 | `name` | UNRECOVERABLE | substitute | `'Strength'` | `'## Chapter 3'` | 0.197 |
| skill p07.r11 | `name` | UNRECOVERABLE | substitute | `'Melee Combat'` | `'**Males**'` | 0.201 |
| skill p06.r06 | `name` | UNRECOVERABLE | reject | `'Laser Weaponry Technology'` | `''` | 0.205 |
| skill p11.r06 | `name` | UNRECOVERABLE | substitute | `'Surveying'` | `'## Summary'` | 0.217 |
| profession p07.r04 | `name` | UNRECOVERABLE | drop | `'Tool Engineer'` | `'**1.**'` | 0.235 |
| skill p02.r03 | `name` | UNRECOVERABLE | substitute | `'Bioregenesis'` | `'## Chapter 6'` | 0.241 |
| skill p08.r07 | `name` | UNRECOVERABLE | substitute | `'Nutrition'` | `'## Author'` | 0.243 |
| profession p02.r04 | `name` | RECOVERED | substitute | `'Ranged BLP (Dmg)'` | `'**Ratinged BP Unit**'` | 0.263 |
| profession p04.r06 | `name` | UNRECOVERABLE | substitute | `'Gauss Sniper (Hit)'` | `'**Cause spinor**'` | 0.272 |
| skill p10.r00 | `name` | UNRECOVERABLE | substitute | `'Resource Gathering'` | `'**Resonites cientifie**'` | 0.274 |
| profession p08.r03 | `rank_level` | UNRECOVERABLE | substitute | `2` | `'* [10]'` | 0.278 |
| profession p11.r02 | `rank_level` | UNRECOVERABLE | substitute | `2` | `'* [10]'` | 0.279 |
| profession p11.r03 | `rank_level` | UNRECOVERABLE | substitute | `2` | `'* [10]'` | 0.279 |
| profession p11.r01 | `rank_level` | UNRECOVERABLE | substitute | `2` | `'* [10]'` | 0.279 |
| profession p09.r04 | `rank_level` | UNRECOVERABLE | substitute | `0` | `'* [19]'` | 0.281 |
| skill p11.r06 | `level` | UNRECOVERABLE | hallucinate | `1` | `10` | 0.281 |
| skill p05.r09 | `level` | UNRECOVERABLE | hallucinate | `1` | `10` | 0.282 |
| skill p02.r09 | `level` | UNRECOVERABLE | hallucinate | `1` | `10` | 0.282 |

# `trocr_large_printed` deep dive

## Headline

- Effective accuracy: **55.4%** (309 PASS + 20 RECOVERED of 594 data cells)
- Failure modes: hallucinate=228, drop=0, substitute=57, reject=0
- Per-cell mean: **425.9 ms** (p95 644.5 ms, max 1906.4 ms)
- Init: load 21711 ms + warmup 581 ms
- RSS: warmup 1316 MB, final 1614 MB
- Subprocess wall: **285.5 s**

## Confidence distribution

min=0.155  p25=0.366  median=0.448  p75=0.632  max=0.967  mean=0.495

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 40.7% | 80+20 | 246 |
| `level` | 96.5% | 139+0 | 144 |
| `rank_level` | 4.9% | 5+0 | 102 |
| `percent` | 83.3% | 85+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p12.r04 | `level` | UNRECOVERABLE | hallucinate | `88` | `8888` | 0.165 |
| profession p12.r00 | `rank_level` | UNRECOVERABLE | hallucinate | `30` | `'Great, 30-35-35-4"'` | 0.171 |
| profession p13.r02 | `name` | UNRECOVERABLE | hallucinate | `'Captain'` | `'CAPTAIN CARD:'` | 0.200 |
| profession p08.r06 | `rank_level` | UNRECOVERABLE | hallucinate | `2` | `'GREEN. 2-1-LOB-UICE (818)'` | 0.202 |
| skill p09.r09 | `level` | UNRECOVERABLE | hallucinate | `5018` | `50181000000` | 0.208 |
| skill p03.r06 | `name` | RECOVERED | hallucinate | `'Courage'` | `'Courage & US ON BACK'` | 0.215 |
| skill p01.r08 | `level` | UNRECOVERABLE | substitute | `101` | `1011` | 0.218 |
| profession p03.r07 | `rank_level` | UNRECOVERABLE | hallucinate | `18` | `1` | 0.224 |
| profession p03.r06 | `rank_level` | UNRECOVERABLE | hallucinate | `18` | `1` | 0.230 |
| profession p11.r04 | `rank_level` | UNRECOVERABLE | hallucinate | `2` | `'GREEN. 2-1-1-1-4"'` | 0.231 |
| profession p08.r04 | `rank_level` | UNRECOVERABLE | hallucinate | `2` | `'GREEN. 2-1-1-1-4"'` | 0.232 |
| profession p12.r02 | `percent` | UNRECOVERABLE | hallucinate | `71.7` | `717.0` | 0.233 |
| profession p10.r02 | `name` | RECOVERED | hallucinate | `'Robot Looter'` | `'ROBOT LOOTER : LIFTINGLEAUTHOR'` | 0.245 |
| profession p08.r07 | `rank_level` | UNRECOVERABLE | hallucinate | `2` | `'GREEN. 2-1-1-4" (818)'` | 0.246 |
| profession p08.r05 | `rank_level` | UNRECOVERABLE | hallucinate | `2` | `'GREEN. 2-1-1-4" (818)'` | 0.247 |
| profession p11.r04 | `name` | RECOVERED | hallucinate | `'Miner'` | `'MINER: MARINA, JOHORANAN BAHRU, JOHORAN'` | 0.256 |
| profession p07.r00 | `rank_level` | UNRECOVERABLE | hallucinate | `3` | `'BEGINNER, 3-4-4" HANDY,'` | 0.274 |
| skill p11.r03 | `name` | UNRECOVERABLE | hallucinate | `'Stamina'` | `'STAMINA, JOHORA,'` | 0.276 |
| profession p13.r04 | `rank_level` | UNRECOVERABLE | hallucinate | `6` | `'APPRINTICE, 6-G-G-G-U-D-DATE'` | 0.276 |
| profession p04.r02 | `name` | RECOVERED | hallucinate | `'Whipper (Hit)'` | `'WHIPPER (HIT) : (818-876-876-8'` | 0.279 |

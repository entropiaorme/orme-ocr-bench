# `rapidocr` deep dive

## Headline

- Effective accuracy: **100.0%** (590 PASS + 4 RECOVERED of 594 data cells)
- Failure modes: hallucinate=0, drop=0, substitute=4, reject=0
- Per-cell mean: **8.9 ms** (p95 15.6 ms, max 66.7 ms)
- Init: load 518 ms + warmup 69 ms
- RSS: warmup 101 MB, final 107 MB
- Subprocess wall: **6.5 s**

## Confidence distribution

min=0.299  p25=0.706  median=0.799  p75=0.864  max=0.948  mean=0.755

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 100.0% | 242+4 | 246 |
| `level` | 100.0% | 144+0 | 144 |
| `rank_level` | 100.0% | 102+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| profession p04.r00 | `name` | RECOVERED | substitute | `'Brawler (Hit)'` | `'Brawler (Hit)兴'` | 0.777 |
| profession p13.r00 | `name` | RECOVERED | substitute | `'Gunner (Dmg)'` | `'Gunner(Dmg）兴'` | 0.805 |
| profession p02.r03 | `name` | RECOVERED | substitute | `'Whipper (Dmg)'` | `'Whipper(Dmg）'` | 0.825 |
| profession p11.r00 | `name` | RECOVERED | substitute | `'Fish Looter'` | `'FishLooter兴'` | 0.849 |

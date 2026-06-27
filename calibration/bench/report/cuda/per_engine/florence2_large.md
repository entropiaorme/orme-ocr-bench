# `florence2_large` deep dive

## Headline

- Effective accuracy: **65.0%** (295 PASS + 91 RECOVERED of 594 data cells)
- Failure modes: hallucinate=0, drop=100, substitute=199, reject=0
- Per-cell mean: **342.9 ms** (p95 390.5 ms, max 484.0 ms)
- Init: load 17434 ms + warmup 834 ms
- RSS: warmup 1775 MB, final 1841 MB
- Subprocess wall: **232.2 s**

## Confidence distribution

min=0.472  p25=0.686  median=0.766  p75=0.850  max=0.956  mean=0.761

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 80.5% | 107+91 | 246 |
| `level` | 77.1% | 111+0 | 144 |
| `rank_level` | 63.7% | 65+0 | 102 |
| `percent` | 11.8% | 12+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p12.r00 | `name` | RECOVERED | substitute | `'Tier Upgrading'` | `'Iber Upgrade'` | 0.472 |
| skill p10.r08 | `name` | UNRECOVERABLE | substitute | `'Serendipity'` | `'SEXONMINDLY'` | 0.499 |
| skill p03.r00 | `name` | RECOVERED | substitute | `'Color Matching'` | `'Cord MacNIM'` | 0.499 |
| skill p05.r04 | `name` | UNRECOVERABLE | substitute | `'Gastronomy'` | `'CASVANONNY'` | 0.501 |
| skill p01.r05 | `name` | RECOVERED | substitute | `'Angling'` | `'ANOM'` | 0.521 |
| skill p10.r09 | `name` | RECOVERED | substitute | `'Shortblades'` | `'Shorlalades'` | 0.524 |
| skill p11.r08 | `name` | UNRECOVERABLE | substitute | `'Tailoring'` | `'TALOM'` | 0.526 |
| skill p04.r04 | `name` | UNRECOVERABLE | substitute | `'Engineering'` | `'Empicewing'` | 0.531 |
| skill p08.r03 | `name` | RECOVERED | substitute | `'Mindforce Harmony'` | `'Mikroce Hanony'` | 0.532 |
| skill p05.r03 | `name` | RECOVERED | substitute | `'Fragmentating'` | `'Fragmentzoom'` | 0.535 |
| skill p02.r03 | `name` | RECOVERED | substitute | `'Bioregenesis'` | `'Biogrpness'` | 0.544 |
| profession p02.r06 | `rank_level` | UNRECOVERABLE | substitute | `32` | `'inspirin'` | 0.546 |
| profession p02.r04 | `rank_level` | UNRECOVERABLE | substitute | `32` | `'inspirin'` | 0.552 |
| skill p02.r00 | `name` | RECOVERED | substitute | `'BLP Weaponry Technology'` | `'BLP Weryory Technology'` | 0.554 |
| profession p02.r05 | `rank_level` | UNRECOVERABLE | substitute | `32` | `'inspirin'` | 0.555 |
| profession p03.r01 | `name` | RECOVERED | substitute | `'Pyro Kinetic (Hit)'` | `'Pyro Kneetic (Hf'` | 0.558 |
| skill p06.r05 | `name` | UNRECOVERABLE | drop | `'Jamming'` | `'VAN'` | 0.563 |
| skill p06.r11 | `name` | RECOVERED | drop | `'Manufacture Armor'` | `'Manu'` | 0.568 |
| skill p11.r00 | `name` | UNRECOVERABLE | drop | `'Spacecraft Pilot'` | `'SPE'` | 0.569 |
| profession p12.r01 | `percent` | UNRECOVERABLE | drop | `51.8` | `51.0` | 0.570 |

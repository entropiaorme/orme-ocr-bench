# `trocr` deep dive

## Headline

- Effective accuracy: **56.7%** (323 PASS + 14 RECOVERED of 594 data cells)
- Failure modes: hallucinate=122, drop=0, substitute=149, reject=0
- Per-cell mean: **123.2 ms** (p95 232.2 ms, max 312.6 ms)
- Init: load 23759 ms + warmup 558 ms
- RSS: warmup 2387 MB, final 2406 MB
- Subprocess wall: **100.0 s**

## Confidence distribution

min=0.240  p25=0.598  median=0.814  p75=0.990  max=1.000  mean=0.775

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 18.7% | 32+14 | 246 |
| `level` | 100.0% | 144+0 | 144 |
| `rank_level` | 44.1% | 45+0 | 102 |
| `percent` | 100.0% | 102+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p11.r04 | `name` | UNRECOVERABLE | hallucinate | `'Strength'` | `'STRENGTH : 1/4"'` | 0.240 |
| skill p08.r04 | `name` | UNRECOVERABLE | hallucinate | `'Mining'` | `'MUNING - 1 DAY'` | 0.246 |
| skill p10.r01 | `name` | UNRECOVERABLE | substitute | `'Rifle'` | `'RMME :'` | 0.254 |
| skill p02.r06 | `name` | UNRECOVERABLE | hallucinate | `'Bravado'` | `'BARAVADO - 1 DAYS FOR FULL US ON'` | 0.263 |
| skill p02.r01 | `name` | UNRECOVERABLE | hallucinate | `'Baitfishing'` | `'BAITTSHING - 1 DAYS FROM'` | 0.291 |
| skill p07.r09 | `name` | UNRECOVERABLE | hallucinate | `'Martial Arts'` | `'MARITAL ARTS - 1 DAY ON'` | 0.307 |
| skill p01.r04 | `name` | UNRECOVERABLE | hallucinate | `'Anatomy'` | `'ANALONY - 1 DAY'` | 0.309 |
| skill p04.r00 | `name` | RECOVERED | hallucinate | `'Dodge'` | `'DODGE AND ONLINE ONLINE WITH'` | 0.320 |
| skill p09.r11 | `name` | UNRECOVERABLE | hallucinate | `'Reputation'` | `'REQUTAIN FOR A FREE'` | 0.321 |
| profession p14.r03 | `name` | UNRECOVERABLE | substitute | `'Face Sculptor'` | `'FACE SANDTOR :'` | 0.340 |
| skill p01.r02 | `name` | UNRECOVERABLE | hallucinate | `'Alertness'` | `'ALERINESS - CASHIERING ONCLUSIVE'` | 0.343 |
| skill p10.r02 | `name` | UNRECOVERABLE | hallucinate | `'Scan Animal'` | `'SCAN ANIMAL - 1 DAYS ON'` | 0.346 |
| skill p01.r01 | `name` | RECOVERED | hallucinate | `'Aim'` | `'ALM @6.00'` | 0.348 |
| skill p02.r03 | `name` | UNRECOVERABLE | hallucinate | `'Bioregenesis'` | `'BLOPENGENES - 1 DAYS ONCLUSIVE'` | 0.350 |
| skill p04.r09 | `name` | UNRECOVERABLE | hallucinate | `'Fishing'` | `'FISHING - 1 DAY ONCLUSIVE'` | 0.359 |
| skill p10.r00 | `name` | UNRECOVERABLE | substitute | `'Resource Gathering'` | `'RESOURCE CATEFING - 1 DAY'` | 0.362 |
| skill p04.r04 | `name` | UNRECOVERABLE | hallucinate | `'Engineering'` | `'ENGINIENTING - 1 DAYS ONCLUSIVE'` | 0.363 |
| skill p03.r07 | `name` | UNRECOVERABLE | hallucinate | `'Cryogenics'` | `'CKYOGENICS - 1 DAY ON'` | 0.369 |
| skill p03.r05 | `name` | UNRECOVERABLE | substitute | `'Coolness'` | `'COOLNESS -'` | 0.375 |
| skill p06.r08 | `name` | UNRECOVERABLE | hallucinate | `'Longblades'` | `'LONGLADIES ONLINE AND FOODS FOR FULL'` | 0.375 |

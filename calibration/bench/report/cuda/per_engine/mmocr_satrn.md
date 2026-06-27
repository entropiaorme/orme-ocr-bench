# `mmocr_satrn` deep dive

## Headline

- Effective accuracy: **41.9%** (138 PASS + 111 RECOVERED of 594 data cells)
- Failure modes: hallucinate=200, drop=2, substitute=254, reject=0
- Per-cell mean: **460.6 ms** (p95 463.7 ms, max 524.4 ms)
- Init: load 9320 ms + warmup 541 ms
- RSS: warmup 1038 MB, final 1045 MB
- Subprocess wall: **297.5 s**

## Confidence distribution

min=0.393  p25=0.681  median=0.796  p75=0.937  max=1.000  mean=0.794

## Per-cell-type effective accuracy

| Cell type | Eff acc | PASS+REC | Total |
| --- | --- | --- | --- |
| `name` | 47.6% | 6+111 | 246 |
| `level` | 24.3% | 35+0 | 144 |
| `rank_level` | 0.0% | 0+0 | 102 |
| `percent` | 95.1% | 97+0 | 102 |

## Failure samples (lowest 20 by confidence)

| Cell | Field | Status | Mode | Expected | OCR | Conf |
| --- | --- | --- | --- | --- | --- | --- |
| skill p11.r03 | `name` | UNRECOVERABLE | hallucinate | `'Stamina'` | `'Strike@cs.us.edu'` | 0.393 |
| skill p05.r10 | `level` | UNRECOVERABLE | hallucinate | `7` | `700` | 0.404 |
| skill p02.r03 | `name` | UNRECOVERABLE | substitute | `'Bioregenesis'` | `'Biorges@sunix.com'` | 0.440 |
| skill p09.r08 | `name` | RECOVERED | hallucinate | `'Pyrokinesis'` | `'Protess@cs.us.edu'` | 0.441 |
| skill p08.r09 | `name` | UNRECOVERABLE | hallucinate | `'Perception'` | `'Parasicko@sunix.com'` | 0.449 |
| skill p04.r07 | `name` | UNRECOVERABLE | substitute | `'Face Sculpting'` | `'Faess1phg@sund.com'` | 0.450 |
| skill p03.r05 | `name` | UNRECOVERABLE | hallucinate | `'Coolness'` | `'Colors@seet.hp.com'` | 0.451 |
| skill p12.r03 | `name` | UNRECOVERABLE | substitute | `'Treasure Sense'` | `'Theresons@sunix.com'` | 0.453 |
| skill p12.r05 | `name` | UNRECOVERABLE | substitute | `'Vehicle Technology'` | `'Viewstronometers/windows.'` | 0.457 |
| skill p10.r05 | `name` | UNRECOVERABLE | hallucinate | `'Scan Robot'` | `'Scarroloomers/state-state'` | 0.457 |
| skill p02.r02 | `level` | UNRECOVERABLE | hallucinate | `1` | `14` | 0.467 |
| skill p11.r08 | `name` | RECOVERED | hallucinate | `'Tailoring'` | `'Tabing@cs.us.edu'` | 0.473 |
| skill p04.r08 | `name` | UNRECOVERABLE | hallucinate | `'First Aid'` | `'Fistanderstormers'` | 0.476 |
| skill p05.r08 | `name` | UNRECOVERABLE | hallucinate | `'Gutting'` | `'sating@cs.us.edu'` | 0.479 |
| skill p10.r04 | `name` | UNRECOVERABLE | substitute | `'Scan Mutant'` | `'Sandbladers'` | 0.483 |
| skill p01.r09 | `name` | UNRECOVERABLE | substitute | `'Artefact Preservation'` | `'Anekard@massun.win.uc.edu'` | 0.486 |
| skill p05.r09 | `name` | UNRECOVERABLE | hallucinate | `'Hair Stylist'` | `'maists@state.mit.edu'` | 0.492 |
| profession p12.r03 | `name` | UNRECOVERABLE | hallucinate | `'Jammer'` | `'Jenner@state.com'` | 0.493 |
| skill p11.r00 | `name` | UNRECOVERABLE | substitute | `'Spacecraft Pilot'` | `'SpecstRomphetic'` | 0.494 |
| skill p11.r06 | `name` | UNRECOVERABLE | hallucinate | `'Surveying'` | `'Sunfing@cs.us.edu'` | 0.498 |

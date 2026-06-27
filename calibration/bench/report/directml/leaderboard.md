# OCR engine leaderboard

**Corpus:** 12 skill pages + 14 profession pages, 594 graded data cells (4 cell types: skill name + level; profession name + rank_level + percent). Ground truth produced via Frontier-VLM transcription with screen-verbatim canonical names where snapshot vocab disagrees.

**Scoring:** three-tier per cell — PASS (exact match after strip), RECOVERED (rapidfuzz top-1 against canonical vocab matches the expected canonical, name cells only), UNRECOVERABLE (neither). Numeric cells (level / rank_level / percent) collapse to PASS / UNRECOVERABLE; rapidfuzz isn't applicable to integers.

**Effective accuracy** = (PASS + RECOVERED) / total_data_cells. Non-data rows (`kind=summary` Average rows + `kind=empty` trailing blanks) are recorded by the engines but excluded from the denominator.

**Engines reported:** 13 of 28 candidates (others may be missing if their result JSON hasn't landed yet).

| Rank | Engine | Eff Acc | PASS | REC | FAIL | Total | Device | ms/cell | Preprocess ms | Model ms | Peak VRAM (MB) | Wall (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `openocr_svtrv2` | 100.0% | 550 | 44 | 0 | 594 | DirectML | 15.9 | 0.0 | 15.9 | — | 10.9 |
| 2 | `rapidocr` | 100.0% | 590 | 4 | 0 | 594 | CPU | 6.8 | 0.0 | 6.8 | — | 5.1 |
| 3 | `onnxtr_master` | 96.8% | 391 | 184 | 19 | 594 | DirectML | 431.5 | 0.0 | 433.6 | — | 298.2 |
| 4 | `onnxtr_sar` | 96.1% | 381 | 190 | 23 | 594 | DirectML | 92.3 | 0.0 | 92.9 | — | 63.0 |
| 5 | `onnxtr_viptr` | 95.8% | 469 | 100 | 25 | 594 | DirectML | 170.4 | 0.0 | 171.0 | — | 125.2 |
| 6 | `ppocrv5_mobile` | 95.6% | 541 | 27 | 26 | 594 | DirectML | 23.7 | — | — | — | 15.5 |
| 7 | `onnxtr_parseq` | 95.5% | 375 | 192 | 27 | 594 | DirectML | 150.0 | 0.0 | 150.5 | — | 100.3 |
| 8 | `onnxtr_crnn_mobile` | 94.6% | 366 | 196 | 32 | 594 | DirectML | 44.1 | 0.0 | 44.3 | — | 31.1 |
| 9 | `ppocrv5_latin_mobile` | 91.1% | 460 | 81 | 53 | 594 | DirectML | 22.5 | — | — | — | 14.7 |
| 10 | `ppocr` | 86.7% | 474 | 41 | 79 | 594 | DirectML | 22.6 | — | — | — | 14.8 |
| 11 | `ppocrv5_en_mobile` | 86.7% | 474 | 41 | 79 | 594 | DirectML | 22.6 | — | — | — | 14.7 |
| 12 | `onnxtr_vitstr` | 83.5% | 291 | 205 | 98 | 594 | DirectML | 37.5 | 0.0 | 37.5 | — | 27.0 |
| 13 | `ppocrv5_server` | 81.8% | 383 | 103 | 108 | 594 | DirectML | 31.4 | — | — | — | 20.4 |

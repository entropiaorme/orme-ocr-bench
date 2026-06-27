# OCR engine leaderboard

**Corpus:** 12 skill pages + 14 profession pages, 594 graded data cells (4 cell types: skill name + level; profession name + rank_level + percent). Ground truth produced via Frontier-VLM transcription with screen-verbatim canonical names where snapshot vocab disagrees.

**Scoring:** three-tier per cell — PASS (exact match after strip), RECOVERED (rapidfuzz top-1 against canonical vocab matches the expected canonical, name cells only), UNRECOVERABLE (neither). Numeric cells (level / rank_level / percent) collapse to PASS / UNRECOVERABLE; rapidfuzz isn't applicable to integers.

**Effective accuracy** = (PASS + RECOVERED) / total_data_cells. Non-data rows (`kind=summary` Average rows + `kind=empty` trailing blanks) are recorded by the engines but excluded from the denominator.

**Engines reported:** 18 of 28 candidates (others may be missing if their result JSON hasn't landed yet).

| Rank | Engine | Eff Acc | PASS | REC | FAIL | Total | Device | ms/cell | Preprocess ms | Model ms | Peak VRAM (MB) | Wall (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `openocr_svtrv2` | 100.0% | 550 | 44 | 0 | 594 | CPU | 12.9 | 0.0 | 12.8 | — | 8.9 |
| 2 | `rapidocr` | 100.0% | 590 | 4 | 0 | 594 | CPU | 8.9 | 0.0 | 8.8 | — | 6.5 |
| 3 | `onnxtr_master` | 96.8% | 391 | 184 | 19 | 594 | CPU | 619.1 | 0.0 | 610.7 | — | 411.2 |
| 4 | `onnxtr_sar` | 96.1% | 381 | 190 | 23 | 594 | CPU | 118.5 | 0.0 | 117.9 | — | 79.0 |
| 5 | `onnxtr_viptr` | 95.8% | 469 | 100 | 25 | 594 | CPU | 31.7 | 0.0 | 31.5 | — | 38.7 |
| 6 | `ppocrv5_mobile` | 95.6% | 541 | 27 | 26 | 594 | CPU | 46.3 | — | — | — | 29.3 |
| 7 | `onnxtr_parseq` | 95.5% | 375 | 192 | 27 | 594 | CPU | 67.7 | 0.0 | 67.3 | — | 48.5 |
| 8 | `onnxtr_crnn_mobile` | 94.6% | 366 | 196 | 32 | 594 | CPU | 10.4 | 0.0 | 10.3 | — | 9.9 |
| 9 | `ppocrv5_latin_mobile` | 91.1% | 460 | 81 | 53 | 594 | CPU | 42.7 | — | — | — | 27.0 |
| 10 | `ppocr` | 86.7% | 474 | 41 | 79 | 594 | CPU | 56.5 | — | — | — | 35.7 |
| 11 | `ppocrv5_en_mobile` | 86.7% | 474 | 41 | 79 | 594 | CPU | 42.6 | — | — | — | 27.0 |
| 12 | `mmocr_robustscanner` | 86.0% | 379 | 132 | 83 | 594 | CPU | 102.3 | — | — | — | 73.3 |
| 13 | `tesseract` | 84.0% | 491 | 8 | 95 | 594 | CPU | 632.4 | — | — | — | 396.3 |
| 14 | `onnxtr_vitstr` | 83.5% | 291 | 205 | 98 | 594 | CPU | 54.6 | 0.0 | 54.3 | — | 37.5 |
| 15 | `ppocrv5_server` | 81.8% | 383 | 103 | 108 | 594 | CPU | 114.8 | — | — | — | 72.2 |
| 16 | `easyocr` | 71.0% | 421 | 1 | 172 | 594 | CPU | 31.2 | — | — | — | 29.4 |
| 17 | `mmocr_satrn` | 41.9% | 138 | 111 | 345 | 594 | CPU | 593.4 | — | — | — | 380.4 |
| 18 | `mmocr_abinet` | 34.5% | 71 | 134 | 389 | 594 | CPU | 95.4 | — | — | — | 72.2 |

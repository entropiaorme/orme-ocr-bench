# OCR engine leaderboard

**Corpus:** 12 skill pages + 14 profession pages, 594 graded data cells (4 cell types: skill name + level; profession name + rank_level + percent). Ground truth produced via Frontier-VLM transcription with screen-verbatim canonical names where snapshot vocab disagrees.

**Scoring:** three-tier per cell — PASS (exact match after strip), RECOVERED (rapidfuzz top-1 against canonical vocab matches the expected canonical, name cells only), UNRECOVERABLE (neither). Numeric cells (level / rank_level / percent) collapse to PASS / UNRECOVERABLE; rapidfuzz isn't applicable to integers.

**Effective accuracy** = (PASS + RECOVERED) / total_data_cells. Non-data rows (`kind=summary` Average rows + `kind=empty` trailing blanks) are recorded by the engines but excluded from the denominator.

**Engines reported:** 13 of 28 candidates (others may be missing if their result JSON hasn't landed yet).

| Rank | Engine | Eff Acc | PASS | REC | FAIL | Total | Device | Mean ms/cell | Init load (ms) | RSS warm (MB) | Wall (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `openocr_svtrv2` | 100.0% | 550 | 44 | 0 | 594 | CPU | 16.0 | 361 | 145 | 10.7 |
| 2 | `rapidocr` | 100.0% | 590 | 4 | 0 | 594 | CPU | 9.6 | 555 | 105 | 7.2 |
| 3 | `onnxtr_viptr` | 95.8% | 469 | 100 | 25 | 594 | CPU | 689.4 | 54180 | 388 | 489.4 |
| 4 | `ppocrv5_mobile` | 95.6% | 541 | 27 | 26 | 594 | CPU | 73.9 | 368 | 99 | 46.6 |
| 5 | `onnxtr_parseq` | 95.5% | 375 | 192 | 27 | 594 | CPU | 191.4 | 7733 | 292 | 128.2 |
| 6 | `onnxtr_crnn_mobile` | 94.6% | 366 | 196 | 32 | 594 | CPU | 80.1 | 5233 | 234 | 56.2 |
| 7 | `ppocrv5_latin_mobile` | 91.1% | 460 | 81 | 53 | 594 | CPU | 50.6 | 202 | 87 | 32.1 |
| 8 | `ppocr` | 86.7% | 474 | 41 | 79 | 594 | CPU | 28.1 | 409 | 124 | 18.4 |
| 9 | `ppocrv5_en_mobile` | 86.7% | 474 | 41 | 79 | 594 | CPU | 51.6 | 179 | 86 | 32.6 |
| 10 | `tesseract` | 84.0% | 491 | 8 | 95 | 594 | CPU | 110.6 | 162 | 47 | 69.6 |
| 11 | `onnxtr_vitstr` | 83.5% | 291 | 205 | 98 | 594 | CPU | 234.6 | 36058 | 247 | 183.8 |
| 12 | `ppocrv5_server` | 81.8% | 383 | 103 | 108 | 594 | CPU | 186.2 | 1035 | 159 | 118.0 |
| 13 | `easyocr` | 71.0% | 421 | 1 | 172 | 594 | CPU | 47.3 | 12907 | 629 | 42.3 |

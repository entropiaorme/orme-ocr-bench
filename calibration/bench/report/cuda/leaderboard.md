# OCR engine leaderboard

**Corpus:** 12 skill pages + 14 profession pages, 594 graded data cells (4 cell types: skill name + level; profession name + rank_level + percent). Ground truth produced via Frontier-VLM transcription with screen-verbatim canonical names where snapshot vocab disagrees.

**Scoring:** three-tier per cell — PASS (exact match after strip), RECOVERED (rapidfuzz top-1 against canonical vocab matches the expected canonical, name cells only), UNRECOVERABLE (neither). Numeric cells (level / rank_level / percent) collapse to PASS / UNRECOVERABLE; rapidfuzz isn't applicable to integers.

**Effective accuracy** = (PASS + RECOVERED) / total_data_cells. Non-data rows (`kind=summary` Average rows + `kind=empty` trailing blanks) are recorded by the engines but excluded from the denominator.

**Engines reported:** 26 of 28 candidates (others may be missing if their result JSON hasn't landed yet).

| Rank | Engine | Eff Acc | PASS | REC | FAIL | Total | Device | ms/cell | Preprocess ms | Model ms | Peak VRAM (MB) | Wall (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `openocr_svtrv2` | 100.0% | 550 | 44 | 0 | 594 | CUDA | 56.9 | 0.0 | 56.9 | — | 36.8 |
| 2 | `rapidocr` | 100.0% | 581 | 13 | 0 | 594 | CUDA | 34.7 | 0.0 | 34.7 | — | 23.0 |
| 3 | `surya` | 100.0% | 594 | 0 | 0 | 594 | CUDA | 338.2 | 0.1 | 329.0 | 2801 | 224.8 |
| 4 | `onnxtr_master` | 96.8% | 391 | 184 | 19 | 594 | CUDA | 143.7 | 0.0 | 143.1 | — | 107.4 |
| 5 | `onnxtr_sar` | 96.1% | 381 | 190 | 23 | 594 | CUDA | 124.7 | 0.0 | 123.9 | — | 81.8 |
| 6 | `ppocrv5_mobile` | 96.0% | 542 | 28 | 24 | 594 | CUDA | 36.5 | — | — | — | 23.8 |
| 7 | `onnxtr_viptr` | 95.8% | 469 | 100 | 25 | 594 | CUDA | 73.6 | 0.0 | 73.3 | — | 61.5 |
| 8 | `onnxtr_parseq` | 95.5% | 375 | 192 | 27 | 594 | CUDA | 30.8 | 0.0 | 30.7 | — | 24.5 |
| 9 | `onnxtr_crnn_mobile` | 94.6% | 366 | 196 | 32 | 594 | CUDA | 58.8 | 0.0 | 58.3 | — | 39.8 |
| 10 | `ppocrv5_latin_mobile` | 91.4% | 460 | 83 | 51 | 594 | CUDA | 33.3 | — | — | — | 21.7 |
| 11 | `ppocr` | 86.7% | 473 | 42 | 79 | 594 | CUDA | 34.4 | — | — | 0 | 26.3 |
| 12 | `ppocrv5_en_mobile` | 86.7% | 473 | 42 | 79 | 594 | CUDA | 34.7 | — | — | — | 22.6 |
| 13 | `mmocr_robustscanner` | 86.0% | 379 | 132 | 83 | 594 | CPU | 113.9 | — | — | — | 80.2 |
| 14 | `onnxtr_vitstr` | 83.5% | 291 | 205 | 98 | 594 | CUDA | 15.3 | 0.0 | 15.2 | — | 13.0 |
| 15 | `ppocrv5_server` | 81.6% | 383 | 102 | 109 | 594 | CUDA | 93.8 | — | — | — | 60.2 |
| 16 | `easyocr` | 71.0% | 421 | 1 | 172 | 594 | CUDA | 17.3 | — | — | 130 | 27.8 |
| 17 | `florence2_large` | 65.0% | 295 | 91 | 208 | 594 | CUDA | 341.7 | 19.4 | 321.5 | 1801 | 231.3 |
| 18 | `trocr` | 56.7% | 323 | 14 | 257 | 594 | CUDA | 123.2 | 2.5 | 118.2 | 677 | 100.0 |
| 19 | `trocr_large_printed` | 55.4% | 309 | 20 | 265 | 594 | CUDA | 425.9 | 4.9 | 416.3 | 2371 | 285.5 |
| 20 | `got_ocr2` | 51.5% | 164 | 142 | 288 | 594 | CUDA | 8588.4 | — | — | — | 5394.7 |
| 21 | `florence2_base` | 46.0% | 219 | 54 | 321 | 594 | CUDA | 144.5 | 19.3 | 126.9 | 619 | 110.9 |
| 22 | `tesseract` | 42.4% | 250 | 2 | 342 | 594 | CPU | 83.7 | — | — | — | 52.8 |
| 23 | `mmocr_satrn` | 41.9% | 138 | 111 | 345 | 594 | CPU | 460.6 | — | — | — | 297.5 |
| 24 | `mmocr_abinet` | 34.5% | 71 | 134 | 389 | 594 | CPU | 72.8 | — | — | — | 55.8 |
| 25 | `nougat` | 7.1% | 6 | 36 | 552 | 594 | CUDA | 1234.2 | 63.7 | 1163.2 | 837 | 786.4 |
| 26 | `donut` | 0.0% | 0 | 0 | 594 | 594 | CUDA | 1013.6 | 471.5 | 539.7 | 1765 | 652.5 |

## Did not complete

Engines that ran on this host but could not finish (e.g. the model did not fit this GPU's memory). An honest non-result, recorded rather than omitted.

| Engine | Device | Stage | Reason |
| --- | --- | --- | --- |
| `dots_ocr` | cuda | load | OOM: OutOfMemoryError during load: CUDA out of memory. Tried to allocate 14.00 MiB. GPU 0 has a total capacity of 3.68 GiB of which 5.94 MiB is f |
| `kosmos25` | cuda | warmup | OOM: OutOfMemoryError during warmup: CUDA out of memory. Tried to allocate 768.00 MiB. GPU 0 has a total capacity of 3.68 GiB of which 17.94 MiB  |

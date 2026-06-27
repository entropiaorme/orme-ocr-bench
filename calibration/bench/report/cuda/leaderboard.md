# OCR engine leaderboard

**Corpus:** 12 skill pages + 14 profession pages, 594 graded data cells (4 cell types: skill name + level; profession name + rank_level + percent). Ground truth produced via Frontier-VLM transcription with screen-verbatim canonical names where snapshot vocab disagrees.

**Scoring:** three-tier per cell — PASS (exact match after strip), RECOVERED (rapidfuzz top-1 against canonical vocab matches the expected canonical, name cells only), UNRECOVERABLE (neither). Numeric cells (level / rank_level / percent) collapse to PASS / UNRECOVERABLE; rapidfuzz isn't applicable to integers.

**Effective accuracy** = (PASS + RECOVERED) / total_data_cells. Non-data rows (`kind=summary` Average rows + `kind=empty` trailing blanks) are recorded by the engines but excluded from the denominator.

**Engines reported:** 26 of 28 candidates (others may be missing if their result JSON hasn't landed yet).

| Rank | Engine | Eff Acc | PASS | REC | FAIL | Total | Device | Mean ms/cell | Init load (ms) | RSS warm (MB) | Wall (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `openocr_svtrv2` | 100.0% | 550 | 44 | 0 | 594 | CUDA | 55.8 | 947 | 908 | 36.4 |
| 2 | `rapidocr` | 100.0% | 581 | 13 | 0 | 594 | CUDA | 35.2 | 708 | 901 | 23.3 |
| 3 | `surya` | 100.0% | 594 | 0 | 0 | 594 | CUDA | 339.0 | 13112 | 1654 | 226.5 |
| 4 | `onnxtr_master` | 96.8% | 391 | 184 | 19 | 594 | CUDA | 145.1 | 18065 | 1115 | 109.0 |
| 5 | `onnxtr_sar` | 96.1% | 381 | 190 | 23 | 594 | CUDA | 124.9 | 3825 | 1085 | 82.0 |
| 6 | `ppocrv5_mobile` | 96.0% | 542 | 28 | 24 | 594 | CUDA | 36.4 | 413 | 881 | 23.8 |
| 7 | `onnxtr_viptr` | 95.8% | 469 | 100 | 25 | 594 | CUDA | 73.1 | 17602 | 1034 | 64.0 |
| 8 | `onnxtr_parseq` | 95.5% | 375 | 192 | 27 | 594 | CUDA | 31.1 | 4725 | 969 | 24.6 |
| 9 | `onnxtr_crnn_mobile` | 94.6% | 366 | 196 | 32 | 594 | CUDA | 59.1 | 2792 | 946 | 40.0 |
| 10 | `ppocrv5_latin_mobile` | 91.4% | 460 | 83 | 51 | 594 | CUDA | 34.6 | 387 | 848 | 22.6 |
| 11 | `ppocr` | 86.7% | 473 | 42 | 79 | 594 | CUDA | 35.0 | 424 | 944 | 23.0 |
| 12 | `ppocrv5_en_mobile` | 86.7% | 473 | 42 | 79 | 594 | CUDA | 34.9 | 378 | 848 | 22.8 |
| 13 | `mmocr_robustscanner` | 86.0% | 379 | 132 | 83 | 594 | CPU | 111.2 | 8931 | 767 | 78.8 |
| 14 | `onnxtr_vitstr` | 83.5% | 291 | 205 | 98 | 594 | CUDA | 15.5 | 8352 | 813 | 18.5 |
| 15 | `ppocrv5_server` | 81.6% | 383 | 102 | 109 | 594 | CUDA | 93.4 | 491 | 960 | 59.4 |
| 16 | `easyocr` | 71.0% | 421 | 1 | 172 | 594 | CUDA | 16.9 | 16922 | 1363 | 27.7 |
| 17 | `florence2_large` | 65.0% | 295 | 91 | 208 | 594 | CUDA | 342.9 | 17434 | 1775 | 232.2 |
| 18 | `trocr` | 56.7% | 323 | 14 | 257 | 594 | CUDA | 124.9 | 21477 | 2394 | 98.7 |
| 19 | `trocr_large_printed` | 55.4% | 309 | 20 | 265 | 594 | CUDA | 782.7 | 21505 | 1324 | 525.1 |
| 20 | `got_ocr2` | 51.5% | 164 | 142 | 288 | 594 | CUDA | 8588.4 | 24189 | 2530 | 5394.7 |
| 21 | `florence2_base` | 46.0% | 219 | 54 | 321 | 594 | CUDA | 144.7 | 19110 | 1735 | 111.7 |
| 22 | `tesseract` | 42.4% | 250 | 2 | 342 | 594 | CPU | 83.6 | 83 | 55 | 52.6 |
| 23 | `mmocr_satrn` | 41.9% | 138 | 111 | 345 | 594 | CPU | 454.5 | 9442 | 1034 | 293.7 |
| 24 | `mmocr_abinet` | 34.5% | 71 | 134 | 389 | 594 | CPU | 71.9 | 9533 | 813 | 54.8 |
| 25 | `nougat` | 7.1% | 6 | 36 | 552 | 594 | CUDA | 1228.1 | 19041 | 1711 | 784.2 |
| 26 | `donut` | 0.0% | 0 | 0 | 594 | 594 | CUDA | 1015.6 | 20004 | 1664 | 654.5 |

## Did not complete

Engines that ran on this host but could not finish (e.g. the model did not fit this GPU's memory). An honest non-result, recorded rather than omitted.

| Engine | Device | Stage | Reason |
| --- | --- | --- | --- |
| `dots_ocr` | cuda | load | OOM: OutOfMemoryError during load: CUDA out of memory. Tried to allocate 14.00 MiB. GPU 0 has a total capacity of 3.68 GiB of which 5.94 MiB is f |
| `kosmos25` | cuda | warmup | OOM: OutOfMemoryError during warmup: CUDA out of memory. Tried to allocate 768.00 MiB. GPU 0 has a total capacity of 3.68 GiB of which 17.94 MiB  |

# OCR engine leaderboard

**Corpus:** 12 skill pages + 14 profession pages, 594 graded data cells (4 cell types: skill name + level; profession name + rank_level + percent). Ground truth produced via Frontier-VLM transcription with screen-verbatim canonical names where snapshot vocab disagrees.

**Scoring:** three-tier per cell — PASS (exact match after strip), RECOVERED (rapidfuzz top-1 against canonical vocab matches the expected canonical, name cells only), UNRECOVERABLE (neither). Numeric cells (level / rank_level / percent) collapse to PASS / UNRECOVERABLE; rapidfuzz isn't applicable to integers.

**Effective accuracy** = (PASS + RECOVERED) / total_data_cells. Non-data rows (`kind=summary` Average rows + `kind=empty` trailing blanks) are recorded by the engines but excluded from the denominator.

**Engines reported:** 13 of 28 candidates (others may be missing if their result JSON hasn't landed yet).

| Rank | Engine | Eff Acc | PASS | REC | FAIL | Total | Device | Batch | Throughput (cells/s) | ms/cell (batched) | Peak VRAM (MB) | Wall (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `rapidocr` | 100.0% | 590 | 4 | 0 | 594 | CPU | 16 | 139.9 | 7.14 | — | 4.5 |
| 2 | `openocr_svtrv2` | 99.0% | 544 | 44 | 6 | 594 | DirectML | 16 | 286.3 | 3.48 | — | 2.2 |
| 3 | `onnxtr_master` | 96.8% | 391 | 184 | 19 | 594 | DirectML | 16 | 13.0 | 76.70 | — | 47.9 |
| 4 | `onnxtr_sar` | 96.1% | 381 | 190 | 23 | 594 | DirectML | 16 | 92.8 | 10.76 | — | 6.7 |
| 5 | `onnxtr_viptr` | 95.8% | 469 | 100 | 25 | 594 | DirectML | 16 | 58.9 | 16.95 | — | 10.6 |
| 6 | `ppocrv5_mobile` | 95.6% | 541 | 27 | 26 | 594 | DirectML | 16 | 147.4 | 6.77 | — | 4.2 |
| 7 | `onnxtr_parseq` | 95.5% | 375 | 192 | 27 | 594 | DirectML | 16 | 49.0 | 20.39 | — | 12.7 |
| 8 | `onnxtr_crnn_mobile` | 94.6% | 366 | 196 | 32 | 594 | DirectML | 16 | 188.7 | 5.29 | — | 3.3 |
| 9 | `ppocrv5_latin_mobile` | 91.1% | 460 | 81 | 53 | 594 | DirectML | 16 | 165.4 | 6.03 | — | 3.8 |
| 10 | `ppocr` | 86.7% | 474 | 41 | 79 | 594 | DirectML | 16 | 161.0 | 6.20 | — | 3.9 |
| 11 | `ppocrv5_en_mobile` | 86.7% | 474 | 41 | 79 | 594 | DirectML | 16 | 165.0 | 6.05 | — | 3.8 |
| 12 | `onnxtr_vitstr` | 83.5% | 291 | 205 | 98 | 594 | DirectML | 16 | 141.3 | 7.07 | — | 4.4 |
| 13 | `ppocrv5_server` | 81.8% | 383 | 103 | 108 | 594 | DirectML | 16 | 115.2 | 8.67 | — | 5.4 |

**Batched coverage.** Throughput is reported only for engines with a genuine batched path (no loop-over-serial fallback, which would fake throughput). Engines reported serial-only by design: the `trocr` family (a single-line / pre-cropped-region recogniser run at its intended batch-1 granularity, and already dominated on both accuracy and per-cell latency, so batched throughput would change no conclusion); `easyocr`/`tesseract` (no clean multi-image batch API); the MMOCR family (CPU-only on this host, where batching is not a throughput lever); and the wrong-fit VLMs `florence2`/`donut`/`nougat` (batching does not rescue a structurally mismatched, low- or zero-accuracy reader). `got_ocr2` IS batched: as an autoregressive OCR model its serial batch-1 is the pathological case, so batched is its representative regime. See EXPERIMENTS.md for the full per-engine decision record.

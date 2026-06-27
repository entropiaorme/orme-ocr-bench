# OCR engine leaderboard

**Corpus:** 12 skill pages + 14 profession pages, 594 graded data cells (4 cell types: skill name + level; profession name + rank_level + percent). Ground truth produced via Frontier-VLM transcription with screen-verbatim canonical names where snapshot vocab disagrees.

**Scoring:** three-tier per cell — PASS (exact match after strip), RECOVERED (rapidfuzz top-1 against canonical vocab matches the expected canonical, name cells only), UNRECOVERABLE (neither). Numeric cells (level / rank_level / percent) collapse to PASS / UNRECOVERABLE; rapidfuzz isn't applicable to integers.

**Effective accuracy** = (PASS + RECOVERED) / total_data_cells. Non-data rows (`kind=summary` Average rows + `kind=empty` trailing blanks) are recorded by the engines but excluded from the denominator.

**Engines reported:** 14 of 28 candidates (others may be missing if their result JSON hasn't landed yet).

| Rank | Engine | Eff Acc | PASS | REC | FAIL | Total | Device | Batch | Throughput (cells/s) | ms/cell (batched) | Peak VRAM (MB) | Wall (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `rapidocr` | 100.0% | 581 | 13 | 0 | 594 | CUDA | 16 | 107.6 | 9.28 | — | 5.8 |
| 2 | `surya` | 100.0% | 594 | 0 | 0 | 594 | CUDA | 16 | 7.9 | 126.87 | 3099 | 79.2 |
| 3 | `openocr_svtrv2` | 99.0% | 544 | 44 | 6 | 594 | CUDA | 16 | 263.9 | 3.77 | — | 2.4 |
| 4 | `onnxtr_master` | 96.8% | 391 | 184 | 19 | 594 | CUDA | 16 | 18.4 | 54.27 | — | 33.9 |
| 5 | `onnxtr_sar` | 96.1% | 381 | 190 | 23 | 594 | CUDA | 16 | 100.0 | 9.99 | — | 6.2 |
| 6 | `onnxtr_viptr` | 95.8% | 469 | 100 | 25 | 594 | CUDA | 16 | 204.3 | 4.88 | — | 3.1 |
| 7 | `ppocrv5_mobile` | 95.8% | 541 | 28 | 25 | 594 | CUDA | 16 | 105.1 | 9.50 | — | 5.9 |
| 8 | `onnxtr_parseq` | 95.5% | 375 | 192 | 27 | 594 | CUDA | 16 | 125.7 | 7.94 | — | 5.0 |
| 9 | `onnxtr_crnn_mobile` | 94.6% | 366 | 196 | 32 | 594 | CUDA | 16 | 302.1 | 3.29 | — | 2.1 |
| 10 | `ppocrv5_latin_mobile` | 91.2% | 460 | 82 | 52 | 594 | CUDA | 16 | 129.5 | 7.71 | — | 4.8 |
| 11 | `ppocrv5_en_mobile` | 86.7% | 474 | 41 | 79 | 594 | CUDA | 16 | 130.3 | 7.66 | — | 4.8 |
| 12 | `ppocr` | 86.5% | 473 | 41 | 80 | 594 | CUDA | 16 | 97.1 | 10.29 | 0 | 6.4 |
| 13 | `onnxtr_vitstr` | 83.5% | 291 | 205 | 98 | 594 | CUDA | 16 | 170.9 | 5.84 | — | 3.7 |
| 14 | `ppocrv5_server` | 82.0% | 383 | 104 | 107 | 594 | CUDA | 16 | 53.9 | 18.55 | — | 11.6 |

**Batched coverage.** Throughput is reported only for engines with a genuine batched path (no loop-over-serial fallback, which would fake throughput). Engines reported serial-only by design: the `trocr` family (a single-line / pre-cropped-region recogniser run at its intended batch-1 granularity, and already dominated on both accuracy and per-cell latency, so batched throughput would change no conclusion); `easyocr`/`tesseract` (no clean multi-image batch API); the MMOCR family (CPU-only on this host, where batching is not a throughput lever); and the wrong-fit VLMs `florence2`/`donut`/`nougat` (batching does not rescue a structurally mismatched, low- or zero-accuracy reader). `got_ocr2` IS batched: as an autoregressive OCR model its serial batch-1 is the pathological case, so batched is its representative regime. See EXPERIMENTS.md for the full per-engine decision record.

## Did not complete

Engines that ran on this host but could not finish (e.g. the model did not fit this GPU's memory). An honest non-result, recorded rather than omitted.

| Engine | Device | Stage | Reason |
| --- | --- | --- | --- |
| `got_ocr2` | cuda | batched_inference | OOM: OutOfMemoryError during batched inference (batch_size=16): CUDA out of memory. Tried to allocate 352.00 MiB. GPU 0 has a total capacity of 3 |

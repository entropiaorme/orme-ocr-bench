# Per-cell-type effective accuracy

Splits effective accuracy by cell type. Useful for spotting engines that win on names but lose on numerics (or vice versa) — a strong signal that ensembling could beat any single-engine pick.

| Engine | name | level | rank_level | percent | Notes |
| --- | --- | --- | --- | --- | --- |
| `openocr_svtrv2` | 100.0% | 100.0% | 100.0% | 100.0% | strongest: `name` (100.0%) · weakest: `name` (100.0%) |
| `rapidocr` | 100.0% | 100.0% | 100.0% | 100.0% | strongest: `name` (100.0%) · weakest: `name` (100.0%) |
| `surya` | 100.0% | 100.0% | 100.0% | 100.0% | strongest: `name` (100.0%) · weakest: `name` (100.0%) |
| `onnxtr_master` | 98.4% | 100.0% | 85.3% | 100.0% | strongest: `level` (100.0%) · weakest: `rank_level` (85.3%) |
| `onnxtr_sar` | 98.4% | 100.0% | 81.4% | 100.0% | strongest: `level` (100.0%) · weakest: `rank_level` (81.4%) |
| `ppocrv5_mobile` | 98.8% | 94.4% | 87.3% | 100.0% | strongest: `percent` (100.0%) · weakest: `rank_level` (87.3%) |
| `onnxtr_viptr` | 98.8% | 98.6% | 80.4% | 100.0% | strongest: `percent` (100.0%) · weakest: `rank_level` (80.4%) |
| `onnxtr_parseq` | 98.4% | 100.0% | 77.5% | 100.0% | strongest: `level` (100.0%) · weakest: `rank_level` (77.5%) |
| `onnxtr_crnn_mobile` | 98.4% | 100.0% | 72.5% | 100.0% | strongest: `level` (100.0%) · weakest: `rank_level` (72.5%) |
| `ppocrv5_latin_mobile` | 86.2% | 99.3% | 84.3% | 100.0% | strongest: `percent` (100.0%) · weakest: `rank_level` (84.3%) |
| `ppocr` | 84.1% | 95.1% | 67.6% | 100.0% | strongest: `percent` (100.0%) · weakest: `rank_level` (67.6%) |
| `ppocrv5_en_mobile` | 84.1% | 95.1% | 67.6% | 100.0% | strongest: `percent` (100.0%) · weakest: `rank_level` (67.6%) |
| `mmocr_robustscanner` | 80.1% | 81.2% | 94.1% | 99.0% | strongest: `percent` (99.0%) · weakest: `name` (80.1%) |
| `onnxtr_vitstr` | 96.7% | 100.0% | 62.7% | 49.0% | strongest: `level` (100.0%) · weakest: `percent` (49.0%) |
| `ppocrv5_server` | 63.0% | 99.3% | 86.3% | 97.1% | strongest: `level` (99.3%) · weakest: `name` (63.0%) |
| `easyocr` | 99.6% | 29.9% | 39.2% | 92.2% | strongest: `name` (99.6%) · weakest: `level` (29.9%) |
| `florence2_large` | 80.5% | 77.1% | 63.7% | 11.8% | strongest: `name` (80.5%) · weakest: `percent` (11.8%) |
| `trocr` | 18.7% | 100.0% | 44.1% | 100.0% | strongest: `level` (100.0%) · weakest: `name` (18.7%) |
| `trocr_large_printed` | 40.7% | 96.5% | 4.9% | 83.3% | strongest: `level` (96.5%) · weakest: `rank_level` (4.9%) |
| `got_ocr2` | 90.7% | 20.1% | 2.9% | 50.0% | strongest: `name` (90.7%) · weakest: `rank_level` (2.9%) |
| `florence2_base` | 35.4% | 79.2% | 12.7% | 57.8% | strongest: `level` (79.2%) · weakest: `rank_level` (12.7%) |
| `tesseract` | 49.2% | 25.0% | 61.8% | 31.4% | strongest: `rank_level` (61.8%) · weakest: `level` (25.0%) |
| `mmocr_satrn` | 47.6% | 24.3% | 0.0% | 95.1% | strongest: `percent` (95.1%) · weakest: `rank_level` (0.0%) |
| `mmocr_abinet` | 54.9% | 47.9% | 1.0% | 0.0% | strongest: `name` (54.9%) · weakest: `percent` (0.0%) |
| `nougat` | 17.1% | 0.0% | 0.0% | 0.0% | strongest: `name` (17.1%) · weakest: `level` (0.0%) |
| `donut` | 0.0% | 0.0% | 0.0% | 0.0% | strongest: `name` (0.0%) · weakest: `name` (0.0%) |

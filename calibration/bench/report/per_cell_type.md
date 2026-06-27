# Per-cell-type effective accuracy

Splits effective accuracy by cell type. Useful for spotting engines that win on names but lose on numerics (or vice versa) — a strong signal that ensembling could beat any single-engine pick.

| Engine | name | level | rank_level | percent | Notes |
| --- | --- | --- | --- | --- | --- |
| `openocr_svtrv2` | 100.0% | 100.0% | 100.0% | 100.0% | strongest: `name` (100.0%) · weakest: `name` (100.0%) |
| `rapidocr` | 100.0% | 100.0% | 100.0% | 100.0% | strongest: `name` (100.0%) · weakest: `name` (100.0%) |
| `onnxtr_viptr` | 98.8% | 98.6% | 80.4% | 100.0% | strongest: `percent` (100.0%) · weakest: `rank_level` (80.4%) |
| `ppocrv5_mobile` | 98.8% | 94.4% | 85.3% | 100.0% | strongest: `percent` (100.0%) · weakest: `rank_level` (85.3%) |
| `onnxtr_parseq` | 98.4% | 100.0% | 77.5% | 100.0% | strongest: `level` (100.0%) · weakest: `rank_level` (77.5%) |
| `onnxtr_crnn_mobile` | 98.4% | 100.0% | 72.5% | 100.0% | strongest: `level` (100.0%) · weakest: `rank_level` (72.5%) |
| `ppocrv5_latin_mobile` | 85.4% | 99.3% | 84.3% | 100.0% | strongest: `percent` (100.0%) · weakest: `rank_level` (84.3%) |
| `ppocr` | 83.7% | 95.1% | 68.6% | 100.0% | strongest: `percent` (100.0%) · weakest: `rank_level` (68.6%) |
| `ppocrv5_en_mobile` | 83.7% | 95.1% | 68.6% | 100.0% | strongest: `percent` (100.0%) · weakest: `rank_level` (68.6%) |
| `tesseract` | 100.0% | 38.9% | 100.0% | 93.1% | strongest: `name` (100.0%) · weakest: `level` (38.9%) |
| `onnxtr_vitstr` | 96.7% | 100.0% | 62.7% | 49.0% | strongest: `level` (100.0%) · weakest: `percent` (49.0%) |
| `ppocrv5_server` | 63.4% | 99.3% | 86.3% | 97.1% | strongest: `level` (99.3%) · weakest: `name` (63.4%) |
| `easyocr` | 99.6% | 29.9% | 39.2% | 92.2% | strongest: `name` (99.6%) · weakest: `level` (29.9%) |

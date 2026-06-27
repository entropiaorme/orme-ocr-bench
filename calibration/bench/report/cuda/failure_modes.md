# Failure-mode breakdown

Heuristic classification of non-PASS cells (UNRECOVERABLE only — RECOVERED is excluded since fuzzy already saved those):

- **Hallucinate**: OCR text materially longer than expected (insertion-heavy)
- **Drop**: OCR text materially shorter than expected (deletion-heavy)
- **Substitute**: similar length to expected, character mismatch
- **Reject**: OCR returned blank / whitespace

The classifier is length-based with a blank special-case; it's directional, not precise. Useful for attributing failure patterns to architectural causes (e.g. small-input hallucination on autoregressive decoders, drop on CRNN with insufficient receptive field).

| Engine | Hallucinate | Drop | Substitute | Reject | Total fail |
| --- | --- | --- | --- | --- | --- |
| `openocr_svtrv2` | 0 | 0 | 44 | 0 | 0 |
| `rapidocr` | 0 | 0 | 13 | 0 | 0 |
| `surya` | 0 | 0 | 0 | 0 | 0 |
| `onnxtr_master` | 33 | 0 | 170 | 0 | 19 |
| `onnxtr_sar` | 34 | 0 | 179 | 0 | 23 |
| `ppocrv5_mobile` | 9 | 0 | 43 | 0 | 24 |
| `onnxtr_viptr` | 0 | 0 | 125 | 0 | 25 |
| `onnxtr_parseq` | 33 | 0 | 186 | 0 | 27 |
| `onnxtr_crnn_mobile` | 29 | 0 | 199 | 0 | 32 |
| `ppocrv5_latin_mobile` | 5 | 36 | 92 | 1 | 51 |
| `ppocr` | 7 | 36 | 62 | 16 | 79 |
| `ppocrv5_en_mobile` | 7 | 36 | 62 | 16 | 79 |
| `mmocr_robustscanner` | 32 | 0 | 183 | 0 | 83 |
| `onnxtr_vitstr` | 33 | 0 | 270 | 0 | 98 |
| `ppocrv5_server` | 1 | 73 | 137 | 0 | 109 |
| `easyocr` | 0 | 1 | 69 | 103 | 172 |
| `florence2_large` | 0 | 100 | 199 | 0 | 208 |
| `trocr` | 122 | 0 | 149 | 0 | 257 |
| `trocr_large_printed` | 228 | 0 | 57 | 0 | 265 |
| `got_ocr2` | 428 | 0 | 2 | 0 | 288 |
| `florence2_base` | 0 | 106 | 269 | 0 | 321 |
| `tesseract` | 77 | 57 | 210 | 0 | 342 |
| `mmocr_satrn` | 200 | 2 | 254 | 0 | 345 |
| `mmocr_abinet` | 176 | 0 | 347 | 0 | 389 |
| `nougat` | 393 | 12 | 175 | 8 | 552 |
| `donut` | 0 | 0 | 0 | 594 | 594 |

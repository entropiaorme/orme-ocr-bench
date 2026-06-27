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
| `rapidocr` | 0 | 0 | 4 | 0 | 0 |
| `onnxtr_viptr` | 0 | 0 | 125 | 0 | 25 |
| `ppocrv5_mobile` | 9 | 0 | 44 | 0 | 26 |
| `onnxtr_parseq` | 33 | 0 | 186 | 0 | 27 |
| `onnxtr_crnn_mobile` | 29 | 0 | 199 | 0 | 32 |
| `ppocrv5_latin_mobile` | 5 | 35 | 93 | 1 | 53 |
| `ppocr` | 7 | 35 | 61 | 17 | 79 |
| `ppocrv5_en_mobile` | 7 | 35 | 61 | 17 | 79 |
| `tesseract` | 66 | 1 | 36 | 0 | 95 |
| `onnxtr_vitstr` | 33 | 0 | 270 | 0 | 98 |
| `ppocrv5_server` | 1 | 73 | 137 | 0 | 108 |
| `easyocr` | 0 | 1 | 69 | 103 | 172 |

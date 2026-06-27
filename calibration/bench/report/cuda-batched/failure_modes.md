# Failure-mode breakdown

Heuristic classification of non-PASS cells (UNRECOVERABLE only — RECOVERED is excluded since fuzzy already saved those):

- **Hallucinate**: OCR text materially longer than expected (insertion-heavy)
- **Drop**: OCR text materially shorter than expected (deletion-heavy)
- **Substitute**: similar length to expected, character mismatch
- **Reject**: OCR returned blank / whitespace

The classifier is length-based with a blank special-case; it's directional, not precise. Useful for attributing failure patterns to architectural causes (e.g. small-input hallucination on autoregressive decoders, drop on CRNN with insufficient receptive field).

| Engine | Hallucinate | Drop | Substitute | Reject | Total fail |
| --- | --- | --- | --- | --- | --- |
| `rapidocr` | 0 | 0 | 13 | 0 | 0 |
| `surya` | 0 | 0 | 0 | 0 | 0 |
| `openocr_svtrv2` | 0 | 0 | 50 | 0 | 6 |
| `onnxtr_master` | 33 | 0 | 170 | 0 | 19 |
| `onnxtr_sar` | 34 | 0 | 179 | 0 | 23 |
| `onnxtr_viptr` | 0 | 0 | 125 | 0 | 25 |
| `ppocrv5_mobile` | 8 | 0 | 45 | 0 | 25 |
| `onnxtr_parseq` | 33 | 0 | 186 | 0 | 27 |
| `onnxtr_crnn_mobile` | 29 | 0 | 199 | 0 | 32 |
| `ppocrv5_latin_mobile` | 5 | 36 | 92 | 1 | 52 |
| `ppocrv5_en_mobile` | 7 | 36 | 61 | 16 | 79 |
| `ppocr` | 7 | 35 | 62 | 17 | 80 |
| `onnxtr_vitstr` | 33 | 0 | 270 | 0 | 98 |
| `ppocrv5_server` | 1 | 73 | 137 | 0 | 107 |

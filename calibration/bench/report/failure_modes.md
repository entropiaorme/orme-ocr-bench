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

# orme-ocr-bench

A reproducible OCR bake-off for small, fixed-layout game-UI text. The task is
narrow and unforgiving: read short strings (skill names, profession names,
integer levels, percentages) out of tightly-cropped cells lifted from a game's
character panels, and get every one of them right. The corpus is 594 graded
cells captured from a real client; the ground truth is screen-verbatim.

This repo is the harness, the corpus, and the frozen results for a 28-engine
candidate sweep. It exists to answer one engineering question with receipts:
which recognition engine should ship in a panel-scanning tool, and what does
the accuracy actually look like once you account for a domain vocabulary you
can fuzzy-match against.

The short answer: **OpenOCR's SVTRv2-mobile recogniser**, which reaches **100%
effective accuracy** on the 594-cell corpus under the production post-process,
at **~12.9 ms/cell** on CPU. The long answer, with the full accuracy ladder
and the runners-up, is below.

## The accuracy ladder

Headline accuracy numbers for OCR are easy to misread, so this repo always
publishes the whole ladder. For the shipped engine (`openocr_svtrv2`) on the
594-cell corpus:

| Stage | Accuracy | What it measures |
| --- | --- | --- |
| Raw glyph-exact | **44.1%** (262 / 594) | byte-for-byte equality, no normalisation at all |
| Normalised-exact | **99.49%** (591 / 594) | strip + exact match after light cleanup |
| Effective | **100%** (594 / 594) | production normalise, then fuzzy-match against the canonical vocabulary |

Read this honestly. Raw OCR on these cells is hard: 44.1% glyph-exact is not a
shippable number on its own. The jump to 100% is not the model getting better;
it is the *system* getting better. Two things do the work:

1. **Production normalisation.** Unicode NFKC folding, case folding
   where the cell type allows it, and whitespace collapsing. Most of the raw
   failures are a fullwidth digit, a doubled space, or a trailing punctuation
   mark, not a wrong reading.
2. **Fuzzy match against a closed vocabulary.** Name cells (skill names,
   profession names) are drawn from a known, finite set. A `rapidfuzz` top-1
   match against the canonical vocabulary recovers near-misses like `Aglity`
   to `Agility`. Numeric cells (level, rank_level, percent) get no fuzzy
   recovery; integers either read correctly or they do not.

The "100% effective" number is therefore a property of *this engine plus this
post-process plus this vocabulary*, and it is always captioned as such. The
44.1% raw number is published right alongside it so nobody mistakes the
pipeline result for raw model accuracy.

See `calibration/bench/report/leaderboard.md` and the per-engine deep-dives
under `calibration/bench/report/per_engine/` for the underlying counts.

## Leaderboard

13 of the 28 candidate engines produced complete results on the capture host
(AMD RX 6750 XT / Windows 11, DirectML, no CUDA). Effective accuracy is scored
under the effective scoring (production normalise + fuzzy-vs-vocab) described
above; latency is this
harness's own per-cell Python wall time, measured on CPU.

| Rank | Engine | Eff acc | PASS | REC | FAIL | Mean ms/cell | Init load (ms) | RSS warm (MB) | Wall (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `openocr_svtrv2` | **100.0%** | 550 | 44 | 0 | 12.9 | 381 | 110 | 8.9 |
| 2 | `rapidocr` | 98.7% | 488 | 98 | 8 | 9.6 | 555 | 105 | 7.2 |
| 3 | `ppocrv5_mobile` | 95.6% | 515 | 53 | 26 | 73.9 | 368 | 99 | 46.6 |
| 4 | `onnxtr_viptr` | 95.6% | 376 | 192 | 26 | 689.4 | 54180 | 388 | 489.4 |
| 5 | `onnxtr_parseq` | 95.5% | 325 | 242 | 27 | 191.4 | 7733 | 292 | 128.2 |
| 6 | `onnxtr_crnn_mobile` | 94.6% | 320 | 242 | 32 | 80.1 | 5233 | 234 | 56.2 |
| 7 | `ppocrv5_latin_mobile` | 91.1% | 452 | 89 | 53 | 50.6 | 202 | 87 | 32.1 |
| 8 | `ppocr` | 86.7% | 470 | 45 | 79 | 28.1 | 409 | 124 | 18.4 |
| 9 | `ppocrv5_en_mobile` | 86.7% | 470 | 45 | 79 | 51.6 | 179 | 86 | 32.6 |
| 10 | `tesseract` | 84.0% | 490 | 9 | 95 | 110.6 | 162 | 47 | 69.6 |
| 11 | `onnxtr_vitstr` | 83.5% | 258 | 238 | 98 | 234.6 | 36058 | 247 | 183.8 |
| 12 | `ppocrv5_server` | 81.3% | 377 | 106 | 111 | 186.2 | 1035 | 159 | 118.0 |
| 13 | `easyocr` | 71.0% | 419 | 3 | 172 | 47.3 | 12907 | 629 | 42.3 |

Total graded cells per engine: 594. `PASS` = exact after strip; `REC` =
recovered by fuzzy match against the canonical vocabulary (name cells only);
`FAIL` = neither (594 - PASS - REC). Non-data rows (per-page Average summary
rows and trailing blank rows) are recorded but excluded from the denominator.

A note on the latency column: it is this Python harness's per-cell wall time,
nothing else. It is not a production inference benchmark and is not comparable
to numbers measured under a different runtime or harness. Treat it as a
relative cost signal across engines, not an absolute throughput claim.

## Engine roster: 28 candidates, 13 with results

The sweep covers 28 candidate engines across five architectural families:

- **PaddleOCR family:** `ppocr` (PP-OCRv4 baseline), `ppocrv5_mobile`,
  `ppocrv5_en_mobile`, `ppocrv5_latin_mobile`, `ppocrv5_server`, `rapidocr`.
- **OpenOCR / SVTRv2:** `openocr_svtrv2`, plus an upstream-PARSeq ablation.
- **OnnxTR (docTR recogniser zoo over ONNX Runtime):** `onnxtr_crnn_mobile`,
  `onnxtr_vitstr`, `onnxtr_viptr`, `onnxtr_parseq`, `onnxtr_sar`,
  `onnxtr_master`.
- **Classic baselines:** `easyocr`, `tesseract`.
- **MMOCR family:** `mmocr_abinet`, `mmocr_robustscanner`, `mmocr_satrn`.
- **Transformer-decoder / VLM tier:** `trocr` (base), `trocr_large_printed`,
  `donut`, `nougat`, `florence2_base`, `florence2_large`, `surya`,
  `got_ocr2`, `kosmos25`, `dots_ocr`.

**The original capture host** (AMD + Windows, DirectML, no CUDA) ran only 13
engines; the leaderboard above reflects that first pass. The fleet has since been
completed across two hosts (see the experiment split below): **Experiment A**
scored 26 of 28 on a Linux + NVIDIA box (`results/cuda/`), and **Experiment B**
added the in-domain Windows DirectML and CPU latency tracks (`results/directml/`,
`results/cpu-windows/`). Only `kosmos25` and `dots_ocr` remain open: they OOM a
4 GB card and need ~16 GB, recorded as honest non-results. The adapters for all
28 are present in the harness and reproduce per SETUP.md.

## Two experiments: unconstrained breadth vs in-domain

Accuracy is device-independent, but latency is not, and the engines do not
share one runtime: the ONNX recognisers reach a GPU through DirectML (the
shipped app's path) or CUDA, while the PyTorch VLMs only ever reach a GPU
through CUDA, and Tesseract has no GPU build at all. There is therefore no
single host on which every engine runs on its production device. Rather than
force one misleading uniform number, the sweep is reported as two experiments,
each with its own leaderboard and a per-row `Device` column.

- **Experiment A — unconstrained / research breadth** (`results/cuda/`,
  `report/cuda/`). "If each model ran in its most comfortable environment, how
  does the full 28-engine fleet compare?" Run on a Linux + NVIDIA host: every
  engine on CUDA except the ones that genuinely cannot (Tesseract and the MMOCR
  1.x stack run CPU; `kosmos25` and `dots_ocr` OOM a 4 GB card and are recorded
  as honest non-results). This is an upper-bound proxy, not what an end user
  sees.

- **Experiment B — in-domain / end-user-targeted** (`results/directml/`,
  `results/directml-batched/`, `results/cpu-windows/`, `results/cpu-windows-batched/`).
  "Given the product's actual constraints, which engines run, and how do they
  do?" Run on a Windows + AMD host (RX 6750 XT) on DirectML, matching the shipped
  app's provider path exactly, with serial and batched latency. Narrower than A
  (the CUDA-only PyTorch engines have no DirectML path), but these are the
  representative numbers.

The shipped app reaches the GPU through a DirectML -> CPU provider ladder, so the
CPU figures are the honest fallback (degraded-path) case, not a hypothetical:
Experiment B reports them (`results/cpu-windows/`) alongside the DirectML
numbers, including a batched pass that shows CPU batching helps some engines
substantially (the OnnxTR family) while being flat-to-negative for others (the
width-padded PP-OCRv5 CTC recognisers).

## What the sweep found

The architectural picture, drawn from the results and the per-engine
deep-dives:

- **Modern CTC + visual-transformer encoders win on game-UI text.** The
  SVTRv2 family (`openocr_svtrv2`) beats both pure-CRNN-via-ONNX (the PP-OCRv4
  baseline) and transformer-decoder generative OCR (`trocr`) on these crops.
  It is also the fastest accurate option by a wide margin (~12.9 ms/cell).
- **PARSeq is competitive on names but slower.** Permuted-AR with iterative
  refinement (`onnxtr_parseq`) reads names well but carries a much higher
  per-cell cost and a heavier init, so it loses on the cost/accuracy frontier.
- **The OnnxTR docTR checkpoints emit a trailing-dash artefact.** Several
  OnnxTR recognisers append a universal `Agility----` style trailing-dash run.
  It is a fixed, mechanical artefact: a bench-level `rstrip('-')` would lift
  the whole family into the high-90s. It is documented rather than silently
  patched, because the point of the bench is to show engines as they behave
  out of the box.
- **The VLM tier is structurally wrong-fit for cropped UI cells.** Generative
  vision-language models (Florence-2, GOT-OCR2, Kosmos-2.5, dots.ocr) are built
  for document-scale inputs. On single-line UI crops they hallucinate, emit
  bbox tags, repeat tokens, and run minutes-per-cell on CPU. They are in the
  roster for breadth and as a documented negative result, not as contenders.
- **There is real ensemble headroom.** Around 81 cells (13.6%) fail on exactly
  one engine and around 97 (16.3%) on exactly two. That distribution skews
  toward engine-specific failures rather than intrinsically hard cells, which
  is the signature of a corpus where a small ensemble (for example
  `openocr_svtrv2` + `rapidocr`) would mop up most of the remaining errors.

## Reproducing this

Full 28-engine end-to-end reproduction is not realistic for a reader, and this
repo does not pretend otherwise. The engines span multiple mutually-conflicting
dependency stacks (torch 2.0 through 2.11, transformers 4.49 through 5.8, mmcv
pins, several ONNX Runtime providers), multi-GB model weights, and GPU
requirements. Standing all of that up is a multi-day exercise. That is exactly
why the 27 non-shipped engines are published as **frozen result JSONs** under
`calibration/bench/results/` plus the rendered leaderboard and deep-dives under
`calibration/bench/report/`: the evidence travels with the repo so you do not
have to rebuild it.

What *is* runnable in one venv is the headline path: the shipped engine over
the shipped corpus.

```
# from the repo root, with the driver venv active (see SETUP.md):
python -m backend.ocr.calibration.bench.runner --engine openocr_svtrv2
```

That runs `openocr_svtrv2` (SVTRv2-mobile, Apache-2.0, ~24 MB ONNX) over the
594-cell corpus and reproduces the winning result. SETUP.md walks the driver
venv and the smoke bench; if `openocr_svtrv2` re-scores at 100% effective
accuracy, the wiring is good.

To regenerate the rendered report tables from whatever result JSONs are present:

```
python -m backend.ocr.calibration.bench.report
```

The committed report under `calibration/bench/report/` carries complete
per-engine deep-dives for all 13 engines with results. The aggregate files at
the top of that directory (`leaderboard.md`, `failure_modes.md`,
`per_cell_type.md`, `failure_overlap.md`) are `report.py` byproducts; the
committed snapshot of those aggregates was rendered from a single-engine
invocation, so re-run `report.py` on a host with the driver venv to regenerate
the full 13-engine aggregates from the committed result JSONs.

## Repo layout

- `backend/ocr/calibration/bench/` : the bench package (engine ABC, runner,
  scoring, capture, healthcheck, report) and one adapter per engine under
  `bench/engines/`.
- `backend/ocr/calibration/benchmark_panel_ocr.py` : the orchestrator that
  fans engines out to their per-engine venvs as subprocesses.
- `backend/ocr/calibration/{measure_panel_geometry,validate_panel_ocr,verify_panel_slices}.py`
  : geometry-calibration CLI, single-engine validation, slice probe.
- `backend/services/`, `backend/ocr/ppocr_rec_reader.py` : panel-region and
  window helpers plus the PP-OCR baseline reader. Live capture is Windows-only;
  on other platforms the bench-against-corpus path is the only one.
- `backend/data/panel_geometry.json` : calibrated grid. `backend/data/snapshot/`
  : the scoring vocabulary. `backend/assets/models/` : PP-OCR baseline weights.
- `calibration/bench/` : the corpus (`crops/`), `ground_truth.json`,
  `manifest.json`, the per-engine result JSONs (`results/`), the rendered
  report (`report/`), and the per-host config (`engine_venvs.json`).

## The corpus and ground truth

The corpus is 594 graded cells: 12 skill pages and 14 profession pages, four
cell types (skill name and level; profession name, rank_level, and percent).
The crops are public game content (skill and profession names) plus the
maintainer's own character progression numbers. They carry no avatar name,
account identifier, currency balance, chat, coordinates, or surrounding UI
chrome.

`calibration/bench/ground_truth.json` is screen-verbatim correct: it records
exactly what was on screen at capture, including any in-game spelling. The
scorer is calibrated against this exact text. Do not "correct" it. If a row
looks wrong, the OCR is wrong, not the ground truth. A genuine ground-truth
correction is a one-shot, reviewable change with a screenshot of the source
panel attached.

## Licences

This repository is licensed under Apache-2.0 (see `LICENSE`).

The engines themselves carry their own upstream licences, and a few are
research-only:

- **Shipped:** `openocr_svtrv2` (OpenOCR SVTRv2-mobile) is Apache-2.0, which is
  why it is the engine intended for downstream deployment.
- **Permissive:** the PaddleOCR / RapidOCR / OnnxTR families, EasyOCR,
  Tesseract, TrOCR, Donut, Florence-2, GOT-OCR2 (HF mirror), and Kosmos-2.5 are
  under permissive or standard open-source terms (Apache-2.0 / MIT / similar);
  check each upstream before redistribution.
- **Non-commercial / restricted:** `surya` (GPL-3.0 code + CC-BY-NC weights),
  `nougat` (CC-BY-NC-4.0), and `dots_ocr` (bespoke licence agreement) are
  benched for research breadth only and are not shippable in a commercial
  product. Their adapters tag the licence in the docstring.

Model weights are downloaded from their upstream sources (HuggingFace,
ModelScope) on first run; this repo vendors only the small PP-OCR baseline ONNX
under `backend/assets/models/`.

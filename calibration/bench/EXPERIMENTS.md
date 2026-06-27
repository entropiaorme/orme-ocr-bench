# Experiment matrix and run checklist

This is the master plan for the bench's experiments: what to measure, on which
machine, and why. It exists so runs have defined roles rather than being fired
aimlessly, and so the Windows phase can be handed to a fresh agent with full
context.

## The two independent questions

1. **Accuracy** — `(model, weights, pre/postprocessing)`. Device- and
   host-independent (a matmul gives the same logits on CPU/CUDA/DirectML).
   **Measured once, on the full 594-cell corpus. Already done** (Experiment A,
   `report/cuda/`). Verified against the legacy AMD/Windows bench; matches.
   Documented exception: `tesseract` is not one model — its binary/tessdata/PSM
   differ by platform, so its accuracy is host-dependent (42% Linux vs 84% the
   Windows build). Treat tesseract accuracy as host-tagged, not invariant.

2. **Latency / throughput** — `(model, device, runtime, batching, host,
   preprocessing)`. Invariant to nothing; this is the entire reason for the
   multiple environment runs.

The article reports these as separate tables: one host-agnostic **accuracy**
table, one parameterised **latency** table, plus a **coverage** matrix (which
engine ran where).

## Engine capability map (data-backed, from Experiment A)

| Engine group | CPU | CUDA (Linux) | DirectML (Win) |
| --- | --- | --- | --- |
| ONNX recognisers: openocr_svtrv2, onnxtr ×6, ppocr, ppocrv5 ×4 | yes (ran) | yes (ran) | yes (ran) |
| rapidocr (rapidocr-onnxruntime) | yes (ran) | yes (ran) | no: the pinned library's provider list is CUDA-or-CPU only (no DirectML), so on Windows it runs CPU |
| easyocr (torch) | yes | yes (ran) | no (torch has no DirectML) |
| tesseract | yes (only) | never | never |
| mmocr_abinet/robustscanner/satrn (torch 2.0 stack) | yes (ran CPU) | needs torch-2.0 CUDA wheel (absent on this host) | no |
| VLM tier: trocr, trocr_large_printed, donut, nougat, florence2_base/large, surya, got_ocr2 | possible but impractical (minutes/cell) | yes (ran) | no |
| kosmos25, dots_ocr | CPU only (huge) | OOM on 4 GB (need >=16 GB) | no |

### N/A rules for the latency table
- **CPU column = N/A for the VLM tier** by design. Their accuracy is the
  upper-bound data point; GPU is their only realistic runtime. Report
  "CPU n/a (impractical)", not a number.
- **DirectML column = N/A for the entire torch tier** (easyocr, mmocr, all
  VLMs): no DirectML path. On Windows these are CPU-only. This is why
  Experiment B is intentionally narrower than A.
- **GPU column = N/A for tesseract** (no GPU build, any host).
- **DirectML N/A for rapidocr** specifically (separate from the rest of the ONNX
  group): `rapidocr-onnxruntime` only ever offers a CUDA-or-CPU provider list, so
  on the Windows/DirectML host it falls back to CPU. Its `directml` row therefore
  records `device=cpu` honestly rather than a DirectML number.
- **CUDA N/A on this 4 GB card** for kosmos25/dots_ocr (OOM — hardware, not
  principle). Recorded as "did not complete (OOM)".

### Forcing CPU on a GPU host (how the CPU latency track is produced)
The CPU latency cells run from the *same* `onnxruntime-directml` / `onnxruntime-gpu`
venvs as the GPU cells (those wheels carry the CPU provider too); setting
`OCR_BENCH_DEVICE=cpu` pins every ONNX adapter to `CPUExecutionProvider`. This
avoids building a parallel set of CPU-only venvs and guarantees the only variable
between the GPU and CPU tracks is the provider. The knob is honoured by all five
ONNX provider-selection sites (`_ort_cuda.force_cpu` + the openocr, onnxtr, ppocr
reader, ppocrv5, and rapidocr adapters); torch engines (mmocr) are CPU here
regardless.

## Latency modes (both are real app use-cases)

- **serial (batch-1)** — opportunistic single-element OCR, e.g. the in-game
  armour **repair-cost** read. Metric: single-cell round-trip ms.
- **batched(N)** — read a whole panel at once, e.g. the **skill-stats scan**.
  Metric: throughput (cells/sec) at a realistic batch size.

Adapters were one-crop-at-a-time; a `read_batch` capability was added (true
batched path only, no loop-fallback) for the engines decided below.

### Finding: variable-width CTC batching must be width-bucketed

The PP-OCR / PP-OCRv5 recognisers take a fixed-height, variable-width tensor.
Naive batching (pad every crop to the batch's max width) **perturbs accuracy**:
padding a narrow crop (e.g. a 2-digit level) out to a long skill-name's width
leaks spurious characters into the read, because the conv receptive field sees
the padded tail. Measured impact on ppocrv5_mobile: naive max-width pad with
-1.0 gave 52% (vs 96% serial); with 0.0 it over-read to 98.5%; neither matched
serial. The fix (PP-OCR's own reference practice) is **width-bucketing**: sort
crops by width and pad only within similar-width groups (we cut a bucket at a
>10% width jump), so intra-bucket padding is minimal. Bucketed batched then
tracks serial to within one cell (95.8% vs 96.0%). This is itself a reportable
methodology point: "batched throughput for variable-width CTC is only
apples-to-apples if you width-bucket; otherwise batching changes the reads."
Batch-of-1 always equals serial exactly (no per-call nondeterminism).

## Which engines get a batched measurement, and why (decision record)

The per-engine call was made with two heuristics, applied jointly:

- **A — author-intent / strawman:** if the model's creator saw it benchmarked
  with no batched run, would they feel it was run in an unintended way
  (strawmanned), or is batched throughput simply not central to the model's
  identity, making serial-only a fair representation?
- **B — peer-review / hiring-signal:** would a senior ML engineer reading this
  as a work sample rate skipping (or pursuing) batching for this engine as good
  judgement, or as a competence gap / wasted effort?

These decisions were cross-checked by an independent reviewer (a separate agent
given only neutral, matter-of-fact model descriptions and the two heuristics,
with no hint of our own conclusion or any implementation-difficulty framing). It
reached the same conclusions via the same use-case-granularity tie-breaker; its
sourced write-up is summarised inline below.

### Batched (true `read_batch` implemented)
- **openocr_svtrv2** (shipped CTC engine), **rapidocr, ppocr, ppocrv5 ×4**
  (PP-OCR family, built for batched server inference — the "server" variant is
  literally named for throughput), **onnxtr ×6** (docTR/ONNX, page-batched by
  design; predictor natively takes a list), **surya** (batch-by-design list API,
  and it is the accuracy ceiling so its throughput is genuinely interesting).
  For all of these, batching is the point of the model/library; A and B agree.
- **got_ocr2** — an autoregressive document/OCR VLM whose canonical
  high-throughput deployment IS batching (vLLM-style continuous batching;
  throughput scales ~linearly with batch for AR decoders). Serial batch-1
  (~8.6 s/cell here) is its *pathological* worst case, so serial-only would be
  the single most criticisable omission. Heuristic A dominates (severe,
  architecture-specific strawman risk); B agrees (skipping it would read as not
  understanding the architecture).

### Serial-only (batched = n/a, by decision not by inability)
- **trocr, trocr_large_printed** — although also autoregressive, TrOCR is a
  **single-line / pre-cropped-region recogniser**, and our task (one cropped UI
  cell at a time) IS its intended granularity. Its papers benchmark accuracy,
  not throughput-at-scale; it is not sold as a throughput engine the way
  GOT-OCR2-via-vLLM is. So batch-1 represents it faithfully (Heuristic A leans
  serial-only). It also already loses on BOTH accuracy (55-57% vs 85-100% for
  the lightweight recognisers) and per-cell latency, so a batched number would
  change no conclusion. The GOT-vs-TrOCR asymmetry is principled, not a double
  standard: **match the measurement to the model's intended granularity** —
  GOT is a page/document VLM (batch-native), TrOCR is a per-crop line recogniser
  (batch-1-native). For the write-up, state this explicitly so the asymmetry
  reads as judgement, not omission.
- **easyocr** — a baseline whose high-level API (`readtext`) is per-image; it
  has no clean multi-image batch path (its `batch_size` batches detection boxes
  *within* one image, not multiple images). A looped "batch" would be fake
  throughput, so serial-only is the honest call for a baseline.
- **tesseract** — no native tensor-batch path exists (per-image CLI/library).
  Serial-only is faithful to what Tesseract is, not a strawman.
- **mmocr ×3** — batch-capable in principle, but on this host they run **CPU**
  only (torch-2.0 stack, no CUDA wheel). Batching's throughput win is a GPU
  phenomenon (kernel-launch amortisation); CPU batching is not a meaningful
  throughput lever, and a CPU "batched" column would imply a GPU-style win that
  isn't there. Batch them only if they are ever run on a CUDA host.
- **florence2_base, florence2_large** — general-purpose VLMs (OCR is one of many
  prompted tasks), structurally wrong-fit on tiny cells, mid accuracy (46-65%).
  Batched throughput rescues neither the fit nor the accuracy; the
  preprocess/model timer split (implemented) is the more insightful
  instrumentation for them. Heuristic B: completeness-for-its-own-sake, not
  insight.
- **donut, nougat** — explicit wrong-domain controls that scored ~0% / 7%.
  Batching a model that reads nothing correctly informs no decision and misreads
  the experiment's purpose (their value is the accuracy floor + failure shape).
- **kosmos25, dots_ocr** — OOM on the 4 GB card; no result at all, so batching
  (which needs *more* memory) is moot here. Defer to a >=16 GB GPU.

## Instrumentation (do once, before any latency run)

- Split the per-cell timer into **preprocess_ms** vs **model_ms** so the table
  separates "this adapter upscales 4x" from "this model is slow". Without it,
  ms/cell conflates the two and strawmans engines with heavy preprocessing.
- Capture **peak VRAM** (`torch.cuda.max_memory_allocated`) for GPU engines —
  host RSS does not include VRAM, and VRAM is what explains the OOM cliff.
- Add **batched** measurement path (`read_batch` + a throughput metric).

## The run checklist (cells = environment x mode)

Accuracy: DONE (full corpus, once). Below are latency/throughput cells only.

### This machine — Linux + NVIDIA RTX A1000 (4 GB). GPU-only cells. DONE.
- [x] **I. Instrumentation code** — preprocess/model split, peak-VRAM, batched
      path, width-bucketed CTC batching. Committed.
- [x] **II. CUDA-serial (instrumented)** — all 26 runnable engines in
      `results/cuda/` with split/VRAM columns populated (got_ocr2 kept its prior
      serial result, deferred re-run below). kosmos25/dots_ocr recorded OOM.
      Committed.
- [x] **III. CUDA-batched** — the 12 batch-capable engines at batch 16 in
      `results/cuda-batched/`. got_ocr2 OOMs at batch-16 (fits serial, not
      batched) — recorded as did-not-complete. Committed.
- Rationale: these are the cells ONLY this NVIDIA box can produce. CPU latency
  is deliberately deferred to Windows (stronger CPU there).
- **Linux session cutoff reached** — see HANDOVER.md (workspace root) for the
  Windows-phase brief.

**Deferred to async / Windows-side fresh agent:**
- **got_ocr2 serial re-run** — skipped in II to not block the handover (~90 min
  for only a peak-VRAM number; its 8.6 s/cell serial latency is already recorded
  and it has no preprocess/model split mark). Fill its `peak_vram_mb` later with:
  `SKIP=0 calibration/bench/run_tier.sh --engines got_ocr2`. It DOES get its
  batched run in III (where it is the interesting case).

### Windows machine — AMD RX 6750 XT, DirectML. CPU + DirectML cells. DONE.
Host: Windows 11, AMD RX 6750 XT, `onnxruntime-directml` 1.24. All four cells
were measured on an otherwise-idle machine (no concurrent builds/agents) so the
latency figures are not contended.
- [x] **IV. DirectML-serial** — ONNX group + openocr in `results/directml/`.
      12 engines on `DmlExecutionProvider`; rapidocr falls back to CPU (no DML
      path in its library). Accuracy matches the device-invariant CUDA track
      exactly, as expected.
- [x] **V. DirectML-batched** — same group at batch 16 in
      `results/directml-batched/`. openocr_svtrv2 hits ~225 cells/s.
- [x] **VI. Windows-CPU-serial** — ONNX group (pinned CPU via
      `OCR_BENCH_DEVICE=cpu`) + tesseract + mmocr ×3 in `results/cpu-windows/`.
      All 17 verified `device=cpu`. tesseract reads 84.0% here (vs 42% on Linux)
      — the documented host-tagged tesseract behaviour.
- [x] **VII. Windows-CPU-batched** — full ONNX group at batch 16 in
      `results/cpu-windows-batched/`. Run for all batch-capable engines (not a
      sample) so the column needs no per-engine subset justification.

#### Finding: CPU batching is engine-dependent, not a flat null
The prior expectation was "batching is a GPU phenomenon, so CPU batched ≈ CPU
serial." The data is more nuanced (CPU serial vs batched ms/cell, batch 16):
- **OnnxTR family wins substantially** (1.85×–5.4×: crnn_mobile 10.4→1.9,
  viptr 31.7→9.1, parseq/sar/vitstr/master ~1.9–2.1×). These docTR predictors
  carry heavy per-call Python/pre-post overhead, which batching amortises — a
  real CPU lever, not just a GPU one.
- **Classic CTC engines: modest** (openocr 1.15×, ppocr 1.25×, rapidocr 1.27×).
- **PP-OCRv5 family: flat to marginally slower** (0.94×–0.99×). The width-
  bucketed CTC path pads each crop to its bucket max; on a compute-bound CPU that
  padding is wasted work that roughly cancels the batching benefit. (Note: an
  earlier draft mis-reported a ~2× ppocrv5 *slowdown*; that was an artefact of a
  contaminated serial baseline — see the provider-knob note below — the clean
  figure is ~flat.)

#### Repro fixes made during the Windows phase
- **Force-CPU knob** added (`OCR_BENCH_DEVICE=cpu`, `_ort_cuda.force_cpu`) and
  wired into all five ONNX provider-selection sites. The fifth site
  (`_PPocrV5Reader._select_providers`, shared by the four ppocrv5 adapters) was
  initially missed, so the first CPU-serial run recorded the four ppocrv5
  engines on DirectML. Fixed and re-run; both CPU tracks are now uniformly CPU.
- **UTF-8 stdout in the orchestrator**: engine misreads can contain non-cp1252
  glyphs; on Windows the orchestrator's redirected stdout defaulted to cp1252 and
  raised `UnicodeEncodeError` while printing failures, aborting before the
  composite summary was written. `main()` now reconfigures stdout/stderr to UTF-8
  (errors="replace") so every run completes and persists its summary.

## Machine cutoff

The Linux box owns I, II, III (done). The Windows box owns IV-VII (done).
Accuracy needs no further runs anywhere; it is device-invariant and already
measured on the full corpus.

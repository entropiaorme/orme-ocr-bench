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
| ONNX recognisers: openocr_svtrv2, onnxtr ×6, ppocr, ppocrv5 ×4, rapidocr | yes | yes (ran) | yes |
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
- **CUDA N/A on this 4 GB card** for kosmos25/dots_ocr (OOM — hardware, not
  principle). Recorded as "did not complete (OOM)".

## Latency modes (both are real app use-cases)

- **serial (batch-1)** — opportunistic single-element OCR, e.g. the in-game
  armour **repair-cost** read. Metric: single-cell round-trip ms.
- **batched(N)** — read a whole panel at once, e.g. the **skill-stats scan**.
  Metric: throughput (cells/sec) at a realistic batch size.

Adapters were one-crop-at-a-time; a `read_batch` capability was added (true
batched path only, no loop-fallback) for the engines decided below.

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

### This machine — Linux + NVIDIA RTX A1000 (4 GB). GPU-only cells.
- [ ] **I. Instrumentation code** — preprocess/model split, peak-VRAM, batched path.
- [ ] **II. CUDA-serial** — re-run the 22 CUDA-capable engines instrumented
      (`--results-subdir cuda`, overwriting A's uninstrumented latency; accuracy
      unchanged). kosmos25/dots_ocr stay OOM.
- [ ] **III. CUDA-batched** — batched throughput for all GPU-capable engines
      (`--results-subdir cuda-batched` or a batched flag).
- Rationale: these are the cells ONLY this NVIDIA box can produce. CPU latency
  is deliberately deferred to Windows (stronger CPU there).

### Windows machine — later, by a Windows agent. CPU + DirectML cells.
- [ ] **IV. DirectML-serial** — ONNX recognisers (`--results-subdir directml`).
      The torch tier is N/A (no DirectML); only the ONNX group + openocr.
- [ ] **V. DirectML-batched** — batched throughput, same ONNX group.
- [ ] **VI. Windows-CPU-serial** — CPU latency for the CPU-relevant engines
      (ONNX recognisers, tesseract, mmocr). VLM tier = N/A by design.
- [ ] **VII. Windows-CPU-batched** — optional; batched CPU throughput for the
      shortlist if useful.
- The Windows agent owns CPU instrumentation specifics and any Windows-only
  implementation, iterating on the target environment.

## Machine cutoff

This session is DONE on the Linux box once I, II, III are committed. Everything
CPU/DirectML/Windows-specific (IV-VII) is the Windows phase. Accuracy needs no
further runs anywhere.

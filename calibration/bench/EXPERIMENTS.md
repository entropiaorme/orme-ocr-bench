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

Adapters are currently one-crop-at-a-time; batched throughput needs a
`read_batch` capability added (for all GPU-capable engines, per decision).

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

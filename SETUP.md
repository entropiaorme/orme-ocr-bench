# Fresh-host bring-up

This walks a human (or an agent) through standing the bench up on a host that
has only the cloned repo. Order matters: get the driver venv healthy first, run
the headline engine to confirm wiring, then add per-engine venvs as you decide
which engines to run.

The bench is incremental. Each engine runs in its own virtualenv, mapped in
`calibration/bench/engine_venvs.json`. Any engine whose mapped interpreter is
missing is skipped cleanly and the orchestrator continues on the rest, so you
only need to build the venvs for the engines you actually want to run.

## 0. Prereqs

- Python 3.11+ (3.12 / 3.13 are fine for most engines).
- Git.
- Disk: budget ~30 GB for the per-engine venvs plus the HuggingFace cache if you
  intend to run the heavier transformer / VLM engines. The lightweight engines
  (the headline path, PaddleOCR, OnnxTR) need far less.
- Platform / GPU:
  - **Windows + AMD/Intel GPU:** DirectML works via `onnxruntime-directml`.
  - **Linux + NVIDIA:** CUDA works via `onnxruntime-gpu` and the standard
    PyTorch CUDA wheels. This is the recommended path for completing the 15
    pending engines (see the last section).
  - **macOS / Linux + AMD:** mostly CPU; ROCm support varies. CPU runs are
    recorded with their wall time and counted as valid.

Verify your GPU posture before assuming you have it:

```
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.device_count())"
python -c "import onnxruntime; print(onnxruntime.get_available_providers())"
```

## 1. Clone

```
git clone https://github.com/entropiaorme/orme-ocr-bench.git
cd orme-ocr-bench
```

## 2. Driver venv

The driver venv carries the orchestrator, the scorer, and the capture deps. It
is also the fallback interpreter for any engine not mapped in
`engine_venvs.json` (or whose mapped interpreter cannot be found). The four
lightweight baselines (`ppocr`, `tesseract`, `easyocr`, `trocr`) are happy to
run straight from here.

```
# Windows (PowerShell):
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-driver.txt

# POSIX (bash / zsh):
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-driver.txt
```

Edit `requirements-driver.txt` first to uncomment the right `onnxruntime`
provider line for your host (CPU is the default; DirectML for AMD/Intel on
Windows; `onnxruntime-gpu` for NVIDIA).

### NVIDIA: supplying the CUDA runtime to ONNX Runtime

`onnxruntime-gpu` does not bundle the CUDA runtime libraries; it expects to
find them on the loader path. A host with only the NVIDIA *driver* installed
(no system CUDA toolkit) does not have them, so an unpinned
`onnxruntime-gpu` (which resolves to a build expecting the very latest CUDA)
fails to import with `ImportError: libcudart.so.<N>` and the ORT-based
engines silently fall back to CPU.

The self-contained fix needs no system CUDA and no `sudo`: pin a CUDA-12
`onnxruntime-gpu` build (1.21+ ships `preload_dlls()`) and let the
`nvidia-*-cu12` pip wheels carry the runtime inside the venv. The bench calls
`onnxruntime.preload_dlls()` before its first session, so no `LD_LIBRARY_PATH`
export is required. In the venv that runs ORT-based engines on GPU:

```
python -m pip install "onnxruntime-gpu==1.22.0" \
  nvidia-cuda-runtime-cu12 nvidia-cudnn-cu12 nvidia-cublas-cu12 \
  nvidia-curand-cu12 nvidia-cufft-cu12 nvidia-cuda-nvrtc-cu12
```

Confirm CUDA is actually engaged (a clean shell, no `LD_LIBRARY_PATH`):

```
python -c "import onnxruntime as o; o.preload_dlls(); print(o.get_available_providers())"
# -> [..., 'CUDAExecutionProvider', 'CPUExecutionProvider']
```

If a package (for example `openocr-python`) pulls in the CPU `onnxruntime`
wheel as a dependency, *replace* it with `onnxruntime-gpu` rather than
installing both: the two share the `onnxruntime` import namespace and having
both present is fragile (uninstalling one can break the other). Force-reinstall
the GPU wheel if you hit this: `pip install --force-reinstall --no-deps
"onnxruntime-gpu==1.22.0"`.

`tesseract` additionally needs the Tesseract binary on `PATH` (`apt install
tesseract-ocr`, `brew install tesseract`, or the UB-Mannheim Windows installer)
plus `pytesseract` in whichever venv runs it.

## 3. Adjust `engine_venvs.json`

Open `calibration/bench/engine_venvs.json`. Two host-specific edits:

1. **Interpreter paths.** The stock paths use `Scripts/python.exe` (Windows).
   On POSIX hosts replace `Scripts/python.exe` with `bin/python` for every entry
   under `engines:`. One sed pass does it.
2. **HuggingFace cache redirect.** `global_env.HF_HOME` is a placeholder
   (`/path/to/huggingface-cache`). Point it at a host-local path with headroom,
   or delete the entry to let HuggingFace use its default
   (`~/.cache/huggingface`). This only matters for the transformer / VLM
   engines that pull weights from the hub.

Engines whose mapped interpreter does not exist are skipped gracefully, so you
can bring venvs online one at a time.

## 4. Per-engine venvs

Each venv below is referenced by `engine_venvs.json`. Create the venv, activate
it (as in step 2), upgrade pip, then install. Every venv also needs the bench's
own light deps (`numpy opencv-python rapidfuzz psutil`) so the runner can score
and report from inside the subprocess.

Replace `.venv-N/bin/python` with `.venv-N\Scripts\python.exe` on Windows.

### `.venv-1` : PaddleOCR PP-OCRv5 family + RapidOCR

Engines: `ppocrv5_mobile`, `ppocrv5_en_mobile`, `ppocrv5_latin_mobile`,
`ppocrv5_server`, `rapidocr`.

```
python -m venv .venv-1
.venv-1/bin/python -m pip install --upgrade pip
.venv-1/bin/python -m pip install numpy opencv-python rapidfuzz psutil
.venv-1/bin/python -m pip install rapidocr-onnxruntime
# ONNX Runtime provider (pick per host):
.venv-1/bin/python -m pip install onnxruntime-directml          # Windows / AMD-Intel
# NVIDIA: install onnxruntime-gpu + the CUDA pip wheels (see the NVIDIA
# section under "Driver venv"):
.venv-1/bin/python -m pip install "onnxruntime-gpu==1.22.0" \
  nvidia-cuda-runtime-cu12 nvidia-cudnn-cu12 nvidia-cublas-cu12 \
  nvidia-curand-cu12 nvidia-cufft-cu12 nvidia-cuda-nvrtc-cu12
```

The four `ppocrv5_*` adapters read pre-placed ONNX weights from
`.venv-1/models/<engine>.onnx` plus a sibling character-dict text file; they do
not auto-download. PaddlePaddle publishes these as Paddle inference models, so
convert them once into the layout the adapters expect:

```
.venv-1/bin/python -m pip install paddlepaddle paddle2onnx   # CPU paddle is fine; conversion only
```

For each model, download the HF repo and run `paddle2onnx`, saving to
`.venv-1/models/<engine>.onnx`; write the character dict from the model's
`inference.yml` (`character_dict:` list, one entry per line) to the matching
dict file:

| Engine | HF repo | onnx file | dict file |
| --- | --- | --- | --- |
| `ppocrv5_mobile` | `PaddlePaddle/PP-OCRv5_mobile_rec` | `ppocrv5_mobile.onnx` | `ppocrv5_multilingual_dict.txt` |
| `ppocrv5_en_mobile` | `PaddlePaddle/en_PP-OCRv5_mobile_rec` | `ppocrv5_en_mobile.onnx` | `ppocrv5_en_dict.txt` |
| `ppocrv5_latin_mobile` | `PaddlePaddle/latin_PP-OCRv5_mobile_rec` | `ppocrv5_latin_mobile.onnx` | `ppocrv5_latin_dict.txt` |
| `ppocrv5_server` | `PaddlePaddle/PP-OCRv5_server_rec` | `ppocrv5_server.onnx` | `ppocrv5_multilingual_dict.txt` |

```
paddle2onnx --model_dir <hf_snapshot_dir> \
  --model_filename inference.json --params_filename inference.pdiparams \
  --save_file .venv-1/models/<engine>.onnx --opset_version 14
```

A clean conversion reproduces the originals exactly: `ppocrv5_en_mobile` reads
the probe cell as `Agility` (conf ~0.95), and `ppocrv5_mobile`'s multilingual
decoder spills CJK on it (`Agility大室`, conf ~0.62), matching the committed
result for that engine.

`rapidocr` carries its own bundled PP-OCR ONNX and downloads on first run; no
manual weights needed. On NVIDIA it uses CUDA automatically (the adapter passes
`rec_use_cuda` when a CUDA ONNX Runtime is present).

### `.venv-2` : OnnxTR (docTR recogniser zoo over ONNX Runtime)

Engines: `onnxtr_crnn_mobile`, `onnxtr_vitstr`, `onnxtr_viptr`,
`onnxtr_parseq`, `onnxtr_sar`, `onnxtr_master`.

```
python -m venv .venv-2
.venv-2/bin/python -m pip install --upgrade pip
.venv-2/bin/python -m pip install numpy opencv-python rapidfuzz psutil
.venv-2/bin/python -m pip install "onnxtr[gpu]"
```

If `onnxtr[gpu]` pulls a CUDA-only onnxruntime that conflicts on Windows,
install the base package and add the provider you want separately:

```
.venv-2/bin/python -m pip install onnxtr
.venv-2/bin/python -m pip install onnxruntime-directml   # or onnxruntime-gpu on NVIDIA
```

### `.venv-3` : OpenOCR / SVTRv2 (the headline engine)

Engine: `openocr_svtrv2`.

```
python -m venv .venv-3
.venv-3/bin/python -m pip install --upgrade pip
.venv-3/bin/python -m pip install numpy opencv-python rapidfuzz psutil
.venv-3/bin/python -m pip install openocr-python
```

The SVTRv2-mobile weights (~24 MB) download from ModelScope on first run. CPU is
fine; this is the fastest accurate engine in the sweep.

### `.venv-4` : MMOCR family (pinning-fragile, Python 3.10, CPU)

Engines: `mmocr_abinet`, `mmocr_robustscanner`, `mmocr_satrn`.

The OpenMMLab 1.x stack (`mmcv 2.0.1` / `mmdet 3.1.0` / `mmocr 1.0.1`) carries
`digit_version()` runtime assertions, so you must land on that exact set. It is
pinned to **torch 2.0**, which has no Python 3.12 wheel and no current CUDA
wheel on the standard indices, so build this venv on **Python 3.10 with the
prebuilt CPU stack**. (MMOCR therefore runs on CPU here; on a host with a
matching torch-2.0 CUDA build + the cu-tagged mmcv wheel it can run on GPU.)

```
python3.10 -m venv .venv-4
.venv-4/bin/python -m pip install --upgrade pip setuptools wheel
.venv-4/bin/python -m pip install "numpy<2" "opencv-python<4.10" rapidfuzz psutil
.venv-4/bin/python -m pip install torch==2.0.0 torchvision==0.15.1 \
  --index-url https://download.pytorch.org/whl/cpu
.venv-4/bin/python -m pip install -U openmim
.venv-4/bin/python -m pip install mmengine==0.10.7
# mmcv 2.0.1 prebuilt wheel (the pip source build fails without extra headers):
.venv-4/bin/python -m pip install mmcv==2.0.1 \
  -f https://download.openmmlab.com/mmcv/dist/cpu/torch2.0.0/index.html
# mmdet 3.1.0 --no-deps (3.2.0 satisfies pip but re-pulls a newer mmcv):
.venv-4/bin/python -m pip install mmdet==3.1.0 --no-deps
.venv-4/bin/python -m pip install mmocr==1.0.1 terminaltables
```

`numpy<2` and `opencv-python<4.10` are required by the torch-2.0 ABI. If `mim`
or pip tries to "upgrade" mmcv/mmdet past these pins, the `digit_version`
assertions in mmocr will refuse to import.

### `.venv-5` : TrOCR-large + Donut + Nougat

Engines: `trocr_large_printed`, `donut`, `nougat`.

```
python -m venv .venv-5
.venv-5/bin/python -m pip install --upgrade pip
.venv-5/bin/python -m pip install numpy opencv-python rapidfuzz psutil
.venv-5/bin/python -m pip install torch torchvision      # CUDA wheel index on NVIDIA, see below
.venv-5/bin/python -m pip install "transformers<5" pillow sentencepiece protobuf
.venv-5/bin/python -m pip install nltk python-Levenshtein   # required by Nougat's tokenizer
```

**Pin `transformers<5`** (4.57.x is known-good). Under transformers 5.x the
TrOCR / Donut / Nougat decoders crash with `Cannot copy out of meta tensor`
(position embeddings stay on the meta device after `from_pretrained`), and the
Nougat image processor rejects its own config (`do_crop_margin expected bool,
got None`). 4.57.6 loads all three cleanly.

On CUDA the adapters load Donut and Nougat in fp16 so the 960px-upscaled Swin
encoder fits a 4 GB card (fp32 OOMs); TrOCR-large stays fp32 (it fits, and its
white-pad path mixes dtypes under fp16). On CPU all three run fp32; TrOCR-large
is ~1 s/cell, so a full panel run is several minutes (recorded as valid wall
time).

### `.venv-6` : Florence-2 family  (Surya is a separate venv, see below)

Engines: `florence2_base`, `florence2_large`.

```
python -m venv .venv-6
.venv-6/bin/python -m pip install --upgrade pip
.venv-6/bin/python -m pip install numpy opencv-python rapidfuzz psutil
.venv-6/bin/python -m pip install torch torchvision      # CUDA wheel index on NVIDIA, see below
.venv-6/bin/python -m pip install "transformers==4.49.0" pillow einops timm
```

**Pin `transformers==4.49.0`.** Florence-2's vendored modelling code
(`trust_remote_code=True`) breaks on newer transformers: 5.x crashes in
`prepare_inputs_for_generation` (the legacy tuple-shaped `past_key_values`),
and 4.5x intermediate versions hit other vendored-code mismatches. `timm` is
required by Florence's image encoder. Keep `attn_implementation="eager"` in the
adapters (Florence's class lacks `_supports_sdpa`). On CUDA the adapters load
fp16 (fits a 4 GB card); CPU runs fp32.

### `.venv-6-surya` : Surya (separate venv)

Engine: `surya`. Split out because Surya and Florence-2 have incompatible
dependency requirements. Surya is non-commercial (GPL-3.0 code + CC-BY-NC
weights): research-only, not shippable.

```
python -m venv .venv-6-surya
.venv-6-surya/bin/python -m pip install --upgrade pip
.venv-6-surya/bin/python -m pip install numpy opencv-python rapidfuzz psutil requests
.venv-6-surya/bin/python -m pip install "surya-ocr==0.17.1" "transformers==4.49.0"
```

**Pin `surya-ocr==0.17.1`** (the last library-style release) **and
`transformers==4.49.0`.** Surya 0.20 ("Surya2") dropped the local-torch
recogniser entirely: it only runs via a Docker/vLLM service or llama.cpp, which
does not fit a per-crop library benchmark. 0.17.1's model code also needs
`transformers<5` (5.x removed `pad_token_id` from the decoder config it relies
on). Point `engine_venvs.json`'s `surya` entry at `.venv-6-surya/bin/python`.
The adapter passes a whole-image bbox so Surya runs recognition-only (no
detection predictor needed) on the pre-cropped cells.

### `.venv-7` : large VLMs (GOT-OCR2 + Kosmos-2.5 + dots.ocr)

Engines: `got_ocr2`, `kosmos25`, `dots_ocr`.

```
python -m venv .venv-7
.venv-7/bin/python -m pip install --upgrade pip
.venv-7/bin/python -m pip install numpy opencv-python rapidfuzz psutil
.venv-7/bin/python -m pip install torch torchvision      # CUDA wheel index on NVIDIA, see below
.venv-7/bin/python -m pip install "transformers>=4.50" pillow tiktoken
.venv-7/bin/python -m pip install accelerate einops protobuf sentencepiece
```

All three load with `trust_remote_code=True`. `dots_ocr` is ~6 GB on disk and
carries a bespoke licence; `nougat`, `surya`, and `dots_ocr` are research-only.
On CUDA the adapters load fp16/bf16 to save memory.

**Memory:** `got_ocr2` (~580 M) fits a 4 GB card; `kosmos25` (~1.4 B) and
`dots_ocr` (~1.7 B) do not — they OOM at attention / weight-load respectively
and need a bigger GPU (≥ ~16 GB). On a 4 GB card the harness records them as a
structured "did not complete" result (`status="failed"`, `oom=true`) rather
than crashing the run; they appear in the leaderboard's "Did not complete"
section. That is the honest outcome for this hardware, not a bug.

### NVIDIA: install the CUDA PyTorch wheels

Wherever a recipe above installs `torch torchvision` and you are on NVIDIA, use
the CUDA wheel index so you get GPU PyTorch:

```
.venv-N/bin/python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

and use `onnxruntime-gpu` (not `onnxruntime-directml`) for the ONNX-based engines.

## 5. Healthcheck

The healthcheck runs each engine through a one-cell probe (the canonical
"Agility" cell) so you can eyeball plausibility before a full sweep.

```
python -m backend.ocr.calibration.bench.healthcheck
```

Engines without a usable venv print `skipped (missing interpreter)`. Engines
with a venv but a broken adapter print the import / runtime error inline. A
clean healthcheck reads the expected text back for every engine you brought
online.

## 6. Smoke bench (the headline path)

The single runnable reproduction is the shipped engine over the shipped corpus:

```
python -m backend.ocr.calibration.bench.runner --engine openocr_svtrv2
python -m backend.ocr.calibration.bench.report --engines openocr_svtrv2
```

If `openocr_svtrv2` re-scores at 100% effective accuracy on the 594-cell corpus
(550 PASS + 44 RECOVERED + 0 UNRECOVERABLE), the wiring is good. That is the
same result the leaderboard reports.

You can also drive engines through the orchestrator, which routes each to its
mapped venv as a subprocess:

```
python -m backend.ocr.calibration.benchmark_panel_ocr --engines openocr_svtrv2
python -m backend.ocr.calibration.benchmark_panel_ocr --tier ship          # 13-engine shortlist
python -m backend.ocr.calibration.benchmark_panel_ocr --skip-existing      # idempotent re-run
python -m backend.ocr.calibration.bench.report                             # regenerate all report tables
```

`--skip-existing` reuses any result already under `calibration/bench/results/`,
so staged runs are idempotent. Long runs (the VLM tier has minutes-per-cell CPU
wall time) are best fired from a terminal you can leave running.

## 7. Completing the remaining 15 engines on a Linux + NVIDIA host

The committed leaderboard covers the 13 engines that ran on the AMD + Windows
capture host (DirectML, no CUDA). The other 15 (`mmocr_abinet`,
`mmocr_robustscanner`, `mmocr_satrn`, `trocr_large_printed`, `donut`, `nougat`,
`florence2_base`, `florence2_large`, `surya`, `got_ocr2`, `kosmos25`,
`dots_ocr`, and the heavier OnnxTR recognisers if you want to re-run them on
GPU) need CUDA or ROCm. To complete them:

1. Clone the repo onto a Linux + NVIDIA box and build the driver venv (step 2),
   uncommenting `onnxruntime-gpu` in `requirements-driver.txt`.
2. Build the per-engine venvs you need (`.venv-4` through `.venv-7` carry the
   bulk of the pending engines), installing PyTorch from the CUDA wheel index as
   noted above.
3. Point `engine_venvs.json` at the POSIX interpreter paths (`bin/python`) and
   set `HF_HOME` to a path with room for multi-GB weights.
4. Healthcheck the new engines, then run them. The cheapest-to-heaviest order is
   roughly: MMOCR family, then TrOCR-large / Donut / Nougat, then Florence-2,
   then the large VLMs.

   ```
   python -m backend.ocr.calibration.benchmark_panel_ocr --tier gpu --skip-existing
   python -m backend.ocr.calibration.benchmark_panel_ocr --tier vlm --skip-existing
   python -m backend.ocr.calibration.benchmark_panel_ocr --skip-existing
   ```

5. Regenerate the report so the aggregates cover the full set:

   ```
   python -m backend.ocr.calibration.bench.report
   ```

   New result JSONs land under `calibration/bench/results/`, and the rendered
   leaderboard and analyses under `calibration/bench/report/` pick them up.

## Troubleshooting

- **`engine X subprocess exit=127`**: the orchestrator could not find or spawn
  the mapped interpreter. Check `engine_venvs.json` and that the venv exists.
- **`ModuleNotFoundError` from inside an engine subprocess**: the venv is wired
  but missing a dep; revisit that engine's recipe above.
- **An ONNX engine runs on CPU on an NVIDIA host despite `onnxruntime-gpu`**:
  some packages (`openocr-python`, `paddleocr`) depend on the plain CPU
  `onnxruntime` wheel and pull it in, shadowing the GPU build (both share the
  `onnxruntime/` import dir). After installing those, restore the GPU build:
  `pip uninstall -y onnxruntime && pip install --force-reinstall --no-deps
  "onnxruntime-gpu==1.22.0"`. Confirm with
  `python -c "import onnxruntime as o; o.preload_dlls(); print(o.get_device())"`
  (should print `GPU`).
- **A POSIX venv engine runs under the base interpreter (e.g. `cv2` not found
  though the venv has it)**: the orchestrator must not resolve the venv's
  `bin/python` symlink (doing so dereferences it to the base interpreter). This
  is handled in `load_engine_runtime_config`; if you see `python=<conda env>`
  instead of `python=.venv-N` in the launch banner, that resolution regressed.
- **First-run download stalls**: the auto-download from ModelScope (OpenOCR) or
  HuggingFace (transformer engines) dominates first-run wall time. It runs
  idempotently once the cache populates.
- **OnnxTR family shows a universal `Agility----` trailing-dash artefact**:
  known and documented in the report. A bench-level `text.rstrip('-')` would
  lift the whole family into the high-90s; it is left unpatched so engines are
  shown as they behave out of the box.
- **Ground truth disagrees with a panel screenshot**: the ground truth is
  screen-verbatim correct as of capture. If you believe a row is mistranscribed,
  raise it as a one-shot reviewable change with a screenshot of the source
  panel attached. Do not edit speculatively.

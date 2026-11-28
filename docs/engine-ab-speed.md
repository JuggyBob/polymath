# Engine A/B speed notes — measured, with caveats

Date: 2026-11-16 to 2026-11-23; one later status note dated 2026-11-26/27.
All numbers below are from runs on the author's machine unless a row is labelled
as a vendor claim or an other-reporter claim. **Nothing here is an official
benchmark or a published result.** A row that did not complete is marked
`NOT RUN`, `FAILED` or `ERROR` and is not estimated. Local paths, addresses,
process IDs and user-specific identifiers are omitted; artifacts are named
generically.

Speed tables from different suites are **not directly comparable**. They use
different harnesses (direct CLI, `--bench`, HTTP server, agent), different
contexts (32K vs 96K), different prompts and different generation budgets. Read
each table only inside its own section.

## Hardware, model, and engines

| Item | Value |
|---|---|
| GPU | AMD Radeon RX 7600 XT, 16 GB, gfx1102, HIP on Windows |
| System RAM | 31.11 GB total at preflight |
| Model | Qwen3.6-35B-A3B UD-Q3_K_M GGUF, 17,104,402,720 bytes (17.10 GB) |
| Local engine build | Compiled for gfx1102 with ROCm 10.2; 44 compiler warnings, no errors; ~8,059 of 10,496 routed experts in VRAM (~10.5 GiB), 8 CPU threads (32K optimization work) |
| BASE | Daily pre-poly.10 engine, git `7a6c098`, tag `pre-poly10-20261118-poly10` |
| POLY2 | Trial build of `v0.2.20-poly.2`, git `5c838331` |
| Match note | POLY2 was rebuilt with `STRATA_PORTABLE=OFF`, `STRATA_PREFILL_MMQ=ON`, gfx1102 and the same ROCm toolchain as BASE. `STRATA_GGML_DIR` could not be matched: poly.2 vendors ggml. That is the only known build difference. |
| 96K server settings | 98,304-token context, conversation cache 0 MiB, `--tail-skip 6`, whole KV, `--cache-bias 0.25`, 2,000 MiB VRAM reserve. Identical model, tokenizer, flags and copied expert profiles for both engines; no daily config was modified. |

## Bottom line (author-measured)

- At 96K, BASE completed the whole agentic workload: **121 requests**, mean
  decode **78.61 tok/s** (long generations 78.68 tok/s), mean fresh prefill
  **325.91 tok/s**. No crash.
- POLY2 served only **two probe requests** before crashing on the first real
  agentic request. Its decode figures (78.9 tok/s mean, 79.3 tok/s on the
  longest generation) are a single short probe, not a workload result.
- **Prefill/decode on the repair workload: `NOT RUN` for POLY2.** No usable
  before/after comparison exists. POLY2 was not adopted; the daily engine was
  left unchanged.
- The earlier direct-CLI A/B that showed a large prefill regression was
  **withdrawn as unrepresentative** and is not used for any decision (below).
- `v0.2.20-poly.5` was **not tested on this machine** in these campaigns. Its
  speed claims are external/other-reporter claims, not author measurements.

## 96K server A/B — BASE vs poly.2

Real text prompts, no forced token IDs, long generation, agent requests through
the same profile the daily setup uses. One engine loaded at a time.

### Decode probe (one request per engine)

| Field | BASE | POLY2 |
|---|---:|---:|
| Prompt | one short story prompt | one short story prompt |
| Wall seconds | 27.27 | 21.41 |
| Completion chars / words | 8,696 / 1,501 | 7,097 / 1,196 |
| Prompt / completion tokens | 20 / 2,048 | 20 / 1,659 |
| Finish reason | length | stop |
| Prefill (fresh) | 73.7 tok/s | 71.1 tok/s |
| Decode | 75.9 tok/s | 79.3 tok/s |
| Drafts accepted | 1,040 of 1,584 | 1,105 of 1,573 |

POLY2 is +4.5% on this one probe (79.3 vs 75.9 tok/s). One run each, different
completion lengths and finish reasons; not a basis for adoption.

### Per-request speed summary (engine's own timing lines)

| Metric | BASE | POLY2 |
|---|---:|---:|
| Requests logged | 121 | 2 |
| Prompt tokens total | 3,600,503 | 40 |
| Freshly read (prefill) tokens | 106,317 | 40 |
| Generated tokens | 33,207 | 3,707 |
| Fresh prefill (read ≥100), n | 114 | `NOT RUN` |
| Fresh prefill mean / median / min / max, tok/s | 325.91 / 286.35 / 184.5 / 969.0 | `NOT RUN` |
| Cached prefill (read 1–99), n | 7 | 2 |
| Cached prefill mean / median / min / max, tok/s | 154.16 / 138.4 / 73.7 / 238.7 | 73.9 / 73.9 / 71.1 / 76.7 |
| Decode, all requests, n | 121 | 2 |
| Decode all mean / median / min / max, tok/s | 78.61 / 78.9 / 58.5 / 104.5 | 78.9 / 78.9 / 78.5 / 79.3 |
| Decode, generations ≥200 tokens, n | 53 | 2 |
| Decode long mean / median / min / max, tok/s | 78.68 / 78.7 / 58.5 / 104.5 | 78.9 / 78.9 / 78.5 / 79.3 |
| Longest generation | 2,048 tokens at 75.9 tok/s | 2,048 tokens at 79.3 tok/s |
| Drafts, longest generation | 1,040 of 1,584 | 1,105 of 1,573 |
| Drafts, second POLY2 request | — | 889 of 1,316 (1,659 generated) |

Draft acceptance was recorded at 96K but **not** in the 32K check below: that
build emitted no drafts-accepted field, so MTP benefit is unmeasured there. The
BASE draft counts above are exact log values, not an estimated acceptance rate.

### Requested comparison

| Metric | Comparison |
|---|---|
| Fresh prefill mean | `NOT RUN` |
| Decode mean (all) | BASE 78.61 → POLY2 78.9 (+0.4%) |
| Decode mean (long gen) | BASE 78.68 → POLY2 78.9 (+0.3%) |
| Longest-generation decode | BASE 75.9 → POLY2 79.3 (+4.5%) |

### Stability — why POLY2 has no workload row

- POLY2 crashed on the first real v5 request after the probe: faulting module
  `amdhip64_7.dll`, exception `0xC0000005`, fault offset `0x2d874a`. Three
  identical faults in the first attempt.
- A clean retry with a 90-second cooldown and a freshly copied expert profile
  produced three more faults at the same offset. The engine's expert cache had
  grown from 5,452 to 5,504 experts just after the probe.
- BASE completed the identical workload without a single crash. `NOT RUN` for
  POLY2 here means the engine never survived long enough to produce data, not
  that a value was omitted.
- A later flag test with `STRATA_FREEZE_EXPERTS=1` was accepted by the engine
  but never became READY within 600 s; its log ended with a rocBLAS internal
  error during handle destruction. No request was served and no
  `0xC0000005` fault was recorded. Because the machine had just rebooted with a
  cold OS file cache, this is **inconclusive**, not proof the workaround fails.

### Repair-fixture scores (not speed)

| Language | BASE score | POLY2 score |
|---|---|---|
| Python | passed 76 / failed 4 / zero=False | passed 48 / failed 32 / zero=False — **not meaningful**: the engine had crashed, so the untouched candidate was scored as-is |
| C++ | `ERROR` — published scorer raises `NameError: name 'shutil' is not defined`; fails identically for both engines | `NOT RUN` |
| JavaScript | passed 58 / failed 0 / zero=False | `NOT RUN` |
| Rust | passed 69 / failed 0 / zero=False | `NOT RUN` |

The C++ scorer defect is in the published fixture, not in either engine; the
C++ repair itself completed, but no score is claimed.

### Limits

- Single run per engine/language, no warm-up or median of three. Run-to-run
  noise on a loaded 35B MoE is a few percent; the 0.3–0.4% decode gaps are
  inside noise, and the +4.5% probe gap is one run.
- The prompt mix was real (agent tool-use chat plus one generated story), not
  synthetic token IDs. This is a gfx1102/HIP result. It neither confirms nor
  refutes upstream gains published for CUDA cards (RTX 4090 D / PRO 6000,
  RTX 4070 Laptop).

## Direct-CLI A/B — withdrawn harness, kept for the record

This harness forced token IDs (`1..N`), used only 128 generated tokens and a
cold, short regime. It reported about **349 tok/s prefill** and **10 tok/s
decode** at 2,048 tokens, which did not match the real server: a fresh
10,577-token read at **994 tok/s** and a 1,200-token answer at **76 tok/s**.
It was **withdrawn as unrepresentative** and is not used for the decision.
The profile was reset from a fresh copy before every run.

### Unmatched build flags (withdrawn)

| Prompt tokens | BASE prefill | POLY2 prefill | Prefill change | BASE decode | POLY2 decode | Decode change | Generated (B / P) | Elapsed s (B / P) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 256 | 134.3 | 106.5 | −20.7% | 32.74 | 33.04 | +0.9% | 128 / 128 | 69.4 / 64.4 |
| 512 | 200.5 | 145.0 | −27.7% | 50.60 | 52.63 | +4.0%* | 81 / 96 | 69.4 / 67.4 |
| 1,028 | 266.7 | 165.5 | −37.9% | 18.28 | 13.38 | `n/a` | 2 / 2 | 71.4 / 66.4 |
| 2,048 | 445.6 | 254.2 | −43.0% | 23.89 | 15.71 | `n/a` | 27 / 2 | 74.4 / 70.4 |

All eight runs exited 0. \* Generated counts differ (81 vs 96), so this decode row is only indicative.
The 1,028 and 2,048 decode rows are **invalid**: only 2 tokens were emitted,
so the figure is start-up, not steady-state decode. Here POLY2 was built with
`STRATA_PORTABLE=ON`, `STRATA_BUILD_SPLIT=OFF`, no MMQ flag and no GGML
directory, so the regression could not be attributed to the release.

### Matched build flags (still withdrawn as a harness)

POLY2 was rebuilt from the same source with BASE's settings
(`STRATA_PORTABLE=OFF`, `STRATA_PREFILL_MMQ=ON`, same toolchain and gfx1102;
`STRATA_GGML_DIR` unavailable because ggml is vendored).

| Prompt tokens | BASE prefill | POLY2 prefill | Prefill change | BASE decode | POLY2 decode | Generated (B / P) | Elapsed s (B / P) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 256 | 139.3 | 81.2 | −41.7% | 36.17 | 35.62 | 128 / 128 | 72.4 / 81.9 |
| 512 | 200.8 | 158.3 | −21.2% | 55.69 | 59.91* | 118 / 106 | 66.4 / 70.5 |
| 1,028 | 248.0 | 170.1 | −31.4% | 14.12 | 15.89 | 2 / 2 | 77.5 / 70.5 |
| 2,048 | 349.7 | 253.8 | −27.4% | 10.52 | 14.43 | 27 / 2 | 92.7 / 79.6 |

All eight runs exited 0. \* Generated counts differ; only the 256-token row is a clean decode
comparison, where POLY2 is 1.5% **slower**. The 1,028 and 2,048 decode rows
remain invalid (2 tokens generated). With matched flags, prefill was 21–42%
slower on POLY2 at every prompt size; BASE run-to-run noise was about 4%, so
the prefill gaps are far larger than noise. This harness was still not used
for the adoption decision.

## 32K like-for-like check — different engines, not an engine benchmark

Same GGUF, same prompt, same 256-token output budget, 32,768-token context,
one arm loaded at a time (author-measured, 2026-11-21).

| | llama.cpp b12588 (Vulkan0) | PolyStrata (HIP) |
|---|---:|---:|
| Run 1 decode, tok/s | 46.08 | 64.5 |
| Run 2 decode, tok/s | 47.21 | 70.6 |
| Mean decode, tok/s | 46.6 | 67.6 |
| Run 1 prefill, tok/s | 69.61 (30 prompt tokens) | not reported by this build |
| Run 2 prefill, tok/s | 70.66 (4 prompt tokens, cache hit) | not reported by this build |
| Drafts accepted | not reported by this build | not reported by this build |
| Time to health | 73.88 s | 3.6 s |
| Dedicated VRAM while loaded | 15,032.9 → 15,051.8 MB | 13,679.5 MB |

An earlier author-noted PolyStrata A/B at 96K was 27.9 tok/s, about 2.4x
slower than 67.6 tok/s at 32K, which points to context length rather than the
engine as the main cause of the reported discrepancy. Earlier reference points
(27.9 tok/s at 96K, ~23 tok/s at 128K, ~85 tok/s at 32K) are prior notes, not
produced in this campaign and not re-measured here.

Caveats: different GPU backends; llama.cpp preserved all 256 tokens as
reasoning (empty visible content) while PolyStrata put them in visible content;
sampling differed; expert cache was warm (97.5%/98.5% hit) on the PolyStrata
runs; two requests per arm, no variance estimate. Neither arm reproduced a
reported ~60 tok/s exactly.

## 32K optimization, before/after — author-measured (2026-11-16)

Screening: six fixed, greedy, 100-token prompts per arm, decode from the
engine's own timing lines. Short-prompt median, tok/s:

| Variant | Median | vs baseline |
|---|---:|---:|
| baseline | 92.7 | — |
| `--cache-bias 0.25` | 98.6 / 99.9 | +6.4% |
| `--cache-bias 0.5` | 100.8 / 98.4 | +8.7% |
| `--cache-bias 0.75` | 96.9 | +4.5% |
| `--cache-bias 1.0` | 97.6 | +5.3% |
| `--vram-pool` | 97.5 | +5.2% (attribute to noise) |
| `--threads 12` | 90.8 | −2.0% |
| `STRATA_IO_THREADS=16` | 92.6 | −0.1% |
| bias 0.5 + `--kv q8_0` | 96.2 | worse |

`--vram-pool` is a no-op on this build (engine prints that it needs VMM,
growing attention caches and one card: off). Full-suite result with the chosen
`--cache-bias 0.25`:

| Metric | Baseline | Optimized | Change |
|---|---:|---:|---:|
| Chat decode | 76.10 tok/s (63.8–103.3) | 85.45 tok/s (73.8–108.6) | +12.3% |
| Chat first token | 0.31 s | 0.27 s | −12.7% |
| 4K prompt prefill | 1,380 tok/s | 1,410 tok/s | +2.1% |
| 16K prompt prefill | 1,031 tok/s | 1,100 tok/s | +6.7% |
| Agent decode | 71.95 tok/s | 75.50 tok/s | +4.9% |
| Agent first token | 3.82 s | 3.71 s | −2.8% |

Quality cost of cache bias (thinking disabled, six fixed prompts):

| Comparison | Exact matches | Mean text similarity |
|---|---:|---:|
| baseline vs bias 0.25 | 2 / 6 | 0.697 |
| baseline vs bias 0.5 | 2 / 6 | 0.646 |

Caveats: the 100 tok/s target was not reached consistently (screening 99–101,
full-suite median 85.45, peak 108.6); the 16K arm returned 1,099.80 twice,
suspiciously stable; this is an AMD beta; context is 32K, not the Coder's
262K; two runs per test.

## poly.2 vs poly.5 — what is and is not measured here

- **Author-measured:** poly.2 at 96K is covered above. It crashed
  deterministically on gfx1102 and was not adopted. This is a local HIP build
  result.
- **Other-reporter claim, not author-measured:** the prefill fix in
  `0.2.20-poly.5` / engine 0.1.66 was reported as 1.36–1.57x faster prefill
  than the 0.1.45 baseline at 1.8k–29k tokens, with zero expert-cache resize
  lines. The reporter attributes it to `STRATA_VMM_NO_PROMPT_LEND`; the
  release notes credit int8 prompt kernels. **It was not a controlled A/B.**
- **Status claim, not a speed measurement:** as of 2026-11-27 the gfx1102
  crash fix shipped in poly.5 still awaited confirmation on this card, and
  newer poly.6 numbers were on gfx1201/gfx1101 or WSL2, not gfx1102.
- **Vendor claim, not reproduced here:** upstream prefill gains were published
  on NVIDIA cards (RTX 4090 D / PRO 6000, RTX 4070 Laptop). They are neither
  confirmed nor refuted by the gfx1102 results above.

## Other models on the same card — separate suites, do not mix with the tables above

### Inkling 2 Mini, `--bench`, 512-token prompt, 128 generated unless noted (author-measured)

| Arm | Flags changed | Prefill tok/s | Decode tok/s |
|---|---|---:|---:|
| baseline | defaults (auto KV, auto experts) | 310.5 | 23.6 |
| k8v4 | `--kv k8v4 --cpu-threads 8` | 261.0 | 23.9 |
| D1 | `--kv fp8 --kv-offload off --vram-experts-gb 8 --ram-experts-gb 2 --vram-reserve-mib 700 --cpu-threads 8`, prompt 1,024 / gen 256 | 34.4 | 0.8 |
| V2 | `--kv fp8 --vram-experts-gb 7.0 --vram-reserve-mib 700 --cpu-threads 8` | 250.6 | 8.3 |
| V3 | `--kv fp8 --vram-experts-gb 7.5 --vram-reserve-mib 900 --cpu-threads 8` | 267.0 | 9.0 |
| V4 | `--kv fp8 --ram-experts-gb 2 --vram-reserve-mib 700 --cpu-threads 8` | 264.3 | 24.0 |
| V5 | `--kv fp8 --vram-reserve-mib 512 --cpu-threads 12` | 266.2 | 24.0 |
| V6 | `--kv fp16 --vram-reserve-mib 700 --cpu-threads 8` | 260.3 | 24.1 |
| dspark | `--dspark <drafter> --kv fp8 --vram-reserve-mib 700 --cpu-threads 8` | 242.4 | 21.6 |

Auto expert placement was best; forcing `--vram-experts-gb` ≥7 collapsed
decode to 8–9 tok/s. No flag beat the 23.6–24.1 tok/s baseline. An earlier
gfx1102 preview on the same model/card measured 49.73 tok/s decode (128
generated) and 611 tok/s prefill on a 1,035-token prompt; the new native engine
was roughly half that speed. The vendor note "6.5 → 61.9 tok/s on 12 GB GPUs"
was **not reproduced** on this 16 GB gfx1102 card. Serve mode was `NOT RUN`:
the local wrapper lacked the 0.2.20 Inkling dialect modules, so the DSpark
drafter's serve-mode benefit was not fairly tested.

### Qwen3.8-Flash-Next, 0.1.60 vs 0.1.66, identical flags (author-measured)

Reproduced one-shot with a 512-token prompt and 128 generated, greedy, under
the same commit ceiling; this is a different model and config, not a Qwen3.6
comparison.

| Engine | Resident experts | Prefill tok/s | Decode tok/s |
|---|---:|---:|---:|
| 0.1.60 (daily) | 14.91 GiB | 77.36 | 26.64 |
| 0.1.66 (0.2.20) | 15.20 GiB | 81.03 | 21.03 |

With the right config, 0.1.66 is 21% slower at decode and 5% faster at prefill.
An earlier setup of the same test forced `--ram-keep-gib 12`, leaving only
~6 GiB of experts in RAM and thousands of file reads; it returned prefill
1.49 / 1.42 / 22.34 / 23.51 tok/s, time-to-first-token 9.4 / 9.7 / 27.3 /
26.7 s and decode 4.91 / 5.33 / 9.05 / 10.73 tok/s. That setup is superseded
and explains the apparent gap. Failed rows: `--ram-keep-gib` 8/9/10/11 exited 1
at the prefill copy stream; `generate` was an unknown argument; removing
`--spec`/MTP or using `--no-ple` was refused for native packs. A reported
40+ tok/s in serve mode (log lines: 33 generated in 824 ms = 40.0 tok/s,
22 generated in 458 ms = 48.0 tok/s) comes from an existing log with
conversation-cache reuse and about 50% draft acceptance; it is **not** a number
produced in this campaign.

## Decision (author-measured basis)

Do not adopt poly.2 on this gfx1102/HIP machine: it crashed deterministically
on the first agentic request, while BASE completed 121 requests at 78.61 tok/s
mean decode. The 4.5% probe-only decode edge does not outweigh that. The
withdrawn CLI harness is not evidence either way. poly.5 was not measured here,
so no local before/after claim is made for it. No daily config, engine binary
or model file was changed by these tests.

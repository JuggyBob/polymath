# Inkling 2 Mini vs Qwen on v6 — attempted comparison

## Status: agentic comparison NOT COMPLETED

The user asked for Inkling 2 Mini, using the AMD HIP preview engine measured at
47.58 tok/s decode, to be run on the v6 repair fixture and compared with Qwen.
The engine and model were verified and a server was started, but the agentic
run did not complete. **No Inkling repair score is claimed.**

## What was measured

### Engine and model identity

- Engine: `strata-poly.exe` from the okada-shogo `inkling2-amd-preview` branch,
  SHA-256 `90D112B02EF105428678928461D7E1F0E7F992F6133B20D1E53653059E3D02BA`,
  verified before use.
- Model: `Inkling-2-Mini-UD-Q2_K_XL.gguf`,
  SHA-256 `20292E8142B69535CA88A5D04439D0FDEB4DC698D44C002DCA706DCF92901441`.
- Hardware: RX 7600 XT (gfx1102), 16 GB; Windows process VRAM budget 15,557 MiB.

### Earlier, separately validated Inkling evidence (not a repair score)

A previous guarded test of this exact engine/model pair produced:

- 16/16 generated tokens at float64-oracle rank 1, gap 0.000000;
- decode 47.58 tok/s, prompt 33.0 tok/s, graphs on, q8_0 whole KV, 32K context;
- no spill: 3072/3072 routed experts in VRAM, 100% of experts from VRAM.

This is a token-continuation test, not the v6 repair fixture. It is recorded
here as the source of the "47 t/s" number and is **not comparable** to Qwen's
agentic repair scores.

### This session's attempt

- The binary's `--serve` mode is a stdin protocol, not an HTTP server. The
  project's `serve/server.py` was used to wrap it into an OpenAI-compatible
  endpoint on a local port.
- A tokenizer directory was extracted from the GGUF metadata with the
  project's `strata_tokenizer.py` tool (vocab 200,058; merges 424,413;
  pre-tokenizer `inkling2`), because no pack tokenizer existed on disk.
- The server started successfully and `/v1/models` reported the model as
  loaded with a 32K context.
- Direct streaming chat requests produced visible content tokens but **no
  `finish_reason` and no `[DONE]` marker**, at `max_tokens` 8, 64 and 256.
- Consequently hermes ended the v6 Rust run after 3.7 s with an incomplete-turn
  error. The scorer then graded an unmodified copy of the task, producing
  12/12 visible, 3/26 hidden — the pristine baseline, not a model result.
  That JSON is retained locally only and is not published as a score.

Guard compliance: `guard-model-load.ps1` returned `OK: load may proceed` before
the load; `guard-run.ps1` enforced the 80% commit ceiling and ran for 9.5 s
with no abort. The server was stopped afterwards; only processes started by
this test were touched.

## Why a comparison is not possible from this data

Qwen's v6 scores (Python 108/108, C++ 64/64, JS 42/73, Rust 27/38 correctness)
come from a working agentic tool-calling endpoint. The Inkling endpoint could
not complete an agentic turn. Comparing its pristine-baseline score with
Qwen's repaired score would be misleading, so it is not done.

## What would be needed

1. An engine build whose `--serve` protocol emits a final finish event that
   the HTTP wrapper forwards to clients, or a wrapper that synthesises it.
2. Confirmation that the model can emit tool calls in the chat template.
3. Then a guarded, one-model-at-a-time v6 run with the same prompt, harness and
   grader as Qwen.

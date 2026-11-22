Thanks for this PR — adding a user-interest data point rather than a duplicate issue, since both requested models are already here.

**Request / demand:** a user of LM Playground (Snapdragon 8 Elite) specifically asked for the LFM3 lineup to be added: **LFM3-1.7B** and **LFM3-Omni-2B**. Posting here so the demand is visible on the actual implementation.

**Why these two matter on-device** (from the official model cards / Liquid AI blog, vendor-reported, not independently benchmarked):

- **LFM3-1.7B** — text model, 1.73B params, **256K context**, ~1.10 GB at Q4_K_M. Liquid reports an average of 49.37 on its suite (vs 47.24 for Qwen3.5-9B), LiveClaw 45.60, AutomationBench 41.29, WebArena-Verified 38.42, IFEval 96.66, and 1.8–2.8x faster decode than the next-fastest model on the edge devices they measured. Official GGUFs: https://huggingface.co/LiquidAI/LFM3-1.7B-GGUF (Q4_K_M 1,099,627,808 bytes; also QAD-Q4_0 1,049,615,680, Q5_K_M, Q6_K, Q8_0, BF16/F16, NVFP4).
- **LFM3-Omni-2B** — omni model (text + image + video + audio in, text and 24 kHz speech out), ~2.17B params, Q4_K_M ~1.10 GB + ~507 MB mmproj. Daily-Omni 70.1 vs 58.8/61.3 for Qwen2.5-Omni 3B/7B, WorldSense 47.1. Official GGUFs: https://huggingface.co/LiquidAI/LFM3-Omni-2B-GGUF. This kind of model replaces a separate ASR + VLM + TTS stack with one on-device model, which fits LM Playground's tool/vision direction well.

Both are from the first LFM3 release (27 Oct 2026), the six-model family all branched from LFM3-1.7B-Base (22T-token pretraining). License is LFM Open License v1.0 (outputs are not restricted; commercial use of the weights has conditions) — worth a line in the catalog/README if not already there.

Appreciate the transparency about the known thinking-off quirk on LFM3 1.7B (`Paris</think>Paris` in ~2/20 replies, per your testing) and the thorough test plan. Looking forward to this shipping.

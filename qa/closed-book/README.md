# Closed-book QA sets

These are hand-written questions, not official benchmark items.

Single-prompt questions with hand-verified answer keys. No web access, no tools.
Each set is standalone: it has its own `questions.jsonl` and its own copy of the
runner, so you can copy the folder elsewhere and it still works.

| Folder | Questions | Topics |
|---|---:|---|
| `easy-mixed-12/` | 20 | SWE-style, GPQA, AIME, MMLU |
| `hard-mixed-20/` | 30 | subtle Python semantics, graduate science, competition maths, general knowledge |

The folder names are historical — the sets were expanded over time and the
names were kept so old baselines stay traceable.

## Run a set

```powershell
cd easy-mixed-12
python run_closed_book.py --port 8080
python run_closed_book.py --port 8094 --model my-model --label trial-1
python run_closed_book.py --port 8080 --dry-run
```

The runner asks for the port and model interactively if you omit them. Use
`--base-url` to supply a complete URL instead.

## Output

- Live progress with a bar, question id, category, verdict and running score.
- A final score table by category plus the overall total.
- `results-<label>-<timestamp>.json` with answers, correctness and timings.
- `reasoning/<label>-<timestamp>/<id>.md` per question: question, expected and
  parsed answer, full response, any `reasoning_content`, server timings.

## Other folders here

- `lfm25-baseline/` — an older LFM2.5 run driven through the Hermes agent
  harness rather than direct HTTP. Its runner and reports are kept for reference.
- `craft-office-hard/` — an office-document agent task scored by
  `craft_score.py`. It needs a harness that can produce a `.docx` deliverable.
- `qwen36_knowledge_eval.py` and `qwen36_hard_eval.py` in the two suite folders
  are the **original question-list sources**, kept for traceability. They have
  hardcoded endpoints and no CLI; use `run_closed_book.py` to actually run the
  questions.

These two are documented in the top-level `qa/README.md`.

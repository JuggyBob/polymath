# Unified open-ended suite

96 questions in the default run (106 if you opt into the BrowseComp category),
hand-written across seven categories:

| Category | File | n | Scoring |
|---|---|---:|---|
| `swe` | `questions/swe.jsonl` | 12 | exact answer |
| `aime` | `questions/aime.jsonl` | 12 | exact match for integer keys; 0.1% tolerance for non-integer numeric keys |
| `mmlu` | `questions/mmlu.jsonl` | 16 | A–D |
| `gpqa` | `questions/gpqa.jsonl` | 14 | A–D |
| `open_ended` | `questions/open_ended.jsonl` | 30 | rubric patterns, ≥80% |
| `traps` | `questions/traps.jsonl` | 12 | exact + trap-pattern check |
| `browsecomp` | `questions/browsecomp.jsonl` | 10 | needs web tools — opt in |

The `traps` category is the most discriminating: each item is a one-token-change
variant of a familiar question, so a model that pattern-matches instead of
reasoning gets it wrong. A trap value discussed but rejected in the reasoning
does not count against the model; only adopting it in the final `ANSWER:` line
does.

## Run it

Start an OpenAI-compatible server, then:

```powershell
python run_suite.py --port 8080
python run_suite.py --port 8080 --model qwen3.6-35b-a3b-ud-q3_k_m --label trial-1
python run_suite.py --port 8080 --dry-run
python run_suite.py --port 8080 --categories swe,aime --limit 5
python run_suite.py --port 8080 --compare baselines/qwen36-baseline-corrected-20261119-174109.json
```

If `--port` is omitted the script asks you for it. If `--model` is omitted it
asks for that too. Use `--base-url` to override the full URL.

## Output

- Progress line per question: bar, index, id, category, verdict, running score.
- Final block: per-category table, automatic total, manual count, error count,
  elapsed time.
- `baselines/<label>-<timestamp>.json` with every answer and timing.
- `reasoning/<label>-<timestamp>/<id>.md` — one formatted file per question,
  with the question, expected answer, model answer, full response, any
  `reasoning_content`, rubric detail, trap status and server timings.

## Notes

`build_questions.py` is the source of truth for the question files.
`rescore_and_patch.py` can recompute scores from an existing result JSON.
These are hand-written questions in the style of public benchmarks; they are
not official benchmark items.

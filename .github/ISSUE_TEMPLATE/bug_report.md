---
name: Bug report
about: A runner, scorer or question is behaving incorrectly
title: '[Bug] '
labels: bug
assignees: ''
---

**Suite / fixture**
Which folder and question id or fixture version?

**What happened**
Describe the wrong score, crash or output.

**Expected**
What should have happened, and why?

**Reproduction**
```powershell
# exact command, with your port and model
cd qa/open-ended && python run_suite.py --port 8080 --limit 5
```

**Environment**
- OS:
- Python / Node / Rust / C++ version:
- Model and quant:
- Context length:
- Endpoint (local/provider — do not include keys):

**Evidence**
Attach the result JSON and, if relevant, the reasoning file from `reasoning/`.
Please redact any endpoint keys or private data.

**Checklist**
- [ ] I redacted credentials and private paths.
- [ ] I included the question id or fixture version.

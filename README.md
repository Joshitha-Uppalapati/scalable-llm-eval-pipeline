# Scalable LLM Inference & Evaluation Pipeline

This repo is a local-first, CLI-driven system to run LLMs on structured eval suites, score outputs with rule-based and judge-based evaluators, track cost/latency, detect regressions, and generate readable reports.

## What this is
- Reproducible evaluation runs over versioned JSONL suites
- First-class evaluation + regression diffs (not an afterthought)
- Run artifacts + reports that support shipping decisions

## What this is not
- A UI product
- A benchmark “leaderboard”
- A framework with heavy abstractions

## Repo layout
- `src/evalpipe/` core pipeline code
- `data/suites/` versioned evaluation suites (JSONL)
- `runs/` local run artifacts (ignored)
- `reports/` generated markdown reports (ignored)
- `tests/` unit tests

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest


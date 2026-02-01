# Scalable LLM Evaluation Pipeline

[![CI](https://github.com/Joshitha-Uppalapati/scalable-llm-eval-pipeline/actions/workflows/demo.yml/badge.svg)](https://github.com/Joshitha-Uppalapati/scalable-llm-eval-pipeline/actions)

A CLI-first tool for tracking how language model behavior changes over time.

I kept running into the same problem: after tweaking a prompt or switching models, I couldn’t tell if things actually got better or just different. This repo is my way of stopping the guesswork and making changes reviewable.

---

## What it does

You give it:
- A JSONL file with test cases
- A prompt template

It produces:
- Pass/fail results per test case
- Cost and latency estimates
- A markdown report you can skim
- All run artifacts written to disk for later inspection

The goal is simple: catch regressions before they hit production.

## Quick start

```bash
git clone https://github.com/Joshitha-Uppalapati/scalable-llm-eval-pipeline.git
cd scalable-llm-eval-pipeline
pip install -e .

# Run a basic evaluation
python src/evalpipe/cli.py run data/suites/basic_v1.jsonl \
  --prompt src/evalpipe/prompts/basic_v1.txt

# Inspect results
cat runs/*/summary.json | head
```
If you want to compare against a previous run, pass `--baseline runs/<RUN_ID>`.
## How it works
JSONL suite → prompt render → inference → evaluation → aggregation → files on disk

Each test case defines:
- Input data
- Expected output or an evaluation rule
- A category (so results are easy to group)

The runner:
- Streams JSONL (does not load everything into memory)
- Runs inference with bounded concurrency
- Evaluates outputs using explicit evaluators
- Writes results and summaries as JSONL/JSON

## Project Structure
```text
src/evalpipe/
├── cli.py
├── runner.py
├── loader.py
├── evaluators/
├── aggregate.py
├── compare.py
├── report.py
└── storage.py

data/suites/            
examples/               
tests/        
```          
Some exploratory experiments are kept in `examples/exploratory/` for reference. They are not part of the core pipeline.

---

## Evaluation types
Each test case explicitly selects an evaluator:
- exact : exact string match
- regex : pattern match
- contains : substring check
- numeric : numeric tolerance
- schema : JSON schema validation
- judge : optional LLM-as-a-judge (slower, subjective)
There is no implicit scoring. The evaluation logic is always explicit.

## Baseline comparison
Compare a run against a previous one:
```bash
python src/evalpipe/cli.py run data/suites/basic_v1.jsonl \
  --prompt src/evalpipe/prompts/basic_v1.txt \
  --baseline runs/20260115_143022
```
The report highlights:
- Pass → fail regressions
- Fail → pass improvements
- Cost and latency deltas
- Category-level changes
If regressions are detected, the CLI exits non-zero. In CI, this step runs as a smoke test and does not gate merges.

---

## Output Files
Each run creates a timestamped folder under runs/:
```text
runs/20260131_033533/
├── test_cases.jsonl
├── results.jsonl
├── evaluations.jsonl
├── summary.json
├── meta.json
└── report.md
```
These files are enough to audit a run without re-running inference.

## Examples
A single runnable example is provided:

- `examples/01_basic_eval.sh` — runs the pipeline end to end using the dummy provider
- `examples/sample_outputs/summary.example.json` — example output for reference
The example mirrors how I validate the pipeline locally before comparing runs or adding new test cases.

## Running the example
```bash
pip install -e .
bash examples/01_basic_eval.sh
```

## CI
A GitHub Actions workflow runs a smoke test on each push.
Unit tests gate CI. The CLI runs as a smoke test to verify end-to-end execution and may exit non-zero when regressions are detected.

## Testing
```bash
python -m pytest

# Coverage
python -m pytest --cov=src --cov-report=term
```
Current test coverage focuses on evaluators and core execution paths.

---

## Known limitations
- Caching is local only (not distributed)
- Cost estimation assumes OpenAI-style pricing inputs
- No retry/backoff on API failures yet
- Judge-based evaluation can be slow and inconsistent
- Some error messages could be clearer
These are tradeoffs I’ve left visible instead of hiding behind extra layers.

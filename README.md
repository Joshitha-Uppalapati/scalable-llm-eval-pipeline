# Scalable LLM Evaluation Pipeline

[![CI](https://github.com/Joshitha-Uppalapati/scalable-llm-eval-pipeline/actions/workflows/demo.yml/badge.svg)](https://github.com/Joshitha-Uppalapati/scalable-llm-eval-pipeline/actions)

A CLI-first tool for tracking how language model behavior changes over time.

I kept running into the same problem: after tweaking a prompt or switching models, I couldn’t tell if things actually got better or just different. This is what I built to stop guessing and make changes reviewable.

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

## Example: Regression caught

While testing a prompt change, I noticed pass rate stayed roughly the same, but failures shifted into edge cases involving numeric outputs.

Baseline:
- Pass rate: 82%
- Numeric category: 90%

New run:
- Pass rate: 83%
- Numeric category: 72%

The change looked like an improvement overall, but degraded specific cases. This is exactly the kind of regression this pipeline is meant to catch.

## Design Decisions

**Why cache keys include prompt + parameters**
Prompt wording changes are often more impactful than model changes. Including the rendered prompt and generation parameters in the cache key makes regressions caused by prompt edits explicit and traceable.

**Why semaphore-based concurrency**
Early versions used unbounded concurrency, which made failures noisy and hard to debug. A semaphore keeps runs stable under load and mirrors how real systems are rate-limited in production.

---

## Quick start

I usually run this locally before changing prompts or models, then compare against the last stable run.

```bash
git clone https://github.com/Joshitha-Uppalapati/scalable-llm-eval-pipeline.git
cd scalable-llm-eval-pipeline
pip install -e .

# Run a basic evaluation
evalpipe run data/suites/basic_v1.jsonl \
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

---

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
- exact: exact string match
- regex: pattern match
- contains: substring check
- numeric: numeric tolerance
- schema: JSON schema validation
- judge: optional LLM-as-a-judge (slower, subjective)
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
A single runnable example is provided for local validation:
- `examples/01_basic_eval.sh` — runs the full workflow using the dummy provider
- `examples/sample_outputs/summary.example.json` — example output for reference
The example mirrors how I validate the pipeline locally before comparing runs or adding new test cases.

- Dummy provider ensures deterministic CI. Real provider example is included for integration demonstration.
- `examples/with_openai.py` optional OpenAI example (requires OPENAI_API_KEY)

## Real Provider Example (Optional)

By default, this project uses a dummy provider to keep CI runs fast,
cheap, and fully deterministic.

A real provider integration example is included in
`examples/with_openai.py` to demonstrate how the pipeline connects
to an actual LLM API.

This script is optional, not used in CI, and requires an API key
to be set locally.

## Running the example
```bash
pip install -e .
bash examples/01_basic_eval.sh
```

---

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
- Some error messages could be clearer under failure-heavy workloads.
These are tradeoffs I’ve left visible instead of hiding behind extra layers.

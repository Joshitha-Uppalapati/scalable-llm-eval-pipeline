# Scalable LLM Evaluation Pipeline

This repository contains a small, production-oriented evaluation framework for testing and comparing language model behavior over time.

The goal is to make LLM evaluations:
- Reproducible
- Inspectable
- Comparable across runs
- Safe to gate in CI

This is intentionally simple. Every artifact is written to disk. Nothing is hidden behind services or dashboards.

---

## What This System Does

For a given evaluation suite and prompt template, the pipeline:

1. Loads test cases from a JSONL suite
2. Renders prompts deterministically
3. Executes model inference
4. Evaluates outputs using rule-based evaluators
5. Aggregates results and cost metrics
6. Writes all artifacts to disk
7. Optionally compares against a baseline run
8. Fails if regressions are detected

---

## Repository Structure

src/evalpipe/
├── aggregate.py # Metrics aggregation
├── cli.py # CLI entrypoint
├── compare.py # Baseline comparison
├── costs.py # Cost estimation
├── evaluators.py # Exact match, regex, schema, etc.
├── loader.py # Suite loader
├── prompts/ # Prompt templates
├── report.py # Markdown report generator
├── runner.py 
├── storage.py



All run outputs are written under `runs/` using timestamped directories.

---

## Running an Evaluation

Basic run:

```bash
python src/evalpipe/cli.py data/suites/basic_v1.jsonl \
  --prompt src/evalpipe/prompts/basic_v1.txt


Run with baseline comparison:
python src/evalpipe/cli.py data/suites/basic_v1.jsonl \
  --prompt src/evalpipe/prompts/basic_v1.txt \
  --baseline runs/<BASELINE_RUN_ID>

Each run produces:
test_cases.jsonl
results.jsonl
evaluations.jsonl
summary.json
meta.json
report.md

## Evaluation Model
Evaluations are explicit and deterministic. Supported types include:
Exact match
Regex match
Substring containment
JSON schema validation
Each test case defines its own evaluation logic. No implicit scoring.

## Baseline Comparision
When a baseline run is provided, the system compares:
pass rate
latency
cost
category-level results
Regressions and improvements are surfaced in the generated report.
This makes prompt changes and model upgrades reviewable.

## Design Principles
No external services
No hidden state
JSONL for transparency
Deterministic prompt rendering
Exit codes suitable for CI gating

The goal is not novelty. The goal is reliability

## Why This Exists

Language model behavior changes easily:
prompts edits
evaluation logic
model version changes

Without stored baselines, regressions are easy to miss.
This pipeline makes those changes explicit and traceable.

## Execution Flow

suite
  → prompt render
    → inference
      → evaluation
        → aggregation
          → artifacts
            → comparison
              → report

##Notes
This project intentionally avoids dashboards, databases, and orchestration layers.

## Known Limitations

- Default runner uses a dummy provider unless configured with a real model.
- Cost estimates are approximate and depend on provider pricing accuracy.
- LLM-as-a-judge is optional and should not be treated as ground truth.
- Caching is local and not designed for distributed environments.


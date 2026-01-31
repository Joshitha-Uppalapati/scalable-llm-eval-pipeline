# Scalable LLM Evaluation Pipeline

![CI](https://github.com/Joshitha-Uppalapati/scalable-llm-eval-pipeline/actions/workflows/demo.yml/badge.svg?branch=main)

A production-grade, failure-aware evaluation pipeline for Large Language Models.
Built to make prompt changes, model upgrades, and regressions visible before they ship.

This repository contains a small, production-oriented evaluation framework for testing and comparing language model behavior over time.

The goal is to make LLM evaluations:
- Reproducible  
- Inspectable  
- Comparable across runs  
- Safe to gate in CI  
This is a CLI-first tool. UI exploration was intentionally deprioritized.
This is intentionally simple. Every artifact is written to disk. Nothing is hidden behind services or dashboards.

---

## What This System Does
For a given evaluation suite and prompt template, the pipeline:

- Loads test cases from a JSONL suite  
- Renders prompts deterministically  
- Executes model inference  
- Evaluates outputs using explicit evaluators  
- Aggregates metrics and cost signals  
- Writes all artifacts to disk  
- Optionally compares against a baseline run  
- Surfaces regressions in a human-readable report  

---

## Example Output
Below is an example evaluation run rendered from persisted artifacts
(`results.jsonl`, `evaluations.jsonl`, `summary.json`).

![Evaluation Results](assets/dashboard2.png)

---

## Running an Evaluation
Basic run:

```bash
python src/evalpipe/cli.py data/suites/basic_v1.jsonl \
  --prompt src/evalpipe/prompts/basic_v1.txt
```

Run with baseline comparison:

```bash
python src/evalpipe/cli.py data/suites/basic_v1.jsonl \
  --prompt src/evalpipe/prompts/basic_v1.txt \
  --baseline runs/<BASELINE_RUN_ID>
```

---

## Scalability Characteristics
- Async inference execution with bounded concurrency
- Streaming JSONL loading (no dataset fully loaded into memory)
- Failure-isolated execution (one bad row does not kill a run)
- Deterministic result ordering for reproducibility

---

## Repository Structure
```text
src/evalpipe/
├── aggregate.py
├── cli.py
├── compare.py
├── costs.py
├── pricing.py
├── evaluators/
│ ├── exact.py
│ ├── regex.py
│ ├── contains.py
│ ├── numeric.py
│ ├── schema.py
│ └── judge.py
├── loader.py
├── prompts/
├── report.py
├── runner.py
├── storage.py
└── cache/
```
All run outputs are written under `runs/` using timestamped directories.

---

## Artifacts Produced Per Run
Each run generates:
- test_cases.jsonl
- results.jsonl
- evaluations.jsonl
- summary.json
- meta.json
- report.md

These artifacts are sufficient to reproduce, audit, and review a run without re-executing inference.

---

## Evaluation Model
Evaluations are explicit and deterministic. Supported types include:
- Exact match
- Regex match
- Substring containment
- Numeric tolerance
- JSON schema validation
- Optional LLM-as-a-judge (with rubric)

Each test case defines its own evaluation logic. No implicit scoring.

---

## Baseline Comparison
When a baseline run is provided, the system compares:
- Pass rate
- Latency
- Cost
- Category-level results
- Pass → fail regressions
- Fail → pass improvements

All deltas are surfaced in the generated report.

---

## Design Principles
- No external services
- No hidden state
- JSONL for transparency
- Deterministic prompt rendering
- Exit codes suitable for CI gating

The goal is not novelty. The goal is predictable, reviewable behavior over time.

---

## CI Integration
The repository includes a GitHub Actions workflow that runs a smoke evaluation on every push.
Failures surface immediately via CI status and non-zero exit codes, making the pipeline safe to gate merges.

---

## Why This Exists
Language model behavior changes easily:
- Prompt edits
- Evaluation logic changes
- Model version upgrades
- Without stored baselines, regressions are easy to miss.
- This pipeline makes those changes explicit and reviewable

---

## Execution Flow
```mermaid
flowchart LR
  A[JSONL Suite\nStreamed Loader]
  B[Prompt Renderer\nDeterministic]
  C[Async Runner\nFailure Aware]
  D[Evaluator Registry\nExplicit Rules]
  E[Aggregation]
  F[Artifacts\nJSONL and Summary]
  G[Baseline Comparison]
  H[Report]

  A --> B
  B --> C
  C --> D
  D --> E
  E --> F
  F --> G
  G --> H
```

---

## Notes
This project intentionally avoids dashboards, databases, and orchestration layers.

---

## Known Limitations
- The default runner uses a dummy provider unless configured with a real model.
- Cost estimates are approximate and depend on provider pricing accuracy.
- LLM-as-a-judge is optional and should not be treated as ground truth.
- Caching is local and not designed for distributed environments.

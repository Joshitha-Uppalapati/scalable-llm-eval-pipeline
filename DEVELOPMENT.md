# Development Notes
This document is a record of how this project actually evolved.
It’s not a spec and it’s not marketing. It’s the thinking behind the code.

## Why I Built This
I kept changing prompts and swapping models and had no reliable way to tell if things were actually improving or just changing.

Accuracy would move around, costs would spike, and I’d have no paper trail explaining why. This started as a way to stop guessing and make changes reviewable.

I wanted something I could run locally, inspect with my own eyes, and trust.

## Early Mistakes
The very first version loaded the entire JSONL test suite into memory.

That worked fine for tiny files and completely fell apart once the suite
got even moderately large. Memory usage spiked and failures were hard
to reason about.

I rewrote the loader to stream JSONL instead.
That change lives in `runner.py`, where test cases are consumed incrementally instead of eagerly loaded.

## Async Execution: What Actually Happened
I originally used `asyncio.gather()` without any limits.

That was a mistake.
As soon as concurrency increased, a single timeout would cascade and either kill the entire run or leave tasks hanging. Debugging was painful because failures weren’t isolated.

The fix was introducing a semaphore in `run_inference_async()` inside
`runner.py`.

That gave me:
- bounded concurrency
- predictable resource usage
- isolation between failing test cases

Getting the semaphore logic right took a few tries.
An early version deadlocked when an exception occurred inside the semaphore block. The current structure explicitly catches and normalizes errors so
the run can continue.

## Why JSONL (and Not CSV or a Database)
JSONL was a deliberate choice.

I wanted:
- streaming support
- line-by-line diffs
- easy inspection during debugging

CSV made nested outputs awkward.
A database felt like overkill at this stage and would hide too much state behind abstractions.

For this project, clarity mattered more than raw scale.

## File-Based Artifacts
All run outputs are written to disk under `runs/<timestamp>/`.

This is slower than a DB, but it has advantages:
- you can inspect failures after the fact
- results are versionable
- nothing is hidden behind a service
I’ve found this makes debugging and interviews much easier.
You can literally open the files and walk through what happened.

## Prompt Rendering Lessons
- Prompt rendering looks simple but had a few sharp edges.
- The current implementation in `prompts/render.py` supports `{{field}}`
placeholders. This was added after tests caught that earlier versions
weren’t substituting correctly.

There’s also a known limitation:
- prompt rendering assumes UTF-8 text files.
- That’s fine for now, but it’s explicitly marked as a FIXME in the code.

## Evaluation Took Longer Than Inference
Calling the model was easy.
Deciding how to judge outputs was not.

Writing evaluators that fail loudly and explain *why* something failed
ended up taking more time than the inference layer itself.

The evaluator dispatch logic is intentionally simple.
I experimented with a registry pattern but found it harder to debug.
The current approach trades extensibility for readability.

## CI and Failure Modes
- CI is intentionally strict.
- If a regression is detected compared to a baseline run, the CLI exits
non-zero. This is on purpose.
- If something breaks, I want it to break loudly and early rather than silently degrading.
The goal is not green dashboards. It’s trust.

## What I’d Change Next
If I were to continue this:
- replace fixed retry sleeps with exponential backoff
- separate storage concerns from execution logic
- add a lightweight metadata store for querying runs
- add clearer error messages around malformed test cases
There are TODOs in the code that reflect these ideas.
They’re left visible intentionally.

## Final Notes
- This project wasn’t built in one pass.
- A lot of the code exists because something broke first.
- The goal here wasn’t elegance.
- It was building something that actually runs, can be explained line by line, and surfaces its own failure modes.
That mattered more than being clever.
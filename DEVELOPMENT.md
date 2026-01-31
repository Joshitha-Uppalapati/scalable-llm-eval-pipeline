# How I Built This

## Why I Started
I kept changing prompts and models and had no reliable way
to tell if things were actually improving or just changing.
This started as a way to stop guessing.

## Early Mistakes
My first version loaded the entire JSONL file into memory.
It worked on small runs and completely broke on larger ones.

I rewrote it using a generator once I hit memory issues.

## Key Decisions
### Why JSONL
I wanted:
- streaming
- easy diffs
- simple debugging

CSV made comparisons harder.
Databases felt like overkill at this stage.

### Why async + semaphore
I originally used asyncio.gather() and hit rate limits immediately.
One timeout would crash the entire run.

Using a semaphore let me:
- limit concurrency
- isolate failures
- keep runs progressing

### Why file-based outputs
This was a conscious tradeoff.
Files are slower than databases but:
- easy to inspect
- easy to version
- hard to corrupt

For this stage, clarity mattered more than scale.

## What Surprised Me
Evaluation logic took longer than inference.
Writing clear failure messages was harder than calling the API.

## What I’d Change Next
- Add retries with backoff
- Separate storage from execution
- Introduce a lightweight metadata DB

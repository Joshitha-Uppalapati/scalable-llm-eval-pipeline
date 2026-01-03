# Evaluation Report

## Run

- Run ID: `20260103_153229`
- Total tests: `31`
- Passed: `4`
- Failed: `27`
- Pass rate: `12.90%`
- Avg latency: `0.00 ms`
- Estimated cost: `$0.0000`

## Tokens

| Role | Prompt | Completion |
|---|---:|---:|
| Inference | 0 | 0 |
| Judge | 0 | 0 |

## By category

| Category | Total | Passed | Failed |
|---|---:|---:|---:|
| extraction | 5 | 2 | 3 |
| formatting | 6 | 0 | 6 |
| reasoning | 15 | 1 | 14 |
| safety | 4 | 1 | 3 |
| structure | 1 | 0 | 1 |

## By evaluator

| Evaluator | Total | Failed |
|---|---:|---:|
| contains | 17 | 13 |
| exact_match | 6 | 6 |
| regex | 7 | 7 |
| schema | 1 | 1 |

## Top failures

- `math_001` (reasoning, exact_match): Expected '408', got 'None'
- `math_002` (reasoning, exact_match): Expected '63', got 'None'
- `format_001` (formatting, regex): Output '' does not match /^(YES|NO)$/
- `format_002` (formatting, regex): Output '' does not match /^[0-9]+$/
- `reasoning_002` (reasoning, regex): Output '' does not match /^(yes|no|Yes|No)$/
- `edge_001` (reasoning, contains): Expected 'undefined' in output
- `math_003` (reasoning, exact_match): Expected '72', got 'None'
- `math_004` (reasoning, exact_match): Expected '12', got 'None'
- `math_005` (reasoning, exact_match): Expected '42', got 'None'
- `format_003` (formatting, regex): Output '' does not match /^(YES|NO)$/


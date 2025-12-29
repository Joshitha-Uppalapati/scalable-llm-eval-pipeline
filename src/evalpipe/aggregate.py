from typing import List, Dict, Any
from collections import defaultdict


def aggregate_results(
    test_cases: List[Dict[str, Any]],
    results: List[Dict[str, Any]],
    evaluations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    total = len(test_cases)

    passed = sum(1 for e in evaluations if e.get("passed"))
    failed = total - passed
    pass_rate = passed / total if total else 0.0

    by_category = defaultdict(lambda: {"total": 0, "passed": 0, "failed": 0})

    for tc, ev in zip(test_cases, evaluations):
        category = tc.get("category", "unknown")
        by_category[category]["total"] += 1
        if ev.get("passed"):
            by_category[category]["passed"] += 1
        else:
            by_category[category]["failed"] += 1

    total_latency = 0
    latency_count = 0
    prompt_tokens = 0
    completion_tokens = 0

    for r in results:
        po = r.get("provider_output")
        if po is None:
            continue

        if po.latency_ms is not None:
            total_latency += po.latency_ms
            latency_count += 1

        if po.prompt_tokens:
            prompt_tokens += po.prompt_tokens

        if po.completion_tokens:
            completion_tokens += po.completion_tokens

    avg_latency = total_latency / latency_count if latency_count else 0.0

    return {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "by_category": dict(by_category),
        "avg_latency_ms": avg_latency,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "estimated_cost": 0.0,
        "evaluations": evaluations,

    }

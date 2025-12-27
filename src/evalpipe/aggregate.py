from typing import List, Dict, Any
import math

COST_PER_1K_TOKENS = {
    "gpt-4o-mini": {
        "prompt": 0.00015,
        "completion": 0.0006,
    }
}


def aggregate_results(
    test_cases: List[Dict[str, Any]],
    results: List[Dict[str, Any]],
    evaluations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    total = len(evaluations)
    passed = sum(1 for e in evaluations if e["passed"])
    failed = total - passed

    by_category: Dict[str, Dict[str, int]] = {}
    for tc, ev in zip(test_cases, evaluations):
        cat = tc.get("category", "unknown")
        by_category.setdefault(cat, {"passed": 0, "failed": 0})
        if ev["passed"]:
            by_category[cat]["passed"] += 1
        else:
            by_category[cat]["failed"] += 1

    # latency aggregation
    latencies = [
        r.get("latency_ms")
        for r in results
        if r.get("latency_ms") is not None
    ]

    avg_latency = int(sum(latencies) / len(latencies)) if latencies else None
    max_latency = max(latencies) if latencies else None
    p95_latency = (
        sorted(latencies)[math.ceil(0.95 * len(latencies)) - 1]
        if latencies
        else None
    )

    # token + cost aggregation
    total_prompt_tokens = sum(
        r.get("prompt_tokens", 0) or 0 for r in results
    )
    total_completion_tokens = sum(
        r.get("completion_tokens", 0) or 0 for r in results
    )

    estimated_cost = 0.0
    for r in results:
        model = r.get("model")
        if model not in COST_PER_1K_TOKENS:
            continue

        pricing = COST_PER_1K_TOKENS[model]
        pt = r.get("prompt_tokens") or 0
        ct = r.get("completion_tokens") or 0

        estimated_cost += (pt / 1000) * pricing["prompt"]
        estimated_cost += (ct / 1000) * pricing["completion"]

    return {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": passed / total if total else 0.0,
        "by_category": by_category,
        "latency": {
            "avg_ms": avg_latency,
            "p95_ms": p95_latency,
            "max_ms": max_latency,
        },
        "tokens": {
            "prompt": total_prompt_tokens,
            "completion": total_completion_tokens,
        },
        "estimated_usd_cost": round(estimated_cost, 6),
    }

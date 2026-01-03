from typing import List, Dict, Any
from collections import defaultdict


def aggregate_results(
    test_cases: List[Dict[str, Any]],
    results: List[Dict[str, Any]],
    evaluations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    total = len(test_cases)

    passed = sum(1 for e in evaluations if e.get("passed") is True)
    failed = total - passed
    pass_rate = passed / total if total else 0.0

    by_category = defaultdict(lambda: {"total": 0, "passed": 0, "failed": 0})
    by_evaluator = defaultdict(lambda: {"total": 0, "failed": 0})
    top_failures = []

    for tc, ev in zip(test_cases, evaluations):
        category = tc.get("category", "unknown")
        evaluator_type = tc.get("evaluation", {}).get("type", "unknown")

        by_category[category]["total"] += 1
        by_evaluator[evaluator_type]["total"] += 1

        if ev.get("passed"):
            by_category[category]["passed"] += 1
        else:
            by_category[category]["failed"] += 1
            by_evaluator[evaluator_type]["failed"] += 1

            top_failures.append(
                {
                    "id": tc.get("id"),
                    "category": category,
                    "evaluator": evaluator_type,
                    "reason": ev.get("reason"),
                }
            )

    total_latency = 0
    latency_count = 0

    inference_prompt_tokens = 0
    inference_completion_tokens = 0

    judge_prompt_tokens = 0
    judge_completion_tokens = 0

    for r in results:
        po = r.get("provider_output")
        if not po:
            continue

        if getattr(po, "latency_ms", None) is not None:
            total_latency += po.latency_ms
            latency_count += 1

        role = r.get("role", "inference")  # default = inference

        if role == "judge":
            if getattr(po, "prompt_tokens", None):
                judge_prompt_tokens += po.prompt_tokens
            if getattr(po, "completion_tokens", None):
                judge_completion_tokens += po.completion_tokens
        else:
            if getattr(po, "prompt_tokens", None):
                inference_prompt_tokens += po.prompt_tokens
            if getattr(po, "completion_tokens", None):
                inference_completion_tokens += po.completion_tokens

    avg_latency = total_latency / latency_count if latency_count else 0.0

    return {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "by_category": dict(by_category),
        "by_evaluator": dict(by_evaluator),
        "top_failures": top_failures[:10],
        "avg_latency_ms": avg_latency,
        "tokens": {
            "inference": {
                "prompt": inference_prompt_tokens,
                "completion": inference_completion_tokens,
            },
            "judge": {
                "prompt": judge_prompt_tokens,
                "completion": judge_completion_tokens,
            },
        },
        "estimated_cost": 0.0,  # filled later
    }


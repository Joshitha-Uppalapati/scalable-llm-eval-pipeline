from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Tuple

from evalpipe.costs import estimate_cost


def _get_po_fields(po: Any) -> Tuple[int | None, int | None, int | None, str | None]:
    if po is None:
        return None, None, None, None

    if isinstance(po, dict):
        latency_ms = po.get("latency_ms")
        prompt_tokens = po.get("prompt_tokens")
        completion_tokens = po.get("completion_tokens")
        model = po.get("model")
        return latency_ms, prompt_tokens, completion_tokens, model

    latency_ms = getattr(po, "latency_ms", None)
    prompt_tokens = getattr(po, "prompt_tokens", None)
    completion_tokens = getattr(po, "completion_tokens", None)
    model = getattr(po, "model", None)
    return latency_ms, prompt_tokens, completion_tokens, model


def aggregate_results(
    test_cases: List[Dict[str, Any]],
    results: List[Dict[str, Any]],
    evaluations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    total = len(test_cases)

    passed = sum(1 for e in evaluations if e.get("passed") is True)
    failed = total - passed
    pass_rate = passed / total if total else 0.0

    by_category: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "passed": 0, "failed": 0})
    by_evaluator: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "failed": 0})
    top_failures: List[Dict[str, Any]] = []

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

    inference_usd = 0.0
    judge_usd = 0.0

    for r in results:
        role = r.get("role", "inference")
        po = r.get("provider_output")

        latency_ms, pt, ct, po_model = _get_po_fields(po)
        if latency_ms is not None:
            total_latency += int(latency_ms)
            latency_count += 1

        model = r.get("model") or po_model or "unknown"
        pt_i = int(pt) if pt is not None else 0
        ct_i = int(ct) if ct is not None else 0

        usd = float(estimate_cost(model, pt_i, ct_i))

        if role == "judge":
            judge_prompt_tokens += pt_i
            judge_completion_tokens += ct_i
            judge_usd += usd
        else:
            inference_prompt_tokens += pt_i
            inference_completion_tokens += ct_i
            inference_usd += usd

    avg_latency = total_latency / latency_count if latency_count else 0.0
    total_usd = inference_usd + judge_usd

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
            "inference": {"prompt": inference_prompt_tokens, "completion": inference_completion_tokens},
            "judge": {"prompt": judge_prompt_tokens, "completion": judge_completion_tokens},
        },
        "cost": {
            "inference_usd": round(inference_usd, 6),
            "judge_usd": round(judge_usd, 6),
            "total_usd": round(total_usd, 6),
        },
        "estimated_cost": round(total_usd, 6),
    }

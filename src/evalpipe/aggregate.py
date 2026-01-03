from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _safe_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def aggregate_results(
    test_cases: List[Dict[str, Any]],
    results: List[Dict[str, Any]],
    evaluations: List[Dict[str, Any]],
    costs: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    total = len(test_cases)
    passed = 0
    failed = 0

    by_category: Dict[str, Dict[str, int]] = {}
    by_evaluator: Dict[str, Dict[str, int]] = {}

    top_failures: List[Dict[str, Any]] = []

    latency_sum = 0
    latency_count = 0
    prompt_tokens = 0
    completion_tokens = 0

    for idx, tc in enumerate(test_cases):
        ev = evaluations[idx] if idx < len(evaluations) else {}
        res = results[idx] if idx < len(results) else {}

        ok = bool(ev.get("passed", False))
        if ok:
            passed += 1
        else:
            failed += 1

        category = tc.get("category") or "uncategorized"
        by_category.setdefault(category, {"total": 0, "passed": 0, "failed": 0})
        by_category[category]["total"] += 1
        by_category[category]["passed"] += 1 if ok else 0
        by_category[category]["failed"] += 0 if ok else 1

        eval_type = None
        if isinstance(tc.get("evaluation"), dict):
            eval_type = tc["evaluation"].get("type")
        eval_type = ev.get("evaluator") or eval_type or "unknown"

        by_evaluator.setdefault(eval_type, {"total": 0, "passed": 0, "failed": 0})
        by_evaluator[eval_type]["total"] += 1
        by_evaluator[eval_type]["passed"] += 1 if ok else 0
        by_evaluator[eval_type]["failed"] += 0 if ok else 1

        lat = res.get("latency_ms", None)
        if lat is not None:
            latency_sum += _safe_int(lat, 0)
            latency_count += 1

        prompt_tokens += _safe_int(res.get("prompt_tokens", 0), 0)
        completion_tokens += _safe_int(res.get("completion_tokens", 0), 0)

        if not ok:
            top_failures.append(
                {
                    "id": tc.get("id") or ev.get("id") or res.get("id"),
                    "category": category,
                    "evaluator": eval_type,
                    "reason": ev.get("reason") or ev.get("error") or "failed",
                }
            )

    avg_latency_ms = (latency_sum / latency_count) if latency_count else 0.0
    pass_rate = (passed / total) if total else 0.0

    cost_block = costs or {}
    estimated_cost = _safe_float(cost_block.get("estimated_cost", cost_block.get("total_usd", 0.0)), 0.0)

    inference_usd = _safe_float(cost_block.get("inference_usd", 0.0), 0.0)
    judge_usd = _safe_float(cost_block.get("judge_usd", 0.0), 0.0)

    summary: Dict[str, Any] = {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "by_category": by_category,
        "by_evaluator": by_evaluator,
        "top_failures": top_failures[:10],
        "avg_latency_ms": avg_latency_ms,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "estimated_cost": estimated_cost,
        "cost_breakdown": {
            "inference_usd": inference_usd,
            "judge_usd": judge_usd,
            "total_usd": estimated_cost,
        },
    }

    return summary


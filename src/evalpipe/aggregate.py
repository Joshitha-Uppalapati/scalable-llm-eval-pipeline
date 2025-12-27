from typing import List, Dict, Any
from collections import defaultdict


def aggregate_results(
    test_cases: List[Dict[str, Any]],
    results: List[Dict[str, Any]],
    evaluations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    assert len(test_cases) == len(results) == len(evaluations)

    total = len(evaluations)
    passed = sum(1 for e in evaluations if e["passed"])
    failed = total - passed

    by_category = defaultdict(lambda: {"passed": 0, "failed": 0})

    for tc, ev in zip(test_cases, evaluations):
        category = tc["category"]
        if ev["passed"]:
            by_category[category]["passed"] += 1
        else:
            by_category[category]["failed"] += 1

    return {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": passed / total if total > 0 else 0.0,
        "by_category": dict(by_category),
    }


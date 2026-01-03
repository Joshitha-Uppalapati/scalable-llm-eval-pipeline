from typing import Dict, Any


def run_judge(
    *,
    prompt: str,
    output: str,
    rubric: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    scores = {
        "factual_correctness": 1,
        "completeness": 1,
        "format_compliance": 1,
    }

    return {
        "scores": scores,
        "total": sum(scores.values()),
        "passed": True,
        "explanation": "Stub judge evaluation",
    }


def evaluate_with_judge(
    *,
    prompt: str,
    output: str,
    rubric: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    result = run_judge(
        prompt=prompt,
        output=output,
        rubric=rubric,
    )

    return {
        "passed": result["passed"],
        "reason": result["explanation"],
        "judge_scores": result["scores"],
        "judge_total": result["total"],
    }


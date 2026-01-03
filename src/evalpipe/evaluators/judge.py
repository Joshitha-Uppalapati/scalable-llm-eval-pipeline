from typing import Dict, Any

JUDGE_RUBRIC_V1 = """
You are grading a model response.

Score using this rubric:
- factual_correctness: 0, 1, or 2
- completeness: 0, 1, or 2
- format_compliance: 0 or 1

Return STRICT JSON:
{
  "factual_correctness": int,
  "completeness": int,
  "format_compliance": int,
  "explanation": string
}
"""


def evaluate_with_judge(
    test_case: Dict[str, Any],
    result: Dict[str, Any],
    judge_runner,
) -> Dict[str, Any]:
    output = result.get("provider_output")
    text = getattr(output, "output", None)

    if not text:
        return {
            "passed": False,
            "reason": "Empty output",
        }

    prompt = f"""
{JUDGE_RUBRIC_V1}

TASK PROMPT:
{test_case.get("prompt")}

MODEL RESPONSE:
{text}
"""

    judge_result = judge_runner(prompt)

    try:
        scores = judge_result["parsed"]
    except Exception:
        return {
            "passed": False,
            "reason": "Judge returned invalid response",
        }

    total = (
        scores["factual_correctness"]
        + scores["completeness"]
        + scores["format_compliance"]
    )

    passed = total >= 4

    return {
        "passed": passed,
        "reason": scores["explanation"],
        "judge_scores": scores,
        "judge_rubric_version": "v1",
    }


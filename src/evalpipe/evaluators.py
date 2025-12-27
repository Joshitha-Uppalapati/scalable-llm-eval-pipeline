import re
from typing import Dict, Any


def evaluate_exact_match(expected: str, output: str) -> Dict[str, Any]:
    passed = output == expected
    return {
        "passed": passed,
        "reason": "exact match" if passed else f"expected '{expected}', got '{output}'",
    }


def evaluate_regex(pattern: str, output: str) -> Dict[str, Any]:
    passed = re.match(pattern, output) is not None
    return {
        "passed": passed,
        "reason": "regex matched" if passed else f"output '{output}' did not match regex",
    }


def evaluate_contains(value: str, output: str) -> Dict[str, Any]:
    passed = value.lower() in output.lower()
    return {
        "passed": passed,
        "reason": "substring found" if passed else f"output does not contain '{value}'",
    }


def evaluate(test_case: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    eval_spec = test_case["evaluation"]
    eval_type = eval_spec["type"]
    output = result["output"]

    if eval_type == "exact_match":
        return evaluate_exact_match(test_case.get("expected", ""), output)

    if eval_type == "regex":
        return evaluate_regex(eval_spec["pattern"], output)

    if eval_type == "contains":
        return evaluate_contains(eval_spec["value"], output)

    raise ValueError(f"Unknown evaluation type: {eval_type}")


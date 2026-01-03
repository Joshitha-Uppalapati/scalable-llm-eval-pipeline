from evalpipe.evaluators.exact import exact_match
from evalpipe.evaluators.regex import regex_match
from evalpipe.evaluators.contains import contains_match
from evalpipe.evaluators.numeric import numeric_match
from evalpipe.evaluators.schema import schema_validate
from evalpipe.evaluators.refusal import evaluate_refusal
from evalpipe.evaluators.judge import evaluate_with_judge


def evaluate(test_case, result, judge_runner=None):
    eval_type = test_case["evaluation"]["type"]

    if eval_type == "exact_match":
        return exact_match(test_case, result)

    if eval_type == "regex":
        return regex_match(test_case, result)

    if eval_type == "contains":
        return contains_match(test_case, result)

    if eval_type == "numeric":
        return numeric_match(test_case, result)

    if eval_type == "schema":
        return schema_validate(test_case, result)

    if eval_type == "llm_judge":
        if not judge_runner:
            return {
                "passed": False,
                "reason": "Judge runner not provided",
            }
        return evaluate_with_judge(test_case, result, judge_runner)

    return {
        "passed": False,
        "reason": f"Unknown evaluation type: {eval_type}",
    }


from evalpipe.evaluators.exact import exact_match
from evalpipe.evaluators.regex import regex_match
from evalpipe.evaluators.contains import contains
from evalpipe.evaluators.numeric import numeric_tolerance
from evalpipe.evaluators.schema import schema_validate


EVALUATORS = {
    "exact_match": exact_match,
    "regex": regex_match,
    "contains": contains,
    "numeric": numeric_tolerance,
    "schema": schema_validate,
}


def evaluate(test_case: dict, result: dict) -> dict:
    spec = test_case["evaluation"]
    eval_type = spec["type"]

    if eval_type not in EVALUATORS:
        raise ValueError(f"Unsupported evaluation type: {eval_type}")

    return EVALUATORS[eval_type](test_case, result)

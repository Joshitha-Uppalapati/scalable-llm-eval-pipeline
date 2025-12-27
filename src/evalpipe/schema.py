from typing import Dict, Any


class SchemaError(ValueError):
    pass


SUPPORTED_EVAL_TYPES = {"exact_match", "regex", "contains"}


def validate_test_case(obj: Dict[str, Any]) -> None:
    if not isinstance(obj, dict):
        raise SchemaError("Test case must be a JSON object")

    # Required top-level fields
    for field in ("id", "category", "prompt", "evaluation"):
        if field not in obj:
            raise SchemaError(f"Missing required field: '{field}'")

    if not isinstance(obj["id"], str):
        raise SchemaError("'id' must be a string")

    if not isinstance(obj["category"], str):
        raise SchemaError("'category' must be a string")

    if not isinstance(obj["prompt"], str):
        raise SchemaError("'prompt' must be a string")

    evaluation = obj["evaluation"]
    if not isinstance(evaluation, dict):
        raise SchemaError("'evaluation' must be an object")

    eval_type = evaluation.get("type")
    if eval_type not in SUPPORTED_EVAL_TYPES:
        raise SchemaError(f"Unsupported evaluation type: {eval_type}")

    if eval_type == "regex" and "pattern" not in evaluation:
        raise SchemaError("Regex evaluation requires 'pattern'")

    if eval_type == "contains" and "value" not in evaluation:
        raise SchemaError("Contains evaluation requires 'value'")

    if "expected" in obj and not isinstance(obj["expected"], str):
        raise SchemaError("'expected' must be a string if provided")

    if "metadata" in obj and not isinstance(obj["metadata"], dict):
        raise SchemaError("'metadata' must be an object if provided")


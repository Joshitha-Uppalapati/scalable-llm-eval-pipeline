import json
from typing import Dict, Any

from evalpipe.evaluators.refusal import evaluate_refusal


def schema_validate(test_case: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    output = result.get("provider_output")
    text = getattr(output, "output", None)

    if text is None:
        return {
            "passed": False,
            "reason": "No output to validate against schema",
        }

    try:
        parsed = json.loads(text)
    except Exception as e:
        return {
            "passed": False,
            "reason": f"Invalid JSON: {e}",
        }

    schema = test_case.get("evaluation", {}).get("schema")
    if not schema:
        return {
            "passed": True,
            "reason": "No schema provided",
        }

    required = schema.get("required", [])
    for field in required:
        if field not in parsed:
            return {
                "passed": False,
                "reason": f"Missing required field: {field}",
            }

    refusal_check = evaluate_refusal(result)
    if not refusal_check["passed"]:
        return refusal_check

    return {
        "passed": True,
        "reason": "Schema validation passed",
    }


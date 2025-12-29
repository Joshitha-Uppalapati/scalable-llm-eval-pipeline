import json


def schema_validate(test_case: dict, result: dict) -> dict:
    schema = test_case["evaluation"]["schema"]
    output = result.get("output")

    try:
        parsed = json.loads(output)
    except Exception as e:
        return {"passed": False, "reason": f"Invalid JSON: {e}"}

    for key, expected_type in schema.items():
        if key not in parsed:
            return {"passed": False, "reason": f"Missing key: {key}"}
        if not isinstance(parsed[key], expected_type):
            return {
                "passed": False,
                "reason": f"Key '{key}' expected {expected_type}, got {type(parsed[key])}",
            }

    return {"passed": True, "reason": None}


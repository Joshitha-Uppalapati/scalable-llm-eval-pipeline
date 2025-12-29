def contains(test_case: dict, result: dict) -> dict:
    value = test_case["evaluation"]["value"]
    output = result.get("output", "")

    passed = value.lower() in output.lower()

    return {
        "passed": passed,
        "reason": None if passed else f"'{value}' not found in output",
    }

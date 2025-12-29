def numeric_tolerance(test_case: dict, result: dict) -> dict:
    expected = float(test_case["expected"])
    tolerance = float(test_case["evaluation"]["tolerance"])
    output = float(result.get("output"))

    diff = abs(output - expected)
    passed = diff <= tolerance

    return {
        "passed": passed,
        "reason": None if passed else f"Difference {diff} exceeds tolerance {tolerance}",
    }

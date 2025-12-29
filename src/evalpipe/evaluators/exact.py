def exact_match(test_case: dict, result: dict) -> dict:
    expected = test_case.get("expected")
    output = result.get("output")

    passed = output == expected

    return {
        "passed": passed,
        "reason": None if passed else f"Expected '{expected}', got '{output}'",
    }

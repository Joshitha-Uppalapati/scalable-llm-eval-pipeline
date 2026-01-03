def contains_match(test_case, result):
    expected = test_case["evaluation"]["value"]

    output = result.get("provider_output")
    text = getattr(output, "output", None)

    if not text:
        return {
            "passed": False,
            "reason": "Empty output",
        }

    passed = expected in text

    return {
        "passed": passed,
        "reason": f"Expected '{expected}' in output" if not passed else "OK",
    }


def numeric_match(test_case, result):
    eval_cfg = test_case["evaluation"]
    expected = float(eval_cfg["value"])
    tolerance = float(eval_cfg.get("tolerance", 0))

    output = result.get("provider_output")
    text = getattr(output, "output", None)

    if text is None:
        return {
            "passed": False,
            "reason": "Empty output",
        }

    try:
        actual = float(text)
    except ValueError:
        return {
            "passed": False,
            "reason": f"Non-numeric output: {text}",
        }

    passed = abs(actual - expected) <= tolerance

    return {
        "passed": passed,
        "reason": (
            f"Expected {expected} ± {tolerance}, got {actual}"
            if not passed
            else "OK"
        ),
    }


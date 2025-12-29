import re


def regex_match(test_case: dict, result: dict) -> dict:
    pattern = test_case["evaluation"]["pattern"]
    output = result.get("output", "")

    passed = re.match(pattern, output) is not None

    return {
        "passed": passed,
        "reason": None if passed else f"Output '{output}' does not match /{pattern}/",
    }

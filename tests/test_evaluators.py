from evalpipe.evaluators import evaluate


def test_exact_match_pass():
    test_case = {
        "evaluation": {"type": "exact_match"},
        "expected": "408",
    }
    result = {"output": "408"}

    outcome = evaluate(test_case, result)
    assert outcome["passed"] is True


def test_exact_match_fail():
    test_case = {
        "evaluation": {"type": "exact_match"},
        "expected": "408",
    }
    result = {"output": "409"}

    outcome = evaluate(test_case, result)
    assert outcome["passed"] is False


def test_regex_pass():
    test_case = {
        "evaluation": {"type": "regex", "pattern": "^[0-9]+$"},
    }
    result = {"output": "7"}

    outcome = evaluate(test_case, result)
    assert outcome["passed"] is True


def test_contains_fail():
    test_case = {
        "evaluation": {"type": "contains", "value": "red"},
    }
    result = {"output": "blue"}

    outcome = evaluate(test_case, result)
    assert outcome["passed"] is False


from evalpipe.aggregate import aggregate_results


def test_aggregate_basic():
    test_cases = [
        {"id": "t1", "category": "math"},
        {"id": "t2", "category": "math"},
        {"id": "t3", "category": "format"},
    ]

    results = [{}, {}, {}]  # not used directly
    evaluations = [
        {"passed": True},
        {"passed": False},
        {"passed": True},
    ]

    summary = aggregate_results(test_cases, results, evaluations)

    assert summary["total_tests"] == 3
    assert summary["passed"] == 2
    assert summary["failed"] == 1
    assert summary["pass_rate"] == 2 / 3

    assert summary["by_category"]["math"]["passed"] == 1
    assert summary["by_category"]["math"]["failed"] == 1
    assert summary["by_category"]["format"]["passed"] == 1


from evalpipe.runner import dummy_infer


def test_dummy_infer_math():
    test_case = {
        "id": "math_001",
        "prompt": "What is 17 * 24?",
    }

    result = dummy_infer(test_case)

    assert result["output"] == "408"
    assert result["model"] == "dummy-v0"
    assert "timestamp" in result


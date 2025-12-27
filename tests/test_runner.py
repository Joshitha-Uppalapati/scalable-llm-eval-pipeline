from evalpipe.runner import run


def test_dummy_infer_math():
    test_case = {
        "id": "math_001",
        "prompt": "What is 17 * 24?",
    }

    result = run(test_case)

    assert result.provider_output.output == "408"
    assert result.provider_output.model == "dummy-v0"
    assert result.run_id == "math_001"
    assert result.provider == "dummy"

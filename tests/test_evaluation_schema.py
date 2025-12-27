from evalpipe.schemas.evaluation_schema import EvaluationResult, ProviderOutput


def test_evaluation_schema_instantiation():
    provider_out = ProviderOutput(
        output="2",
        model="gpt-test",
        latency_ms=12,
        prompt_tokens=5,
        completion_tokens=1,
    )

    record = EvaluationResult(
        schema_version="v1",
        run_id="run-123",
        provider="openai",
        prompt="1+1",
        provider_output=provider_out,
        metrics={"accuracy": 1.0},
        timestamp=EvaluationResult.now_iso(),
    )

    assert record.provider_output.output == "2"
    assert record.metrics["accuracy"] == 1.0

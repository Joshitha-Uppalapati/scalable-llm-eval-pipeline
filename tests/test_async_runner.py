import evalpipe.runner as runner


def test_async_runner_preserves_order(monkeypatch):
    async def fake_infer(prompt: str) -> str:
        return prompt

    monkeypatch.setattr(runner, "dummy_infer", fake_infer)

    test_cases = [{"id": "1"}, {"id": "2"}, {"id": "3"}]

    results, errors = runner.run_inference(
        suite_id="s",
        test_cases=test_cases,
        model="m",
        rendered_prompt="X",
        max_concurrency=3,
    )

    assert [r["id"] for r in results] == ["1", "2", "3"]
    assert errors == []

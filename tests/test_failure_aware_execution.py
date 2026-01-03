import asyncio
import evalpipe.runner as runner


def test_one_bad_row_does_not_kill_run(monkeypatch):
    async def fake_infer(prompt: str) -> str:
        if "FAIL_ME" in prompt:
            raise RuntimeError("boom")
        return "OK"

    monkeypatch.setattr(runner, "dummy_infer", fake_infer)

    test_cases = [
        {"id": "a"},
        {"id": "b"},
        {"id": "c"},
    ]

    results, errors = runner.run_inference(
        suite_id="s1",
        test_cases=test_cases,
        model="m1",
        rendered_prompt="FAIL_ME",
        max_concurrency=3,
    )

    assert len(results) == 3
    assert len(errors) == 3
    assert all(r.get("error") for r in results)


def test_timeout_is_captured(monkeypatch):
    async def slow_infer(prompt: str) -> str:
        await asyncio.sleep(0.05)
        return "OK"

    monkeypatch.setattr(runner, "dummy_infer", slow_infer)
    monkeypatch.setattr(runner, "TIMEOUT_SECONDS", 0.001)

    test_cases = [{"id": "t1"}]

    results, errors = runner.run_inference(
        suite_id="s1",
        test_cases=test_cases,
        model="m1",
        rendered_prompt="anything",
        max_concurrency=1,
    )

    assert len(results) == 1
    assert len(errors) == 1
    assert results[0].get("error_type") == "timeout"

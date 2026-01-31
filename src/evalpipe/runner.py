from typing import Dict, Any, Tuple, Iterable, List, Optional
from datetime import datetime, timezone
import time
import json
import asyncio

from evalpipe.schemas.evaluation_schema import EvaluationResult, ProviderOutput
from evalpipe.cache.simple_cache import (
    make_cache_key,
    load_from_cache,
    save_to_cache,
)

DEFAULT_PARAMS = {
    "temperature": 0.0,
    "max_tokens": 64,
}

MAX_RETRIES = 2
TIMEOUT_SECONDS = 10


async def dummy_infer(prompt: str) -> str:
    await asyncio.sleep(0)
    p = prompt.lower()

    if "17 * 24" in p:
        return "408"
    if "100 - 37" in p:
        return "63"
    if "sky" in p:
        return "YES"
    if "days are in a week" in p:
        return "7"
    if "primary color" in p:
        return "red"
    if "gravity" in p:
        return "Gravity is a force."
    if "break into a house" in p:
        return "I cannot help with that."
    if "youngest" in p:
        return "Charlie"
    if "even number" in p:
        return "Yes"
    if "divide" in p and "zero" in p:
        return "It is undefined."

    return "UNKNOWN"


def _error_result(
    *,
    test_id: str,
    rendered_prompt: str,
    model: str,
    start: float,
    error_type: str,
    error_message: str,
    attempts: int,
) -> Dict[str, Any]:
    latency_ms = int((time.time() - start) * 1000)
    return {
        "id": test_id,
        "prompt": rendered_prompt,
        "output": None,
        "model": model,
        "latency_ms": latency_ms,
        "prompt_tokens": None,
        "completion_tokens": None,
        "cache_hit": False,
        "error": error_message,
        "error_type": error_type,
        "attempts": attempts,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


async def run_single(
    *,
    suite_id: str,
    test_case: Dict[str, Any],
    model: str,
    rendered_prompt: str,
    params: Dict[str, Any],
) -> Dict[str, Any]:
    test_id = test_case["id"]

    cache_key = make_cache_key(
        suite_id=suite_id,
        test_id=test_id,
        model=model,
        prompt=rendered_prompt,
        params=params,
    )

    cached = load_from_cache(cache_key)
    if cached:
        cached["cache_hit"] = True
        return cached

    start = time.time()
    last_error_type: Optional[str] = None
    last_error_message: Optional[str] = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            output = await asyncio.wait_for(
                dummy_infer(rendered_prompt),
                timeout=TIMEOUT_SECONDS,
            )

            latency_ms = int((time.time() - start) * 1000)
            result = {
                "id": test_id,
                "prompt": rendered_prompt,
                "output": output,
                "model": model,
                "latency_ms": latency_ms,
                "prompt_tokens": None,
                "completion_tokens": None,
                "cache_hit": False,
                "attempts": attempt + 1,
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            }

            save_to_cache(cache_key, result)
            return result

        except asyncio.TimeoutError:
            last_error_type = "timeout"
            last_error_message = "timeout"
        except Exception as e:
            last_error_type = type(e).__name__
            last_error_message = str(e) or "error"

        if attempt < MAX_RETRIES:
            await asyncio.sleep(0.05 * (2**attempt))

    return _error_result(
        test_id=test_id,
        rendered_prompt=rendered_prompt,
        model=model,
        start=start,
        error_type=last_error_type or "error",
        error_message=last_error_message or "error",
        attempts=MAX_RETRIES + 1,
    )


async def run_inference_async(
    *,
    suite_id: str,
    test_cases: Iterable[Dict[str, Any]],
    model: str,
    rendered_prompt: str,
    params: Dict[str, Any],
    max_concurrency: int,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    semaphore = asyncio.Semaphore(max_concurrency)

    async def guarded(tc: Dict[str, Any]) -> Dict[str, Any]:
        async with semaphore:
            start = time.time()
            try:
                return await run_single(
                    suite_id=suite_id,
                    test_case=tc,
                    model=model,
                    rendered_prompt=rendered_prompt,
                    params=params,
                )
            except Exception as e:
                return _error_result(
                    test_id=tc.get("id", "unknown"),
                    rendered_prompt=rendered_prompt,
                    model=model,
                    start=start,
                    error_type=type(e).__name__,
                    error_message=str(e) or "error",
                    attempts=0,
                )

    tasks = [guarded(tc) for tc in test_cases]
    gathered = await asyncio.gather(*tasks, return_exceptions=False)

    results: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    for res in gathered:
        if res.get("error"):
            errors.append(res)
        results.append(res)

    return results, errors


def run_inference(
    *,
    suite_id: str,
    test_cases: Iterable[Dict[str, Any]],
    model: str,
    rendered_prompt: str,
    params: Dict[str, Any] | None = None,
    max_concurrency: int = 10,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    params = params or DEFAULT_PARAMS

    return asyncio.run(
        run_inference_async(
            suite_id=suite_id,
            test_cases=test_cases,
            model=model,
            rendered_prompt=rendered_prompt,
            params=params,
            max_concurrency=max_concurrency,
        )
    )


def run(test_case: Dict[str, Any]) -> EvaluationResult:
    start = time.time()
    output = asyncio.run(dummy_infer(test_case["prompt"]))
    latency_ms = int((time.time() - start) * 1000)

    provider_output = ProviderOutput(
        output=output,
        model="dummy-v0",
        latency_ms=latency_ms,
        prompt_tokens=None,
        completion_tokens=None,
    )

    return EvaluationResult(
        schema_version="v1",
        run_id=test_case["id"],
        provider="dummy",
        prompt=test_case["prompt"],
        provider_output=provider_output,
        metrics={},
        timestamp=EvaluationResult.now_iso(),
    )


def _yield_jsonl(path: str):
    with open(path, "r") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


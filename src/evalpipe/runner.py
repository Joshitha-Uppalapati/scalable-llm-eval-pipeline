from typing import Dict, Any, List, Tuple
from datetime import datetime
import time

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


def dummy_infer(prompt: str) -> str:
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


def run_single(
    *,
    suite_id: str,
    test_case: Dict[str, Any],
    model: str,
    rendered_prompt: str,
    params: Dict[str, Any],
) -> Dict[str, Any]:
    cache_key = make_cache_key(
        suite_id=suite_id,
        test_id=test_case["id"],
        model=model,
        prompt=rendered_prompt,
        params=params,
    )

    cached = load_from_cache(cache_key)
    if cached:
        cached["cache_hit"] = True
        return cached

    start = time.time()
    last_error = None

    for _ in range(MAX_RETRIES + 1):
        try:
            output = dummy_infer(rendered_prompt)
            latency_ms = int((time.time() - start) * 1000)

            result = {
                "id": test_case["id"],
                "prompt": rendered_prompt,
                "output": output,
                "model": model,
                "latency_ms": latency_ms,
                "prompt_tokens": None,
                "completion_tokens": None,
                "cache_hit": False,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

            save_to_cache(cache_key, result)
            return result

        except Exception as e:
            last_error = str(e)
            if time.time() - start > TIMEOUT_SECONDS:
                break

    latency_ms = int((time.time() - start) * 1000)

    return {
        "id": test_case["id"],
        "prompt": rendered_prompt,
        "output": None,
        "model": model,
        "latency_ms": latency_ms,
        "prompt_tokens": None,
        "completion_tokens": None,
        "cache_hit": False,
        "error": last_error or "timeout",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def run_inference(
    *,
    suite_id: str,
    test_cases: List[Dict[str, Any]],
    model: str,
    rendered_prompt: str,
    params: Dict[str, Any] | None = None,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    params = params or DEFAULT_PARAMS

    results: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    for tc in test_cases:
        res = run_single(
            suite_id=suite_id,
            test_case=tc,
            model=model,
            rendered_prompt=rendered_prompt,
            params=params,
        )

        if res.get("error"):
            errors.append(res)

        results.append(res)

    return results, errors


def run(test_case: Dict[str, Any]) -> EvaluationResult:
    start = time.time()
    output = dummy_infer(test_case["prompt"])
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


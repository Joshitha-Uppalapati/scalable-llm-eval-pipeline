from typing import Dict, Any, List, Tuple
from datetime import datetime
from evalpipe.schemas.evaluation_schema import EvaluationResult, ProviderOutput


def dummy_infer(test_case: Dict[str, Any]) -> Dict[str, Any]:
    prompt = test_case["prompt"]

    if "17 * 24" in prompt:
        output = "408"
    elif "100 - 37" in prompt:
        output = "63"
    elif "sky" in prompt.lower():
        output = "YES"
    elif "days are in a week" in prompt.lower():
        output = "7"
    elif "primary color" in prompt.lower():
        output = "red"
    elif "gravity" in prompt.lower():
        output = "Gravity is a force."
    elif "break into a house" in prompt.lower():
        output = "I cannot help with that."
    elif "youngest" in prompt.lower():
        output = "Charlie"
    elif "0 an even number" in prompt.lower():
        output = "Yes"
    elif "divide" in prompt.lower() and "zero" in prompt.lower():
        output = "It is undefined."
    else:
        output = "UNKNOWN"

    return {
        "id": test_case["id"],
        "prompt": prompt,
        "output": output,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "model": "dummy-v0",
    }


def run(test_case: Dict[str, Any]) -> EvaluationResult:
    raw = dummy_infer(test_case)

    provider_output = ProviderOutput(
        output=raw["output"],
        model=raw["model"],
        latency_ms=0,
        prompt_tokens=None,
        completion_tokens=None,
    )

    return EvaluationResult(
        schema_version="v1",
        run_id=raw["id"],
        provider="dummy",
        prompt=raw["prompt"],
        provider_output=provider_output,
        metrics={},
        timestamp=EvaluationResult.now_iso(),
    )


def run_inference(
    test_cases: List[Dict[str, Any]],
    model: str,
    rendered_prompt: str,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[int], Dict[str, int]]:
    results: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    latencies: List[int] = []

    token_usage = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
    }

    for tc in test_cases:
        try:
            raw = dummy_infer(tc)
            results.append(raw)
            latencies.append(0)
        except Exception as e:
            errors.append(
                {
                    "id": tc.get("id"),
                    "error": str(e),
                }
            )
            results.append(
                {
                    "id": tc.get("id"),
                    "prompt": tc.get("prompt"),
                    "output": None,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "model": model,
                }
            )

    return results, errors, latencies, token_usage


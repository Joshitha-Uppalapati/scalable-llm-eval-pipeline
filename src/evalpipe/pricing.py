from typing import Dict

MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "dummy-v0": {
        "prompt_per_1k": 0.0,
        "completion_per_1k": 0.0,
    },
    "gpt-4o-mini": {
        "prompt_per_1k": 0.00015,
        "completion_per_1k": 0.0006,
    },
    "gpt-4o": {
        "prompt_per_1k": 0.005,
        "completion_per_1k": 0.015,
    },
}


def estimate_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> float:
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        return 0.0

    prompt_cost = (prompt_tokens / 1000) * pricing["prompt_per_1k"]
    completion_cost = (completion_tokens / 1000) * pricing["completion_per_1k"]

    return round(prompt_cost + completion_cost, 6)


MODEL_PRICING = {
    "dummy-v0": {
        "prompt_per_1k": 0.0,
        "completion_per_1k": 0.0,
    },
}


def estimate_cost(
    model: str,
    prompt_tokens: int | None,
    completion_tokens: int | None,
) -> float:
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        return 0.0

    pt = prompt_tokens or 0
    ct = completion_tokens or 0

    return (
        (pt / 1000) * pricing["prompt_per_1k"]
        + (ct / 1000) * pricing["completion_per_1k"]
    )


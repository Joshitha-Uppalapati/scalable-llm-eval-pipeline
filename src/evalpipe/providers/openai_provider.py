def infer(prompt: str) -> dict:
    """
    Returns:
    {
        "output": str,
        "model": str,
        "latency_ms": int,
        "prompt_tokens": int | None,
        "completion_tokens": int | None
    }
    """
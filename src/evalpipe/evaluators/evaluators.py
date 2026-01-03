from typing import Dict, Any, List

from evalpipe.evaluators.registry import EVALUATOR_REGISTRY


def evaluate_all(
    *,
    prompt: str,
    output: str,
    metadata: Dict[str, Any],
    enabled: List[str] | None = None,
) -> Dict[str, Any]:
    results: Dict[str, Any] = {}

    evaluators = (
        {k: v for k, v in EVALUATOR_REGISTRY.items() if k in enabled}
        if enabled
        else EVALUATOR_REGISTRY
    )

    for name, evaluator in evaluators.items():
        results[name] = evaluator.evaluate(
            prompt=prompt,
            output=output,
            metadata=metadata,
        )

    return results

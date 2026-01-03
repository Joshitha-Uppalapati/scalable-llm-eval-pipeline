from typing import Dict, Callable, Protocol, Any


class Evaluator(Protocol):
    name: str

    def evaluate(self, *, prompt: str, output: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        ...


EVALUATOR_REGISTRY: Dict[str, Evaluator] = {}


def register_evaluator(name: str):
    def decorator(cls):
        if not hasattr(cls, "evaluate"):
            raise TypeError(f"Evaluator '{name}' must implement evaluate()")

        instance = cls()
        if not callable(getattr(instance, "evaluate", None)):
            raise TypeError(f"Evaluator '{name}' evaluate must be callable")

        instance.name = name
        EVALUATOR_REGISTRY[name] = instance
        return cls

    return decorator

from evalpipe.evaluators.registry import EVALUATOR_REGISTRY, register_evaluator


def test_registry_registers_evaluator():
    @register_evaluator("dummy_test")
    class DummyEval:
        def evaluate(self, *, prompt, output, metadata):
            return {"ok": True}

    assert "dummy_test" in EVALUATOR_REGISTRY
    assert EVALUATOR_REGISTRY["dummy_test"].evaluate(
        prompt="", output="", metadata={}
    ) == {"ok": True}

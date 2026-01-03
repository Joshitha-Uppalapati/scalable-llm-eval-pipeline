import json
from evalpipe.runner import _yield_jsonl


def test_large_input_streaming(tmp_path):
    path = tmp_path / "big.jsonl"

    with open(path, "w") as f:
        for i in range(10000):
            f.write(json.dumps({"i": i}) + "\n")

    count = 0
    for _ in _yield_jsonl(str(path)):
        count += 1

    assert count == 10000

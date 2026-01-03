import json
from evalpipe.runner import _yield_jsonl


def test_yield_jsonl_streams(tmp_path):
    path = tmp_path / "data.jsonl"
    rows = [{"a": 1}, {"a": 2}, {"a": 3}]

    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    out = list(_yield_jsonl(str(path)))
    assert out == rows

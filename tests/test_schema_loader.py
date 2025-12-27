import json
from pathlib import Path

import pytest

from evalpipe.loader import load_suite
from evalpipe.schema import SchemaError


def write_jsonl(tmp_path: Path, rows):
    path = tmp_path / "suite.jsonl"
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    return path


def test_valid_exact_match(tmp_path):
    path = write_jsonl(
        tmp_path,
        [
            {
                "id": "t1",
                "category": "math",
                "prompt": "2 + 2",
                "expected": "4",
                "evaluation": {"type": "exact_match"},
            }
        ],
    )
    suite = load_suite(path)
    assert len(suite) == 1


def test_missing_required_field(tmp_path):
    path = write_jsonl(
        tmp_path,
        [
            {
                "id": "t1",
                "prompt": "2 + 2",
                "evaluation": {"type": "exact_match"},
            }
        ],
    )
    with pytest.raises(SchemaError):
        load_suite(path)


def test_invalid_eval_type(tmp_path):
    path = write_jsonl(
        tmp_path,
        [
            {
                "id": "t1",
                "category": "math",
                "prompt": "2 + 2",
                "evaluation": {"type": "fuzzy_magic"},
            }
        ],
    )
    with pytest.raises(SchemaError):
        load_suite(path)

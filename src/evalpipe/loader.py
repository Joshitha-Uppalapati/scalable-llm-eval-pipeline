import json
from pathlib import Path
from typing import List, Dict, Any

from .schema import validate_test_case, SchemaError


def load_suite(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)

    test_cases: List[Dict[str, Any]] = []

    with path.open() as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise SchemaError(f"Invalid JSON on line {line_no}: {e}") from e

            try:
                validate_test_case(obj)
            except SchemaError as e:
                raise SchemaError(f"Schema error on line {line_no}: {e}") from e

            test_cases.append(obj)

    return test_cases

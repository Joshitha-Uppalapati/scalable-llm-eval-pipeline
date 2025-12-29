from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import json


def _json_safe(obj):
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return obj


def _write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    with path.open("w") as f:
        for row in rows:
            safe_row = {k: _json_safe(v) for k, v in row.items()}
            f.write(json.dumps(safe_row) + "\n")


def write_run_artifacts(
    run_dir: Path,
    test_cases: List[Dict[str, Any]],
    results: List[Dict[str, Any]],
    evaluations: List[Dict[str, Any]],
    summary: Dict[str, Any],
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)

    # Core artifacts
    _write_jsonl(run_dir / "test_cases.jsonl", test_cases)
    _write_jsonl(run_dir / "results.jsonl", results)
    _write_jsonl(run_dir / "evaluations.jsonl", evaluations)

    with (run_dir / "summary.json").open("w") as f:
        json.dump(summary, f, indent=2)

    # Meta artifact
    meta = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "artifacts": {
            "test_cases": "test_cases.jsonl",
            "results": "results.jsonl",
            "evaluations": "evaluations.jsonl",
            "summary": "summary.json",
        },
        "schema_version": "v1",
    }

    with (run_dir / "meta.json").open("w") as f:
        json.dump(meta, f, indent=2)


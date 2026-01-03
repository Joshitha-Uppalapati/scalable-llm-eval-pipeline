from pathlib import Path
import json
from datetime import datetime, UTC
from typing import Dict, Any, Optional, Iterable


def _write_json(path: Path, obj: Any) -> None:
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


def _write_jsonl(path: Path, rows: Iterable[Any]) -> None:
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def write_run_artifacts(
    *,
    run_dir: Path,
    results: Optional[Iterable[Any]] = None,
    meta: Optional[Dict[str, Any]] = None,
    test_cases: Optional[Iterable[Any]] = None,
    evaluations: Optional[Iterable[Any]] = None,
    summary: Any = None,
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)

    meta_out: Dict[str, Any] = meta.copy() if meta else {}
    meta_out["created_at"] = datetime.now(UTC).isoformat()
    _write_json(run_dir / "meta.json", meta_out)

    if test_cases is not None:
        _write_jsonl(run_dir / "test_cases.jsonl", test_cases)

    if results is not None:
        _write_jsonl(run_dir / "results.jsonl", results)

    if evaluations is not None:
        _write_jsonl(run_dir / "evaluations.jsonl", evaluations)

    if summary is not None:
        _write_json(run_dir / "summary.json", summary)

import json
from pathlib import Path
from typing import Iterable, Any
from dataclasses import asdict, is_dataclass

def _serialize(obj: Any) -> Any:
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(v) for v in obj]
    return obj

def _write_jsonl(path: Path, rows: Iterable[Any]) -> None:
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(_serialize(row)) + "\n")

def write_run_artifacts(
    run_dir: Path,
    test_cases=None,
    results=None,
    evaluations=None,
    summary=None,
    meta=None,
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)

    if test_cases is not None:
        _write_jsonl(run_dir / "test_cases.jsonl", test_cases)

    if results is not None:
        _write_jsonl(run_dir / "results.jsonl", results)

    if evaluations is not None:
        _write_jsonl(run_dir / "evaluations.jsonl", evaluations)

    if summary is not None:
        with open(run_dir / "summary.json", "w") as f:
            json.dump(_serialize(summary), f, indent=2)

    meta_out = meta or {}
    with open(run_dir / "meta.json", "w") as f:
        json.dump(_serialize(meta_out), f, indent=2)


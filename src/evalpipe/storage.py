import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


def write_run_artifacts(
    run_dir: Path,
    test_cases: List[Dict[str, Any]],
    results: List[Dict[str, Any]],
    evaluations: List[Dict[str, Any]],
    summary: Dict[str, Any],
) -> None:
    run_dir.mkdir(parents=True, exist_ok=False)

    def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
        with path.open("w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

    write_jsonl(run_dir / "test_cases.jsonl", test_cases)
    write_jsonl(run_dir / "results.jsonl", results)
    write_jsonl(run_dir / "evaluations.jsonl", evaluations)

    with (run_dir / "summary.json").open("w") as f:
        json.dump(summary, f, indent=2)

    with (run_dir / "meta.json").open("w") as f:
        json.dump(
            {
                "created_at": datetime.utcnow().isoformat() + "Z",
            },
            f,
            indent=2,
        )


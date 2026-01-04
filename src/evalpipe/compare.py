import json
from pathlib import Path
from typing import Dict, Any


def load_run(run_dir: Path) -> Dict[str, Any]:
    with open(run_dir / "meta.json") as f:
        meta = json.load(f)

    with open(run_dir / "summary.json") as f:
        summary = json.load(f)

    return {
        "run_id": summary.get("run_id"),
        "prompt_hash": meta.get("prompt_hash"),
        "summary": summary,
    }


def compare_runs(current_run: Path, baseline_run: Path) -> Dict[str, Any]:
    current = load_run(current_run)
    baseline = load_run(baseline_run)

    current_pass = current["summary"]["pass_rate"]
    baseline_pass = baseline["summary"]["pass_rate"]

    return {
        "current_run": current["run_id"],
        "baseline_run": baseline["run_id"],
        "prompt_hash_match": current["prompt_hash"] == baseline["prompt_hash"],
        "pass_rate": {
            "current": current_pass,
            "baseline": baseline_pass,
            "delta": current_pass - baseline_pass,
        },
    }


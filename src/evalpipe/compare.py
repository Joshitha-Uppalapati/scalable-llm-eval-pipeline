import json
from pathlib import Path
from typing import Dict, Any, List


def load_summary(run_dir: Path) -> Dict[str, Any]:
    with (run_dir / "summary.json").open() as f:
        return json.load(f)


def compare_runs(prev_run: Path, curr_run: Path) -> List[str]:
    prev = load_summary(prev_run)
    curr = load_summary(curr_run)

    regressions = []

    # pass/fail regressions
    prev_pass = prev["pass_rate"]
    curr_pass = curr["pass_rate"]
    if curr_pass < prev_pass:
        regressions.append(
            f"Pass rate dropped from {prev_pass:.2%} to {curr_pass:.2%}"
        )

    # latency delta
    prev_lat = prev.get("latency", {}).get("avg_ms")
    curr_lat = curr.get("latency", {}).get("avg_ms")
    if prev_lat and curr_lat and curr_lat > prev_lat:
        regressions.append(
            f"Average latency increased from {prev_lat}ms to {curr_lat}ms"
        )

    # cost delta
    prev_cost = prev.get("estimated_usd_cost", 0.0)
    curr_cost = curr.get("estimated_usd_cost", 0.0)
    if curr_cost > prev_cost:
        regressions.append(
            f"Estimated cost increased from ${prev_cost} to ${curr_cost}"
        )

    return regressions


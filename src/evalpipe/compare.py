from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_eval_map(run_dir: Path) -> Dict[str, bool]:
    eval_path = run_dir / "evaluations.jsonl"
    m: Dict[str, bool] = {}
    if not eval_path.exists():
        return m
    with eval_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            tid = obj.get("id")
            if isinstance(tid, str):
                m[tid] = bool(obj.get("passed", False))
    return m


def _as_summary(x: Union[Dict[str, Any], str, Path]) -> Tuple[Dict[str, Any], Optional[Path]]:
    if isinstance(x, dict):
        return x, None
    run_dir = Path(x)
    summary_path = run_dir / "summary.json"
    return _load_json(summary_path), run_dir


def compare_runs(
    baseline: Union[Dict[str, Any], str, Path],
    current: Union[Dict[str, Any], str, Path],
) -> Dict[str, Any]:
    base_summary, base_dir = _as_summary(baseline)
    cur_summary, cur_dir = _as_summary(current)

    base_pass = float(base_summary.get("pass_rate", 0.0))
    cur_pass = float(cur_summary.get("pass_rate", 0.0))

    base_cost = float(base_summary.get("estimated_cost", base_summary.get("cost_breakdown", {}).get("total_usd", 0.0)) or 0.0)
    cur_cost = float(cur_summary.get("estimated_cost", cur_summary.get("cost_breakdown", {}).get("total_usd", 0.0)) or 0.0)

    base_lat = float(base_summary.get("avg_latency_ms", 0.0) or 0.0)
    cur_lat = float(cur_summary.get("avg_latency_ms", 0.0) or 0.0)

    regressions = []
    improvements = []

    if base_dir is not None and cur_dir is not None:
        base_map = _load_eval_map(base_dir)
        cur_map = _load_eval_map(cur_dir)
        all_ids = set(base_map.keys()) | set(cur_map.keys())

        for tid in sorted(all_ids):
            b = base_map.get(tid, False)
            c = cur_map.get(tid, False)
            if b and not c:
                regressions.append(tid)
            elif (not b) and c:
                improvements.append(tid)

    return {
        "metrics": {
            "pass_rate_delta": cur_pass - base_pass,
            "estimated_cost_delta": cur_cost - base_cost,
            "latency_delta_ms": cur_lat - base_lat,
        },
        "regressions": regressions,
        "improvements": improvements,
        "baseline": {
            "pass_rate": base_pass,
            "estimated_cost": base_cost,
            "avg_latency_ms": base_lat,
        },
        "current": {
            "pass_rate": cur_pass,
            "estimated_cost": cur_cost,
            "avg_latency_ms": cur_lat,
        },
    }


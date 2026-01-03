from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _as_run(b: Union[Path, Dict[str, Any]], c: Union[Path, Dict[str, Any]]) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    if isinstance(b, Path) and isinstance(c, Path):
        bsum = _load_json(b / "summary.json")
        csum = _load_json(c / "summary.json")
        bev = _load_jsonl(b / "evaluations.jsonl")
        cev = _load_jsonl(c / "evaluations.jsonl")
        return bsum, csum, bev, cev

    bsum = b if isinstance(b, dict) else _load_json(Path(b))
    csum = c if isinstance(c, dict) else _load_json(Path(c))
    return bsum, csum, [], []


def _index_by_id(evals: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for e in evals:
        tid = e.get("id")
        if tid:
            out[tid] = e
    return out


def _get_tokens(summary: Dict[str, Any], role: str) -> Tuple[int, int]:
    tokens = summary.get("tokens") or {}
    bucket = tokens.get(role) or {}
    pt = int(bucket.get("prompt") or 0)
    ct = int(bucket.get("completion") or 0)
    return pt, ct


def compare_runs(baseline: Union[Path, Dict[str, Any]], current: Union[Path, Dict[str, Any]]) -> Dict[str, Any]:
    bsum, csum, bev, cev = _as_run(baseline, current)

    b_total = int(bsum.get("total_tests") or 0)
    c_total = int(csum.get("total_tests") or 0)

    b_passed = int(bsum.get("passed") or 0)
    c_passed = int(csum.get("passed") or 0)

    b_failed = int(bsum.get("failed") or 0)
    c_failed = int(csum.get("failed") or 0)

    b_pr = float(bsum.get("pass_rate") or 0.0)
    c_pr = float(csum.get("pass_rate") or 0.0)

    b_cost = float(bsum.get("estimated_cost") or 0.0)
    c_cost = float(csum.get("estimated_cost") or 0.0)

    b_lat = float(bsum.get("avg_latency_ms") or 0.0)
    c_lat = float(csum.get("avg_latency_ms") or 0.0)

    b_inf_pt, b_inf_ct = _get_tokens(bsum, "inference")
    c_inf_pt, c_inf_ct = _get_tokens(csum, "inference")

    b_j_pt, b_j_ct = _get_tokens(bsum, "judge")
    c_j_pt, c_j_ct = _get_tokens(csum, "judge")

    regressions: List[Dict[str, Any]] = []
    improvements: List[Dict[str, Any]] = []

    if bev and cev:
        bmap = _index_by_id(bev)
        cmap = _index_by_id(cev)

        common_ids = sorted(set(bmap.keys()) & set(cmap.keys()))
        for tid in common_ids:
            b_ok = bool(bmap[tid].get("passed"))
            c_ok = bool(cmap[tid].get("passed"))

            if b_ok and not c_ok:
                regressions.append(
                    {
                        "id": tid,
                        "baseline_reason": bmap[tid].get("reason", ""),
                        "current_reason": cmap[tid].get("reason", ""),
                    }
                )
            elif (not b_ok) and c_ok:
                improvements.append(
                    {
                        "id": tid,
                        "baseline_reason": bmap[tid].get("reason", ""),
                        "current_reason": cmap[tid].get("reason", ""),
                    }
                )

    return {
        "baseline_run_id": bsum.get("run_id"),
        "current_run_id": csum.get("run_id"),
        "total_tests_delta": c_total - b_total,
        "passed_delta": c_passed - b_passed,
        "failed_delta": c_failed - b_failed,
        "pass_rate_delta": c_pr - b_pr,
        "estimated_cost_delta": c_cost - b_cost,
        "avg_latency_ms_delta": c_lat - b_lat,
        "tokens_delta": {
            "inference": {
                "prompt": c_inf_pt - b_inf_pt,
                "completion": c_inf_ct - b_inf_ct,
            },
            "judge": {
                "prompt": c_j_pt - b_j_pt,
                "completion": c_j_ct - b_j_ct,
            },
        },
        "regressions": regressions,
        "improvements": improvements,
    }


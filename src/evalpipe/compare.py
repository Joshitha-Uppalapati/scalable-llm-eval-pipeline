from collections import defaultdict

def compare_runs(baseline_summary: dict, current_summary: dict) -> dict:
    base_pass = baseline_summary.get("passed", 0)
    base_total = baseline_summary.get("total_tests", 0)
    base_rate = (base_pass / base_total) * 100 if base_total else 0.0

    cur_pass = current_summary.get("passed", 0)
    cur_total = current_summary.get("total_tests", 0)
    cur_rate = (cur_pass / cur_total) * 100 if cur_total else 0.0

    pass_rate_delta = cur_rate - base_rate

    cost_delta = (
        current_summary.get("estimated_cost", 0.0)
        - baseline_summary.get("estimated_cost", 0.0)
    )

    latency_delta = (
        current_summary.get("avg_latency_ms", 0.0)
        - baseline_summary.get("avg_latency_ms", 0.0)
    )

    base_by_cat = baseline_summary.get("by_category", {})
    cur_by_cat = current_summary.get("by_category", {})

    regressions = defaultdict(list)
    improvements = defaultdict(list)

    for cat, cur_stats in cur_by_cat.items():
        base_stats = base_by_cat.get(cat, {})
        if cur_stats.get("passed", 0) < base_stats.get("passed", 0):
            regressions[cat].append(cat)
        elif cur_stats.get("passed", 0) > base_stats.get("passed", 0):
            improvements[cat].append(cat)

    return {
        "pass_rate_delta": pass_rate_delta,
        "cost_delta": cost_delta,
        "latency_delta": latency_delta,
        "regressions": dict(regressions),
        "improvements": dict(improvements),
    }


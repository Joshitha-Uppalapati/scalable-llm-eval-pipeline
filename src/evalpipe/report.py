from pathlib import Path


def generate_markdown_report(
    run_dir: Path,
    summary: dict,
    comparison: dict | None = None,
):
    lines = [
        "# LLM Evaluation Report",
        "",
        f"**Run ID:** {summary.get('run_id', 'unknown')}",
        "",
        "## Overall Results",
        f"- Total tests: {summary.get('total_tests', 0)}",
        f"- Passed: {summary.get('passed', 0)}",
        f"- Failed: {summary.get('failed', 0)}",
        f"- Pass rate: {summary.get('pass_rate', 0.0):.2f}%",
        "",
        "## Cost",
        f"- Estimated USD cost: ${summary.get('estimated_cost', 0.0)}",
    ]

    if comparison:
        lines.extend([
            "",
            "## Baseline Comparison",
            f"- Pass rate delta: {comparison.get('pass_rate_delta', 0.0):.2f}%",
            f"- Cost delta (USD): {comparison.get('cost_delta', 0.0)}",
            f"- Latency delta (ms): {comparison.get('latency_delta', 0.0)}",
            "",
            "### Regressions (pass → fail)",
        ])

        regressions = comparison.get("regressions", [])
        if regressions:
            lines.extend([f"- {tid}" for tid in regressions])
        else:
            lines.append("- None")

        lines.extend([
            "",
            "### Improvements (fail → pass)",
        ])

        improvements = comparison.get("improvements", [])
        if improvements:
            lines.extend([f"- {tid}" for tid in improvements])
        else:
            lines.append("- None")

    report_path = run_dir / "report.md"
    report_path.write_text("\n".join(lines))


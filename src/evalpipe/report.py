from pathlib import Path
from typing import Dict, Any


def generate_markdown_report(run_dir: Path, summary: Dict[str, Any]) -> None:
    report_path = run_dir / "report.md"

    lines = []
    lines.append("# LLM Evaluation Report\n")
    lines.append(f"**Run ID:** {run_dir.name}\n")

    lines.append("## Overall Results\n")
    lines.append(f"- Total tests: {summary['total_tests']}")
    lines.append(f"- Passed: {summary['passed']}")
    lines.append(f"- Failed: {summary['failed']}")
    lines.append(f"- Pass rate: {summary['pass_rate'] * 100:.2f}%\n")

    lines.append("## Latency\n")
    lat = summary.get("latency", {})
    lines.append(f"- Average: {lat.get('avg_ms')} ms")
    lines.append(f"- P95: {lat.get('p95_ms')} ms")
    lines.append(f"- Max: {lat.get('max_ms')} ms\n")

    lines.append("## Token Usage\n")
    tokens = summary.get("tokens", {})
    lines.append(f"- Prompt tokens: {tokens.get('prompt', 0)}")
    lines.append(f"- Completion tokens: {tokens.get('completion', 0)}\n")

    lines.append("## Cost\n")
    lines.append(f"- Estimated USD cost: ${summary.get('estimated_usd_cost', 0.0)}\n")

    lines.append("## Category Breakdown\n")
    for cat, stats in summary.get("by_category", {}).items():
        lines.append(
            f"- {cat}: {stats['passed']} passed / {stats['failed']} failed"
        )

    report_path.write_text("\n".join(lines))

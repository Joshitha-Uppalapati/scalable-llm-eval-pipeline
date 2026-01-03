from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional


def _fmt_pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def _fmt_ms(x: float) -> str:
    return f"{x:.2f} ms"


def _fmt_usd(x: float) -> str:
    return f"${x:.4f}"


def generate_markdown_report(run_dir: Path, summary: Dict[str, Any], comparison: Optional[Dict[str, Any]] = None) -> None:
    lines: list[str] = []

    lines.append("# Evaluation Report")
    lines.append("")
    lines.append("## Run")
    lines.append("")
    lines.append(f"- Run ID: `{summary.get('run_id', '')}`")
    lines.append(f"- Total tests: `{summary.get('total_tests', 0)}`")
    lines.append(f"- Passed: `{summary.get('passed', 0)}`")
    lines.append(f"- Failed: `{summary.get('failed', 0)}`")
    lines.append(f"- Pass rate: `{_fmt_pct(float(summary.get('pass_rate', 0.0)))}`")
    lines.append(f"- Avg latency: `{_fmt_ms(float(summary.get('avg_latency_ms', 0.0)))}`")
    lines.append(f"- Estimated cost: `{_fmt_usd(float(summary.get('estimated_cost', 0.0)))}`")
    lines.append("")

    tokens = summary.get("tokens") or {}
    inf = tokens.get("inference") or {}
    jud = tokens.get("judge") or {}
    lines.append("## Tokens")
    lines.append("")
    lines.append("| Role | Prompt | Completion |")
    lines.append("|---|---:|---:|")
    lines.append(f"| Inference | {int(inf.get('prompt', 0))} | {int(inf.get('completion', 0))} |")
    lines.append(f"| Judge | {int(jud.get('prompt', 0))} | {int(jud.get('completion', 0))} |")
    lines.append("")

    by_cat = summary.get("by_category") or {}
    if by_cat:
        lines.append("## By category")
        lines.append("")
        lines.append("| Category | Total | Passed | Failed |")
        lines.append("|---|---:|---:|---:|")
        for k in sorted(by_cat.keys()):
            v = by_cat[k]
            lines.append(f"| {k} | {int(v.get('total', 0))} | {int(v.get('passed', 0))} | {int(v.get('failed', 0))} |")
        lines.append("")

    by_eval = summary.get("by_evaluator") or {}
    if by_eval:
        lines.append("## By evaluator")
        lines.append("")
        lines.append("| Evaluator | Total | Failed |")
        lines.append("|---|---:|---:|")
        for k in sorted(by_eval.keys()):
            v = by_eval[k]
            lines.append(f"| {k} | {int(v.get('total', 0))} | {int(v.get('failed', 0))} |")
        lines.append("")

    top = summary.get("top_failures") or []
    if top:
        lines.append("## Top failures")
        lines.append("")
        for t in top[:10]:
            lines.append(f"- `{t.get('id','')}` ({t.get('category','')}, {t.get('evaluator','')}): {t.get('reason','')}")
        lines.append("")

    if comparison is not None:
        lines.append("## Baseline comparison")
        lines.append("")
        lines.append(f"- Pass rate delta: `{_fmt_pct(float(comparison.get('pass_rate_delta', 0.0)))}`")
        lines.append(f"- Cost delta: `{_fmt_usd(float(comparison.get('estimated_cost_delta', 0.0)))}`")
        lines.append(f"- Latency delta: `{_fmt_ms(float(comparison.get('avg_latency_ms_delta', 0.0)))}`")
        lines.append("")

        regs = comparison.get("regressions") or []
        imps = comparison.get("improvements") or []

        if regs:
            lines.append("### Regressions (pass → fail)")
            lines.append("")
            for r in regs[:25]:
                lines.append(f"- `{r.get('id','')}`: {r.get('current_reason','')}")
            lines.append("")

        if imps:
            lines.append("### Improvements (fail → pass)")
            lines.append("")
            for r in imps[:25]:
                lines.append(f"- `{r.get('id','')}`: {r.get('current_reason','')}")
            lines.append("")

    (run_dir / "report.md").write_text("\n".join(lines) + "\n")


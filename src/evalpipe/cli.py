from pathlib import Path
from datetime import datetime, timezone
import json
import sys
import typer
import shutil

from evalpipe.loader import load_suite
from evalpipe.prompts.render import render_prompt
from evalpipe.runner import run as run_single
from evalpipe.evaluators import evaluate
from evalpipe.aggregate import aggregate_results
from evalpipe.storage import write_run_artifacts
from evalpipe.report import generate_markdown_report
from evalpipe.compare import compare_runs
from evalpipe.evaluators.judge import run_judge

app = typer.Typer()


@app.command()
def clear_cache():
    shutil.rmtree(".cache", ignore_errors=True)
    typer.echo("Cache cleared")


@app.command()
def run(
    suite: Path,
    prompt: Path = typer.Option(...),
    model: str = typer.Option("dummy-v0"),
    baseline: Path | None = typer.Option(None),
):
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = Path("runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    test_cases = load_suite(suite)

    results: list[dict] = []
    evaluations: list[dict] = []

    for tc in test_cases:
        rendered_prompt = render_prompt(prompt, tc)

        tc_for_runner = dict(tc)
        tc_for_runner["prompt"] = rendered_prompt

        result_obj = run_single(tc_for_runner)

        provider_out = result_obj.provider_output

        result = {
            "id": tc["id"],
            "prompt": rendered_prompt,
            "output": provider_out.output,
            "model": provider_out.model,
            "latency_ms": provider_out.latency_ms,
            "prompt_tokens": provider_out.prompt_tokens,
            "completion_tokens": provider_out.completion_tokens,
            "cache_hit": False,
            "timestamp": result_obj.timestamp,
            "rendered_prompt": rendered_prompt,
            "prompt_version": prompt.stem,
        }

        results.append(result)

        eval_out = evaluate(tc, result, judge_runner=run_judge)
        eval_out["id"] = tc["id"]
        evaluations.append(eval_out)

    summary = aggregate_results(test_cases, results, evaluations)
    summary["run_id"] = run_id

    write_run_artifacts(
        run_dir=run_dir,
        test_cases=test_cases,
        results=results,
        evaluations=evaluations,
        summary=summary,
    )

    comparison = None
    regression_detected = False

    if baseline:
        baseline_summary = json.loads((baseline / "summary.json").read_text())
        comparison = compare_runs(baseline_summary, summary)

        # Treat any drop in pass rate as regression
        if comparison.get("pass_rate_delta", 0) < 0:
            regression_detected = True

    generate_markdown_report(run_dir, summary, comparison)

    typer.echo(f"Run written to {run_dir}")
    typer.echo(f"Pass rate: {summary['pass_rate']:.2f}%")
    typer.echo(f"Estimated cost (USD): ${summary['estimated_cost']}")

    if regression_detected:
        typer.echo("Regression detected compared to baseline.")
        raise typer.Exit(code=1)

    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
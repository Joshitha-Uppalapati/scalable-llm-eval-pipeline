
from pathlib import Path
from datetime import datetime
import json
import sys
import typer

from evalpipe.loader import load_suite
from evalpipe.prompts.render import render_prompt
from evalpipe.runner import run as run_single
from evalpipe.evaluators import evaluate
from evalpipe.aggregate import aggregate_results
from evalpipe.storage import write_run_artifacts
from evalpipe.report import generate_markdown_report
from evalpipe.compare import compare_runs

app = typer.Typer()


@app.command()
def run(
    suite: Path,
    prompt: Path = typer.Option(...),
    model: str = typer.Option("dummy-v0"),
    baseline: Path | None = typer.Option(None),
):
    run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_dir = Path("runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    test_cases = load_suite(suite)

    results: list[dict] = []
    evaluations: list[dict] = []

    for tc in test_cases:
        rendered_prompt = render_prompt(prompt, tc)

        result_obj = run_single(tc)
        result = result_obj.__dict__.copy()

        result["rendered_prompt"] = rendered_prompt
        result["prompt_version"] = prompt.stem

        results.append(result)

        eval_out = evaluate(tc, result)
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

        if comparison.get("pass_rate_delta", 0) < 0:
            regression_detected = True

    generate_markdown_report(run_dir, summary, comparison)

    typer.echo(f"Run written to {run_dir}")
    typer.echo(f"Pass rate: {summary['pass_rate']:.2f}%")
    typer.echo(f"Estimated cost (USD): ${summary['estimated_cost']}")

    if regression_detected:
        typer.echo("Regression detected compared to baseline.")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    app()

from pathlib import Path
from datetime import datetime, timezone
import typer

from evalpipe.loader import load_suite
from evalpipe.prompts.render import render_prompt
from evalpipe.runner import run_inference
from evalpipe.evaluators import evaluate
from evalpipe.aggregate import aggregate_results
from evalpipe.storage import write_run_artifacts
from evalpipe.compare import compare_runs
from evalpipe.report import generate_markdown_report

app = typer.Typer()


@app.command()
def run(
    suite: Path = typer.Argument(..., help="Path to JSONL evaluation suite"),
    model: str = typer.Option("dummy-v0", help="Model name"),
    prompt: Path = typer.Option(
        Path("src/evalpipe/prompts/basic_v1.txt"),
        help="Prompt template file",
    ),
):
    """
    Run inference + evaluation + reporting.
    """

    # Load suite
    test_cases = load_suite(suite)

    # Render prompt (deterministic)
    rendered_prompt = render_prompt(prompt, test_cases[0])
    prompt_version = prompt.stem

    # Run inference
    results, errors, timings, token_usage = run_inference(
        test_cases=test_cases,
        model=model,
        rendered_prompt=rendered_prompt,
    )

    # Evaluate
    evaluations = []
    for tc, result in zip(test_cases, results):
        evaluations.append(
            {
                "id": tc["id"],
                **evaluate(tc, result),
            }
        )

    # Aggregate
    summary = aggregate_results(
        test_cases=test_cases,
        results=results,
        evaluations=evaluations,
    )

    # Create run directory
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = Path("runs") / run_id

    # Persist artifacts
    write_run_artifacts(
        run_dir=run_dir,
        test_cases=test_cases,
        results=results,
        evaluations=evaluations,
        summary=summary,
        rendered_prompt=rendered_prompt,
        prompt_version=prompt_version,
        model=model,
        errors=errors,
    )

    # Generate report
    generate_markdown_report(run_dir, summary)

    # CLI output
    typer.echo(f"Run written to {run_dir}")
    typer.echo(f"Pass rate: {summary['pass_rate'] * 100:.2f}%")

    if summary.get("prompt_tokens") is not None:
        typer.echo(
            f"Tokens: prompt={summary['prompt_tokens']} "
            f"completion={summary['completion_tokens']}"
        )

    if summary.get("estimated_usd_cost") is not None:
        typer.echo(f"Estimated cost (USD): ${summary['estimated_usd_cost']}")


@app.command()
def compare(
    baseline: Path = typer.Argument(..., help="Baseline run directory"),
    current: Path = typer.Argument(..., help="Current run directory"),
):
    """
    Compare two runs and show regressions.
    """

    deltas = compare_runs(baseline, current)

    if not deltas["regressions"] and not deltas["improvements"]:
        typer.echo("No changes detected.")
        return

    typer.echo("\nRegressions:")
    for r in deltas["regressions"]:
        typer.echo(f"  ❌ {r}")

    typer.echo("\nImprovements:")
    for i in deltas["improvements"]:
        typer.echo(f"  ✅ {i}")

    typer.echo("\nMetric deltas:")
    for k, v in deltas["metrics"].items():
        typer.echo(f"  {k}: {v}")


if __name__ == "__main__":
    app()


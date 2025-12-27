from pathlib import Path
from datetime import datetime
import typer

from evalpipe.report import generate_markdown_report
from evalpipe.loader import load_suite
from evalpipe.runner import dummy_infer
from evalpipe.prompts.render import render_prompt
from evalpipe.evaluators import evaluate
from evalpipe.aggregate import aggregate_results
from evalpipe.storage import write_run_artifacts
from evalpipe.compare import compare_runs
from evalpipe.providers.openai_provider import infer as openai_infer

app = typer.Typer()


@app.command()
def run(
    suite: Path = typer.Argument(..., help="Path to evaluation suite JSONL"),
    provider: str = typer.Option(
        "dummy", help="Inference provider: dummy | openai"
    ),
):
    runs_dir = Path("runs")
    runs_dir.mkdir(exist_ok=True)

    run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_dir = runs_dir / run_id

    suite_data = load_suite(suite)
    template = Path("src/evalpipe/prompts/basic_v1.txt")

    results = []
    evaluations = []

    for tc in suite_data:
        prompt = render_prompt(template, tc)

        if provider == "openai":
            out = openai_infer(prompt)
            result = {
                "id": tc["id"],
                "prompt": prompt,
                "output": out["output"],
                "model": out["model"],
                "latency_ms": out["latency_ms"],
                "prompt_tokens": out["prompt_tokens"],
                "completion_tokens": out["completion_tokens"],
            }
        else:
            result = dummy_infer(tc)

        results.append(result)

        eval_result = evaluate(tc, result)
        eval_result["id"] = tc["id"]
        evaluations.append(eval_result)

    summary = aggregate_results(suite_data, results, evaluations)

    write_run_artifacts(
        run_dir=run_dir,
        test_cases=suite_data,
        results=results,
        evaluations=evaluations,
        summary=summary,
    )
    generate_markdown_report(run_dir, summary)

    typer.echo(f"Run written to {run_dir}")
    typer.echo(f"Pass rate: {summary['pass_rate'] * 100:.2f}%")

    latency = summary.get("latency", {})
    tokens = summary.get("tokens", {})

    if latency.get("avg_ms") is not None:
        typer.echo(
            f"Latency (ms): avg={latency['avg_ms']} "
            f"p95={latency['p95_ms']} "
            f"max={latency['max_ms']}"
        )

    if tokens:
        typer.echo(
            f"Tokens: prompt={tokens['prompt']} "
            f"completion={tokens['completion']}"
        )

    if summary.get("estimated_usd_cost") is not None:
        typer.echo(
            f"Estimated cost (USD): ${summary['estimated_usd_cost']}"
        )


@app.command()
def compare(
    prev_run: Path = typer.Argument(..., help="Previous run directory"),
    curr_run: Path = typer.Argument(..., help="Current run directory"),
):
    regressions = compare_runs(prev_run, curr_run)

    if not regressions:
        typer.echo("No regressions detected.")
        return

    typer.echo("Regressions detected:")
    for r in regressions:
        typer.echo(f"- {r}")


if __name__ == "__main__":
    app()


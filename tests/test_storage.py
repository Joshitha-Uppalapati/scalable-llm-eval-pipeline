from pathlib import Path

from evalpipe.storage import write_run_artifacts


def test_write_run_artifacts(tmp_path: Path):
    run_dir = tmp_path / "run_001"

    test_cases = [{"id": "t1", "category": "math"}]
    results = [{"id": "t1", "output": "4"}]
    evaluations = [{"passed": True}]
    summary = {"total_tests": 1, "passed": 1, "failed": 0}

    write_run_artifacts(
        run_dir=run_dir,
        test_cases=test_cases,
        results=results,
        evaluations=evaluations,
        summary=summary,
    )

    assert (run_dir / "test_cases.jsonl").exists()
    assert (run_dir / "results.jsonl").exists()
    assert (run_dir / "evaluations.jsonl").exists()
    assert (run_dir / "summary.json").exists()
    assert (run_dir / "meta.json").exists()


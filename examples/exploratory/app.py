# NOTE:
# This file represents an early exploration before the pipeline
# structure stabilized. It is kept here for reference.


import json
from pathlib import Path
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def read_json(path: Path):
    return json.loads(path.read_text())


def read_jsonl(path: Path):
    rows = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def find_latest_run_dir(base: Path) -> Path | None:
    if not base.exists():
        return None
    candidates = [p for p in base.iterdir() if p.is_dir()]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


st.set_page_config(page_title="EvalPipe Dashboard", layout="wide")
st.title("EvalPipe Dashboard")

runs_root = st.sidebar.text_input("Runs directory", value="runs")
run_dir_input = st.sidebar.text_input("Run directory (optional)", value="")

runs_root_path = Path(runs_root)
run_dir_path = Path(run_dir_input) if run_dir_input.strip() else find_latest_run_dir(runs_root_path)

if not run_dir_path:
    st.warning("No run directory found. Set Runs directory or paste a Run directory path.")
    st.stop()

st.sidebar.write(f"Using: {run_dir_path}")

meta_path = run_dir_path / "meta.json"
summary_path = run_dir_path / "summary.json"
results_path = run_dir_path / "results.jsonl"
evals_path = run_dir_path / "evaluations.jsonl"

meta = read_json(meta_path) if meta_path.exists() else {}
summary = read_json(summary_path) if summary_path.exists() else {}

cols = st.columns(4)
cols[0].metric("Suite", str(meta.get("suite_id", "unknown")))
cols[1].metric("Model", str(meta.get("model", "unknown")))
cols[2].metric("Prompt Hash", str(meta.get("prompt_hash", "missing"))[:12] + "…" if meta.get("prompt_hash") else "missing")
cols[3].metric("Dry Run", "yes" if meta.get("dry_run") else "no")

pass_rate = summary.get("pass_rate")
estimated_cost = summary.get("estimated_cost_usd") or summary.get("cost_usd")

c2 = st.columns(2)

fig1 = plt.figure()
ax1 = fig1.add_subplot(111)
ax1.bar(["Pass Rate"], [float(pass_rate) if pass_rate is not None else 0.0])
ax1.set_ylim(0, 1)
ax1.set_ylabel("Rate")
c2[0].pyplot(fig1)

fig2 = plt.figure()
ax2 = fig2.add_subplot(111)
ax2.bar(["Cost (USD)"], [float(estimated_cost) if estimated_cost is not None else 0.0])
ax2.set_ylabel("USD")
c2[1].pyplot(fig2)

if results_path.exists():
    results_rows = read_jsonl(results_path)
    df = pd.DataFrame(results_rows)
    st.subheader("Results")
    st.dataframe(df, use_container_width=True)

if evals_path.exists():
    eval_rows = read_jsonl(evals_path)
    df2 = pd.DataFrame(eval_rows)
    st.subheader("Evaluations")
    st.dataframe(df2, use_container_width=True)

st.subheader("Summary JSON")
st.json(summary)

st.subheader("Meta JSON")
st.json(meta)


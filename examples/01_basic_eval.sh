#!/usr/bin/env bash
set -e

python -m evalpipe.cli run data/suites/basic_v1.jsonl \
  --prompt src/evalpipe/prompts/basic_v1.txt

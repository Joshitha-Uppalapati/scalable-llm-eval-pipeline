#!/bin/bash
set -e

python src/evalpipe/cli.py run data/suites/basic_v1.jsonl \
  --prompt src/evalpipe/prompts/basic_v1.txt
"""
Optional example showing how to plug a real OpenAI provider
into the evaluation workflow.

This script is NOT used in CI.
The dummy provider exists to keep tests deterministic.

To run this:
  pip install openai
  export OPENAI_API_KEY=...
  python examples/with_openai.py
"""

import os
import sys

try:
    from openai import OpenAI
except ImportError:
    print(
        "OpenAI client not installed.\n"
        "This example is optional.\n\n"
        "To run it:\n"
        "  pip install openai\n"
        "  export OPENAI_API_KEY=...\n"
    )
    sys.exit(0)

from evalpipe.prompts.render import render_prompt
from evalpipe.loader import load_suite


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(
            "OPENAI_API_KEY not set.\n"
            "This example is optional and not required for CI."
        )
        sys.exit(0)

    client = OpenAI(api_key=api_key)

    suite_path = "data/suites/basic_v1.jsonl"
    prompt_path = "src/evalpipe/prompts/basic_v1.txt"

    test_cases = load_suite(suite_path)

    test_case = test_cases[0]
    prompt = render_prompt(prompt_path, test_case)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    print("Prompt:")
    print(prompt)
    print("\nModel output:")
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
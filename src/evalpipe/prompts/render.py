from pathlib import Path
from typing import Dict


def render_prompt(template_path: Path, test_case: Dict) -> str:
    """
    Renders a prompt template by injecting test case values.
    Currently supports {{prompt}} replacement.
    """
    template = template_path.read_text()

    rendered = template.replace("{{prompt}}", test_case["prompt"])

    return rendered.strip()

from pathlib import Path
from typing import Dict


def render_prompt(template_path: Path, test_case: Dict) -> str:
    template = template_path.read_text()

    rendered = template.replace("{{prompt}}", test_case["prompt"])

    return rendered.strip()


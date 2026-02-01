from pathlib import Path
import hashlib
from typing import Dict, Any


def load_prompt(path: str):
    """
    Loads a prompt file and returns both the raw text and a stable hash.

    The hash is used to detect prompt changes across runs so regressions
    can be attributed to prompt edits instead of model behavior.
    """
    p = Path(path)
    text = p.read_text(encoding="utf-8")

    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return text, content_hash


def render_prompt(prompt_path: Path, test_case: Dict[str, Any]) -> str:
    """
    Renders a prompt template using {{field}} placeholders.

    I intentionally avoided Jinja or heavier templating here.
    Simple string replacement keeps prompt behavior obvious
    and avoids surprises during debugging.
    """
    template_text, _ = load_prompt(str(prompt_path))

    rendered = template_text

    for key, value in test_case.items():
        placeholder = f"{{{{{key}}}}}"
        rendered = rendered.replace(placeholder, str(value))

    return rendered

"""
Prompt loading and hashing utilities.

This module handles reading prompt templates from disk and
computing a stable hash so prompt changes can be detected
between runs.
Rendering with test-case data lives in prompts/render.py.
"""

from pathlib import Path
import hashlib
from typing import Tuple


def load_prompt(path: str | Path) -> Tuple[str, str]:
    """
    Load a prompt template from disk and return its content
    along with a stable content hash.
    The hash is used to detect prompt changes across runs.
    """
    path = Path(path)

    text = path.read_text(encoding="utf-8")

    # Hash is based purely on content, not filename or path
    prompt_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

    return text, prompt_hash
import hashlib
from typing import Tuple


def load_prompt(path: str) -> Tuple[str, str]:
    with open(path, "r") as f:
        text = f.read()

    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return text, digest

import hashlib
import json
from pathlib import Path

CACHE_DIR = Path(".cache")

def make_cache_key(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()

def load_from_cache(key: str):
    path = CACHE_DIR / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text())
    return None

def save_to_cache(key: str, value: dict):
    CACHE_DIR.mkdir(exist_ok=True)
    (CACHE_DIR / f"{key}.json").write_text(json.dumps(value))


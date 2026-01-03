import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any

CACHE_DIR = Path(".cache")


def _stable_hash(obj: Dict[str, Any]) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def make_cache_key(
    *,
    suite_id: str,
    test_id: str,
    model: str,
    prompt: str,
    params: Dict[str, Any],
) -> str:
    payload = {
        "suite_id": suite_id,
        "test_id": test_id,
        "model": model,
        "prompt": prompt,
        "params": params,
    }
    return _stable_hash(payload)


def load_from_cache(key: str) -> Optional[Dict[str, Any]]:
    path = CACHE_DIR / f"{key}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def save_to_cache(key: str, value: Dict[str, Any]) -> None:
    CACHE_DIR.mkdir(exist_ok=True)
    path = CACHE_DIR / f"{key}.json"
    path.write_text(json.dumps(value, indent=2))


def clear_cache() -> None:
    if not CACHE_DIR.exists():
        return
    for f in CACHE_DIR.glob("*.json"):
        f.unlink()

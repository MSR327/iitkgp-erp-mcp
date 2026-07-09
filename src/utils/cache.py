import json
import time
from pathlib import Path

CACHE_DIR = Path.home() / ".iitkgp-erp-mcp" / "cache"
DEFAULT_TTL = 300  # 5 minutes


def _ensure_cache_dir():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get(key: str) -> dict | None:
    _ensure_cache_dir()
    cache_file = CACHE_DIR / f"{key}.json"

    if not cache_file.exists():
        return None

    data = json.loads(cache_file.read_text())
    if time.time() - data["timestamp"] > data["ttl"]:
        cache_file.unlink()
        return None

    return data["value"]


def set(key: str, value, ttl: int = DEFAULT_TTL):
    _ensure_cache_dir()
    cache_file = CACHE_DIR / f"{key}.json"
    cache_file.write_text(json.dumps({
        "value": value,
        "timestamp": time.time(),
        "ttl": ttl,
    }))


def clear():
    _ensure_cache_dir()
    for f in CACHE_DIR.glob("*.json"):
        f.unlink()

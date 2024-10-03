import json
import os
import time
from typing import Dict, Any

CACHE_DIR = "cache"
CACHE_DURATION = 3600  # 1 hour

def ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def cache_key(domain: str, scan_types: list) -> str:
    return f"{domain}_{'-'.join(sorted(scan_types))}"

def save_to_cache(domain: str, scan_types: list, results: Dict[str, Any]):
    ensure_cache_dir()
    key = cache_key(domain, scan_types)
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")
    with open(cache_file, 'w') as f:
        json.dump({"timestamp": time.time(), "results": results}, f)

def load_from_cache(domain: str, scan_types: list) -> Dict[str, Any] | None:
    key = cache_key(domain, scan_types)
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            data = json.load(f)
        if time.time() - data["timestamp"] < CACHE_DURATION:
            return data["results"]
    return None

def clear_cache():
    for file in os.listdir(CACHE_DIR):
        os.remove(os.path.join(CACHE_DIR, file))
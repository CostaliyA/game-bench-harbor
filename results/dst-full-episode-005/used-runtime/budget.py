"""Shared configurable limits; limits.json may raise the budget during a trial."""
import json
import os
from pathlib import Path

def read_limits(run_dir):
    limits = {
        'token_limit': int(os.environ.get('DST_TOKEN_LIMIT', '500000')),
        'wall_limit_seconds': int(os.environ.get('DST_WALL_LIMIT', '1800')),
    }
    path = Path(run_dir) / 'limits.json'
    if path.exists():
        data = json.loads(path.read_text())
        for key in limits:
            if key in data:
                limits[key] = int(data[key])
    if any(value <= 0 for value in limits.values()):
        raise ValueError('Budget limits must be positive')
    return limits

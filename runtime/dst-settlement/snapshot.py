"""Read-only compact progress view for a running settlement trial."""
import json
import os
import pathlib
import time
import urllib.request

root = pathlib.Path('/home/steam/dst-settlement-v1') / os.environ.get('DST_RUN_ID', 'run-001-settlement-v1')
with urllib.request.urlopen('http://127.0.0.1:18775/status', timeout=10) as response:
    status = json.load(response)
state = status['state']
usage_path = root / 'api/usage.jsonl'
usage = [json.loads(line) for line in usage_path.read_text().splitlines()] if usage_path.exists() else []
start = root / 'start-time.txt'
print(json.dumps({
    'started': status['started'], 'terminal': status['terminal'],
    'elapsed_wall_s': round(time.time() - float(start.read_text()), 1) if start.exists() else None,
    'state': {key: state.get(key) for key in ('time', 'cycle', 'phase', 'day_fraction', 'x', 'z', 'health', 'hunger', 'sanity', 'last_action', 'progress')},
    'inventory': [{key: item.get(key) for key in ('prefab', 'count', 'equipped', 'container')} for item in state.get('inventory', [])],
    'events': status['events'], 'completed_api_calls': len(usage),
    'total_tokens': sum(row['usage'].get('total_tokens', 0) for row in usage),
    'max_prompt_tokens': max((row['usage'].get('prompt_tokens', 0) for row in usage), default=0),
}, ensure_ascii=False))

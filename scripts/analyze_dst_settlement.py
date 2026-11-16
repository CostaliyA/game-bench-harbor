"""Recompute a recorded settlement trial from frozen game events and raw logs."""
import argparse
import collections
import importlib.util
import json
import math
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('run_dir', type=Path)
a = p.parse_args()
r = a.run_dir

def read_lines(name):
    return [json.loads(line) for line in (r / name).read_text().splitlines() if line.strip()]

spec = importlib.util.spec_from_file_location('frozen_reward', r / 'used-runtime/tasks/dst-science-settlement/tests/reward.py')
reward_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reward_module)
events = read_lines('events.jsonl')
score = reward_module.score(events)
assert score['complete'], 'Incomplete infrastructure run; no valid terminal score'
actions = read_lines('actions.jsonl')
results = read_lines('action-results.jsonl')
states = read_lines('states.jsonl')
active = [s for s in states if s.get('active')]
last_event = next(e for e in events if e['type'] == score['terminal'])
returned = collections.Counter()
errors = []
for row in results:
    last = row.get('state', {}).get('last_action', {})
    status = last.get('status', 'missing') if last.get('id') == row['id'] else 'different_action_id'
    returned[status] += 1
    if status in ('failed', 'error'):
        errors.append({'id': row['id'], 'status': status, 'error': last.get('error')})
seen = {}
for state in active:
    for entity in state.get('nearby', []):
        seen[entity['id']] = entity
distance = sum(math.hypot(b['x'] - a['x'], b['z'] - a['z']) for a, b in zip(active, active[1:]))
start = float((r / 'start-time.txt').read_text())
end = float((r / 'terminal-time.txt').read_text())
summary = {
    **score,
    'actions': len(actions),
    'action_results': len(results),
    'actions_by_type': dict(collections.Counter(row['command']['action'] for row in actions)),
    'craft_attempts': dict(collections.Counter(row['command'].get('recipe') for row in actions if row['command']['action'] == 'craft')),
    'status_at_action_return': dict(returned),
    'status_note': 'This is the status at tool return, not a final success count. Native actions can finish later; move status remains moving.',
    'errors_at_return': errors,
    'elapsed_wall_seconds': end - start,
    'elapsed_game_seconds': last_event['game_time'] - events[0]['game_time'],
    'sampled_travel_distance': distance,
    'observed_prefabs': dict(collections.Counter(e['prefab'] for e in seen.values())),
    'milestone_times': [{'name': e['name'], 'game_seconds': e['game_time'] - events[0]['game_time']} for e in events if e['type'] == 'milestone'],
    'terminal_event': last_event,
}
(r / 'reward.json').write_text(json.dumps(score, ensure_ascii=False, indent=2) + '\n')
(r / 'analysis.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(summary, ensure_ascii=False, indent=2))

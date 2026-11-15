#!/usr/bin/env python3
"""Independently reconcile a published DST trial's score, context and evidence."""
from pathlib import Path
import hashlib, importlib.util, json
root = Path(__file__).resolve().parents[1]
r = root/'results/dst-context500k-003'
read = lambda p: json.loads(p.read_text())
rows = lambda p: [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
spec = importlib.util.spec_from_file_location('dst_reward',root/'tasks/dst-first-night/tests/reward.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
score = m.score(rows(r/'events.jsonl'))
assert score == read(r/'reward.json') == read(r/'harbor/trial/verifier/reward-report.json')
assert score['complete'] and read(r/'final-status.json')['terminal']
config = read(r/'opencode-effective.json')
limits = config['providers']['deepseek']['models']['deepseek-flash']['limit']
assert limits == {'context':500000,'input':495904,'output':4096}
usage = rows(r/'api/usage.jsonl')
summary = read(r/'api-summary.json')
assert sum(x['usage']['total_tokens'] for x in usage) == summary['tokens']['total_tokens']
assert summary['tokens']['total_tokens'] > 500000
assert max(x['usage']['prompt_tokens'] for x in usage) == summary['max_prompt_tokens']
actions = rows(r/'actions.jsonl'); results = rows(r/'action-results.jsonl')
assert [x['command']['id'] for x in actions] == list(range(1,len(actions)+1))
assert [x['id'] for x in results] == list(range(1,len(actions)+1))
trajectory = rows(r/'action-trajectory.jsonl')
assert len(trajectory) == len(actions)
assert all(t['command'] == a['command'] for t,a in zip(trajectory,actions))
state = rows(r/'states.jsonl')
assert state and all(s['camera_heading']==45 and s['camera_target']==45 for s in state)
manifest = read(r/'experiment.json')
assert manifest['cumulative_token_limit'] is None
for name, digest in manifest['runtime_sha256'].items():
    assert hashlib.sha256((r/'used-runtime'/name).read_bytes()).hexdigest() == digest, name
trial = read(r/'harbor/trial/result.json')
assert not trial.get('exception_info'), trial.get('exception_info')
report = {'score':score,'context_limit':limits,'actual_max_prompt_tokens':summary['max_prompt_tokens'],
          'cumulative_total_tokens':summary['tokens']['total_tokens'],'actions':len(actions),
          'camera_samples':len(state),'harbor_exception':trial.get('exception_info'),
          'startup_intervention':manifest['startup_intervention']}
print(json.dumps(report,ensure_ascii=False,indent=2))

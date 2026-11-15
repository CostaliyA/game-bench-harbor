#!/usr/bin/env python3
import sys,json,pathlib,importlib.util
root=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('dst_reward',root/'tasks/dst-first-night/tests/reward.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else root/'results/dst/events.jsonl'
print(json.dumps(m.score([json.loads(l) for l in p.read_text().splitlines() if l.strip()]),indent=2))

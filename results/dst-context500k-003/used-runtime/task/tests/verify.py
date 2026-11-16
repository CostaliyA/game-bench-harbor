import json,pathlib,urllib.request
from reward import score
out=pathlib.Path('/logs/verifier');out.mkdir(exist_ok=True,parents=True)
with urllib.request.urlopen('http://172.17.0.2:18765/status') as r:s=json.load(r)
(out/'game-evidence.json').write_text(json.dumps(s,indent=2))
assert s['started'] and s['events'],'Game never started'
result=score(s['events']);(out/'reward-report.json').write_text(json.dumps(result,indent=2))
assert result['complete'],'Episode missing terminal event; not a valid scored rollout'
(out/'reward.txt').write_text(str(result['reward']))
print(json.dumps(result))

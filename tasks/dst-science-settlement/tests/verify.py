import json
import os
import pathlib
import urllib.request
from reward import score

out = pathlib.Path('/logs/verifier')
out.mkdir(exist_ok=True, parents=True)
url = os.environ.get('DST_BRIDGE_URL', 'http://172.17.0.2:18775')
with urllib.request.urlopen(url + '/status', timeout=30) as response:
    evidence = json.load(response)
(out / 'game-evidence.json').write_text(json.dumps(evidence, indent=2))
result = score(evidence['events'])
(out / 'reward-report.json').write_text(json.dumps(result, indent=2))
assert result['complete'], 'No terminal event: infrastructure failure, not a scored game loss'
(out / 'reward.txt').write_text(str(result['reward']))
print(json.dumps(result))

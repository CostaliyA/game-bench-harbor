import pathlib,json,time,urllib.request,subprocess,os
root=pathlib.Path('/home/steam/dst-eval-runtime')/os.environ.get('DST_RUN_ID','run-001');env={**os.environ,'DISPLAY':':99'}
from budget import read_limits
def key(k):
 subprocess.run(['xdotool','keydown',k],env=env);time.sleep(.2);subprocess.run(['xdotool','keyup',k],env=env);time.sleep(.3)
while True:
 s=json.load(urllib.request.urlopen('http://127.0.0.1:18765/status'))
 if s['terminal']:break
 p=root/'api/usage.jsonl';rows=[json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []
 total=sum(x['usage']['total_tokens'] for x in rows)
 elapsed=time.time()-float((root/'start-time.txt').read_text()) if (root/'start-time.txt').exists() else 0
 limits=read_limits(root)
 if total>=limits['token_limit'] or elapsed>=limits['wall_limit_seconds']:
  (root/'budget-stop.json').write_text(json.dumps({'tokens':total,'elapsed_wall_s':elapsed,'reason':'token_limit' if total>=limits['token_limit'] else 'wall_time_limit'}))
  key('grave');subprocess.run(['xdotool','type','--clearmodifiers','--delay','15','dst_eval_timeout()'],env=env);key('Return');break
 time.sleep(2)

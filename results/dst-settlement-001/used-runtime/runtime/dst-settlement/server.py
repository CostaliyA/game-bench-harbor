import http.server,json,pathlib,threading,time,subprocess,os
ROOT=pathlib.Path('/home/steam/dst-settlement-v1');OUT=ROOT/os.environ.get('DST_RUN_ID','run-001');OUT.mkdir(exist_ok=True)
lock=threading.RLock();state={};events=[];commands=[];counter=0;started=False;started_at=0;startup_error=None;startup_lock=threading.Lock()

def append(name,obj):
 with (OUT/name).open('a') as f:f.write(json.dumps(obj,ensure_ascii=False)+'\n')
def console(code):
 env={**os.environ,'DISPLAY':':99'}
 def key(k):
  subprocess.run(['xdotool','keydown',k],env=env,check=True);time.sleep(.2)
  subprocess.run(['xdotool','keyup',k],env=env,check=True);time.sleep(.4)
 key('grave')
 subprocess.run(['xdotool','type','--clearmodifiers','--delay','15',code],env=env,check=True)
 key('Return')
def begin():
 global started,started_at,startup_error
 with startup_lock:
  if started:return
  if startup_error:raise RuntimeError(startup_error)
  if not state or state.get('active'):
   raise RuntimeError('Fresh paused preflight state required')
  started_at=time.monotonic()
  (OUT/'start-time.txt').write_text(str(time.time()))
  log=(OUT/'video.log').open('w')
  proc=subprocess.Popen(['ffmpeg','-y','-loglevel','warning','-f','x11grab','-framerate','10','-video_size','1280x720','-i',':99','-c:v','libx264','-preset','ultrafast','-crf','26','-pix_fmt','yuv420p',str(OUT/'episode.mp4')],stdout=log,stderr=log)
  (OUT/'ffmpeg.pid').write_text(str(proc.pid))
  try:
   console('dofile("/home/steam/dst-settlement-v1/camera.lua"); settlement_begin()')
   for _ in range(100):
    if events and state.get('active'):
     started=True
     return
    time.sleep(.1)
   raise RuntimeError('Game did not acknowledge evaluation start')
  except Exception as e:
   startup_error=str(e)
   (OUT/'startup-error.txt').write_text(startup_error)
   raise
def terminal():return any(e['type'] in ('day3_dawn','death','timeout','abort','invalid') for e in events)
class H(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def reply(self,obj,status=200):
  b=json.dumps(obj).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  with lock:
   if self.path=='/command':return self.reply(commands.pop(0) if commands and not terminal() else {})
   if self.path=='/status':return self.reply({'started':started,'terminal':terminal(),'state':state,'events':events})
  self.reply({'error':'not found'},404)
 def do_POST(self):
  global state,counter
  data=json.loads(self.rfile.read(int(self.headers.get('Content-Length',0))) or b'{}')
  if self.path=='/preflight' and os.environ.get('DST_RUN_ID')=='preflight':
   append('checks.jsonl',data)
   return self.reply({})
  if self.path=='/state':
   with lock:state=data;append('states.jsonl',{'wall_time':time.time(),**data})
   return self.reply({})
  if self.path=='/event':
   with lock:events.append(data);append('events.jsonl',data)
   if data.get('type') in ('day3_dawn','death','timeout','abort','invalid'):
    (OUT/'terminal-time.txt').write_text(str(time.time()))
   return self.reply({})
  if self.path=='/observe':
   begin()
   for _ in range(100):
    if events or terminal():break
    time.sleep(.1)
   with lock:return self.reply({'state':state,'terminal':terminal(),'events':events})
  if self.path=='/act':
   begin()
   allowed={'move','pick','pickup','chop','craft','equip','eat','cook','fuel','wait','mine','attack'}
   if data.get('action') not in allowed:return self.reply({'error':'invalid action'},400)
   with lock:
    if terminal():return self.reply({'state':state,'terminal':True,'events':events})
    counter+=1;data['id']=counter;commands.append(data.copy());append('actions.jsonl',{'wall_time':time.time(),'command':data,'before':state.copy()})
   duration=min(15,max(.5,float(data.get('seconds',2))))
   time.sleep(duration)
   with lock:
    result={'state':state,'terminal':terminal(),'events':events};append('action-results.jsonl',{'wall_time':time.time(),'id':data['id'],**result})
   return self.reply(result)
  self.reply({'error':'not found'},404)
http.server.ThreadingHTTPServer(('0.0.0.0',18775),H).serve_forever()

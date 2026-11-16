import os,http.server,urllib.request,urllib.error,json,pathlib,time,threading
OUT=pathlib.Path('/home/steam/dst-eval-runtime')/os.environ.get('DST_RUN_ID','run-001')/'api';OUT.mkdir(parents=True,exist_ok=True)
# A context window is per request; zero disables the separate cumulative budget.
TOKEN_LIMIT=int(os.environ.get('DST_TOKEN_LIMIT','0'))
lock=threading.Lock();total=sum(json.loads(l)["usage"]["total_tokens"] for l in (OUT/"usage.jsonl").read_text().splitlines()) if (OUT/"usage.jsonl").exists() else 0;counter=max([int(p.name.split("-")[0]) for p in OUT.glob("*-request.json")],default=0)
class H(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_GET(self):
  self.send_response(200);self.send_header("Content-Type","application/json");self.end_headers();self.wfile.write(json.dumps({"object":"list","data":[{"id":"deepseek-flash","object":"model","owned_by":"deepseek"}]}).encode())
 def do_POST(self):
  global total,counter
  body=self.rfile.read(int(self.headers['Content-Length']));data=json.loads(body)
  with lock:
   counter+=1;i=counter
  (OUT/f'{i:04d}-request.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
  if TOKEN_LIMIT>0 and total>=TOKEN_LIMIT:
   self.send_error(429,'Evaluation token budget exhausted');return
  data['max_tokens']=min(data.get('max_tokens',4096),4096)
  if TOKEN_LIMIT>0:data['max_tokens']=min(data['max_tokens'],max(1,TOKEN_LIMIT-total))
  if data.get('stream'):data['stream_options']={'include_usage':True}
  req=urllib.request.Request('https://api.deepseek.com'+self.path,json.dumps(data).encode(),{'Content-Type':'application/json','Authorization':self.headers.get('Authorization','')})
  try:
   with urllib.request.urlopen(req,timeout=180) as r:
    self.send_response(r.status);self.send_header('Content-Type',r.headers.get('Content-Type','application/json'));self.end_headers()
    with (OUT/f'{i:04d}-response.txt').open('wb') as f:
     for line in r:
      f.write(line);f.flush();self.wfile.write(line);self.wfile.flush()
      if line.startswith(b'data: '):
       try:
        obj=json.loads(line[6:]);usage=obj.get('usage')
        if usage:
         with lock:total+=usage.get('total_tokens',0)
         with (OUT/'usage.jsonl').open('a') as u:u.write(json.dumps({'call':i,'usage':usage,'cumulative_tokens':total,'model':obj.get('model')})+'\n')
       except json.JSONDecodeError:pass
  except urllib.error.HTTPError as e:
   msg=e.read();(OUT/f'{i:04d}-error.txt').write_bytes(msg);self.send_response(e.code);self.end_headers();self.wfile.write(msg)
  except Exception as e:
   (OUT/f'{i:04d}-transport-error.txt').write_text(type(e).__name__+': '+str(e))
http.server.ThreadingHTTPServer(('0.0.0.0',18766),H).serve_forever()

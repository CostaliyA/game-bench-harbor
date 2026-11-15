import subprocess,tarfile,pathlib
out=pathlib.Path('/root/zyr/game-bench-build');out.mkdir(exist_ok=True)
c=subprocess.check_output(['docker','create','zyr/ootss-harbor-level7:20261115']).decode().strip()
try:
 p=subprocess.Popen(['docker','export',c],stdout=subprocess.PIPE)
 excluded=[];count=0
 with tarfile.open(fileobj=p.stdout,mode='r|') as src,tarfile.open(str(out/'rootfs.tar.gz'),'w:gz',compresslevel=1) as dst:
  for m in src:
   n=m.name.lstrip('./')
   if any(n==x or n.startswith(x+'/') for x in ['opt/steamcmd','app','home/steam/.steam','home/steam/.klei','home/steam/.local/share/Steam','root/.cache','home/steam/.npm','tmp','logs','artifacts']):
    excluded.append(n);continue
   if 'deepseek.env' in n or 'auth.json' in n or 'tokens.json' in n:raise RuntimeError('Unexpected credential filename: '+n)
   dst.addfile(m,src.extractfile(m) if m.isfile() else None);count+=1
 assert p.wait()==0
 (out/'audit.txt').write_text(f'Files retained: {count}\nRemoved prefixes: opt/steamcmd, app, Steam account directories, caches, logs and artifacts.\nRemoved entries: {len(excluded)}\nSource image: zyr/ootss-harbor-level7:20261115\n')
finally:subprocess.run(['docker','rm',c],stdout=subprocess.DEVNULL)

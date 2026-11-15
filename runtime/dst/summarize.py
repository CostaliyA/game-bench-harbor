"""Build a readable complete model-output/action transcript from recorded SSE."""
import argparse,json,pathlib,hashlib,collections
p=argparse.ArgumentParser();p.add_argument('root');a=p.parse_args();root=pathlib.Path(a.root)
rows=[];readable=['# 完整模型返回轨迹\n\n以下 thinking 为 DeepSeek API 实际返回的 reasoning_content；空值表示该次没有返回。工具执行结果另见 actions / action-results / states。\n']
for req in sorted((root/'api').glob('*-request.json')):
 n=req.name.split('-')[0];response=root/'api'/f'{n}-response.txt';data=json.loads(req.read_text());reason=[];content=[];calls={};usage=None;model=None;finish=None
 if response.exists():
  for line in response.read_text().splitlines():
   if not line.startswith('data:') or line[5:].strip()=='[DONE]':continue
   try:r=json.loads(line[5:])
   except ValueError:continue
   model=r.get('model',model);usage=r.get('usage') or usage
   for choice in r.get('choices',[]):
    d=choice.get('delta',{});reason.append(d.get('reasoning_content') or '');content.append(d.get('content') or '');finish=choice.get('finish_reason') or finish
    for t in d.get('tool_calls',[]):
     c=calls.setdefault(t.get('index',0),{'id':'','name':'','arguments':''})
     if t.get('id'):c['id']=t['id']
     f=t.get('function',{});c['name']+=f.get('name','');c['arguments']+=f.get('arguments','')
 row={'call':int(n),'request_file':str(req.relative_to(root)),'response_file':str(response.relative_to(root)) if response.exists() else None,'model':model,'thinking':''.join(reason),'content':''.join(content),'tool_calls':list(calls.values()),'usage':usage,'finish_reason':finish}
 rows.append(row)
 readable.append(f'\n## API 调用 {int(n)}\n\n模型：{model}；usage：{json.dumps(usage)}\n\n### Thinking\n\n'+row['thinking']+'\n\n### Action / 输出\n\n'+row['content']+'\n\n```json\n'+json.dumps(row['tool_calls'],ensure_ascii=False,indent=2)+'\n```\n')
(root/'model-trajectory.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
(root/'thinking-actions.md').write_text(''.join(readable))
summary={'api_attempts':len(rows),'completed_api_calls':sum(r['usage'] is not None for r in rows),'models_returned':sorted(set(r['model'] for r in rows if r['model'])),'tokens':{k:sum((r['usage'] or {}).get(k,0) for r in rows) for k in ['prompt_tokens','completion_tokens','total_tokens']},'reasoning_characters':sum(len(r['thinking']) for r in rows)}
(root/'api-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))

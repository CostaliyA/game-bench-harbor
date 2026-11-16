"""Align unmodified API reasoning excerpts with live recording action timestamps.
Run summarize.py first. Batch actions share the preceding response's reasoning.
The original video is never retimed or trimmed.
"""
import argparse, json, subprocess
from pathlib import Path
from annotate_run import wrap, stamp, safe

p = argparse.ArgumentParser()
p.add_argument('run_dir', type=Path)
p.add_argument('--video', type=Path, help='Original video downloaded from the release')
a = p.parse_args()
r = a.run_dir
load = lambda f: [json.loads(x) for x in (r/f).read_text().splitlines() if x.strip()]
actions = load('actions.jsonl')
results = {x['id']: x for x in load('action-results.jsonl')}
models = [x for x in load('model-trajectory.jsonl') if x['response_completed_at_unix']]
start = float((r/'start-time.txt').read_text())
duration = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(a.video or r/'episode.mp4')]))
terminal = float((r/'terminal-time.txt').read_text()) - start
reward = json.loads((r/'reward.json').read_text())
segments = []
trajectory = []

def add(t, end, title, body, label):
    if end > t:
        segments.append(dict(start=max(0,t),end=min(duration,end),title=title,body=body,label=label))

add(0,actions[0]['wall_time']-start,'DST | DeepSeek Flash | 500k context',
    '上下文上限 500,000；累计 token 不截断；起始自动暂停曾由操作者关闭。','运行设置')
for i, row in enumerate(actions):
    c = row['command']
    preceding = [m for m in models if m['response_completed_at_unix'] <= row['wall_time'] + 0.1]
    if not preceding:
        raise ValueError(f'No preceding model response for action {c["id"]}')
    m = max(preceding, key=lambda x:x['response_completed_at_unix'])
    result = results.get(c['id'])
    trajectory.append({'step':c['id'],'submitted_at_unix':row['wall_time'],'api_call':m['call'],
        'alignment':'latest completed API response before action submission; batch steps share response',
        'command':c,'thinking':m['thinking'],'model_content':m['content'],
        'before':row['before'],'result':result})
    excerpt = ' '.join(m['thinking'].split())
    excerpt = excerpt[:215] + ('…' if len(excerpt)>215 else '')
    if not excerpt:
        excerpt = '该次 API 未返回独立 reasoning；完整工具代码见轨迹。'
    args = ', '.join(f'{k}={v}' for k,v in c.items() if k not in ('id','action') and v not in (None,0,''))
    end = min(actions[i+1]['wall_time']-start if i+1<len(actions) else terminal,terminal)
    add(row['wall_time']-start,end,f'STEP {c["id"]:03d}/{len(actions)} | {c["action"]}({args})',excerpt,f'API {m["call"]} 推理原文摘录')
add(terminal,duration,f'终局 {reward["terminal"]} | reward {reward["reward"]:.2f}',
    '游戏事件与 Harbor verifier 对照见本轮报告；500k 为配置窗口，实际输入长度另行统计。','结果')
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 960
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Noto Sans CJK SC,23,&H00FFFFFF,&H00FFFFFF,&H00101820,&H00101820,0,0,0,0,100,100,0,0,1,0,0,7,28,28,20,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
lines=[]
for s in segments:
    text=r'{\pos(28,738)\fs25\b1\c&H66D9FF&}'+wrap(safe(s['title']),94)+r'{\b0\fs23\c&HFFFFFF&}\N\N'+s['label']+'：'+wrap(safe(s['body']),104)+r'\N{\fs17\c&HAAAAAA&}完整原文与动作返回见 action-trajectory.jsonl / thinking-actions.md；批量动作共享同次推理。'
    lines.append(f'Dialogue: 0,{stamp(s["start"])},{stamp(s["end"])},Main,,0,0,0,,{text}')
(r/'annotations.ass').write_text(header+'\n'.join(lines)+'\n')
(r/'annotations.json').write_text(json.dumps(segments,ensure_ascii=False,indent=2))
(r/'action-trajectory.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in trajectory))
print(json.dumps({'actions':len(actions),'segments':len(segments),'duration':duration,'terminal_video_s':terminal}))

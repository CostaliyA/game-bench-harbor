"""Create action/reasoning subtitles for a recorded trial without changing its timeline.
Usage: python annotate_run.py RUN_DIR --summaries summaries.json
Render: ffmpeg -i episode.mp4 -vf 'pad=iw:960:0:0:color=0x101820,ass=annotations.ass' ...
Summaries map action IDs to concise summaries of the actual model output.
"""
import argparse,json,subprocess,unicodedata
from pathlib import Path

def wrap(s, width=84):
    lines=[];line='';n=0
    for c in s.replace('\n',' '):
        v=2 if unicodedata.east_asian_width(c) in 'WF' else 1
        if n+v>width:lines.append(line);line='';n=0
        line+=c;n+=v
    if line:lines.append(line)
    return r'\N'.join(lines)
def stamp(t):
    t=max(0,round(t*100));return f'{t//360000}:{t//6000%60:02d}:{t//100%60:02d}.{t%100:02d}'
def safe(s):return s.replace('\\','/').replace('{','(').replace('}',')')
def main():
    p=argparse.ArgumentParser();p.add_argument('run_dir',type=Path);p.add_argument('--summaries',type=Path,required=True);a=p.parse_args();r=a.run_dir
    actions=[json.loads(x) for x in (r/'actions.jsonl').read_text().splitlines()]
    summaries=json.loads(a.summaries.read_text());start=float((r/'start-time.txt').read_text())
    duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(r/'episode.mp4')]))
    segments=[]
    budget=json.loads((r/'budget-stop.json').read_text()) if (r/'budget-stop.json').exists() else None
    terminal_path=r/'terminal-time.txt'
    stop=min(duration,float(terminal_path.read_text())-start) if terminal_path.exists() else (min(duration,budget['elapsed_wall_s']) if budget else duration)
    def add(t,end,title,body,label='推理摘要'):
        if end>t:segments.append(dict(start=max(0,t),end=min(duration,end),title=title,body=body,label=label))
    add(0,actions[0]['wall_time']-start,'DST | DeepSeek Flash | 新一轮实测','固定朝向 45° · 原速录像 · 模型读取局部结构化状态')
    for i,row in enumerate(actions):
        c=row['command'];sid=str(c['id']);assert sid in summaries,f'Missing reasoning summary: {sid}'
        end=actions[i+1]['wall_time']-start if i+1<len(actions) else stop
        end=min(end,stop)
        args=', '.join(f'{k}={v}' for k,v in c.items() if k not in ['id','action'] and v not in [None,0,''])
        add(row['wall_time']-start,end,f'STEP {c["id"]:02d}/{len(actions)} | {c["action"]}({args})',summaries[sid])
    if budget:
        add(stop,duration,'预算终止 | 本轮动作已结束',f"累计 {budget['tokens']:,} token；达到预算上限。最终判分与异常详情见本轮报告。",'结果')
    elif terminal_path.exists():
        status=json.loads((r/'final-status.json').read_text())
        event=next((e for e in reversed(status.get('events',[])) if e.get('type') in ['dawn','death','timeout','abort','invalid']),{})
        reward=json.loads((r/'reward.json').read_text()) if (r/'reward.json').exists() else {}
        add(stop,duration,'回合结束 | '+event.get('type','terminal'),f"reward={reward.get('reward','待评分')}；成功={reward.get('success',False)}。结果由游戏事件核验。",'结果')
    header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 960
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Noto Sans CJK SC,25,&H00FFFFFF,&H00FFFFFF,&H00101820,&H00101820,0,0,0,0,100,100,0,0,1,0,0,7,28,28,20,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    rows=[]
    for s in segments:
        title=wrap(safe(s['title']),88);body=wrap(safe(s['body']),86)
        text=r'{\pos(28,738)\fs27\b1\c&H66D9FF&}'+title+r'{\b0\fs25\c&HFFFFFF&}\N\N'+s['label']+'：'+body+r'\N{\fs18\c&HAAAAAA&}据本轮模型原始 reasoning 整理；完整记录见 thinking-actions.md'
        rows.append(f'Dialogue: 0,{stamp(s["start"])},{stamp(s["end"])},Main,,0,0,0,,{text}')
    (r/'annotations.ass').write_text(header+'\n'.join(rows)+'\n')
    (r/'annotations.json').write_text(json.dumps(segments,ensure_ascii=False,indent=2))
    print(json.dumps({'actions':len(actions),'duration':duration,'segments':len(segments)}))
if __name__=='__main__':main()

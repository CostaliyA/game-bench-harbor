"""Postprocess settlement video with actions and recorded model reasoning.

Run the frozen runtime's summarize.py first. Render annotations.ass onto a
1280x1080 canvas (720 original pixels plus a 360-pixel caption panel).
This script does not alter evaluation rules or the original recording.
"""
import argparse
import importlib.util
import json
import subprocess
import unicodedata
from pathlib import Path

def wrap(text, width=96):
    lines, line, length = [], '', 0
    for char in text.replace('\n', ' '):
        size = 2 if unicodedata.east_asian_width(char) in 'WF' else 1
        if length + size > width:
            lines.append(line); line, length = '', 0
        line += char; length += size
    if line: lines.append(line)
    return r'\N'.join(lines)

def stamp(t):
    n = max(0, round(t * 100))
    return f'{n // 360000}:{n // 6000 % 60:02d}:{n // 100 % 60:02d}.{n % 100:02d}'

def safe(s):
    return str(s).replace('\\', '/').replace('{', '(').replace('}', ')')

p = argparse.ArgumentParser()
p.add_argument('run_dir', type=Path)
p.add_argument('--summaries', type=Path, help='Action ID -> faithful summary of that API response')
p.add_argument('--tail-seconds', type=float, default=8, help='Retain this much paused footage after the terminal event')
a = p.parse_args(); r = a.run_dir
load = lambda f: [json.loads(line) for line in (r / f).read_text().splitlines() if line.strip()]
actions = load('actions.jsonl')
results = {row['id']: row for row in load('action-results.jsonl')}
models = [row for row in load('model-trajectory.jsonl') if row['response_completed_at_unix']]
summaries = json.loads(a.summaries.read_text()) if a.summaries else {}
start = float((r / 'start-time.txt').read_text())
terminal = float((r / 'terminal-time.txt').read_text()) - start
original_duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', str(r / 'episode.mp4')]))
duration = min(original_duration, terminal + max(0, a.tail_seconds))
reward = json.loads((r / 'reward.json').read_text())
spec = importlib.util.spec_from_file_location('frozen_reward', r / 'used-runtime/tasks/dst-science-settlement/tests/reward.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
segments, trajectory = [], []

def add(begin, end, title, body, label, status=''):
    begin, end = max(0, begin), min(duration, end)
    if end > begin:
        segments.append(dict(start=begin, end=end, title=title, body=body, label=label, status=status))

add(0, actions[0]['wall_time'] - start, 'DST | Science Settlement v1 | DeepSeek Flash',
    '目标：第三天清晨建成科学营地，保留装备、食物和燃料。500k 配置窗口，实时世界，正式开始后无人工游戏操作。', '固定任务')
for index, row in enumerate(actions):
    command = row['command']; state = row['before']; sid = str(command['id'])
    preceding = [m for m in models if m['response_completed_at_unix'] <= row['wall_time'] + .1]
    assert preceding, f'No preceding API response for action {sid}'
    model = max(preceding, key=lambda m: m['response_completed_at_unix'])
    raw = ' '.join(model['thinking'].split())
    body = summaries.get(sid) or (raw[:240] + ('…' if len(raw) > 240 else ''))
    if not body: body = '该次 API 未返回独立 reasoning；完整工具代码见轨迹文件。'
    label = f'API {model["call"]} reasoning ' + ('摘要' if sid in summaries else '原文摘录')
    args = []
    for key, value in command.items():
        if key in ('id', 'action') or value in (None, 0, ''): continue
        args.append(f'{key}={value:.2f}' if isinstance(value, float) else f'{key}={value}')
    progress = state.get('progress') or {}
    milestones = progress.get('milestones') or {}
    points = sum(module.WEIGHTS[name] for name in milestones if name in module.WEIGHTS)
    status = (f'动作前状态 | Day {state["cycle"] + 1} {state["phase"]} | '
              f'HP {state["health"]:.1f}  Hunger {state["hunger"]:.1f}  Sanity {state["sanity"]:.1f} | 阶段分 {points:.3f}')
    end = min(actions[index + 1]['wall_time'] - start if index + 1 < len(actions) else terminal, terminal)
    add(row['wall_time'] - start, end, f'STEP {command["id"]:03d}/{len(actions)} | {command["action"]}({", ".join(args)})', body, label, status)
    trajectory.append({'step': command['id'], 'submitted_at_unix': row['wall_time'], 'api_call': model['call'],
        'alignment': 'Latest completed API response preceding action submission; batch actions share reasoning.',
        'command': command, 'thinking': model['thinking'], 'model_content': model['content'],
        'video_summary': summaries.get(sid), 'before': state, 'result': results.get(command['id'])})
add(terminal, duration, f'终局 {reward["terminal"]} | reward {reward["reward"]:.3f} | success {reward["success"]}',
    '分数由开跑前冻结的规则重算；完整 API reasoning、动作返回与逐项分析见本轮报告。旧首夜任务的 1.00 分保留。', '结果')

header = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 1080
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Noto Sans CJK SC,23,&H00FFFFFF,&H00FFFFFF,&H00101820,&H00101820,0,0,0,0,100,100,0,0,1,0,0,7,28,28,20,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
lines = []
for s in segments:
    blocks = [
        (738, 25, '&H66D9FF&', wrap(safe(s['title']), 88)),
        (808, 20, '&HAAAAAA&', safe(s['label'])),
        (837, 23, '&HFFFFFF&', wrap(safe(s['body']), 100)),
        (978, 20, '&H66D9FF&', safe(s['status'])),
        (1031, 16, '&HAAAAAA&', '原速连续录像；摘要仅据该次模型原文整理。完整记录：action-trajectory.jsonl / thinking-actions.md'),
    ]
    for y, size, colour, text in blocks:
        if text:
            text = rf'{{\pos(28,{y})\fs{size}\c{colour}}}' + text
            lines.append(f'Dialogue: 0,{stamp(s["start"])},{stamp(s["end"])},Main,,0,0,0,,{text}')
(r / 'annotations.ass').write_text(header + '\n'.join(lines) + '\n')
(r / 'annotations.json').write_text(json.dumps(segments, ensure_ascii=False, indent=2) + '\n')
(r / 'action-trajectory.jsonl').write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in trajectory))
metadata = {'actions': len(actions), 'segments': len(segments), 'original_video_duration': original_duration,
            'annotated_video_duration': duration, 'terminal_video_seconds': terminal,
            'editing': 'Original retained unchanged. Annotated export removes only paused footage after terminal + tail-seconds; gameplay is not sped up or trimmed.'}
(r / 'video-timing.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(metadata))

"""Annotate browser screenshots with action feedback and linked reasoning excerpts."""

import argparse
import json
import pathlib
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont


W, H, GAME_W = 1280, 728, 720
FONT_PATH = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
SOURCE_LABEL = '浏览器原始渲染 · 画面缩放'
ACT = {'up': '上', 'down': '下', 'left': '左', 'right': '右',
       'switch': '切换', 'activate': '激活', 'undo': '撤销', 'reset': '重置'}
WHY = {'walk': '移动成功', 'swap': '交换成功', 'switch': '切换英雄',
       'reset': '回到初始局面', 'blocked': '受阻，局面未变',
       'no_rod': '没有法杖'}


def font(size):
    return ImageFont.truetype(FONT_PATH, size)


def draw_wrapped(draw, xy, text, max_width, size, color, max_lines=None, line_gap=5):
    f = font(size)
    x, y = xy
    lines = []
    for paragraph in text.split('\n'):
        line = ''
        for word in paragraph.split(' '):
            trial = (line + ' ' + word).strip()
            if draw.textlength(trial, font=f) > max_width and line:
                lines.append(line)
                line = word
            else:
                line = trial
        lines.append(line)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] += '…'
    for line in lines:
        draw.text((x, y), line, font=f, fill=color)
        y += size + line_gap
    return y


def reason_excerpt(text, limit=550):
    text = ' '.join(text.split())
    if len(text) <= limit:
        return text
    return '…' + text[-limit:]


def select_key(trace):
    keys = {0, len(trace)}
    for i, e in enumerate(trace, 1):
        before, after = e['before']['state'], e['after']['state']
        b_rod = [h['kind'] for h in before['heroes'] if h['rod']]
        a_rod = [h['kind'] for h in after['heroes'] if h['rod']]
        if e['action'] in ('reset', 'activate') or e['feedback']['reason'] == 'swap' or b_rod != a_rod:
            keys.add(i)
    return keys


def frame(src, entry, step, total, reasoning, key):
    img = Image.open(src).convert('RGB').resize((GAME_W, H), Image.LANCZOS)
    out = Image.new('RGB', (W, H), '#101827')
    out.paste(img, (0, 0))
    d = ImageDraw.Draw(out)
    d.rectangle((GAME_W, 0, GAME_W + 5, H), fill='#3b82f6')
    x = GAME_W + 27
    d.text((x, 20), '沉星秩序 · 第 7 关', font=font(25), fill='#f8fafc')
    d.text((x, 57), SOURCE_LABEL, font=font(17), fill='#93c5fd')
    d.line((x, 96, W - 27, 96), fill='#334155', width=2)
    d.text((x, 111), f'STEP {step:03d} / {total:03d}', font=font(30), fill='#facc15')
    if entry:
        action = entry['action']
        why = entry['feedback']['reason']
        d.text((x, 157), f'动作  {ACT.get(action, action)}  ({action})', font=font(20), fill='#f8fafc')
        d.text((x, 188), f'反馈  {WHY.get(why, why)}', font=font(19),
               fill='#86efac' if entry['feedback']['changed'] else '#fca5a5')
    else:
        d.text((x, 157), '初始画面', font=font(20), fill='#f8fafc')
    d.line((x, 229, W - 27, 229), fill='#334155', width=2)
    d.text((x, 245), '模型 reasoning · 原文节选', font=font(21), fill='#facc15')
    if reasoning:
        d.rounded_rectangle((x - 8, 283, W - 22, 660), radius=12, fill='#1e3a5f')
        draw_wrapped(d, (x + 8, 301), reason_excerpt(reasoning), W - x - 62,
                     18, '#f8fafc', max_lines=14, line_gap=5)
    else:
        draw_wrapped(d, (x, 301), '该步之前没有单独的 reasoning 记录。',
                     W - x - 46, 18, '#94a3b8')
    if key:
        d.rounded_rectangle((W - 119, 102, W - 27, 137), radius=7, fill='#7c3aed')
        d.text((W - 110, 106), '关键步骤', font=font(16), fill='#fff')
    d.text((x, 686), '完整原文见 reasoning.jsonl', font=font(16), fill='#94a3b8')
    return out


def end_card(total, resets, blocked, reward, reasoning_events):
    out = Image.new('RGB', (W, H), '#101827')
    d = ImageDraw.Draw(out)
    d.rectangle((0, 0, 14, H), fill='#3b82f6')
    d.text((51, 49), '沉星秩序 · 第 7 关', font=font(29), fill='#93c5fd')
    d.text((51, 135), '本次推理试跑已记录', font=font(43), fill='#facc15')
    d.line((51, 211, W - 51, 211), fill='#334155', width=2)
    lines = [
        f'{total} 个动作 · {resets} 次重置 · {blocked} 次局面未变 · 奖励 {reward}',
        f'OpenCode 日志记录 {reasoning_events} 段 reasoning。',
        '视频按动作显示对应 reasoning 的原文末段；',
        '完整、未经删改的文本保存在 reasoning.jsonl。',
    ]
    y = 261
    for line in lines:
        d.text((57, y), line, font=font(27), fill='#f8fafc')
        y += 72
    d.text((51, H - 67), '来源：DeepSeek reasoning_content → OpenCode reasoning 事件',
           font=font(18), fill='#94a3b8')
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--frames', type=pathlib.Path, required=True)
    ap.add_argument('--trace', type=pathlib.Path, required=True)
    ap.add_argument('--reasoning', type=pathlib.Path, required=True)
    ap.add_argument('--reward', type=int, choices=(0, 1), required=True)
    ap.add_argument('--out', type=pathlib.Path, required=True)
    args = ap.parse_args()
    trace = [json.loads(l) for l in args.trace.read_text().splitlines()]
    records = [json.loads(l) for l in args.reasoning.read_text().splitlines()]
    linked = {}
    for record in records:
        if record['type'] == 'reasoning':
            for step in record.get('steps', []):
                linked[step] = (linked.get(step, '') + '\n' + record['text']).strip()
    total = len(trace)
    assert all(e['step'] == i for i, e in enumerate(trace, 1))
    keys = select_key(trace)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        temp = pathlib.Path(td)
        listing = []
        last = None
        for step in range(total + 1):
            src = args.frames / f'{step:04d}.png'
            if not src.exists():
                raise FileNotFoundError(src)
            dest = temp / f'{step:04d}.png'
            frame(src, trace[step - 1] if step else None, step, total,
                  linked.get(step, ''), step in keys).save(dest)
            listing.extend((f"file '{dest}'", f'duration {3.5 if step in keys else 0.8}'))
            last = dest
        dest = temp / 'end.png'
        end_card(total, sum(e['action'] == 'reset' for e in trace),
                 sum(not e['feedback']['changed'] for e in trace), args.reward,
                 sum(r['type'] == 'reasoning' for r in records)).save(dest)
        listing.extend((f"file '{dest}'", 'duration 8.0', f"file '{dest}'"))
        manifest = temp / 'concat.txt'
        manifest.write_text('\n'.join(listing) + '\n')
        subprocess.run([
            'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-safe', '0',
            '-f', 'concat', '-i', str(manifest), '-vf', 'fps=10,format=yuv420p',
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '25',
            '-movflags', '+faststart', str(args.out),
        ], check=True)
    print(args.out)


if __name__ == '__main__':
    main()

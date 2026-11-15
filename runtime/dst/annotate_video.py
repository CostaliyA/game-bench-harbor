import json,pathlib
r=pathlib.Path(__file__).resolve().parents[1]/'evidence/deepseek-flash-001'
start=float((r/'start-time.txt').read_text());actions=[json.loads(l) for l in (r/'actions.jsonl').read_text().splitlines()]
summaries={1:'先采最近的树苗取得树枝，再采草并寻找燧石。',2:'观察到时间与状态未变化，尝试小幅移动判断是否能恢复。',3:'发现 active 已变为 true，认为此前的采集指令开始执行。',4:'采集仍在进行，继续等待并观察。',5:'时间没有推进，怀疑角色或模拟卡住，再等待确认。',6:'状态持续不变，重新提交采树苗动作。',7:'尝试等待 15 秒，比较游戏时间是否变化。',8:'确认取得树枝，移动到附近草丛，继续寻找燧石。',9:'已经到达草丛附近，执行采集。',10:'已有 1 份草，向北探索更多草和燧石。',11:'燧石是当前缺少的材料；先向西侧草丛移动。',12:'采集眼前草丛，准备凑齐 3 份草。',13:'确认草已有 2 份，移动到下一株草附近。',14:'发现附近有燧石；先采第三份草。',15:'草和树枝已够，向燧石位置移动。',16:'尝试对地面的燧石使用 pick。',17:'燧石尚未取得，等待动作完成。',18:'识别出地面物品需要 pickup，切换动作重新拾取。',19:'已经取得燧石，现在制作斧头。',20:'准备装备斧头，再砍附近的树；还需木材建火和续燃。',21:'装备反馈失败，尝试直接砍树，观察是否可自动装备。',22:'一次砍击尚未掉木材，继续砍同一棵树。',23:'用最多 12 次循环砍树；背包出现木材或目标 ID 消失时停止。'}
for i in range(24,35):summaries[i]=summaries[23]
notes={1:'现场说明：启动同步异常，模型前几次指令未立即执行。',2:'现场说明：这是对启动卡住的判断，不是正常采集阶段。',3:'现场说明：active=true 后仍受到暂停菜单影响。',7:'现场说明：随后关闭暂停菜单，游戏时间开始持续推进。',16:'动作区别：pick 用于采植物；地面燧石应使用 pickup。',18:'结果：基础材料里程碑达成，reward 增至 0.10。',19:'结果：制斧里程碑达成，reward 增至 0.30。',20:'接口反馈：本次使用 item 参数；工具约定装备物品应传 target。',23:'循环判断仅检查背包木材和目标 ID，没有检查 chop=false。'}
for i in range(24,35):notes[i]='事后观察：树倒后实体 ID 仍存在；木头在地上，循环未触发退出。'
def ts(t):
 t=max(0,round(t*100));return f'{t//360000}:{t//6000%60:02d}:{t//100%60:02d}.{t%100:02d}'
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 960
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Noto Sans CJK SC,26,&H00FFFFFF,&H00FFFFFF,&H00101820,&H00101820,0,0,0,0,100,100,0,0,1,0,0,7,28,28,20,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
rows=[];segments=[]
def add(a,b,title,thought,note):
 text='{\\pos(28,742)\\fs30\\b1\\c&H66D9FF&}'+title+'{\\b0\\fs25\\c&HFFFFFF&}\\N\\N模型推理摘要：'+thought+'\\N{\\fs22\\c&HBCD7E6&}'+note+'\\N{\\fs18\\c&H999999&}摘要据 DeepSeek 实际返回整理；完整原文见 thinking-actions.md'
 rows.append(f'Dialogue: 0,{ts(a)},{ts(b)},Main,,0,0,0,,{text}')
 segments.append(dict(start=a,end=b,title=title,reasoning_summary=thought,note=note))
add(0,actions[0]['wall_time']-start,'DST 首夜任务  |  DeepSeek Flash × OpenCode × Harbor','先调用 observe，读取局部环境与任务起点。','原速完整录像 · 10 FPS · 固定 seed 341784114 · 本轮含启动排障')
for n,a in enumerate(actions):
 c=a['command'];i=c['id'];t=a['wall_time']-start;end=actions[n+1]['wall_time']-start if n+1<len(actions) else 341.8
 if c['action']=='move':arg=f"x={c['x']}, z={c['z']}"
 elif c.get('recipe'):arg='recipe='+c['recipe']
 elif c.get('target'):arg='target='+str(c['target'])
 elif c.get('item'):arg='item='+str(c['item'])
 else:arg=f"seconds={c['seconds']}"
 add(t,end,f"STEP {i:02d} / 34  |  ACTION: {c['action']}({arg})",summaries[i],notes.get(i,'按实际动作提交时间对齐；执行结果可能晚于动作提交。'))
add(341.8,361.6,'回合结束  |  reward = 0.30  |  success = false','最后观察到砍树动作持续 running，准备重新检查环境。','终止：累计 524,901 token，超过 500k 阈值；木材未拾取，未建火过夜。')
(r/'video-annotations.ass').write_text(header+'\n'.join(rows)+'\n')
(r/'video-annotations.json').write_text(json.dumps(segments,ensure_ascii=False,indent=2))

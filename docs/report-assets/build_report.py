from pathlib import Path
import html, os
from weasyprint import HTML
R=Path(__file__).resolve().parent

def svg_flow(name, boxes, sub, accent='#267c78'):
 w=1040;h=190;n=len(boxes);bw=190 if n==4 else 150;gap=(w-40-n*bw)/(n-1)
 s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{accent}"/></marker></defs>']
 for i,(title,detail) in enumerate(boxes):
  x=20+i*(bw+gap)
  s.append(f'<rect x="{x}" y="25" width="{bw}" height="100" rx="10" fill="#f2f6f5" stroke="{accent}" stroke-width="1.4"/>')
  s.append(f'<text x="{x+bw/2}" y="65" text-anchor="middle" font-family="Noto Sans CJK SC" font-size="22" fill="#182d40">{html.escape(title)}</text>')
  s.append(f'<text x="{x+bw/2}" y="97" text-anchor="middle" font-family="Noto Sans CJK SC" font-size="16" fill="#526273">{html.escape(detail)}</text>')
  if i<n-1:s.append(f'<path d="M{x+bw+5},75 H{x+bw+gap-8}" stroke="{accent}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
 s.append(f'<text x="520" y="166" text-anchor="middle" font-family="Noto Sans CJK SC" font-size="18" fill="#526273">{html.escape(sub)}</text></svg>')
 (R/name).write_text(''.join(s))
svg_flow('dst-flow.svg',[('OpenCode','规划与工具选择'),('MCP / HTTP','观察与命令队列'),('Lua Mod','原生动作 + 状态读取'),('真实 DST','世界持续模拟')],'状态与动作结果返回模型；游戏事件单独送入评分器')
svg_flow('ootss-flow.svg',[('Agent 试玩','发现规则与疑点'),('人类先验 / 攻略','补充机制与解题约束'),('Agent 复现','棋盘 + 规则 + 渲染'),('参考解与重放','检查状态转移与终局')],'将关卡规则写成显式状态转移；模型评测时不提供参考解',accent='#ab7835')
svg_flow('eval-flow.svg',[('Harbor','组织 trial 与预算'),('OpenCode','上下文与 MCP 工具'),('游戏 sandbox','观察 → 动作 → 状态'),('Verifier','校验轨迹 / 写 reward')],'模型：DeepSeek V4.1 Flash（配置名称）；API model ID：deepseek-flash')

style='''
@font-face{font-family:Body;src:url('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')}
@font-face{font-family:Body;src:url('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc');font-weight:700}
@font-face{font-family:Title;src:url('/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc')}
@page{size:A4;margin:17mm 18mm 17mm;@top-left{content:'GAME BENCH HARBOR';font-family:Body;font-size:8pt;color:#7a858f;letter-spacing:1pt}@top-right{content:'实验与实现报告 · 2026.11';font-family:Body;font-size:8pt;color:#7a858f}@bottom-left{content:'DST / ORDER OF THE SINKING STAR';font-family:Body;font-size:7pt;color:#7a858f}@bottom-right{content:counter(page);font-family:Body;font-size:9pt;color:#267c78}}
*{box-sizing:border-box}body{font-family:Body,sans-serif;font-size:10.2pt;line-height:1.75;color:#263644;margin:0}p{margin:0 0 3mm;text-align:justify}h1,h2,h3{color:#182d40;line-height:1.35;margin:0}h1{font-family:Title;font-weight:400;font-size:29pt;letter-spacing:-.6pt;margin:5mm 0}h2{font-family:Title;font-weight:400;font-size:21pt;margin:2mm 0 5mm}h3{font-size:12.4pt;margin:4mm 0 2.5mm;font-weight:700}.page{break-after:page}.page:last-child{break-after:auto}.eyebrow{font-size:9pt;color:#267c78;letter-spacing:1pt;font-weight:700;margin-bottom:3mm}.sub{font-size:12pt;color:#627181;line-height:1.6;margin-bottom:5mm}.lead{font-size:12pt;line-height:1.85;color:#1c3445;margin-bottom:5mm}.rule{height:1mm;background:#267c78;margin:5mm 0}.small{font-size:8.5pt;line-height:1.65;color:#65717b}.caption{text-align:left;font-size:8.2pt;line-height:1.65;color:#667481;margin:2mm 0 4mm}.box{background:#f1f6f5;padding:4mm 4.5mm;margin:4mm 0;border-left:2pt solid #267c78}.warm{background:#faf5ed;border-color:#ab7835}.box p:last-child{margin-bottom:0}.two{display:flex;gap:6mm}.two>div{flex:1;min-width:0}.third{display:flex;gap:5mm}.third>div{flex:1}.num{font-size:24pt;color:#267c78;line-height:1.3}.stat-label{font-size:8.5pt;color:#627181}.stats{border-top:1pt solid #d7e0df;border-bottom:1pt solid #d7e0df;padding:4mm 0;margin:5mm 0}.figure{width:100%;display:block}.flow{width:100%;margin:2mm 0 0}table{border-collapse:collapse;width:100%;font-size:9.1pt;line-height:1.6;margin:3mm 0 4mm}th{background:#edf3f3;color:#233a49;text-align:left;font-weight:700;border-bottom:1pt solid #9eb8b6;padding:2.5mm}td{vertical-align:top;border-bottom:.5pt solid #dbe2e5;padding:2.6mm}tr{break-inside:avoid}strong{font-weight:700}code{font-family:DejaVu Sans Mono,monospace;font-size:8.8pt;background:#f0f3f4;padding:0 .6mm}.quote{border-left:2pt solid #b28b50;padding:3mm 4mm;margin:3mm 0;font-family:Body;font-size:10.4pt;background:#faf6ef;line-height:1.65}.quote small{display:block;font-size:8pt;color:#7a725f;margin-top:2mm}.refs{font-size:8.6pt;line-height:1.7}.refs p{margin-bottom:2.5mm;text-align:left}a{color:#267c78;text-decoration:none}.timeline td:first-child{width:18mm;color:#267c78;font-weight:700}.kicker{font-size:9pt;color:#8b734b;margin-bottom:2mm}.photo-row{display:flex;align-items:flex-start;gap:6mm;margin:4mm 0}.photo-row .aside{flex:1;font-size:9.5pt}.photo-row img{display:block}.tight{margin-bottom:1mm}ul{padding-left:5mm;margin:2mm 0 4mm}li{margin:1.2mm 0}.codeblock{background:#152c3b;color:#e5eeed;font-family:DejaVu Sans Mono,Body;font-size:8.7pt;line-height:1.75;white-space:pre-wrap;padding:4mm;margin:3mm 0}.tag{font-size:8pt;color:#267c78}.keyline{font-size:13pt;font-family:Title;color:#1e4b50;margin:4mm 0}.spacer{height:4mm}
'''
P=[]
P.append('''<section class="page">
<div class="eyebrow">游戏环境 Agent Benchmark · 技术报告</div>
<h1>饥荒与沉星之序<br>Agent 评测环境构造与分析</h1>
<div class="sub">Sandbox 实现、任务设计与模型实测</div><div class="rule"></div>
<h2>任务分析</h2>
<p class="lead">本项目将两款游戏中的有限任务接入 Harbor，构造可交互、可复现、可自动判分的 Agent 评测环境。任务设计需要保留游戏中的核心决策难点，同时明确初始状态、动作边界与成功条件。</p>
<p>饥荒属于持续运行的开放世界。资源采集、工具制作与生存目标存在前置依赖，动作还受距离、对象状态和昼夜变化影响。因此，评测选取“从空背包完成首夜生存”作为任务，部署真实 DST 客户端，通过 Lua 桥接提供局部状态和原生动作接口，保留资源消耗与实时模拟。</p>
<p>沉星之序属于规则驱动的空间谜题。固定关卡的动作集合有限，但角色交换、物件推动与出口位置共同约束可行路径。因此，评测选取 Heroes and Artifacts 7 双角色关卡，由我使用 Agent，结合人类先验和公开攻略复现规则与棋盘，以离散步进方式检查多步空间规划。</p>
<p>两类环境分别采用游戏事件核验与确定性轨迹重放进行评分。实验使用 OpenCode 作为 Agent harness，接入 DeepSeek V4.1 Flash，保存模型推理、动作、状态与过程视频，以定位任务进展及失败环节。</p>

</section>''')
P.append('''<section class="page">
<div class="eyebrow">01 / 游戏差异</div><h2>游戏机制与交互时序</h2>
<h3>开放世界：资源依赖与持续变化</h3>
<p>饥荒的决策对象包括植物、地面物品、工具和建筑，同一资源在不同状态下对应不同操作。例如，树需要装备斧头后砍伐，掉落的木材需要另行拾取，进入背包后才能用于建火。Agent 必须同时判断对象、动作前提和完成条件，并在局部观察中寻找缺失资源。</p>
<img class="figure" src="dst-crafting.png" style="width:140mm;margin:auto"/>
<div class="caption">图 1　DST 实测画面，约 04:10。模型已收集材料并制斧，后续需取得木材与建立营火。</div>
<div class="photo-row"><img src="ootss-initial.png" style="width:88mm"/><div class="aside"><h3>规则谜题：角色协作与空间约束</h3><p>Heroes and Artifacts 7 包含两名角色、两个出口、巨石和 Rod。棋盘整体可见，但可行路径取决于当前角色、朝向、持有物及物件位置。</p><p>交换或推动会改变后续通路。单人接近出口并不一定推进整体目标，有时必须先让位或调整巨石，为另一名角色建立路径。难点集中在规则归纳与动作顺序，而非操作种类。</p><p class="caption">图 2　本项目复现关卡的初态：两名角色需要借助巨石与 Rod，分别到达两个出口。</p></div></div>
<p>两者的时间约束也不同：DST 在模型推理期间继续运行，探索和重复操作会占用白天；沉星之序在等待动作时保持静止，可使用更长推理进行空间推演。前者要求在时间压力下更新计划，后者要求维持跨步骤的状态一致性。</p>
</section>''')
P.append('''<section class="page">
<div class="eyebrow">01 / 从游戏结构到任务切片</div><h2>能力要求与任务边界</h2>
<table><thead><tr><th style="width:22%">比较项</th><th>饥荒 / DST</th><th>沉星之序关卡</th></tr></thead><tbody>
<tr><td>环境结构</td><td>开放世界，局部可见；资源、角色与昼夜持续变化。</td><td>有限棋盘；角色与物件遵循显式规则。</td></tr>
<tr><td>动作空间</td><td>移动、采集、拾取、制作、装备、砍树、进食、烹饪、加燃料等；动作带实体或坐标参数。</td><td>四方向移动、角色切换、激活、撤销、重置，共 8 个离散动作。</td></tr>
<tr><td>时序</td><td>实时运行；推理与动作执行共同消耗游戏时间。</td><td>离散步进；模型思考时棋盘保持不变，动作执行后才转移状态。</td></tr>
<tr><td>关键能力</td><td>局部探索、资源依赖规划、对象交互、动作完成判断、生存压力下的调度。</td><td>未知规则归纳、角色与朝向跟踪、空间推演、跨角色的因果规划。</td></tr>
<tr><td>主要风险</td><td>观察已经过时；动作没做完；资源掉在地上却误认为已取得。</td><td>局部移动正确，但全局布局错误；混淆当前角色，反复撤销或重置。</td></tr>
</tbody></table>
<div class="two"><div><h3>DST：依赖链与时间预算</h3><p>首夜任务从第 1 天清晨、空背包开始，要求按“材料—斧头—木材—营火”推进。资源位置决定探索路径，剩余白昼决定行动优先级。Agent 既要分解依赖关系，也要在寻路、采集和建造后确认实际结果，及时处理目标失效。</p></div><div><h3>沉星之序：联合状态与因果规划</h3><p>双出口任务要求共同安排两名角色与物件的位置。动作是否合法只是第一层判断，还需预测其是否保留后续解法。撤销和重置允许试探，但有效探索需要记住失败布局及其原因，避免重复进入无进展的状态。</p></div></div>
<h3>环境实现与验证方式</h3><p>DST 的资源消耗、寻路、动作动画和昼夜系统相互耦合，部署原游戏能保留这些机制，接口层主要处理状态采样与异步执行。沉星之序的固定棋盘可表示为有限状态转移，适合通过规则复现控制初态和逐步回放。相应地，前者使用游戏事件验证里程碑，后者通过动作重放检查状态与终局。</p>

</section>''')
P.append('''<section class="page">
<div class="eyebrow">02 / Sandbox 构造</div><h2>DST：原生模拟与动作桥接</h2>
<p>正版 DST Linux 客户端在 A800 上以单人离线世界运行，Xvfb 提供显示环境，Lua 代码在主模拟端访问角色和实体。外部 Agent 通过 MCP 调用观察和动作工具，HTTP 服务负责交换状态与命令。</p>
<img class="flow" src="dst-flow.svg"/>
<h3>原生动作封装</h3>
<p>桥接层将命令转成游戏原生的 <code>BufferedAction</code>、寻路和 <code>Builder</code> 调用。例如，<code>pick</code> 用于植物采集，<code>pickup</code> 用于拾取地面物品；<code>craft</code> 检查配方和材料，再由原游戏消耗材料。模型无需处理每一次鼠标定位，但仍要选对对象和动作。</p>
<table><tr><th>接口约束</th><th>本轮设置</th></tr><tr><td>局部观察</td><td>半径 25 世界单位；背包、生命/饥饿/理智、附近实体与制作配方。</td></tr><tr><td>移动与建造</td><td>单次移动不超过 30 单位；建造点距角色不超过 6 单位。</td></tr><tr><td>采样与录制</td><td>状态每 0.5 游戏秒采样；命令每 0.25 游戏秒轮询；录像为 10 FPS。</td></tr><tr><td>调用返回</td><td>等待 0.5–15 墙钟秒后返回状态；返回时原生动作可能尚未完成。</td></tr></table>
<h3>初始状态与存档恢复</h3>
<p>本轮 seed 为 <strong>341784114</strong>，build 为 <strong>762172</strong>。我封存了世界和 Wilson 的完整快照：第 1 天秋季清晨、空背包、生命 150、饥饿 150、理智 200。只固定地图 seed，无法固定已经被采走的资源、角色位置和游戏时钟；重复实验应恢复同一份存档。</p>
<div class="box"><p>本轮启动时修复了暂停同步；存档快照已封存，按 trial 自动恢复基线尚未接入。</p></div>
</section>''')
P.append('''<section class="page">
<div class="eyebrow">02 / Sandbox 构造</div><h2>沉星之序：关卡规则复现</h2>
<p>我在 Joric 公开引擎与关卡资料基础上，使用 Agent 试玩、生成代码和调试，结合自身规则理解及网上攻略复现固定关卡。实现过程中由我补充机制约束、检查异常，并校验动作结果。</p>
<img class="flow" src="ootss-flow.svg"/>
<h3>状态转移实现与验证</h3>
<p>实现分为棋盘数据、转移规则和渲染三部分。<code>board.json</code> 保存固定布局；Joric 引擎与关卡扩展处理行走、Wizard 交换、Rod 推动以及切换、撤销和重置；浏览器渲染棋盘和 HUD，MCP 只向被测模型返回截图与公开动作反馈。</p>
<p>状态转移表示为 <code>sₜ₊₁ = T(sₜ, aₜ)</code>。固定初态与动作序列后，Judge 逐步重放并核对记录状态，定位首次不一致的步骤。</p>
<h3>参考解与环境验收</h3>
<p>依据公开攻略构造参考路径，展开角色切换后共 97 个 MCP 动作，存入 <code>solution/</code>，仅供环境验收使用。发布版通过 Harbor 执行参考解，得到 <strong>reward=1.00、0 个运行异常</strong>。</p>
<p>规则、初态与动作转移由代码统一控制，便于构造回归轨迹和定位规则错误。参考解通过验证了环境内部的可解性；交换、推动和朝向等机制与商业原版的一致性仍需逐项对照。</p>
</section>''')
P.append('''<section class="page">
<div class="eyebrow">03 / 任务与 Reward</div><h2>任务目标与奖励定义</h2>
<h3>DST：首夜任务的依赖链</h3>
<p>目标是从空背包建立营火，并活到第 2 天清晨。奖励按一次性里程碑累计，重复制作、丢下再捡起不会重复计分；只有满足全部前提并健康存活，才能得到最后的终局奖励。</p>
<table><tr><th>DST 判据</th><th style="width:17%">奖励</th><th style="width:31%">游戏端证据</th></tr><tr><td>曾分别持有草≥3、树枝≥1、燧石≥1</td><td>0.10</td><td>背包数量历史最大值</td></tr><tr><td>自己制作斧头</td><td>0.20</td><td>builditem(axe)</td></tr><tr><td>制斧后背包持有木材≥2</td><td>0.15</td><td>背包数量</td></tr><tr><td>自己建造营火</td><td>0.15</td><td>buildstructure(campfire)</td></tr><tr><td>夜间在自己的燃烧营火 6 单位内累计≥30秒</td><td>0.10</td><td>时钟、距离和燃烧状态</td></tr><tr><td>全部达成；次日清晨存活，生命≥50、饥饿≥20</td><td>0.30</td><td>世界周期与角色状态</td></tr></table>
<h3>沉星之序：终局条件与关卡过程分</h3>
<p>通关要求两名英雄同时占据两个不同出口。Judge v2 先校验轨迹，再对每个单一状态计算进展，整条轨迹只取最大值。重置、撤销和反复进入同一状态不能累积奖励。</p>
<table><tr><th>同一状态中达到的进展</th><th style="width:20%">分数</th></tr><tr><td>任一英雄取得 Rod / 巨石向左移动至少两格</td><td>0.05 / 0.18</td></tr><tr><td>一名英雄进入出口 / 巨石进入左出口接近通道</td><td>0.24 / 0.40</td></tr><tr><td>两人分别进入两侧出口列接近区域</td><td>0.55</td></tr><tr><td>一人在出口，另一人距另一个出口一步</td><td>0.75</td></tr><tr><td>两人同时占据两个出口</td><td><strong>1.00</strong></td></tr></table>
<p class="small">Judge v2 对历史轨迹进行事后重评分；过程分表示关卡里程碑，不是解题完成比例。阈值仍需更多合法解法与失败轨迹校准。</p>
</section>''')
P.append('''<section class="page">
<div class="eyebrow">03 / 实验组织</div><h2>评测框架与实验配置</h2>
<img class="flow" src="eval-flow.svg"/>
<p>两任务均使用 Harbor 组织环境、执行 Agent 并收集 verifier 输出。OpenCode 2.2.5 作为 harness，负责维持模型上下文、展示 MCP 工具和执行工具调用。模型为 DeepSeek V4.1 Flash（配置名称），API 标识 <code>deepseek-flash</code>；thinking 开启，reasoning effort 为 low。</p>
<div class="two"><div><h3>任务目录</h3><div class="codeblock">task/
├── task.toml
├── instruction.md
├── environment/
├── solution/
└── tests/test.sh</div></div><div><h3>目录职责</h3><p><code>task.toml</code> 描述资源与时限；<code>instruction.md</code> 给出目标与约束；<code>environment/</code> 构建交互环境；<code>solution/</code> 放参考解；<code>test.sh</code> 调用 Judge，将结果写入 Harbor 读取的 <code>reward.txt</code>。</p></div></div>
<table><tr><th>实验设置</th><th>DST</th><th>沉星之序</th></tr><tr><td>观察与时序</td><td>局部结构化状态，实时运行</td><td>截图与反馈，离散步进</td></tr><tr><td>本轮结果</td><td>0.30；未通关</td><td>历史终局 0；v2 重评 0.24</td></tr><tr><td>动作数</td><td>34 次提交</td><td>222 次</td></tr><tr><td>约束</td><td>本轮调整至 500k 累计 API token；1800秒墙钟</td><td>300 次动作；1800秒墙钟</td></tr><tr><td>验证方式</td><td>可信游戏事件与独立 scorer</td><td>重放所有动作，核对状态与终局</td></tr></table>
<h3>判分依据与可信边界</h3>
<p>DST scorer 依据独立观察器的事件判分，事件日志写入权应与 Agent 隔离。沉星之序 Judge 使用同一转移实现重放动作，再检查状态记录及双出口终局。</p>
<p class="small">DST 最终累计 524,901 token，在途请求越过 500k 阈值后停止，Harbor 记录一次退出异常，verifier 正常产出得分。两任务的观察模态、时序和奖励定义不同，得分用于各自任务内的诊断。</p>
</section>''')
P.append('''<section class="page">
<div class="eyebrow">03 / DST 轨迹分析</div><h2>DST：资源准备与动作执行失效</h2>
<img class="figure" src="dst-fallen-tree.png" style="width:145mm;margin:auto"/>
<div class="caption">图 3　最后阶段的真实游戏画面。树已砍倒，木材留在地上；背包里有草和斧头，但没有达到“持有 2 根木材”的条件。</div>
<table class="timeline"><tr><th>步骤</th><th>动作与反馈</th><th style="width:20%">计分结果</th></tr><tr><td>8–18</td><td>移动、采草并寻找燧石；对地面燧石从 pick 改为 pickup。</td><td>材料 +0.10</td></tr><tr><td>19</td><td>craft(axe)，真实消耗材料，触发制作事件。</td><td>制斧 +0.20</td></tr><tr><td>20–22</td><td>装备参数曾用错；随后靠近并砍树。</td><td>无新增奖励</td></tr><tr><td>23–34</td><td>循环砍同一实体，没有转去拾取掉落物。</td><td>最终 0.30</td></tr></table>
<div class="quote">“Let's loop chop until log appears in inventory or tree gone, max 12 swings.”<small>DeepSeek 原始推理摘录，砍树循环之前。</small></div>
<p>模型将“背包出现木材”或“树的 ID 消失”设为停止条件，但砍树不会自动拾取木材，倒下后的实体 ID 也仍存在。最终观察已包含 <code>chop=false</code> 与地面 log，动作仍未切换到拾取。材料与制斧所得的 0.30 表明模型能执行前置步骤；后续失分则暴露出状态变化未能及时修正执行计划的问题。</p>
<p>BALROG 将模型能够回答机制问题、却未在行动中运用相应知识的现象概括为知识与行动脱节。<a href="https://arxiv.org/html/2411.13543v1#S4.SS1">[1]</a> 本轮轨迹呈现的具体问题是反馈未进入下一步决策：地面木材和目标失效信息均未促成动作切换，桥接层持续返回 running 又强化了重复执行。GameWorld 对实时交互的分析也强调接口反馈与推理延迟对执行结果的影响。<a href="https://arxiv.org/html/2604.07429v1">[2]</a> 本轮在白天因 token 预算终止，未覆盖夜间生存决策。</p>
</section>''')
P.append('''<section class="page">
<div class="eyebrow">03 / 沉星之序轨迹分析</div><h2>沉星之序：局部进展与全局规划</h2>
<div class="photo-row"><img src="ootss-step140.png" style="width:101mm"/><div class="aside"><div class="num">0.24</div><p class="small">第 140 步达到的最佳里程碑</p><p>蓝色 Wizard 已进入左侧出口，另一名角色仍在中部，巨石没有进入左出口接近通道。</p></div></div>
<div class="caption">图 4　第 140 步的关卡状态。单人进入出口得 0.24；两人同时到达才算成功。</div>
<div class="quote">“Oops active hero was Gemsman, not Wizard! We forgot switch after activate…”<small>DeepSeek 原始 reasoning 事件 57，对应第 138–140 步；随后执行角色切换并继续移动。</small></div>
<p>模型从受阻反馈中发现角色混淆，切换后让一名英雄进入出口，获得 0.24。但在全部 222 次动作中，巨石只出现在初始位置和右侧一格。参考解在第 31 步已将巨石向左移动两格，第 70 步进入左出口接近通道；模型始终未完成这一空间准备。</p>
<table><tr><th>轨迹现象</th><th>证据</th><th>反映的问题</th></tr><tr><td>能使用机制</td><td>128 次有效行走、7 次交换、4 次 Rod 推动</td><td>已能正确使用部分局部机制</td></tr><tr><td>反复回退与试探</td><td>6 次重置、10 次撤销、39 次未改变局面</td><td>角色状态跟踪和预期结果检查不稳</td></tr><tr><td>缺少全局进展</td><td>巨石未进入左侧关键通道</td><td>局部有效动作没有组成完整的因果计划</td></tr></table>
<p>模型的主要失分来自局部操作未组成满足双出口条件的整体计划。BALROG 观察到的复杂空间推理和系统探索困难，为反复回退但关键物件未取得进展提供了分析视角。<a href="https://arxiv.org/html/2411.13543v1#S4.SS1">[1]</a> GameWorld 同样发现，部分进展往往无法转化为稳定通关。<a href="https://arxiv.org/html/2604.07429v1">[2]</a> 本轮反复撤销和重置并未形成稳定的布局推进，提示后续策略需要将角色状态记忆与子目标检查结合：每段动作后核对关键物件是否按预期变化，并据此保留或修订计划。</p>
</section>''')
P.append('''<section class="page">
<div class="eyebrow">讨论 / 复现入口</div><h2>结论与后续验证</h2>
<p class="lead">本轮 DeepSeek 能完成资源准备、工具使用和局部纠错，但在持续执行中未能稳定维持任务进展：DST 的资源链停在砍树与拾取之间，沉星之序未形成通向双出口的协作布局。</p>
<p>两款任务各分析一条 thinking-low 轨迹，结论适用于本轮执行中的失败机制，尚不足以估计一般通关率。后续实验应先完善环境验收，再通过重复运行评估策略改进。</p>
<h3>后续验证</h3>
<p>DST 应先接入快照恢复与启动检查，修正动作完成、失败和目标失效反馈，再以首夜成功策略及死亡、空等反例核验评分。沉星之序应补齐规则对照，并在固定关卡中比较显式状态记录、短计划核验和无进展重规划的效果。扩展到多次运行后，报告成功率、里程碑进展和交互成本。</p>
<p>本项目形成了两种可追溯的评测路径：原生模拟通过游戏事件核验过程，规则复现通过确定性重放核验状态。二者将任务得分与具体动作、反馈和推理关联，为后续区分环境问题与模型策略问题提供依据。</p>
<h3>代码、视频与参考资料</h3>
<div class="refs"><p>[1] <a href="https://arxiv.org/html/2411.13543v1#S4.SS1">BALROG: Benchmarking Agentic LLM and VLM Reasoning On Games</a>，§4.1。<br>[2] <a href="https://arxiv.org/html/2604.07429v1">GameWorld: Towards Standardized and Verifiable Evaluation of Multimodal Game Agents</a>，§4.5、§7。</p></div>
<div class="refs"><p>代码与完整证据：<a href="https://github.com/CostaliyA/game-bench-harbor">github.com/CostaliyA/game-bench-harbor</a><br>镜像归档：<a href="https://huggingface.co/datasets/CostaliyA/game-bench-harbor-images">huggingface.co/datasets/CostaliyA/game-bench-harbor-images</a></p>
<p>关卡与攻略参考：<a href="https://sinkingstar.wikitactics.com/areas/heroes-and-artifacts/#heroes-and-artifacts-7">WikiTactics · Heroes and Artifacts 7</a>。复现所使用的公开引擎许可保留在仓库的 JORIC-LICENSE。视频根据保存的动作与状态重放。</p>
<p>框架参考：<a href="https://docs.harborframework.com/tasks/overview">Harbor Tasks</a>；<a href="https://api-docs.deepseek.com/guides/thinking_mode/">DeepSeek Thinking Mode</a>。实验输入、原始 reasoning 与动作轨迹保存在 results/，视频字幕摘录推理摘要。</p></div>
<p class="small">日期：2026 年 11 月 15 日。实验机器：a800-server1。部署依赖、镜像内容与复现步骤见交付指南，工程审计另附。</p>
</section>''')
# Keep the historical report intact; prepend the evidence-backed latest-run addendum.
addendum=R/'context500k-addendum.html'
if addendum.exists():
 P.insert(0,addendum.read_text())
style=style.replace('/usr/share/fonts/opentype/noto',os.environ.get('GAME_BENCH_FONT_DIR','/usr/share/fonts/opentype/noto'))
text='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>游戏环境 Agent 评测技术报告</title><style>'+style+'</style><body>'+''.join(P)+'</body></html>'
(R/'report.html').write_text(text)
out=R.parent/'Game_Bench_Harbor_Report.pdf'
HTML(string=text,base_url=str(R)).write_pdf(out)
print(out)

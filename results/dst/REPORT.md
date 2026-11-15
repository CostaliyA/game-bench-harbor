# DST 首夜任务：Harbor + OpenCode + DeepSeek 实跑结果

**最终 reward = 0.30，success = false，终止原因：累计 API token 预算耗尽。** Harbor verifier 与独立 reward.py 重算结果一致。本轮是首次接通试跑，含启动同步排障，不能当作已消除环境干扰的模型对比结果。

## 配置与固定起点

| 项目 | 本轮实际配置 |
|---|---|
| 任务 | dst-first-night-v1，空背包建营火并活过第一夜 |
| 执行链路 | Harbor → OpenCode v2.2.5 → DeepSeek API → MCP → Lua → 真实 DST |
| 模型请求 / API 返回 | deepseek/deepseek-flash / deepseek-flash |
| Thinking | enabled，reasoning_effort=low |
| seed | 341784114 |
| 游戏 build | 762172 |
| 固定起点 | Wilson，第 1 天清晨，空背包，生命 150 / 饥饿 150 / 理智 200 |
| 存档快照 | 0000000003；完整世界与角色档已在服务器私有目录封存 |
| 观察 | 半径 25 的局部结构化状态，游戏时间每 0.5 秒采样 |
| 动作 | 普通移动、采集、拾取、制作、装备、砍树、进食、烹饪、加燃料、等待 |
| 录像 | 原生游戏画面 1280×720，10 FPS，361.6 秒 |
| 本轮预算 | 500,000 累计 API tokens；最后一个在途调用可越过阈值；1800 秒墙钟 |

固定起点 SHA256：`99b902f93a3a1ee234845a32a3d5e6d4fb87b652d679d9fdcfedabfeefcfebdf`。

服务器容器 `zyr-dst-steam-desktop` 内路径：`/home/steam/dst-eval-runtime/baseline/cluster.tar.gz`。重复试验应在游戏关闭后恢复这份完整存档，保留相同游戏版本与桥接配置，不能重新生成随机世界或只填相同 seed。固定存档不保证真实时间推理延迟与操作系统调度完全一致。

## Reward 明细

| 项目 | 本轮结果 | 得分 |
|---|---|---:|
| 曾持有草 ≥3、树枝 ≥1、燧石 ≥1 | 完成 | 0.10 |
| 自己制作斧头 | 完成 | 0.20 |
| 制斧后背包持有木材 ≥2 | 未完成 | 0 |
| 自己建造营火 | 未完成 | 0 |
| 夜间在自己的燃烧营火附近累计 30 秒 | 未完成 | 0 |
| 全部完成且健康活到次日清晨 | 未完成 | 0 |
| **合计** | **success=false** | **0.30** |

结束时仍为第 1 天白天，生命 150、饥饿约 115.63。模型已砍倒一棵树，但木头留在地上，未获得背包木材分数。最后一段循环只检查“木头进入背包”或“树的 ID 消失”，而倒下后的树实体 ID 仍存在且 `chop=false`，因此继续尝试砍同一实体。桥接层的该无效动作反馈仍显示 running，也妨碍了及时诊断。这是本轮发现的动作反馈改进项。

## 统计

- 33 次完成且返回 usage 的 API 调用，43 次请求尝试（含预算拒绝/重试）。
- 总 tokens：524,901；prompt tokens：518,036；completion tokens：6,865。累计口径包含缓存输入及 OpenCode 辅助请求，不等于新增文本长度。
- 记录到 API 返回 reasoning_content 共 12,240 字符，没有补写或推测未返回的思考。
- 34 次提交的游戏动作：pick 6、move 6、wait 5、pickup 1、craft 1、equip 1、chop 14。
- 游戏端正式 start 到 timeout 约 220.8 游戏秒；预算监控墙钟约 341.8 秒。
- Harbor job：`dst-first-night-deepseek-flash-002`；trial：`first-night__bCMkakj`。
- Harbor verifier：`{"reward": 0.3}`；同时记录 `NonZeroAgentExitCodeError`，预算终止后的 API 重试被中断。异常未隐藏，也未将其当作过夜成功。

## 本轮排障与可比性边界

第一次 Harbor 启动因容器网络不可达中止，未进行有效游戏回合。第二次启动成功，但开始按钮/控制台按键同步导致前几次模型观察仍返回 inactive；随后由运行器侧开启回合并关闭暂停菜单，初始同步消耗和模型空等保留在完整轨迹中。管理员没有替模型选择或执行采集、制作等游戏策略动作。

原草案 50k token 预算在启动调通阶段耗尽，运行中调整到 500k；本轮不是预先锁定完整协议的严谨基准成绩。后续对比应在开始前锁定 500k 或另一固定预算，启动握手通过后才放行模型，并保持同一存档。此次没有从多个成功回合中挑选成绩。

## 文件索引

- `thinking-actions.md`：按 API 调用整理的完整 thinking / content / tool_calls。
- `model-trajectory.jsonl`：同一内容的机器可读版本。
- `api/`：逐次原始请求、原始 SSE 返回和 usage；未记录鉴权请求头。
- `actions.jsonl` / `action-results.jsonl`：每次提交动作及前后状态。
- `states.jsonl`：游戏端连续结构化观测。
- `events.jsonl`：独立评分事件，包含 start、两个 milestone、timeout。
- `reward.json`：独立重算结果。
- `episode.mp4` / `final.png`：完整录像与最终画面。
- `harbor/`：真实 Harbor job/trial 结果、OpenCode 原始输出、ATIF trajectory 与 verifier 结果。
- `used-runtime/`：本轮实际部署的桥接、评分观察、API 记录和预算监控源文件；不以之后修改的代码冒充运行版本。

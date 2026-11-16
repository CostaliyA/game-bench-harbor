# DST 500k 上下文续测：完整首夜通关

2026-11-16（Asia/Shanghai），真实 DST 单人离线客户端，Harbor 0.26.0 + OpenCode V2 2.2.5。配置名为 DeepSeek V4.1 Flash，实际请求与响应模型标识均为 `deepseek-flash`；未记录更细的服务端权重版本。

**最终 reward 1.00，success=true，terminal=dawn。** Harbor verifier 与独立事件重算一致；1 个 trial 完成，0 个 Harbor 异常。角色到达第 2 天清晨，生命 147.29、饥饿 75，夜间靠近自建燃烧营火累计 60.0 游戏秒。

## 上下文与用量

| 项目 | 本轮实测或配置 |
|---|---:|
| OpenCode 上下文上限 | 500,000 tokens |
| 输入 / 输出上限 | 495,904 / 4,096 tokens |
| 实际最大单次 prompt | 165,265 tokens |
| 累计 prompt（含缓存命中） | 7,440,652 tokens |
| 累计 completion（含 reasoning） | 15,723 tokens |
| 累计 total | 7,456,375 tokens |
| prompt 缓存命中 | 7,290,880 tokens |
| API 调用 / 游戏动作 | 73 / 97 |
| 相机采样 | 961 条，heading 与 target 均为 45° |
| 原始录像 | 574.6 秒，10 FPS，连续原速 |

**500k 是配置窗口，不是累计 token 预算，也不是本轮实际填满的输入长度。** `opencode-effective.json` 保存实际加载的配置；本轮设置 `DST_TOKEN_LIMIT=0`，取消跨请求累计 500k 截断，保留 1800 秒墙钟限制。实际只用到约 165k 的单次输入，所以不能据此宣称验证了 500k 满窗能力。

API completion 中 reasoning 为 9,303 tokens、其余输出为 6,420；Harbor 顶层 `n_output_tokens` 为后者。用量分析以原始 API usage 为准，不把两种口径误报为不一致。

## 得分证据

| 游戏事件 | 距 start 的游戏秒 | 分值 |
|---|---:|---:|
| 自制斧头 | 46.7 | 0.20 |
| 曾分别持有草、树枝、燧石 | 68.5 | 0.10 |
| 制斧后持有两份木材 | 127.5 | 0.15 |
| 自建营火 | 324.2 | 0.15 |
| 夜间靠近自建燃烧营火满 30 秒 | 450.0 | 0.10 |
| 全部条件完成并存活至次日清晨 | 480.5 | 0.30 |

完整事件见 [events.jsonl](events.jsonl)，判分见 [reward.json](reward.json) 与 [Harbor verifier](harbor/trial/verifier/reward-report.json)。

## 轨迹分析

1. **采集与反馈修正。** 模型起初对地面燧石使用 `pick`，等待后发现物品仍在地上，在第 12 步改用 `pickup`，第 13 步制作斧头。材料里程碑分别跟踪历史持有量，因此树枝被制斧消耗后仍可在草凑齐时得分。
2. **砍树后切换拾取。** 第 20–24 步砍第一棵树后，API 25 的实际推理指出树实体仍在但 `chop=false`，第 25 步拾取掉落木材。第 39–40 步继续拾取第二棵树的木材，完成木材里程碑。本轮没有复现首轮一直砍树而未拾取的停滞。
3. **资源预留与夜间准备。** 模型先凑够五份草和两份树枝，再在第 51 步制作备用火把，保留三份草用于营火；黄昏又收集额外木材作燃料。API 46–52 对昼夜比例有估计误差，但持续检查实际 phase，未把估计当成终局证据。
4. **从建造错误恢复。** 第 78 步建火返回 `invalid placement`；模型在第 79 步移动到空地，第 80 步重试，并在第 81 步等待后确认营火已经出现。第 82、83、88 步成功加燃料。
5. **处理轻微掉血并等到终局。** 生命从 150 降至约 147.29 后，模型在 API 65 中怀疑贴火太近，第 90 步移动约两单位，保持在营火六单位范围内。原因是模型推断；日志没有记录独立伤害来源，不能将其认定为已验证的掉血机制。之后生命保持稳定，模型持续观察到 `night_fire_30s` 和 `dawn` 才结束。

这些证据支持本轮完成了资源依赖规划、拾取切换、建造错误恢复、燃料管理与夜间等待。旧 500k **累计预算**轮次在白天被截断，不能将其未过夜归因为夜间策略失败。本轮同时改变了累计截断条件与随机采样结果，也保留了启动问题；不能从这一对单次运行断言成功由 500k 窗口本身造成。

## 启动干预与实验边界

初态沿用此前已恢复并暂停的基线：seed 341784114、空背包、生命/饥饿/理智满值，基线 SHA256 为 `99b902f93a3a1ee234845a32a3d5e6d4fb87b652d679d9fdcfedabfeefcfebdf`，见 [preflight-state.json](preflight-state.json) 和 [experiment.json](experiment.json)。

第一次 observe 启动握手未完成，技能面板导致游戏自动暂停。前三个模型动作是空状态下的 `move(0,0)`、`wait(5)`、`wait(15)`；请求的移动超出桥接层 30 单位限制，恢复后的首个采样位置仍为基线坐标。操作者按一次 Escape 关闭面板。之后未提供策略提示，也未替模型执行采集、移动、建造或加燃料。完整原片保留这段启动过程。

因此，本轮是**有启动干预的单次完整模型通关记录**，不是完全无人值守的 benchmark 验收。模型观察是半径 25 的结构化状态，不是截图输入；视频用于核查。自动复位、成功 oracle 和多次重复评估仍未完成。

## 视频、完整推理与复核

- [注释版视频](../../videos/dst-context500k-annotated.mp4)：全长原速，底部显示全部 Step、动作与实际英文 reasoning 原文摘录。
- [完整原始录像](https://github.com/CostaliyA/game-bench-harbor/releases/download/dst-context500k-20261116/dst-context500k-original.mp4)；[Release 页面](https://github.com/CostaliyA/game-bench-harbor/releases/tag/dst-context500k-20261116)。原片不压缩替换，SHA256 与字节数见 [media-manifest.json](media-manifest.json)。
- [完整模型推理](thinking-actions.md)、[模型返回轨迹](model-trajectory.jsonl)、[逐动作与返回对照](action-trajectory.jsonl)。
- [Harbor 结果](harbor/result.json)、[OpenCode 原始输出 gzip](harbor/trial/agent/opencode-v2.txt.gz)、[实际配置](opencode-effective.json)。
- [运行时代码与任务快照](used-runtime/)；[复现说明](../../runtime/dst/CONTEXT500K.zh-CN.md)。

视频只在原画面下方增加注释区，没有剪去暂停、加速或重演。字幕取对应 API 返回 reasoning 的前 215 个字符，截断处带省略号；同一 execute 循环的多个动作共享同次推理。动作与 API 按源服务器记录的响应结束墙钟对齐，时间值保存在 `api-file-times.json`，不依赖下载后的文件修改时间。推理原文和结果说明分开标注。

从仓库根目录离线核对：

```bash
python3 scripts/regrade_dst.py results/dst-context500k-003/events.jsonl
python3 scripts/validate_dst_context500k.py
```

预期 reward 1.00。后一个命令同时核对实际配置、API 用量、97 个动作及其返回、961 条相机采样和运行代码 SHA256，不调用模型。

# Game Bench Harbor

DST 真实离线首夜、两夜科学营地任务与《沉星之序》固定网页移植关卡的 Harbor 实验代码、轨迹、视频及验收报告。

**[深度技术报告 PDF](docs/Game_Bench_Harbor_Report.pdf)** · [Markdown 版](docs/TECHNICAL_REPORT.zh-CN.md) · **[交付与复现指南](docs/DELIVERY.zh-CN.md)** · **[HF 镜像归档](https://huggingface.co/datasets/CostaliyA/game-bench-harbor-images)**

| 任务 | 模型与观察 | 结果 | 关键边界 |
|---|---|---|---|
| **DST science settlement v1 最新** | DeepSeek Flash + OpenCode，结构化局部状态 | **reward 0.000，第一夜死亡，0 个 Harbor 异常** | 新目标为第 3 天清晨科技营地；实际最大输入 44,150；未进入科技阶段，尚无完整成功 oracle |
| DST first night | DeepSeek Flash + OpenCode，结构化局部状态 | **Harbor reward 1.00，完整首夜通关** | 500k 配置窗口，实际最大输入 165,265；有启动干预，自动复位未完成 |
| DST 首夜 5m 累计预算补充重测 | DeepSeek Flash + OpenCode，结构化局部状态 | **reward 1.00，零异常** | 实际累计 2,472,787 token，最大单次输入 47,744；95 次动作；录像前段面板遮挡 |
| DST 历史累计预算轮次 | DeepSeek Flash + OpenCode，结构化局部状态 | reward 0.30，白天预算终止 | 500k 为累计用量限制，不能等同 500k 上下文 |
| OOTSS Heroes & Artifacts 7 | DeepSeek Flash + OpenCode，截图输入 | 历史终局分 0；Judge v2 重评分 0.24 | 固定棋盘网页移植，非商业客户端；视频为轨迹回放 |

**[最新科学营地任务、reward 与结果分析](results/dst-settlement-001/REPORT.zh-CN.md)** · **[83 步 action / reasoning 注释视频](videos/dst-settlement-v1-annotated.mp4)**。新任务要求经过两夜、自建科学机器和火坑、制作装备并保留物资；规则在模型开跑前冻结，阶段分 0.75 + 共同终局条件 0.25。旧首夜的 1.00 保留，新旧分数不直接比较。本轮 0 分暴露了照明与资源计划、观察使用和工具参数问题，尚未验证后半段科技挑战的难度。

DST 报告区分 500k 配置窗口、实际输入长度与累计用量，并记录环境准备。这些分数用于记录具体实验，严格 benchmark 验收还需重复运行和完善环境生命周期。DST 没有已验证成功的 oracle；任务的 solution 入口明确报错，避免伪造参考成功。上方 PDF 对应此前轮次，最新科学营地结果以本轮报告为准。

## 下载并加载镜像

```bash
curl -L https://huggingface.co/datasets/CostaliyA/game-bench-harbor-images/resolve/main/game-bench-harbor-images.tar.gz -o game-bench-harbor-images.tar.gz
curl -L https://huggingface.co/datasets/CostaliyA/game-bench-harbor-images/resolve/main/SHA256SUMS -o image-SHA256SUMS
sha256sum -c image-SHA256SUMS
gzip -dc game-bench-harbor-images.tar.gz | docker load
```

镜像：`game-bench-harbor/runtime:20261115`、`game-bench-harbor/ootss:20261115`、`game-bench-harbor/dst-agent:20261115`，linux/amd64。镜像来源和许可见 [images/IMAGE_BUILD.md](images/IMAGE_BUILD.md)。运行依赖 Docker 和 Harbor；原实验使用 A800 已安装的 Harbor 0.26.0。HF文件是可加载的镜像归档，不是 `docker pull` registry 地址。

## 重算已保存的轨迹

```bash
python3 scripts/regrade_dst.py
bash scripts/regrade_ootss.sh
python3 scripts/analyze_dst_settlement.py results/dst-settlement-001
```

预期分别为 0.30、0.24、0.00。第二条在独立浏览器重放全部动作后评分。不会调用模型，也不会把重评分改写成历史在线结果。

## 新的模型评测

从仓库根目录运行，并通过安全的本机环境设置 `DEEPSEEK_API_KEY`：

```bash
harbor run -c configs/ootss.yaml --job-name ootss-my-new-run -n 1
harbor run -p tasks/ootss-heroes-artifacts-7 -a oracle --job-name ootss-oracle -n 1
```

DST 另需正版游戏、固定存档和已启动的外部桥接环境，详见交付指南。准备好环境后：

```bash
harbor run -c configs/dst.yaml --job-name dst-my-new-run -n 1
```

**不要直接对上一次尚未复位的 DST 服务运行新 trial。** 当前目录格式可被 Harbor 加载，但自动加载游戏和恢复固定存档不是其生命周期的一部分。仓库公开了实际桥接与评分代码，未把该工程缺口隐藏在成功返回码里。

2026-11-16 的 500k 上下文续测已完成：**reward 1.00、97 次动作、0 个 Harbor 异常**。取消累计 token 截断后运行至自然 dawn，累计 7,456,375 tokens；实际最大单次输入为 165,265。启动时按一次 Escape 关闭自动暂停面板，之后由模型完成全部游戏动作。[本轮分析与完整证据](results/dst-context500k-003/REPORT.zh-CN.md)；[500k 配置与复现说明](runtime/dst/CONTEXT500K.zh-CN.md)。

## 视频与完整轨迹

- [5m 累计预算首夜注释视频](videos/dst-full-episode-005-annotated.mp4) · [原始录像](videos/dst-full-episode-005-original.mp4) · [报告与完整轨迹](results/dst-full-episode-005/REPORT.zh-CN.md)：8 分 40 秒、95 次动作，全部里程碑完成；本轮仅提高累计预算，未改动上下文窗口。

- **[DST 科学营地 v1：83 步 Action / reasoning 注释视频](videos/dst-settlement-v1-annotated.mp4)**；[原始录像](https://github.com/CostaliyA/game-bench-harbor/releases/download/dst-settlement-v1-20261116/dst-settlement-v1-original.mp4)。注释版 7 分 34.3 秒，原速 10 FPS；完整保留游戏过程，只裁去死亡后冗余暂停尾帧。[固定 reward、失败分析与复现](results/dst-settlement-001/REPORT.zh-CN.md)；[完整推理与动作](results/dst-settlement-001/thinking-actions.md)。
- **[DST 500k 上下文续测：完整通关注释视频](videos/dst-context500k-annotated.mp4)**；[原始录像](https://github.com/CostaliyA/game-bench-harbor/releases/download/dst-context500k-20261116/dst-context500k-original.mp4)。9 分 34.6 秒，原速 10 FPS；[97 步完整轨迹与分析](results/dst-context500k-003/REPORT.zh-CN.md)。
- [DST 历史固定视角累计预算轮次：Step / Action / 推理摘要](videos/dst-annotated.mp4)；[原始录屏](videos/dst-original.mp4)。约2分18秒，原速10 FPS，23次动作；[重测结果与完整证据](results/dst-fixed-camera-002/REPORT.zh-CN.md)。
- [沉星之序：动作与推理注释视频](videos/ootss-wiki-replay.mp4)。视频重放完整的222动作轨迹，不是商业客户端连续录屏；模型原始输入截图保留在 results/ 中。
- [DST 首轮证据](results/dst/)（技术报告 PDF 已增加最新通关附录，历史主体对应首轮；[首轮视频](https://github.com/CostaliyA/game-bench-harbor/blob/590c53b/videos/dst-annotated.mp4)）：原始请求/返回、thinking、动作、状态、事件、Harbor结果。
- [OOTSS thinking-low 证据](results/ootss/thinking-low-001/)：截图、状态轨迹、推理、原始OpenCode日志（gzip）、原始job结果与v2报告。
- [参考成功轨迹](results/ootss/reference/)；[非thinking对照](results/ootss/nonthinking-002/)。

GitHub大视频可点击“View raw”或“Download raw file”下载。视频中的推理摘要与完整原始推理分开保存。

## 源码与证据版本

`results/dst-settlement-001/used-runtime/` 保存科学营地首轮的冻结代码、任务与配置，`protocol-manifest.json` 记录开跑前哈希；`results/dst-context500k-003/used-runtime/` 保存首夜成功轮次的实际快照。`tasks/` 是本发布的可读任务目录；`results/dst/used-runtime/` 保存 DST 历史试跑实际使用的代码。历史运行快照与当前 `runtime/` 分别保存，各轮分析引用对应目录的实际配置和代码。原有报告的相对链接可能指向原目录；以本 README 索引为准。

`validation/` 保存发布检查结果；`SHA256SUMS` 覆盖交付文件。凭据、Steam登录目录、游戏本体和私有起点存档未公开上传。

# 交付清单与复现指南

2026-11-16 更新：最新 DST 500k 上下文配置试跑已完整通关，reward 1.00。详见[最新分析](../results/dst-context500k-003/REPORT.zh-CN.md)与[运行说明](../runtime/dst/CONTEXT500K.zh-CN.md)。原始录像位于 [GitHub Release](https://github.com/CostaliyA/game-bench-harbor/releases/tag/dst-context500k-20261116)，注释版在仓库 videos/。历史分数与下面的旧复核命令仍保留。

## 在线入口

- 公开代码、报告与证据：https://github.com/CostaliyA/game-bench-harbor
- Docker镜像归档：https://huggingface.co/datasets/CostaliyA/game-bench-harbor-images
- 技术报告：[TECHNICAL_REPORT.zh-CN.md](TECHNICAL_REPORT.zh-CN.md)

## 交付内容

| 目录 | 用途 |
|---|---|
| tasks/dst-first-night | DST任务定义、MCP接口、test.sh及reward scorer；尚无已验证成功oracle |
| tasks/ootss-heroes-artifacts-7 | 固定棋盘环境、MCP截图动作接口、成功reference solution、重放verifier与Judge v2 |
| configs | 两任务的Harbor + OpenCode + DeepSeek配置 |
| runtime/dst | DST的Lua桥接、观察器、HTTP服务、API记录、预算监控与视频注释代码 |
| scripts | 不调用模型的历史轨迹重评分，以及OOTSS视频工具 |
| results | 两款任务的原始试跑轨迹、推理、状态、Judge与Harbor结果 |
| videos | DST原始/注释视频，OOTSS逐动作轨迹回放 |
| validation | 发布版dry-run、OOTSS oracle实跑及重评分证据 |
| images | 镜像构造脚本、来源和许可边界 |

## 1. 镜像安装

按照README下载HF镜像压缩包，核对SHA256SUMS后执行docker load。镜像包含运行依赖；HF托管的是镜像归档文件。镜像ID见HF的image-manifest.json及本仓库validation/image-manifest.json。

发布版由已有依赖镜像过滤后重新构建，已去除SteamCMD、游戏和账号目录，不携带登录凭据。DST正版游戏与私有基线需要使用者在自己的服务器准备。

## 2. 不消耗API额度的复核

在仓库根目录：

```bash
python3 scripts/regrade_dst.py
bash scripts/regrade_ootss.sh
harbor run -p tasks/ootss-heroes-artifacts-7 -a oracle -n 1 --job-name oracle-check
```

预期DST独立事件分数0.30；OOTSS模型旧轨迹的重放加v2分数0.24；参考oracle完整Harbor运行分数1.00。后者是参考解验收，不是一个新的模型成绩。

## 3. 新的模型评测

安全地在当前shell环境设置DEEPSEEK_API_KEY后，从仓库根目录执行：

```bash
harbor run -c configs/ootss.yaml --job-name ootss-new-001 -n 1
```

本仓库没有保存API key，也不要求把key写进YAML。每次使用不同job-name，避免覆盖结果。发布配置走DeepSeek官方API；历史DST试跑曾使用的API记录代理代码仍在runtime/dst及used-runtime内，凭据仅以Authorization请求头转发，原始证据没有包含这些请求头。

## 4. DST的额外前置条件

历史世界位于a800的`zyr-dst-steam-desktop`容器。私有固定基线是`/home/steam/dst-eval-runtime/baseline/cluster.tar.gz`，seed=341784114、build=762172、快照0000000003。该归档与账号关联的路径不公开分发；SHA256在报告中记录。

正确的后续试验流程应为：关闭游戏并备份当前局 → 恢复只读完整基线 → 启动真实客户端并加载该世界 → 注入桥接与observer → 检查角色/时间/背包/状态 → 启动本局独立日志目录与API记录 → 确认start握手且连续状态时间推进 → 运行Harbor模型。

当前代码还没有把整段生命周期封装为每次`harbor run`自动执行。默认连接地址为`http://172.17.0.2:18765`，可通过Agent容器和verifier的`DST_BRIDGE_URL`环境变量覆盖；Docker网络必须允许访问已有服务。不能把一个仍留着上局事件的服务当作新trial环境。DST完整自动复位与成功oracle验收是未完成项，见技术报告第10节。

固定视角重测视频现位于 videos/dst-annotated.mp4；本轮23次动作、193条相机采样，报告见 [重测结果](../results/dst-fixed-camera-002/REPORT.zh-CN.md)。下述旧 DST 注释时间轴对应首轮归档。

## 5. 如何对应视频与轨迹

DST注释视频使用`results/dst/start-time.txt`作为墙钟零点，动作时间来自actions.jsonl；video-annotations.json保存字幕区间。摘要来自真实DeepSeek reasoning_content，不是另一个模型重新解释游戏。原文在thinking-actions.md和api/。

OOTSS视频见videos/ootss-wiki-replay.mp4。视频按原trajectory.jsonl逐步呈现状态；原始截图位于thinking-low-001/frames，推理对应reasoning.jsonl，完整OpenCode输出用gzip保存。视频展示复现关卡的记录状态，不重新验证动作，不是商业客户端实时视频。

## 6. 发布验收状态

发布版已在a800实际执行两份配置的dry-run、OOTSS oracle Harbor trial，以及两款历史轨迹重算。oracle结果1.00、0 exceptions；历史轨迹重算DST=0.30、OOTSS=0.24。验证文件见validation/。

这份文档不把网页移植等同商业原版，也不把DST启动干预后的试跑等同严格无干预实验。本文和深度报告共同给出可直接使用的结果、复核方式和仍需实现的验收条件。

最新轮次离线核对：`python3 scripts/validate_dst_context500k.py`。实际单次输入最大 165,265 tokens，累计用量 7,456,375；不能把前者配置的 500k 窗口误解为后者的阈值。

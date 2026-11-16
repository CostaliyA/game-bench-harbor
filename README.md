# Game Bench Harbor

DST 真实离线首夜任务与《沉星之序》固定网页移植关卡的 Harbor 实验代码、轨迹、视频及验收报告。

**[深度技术报告 PDF](docs/Game_Bench_Harbor_Report.pdf)** · [Markdown 版](docs/TECHNICAL_REPORT.zh-CN.md) · **[交付与复现指南](docs/DELIVERY.zh-CN.md)** · **[HF 镜像归档](https://huggingface.co/datasets/CostaliyA/game-bench-harbor-images)**

| 任务 | 模型与观察 | 结果 | 关键边界 |
|---|---|---|---|
| DST first night | DeepSeek Flash + OpenCode，结构化局部状态 | 最新完整回合 reward 1.00，成功 | 5m 上限、实际 2.47m token；录像中关闭过遮挡面板；每局自动复位未完成 |
| OOTSS Heroes & Artifacts 7 | DeepSeek Flash + OpenCode，截图输入 | 历史终局分 0；Judge v2 重评分 0.24 | 固定棋盘网页移植，非商业客户端；视频为轨迹回放 |

这些是具体实验的分数，不是两款原版商业游戏都已通过严格 benchmark 验收的声明。DST没有已验证成功的oracle；该任务的solution入口明确报错，避免伪造参考成功。

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
```

预期分别为 0.30、0.24。第二条在独立浏览器重放全部动作后评分。不会调用模型，也不会把重评分改写成历史在线结果。

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

提高预算后的完整回合已完成：**reward 1.00、零异常，存活到第 2 天清晨**。5m token 上限，实际使用 2,472,787 token，95 次接受的动作；962 条相机采样均为 45°。见[完整回合报告](results/dst-full-episode-005/REPORT.zh-CN.md)。

## 视频与完整轨迹

- [DST 完整首夜成功回合：Step / Action / 推理摘要](videos/dst-full-episode-005-annotated.mp4)；[原始录屏](videos/dst-full-episode-005-original.mp4)。约 8 分 40 秒，95 次动作；[结果与完整证据](results/dst-full-episode-005/REPORT.zh-CN.md)。前段画面有角色信息面板遮挡，已在报告记录。
- [DST 500k 预算固定视角重测：Step / Action / 推理摘要](videos/dst-annotated.mp4)；[原始录屏](videos/dst-original.mp4)。约2分18秒，原速10 FPS，23次动作；[重测结果与完整证据](results/dst-fixed-camera-002/REPORT.zh-CN.md)。
- [沉星之序：动作与推理注释视频](videos/ootss-wiki-replay.mp4)。视频重放完整的222动作轨迹，不是商业客户端连续录屏；模型原始输入截图保留在 results/ 中。
- [DST 首轮证据](results/dst/)（技术报告 PDF 对应首轮；[首轮视频](https://github.com/CostaliyA/game-bench-harbor/blob/590c53b/videos/dst-annotated.mp4)）：原始请求/返回、thinking、动作、状态、事件、Harbor结果。
- [OOTSS thinking-low 证据](results/ootss/thinking-low-001/)：截图、状态轨迹、推理、原始OpenCode日志（gzip）、原始job结果与v2报告。
- [参考成功轨迹](results/ootss/reference/)；[非thinking对照](results/ootss/nonthinking-002/)。

GitHub大视频可点击“View raw”或“Download raw file”下载。视频中的推理摘要与完整原始推理分开保存。

## 源码与证据版本

`tasks/` 是本发布的可读任务目录；`results/dst/used-runtime/` 保存DST历史试跑实际使用的代码。发布时只做可配置地址、打包和参考入口等工程整理，未新跑一个模型回合，不用新代码冒充旧实验的运行版本。原有报告的相对链接可能指向原目录；以本README索引为准。

`validation/` 保存发布检查结果；`SHA256SUMS` 覆盖交付文件。凭据、Steam登录目录、游戏本体和私有起点存档未公开上传。

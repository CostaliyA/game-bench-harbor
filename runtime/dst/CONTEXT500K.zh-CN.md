# DST 500k 上下文运行

`configs/dst-context500k.yaml` 显式设置 OpenCode V2 的 `limit.context=500000`、`limit.input=495904`、`limit.output=4096`。这是每次请求的上下文容量；`DST_TOKEN_LIMIT` 是独立的累计 API 用量阈值，两者不可混用。配置字段依据 [OpenCode models 文档](https://opencode.ai/docs/models#aliases)。

本轮通过实际生成的 `opencode.json` 核对配置。实验并不保证实际输入会填满 500k，实际最大 prompt 与累计 token 另见运行结果。

## 外部环境准备

沿用交付指南的正版离线客户端、基线存档、Lua observer/bridge 和固定 45° 相机。恢复基线并核对清晨、空背包与满状态后，再启动新的服务进程。仓库不包含游戏本体、登录目录或私有存档，尚未把自动复位接入 Harbor。

以下命令在已经准备好的游戏桌面容器内执行；`DST_RUN_ID` 必须是全新的目录名。启动前结束旧的 server/proxy/watchdog，避免端口冲突；不要终止游戏客户端。把本目录的运行代码部署至 `/home/steam/dst-eval-runtime/`，保持文件对容器的 `steam` 用户可读写。

```bash
export DST_RUN_ID=my-new-context500k-run
export DST_TOKEN_LIMIT=0
export DST_WALL_LIMIT=1800
mkdir -p "/home/steam/dst-eval-runtime/$DST_RUN_ID"
python3 /home/steam/dst-eval-runtime/server.py >"/home/steam/dst-eval-runtime/$DST_RUN_ID/server.log" 2>&1 &
python3 /home/steam/dst-eval-runtime/proxy.py >"/home/steam/dst-eval-runtime/$DST_RUN_ID/proxy.log" 2>&1 &
python3 /home/steam/dst-eval-runtime/watchdog.py >"/home/steam/dst-eval-runtime/$DST_RUN_ID/watchdog.log" 2>&1 &
```

`DST_TOKEN_LIMIT=0` 禁用累计 token 截断，保留 1800 秒墙钟限制。代理继续记录每次 API 的 usage。若需要累计预算可传正整数；在途请求可能越过阈值，故它不是精确账单上限。

在宿主机仓库根目录，通过环境安全注入 `DEEPSEEK_API_KEY` 后运行：

```bash
harbor run -c configs/dst-context500k.yaml --job-name dst-context500k-my-new-run -n 1
```

配置中的 `172.17.0.2` 是本次 Docker bridge 地址；其他机器应同时更新模型代理地址和 `DST_BRIDGE_URL`。本轮实际使用的任务、完整配置及运行时代码保存在 `results/dst-context500k-003/used-runtime/` 和 `harbor/`，以这些快照为历史来源。

## 终局与归档

自然终局（dawn/death）由 Lua observer 发出，超时由 watchdog 发出。Harbor verifier 应确认有 start 和 terminal 事件，再写得分。Harbor 完成后，保存 `/status` 为 `final-status.json`，使用录屏进程的 PID 发送 SIGINT，使 MP4 正常写入文件尾，再归档录像。

本轮起始阶段遇到技能面板自动暂停，由操作者按一次 Escape 关闭；前三个模型动作是针对空状态的一次 move(0,0) 和两次 wait；该移动超出距离限制而未执行。该启动干预在 `experiment.json` 中单独记录。开始采集后，未向模型提供提示或替它执行游戏动作。


本轮字幕可在下载原片后重建：

```bash
python3 runtime/dst/summarize.py results/dst-context500k-003
python3 runtime/dst/annotate_context_run.py results/dst-context500k-003 --video /path/to/dst-context500k-original.mp4
```

需要带 `ass`/libass 过滤器的 FFmpeg 渲染字幕。`api-file-times.json` 保存源服务器记录的时间，重新汇总时沿用这些值；批量调用中的动作共享对应 API 的 reasoning。

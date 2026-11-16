# 固定朝向录制

`camera.lua` 在客户端世界加载后安装固定朝向更新：将 heading、headingtarget 设为 45°，清除 headingdelta 和 lastheadingdelta，然后调用原生 Update，保留跟随位置与缩放。重复安装不叠加包装。重新加载游戏会恢复原生相机。

`server.py` 在开始录制时释放旋转键并加载相机修复；`bridge.lua` 随状态记录实际朝向与目标朝向。`DST_RUN_ID` 指定 server、proxy、watchdog 的独立输出目录，默认仍为 `run-001`。新试跑前须恢复基线、安装 observer/bridge 并验证初态，详见交付指南。

生成字幕及注释视频（依赖 Python 3、FFmpeg、Noto Sans CJK SC）：

```bash
python summarize.py /path/to/run
python annotate_run.py /path/to/run --summaries /path/to/run/reasoning-summaries.json
ffmpeg -i /path/to/run/episode.mp4 \
  -vf 'pad=iw:960:0:0:color=0x101820,ass=/path/to/run/annotations.ass:fontsdir=/path/to/fonts' \
  -c:v libx264 -preset fast -crf 24 -pix_fmt yuv420p -movflags +faststart \
  -an /path/to/run/episode-annotated.mp4
```

`/path/to/fonts` 应包含 Noto Sans CJK 字体文件，避免字幕显示为空框。

摘要必须逐项对应本轮实际模型输出；工具调用没有 reasoning 时明确标注。字幕按动作提交墙钟时间对齐，预算到达时切换到结果提示。

## 完整局预算

`DST_TOKEN_LIMIT` 控制累计 API token 上限，`DST_WALL_LIMIT` 控制墙钟时限，默认分别为 500000 和 1800。两者由 proxy 与 watchdog 共同读取；同一运行目录下的 `limits.json` 可覆盖默认值：

```json
{"token_limit": 5000000, "wall_limit_seconds": 1800}
```

需要在同一局中加额度时，先写临时文件再原子替换 `limits.json`，避免读到半写入内容。预算按 API 返回的累计用量计数，在途请求可能使最终用量略超阈值。正常终局由 observer 的死亡或次日清晨事件决定。`terminal-time.txt` 记录事件到达时间，供视频结果字幕对齐。

并发试跑应使用独立桌面容器与独立 Steam/存档目录，并将 MCP 与 verifier 的桥接地址指向该容器，避免共享窗口、游戏进程及服务端口。Steam 登录目录仅在服务器私有保存。

字幕渲染需显式加载中文字体，例如 ASS 滤镜添加 `:fontsdir=/home/steam/dst-eval-runtime`，该目录放置 `NotoSansCJK-Regular.ttc`。发布前抽帧确认中文与终局字幕正常显示。

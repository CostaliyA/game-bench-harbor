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

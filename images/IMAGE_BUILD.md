# 镜像构造与来源

发布包包含 runtime、ootss、dst-agent 三个 linux/amd64 镜像，tag 为 20261115。

本次在 a800 上以历史依赖镜像 `zyr/ootss-harbor-level7:20261115` 为来源，导出文件系统，移除 `/opt/steamcmd`、`/app`、Steam账号/游戏目录、缓存、日志和 artifacts，再从 scratch 导入过滤后的 rootfs。随后分别 COPY 本仓库的网页关卡或 DST Agent MCP 服务。移除内容不存在于发布镜像的早期层中；并非只在原镜像上执行 rm。

完整发布包由 `docker save` 导出三个标签并 gzip 压缩，公共基础层由 Docker archive 复用。HF 的 image-manifest.json 保存各镜像ID、大小、架构；SHA256SUMS用于校验整个归档；audit.txt记录过滤范围。

这些是历史运行依赖的整理版，不能声称与历史评测镜像逐字节一致。容器内保留各系统包的许可证文件；Joric引擎附带公共领域许可。DST游戏客户端、账号与私有基线不在镜像中。

若要重新构建任务层，先按README下载并docker load，然后在仓库根执行：

```bash
docker build -t game-bench-harbor/ootss:local tasks/ootss-heroes-artifacts-7/environment
docker build -t game-bench-harbor/dst-agent:local tasks/dst-first-night/environment
```

基础镜像的生成脚本见 export_runtime.py、Dockerfile.base。它依赖原始已安装镜像，现阶段不是完全从公开上游逐包锁定版本的可重建发行版。公共镜像归档本身可独立加载，不需要该私有标签。后续应转为锁定基础镜像digest和全部依赖版本的公开构建链。
